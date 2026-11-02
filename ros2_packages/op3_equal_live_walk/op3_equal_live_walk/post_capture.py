"""Capture overlay and two joint samples immediately after a walking run stops."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def capture_joint(path: Path) -> None:
    result = subprocess.run(
        ["ros2", "topic", "echo", "--once", "/robotis/present_joint_states", "sensor_msgs/msg/JointState"],
        capture_output=True,
        text=True,
        timeout=8,
        check=True,
    )
    path.write_text(result.stdout, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    marker = args.out_dir / "gait_stop_sent_utc.txt"
    deadline = time.monotonic() + 130
    while not marker.is_file():
        if time.monotonic() > deadline:
            raise TimeoutError(f"Gait stop marker tidak muncul: {marker}")
        time.sleep(0.1)
    subprocess.run(
        [sys.executable, "-m", "op3_equal_live_report.capture", str(args.out_dir / "frame_deteksi_sesudah_jendela.png")],
        check=True,
        timeout=7,
    )
    capture_joint(args.out_dir / "telemetry_after.txt")
    time.sleep(5)
    capture_joint(args.out_dir / "telemetry_after2.txt")
    print("POST_CAPTURE_DONE", args.out_dir, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
