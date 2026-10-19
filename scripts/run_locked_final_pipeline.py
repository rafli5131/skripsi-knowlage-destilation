"""Wait for the paired training queue, then run locked TEST, benchmark, and analysis."""

from __future__ import annotations

import hashlib
import argparse
import json
import os
import shutil
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
PIPELINE_CONFIG = RUN_CONFIG["pipeline"]
SEED_RUNS = {int(seed): value for seed, value in QUEUE_CONFIG["seeds"].items()}
PYTHON = resolve_repo_path(RUN_CONFIG["training_python"])
FINGERPRINT = resolve_repo_path(RUN_CONFIG["fingerprint"])
TRAINING_QUEUE = ROOT / "artifacts/student_training_queue.json"
PIPELINE_STATE = ROOT / "artifacts/final_evaluation_pipeline.json"
LOG_DIR = resolve_repo_path(PIPELINE_CONFIG["log_dir"])
FAILED_TEST_ATTEMPT = resolve_repo_path(PIPELINE_CONFIG["failed_test_attempt"])
TEST_OUTPUT = resolve_repo_path(PIPELINE_CONFIG["test_output"])
BENCHMARK_OUTPUT = resolve_repo_path(PIPELINE_CONFIG["benchmark_output"])
ANALYSIS_OUTPUT = resolve_repo_path(PIPELINE_CONFIG["analysis_output"])
POLL_SECONDS = 20
STALE_SECONDS = 30 * 60
SEEDS = tuple(sorted(SEED_RUNS))


class PipelineError(RuntimeError):
    """Raised when the locked final pipeline cannot proceed safely."""


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


def expected_models() -> dict[str, Path]:
    models = {"teacher_fp32": resolve_repo_path(RUN_CONFIG["teacher_checkpoint"])}
    for seed in SEEDS:
        model_runs = SEED_RUNS[seed]
        models[f"kd_seed{seed}"] = ROOT / "runs/kd" / model_runs["kd"] / "weights/best.pt"
        models[f"supervised_seed{seed}"] = ROOT / "runs/supervised" / model_runs["supervised"] / "weights/best.pt"
    return models


def verify_training_queue() -> dict[str, Path]:
    if not TRAINING_QUEUE.is_file():
        raise PipelineError(f"Training queue state is missing: {TRAINING_QUEUE}")
    queue = json.loads(TRAINING_QUEUE.read_text(encoding="utf-8"))
    if queue.get("status") != "complete":
        raise PipelineError(f"Training queue is not complete: {queue.get('status')}")
    expected_fingerprint = sha256_file(FINGERPRINT)
    if queue.get("fingerprint_sha256") != expected_fingerprint:
        raise PipelineError("Training queue references a different dataset fingerprint.")
    if queue.get("status") != "complete" or any(
        item.get("status") != "succeeded" for item in queue.get("items", [])
    ):
        raise PipelineError("At least one queue step is not marked succeeded.")

    checkpoints = expected_models()
    kd_implementation_sha256: str | None = None
    for label, checkpoint in checkpoints.items():
        if not checkpoint.is_file():
            raise PipelineError(f"Required checkpoint is missing: {checkpoint}")
        if label == "teacher_fp32":
            continue
        run_manifest_path = checkpoint.parent.parent / "manifest.json"
        if not run_manifest_path.is_file():
            raise PipelineError(f"Training manifest is missing: {run_manifest_path}")
        manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "complete" or manifest.get("test_split_used") is not False:
            raise PipelineError(f"Training manifest is incomplete or used TEST: {run_manifest_path}")
        if manifest.get("dataset_fingerprint_sha256") != expected_fingerprint:
            raise PipelineError(f"Training manifest has the wrong dataset fingerprint: {run_manifest_path}")
        if manifest.get("student_best_sha256") != sha256_file(checkpoint):
            raise PipelineError(f"Best checkpoint hash differs from its manifest: {checkpoint}")
        is_kd = label.startswith("kd_")
        seed = int(label.removeprefix("kd_seed").removeprefix("supervised_seed"))
        if manifest.get("seed") != seed or manifest.get("train_labels_used_for_loss") is not (not is_kd):
            raise PipelineError(f"Seed/objective metadata disagrees with model label: {label}")
        if is_kd:
            if "teacher-only" not in str(manifest.get("objective", "")):
                raise PipelineError(f"KD run is not declared teacher-only: {label}")
            implementation = manifest.get("distillation_implementation")
            if not isinstance(implementation, dict):
                raise PipelineError(f"KD implementation snapshot is missing: {label}")
            implementation_path = Path(str(implementation.get("path", ""))).expanduser().resolve()
            implementation_hash = implementation.get("sha256")
            expected_snapshot_timing = label != "kd_seed42"
            if (
                implementation.get("module") != "ultralytics.nn.distill_model"
                or not implementation_path.is_file()
                or not implementation_hash
                or sha256_file(implementation_path) != implementation_hash
                or implementation.get("snapshot_recorded_at_run_time") is not expected_snapshot_timing
                or manifest.get("training_script_snapshot_recorded_at_run_time") is not expected_snapshot_timing
            ):
                raise PipelineError(f"KD implementation snapshot is missing or invalid: {label}")
            if kd_implementation_sha256 is None:
                kd_implementation_sha256 = str(implementation_hash)
            elif kd_implementation_sha256 != implementation_hash:
                raise PipelineError("Final KD seeds use different DistillationModel implementations.")
        if not is_kd and "supervised" not in str(manifest.get("objective", "")):
            raise PipelineError(f"Control run is not declared supervised: {label}")
    return checkpoints


def wait_for_training(state: dict[str, Any]) -> None:
    state["status"] = "waiting_for_training_queue"
    state["updated_at_utc"] = now_utc()
    write_json(PIPELINE_STATE, state)
    print(f"Waiting for paired training queue: {TRAINING_QUEUE}", flush=True)
    last_progress_at = time.monotonic()
    last_signature: tuple[str, int, int] | None = None

    while True:
        if not TRAINING_QUEUE.is_file():
            raise PipelineError("Training queue state disappeared while waiting.")
        queue = json.loads(TRAINING_QUEUE.read_text(encoding="utf-8"))
        queue_status = queue.get("status")
        if queue_status == "complete":
            return
        if queue_status in {"failed", "interrupted"}:
            raise PipelineError(f"Training queue ended with status {queue_status}: {queue.get('error', '')}")

        running_item = next((item for item in queue.get("items", []) if item.get("status") == "running"), None)
        waiting_item = next((item for item in queue.get("items", []) if item.get("status") == "waiting"), None)
        run_dir_value = (running_item or waiting_item or {}).get("run_dir")
        if waiting_item and waiting_item.get("label") == "wait_supervised_seed42":
            run_dir_value = str(Path("runs/supervised") / str(QUEUE_CONFIG["initial_supervised_run"]))
        if run_dir_value:
            results_path = ROOT / run_dir_value / "results.csv"
            if results_path.is_file():
                stat = results_path.stat()
                signature = (str(results_path), stat.st_mtime_ns, stat.st_size)
                if signature != last_signature:
                    last_signature = signature
                    last_progress_at = time.monotonic()
                    try:
                        epoch = results_path.read_text(encoding="utf-8").splitlines()[-1].split(",", 1)[0]
                    except (OSError, IndexError):
                        epoch = "unknown"
                    print(f"Training queue active at {Path(run_dir_value).name}, epoch {epoch}.", flush=True)
                elif time.monotonic() - last_progress_at > STALE_SECONDS:
                    raise PipelineError("Training queue results.csv has not advanced for 30 minutes.")
            elif running_item and running_item.get("kind") != "provenance":
                if time.monotonic() - last_progress_at > STALE_SECONDS:
                    raise PipelineError("Training queue has no results.csv progress for 30 minutes.")
        elif time.monotonic() - last_progress_at > STALE_SECONDS:
            queue_mtime_age = time.time() - TRAINING_QUEUE.stat().st_mtime
            if queue_mtime_age > STALE_SECONDS:
                raise PipelineError("Training queue state has not advanced for 30 minutes.")

        time.sleep(POLL_SECONDS)


def run_stage(label: str, command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.is_file() and log_path.stat().st_size:
        archive_path = log_path.with_name(f"{log_path.stem}.previous-{time.time_ns()}{log_path.suffix}")
        shutil.copy2(log_path, archive_path)
        print(f"Archived previous stage log: {archive_path}", flush=True)
    print(f"Starting stage {label}; log: {log_path}", flush=True)
    with log_path.open("w", encoding="utf-8") as log_stream:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
            stdout=log_stream,
            stderr=subprocess.STDOUT,
        )
        while process.poll() is None:
            try:
                return_code = process.wait(timeout=60)
            except subprocess.TimeoutExpired:
                print(f"Stage {label} is still running.", flush=True)
                continue
        if process.returncode != 0:
            raise PipelineError(f"Stage {label} exited {process.returncode}; inspect {log_path}")


def run_locked_test(checkpoints: dict[str, Path]) -> None:
    if TEST_OUTPUT.exists():
        raise PipelineError(f"Refusing to reuse a TEST output directory: {TEST_OUTPUT}")
    command = [
        str(PYTHON), "scripts/evaluate_locked_test.py", "--models",
        *[f"{label}={path}" for label, path in checkpoints.items() if label != "teacher_fp32"],
        "--output", str(TEST_OUTPUT),
    ]
    prior_manifest = FAILED_TEST_ATTEMPT / "manifest.json"
    if prior_manifest.is_file():
        command.extend(["--retry-of-manifest", str(prior_manifest)])
    run_stage("locked_test_evaluation", command, LOG_DIR / "locked_test_evaluation.log")
    manifest_path = TEST_OUTPUT / "manifest.json"
    if not manifest_path.is_file():
        raise PipelineError(f"Locked TEST evaluator did not write a manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" or set(manifest.get("models", {})) != set(checkpoints):
        raise PipelineError("Locked TEST evaluation is incomplete or missing models.")


def run_benchmark(checkpoints: dict[str, Path]) -> None:
    if BENCHMARK_OUTPUT.exists():
        raise PipelineError(f"Refusing to overwrite a benchmark: {BENCHMARK_OUTPUT}")
    command = [
        str(PYTHON), "scripts/benchmark_inference.py", "--models",
        *[f"{label}={path}" for label, path in checkpoints.items()],
        "--data", str(ROOT / "configs/data_train_val.yaml"),
        "--device", "0", "--imgsz", "640", "--warmup", "30", "--iterations", "200",
        "--output", str(BENCHMARK_OUTPUT),
    ]
    run_stage("inference_benchmark", command, LOG_DIR / "inference_benchmark.log")
    benchmark = json.loads(BENCHMARK_OUTPUT.read_text(encoding="utf-8"))
    if set(benchmark.get("models", {})) != set(checkpoints):
        raise PipelineError("Inference benchmark is missing one or more locked models.")
    if benchmark.get("settings", {}).get("batch") != 1 or benchmark.get("settings", {}).get("precision") != "FP32":
        raise PipelineError("Inference benchmark settings differ from the frozen protocol.")


def run_analysis() -> None:
    if ANALYSIS_OUTPUT.exists():
        raise PipelineError(f"Refusing to overwrite an analysis directory: {ANALYSIS_OUTPUT}")
    command = [
        str(PYTHON), "scripts/build_thesis_analysis.py",
        "--test-manifest", str(TEST_OUTPUT / "manifest.json"),
        "--benchmark", str(BENCHMARK_OUTPUT),
        "--fingerprint", str(FINGERPRINT),
        "--output", str(ANALYSIS_OUTPUT),
    ]
    run_stage("thesis_analysis", command, LOG_DIR / "thesis_analysis.log")
    manifest_path = ANALYSIS_OUTPUT / "analysis_manifest.json"
    if not manifest_path.is_file() or json.loads(manifest_path.read_text(encoding="utf-8")).get("status") != "complete":
        raise PipelineError("Analysis output manifest is missing or incomplete.")


def load_or_create_state(*, resume: bool) -> dict[str, Any]:
    if PIPELINE_STATE.exists():
        if not resume:
            raise PipelineError(f"Pipeline state already exists; inspect it and use --resume only after a failed/interrupted wait stage: {PIPELINE_STATE}")
        state = json.loads(PIPELINE_STATE.read_text(encoding="utf-8"))
        if state.get("status") not in {"failed", "interrupted"}:
            raise PipelineError(f"Only a failed or interrupted pipeline can be resumed; current status is {state.get('status')}.")
        if state.get("fingerprint_sha256") != sha256_file(FINGERPRINT):
            raise PipelineError("Refusing to resume a pipeline with a different dataset fingerprint.")
        if TEST_OUTPUT.exists() or BENCHMARK_OUTPUT.exists() or ANALYSIS_OUTPUT.exists():
            raise PipelineError("Refusing automatic resume because a final evaluation artifact already exists; inspect outputs first.")
        prior_manifest_path = FAILED_TEST_ATTEMPT / "manifest.json"
        prior_attempt: dict[str, Any] | None = None
        if prior_manifest_path.is_file():
            prior_manifest = json.loads(prior_manifest_path.read_text(encoding="utf-8"))
            if (
                prior_manifest.get("status") != "failed"
                or prior_manifest.get("models") != {}
                or prior_manifest.get("error") != "AttributeError: 'dict' object has no attribute 'box'"
                or prior_manifest.get("dataset_fingerprint_sha256") != sha256_file(FINGERPRINT)
            ):
                raise PipelineError(
                    "Refusing retry because the prior TEST attempt contains model metrics or a different failure."
                )
            prior_attempt = {
                "manifest": str(prior_manifest_path),
                "manifest_sha256": sha256_file(prior_manifest_path),
                "status": prior_manifest["status"],
                "error": prior_manifest["error"],
                "models_with_metrics": [],
                "note": "Prior attempt scanned TEST labels but failed before recording any model metrics.",
            }
        stages = state.get("stages", {})
        retry_stage = None
        safe_test_preflight_retry = stages == {
            "locked_test_evaluation": "running",
            "inference_benchmark": "queued",
            "thesis_analysis": "queued",
        }
        if safe_test_preflight_retry:
            retry_stage = "locked_test_evaluation"
            state["stages"][retry_stage] = "queued"
        elif any(value != "queued" for value in stages.values()):
            raise PipelineError(
                "Automatic resume is allowed only when no final outputs exist and a failed locked TEST preflight is requeued."
            )
        state.setdefault("resume_history", []).append({
            "previous_status": state.get("status"),
            "previous_error": state.get("error"),
            "resumed_at_utc": now_utc(),
            "requeued_stage": retry_stage,
            "retry_reason": (
                "Locked TEST stage failed before producing model metrics; retry uses a new output directory."
                if retry_stage
                else None
            ),
            "prior_failed_test_attempt": prior_attempt,
        })
        if state.get("test_output") and state.get("test_output") != str(TEST_OUTPUT):
            state.setdefault("superseded_test_outputs", []).append(state["test_output"])
        if state.get("analysis_output") and state.get("analysis_output") != str(ANALYSIS_OUTPUT):
            state.setdefault("superseded_analysis_outputs", []).append(state["analysis_output"])
        state["test_output"] = str(TEST_OUTPUT)
        state["analysis_output"] = str(ANALYSIS_OUTPUT)
        state["benchmark_output"] = str(BENCHMARK_OUTPUT)
        state.pop("error", None)
        state["status"] = "waiting_for_training_queue"
        if prior_attempt is not None:
            state.setdefault("prior_failed_test_attempts", []).append(prior_attempt)
        state["updated_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)
        print(f"Resuming locked final pipeline. State: {PIPELINE_STATE}", flush=True)
        return state

    if resume:
        raise PipelineError(f"Cannot resume because pipeline state does not exist: {PIPELINE_STATE}")
    state: dict[str, Any] = {
        "created_at_utc": now_utc(),
        "status": "starting",
        "training_queue": str(TRAINING_QUEUE),
        "fingerprint_sha256": sha256_file(FINGERPRINT),
        "test_output": str(TEST_OUTPUT),
        "benchmark_output": str(BENCHMARK_OUTPUT),
        "analysis_output": str(ANALYSIS_OUTPUT),
        "stages": {"locked_test_evaluation": "queued", "inference_benchmark": "queued", "thesis_analysis": "queued"},
    }
    write_json(PIPELINE_STATE, state)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="resume after a failed/interrupted wait, preserving the locked stage state")
    args = parser.parse_args()
    if not PYTHON.is_file() or not FINGERPRINT.is_file():
        raise PipelineError("Experiment Python environment or dataset fingerprint is missing.")
    state = load_or_create_state(resume=args.resume)
    try:
        wait_for_training(state)
        checkpoints = verify_training_queue()
        state["status"] = "training_verified"
        state["checkpoints"] = {label: {"path": str(path), "sha256": sha256_file(path)} for label, path in checkpoints.items()}
        state["updated_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)

        state["status"] = "running_locked_test"
        state["stages"]["locked_test_evaluation"] = "running"
        state["updated_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)
        print("All six student runs passed provenance checks; beginning the single locked TEST evaluation.", flush=True)
        run_locked_test(checkpoints)
        state["stages"]["locked_test_evaluation"] = "complete"
        state["status"] = "running_benchmark"
        state["stages"]["inference_benchmark"] = "running"
        state["updated_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)

        run_benchmark(checkpoints)
        state["stages"]["inference_benchmark"] = "complete"
        state["status"] = "running_analysis"
        state["stages"]["thesis_analysis"] = "running"
        state["updated_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)

        run_analysis()
        state["stages"]["thesis_analysis"] = "complete"
        state["status"] = "complete"
        state["finished_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)
        print("Locked TEST evaluation, inference benchmark, and thesis analysis are complete.", flush=True)
        return 0
    except KeyboardInterrupt:
        state["status"] = "interrupted"
        state["updated_at_utc"] = now_utc()
        write_json(PIPELINE_STATE, state)
        print("Final pipeline interrupted; inspect stage outputs before resuming.", file=sys.stderr)
        return 130
    except Exception as error:
        state["status"] = "failed"
        state["updated_at_utc"] = now_utc()
        state["error"] = f"{type(error).__name__}: {error}"
        write_json(PIPELINE_STATE, state)
        print(state["error"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
