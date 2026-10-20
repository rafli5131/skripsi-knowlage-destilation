#!/usr/bin/env python3
"""Sample unannotated ROS camera frames for a manually reviewed OP3 dataset."""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path


DATA_ROOT = Path(__file__).resolve().parents[1] / "data/op3_camera_eval/sessions"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", required=True, help="Unique letters, digits, underscores, or hyphens")
    parser.add_argument("--condition", choices=("servo_idle", "walking", "unknown"), required=True)
    parser.add_argument("--topic", default="/thesis/image_raw")
    parser.add_argument("--max-frames", type=int, default=120)
    parser.add_argument("--interval-sec", type=float, default=1.0)
    parser.add_argument("--duration-sec", type=float, default=300.0)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.session_id):
        parser.error("session-id must contain only letters, digits, underscores, or hyphens")
    if args.max_frames < 1 or args.interval_sec <= 0 or args.duration_sec <= 0:
        parser.error("max-frames, interval-sec, and duration-sec must be positive")

    try:
        import cv2
        import rclpy
        from cv_bridge import CvBridge
        from rclpy.node import Node
        from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
        from sensor_msgs.msg import Image
    except ImportError as exc:
        parser.error(f"Activate the OP3 ROS/Python environment first: {exc}")

    session_dir = DATA_ROOT / args.session_id
    session_dir.mkdir(parents=True, exist_ok=False)
    image_dir = session_dir / "images"
    image_dir.mkdir()
    journal_path = session_dir / "capture_frames.jsonl"
    started_at = datetime.now(timezone.utc).isoformat()

    class FrameCapture(Node):
        def __init__(self) -> None:
            super().__init__("op3_camera_dataset_capture")
            self.bridge = CvBridge()
            self.count = 0
            self.last_saved = float("-inf")
            self.journal = journal_path.open("x", encoding="utf-8")
            qos = QoSProfile(
                history=HistoryPolicy.KEEP_LAST,
                depth=1,
                reliability=ReliabilityPolicy.BEST_EFFORT,
            )
            self.subscription = self.create_subscription(Image, args.topic, self.on_image, qos)

        def on_image(self, message: Image) -> None:
            now = time.monotonic()
            if self.count >= args.max_frames or now - self.last_saved < args.interval_sec:
                return
            frame = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            filename = f"frame_{self.count + 1:06d}.jpg"
            image_path = image_dir / filename
            if not cv2.imwrite(str(image_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95]):
                raise OSError(f"Failed to save {image_path}")
            self.count += 1
            self.last_saved = now
            record = {
                "image": filename,
                "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                "ros_stamp_sec": int(message.header.stamp.sec),
                "ros_stamp_nanosec": int(message.header.stamp.nanosec),
                "frame_id": str(message.header.frame_id),
                "width": int(message.width),
                "height": int(message.height),
            }
            self.journal.write(json.dumps(record) + "\n")
            self.journal.flush()
            self.get_logger().info(f"Saved {self.count}/{args.max_frames}: {image_path}")

    rclpy.init()
    node = FrameCapture()
    deadline = time.monotonic() + args.duration_sec
    status = "duration_elapsed"
    try:
        while rclpy.ok() and node.count < args.max_frames and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        if node.count >= args.max_frames:
            status = "max_frames_reached"
        elif node.count == 0:
            status = "no_frames"
    except KeyboardInterrupt:
        status = "interrupted"
    except Exception:
        status = "error"
        raise
    finally:
        node.journal.close()
        manifest = {
            "session_id": args.session_id,
            "condition": args.condition,
            "image_topic": args.topic,
            "started_at_utc": started_at,
            "ended_at_utc": datetime.now(timezone.utc).isoformat(),
            "frame_count": node.count,
            "interval_sec": args.interval_sec,
            "max_frames": args.max_frames,
            "duration_sec": args.duration_sec,
            "status": status,
            "images_dir": "images",
            "frames_journal": journal_path.name,
        }
        (session_dir / "capture_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        print(f"Captured {node.count} raw frames in {image_dir}")
    return 0 if node.count else 1


if __name__ == "__main__":
    raise SystemExit(main())
