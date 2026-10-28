"""Train a private, matched-recipe YOLO11 teacher for the T42 VAL ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

try:
    from .experiment_paths import resolve_training_data, write_resolved_data_yaml
    from .training_runtime import verify_training_runtime
except ImportError:
    from experiment_paths import resolve_training_data, write_resolved_data_yaml
    from training_runtime import verify_training_runtime


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human")
PRIVATE = ROOT / "models_local/teacher_ablation_t42"
PRETRAINED_HASH = {
    "n": "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1",
    "s": "85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("n", "s"), required=True)
    parser.add_argument("--run-name", help="Unique run directory for a documented retry")
    args = parser.parse_args()
    runtime = verify_training_runtime()
    source = PRIVATE / "pretrained" / f"yolo11{args.variant}.pt"
    if sha256(source) != PRETRAINED_HASH[args.variant]:
        raise RuntimeError(f"Official YOLO11{args.variant} pretrained hash mismatch")
    run_name = args.run_name or f"teacher_yolo11{args.variant}_seed42"
    if Path(run_name).name != run_name or run_name in {".", ".."}:
        raise ValueError("Run name must be a single directory name")
    run_dir = PRIVATE / "training" / run_name
    if run_dir.exists():
        raise FileExistsError(f"Refusing to overwrite teacher run: {run_dir}")
    data_yaml, data, data_meta = resolve_training_data(
        ROOT / "configs/data_train_val.yaml", run_dir,
        ROOT / "artifacts/advance_vision_dataset_fingerprint.json", DATA_ROOT,
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    write_resolved_data_yaml(data_yaml, data)
    started = datetime.now(timezone.utc)
    start = time.monotonic()
    model = YOLO(str(source), task="detect")
    result = model.train(
        data=str(data_yaml), epochs=100, batch=16, workers=2, imgsz=640,
        device="0", seed=42, optimizer="AdamW", lr0=0.001, lrf=0.01,
        warmup_epochs=3.0, weight_decay=0.0005, close_mosaic=10,
        amp=False, patience=30, pretrained=True, val=True, plots=False,
        save=True, project=str(run_dir.parent), name=run_name,
        exist_ok=True, compile=False,
    )
    checkpoint = run_dir / "weights/best.pt"
    if not checkpoint.is_file():
        raise RuntimeError(f"Teacher training produced no best.pt: {checkpoint}")
    trained = YOLO(str(checkpoint), task="detect").model
    names = {int(k): str(v) for k, v in trained.names.items()}
    if names != {0: "ball", 1: "gawang", 2: "robot"}:
        raise RuntimeError(f"Teacher class mapping changed: {names}")
    manifest = {
        "status": "complete", "kind": "matched_teacher_training_t42",
        "variant": f"yolo11{args.variant}", "seed": 42,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": time.monotonic() - start,
        "pretrained_source_url": f"https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11{args.variant}.pt",
        "pretrained_checkpoint": str(source), "pretrained_sha256": sha256(source),
        "teacher_best_checkpoint": str(checkpoint), "teacher_best_sha256": sha256(checkpoint),
        "teacher_parameters": sum(p.numel() for p in trained.parameters()),
        "gpu_peak_allocated_bytes": torch.cuda.max_memory_allocated(0),
        "gpu_peak_reserved_bytes": torch.cuda.max_memory_reserved(0),
        "data_yaml": str(data_yaml), "data_yaml_sha256": sha256(data_yaml),
        "dataset_fingerprint_sha256": sha256(ROOT / "artifacts/advance_vision_dataset_fingerprint.json"),
        "dataset_split_fingerprints_verified": data_meta["dataset_split_fingerprints_verified"],
        "training": {"epochs": 100, "batch": 16, "workers": 2, "imgsz": 640,
                     "optimizer": "AdamW", "lr0": 0.001, "lrf": 0.01,
                     "warmup_epochs": 3.0, "weight_decay": 0.0005,
                     "close_mosaic": 10, "amp": False, "patience": 30,
                     "pretrained": True},
        "validation_split": "VAL only", "test_split_used": False,
        "distillation": {"mode": "teacher_supervised_pretrained"},
        "ultralytics_metrics": getattr(result, "results_dict", {}),
        "runtime": runtime, "versions": {"python": platform.python_version(),
                                         "torch": torch.__version__, "ultralytics": ultralytics.__version__},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(checkpoint)


if __name__ == "__main__":
    main()
