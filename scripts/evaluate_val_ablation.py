"""Evaluate the pure_v4 and pure_weighted best checkpoints on locked VAL only.

This script does not use TEST or train models. It records both Ultralytics AP
metrics and a fixed-confidence operating point for each of the three classes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from types import MethodType

import numpy as np
import torch
import ultralytics
import yaml
from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG, get_cfg
from ultralytics.data.build import build_dataloader
from ultralytics.models.yolo.detect.val import DetectionValidator

try:
    from .analyze_val_detections import DATA_YAML, NAMES, ROOT, source_paths, verify_val_bytes
    from .evaluate_locked_test import ReadOnlyTestDataset
except ImportError:
    from analyze_val_detections import DATA_YAML, NAMES, ROOT, source_paths, verify_val_bytes
    from evaluate_locked_test import ReadOnlyTestDataset


OUT = ROOT / "runs/val_ablation/pure_weighted_20261020"
BASELINES = ("kd_seed42", "kd_seed1337", "kd_seed2025")
PILOT = "pure_weighted_seed42"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkpoint_and_manifest(label: str) -> tuple[Path, Path, dict]:
    if label == PILOT:
        manifest_path = ROOT / "runs/kd/yolo11_tiny_pure_weighted_pilot_seed42/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        checkpoint = Path(manifest["student_best_checkpoint"])
        expected = manifest["student_best_sha256"]
    else:
        registry = yaml.safe_load((ROOT / "configs/model_registry.yaml").read_text(encoding="utf-8"))["models"]
        record = registry[label]
        manifest_path = Path(record["manifest"])
        checkpoint = Path(record["checkpoint"])
        expected = record["sha256"]
        if not manifest_path.is_absolute():
            manifest_path = ROOT / manifest_path
    if not checkpoint.is_absolute():
        checkpoint = ROOT / checkpoint
    checkpoint = checkpoint.resolve()
    if label == PILOT and manifest["status"] != "complete":
        raise RuntimeError("Pilot training manifest is not complete")
    if sha256(checkpoint) != expected:
        raise RuntimeError(f"Checkpoint hash mismatch: {label}")
    return checkpoint, manifest_path.resolve(), json.loads(manifest_path.read_text(encoding="utf-8"))


def evaluate(label: str, images: Path, expected_images: set[str], fingerprint: dict,
             threads: int, device: torch.device) -> Path:
    cp, manifest_path, run_manifest = checkpoint_and_manifest(label)
    torch.set_num_threads(threads)
    model = YOLO(str(cp), task="detect").model
    if {int(k): str(v) for k, v in model.names.items()} != NAMES:
        raise RuntimeError(f"Class mapping differs from expected: {label}")
    model.to(device).float().eval()
    cfg = get_cfg(DEFAULT_CFG, {
        "task": "detect", "mode": "val", "split": "val", "data": str(DATA_YAML),
        "imgsz": 640, "batch": 16, "workers": 0,
        "device": "cpu" if device.type == "cpu" else "0", "cache": False,
        "fraction": 1.0, "rect": True, "augment": False, "amp": False,
        "plots": False, "save_json": False, "save_txt": False, "conf": 0.001,
        "iou": 0.7, "verbose": False, "compile": False,
    })
    dataset = ReadOnlyTestDataset(
        img_path=str(images), imgsz=cfg.imgsz, batch_size=cfg.batch, augment=False,
        hyp=copy.copy(cfg), rect=True, cache=False, single_cls=False,
        stride=max(int(model.stride.max()), 32), pad=0.5, prefix="val: ",
        task="detect", classes=None, data=yaml.safe_load(DATA_YAML.read_text(encoding="utf-8")),
        fraction=1.0, external_cache_path=OUT / ".val_labels.cache",
    )
    loader = build_dataloader(dataset, batch=cfg.batch, workers=0, shuffle=False,
                              rank=-1, drop_last=False, device=device)
    validator = DetectionValidator(loader, save_dir=OUT / label, args=copy.copy(cfg))
    pred_count = np.zeros(3, dtype=int)
    tp_count = np.zeros(3, dtype=int)
    gt_count = np.zeros(3, dtype=int)
    seen = set()
    original = validator._process_batch

    def capture(self: DetectionValidator, preds: dict, batch: dict) -> dict:
        stats = original(preds, batch)
        name = Path(batch["im_file"]).name
        if name in seen:
            raise RuntimeError(f"Duplicate VAL image: {name}")
        seen.add(name)
        pc = preds["cls"].cpu().numpy().astype(int)
        conf = preds["conf"].cpu().numpy()
        tp = stats["tp"][:, 0]
        gc = batch["cls"].cpu().numpy().astype(int)
        for cls in NAMES:
            selected = (pc == cls) & (conf > 0.25)
            pred_count[cls] += int(selected.sum())
            tp_count[cls] += int(tp[selected].sum())
            gt_count[cls] += int((gc == cls).sum())
        return stats

    validator._process_batch = MethodType(capture, validator)
    try:
        validator(model=model)
    finally:
        if hasattr(loader, "close"):
            loader.close()
    if seen != expected_images:
        raise RuntimeError(f"VAL inventory mismatch for {label}: {len(seen)}")

    class_metrics = validator.metrics.box
    by_class = {}
    for idx, cls in enumerate(class_metrics.ap_class_index):
        cls = int(cls)
        precision_fixed = tp_count[cls] / pred_count[cls] if pred_count[cls] else 0.0
        recall_fixed = tp_count[cls] / gt_count[cls] if gt_count[cls] else 0.0
        f1_fixed = (2 * precision_fixed * recall_fixed / (precision_fixed + recall_fixed)
                    if precision_fixed + recall_fixed else 0.0)
        by_class[NAMES[cls]] = {
            "ground_truth_count": int(gt_count[cls]),
            "precision_conf025": precision_fixed, "recall_conf025": recall_fixed,
            "F1_conf025": f1_fixed, "AP50": float(class_metrics.ap50[idx]),
            "AP50_95": float(class_metrics.ap[idx]),
            "validator_precision": float(class_metrics.p[idx]),
            "validator_recall": float(class_metrics.r[idx]),
        }
    precision = float(np.mean([item["precision_conf025"] for item in by_class.values()]))
    recall = float(np.mean([item["recall_conf025"] for item in by_class.values()]))
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    payload = {
        "model": label, "checkpoint": str(cp), "checkpoint_sha256": sha256(cp),
        "training_manifest": str(manifest_path), "training_manifest_sha256": sha256(manifest_path),
        "training_mode": run_manifest.get("distillation", {}).get("mode", "pure_v4"),
        "val_split_fingerprint_sha256": fingerprint["split_fingerprint_sha256"],
        "images": len(seen), "ultralytics": ultralytics.__version__,
        "settings": {"imgsz": 640, "batch": 16, "rect": True, "augment": False,
                     "confidence_floor_for_AP": 0.001, "nms_iou": 0.7,
                     "fixed_confidence": 0.25, "match_iou": 0.5, "device": str(device),
                     "threads": threads},
        "validator_metrics": validator.metrics.results_dict,
        "fixed_confidence_metrics": {"precision_macro": precision, "recall_macro": recall, "F1_macro": f1},
        "per_class": by_class,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    path = OUT / f"{label}_val.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", choices=(*BASELINES, PILOT), default=[*BASELINES, PILOT])
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--device", choices=("cpu", "cuda:0"), default="cpu")
    args = parser.parse_args()
    if args.threads < 1:
        raise ValueError("threads must be positive")
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA device was requested but is unavailable")
    images, expected, fingerprint = source_paths()
    verify_val_bytes(fingerprint)
    OUT.mkdir(parents=True, exist_ok=True)
    for label in args.models:
        path = OUT / f"{label}_val.json"
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing VAL result: {path}")
        print(f"Evaluating {label} on locked VAL", flush=True)
        print(evaluate(label, images, expected, fingerprint, args.threads, device), flush=True)


if __name__ == "__main__":
    main()
