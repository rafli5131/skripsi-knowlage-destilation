"""Continue the locked S1-S3 VAL screen without touching existing runs."""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "runs/kd_hybrid_v2"
EVAL = ROOT / "runs/val_ablation/hybrid_v2_20261023"
PYTHON = Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python")
STATUS = PROJECT / "screen_s1_s3_status.jsonl"


def record(event: str, **details: object) -> None:
    payload = {"time_utc": datetime.now(timezone.utc).isoformat(), "event": event, **details}
    with STATUS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def complete_manifest(stage: str) -> Path | None:
    run = PROJECT / f"yolo11_tiny_hybrid_v2_{stage}_seed42"
    manifest = run / "manifest.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("status") != "complete":
            raise RuntimeError(f"{stage}: final manifest is not complete")
        return run
    pending = PROJECT / f".{run.name}.manifest.json"
    if pending.is_file():
        data = json.loads(pending.read_text(encoding="utf-8"))
        if data.get("status") in {"failed", "interrupted"}:
            raise RuntimeError(f"{stage}: training {data['status']}: {data.get('error')}")
    return None


def evaluate(stage: str, env: dict[str, str]) -> None:
    run = complete_manifest(stage)
    if run is None:
        raise RuntimeError(f"{stage}: training did not complete")
    result = EVAL / f"{run.name}_val.json"
    if result.exists():
        raise FileExistsError(f"Refusing to overwrite result: {result}")
    EVAL.mkdir(parents=True, exist_ok=True)
    log = EVAL / f"{stage}_eval.log"
    record("evaluation_started", stage=stage, run=str(run))
    with log.open("x", encoding="utf-8") as stream:
        subprocess.run(
            [str(PYTHON), str(ROOT / "scripts/evaluate_hybrid_v2_val.py"),
             "--run-dir", str(run), "--output-dir", str(EVAL)],
            cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True,
        )
    if not result.is_file():
        raise RuntimeError(f"{stage}: expected VAL result is missing")
    record("evaluation_complete", stage=stage, result=str(result))


def main() -> None:
    PROJECT.mkdir(parents=True, exist_ok=True)
    if STATUS.exists():
        raise FileExistsError(f"Screen driver already started: {STATUS}")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    record("driver_started", stages=["s1", "s2", "s3"])
    try:
        deadline = time.monotonic() + 4 * 3600
        while complete_manifest("s1") is None:
            if time.monotonic() > deadline:
                raise TimeoutError("S1 has not completed within four hours")
            time.sleep(30)
        evaluate("s1", env)
        for stage in ("s2", "s3"):
            run = PROJECT / f"yolo11_tiny_hybrid_v2_{stage}_seed42"
            pending = PROJECT / f".{run.name}.manifest.json"
            if run.exists() or pending.exists():
                raise FileExistsError(f"Refusing to overwrite existing {stage} run")
            log = PROJECT / f"{stage}_train.log"
            record("training_started", stage=stage, config=f"configs/kd_hybrid_v2_{stage}.yaml")
            with log.open("x", encoding="utf-8") as stream:
                subprocess.run(
                    [str(PYTHON), str(ROOT / "scripts/train_kd.py"), "--config",
                     str(ROOT / f"configs/kd_hybrid_v2_{stage}.yaml")],
                    cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True,
                )
            record("training_complete", stage=stage, run=str(run))
            evaluate(stage, env)
        record("screen_s1_s3_complete")
    except BaseException as error:
        record("driver_failed", error=f"{type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
