"""Simpan satu frame overlay ROS tanpa menjalankan detektor lain."""

import argparse
import time
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class Capture(Node):
    def __init__(self, topic: str) -> None:
        super().__init__("op3_equal_live_overlay_capture")
        self.bridge = CvBridge()
        self.frame = None
        self.subscription = self.create_subscription(Image, topic, self.on_image, qos_profile_sensor_data)

    def on_image(self, msg: Image) -> None:
        self.frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--topic", default="/vision/debug_image")
    parser.add_argument("--timeout", type=float, default=12)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Berkas sudah ada: {args.output}")
    rclpy.init()
    node = Capture(args.topic)
    try:
        deadline = time.monotonic() + args.timeout
        while node.frame is None and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        if node.frame is None:
            raise TimeoutError(f"Tidak ada frame di {args.topic}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(args.output), node.frame):
            raise RuntimeError("Gagal menyimpan PNG")
        print(args.output)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
