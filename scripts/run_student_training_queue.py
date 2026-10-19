"""Run the locked paired student training jobs serially after supervised seed 42."""

from __future__ import annotations

import csv
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .project_config import load_run_config, resolve_repo_path
except ImportError:
    from project_config import load_run_config, resolve_repo_path


ROOT = Path(__file__).resolve().parents[1]
RUN_CONFIG = load_run_config()
QUEUE_CONFIG = RUN_CONFIG["queue"]
SEED_RUNS = {int(seed): value for seed, value in QUEUE_CONFIG["seeds"].items()}
PYTHON = resolve_repo_path(RUN_CONFIG["training_python"])
INITIAL_RUN_NAME = str(QUEUE_CONFIG["initial_supervised_run"])
INITIAL_RUN = ROOT / "runs/supervised" / INITIAL_RUN_NAME
INITIAL_FINAL_MANIFEST = INITIAL_RUN / "manifest.json"
INITIAL_PENDING_MANIFEST = INITIAL_RUN.parent / f".{INITIAL_RUN_NAME}.manifest.json"
FINGERPRINT = resolve_repo_path(RUN_CONFIG["fingerprint"])
QUEUE_STATE = ROOT / "artifacts/student_training_queue.json"
QUEUE_LOGS = resolve_repo_path(QUEUE_CONFIG["log_dir"])
POLL_SECONDS = 20
STALE_SECONDS = 30 * 60


class QueueError(RuntimeError):
    """Raised when a queued run fails its safety or provenance checks."""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def manifest_status(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("status", "missing"))
    except (json.JSONDecodeError, OSError):
        return "incomplete-write"


def latest_epoch(results_csv: Path) -> int | None:
    if not results_csv.is_file():
        return None
    try:
        with results_csv.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        return int(float(rows[-1]["epoch"])) if rows else None
    except (OSError, KeyError, ValueError, csv.Error):
        return None


def wait_for_existing_baseline(state: dict[str, Any]) -> Path:
    item = state["items"][0]
    item["status"] = "waiting"
    item["started_at_utc"] = now_utc()
    write_json(QUEUE_STATE, state)
    print(f"Waiting for existing baseline run to finish: {INITIAL_RUN}", flush=True)
    last_epoch = None
    last_progress_at = time.monotonic()
    missing_since: float | None = None

    while True:
        if INITIAL_FINAL_MANIFEST.is_file():
            manifest = json.loads(INITIAL_FINAL_MANIFEST.read_text(encoding="utf-8"))
            if manifest.get("status") != "complete":
                raise QueueError(f"Existing baseline manifest is not complete: {manifest.get('status')}")
            item["status"] = "succeeded"
            item["finished_at_utc"] = now_utc()
            item["manifest"] = str(INITIAL_FINAL_MANIFEST)
            write_json(QUEUE_STATE, state)
            return INITIAL_FINAL_MANIFEST

        pending_status = manifest_status(INITIAL_PENDING_MANIFEST)
        if pending_status in {"failed", "interrupted"}:
            raise QueueError(f"Existing baseline ended with status {pending_status}.")
        if pending_status is None:
            if missing_since is None:
                missing_since = time.monotonic()
            elif time.monotonic() - missing_since > 120:
                raise QueueError("Both pending and final baseline manifests are missing.")
        else:
            missing_since = None
            if pending_status not in {"started", "complete", "incomplete-write"}:
                raise QueueError(f"Unexpected baseline manifest status: {pending_status}")

        current_epoch = latest_epoch(INITIAL_RUN / "results.csv")
        if current_epoch is not None and current_epoch != last_epoch:
            last_epoch = current_epoch
            last_progress_at = time.monotonic()
            print(f"Existing supervised seed 42 finished epoch {current_epoch}.", flush=True)
        elif pending_status == "started" and (INITIAL_RUN / "results.csv").is_file():
            if time.monotonic() - last_progress_at > STALE_SECONDS:
                raise QueueError("Baseline results.csv has not advanced for 30 minutes; inspect the live run.")
        time.sleep(POLL_SECONDS)


def run_logged(command: list[str], log_path: Path, *, progress_dir: Path | None = None) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_stream:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
            stdout=log_stream,
            stderr=subprocess.STDOUT,
        )
        last_epoch = None
        while process.poll() is None:
            try:
                return_code = process.wait(timeout=POLL_SECONDS)
            except subprocess.TimeoutExpired:
                if progress_dir is not None:
                    current_epoch = latest_epoch(progress_dir / "results.csv")
                    if current_epoch is not None and current_epoch != last_epoch:
                        last_epoch = current_epoch
                        print(f"{progress_dir.name}: finished epoch {current_epoch}.", flush=True)
                continue
            if return_code != 0:
                raise QueueError(f"Command exited {return_code}; inspect log: {log_path}")
        if process.returncode != 0:
            raise QueueError(f"Command exited {process.returncode}; inspect log: {log_path}")


def validate_completed_run(manifest_path: Path, *, expected_kd: bool) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_fingerprint = sha256_file(FINGERPRINT)
    if manifest.get("status") != "complete":
        raise QueueError(f"Run manifest is not complete: {manifest_path}")
    if manifest.get("test_split_used") is not False:
        raise QueueError(f"Run used TEST or does not attest TEST was unused: {manifest_path}")
    if manifest.get("dataset_fingerprint_sha256") != expected_fingerprint:
        raise QueueError(f"Run is not tied to the locked dataset fingerprint: {manifest_path}")
    if manifest.get("train_labels_used_for_loss") is not (not expected_kd):
        raise QueueError(f"Run objective/label-use provenance is inconsistent: {manifest_path}")
    if expected_kd and "teacher-only" not in str(manifest.get("objective", "")):
        raise QueueError(f"KD run is not declared teacher-only: {manifest_path}")
    if not expected_kd and "supervised" not in str(manifest.get("objective", "")):
        raise QueueError(f"Control run is not declared supervised: {manifest_path}")


def run_item(state: dict[str, Any], index: int, item: dict[str, Any]) -> None:
    run_dir = ROOT / item["run_dir"]
    pending = run_dir.parent / f".{run_dir.name}.manifest.json"
    final_manifest = run_dir / "manifest.json"
    if run_dir.exists() or pending.exists():
        raise QueueError(f"Refusing to overwrite an existing run artifact: {run_dir}")

    item["status"] = "running"
    item["started_at_utc"] = now_utc()
    item["log"] = str(ROOT / item["log"])
    write_json(QUEUE_STATE, state)
    print(f"Starting {item['label']}; log: {item['log']}", flush=True)
    run_logged(item["command"], Path(item["log"]), progress_dir=run_dir)
    validate_completed_run(final_manifest, expected_kd=item["kind"] == "kd")

    item["status"] = "succeeded"
    item["finished_at_utc"] = now_utc()
    item["manifest"] = str(final_manifest)
    write_json(QUEUE_STATE, state)
    epoch = latest_epoch(run_dir / "results.csv")
    print(f"Completed {item['label']} (last CSV epoch {epoch}).", flush=True)


def archive_failed_attempt(item: dict[str, Any]) -> None:
    """Keep a failed attempt's manifest and log before retrying the same run."""
    run_dir = ROOT / item["run_dir"]
    pending = run_dir.parent / f".{run_dir.name}.manifest.json"
    if run_dir.exists():
        raise QueueError(f"Refusing automatic retry because partial run files exist: {run_dir}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    attempts = item.setdefault("attempts", [])
    attempt_number = len(attempts) + 1
    manifest_archive: Path | None = None
    if pending.exists():
        status = manifest_status(pending)
        if status != "failed":
            raise QueueError(f"Refusing automatic retry for pending manifest with status {status}: {pending}")
        manifest_archive = pending.with_name(f"{pending.stem}.failed-{stamp}{pending.suffix}")
        pending.replace(manifest_archive)

    log_path = Path(item["log"])
    if not log_path.is_absolute():
        log_path = ROOT / log_path
    log_archive: Path | None = None
    if log_path.exists():
        log_archive = log_path.with_name(f"{log_path.stem}.attempt{attempt_number}-{stamp}{log_path.suffix}")
        log_path.replace(log_archive)

    attempts.append({
        "status": "failed",
        "manifest": str(manifest_archive) if manifest_archive else None,
        "log": str(log_archive) if log_archive else None,
        "error": item.get("error"),
        "archived_at_utc": now_utc(),
    })
    item["status"] = "queued"
    item.pop("error", None)
    item.pop("finished_at_utc", None)


def load_or_create_state(*, resume: bool) -> tuple[dict[str, Any], bool]:
    if QUEUE_STATE.exists():
        if not resume:
            raise QueueError(f"Queue state already exists; inspect it and use --resume only after a failed/interrupted run: {QUEUE_STATE}")
        state = json.loads(QUEUE_STATE.read_text(encoding="utf-8"))
        if state.get("status") not in {"failed", "interrupted"}:
            raise QueueError(f"Only a failed or interrupted queue can be resumed; current status is {state.get('status')}.")
        if state.get("fingerprint_sha256") != sha256_file(FINGERPRINT):
            raise QueueError("Refusing to resume a queue with a different dataset fingerprint.")
        for item in state.get("items", []):
            if item.get("status") in {"running", "failed"}:
                archive_failed_attempt(item)
        state["status"] = "running"
        state.pop("error", None)
        state["resumed_at_utc"] = now_utc()
        state["updated_at_utc"] = now_utc()
        write_json(QUEUE_STATE, state)
        print(f"Resuming failed training queue. State: {QUEUE_STATE}", flush=True)
        return state, True

    if resume:
        raise QueueError(f"Cannot resume because queue state does not exist: {QUEUE_STATE}")
    state: dict[str, Any] = {
        "created_at_utc": now_utc(),
        "status": "running",
        "protocol": "official Roboflow image-level split; three paired seeds; TEST excluded from training",
        "initial_run": str(INITIAL_RUN),
        "fingerprint_sha256": sha256_file(FINGERPRINT),
        "items": [{"label": "wait_supervised_seed42", "kind": "wait", "status": "queued"}, *build_items()],
    }
    write_json(QUEUE_STATE, state)
    print(f"Student training queue started. State: {QUEUE_STATE}", flush=True)
    return state, False


def build_items() -> list[dict[str, Any]]:
    python = str(PYTHON)
    items = [
        {
            "label": "link_supervised_seed42_provenance",
            "kind": "provenance",
            "status": "queued",
            "run_dir": str(Path("runs/supervised") / INITIAL_RUN_NAME),
            "command": [python, "scripts/link_run_dataset_provenance.py", "--manifest", str(INITIAL_FINAL_MANIFEST)],
            "log": str(QUEUE_LOGS / "link_supervised_seed42.log"),
        },
    ]
    for seed in sorted(SEED_RUNS):
        if seed == 42:
            kd_name = SEED_RUNS[seed]["kd"]
            items.append({
                "label": "kd_seed42", "kind": "kd", "status": "queued",
                "run_dir": str(Path("runs/kd") / kd_name),
                "command": [python, "scripts/train_kd.py", "--seed", str(seed), "--run-name", kd_name],
                "log": str(QUEUE_LOGS / "kd_seed42.log"),
            })
            continue
        supervised_name = SEED_RUNS[seed]["supervised"]
        kd_name = SEED_RUNS[seed]["kd"]
        items.extend([
            {
                "label": f"supervised_seed{seed}", "kind": "supervised", "status": "queued",
                "run_dir": str(Path("runs/supervised") / supervised_name),
                "command": [python, "scripts/train_supervised_baseline.py", "--seed", str(seed), "--run-name", supervised_name],
                "log": str(QUEUE_LOGS / f"supervised_seed{seed}.log"),
            },
            {
                "label": f"kd_seed{seed}", "kind": "kd", "status": "queued",
                "run_dir": str(Path("runs/kd") / kd_name),
                "command": [python, "scripts/train_kd.py", "--seed", str(seed), "--run-name", kd_name],
                "log": str(QUEUE_LOGS / f"kd_seed{seed}.log"),
            },
        ])
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="resume a failed/interrupted queue while preserving failed attempt artifacts")
    args = parser.parse_args()
    if not PYTHON.is_file():
        raise QueueError(f"Experiment Python environment is missing: {PYTHON}")
    if not FINGERPRINT.is_file():
        raise QueueError(f"Locked dataset fingerprint is missing: {FINGERPRINT}")
    state, resumed = load_or_create_state(resume=args.resume)
    QUEUE_LOGS.mkdir(parents=True, exist_ok=True)

    active_item: dict[str, Any] | None = None
    try:
        if not resumed:
            active_item = state["items"][0]
            baseline_manifest = wait_for_existing_baseline(state)
            link_item = state["items"][1]
            active_item = link_item
            link_item["status"] = "running"
            link_item["started_at_utc"] = now_utc()
            write_json(QUEUE_STATE, state)
            print("Linking and revalidating pre-run dataset fingerprint for supervised seed 42.", flush=True)
            run_logged(link_item["command"], Path(link_item["log"]))
            validate_completed_run(baseline_manifest, expected_kd=False)
            baseline_manifest_data = json.loads(baseline_manifest.read_text(encoding="utf-8"))
            if baseline_manifest_data.get("dataset_snapshot_provenance", {}).get("linked_after_training") is not True:
                raise QueueError("Seed 42 provenance was not explicitly recorded as a post-run linkage.")
            link_item["status"] = "succeeded"
            link_item["finished_at_utc"] = now_utc()
            link_item["manifest"] = str(baseline_manifest)
            write_json(QUEUE_STATE, state)

        for index, item in enumerate(state["items"]):
            if item["kind"] in {"kd", "supervised"} and item.get("status") == "queued":
                active_item = item
                run_item(state, index, item)

        state["status"] = "complete"
        state["finished_at_utc"] = now_utc()
        write_json(QUEUE_STATE, state)
        print("All six paired student runs are complete; TEST remains unopened.", flush=True)
        return 0
    except KeyboardInterrupt:
        state["status"] = "interrupted"
        state["updated_at_utc"] = now_utc()
        write_json(QUEUE_STATE, state)
        print("Training queue interrupted; inspect its state and run manifests before resuming.", file=sys.stderr)
        return 130
    except Exception as error:
        if active_item is not None and active_item.get("status") == "running":
            active_item["status"] = "failed"
            active_item["finished_at_utc"] = now_utc()
            active_item["error"] = f"{type(error).__name__}: {error}"
        state["status"] = "failed"
        state["updated_at_utc"] = now_utc()
        state["error"] = f"{type(error).__name__}: {error}"
        write_json(QUEUE_STATE, state)
        print(state["error"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
