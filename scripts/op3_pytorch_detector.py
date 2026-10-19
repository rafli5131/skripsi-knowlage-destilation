#!/usr/bin/env python3
"""Read-only ROS 2 camera inference for the KD student on ROBOTIS OP3."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main(args: list[str] | None = None) -> int:
    try:
        import cv2
        import psutil
        import rclpy
        import torch
        import ultralytics
        import yaml
        from cv_bridge import CvBridge
        from rclpy.node import Node
        from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
        from sensor_msgs.msg import Image
        from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
    except ImportError as error:
        raise SystemExit(
            f"Dependensi runtime belum tersedia ({error}). Gunakan Python yang memuat ROS 2 Jazzy, "
            "PyTorch, Ultralytics, OpenCV, psutil, PyYAML, cv_bridge, dan vision_msgs."
        ) from error

    class DetectorNode(Node):
        def __init__(self) -> None:
            super().__init__("op3_kd_pytorch_detector")
            self.declare_parameter("model_path", str(ROOT / "models/weights/kd_student_best.pt"))
            self.declare_parameter("data_config", str(ROOT / "configs/data_train_val.yaml"))
            self.declare_parameter("input_topic", "/thesis/image_raw")
            self.declare_parameter("imgsz", 640)
            self.declare_parameter("confidence_threshold", 0.25)
            self.declare_parameter("iou_threshold", 0.45)
            self.declare_parameter("experiment_condition", "unknown")
            self.declare_parameter("publish_debug_image", False)
            self.declare_parameter("debug_image_topic", "/vision/debug_image")
            self.declare_parameter("output_dir", str(ROOT / "runs/op3_pytorch"))
            self.declare_parameter("run_id", "")

            value = lambda name: self.get_parameter(name).value
            self.model_path = Path(str(value("model_path"))).expanduser().resolve()
            data_config = Path(str(value("data_config"))).expanduser().resolve()
            self.input_topic = str(value("input_topic"))
            self.imgsz = int(value("imgsz"))
            self.conf = float(value("confidence_threshold"))
            self.iou = float(value("iou_threshold"))
            self.condition = str(value("experiment_condition"))
            self.publish_debug = bool(value("publish_debug_image"))
            self.debug_topic = str(value("debug_image_topic"))
            self.output_dir = Path(str(value("output_dir"))).expanduser().resolve()
            self.run_id = str(value("run_id")) or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

            if self.condition not in {"unknown", "servo_idle", "walking"}:
                raise ValueError("experiment_condition must be unknown, servo_idle, or walking")
            if self.imgsz <= 0 or not 0 <= self.conf <= 1 or not 0 <= self.iou <= 1:
                raise ValueError("imgsz must be positive and confidence/IoU must be in [0, 1]")
            if not self.model_path.is_file():
                raise FileNotFoundError(f"Checkpoint not found: {self.model_path}")
            if not data_config.is_file():
                raise FileNotFoundError(f"Data config not found: {data_config}")
            config = yaml.safe_load(data_config.read_text(encoding="utf-8")) or {}
            configured_names = config.get("names", {})
            configured_names = {int(k): str(v) for k, v in configured_names.items()}
            if configured_names != EXPECTED_NAMES:
                raise ValueError(f"Dataset class mapping mismatch: {configured_names}")

            if str(torch.__version__).startswith("2.4") is False:
                self.get_logger().warning(f"PyTorch runtime is {torch.__version__}; verify checkpoint compatibility")
            self.model = ultralytics.YOLO(str(self.model_path), task="detect")
            checkpoint_names = {int(k): str(v) for k, v in self.model.names.items()}
            if checkpoint_names != EXPECTED_NAMES:
                raise ValueError(f"Checkpoint class mapping mismatch: {checkpoint_names}")
            self.model.model.eval()
            self.model.to("cpu")
            self.model.model.float()
            self.bridge = CvBridge()
            self.process = psutil.Process()
            self.process.cpu_percent(interval=None)
            self.publisher = self.create_publisher(Detection2DArray, "/vision/detections", 10)
            self.debug_publisher = (
                self.create_publisher(Image, self.debug_topic, 1) if self.publish_debug else None
            )
            # Sensor QoS depth=1 favors the newest frame; frames arriving during inference are dropped.
            camera_qos = QoSProfile(
                history=HistoryPolicy.KEEP_LAST,
                depth=1,
                reliability=ReliabilityPolicy.BEST_EFFORT,
            )
            self.subscription = self.create_subscription(Image, self.input_topic, self.on_image, camera_qos)
            self.last_frame_time = time.monotonic()
            self.frame_count = 0
            self.error_count = 0
            self.started = time.monotonic()
            self.last_warning = 0.0

            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.csv_path = self.output_dir / f"{self.run_id}.csv"
            self.csv_stream = self.csv_path.open("x", newline="", encoding="utf-8")
            self.csv_fields = [
                "run_id", "condition", "frame_index", "capture_stamp_ns", "receive_time_utc",
                "width", "height", "preprocess_ms", "inference_ms", "postprocess_ms",
                "end_to_end_ms", "fps_running", "process_cpu_percent", "process_rss_bytes",
                "detection_count", "error",
            ]
            self.csv_writer = csv.DictWriter(self.csv_stream, fieldnames=self.csv_fields, lineterminator="\n")
            self.csv_writer.writeheader()
            self.csv_stream.flush()
            self.metadata_path = self.output_dir / f"{self.run_id}.json"
            metadata = {
                "status": "running", "run_id": self.run_id,
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "condition": self.condition,
                "condition_source": "operator_supplied_label; motion is not inferred from telemetry",
                "source": "ros_image_topic", "input_topic": self.input_topic,
                "output_topic": "/vision/detections", "checkpoint": str(self.model_path),
                "checkpoint_sha256": sha256_file(self.model_path), "class_names": EXPECTED_NAMES,
                "device": "cpu", "precision": "FP32", "imgsz": self.imgsz,
                "confidence_threshold": self.conf, "iou_threshold": self.iou,
                "preview_enabled": self.publish_debug,
                "frame_queue_policy": "best_effort_keep_last_depth_1; callback is serial; stale frames are dropped",
                "python": sys.version, "platform": platform.platform(), "torch": str(torch.__version__),
                "ultralytics": ultralytics.__version__, "opencv": cv2.__version__,
                "csv": str(self.csv_path),
            }
            self.metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
            self.watchdog = self.create_timer(2.0, self.check_camera)
            self.get_logger().info(
                f"CPU FP32 checkpoint={self.model_path}; input={self.input_topic}; "
                f"condition={self.condition}; detections=/vision/detections"
            )

        def write_row(self, row: dict[str, Any]) -> None:
            self.csv_writer.writerow(row)
            self.csv_stream.flush()

        def on_image(self, message: Image) -> None:
            self.last_frame_time = time.monotonic()
            started = time.perf_counter()
            now_utc = datetime.now(timezone.utc).isoformat()
            stamp_ns = int(message.header.stamp.sec) * 1_000_000_000 + int(message.header.stamp.nanosec)
            try:
                frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
                if frame is None or frame.size == 0:
                    raise ValueError("received an empty image frame")
                if frame.ndim != 3 or frame.shape[2] != 3:
                    raise ValueError(f"expected a 3-channel BGR frame, got shape {frame.shape}")
                height, width = frame.shape[:2]
                results = self.model.predict(
                    source=frame, imgsz=self.imgsz, batch=1, device="cpu",
                    conf=self.conf, iou=self.iou, verbose=False, save=False, plots=False,
                    stream=False, max_det=300,
                )
                result = results[0]
                speed = result.speed
                detections = Detection2DArray()
                detections.header = message.header
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls.item())
                        confidence = float(box.conf.item())
                        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
                        detection = Detection2D()
                        detection.header = message.header
                        detection.bbox.center.position.x = (x1 + x2) / 2.0
                        detection.bbox.center.position.y = (y1 + y2) / 2.0
                        detection.bbox.size_x = max(0.0, x2 - x1)
                        detection.bbox.size_y = max(0.0, y2 - y1)
                        hypothesis = ObjectHypothesisWithPose()
                        hypothesis.hypothesis.class_id = f"{class_id}:{EXPECTED_NAMES[class_id]}"
                        hypothesis.hypothesis.score = confidence
                        detection.results.append(hypothesis)
                        detections.detections.append(detection)

                self.publisher.publish(detections)
                if self.debug_publisher is not None:
                    annotated = result.plot()
                    image_message = self.bridge.cv2_to_imgmsg(annotated, encoding="bgr8")
                    image_message.header = message.header
                    self.debug_publisher.publish(image_message)

                self.frame_count += 1
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                uptime = max(time.monotonic() - self.started, 1e-9)
                self.write_row({
                    "run_id": self.run_id, "condition": self.condition, "frame_index": self.frame_count,
                    "capture_stamp_ns": stamp_ns, "receive_time_utc": now_utc, "width": width, "height": height,
                    "preprocess_ms": speed.get("preprocess", 0.0), "inference_ms": speed.get("inference", 0.0),
                    "postprocess_ms": speed.get("postprocess", 0.0), "end_to_end_ms": elapsed_ms,
                    "fps_running": self.frame_count / uptime, "process_cpu_percent": self.process.cpu_percent(interval=None),
                    "process_rss_bytes": self.process.memory_info().rss,
                    "detection_count": len(detections.detections), "error": "",
                })
            except Exception as error:  # Keep the subscriber alive after a bad frame.
                self.error_count += 1
                self.get_logger().error(f"Frame processing failed: {error}")
                self.write_row({
                    "run_id": self.run_id, "condition": self.condition, "frame_index": self.frame_count,
                    "capture_stamp_ns": stamp_ns, "receive_time_utc": now_utc,
                    "width": message.width, "height": message.height,
                    "end_to_end_ms": (time.perf_counter() - started) * 1000.0,
                    "process_rss_bytes": self.process.memory_info().rss, "error": str(error),
                })

        def check_camera(self) -> None:
            if time.monotonic() - self.last_frame_time > 5.0 and time.monotonic() - self.last_warning > 5.0:
                self.last_warning = time.monotonic()
                self.get_logger().warning(f"No image received on {self.input_topic} for over 5 seconds")

        def close(self) -> None:
            self.csv_stream.flush()
            self.csv_stream.close()
            metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            metadata.update({
                "status": "stopped", "stopped_at_utc": datetime.now(timezone.utc).isoformat(),
                "processed_frames": self.frame_count, "frame_errors": self.error_count,
                "mean_fps": self.frame_count / max(time.monotonic() - self.started, 1e-9),
            })
            self.metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    rclpy.init(args=args)
    node = None
    try:
        node = DetectorNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.close()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
