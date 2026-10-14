"""Continue the already-authorized student queue or locked final pipeline.

Finish supervised recovery and resume training only when the queue is incomplete.
When training is already complete, continue directly to the locked
TEST/benchmark/analysis stages.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUEUE_STATE = ROOT / "artifacts/student_training_queue.json"
PIPELINE_STATE = ROOT / "artifacts/final_evaluation_pipeline.json"
SUPERVISOR_STATE = ROOT / "artifacts/continuation_supervisor.json"
RECOVERY_PENDING = ROOT / "runs/supervised/.yolo11_tiny_supervised_seed1337.manifest.json"
RECOVERY_FINAL = ROOT / "runs/supervised/yolo11_tiny_supervised_seed1337/manifest.json"
RECOVERY_RESULTS = ROOT / "runs/supervised/yolo11_tiny_supervised_seed1337/results.csv"
RECOVERY_LOG = ROOT / "runs/student_training_queue_logs/supervised_seed1337.resume1.log"
LOG_DIR = ROOT / "runs/student_training_queue_logs"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_state(status: str, **fields: Any) -> None:
    state = {
        "status": status,
        "updated_at_utc": now_utc(),
        "pid": os.getpid(),
        "protocol": "official Roboflow image-level split; three paired seeds; TEST excluded from training",
        **fields,
    }
    SUPERVISOR_STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_queue() -> dict[str, Any]:
    return json.loads(QUEUE_STATE.read_text(encoding="utf-8"))


def wait_for_recovery() -> None:
    progress_paths = (RECOVERY_RESULTS, RECOVERY_LOG)
    last_mtime = max((path.stat().st_mtime for path in progress_paths if path.is_file()), default=0.0)
    last_progress = time.monotonic()
    write_state("waiting_for_supervised_recovery", recovery_pending=str(RECOVERY_PENDING))
    while True:
        queue = load_queue()
        item = next(x for x in queue["items"] if x.get("label") == "supervised_seed1337")
        if item.get("status") == "succeeded" and RECOVERY_FINAL.is_file():
            manifest = json.loads(RECOVERY_FINAL.read_text(encoding="utf-8"))
            if manifest.get("status") == "complete":
                return
        if queue.get("status") == "failed":
            raise RuntimeError(f"Training queue failed during supervised recovery: {queue.get('error', '')}")
        if RECOVERY_PENDING.is_file():
            pending = json.loads(RECOVERY_PENDING.read_text(encoding="utf-8"))
            if pending.get("status") in {"failed", "interrupted"}:
                raise RuntimeError(f"Supervised recovery ended before completion: {pending.get('error', '')}")
        current_mtime = max((path.stat().st_mtime for path in progress_paths if path.is_file()), default=0.0)
        if current_mtime > last_mtime:
            last_mtime = current_mtime
            last_progress = time.monotonic()
        elif time.monotonic() - last_progress > 1800:
            raise RuntimeError("Supervised recovery files have not advanced for 30 minutes.")
        time.sleep(15)


def record_resumed_training_time() -> None:
    manifest = json.loads(RECOVERY_FINAL.read_text(encoding="utf-8"))
    with RECOVERY_RESULTS.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    pre_resume_row = next((row for row in rows if int(row["epoch"]) == 37), None)
    if pre_resume_row is None or not rows or not manifest.get("resume_history"):
        raise RuntimeError("Cannot reconstruct supervised runtime segments from manifest and results.csv.")
    resume_record = manifest["resume_history"][-1]
    pre_resume_seconds = float(pre_resume_row["time"])
    resumed_seconds = float(rows[-1]["time"])
    resume_record.update(
        {
            "results_csv_time_semantics": (
                "Ultralytics restarted the results.csv time counter at resume. "
                "The pre-interruption and resumed segment values are recorded separately; "
                "manifest start-to-finish wall time includes the interruption gap."
            ),
            "pre_resume_results_csv_time_seconds": pre_resume_seconds,
            "post_resume_results_csv_time_seconds": resumed_seconds,
            "sum_of_recorded_training_segments_seconds": pre_resume_seconds + resumed_seconds,
        }
    )
    RECOVERY_FINAL.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_step(label: str, command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.is_file() and log_path.stat().st_size:
        archive_path = log_path.with_name(f"{log_path.stem}.previous-{time.time_ns()}{log_path.suffix}")
        log_path.replace(archive_path)
    write_state(f"running_{label}", command=command, log=str(log_path))
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    with log_path.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT, check=False)
    if result.returncode != 0:
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-4000:]
        raise RuntimeError(f"{label} exited with {result.returncode}; log={log_path}\n{tail}")


def main() -> int:
    try:
        write_state("started")
        python = sys.executable
        queue = load_queue()
        if queue.get("status") != "complete":
            wait_for_recovery()
            record_resumed_training_time()
            write_state("supervised_recovery_complete", manifest=str(RECOVERY_FINAL))
            run_step(
                "training_queue",
                [python, "scripts/run_student_training_queue.py", "--resume"],
                LOG_DIR / "queue_resume_after_seed1337.log",
            )
        else:
            write_state("training_queue_already_complete", queue_state=str(QUEUE_STATE))
        run_step(
            "locked_final_pipeline",
            [python, "scripts/run_locked_final_pipeline.py", "--resume"],
            LOG_DIR / "locked_pipeline_resume.log",
        )
        write_state(
            "complete",
            queue_state=str(QUEUE_STATE),
            pipeline_state=str(PIPELINE_STATE),
            queue_log=str(LOG_DIR / "queue_resume_after_seed1337.log"),
            pipeline_log=str(LOG_DIR / "locked_pipeline_resume.log"),
        )
        return 0
    except Exception as error:
        write_state("failed", error=f"{type(error).__name__}: {error}")
        return 1
    except KeyboardInterrupt:
        write_state("interrupted", error="Supervisor interrupted; inspect child processes and stage states before resuming.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
