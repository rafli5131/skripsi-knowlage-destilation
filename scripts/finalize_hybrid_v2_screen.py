"""Build T40 once the autonomous S1-S3 screen has finished successfully."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "runs/kd_hybrid_v2"
STATUS = PROJECT / "screen_s1_s3_status.jsonl"
PYTHON = "/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python"


def main() -> None:
    marker = PROJECT / "t40_finalizer_status.json"
    if marker.exists():
        raise FileExistsError(f"Finalizer already ran: {marker}")
    deadline = time.monotonic() + 12 * 3600
    while True:
        events = [json.loads(line) for line in STATUS.read_text(encoding="utf-8").splitlines() if line]
        if any(event["event"] == "driver_failed" for event in events):
            raise RuntimeError("Screen driver failed; T40 cannot be finalized")
        if any(event["event"] == "screen_s1_s3_complete" for event in events):
            break
        if time.monotonic() > deadline:
            raise TimeoutError("Screen has not completed in twelve hours")
        time.sleep(60)
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    subprocess.run([PYTHON, str(ROOT / "scripts/build_t40_hybrid_v2_val.py")], cwd=ROOT, env=env, check=True)
    with marker.open("x", encoding="utf-8") as stream:
        json.dump({"status": "complete", "table": "analisis_performa/tabel/T40_penyaringan_hybrid_v2_val.csv"}, stream)
        stream.write("\n")


if __name__ == "__main__":
    main()
