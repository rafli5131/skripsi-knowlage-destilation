#!/usr/bin/env python3
"""Infer camera frames until one detection is found, then save one annotated PNG."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import rclpy
import torch
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from ultralytics import YOLO


EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class DetectionExampleNode(Node):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__("op3_documentation_detection_capture")
        self.args = args
        self.bridge = CvBridge()
        self.model = YOLO(str(args.checkpoint), task="detect")
        names = {int(key): str(value) for key, value in self.model.names.items()}
        if names != EXPECTED_NAMES:
            raise ValueError(f"Checkpoint class mapping mismatch: {names}")
        self.model.model.eval()
        self.model.to("cpu")
        self.model.model.float()
        self.saved = False
        self.started = time.monotonic()
        self.subscription = self.create_subscription(
            Image, args.topic, self.on_image, qos_profile_sensor_data
        )
        self.get_logger().info(
            f"Waiting for a camera frame with at least one detection on {args.topic}; CPU FP32"
        )

    def on_image(self, message: Image) -> None:
        if self.saved:
            return
        frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
        if frame is None or frame.size == 0:
            return
        result = self.model.predict(
            source=frame,
            imgsz=self.args.imgsz,
            batch=1,
            device="cpu",
            conf=self.args.confidence,
            iou=self.args.iou,
            verbose=False,
            save=False,
            plots=False,
            max_det=300,
        )[0]
        if result.boxes is None or len(result.boxes) == 0:
            return

        detections = []
        for box in result.boxes:
            class_id = int(box.cls.item())
            xyxy = [float(value) for value in box.xyxy[0].tolist()]
            detections.append(
                {
                    "class_id": class_id,
                    "class_name": EXPECTED_NAMES[class_id],
                    "confidence": float(box.conf.item()),
                    "bbox_xyxy_px": xyxy,
                }
            )

        annotated = result.plot()
        self.args.image_output.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(self.args.image_output), annotated):
            raise OSError(f"Could not save annotated image: {self.args.image_output}")
        payload = {
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_topic": self.args.topic,
            "camera_frame_id": str(message.header.frame_id or "unspecified"),
            "capture_stamp": {
                "sec": int(message.header.stamp.sec),
                "nanosec": int(message.header.stamp.nanosec),
            },
            "image_resolution": {"width": int(message.width), "height": int(message.height)},
            "checkpoint": str(self.args.checkpoint),
            "checkpoint_sha256": sha256_file(self.args.checkpoint),
            "class_names": EXPECTED_NAMES,
            "device": "cpu",
            "precision": "FP32",
            "imgsz": self.args.imgsz,
            "confidence_threshold": self.args.confidence,
            "iou_threshold": self.args.iou,
            "detections": detections,
            "annotated_image": str(self.args.image_output),
            "elapsed_seconds_until_example": time.monotonic() - self.started,
            "raw_frame_or_video_saved": False,
        }
        self.args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.saved = True
        self.get_logger().info(f"Saved one annotated frame containing {len(detections)} detections")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="/thesis/image_raw")
    parser.add_argument("--checkpoint", type=Path, default=Path("models/weights/kd_student_best.pt"))
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--image-output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--timeout-sec", type=float, default=120.0)
    args, ros_args = parser.parse_known_args()
    args.checkpoint = args.checkpoint.expanduser().resolve()
    args.image_output = args.image_output.expanduser().resolve()
    args.json_output = args.json_output.expanduser().resolve()
    if not args.checkpoint.is_file():
        raise SystemExit(f"Checkpoint does not exist: {args.checkpoint}")
    if args.imgsz <= 0 or not 0 <= args.confidence <= 1 or not 0 <= args.iou <= 1:
        raise SystemExit("imgsz must be positive and confidence/IoU must be in [0, 1]")
    if args.timeout_sec <= 0:
        raise SystemExit("timeout-sec must be positive")
    if args.image_output.exists() or args.json_output.exists():
        raise SystemExit("Refusing to overwrite existing documentation capture files")

    rclpy.init(args=ros_args)
    node = DetectionExampleNode(args)
    deadline = time.monotonic() + args.timeout_sec
    try:
        while rclpy.ok() and not node.saved and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        if not node.saved:
            raise TimeoutError(f"No detection arrived within {args.timeout_sec:g} seconds")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
