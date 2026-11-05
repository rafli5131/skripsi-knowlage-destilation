"""Queue the locked T42 teacher-size ablation without overwriting prior runs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    from .server_paths import data_root, t42_layout, training_python
except ImportError:
    from server_paths import data_root, t42_layout, training_python


ROOT = Path(__file__).resolve().parents[1]
# Default values match the original server; see scripts/server_paths.py for overrides.
PYTHON = training_python()
DATA_ROOT = str(data_root())
LAYOUT = t42_layout(ROOT)
PROJECT = LAYOUT.project
PRIVATE = LAYOUT.private
EVAL = LAYOUT.evaluation
STATUS = LAYOUT.status


def teacher_run_name(variant: str) -> str:
    # Legacy attempt: the first YOLO11n run stopped before epoch 1 and is preserved for audit.
    return LAYOUT.teacher_run_name(variant)


def record(event: str, **details: object) -> None:
    with STATUS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": event, "time_utc": datetime.now(timezone.utc).isoformat(),
                                 **details}, sort_keys=True) + "\n")


def gpu_snapshot() -> list[tuple[int, int, int]]:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    )
    return [tuple(int(part.strip()) for part in row.split(","))
            for row in result.stdout.splitlines() if row.strip()]


def wait_for_gpu() -> int:
    last: int | None = None
    stable = 0
    while True:
        try:
            candidates = [(used, index) for index, used, utilization in gpu_snapshot()
                          if used <= 8000 and utilization <= 25]
        except (OSError, subprocess.CalledProcessError, ValueError) as error:
            candidates = []
            record("gpu_probe_unavailable", error=str(error))
        selected = min(candidates)[1] if candidates else None
        stable = stable + 1 if selected is not None and selected == last else 1 if selected is not None else 0
        last = selected
        if stable >= 2 and selected is not None:
            record("gpu_available", physical_index=selected)
            return selected
        time.sleep(60)


def gpu_process_memory(pid: int) -> int | None:
    result = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,used_gpu_memory", "--format=csv,noheader,nounits"],
        capture_output=True, text=True,
    )
    if result.returncode:
        return None
    for row in result.stdout.splitlines():
        parts = [part.strip() for part in row.split(",")]
        if len(parts) >= 2 and parts[0] == str(pid):
            try:
                return int(parts[1])
            except ValueError:
                return None
    return None


def run_step(name: str, command: list[str], *, gpu: bool) -> None:
    log = PROJECT / "logs" / f"{name}.log"
    if log.exists():
        raise FileExistsError(f"Refusing to overwrite T42 log: {log}")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    selected = wait_for_gpu() if gpu else None
    if selected is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(selected)
    env["WANDB_MODE"] = "disabled"
    record("step_started", name=name, command=command, physical_gpu=selected, log=str(log))
    started = time.monotonic()
    peak_mib = 0
    with log.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        while process.poll() is None:
            if gpu:
                memory = gpu_process_memory(process.pid)
                peak_mib = max(peak_mib, memory or 0)
            time.sleep(20)
        code = process.wait()
    record("step_finished" if code == 0 else "step_failed", name=name, exit_code=code,
           elapsed_seconds=time.monotonic() - started, gpu_process_peak_mib=peak_mib, log=str(log))
    if code:
        raise RuntimeError(f"T42 step failed ({code}): {name}; inspect {log}")


def evaluate(label: str, checkpoint: Path, manifest: Path, step_name: str | None = None) -> None:
    output = EVAL / f"{label}_val.json"
    if output.exists():
        raise FileExistsError(f"T42 VAL result already exists: {output}")
    run_step(step_name or f"eval_{label}", [PYTHON, str(ROOT / "scripts/evaluate_t42_val.py"),
                               "--checkpoint", str(checkpoint), "--manifest", str(manifest),
                               "--label", label, "--output-dir", str(EVAL)], gpu=False)


def student_config(variant: str, seed: int) -> Path:
    source = yaml.safe_load((ROOT / "configs/kd_hybrid_full.yaml").read_text(encoding="utf-8"))
    run_name = f"student_teacher_yolo11{variant}_seed{seed}"
    source["teacher_checkpoint"] = str(PRIVATE / teacher_run_name(variant) / "weights/best.pt")
    source["run"] = {"project": PROJECT.relative_to(ROOT).as_posix(), "name": run_name}
    source["training"]["seed"] = seed
    output = LAYOUT.student_config_path(run_name)
    if output.exists():
        raise FileExistsError(f"T42 config already exists: {output}")
    output.write_text(yaml.safe_dump(source, sort_keys=False), encoding="utf-8")
    return output


def main() -> None:
    if (ROOT / "analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md").exists():
        raise FileExistsError("T42 already completed; do not overwrite it")
    PROJECT.mkdir(parents=True, exist_ok=True)
    (PROJECT / "logs").mkdir(exist_ok=True)
    EVAL.mkdir(parents=True, exist_ok=True)
    baseline = hashlib.sha256((ROOT / "configs/kd_hybrid_full.yaml").read_bytes()).hexdigest()
    if STATUS.exists() and LAYOUT.attempt:
        raise RuntimeError(f"Status T42 percobaan {LAYOUT.attempt!r} sudah ada; audit dulu atau pakai T42_ATTEMPT baru")
    if STATUS.exists():
        events = [json.loads(line) for line in STATUS.read_text(encoding="utf-8").splitlines()]
        failed = [event for event in events if event["event"] == "step_failed"]
        if (events[-1]["event"] != "t42_failed" or len(failed) != 1
                or failed[0]["name"] != "train_teacher_yolo11n_seed42"
                or any(event["event"] == "step_finished" for event in events)):
            raise RuntimeError("T42 status is not the documented first preflight failure; inspect before resuming")
        record("t42_resumed", failed_run_preserved="teacher_yolo11n_seed42",
               new_run="teacher_yolo11n_seed42_retry1", reason="CUDA peak counter called before training")
    else:
        record("t42_started", recipe_sha256=baseline, teachers=["yolo11n", "yolo11s"],
               student_mode="hybrid_full", student_seeds=[42, 1337, 2025], split="TRAIN/VAL only",
               attempt=LAYOUT.attempt or "legacy", training_python=PYTHON, data_root=DATA_ROOT)
    try:
        for variant in ("n", "s"):
            label = f"teacher_yolo11{variant}_seed42"
            run_name = teacher_run_name(variant)
            command = [PYTHON, str(ROOT / "scripts/train_t42_teacher.py"), "--variant", variant]
            if run_name != label:
                command += ["--run-name", run_name]
            run_step(f"train_{run_name}", command, gpu=True)
            run_dir = PRIVATE / run_name
            evaluate(label, run_dir / "weights/best.pt", run_dir / "manifest.json")
        for variant in ("n", "s"):
            for seed in (42, 1337, 2025):
                label = f"student_teacher_yolo11{variant}_seed{seed}"
                config = student_config(variant, seed)
                run_step(f"train_{label}", [PYTHON, str(ROOT / "scripts/train_kd.py"),
                                            "--config", str(config), "--data-root", DATA_ROOT], gpu=True)
                run_dir = PROJECT / label
                evaluate(label, run_dir / "weights/best.pt", run_dir / "manifest.json")
        run_step("build_t42", [PYTHON, str(ROOT / "scripts/build_t42_teacher_ablation.py")], gpu=False)
        record("t42_complete", table=str(ROOT / "analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md"))
    except BaseException as error:
        record("t42_failed", error=f"{type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
