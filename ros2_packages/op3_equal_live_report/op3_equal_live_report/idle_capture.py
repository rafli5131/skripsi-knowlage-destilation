"""Save two mid-run joint samples and an overlay after an idle measurement window."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def first_measure_time(path: Path) -> datetime | None:
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row.get("is_warmup", "").lower() == "false":
                return datetime.fromisoformat(row["receive_time_utc"])
    return None


def until(target: float) -> None:
    while time.time() < target:
        time.sleep(min(0.1, target - time.time()))


def capture_joint(path: Path) -> str:
    result = subprocess.run(
        ["ros2", "topic", "echo", "--once", "/robotis/present_joint_states", "sensor_msgs/msg/JointState"],
        capture_output=True,
        text=True,
        timeout=8,
        check=True,
    )
    received = datetime.now(timezone.utc).isoformat()
    path.write_text(result.stdout, encoding="utf-8")
    return received


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + 120
    tw = None
    while tw is None:
        tw = first_measure_time(args.csv)
        if time.monotonic() > deadline:
            raise TimeoutError(f"Warm-up tidak selesai: {args.csv}")
        if tw is None:
            time.sleep(0.1)
    log = {"t_w_utc": tw.isoformat(), "source_csv": str(args.csv), "samples": {}}
    for name, offset in (("mid1", 20), ("mid2", 40)):
        until(tw.timestamp() + offset)
        log["samples"][name] = capture_joint(args.out_dir / f"telemetry_{name}.txt")
        print("SAMPLE", name, log["samples"][name], flush=True)
    until(tw.timestamp() + 65)
    subprocess.run(
        [sys.executable, "-m", "op3_equal_live_report.capture", str(args.out_dir / "frame_deteksi_sesudah_jendela.png")],
        check=True,
        timeout=7,
    )
    log["overlay_capture_utc"] = datetime.now(timezone.utc).isoformat()
    log["samples"]["after"] = capture_joint(args.out_dir / "telemetry_after.txt")
    time.sleep(5)
    log["samples"]["after2"] = capture_joint(args.out_dir / "telemetry_after2.txt")
    (args.out_dir / "sampling_times.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print("IDLE_CAPTURE_DONE", args.out_dir, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
