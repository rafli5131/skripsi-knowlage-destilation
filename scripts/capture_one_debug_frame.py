#!/usr/bin/env python3
"""Save one annotated frame only when the detector has published a detection."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray


class OneFrameCapture(Node):
    def __init__(self, image_topic: str, detections_topic: str, image_path: Path, json_path: Path) -> None:
        super().__init__("op3_documentation_frame_capture")
        self.image_topic = image_topic
        self.image_path = image_path
        self.json_path = json_path
        self.bridge = CvBridge()
        self.detections_by_stamp: dict[tuple[int, int], list[dict]] = {}
        qos = QoSProfile(depth=10)
        self.detection_sub = self.create_subscription(
            Detection2DArray, detections_topic, self.on_detections, qos
        )
        self.image_sub = self.create_subscription(Image, image_topic, self.on_image, qos)
        self.saved = False

    @staticmethod
    def stamp_key(header) -> tuple[int, int]:
        return (int(header.stamp.sec), int(header.stamp.nanosec))

    def on_detections(self, message: Detection2DArray) -> None:
        detections = []
        for item in message.detections:
            if not item.results:
                continue
            hypothesis = item.results[0].hypothesis
            class_id = str(hypothesis.class_id)
            class_name = class_id.split(":", 1)[1] if ":" in class_id else class_id
            detections.append(
                {
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": float(hypothesis.score),
                    "center_x_px": float(item.bbox.center.position.x),
                    "center_y_px": float(item.bbox.center.position.y),
                    "width_px": float(item.bbox.size_x),
                    "height_px": float(item.bbox.size_y),
                }
            )
        self.detections_by_stamp[self.stamp_key(message.header)] = detections
        if len(self.detections_by_stamp) > 20:
            self.detections_by_stamp.pop(next(iter(self.detections_by_stamp)))

    def on_image(self, message: Image) -> None:
        if self.saved:
            return
        detections = self.detections_by_stamp.get(self.stamp_key(message.header))
        if not detections:
            return
        frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
        self.image_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(self.image_path), frame):
            raise OSError(f"Could not write annotated frame to {self.image_path}")
        payload = {
            "saved_at_utc": datetime.now(timezone.utc).isoformat(),
            "camera_frame_id": str(message.header.frame_id or "unspecified"),
            "image_topic": self.image_topic,
            "detections_topic": "/vision/detections",
            "capture_stamp": {
                "sec": int(message.header.stamp.sec),
                "nanosec": int(message.header.stamp.nanosec),
            },
            "width": int(message.width),
            "height": int(message.height),
            "detections": detections,
            "image_path": str(self.image_path),
        }
        self.json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self.saved = True
        self.get_logger().info(f"Saved one annotated frame with {len(detections)} detections: {self.image_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-topic", default="/vision/debug_image")
    parser.add_argument("--detections-topic", default="/vision/detections")
    parser.add_argument("--image-output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--timeout-sec", type=float, default=120.0)
    args, ros_args = parser.parse_known_args()
    if args.timeout_sec <= 0:
        raise SystemExit("timeout-sec must be positive")
    args.image_output = args.image_output.expanduser().resolve()
    args.json_output = args.json_output.expanduser().resolve()
    if args.image_output.exists() or args.json_output.exists():
        raise SystemExit("Refusing to overwrite existing documentation capture files")

    rclpy.init(args=ros_args)
    node = OneFrameCapture(args.image_topic, args.detections_topic, args.image_output, args.json_output)
    deadline = time.monotonic() + args.timeout_sec
    try:
        while rclpy.ok() and not node.saved and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        if not node.saved:
            raise TimeoutError(f"No matching image with detections arrived within {args.timeout_sec:g} seconds")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
