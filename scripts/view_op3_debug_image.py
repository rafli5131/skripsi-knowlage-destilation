#!/usr/bin/env python3
"""Display the detector's annotated ROS image without running another model."""

from __future__ import annotations

import argparse
import os
import time


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="/vision/debug_image")
    parser.add_argument("--timeout-sec", type=float, default=15.0)
    args = parser.parse_args()
    if args.timeout_sec <= 0:
        parser.error("timeout-sec must be positive")
    if not os.environ.get("DISPLAY"):
        parser.error("DISPLAY is empty; use the robot desktop or SSH with X11 forwarding")

    try:
        import cv2
        import rclpy
        from cv_bridge import CvBridge
        from rclpy.node import Node
        from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
        from sensor_msgs.msg import Image
    except ImportError as exc:
        parser.error(f"Activate the OP3 ROS/Python environment first: {exc}")

    class DebugViewer(Node):
        def __init__(self) -> None:
            super().__init__("op3_debug_image_viewer")
            self.bridge = CvBridge()
            self.latest = None
            self.received = 0
            qos = QoSProfile(
                history=HistoryPolicy.KEEP_LAST,
                depth=1,
                reliability=ReliabilityPolicy.BEST_EFFORT,
            )
            self.subscription = self.create_subscription(Image, args.topic, self.on_image, qos)

        def on_image(self, message: Image) -> None:
            self.latest = self.bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
            self.received += 1

    rclpy.init()
    node = DebugViewer()
    deadline = time.monotonic() + args.timeout_sec
    window = "OP3 live detection | q/Esc: exit"
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.03)
            if node.latest is not None:
                cv2.imshow(window, node.latest)
                node.latest = None
            elif node.received == 0 and time.monotonic() >= deadline:
                raise TimeoutError(f"No annotated frames received on {args.topic}")
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
