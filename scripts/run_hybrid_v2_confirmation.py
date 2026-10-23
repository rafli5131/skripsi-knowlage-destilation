"""Train S2 on seeds 1337/2025 and build paired VAL confirmation T41."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "runs/kd_hybrid_v2"
EVAL = ROOT / "runs/val_ablation/hybrid_v2_20261023"
PYTHON = "/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python"
STATUS = PROJECT / "confirmation_s2_status.jsonl"
BASE_CONFIG = ROOT / "configs/kd_hybrid_v2_s2.yaml"


def record(event: str, **details: object) -> None:
    with STATUS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": event, "time_utc": datetime.now(timezone.utc).isoformat(), **details}, sort_keys=True) + "\n")


def main() -> None:
    if STATUS.exists():
        raise FileExistsError(f"Confirmation already started: {STATUS}")
    screen = (PROJECT / "screen_s4_s8_status.jsonl").read_text(encoding="utf-8")
    if '"event": "screen_s1_s8_complete"' not in screen or '"best_stage": "s2"' not in screen:
        raise RuntimeError("S2 must first win the locked S1-S8 VAL screen")
    base = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    first = json.loads((PROJECT / "yolo11_tiny_hybrid_v2_s2_seed42/manifest.json").read_text(encoding="utf-8"))
    import hashlib
    current_source_hash = hashlib.sha256((ROOT / "scripts/train_kd.py").read_bytes()).hexdigest()
    if first["training_script_sha256"] != current_source_hash:
        raise RuntimeError("Training implementation changed since seed 42")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    record("confirmation_started", candidate="s2", seeds=[1337, 2025], training_script_sha256=current_source_hash)
    try:
        for seed in (1337, 2025):
            config = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
            config["training"]["seed"] = seed
            config["run"]["name"] = f"yolo11_tiny_hybrid_v2_s2_seed{seed}"
            for section in ("teacher_checkpoint", "student_model", "data_yaml", "distillation"):
                if config[section] != base[section]:
                    raise RuntimeError(f"Seed {seed} changes locked {section}")
            config_path = ROOT / f"configs/kd_hybrid_v2_s2_seed{seed}.yaml"
            run = PROJECT / config["run"]["name"]
            pending = PROJECT / f".{run.name}.manifest.json"
            result_path = EVAL / f"{run.name}_val.json"
            if config_path.exists() or run.exists() or pending.exists() or result_path.exists():
                raise FileExistsError(f"Refusing to overwrite seed {seed} artifacts")
            with config_path.open("x", encoding="utf-8") as stream:
                yaml.safe_dump(config, stream, sort_keys=False)
            record("training_started", seed=seed, config=str(config_path))
            log = PROJECT / f"s2_seed{seed}_train.log"
            with log.open("x", encoding="utf-8") as stream:
                subprocess.run([PYTHON, str(ROOT / "scripts/train_kd.py"), "--config", str(config_path)],
                               cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True)
            manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
            if manifest["status"] != "complete" or manifest["training_script_sha256"] != current_source_hash:
                raise RuntimeError(f"Seed {seed} training manifest failed or code changed")
            record("training_complete", seed=seed, checkpoint=manifest["student_best_checkpoint"])
            record("evaluation_started", seed=seed)
            log = EVAL / f"s2_seed{seed}_eval.log"
            with log.open("x", encoding="utf-8") as stream:
                subprocess.run([PYTHON, str(ROOT / "scripts/evaluate_hybrid_v2_val.py"), "--run-dir", str(run),
                                "--output-dir", str(EVAL)], cwd=ROOT, env=env,
                               stdout=stream, stderr=subprocess.STDOUT, check=True)
            if not result_path.is_file():
                raise RuntimeError(f"Seed {seed} VAL result missing")
            record("evaluation_complete", seed=seed, val_json=str(result_path))
        subprocess.run([PYTHON, str(ROOT / "scripts/build_t41_hybrid_v2_val.py")], cwd=ROOT, env=env, check=True)
        record("confirmation_complete", table=str(ROOT / "analisis_performa/tabel/T41_konfirmasi_hybrid_v2_val.md"))
    except BaseException as error:
        record("confirmation_failed", error=f"{type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
