"""Capture frozen VAL predictions and build diagnosis tables T09/T10/T11/T14.

Uses the same Ultralytics DetectionValidator settings as the locked TEST evaluator.
No training or TEST images are used by this script.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import MethodType
from typing import Any

import numpy as np
import torch
import ultralytics
import yaml
from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG, get_cfg
from ultralytics.data.build import build_dataloader
from ultralytics.models.yolo.detect.val import DetectionValidator

try:
    from .evaluate_locked_test import ReadOnlyTestDataset
    from .model_registry import validate_checkpoint
except ImportError:
    from evaluate_locked_test import ReadOnlyTestDataset
    from model_registry import validate_checkpoint


ROOT = Path(__file__).resolve().parents[1]
DATA_YAML = ROOT / "configs/data_train_val.yaml"
FINGERPRINT = ROOT / "artifacts/advance_vision_dataset_fingerprint.json"
REGISTRY = ROOT / "configs/model_registry.yaml"
OUT = ROOT / "runs/val_diagnostics/official_split_20261020"
TABLES = ROOT / "analisis_performa/tabel"
NAMES = {0: "ball", 1: "gawang", 2: "robot"}
MODELS = (
    "teacher_fp32",
    "kd_seed42", "kd_seed1337", "kd_seed2025",
    "supervised_seed42", "supervised_seed1337", "supervised_seed2025",
)
THRESHOLDS = [round(i * 0.05, 2) for i in range(1, 19)]
OPERATING_CONFIDENCE = 0.25
MATCH_IOU = 0.5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", choices=MODELS, default=list(MODELS))
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--threads", type=int, default=8)
    return parser.parse_args()


def registry_models() -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return data["models"]


def source_paths() -> tuple[Path, set[str], dict[str, Any]]:
    data = yaml.safe_load(DATA_YAML.read_text(encoding="utf-8"))
    images = Path(data["val"]).resolve()
    fingerprint = json.loads(FINGERPRINT.read_text(encoding="utf-8"))["splits"]["val"]
    expected = {item["image"] for item in fingerprint["files"]}
    actual = {path.name for path in images.iterdir() if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}}
    if actual != expected or len(expected) != fingerprint["image_count"]:
        raise RuntimeError("VAL image inventory differs from its locked fingerprint")
    return images, expected, fingerprint


def verify_val_bytes(fingerprint: dict[str, Any]) -> None:
    """Check VAL image and label bytes against the previously locked inventory."""
    images = Path(fingerprint["images_dir"])
    labels = images.parent / "labels"
    for item in fingerprint["files"]:
        if sha256(images / item["image"]) != item["image_sha256"]:
            raise RuntimeError(f"VAL image changed: {item['image']}")
        if sha256(labels / item["label"]) != item["label_sha256"]:
            raise RuntimeError(f"VAL label changed: {item['label']}")


def capture_one(label: str, output: Path, images: Path, expected: set[str], fingerprint: dict[str, Any], threads: int) -> None:
    checkpoint = Path(registry_models()[label]["checkpoint"])
    if not checkpoint.is_absolute():
        checkpoint = ROOT / checkpoint
    checkpoint = checkpoint.resolve()
    validate_checkpoint(checkpoint, label=label)
    torch.set_num_threads(threads)
    model = YOLO(str(checkpoint), task="detect").model
    if {int(k): str(v) for k, v in model.names.items()} != NAMES:
        raise RuntimeError(f"Unexpected class mapping in {label}")
    model.to(torch.device("cpu")).float().eval()
    cfg = get_cfg(DEFAULT_CFG, {
        "task": "detect", "mode": "val", "split": "val", "data": str(DATA_YAML),
        "imgsz": 640, "batch": 16, "workers": 0, "device": "cpu", "cache": False,
        "fraction": 1.0, "rect": True, "augment": False, "amp": False,
        "plots": False, "save_json": False, "save_txt": False, "conf": 0.001,
        "iou": 0.7, "verbose": False, "compile": False,
    })
    dataset = ReadOnlyTestDataset(
        img_path=str(images), imgsz=cfg.imgsz, batch_size=cfg.batch, augment=False,
        hyp=copy.copy(cfg), rect=True, cache=False, single_cls=False,
        stride=max(int(model.stride.max()), 32), pad=0.5, prefix="val: ",
        task="detect", classes=None, data=yaml.safe_load(DATA_YAML.read_text(encoding="utf-8")),
        fraction=1.0, external_cache_path=output / ".val_labels.cache",
    )
    loader = build_dataloader(dataset, batch=cfg.batch, workers=0, shuffle=False,
                              rank=-1, drop_last=False, device=torch.device("cpu"))
    validator = DetectionValidator(loader, save_dir=output / label, args=copy.copy(cfg))
    records: list[dict[str, Any]] = []
    original = validator._process_batch

    def capture(self: DetectionValidator, preds: dict[str, torch.Tensor], batch: dict[str, Any]) -> dict[str, np.ndarray]:
        stats = original(preds, batch)
        records.append({
            "image": Path(batch["im_file"]).name,
            "image_shape": [int(x) for x in batch["imgsz"]],
            "gt_cls": batch["cls"].cpu().numpy().astype(int).tolist(),
            "gt_xyxy": batch["bboxes"].cpu().numpy().tolist(),
            "pred_cls": preds["cls"].cpu().numpy().astype(int).tolist(),
            "pred_conf": preds["conf"].cpu().numpy().tolist(),
            "pred_xyxy": preds["bboxes"].cpu().numpy().tolist(),
            "tp_iou50_validator": stats["tp"][:, 0].astype(int).tolist(),
        })
        return stats

    validator._process_batch = MethodType(capture, validator)
    try:
        validator(model=model)
    finally:
        if hasattr(loader, "close"):
            loader.close()
    seen = {record["image"] for record in records}
    if len(records) != len(expected) or seen != expected:
        raise RuntimeError(f"Incomplete VAL capture for {label}: {len(records)} records / {len(seen)} unique")
    payload = {
        "model": label, "checkpoint": str(checkpoint), "checkpoint_sha256": sha256(checkpoint),
        "val_split_fingerprint_sha256": fingerprint["split_fingerprint_sha256"],
        "dataset_fingerprint_sha256": sha256(FINGERPRINT),
        "data_yaml_sha256": sha256(DATA_YAML), "ultralytics": ultralytics.__version__,
        "settings": {"imgsz": 640, "batch": 16, "rect": True, "augment": False,
                     "confidence_floor": 0.001, "nms_iou": 0.7, "device": "cpu", "threads": threads},
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "images": sorted(records, key=lambda row: row["image"]),
    }
    path = output / f"{label}_predictions.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    temporary.replace(path)
    print(f"Captured {label}: {len(records)} VAL images -> {path}", flush=True)


def iou_matrix(gt: np.ndarray, pred: np.ndarray) -> np.ndarray:
    if not len(gt) or not len(pred):
        return np.zeros((len(gt), len(pred)), dtype=float)
    top_left = np.maximum(gt[:, None, :2], pred[None, :, :2])
    bottom_right = np.minimum(gt[:, None, 2:], pred[None, :, 2:])
    intersection = np.prod(np.maximum(bottom_right - top_left, 0), axis=2)
    ga = np.prod(np.maximum(gt[:, 2:] - gt[:, :2], 0), axis=1)
    pa = np.prod(np.maximum(pred[:, 2:] - pred[:, :2], 0), axis=1)
    return intersection / np.maximum(ga[:, None] + pa[None, :] - intersection, 1e-9)


def image_matches(record: dict[str, Any]) -> tuple[Counter[str], Counter[tuple[str, str]]]:
    gt_cls = np.asarray(record["gt_cls"], dtype=int)
    pred_cls_all = np.asarray(record["pred_cls"], dtype=int)
    conf_all = np.asarray(record["pred_conf"], dtype=float)
    selected = np.flatnonzero(conf_all > OPERATING_CONFIDENCE)
    pred_cls = pred_cls_all[selected]
    pred_conf = conf_all[selected]
    gt_boxes = np.asarray(record["gt_xyxy"], dtype=float).reshape(-1, 4)
    pred_boxes = np.asarray(record["pred_xyxy"], dtype=float).reshape(-1, 4)[selected]
    iou = iou_matrix(gt_boxes, pred_boxes)
    matched_gt: set[int] = set()
    matched_pred: set[int] = set()
    correct_gt: set[int] = set()
    counts: Counter[str] = Counter()
    confusion: Counter[tuple[str, str]] = Counter()

    for p in np.argsort(-pred_conf):
        candidates = [g for g in range(len(gt_cls)) if g not in matched_gt and gt_cls[g] == pred_cls[p]]
        if candidates:
            best = max(candidates, key=lambda g: iou[g, p])
            if iou[best, p] >= MATCH_IOU:
                matched_gt.add(best)
                correct_gt.add(best)
                matched_pred.add(int(p))
                confusion[(NAMES[int(gt_cls[best])], NAMES[int(pred_cls[p])])] += 1

    wrong_pairs = sorted(
        ((float(iou[g, p]), g, p) for g in range(len(gt_cls)) for p in range(len(pred_cls))
         if g not in matched_gt and p not in matched_pred and gt_cls[g] != pred_cls[p] and iou[g, p] >= MATCH_IOU),
        reverse=True,
    )
    for _, g, p in wrong_pairs:
        if g not in matched_gt and p not in matched_pred:
            matched_gt.add(g)
            matched_pred.add(p)
            counts["fp_wrong_class_count"] += 1
            confusion[(NAMES[int(gt_cls[g])], NAMES[int(pred_cls[p])])] += 1

    for p in range(len(pred_cls)):
        if p in matched_pred:
            continue
        same = [g for g in range(len(gt_cls)) if gt_cls[g] == pred_cls[p]]
        maximum = max((float(iou[g, p]) for g in same), default=0.0)
        if maximum >= MATCH_IOU:
            counts["fp_duplicate_count"] += 1
        elif maximum >= 0.1:
            counts["fp_localization_count"] += 1
        else:
            counts["fp_background_count"] += 1
        confusion[("background", NAMES[int(pred_cls[p])])] += 1

    for g in range(len(gt_cls)):
        if g not in correct_gt:
            area = float(np.prod(np.maximum(gt_boxes[g, 2:] - gt_boxes[g, :2], 0)))
            size = "small" if area < 1024 else "medium" if area <= 9216 else "large"
            counts[f"fn_{size}_count"] += 1
        if g not in matched_gt:
            confusion[(NAMES[int(gt_cls[g])], "background")] += 1
    counts["prediction_count"] += len(pred_cls)
    counts["correct_count"] += len(correct_gt)
    return counts, confusion


def operating_metrics(records: list[dict[str, Any]], threshold: float) -> dict[str, float]:
    pred_counts = np.zeros(3, dtype=int)
    true_counts = np.zeros(3, dtype=int)
    gt_counts = np.zeros(3, dtype=int)
    for row in records:
        pc = np.asarray(row["pred_cls"], dtype=int)
        conf = np.asarray(row["pred_conf"], dtype=float)
        tp = np.asarray(row["tp_iou50_validator"], dtype=bool)
        gc = np.asarray(row["gt_cls"], dtype=int)
        for cls in NAMES:
            sel = (pc == cls) & (conf > threshold)
            pred_counts[cls] += int(sel.sum())
            true_counts[cls] += int(tp[sel].sum())
            gt_counts[cls] += int((gc == cls).sum())
    precision_by_class = np.divide(true_counts, pred_counts, out=np.zeros(3), where=pred_counts > 0)
    recall_by_class = np.divide(true_counts, gt_counts, out=np.zeros(3), where=gt_counts > 0)
    precision = float(precision_by_class.mean())
    recall = float(recall_by_class.mean())
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "F1": f1,
            "detections_per_image": float(pred_counts.sum() / len(records))}


def calibration(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float]:
    confidence = np.concatenate([np.asarray(row["pred_conf"], dtype=float) for row in records])
    correct = np.concatenate([np.asarray(row["tp_iou50_validator"], dtype=bool) for row in records])
    selected = confidence > OPERATING_CONFIDENCE
    confidence, correct = confidence[selected], correct[selected]
    bins: list[dict[str, Any]] = []
    ece = 0.0
    for index in range(10):
        lo, hi = index / 10, (index + 1) / 10
        in_bin = (confidence >= lo) & (confidence < hi if index < 9 else confidence <= hi)
        n = int(in_bin.sum())
        mean_conf = float(confidence[in_bin].mean()) if n else math.nan
        precision = float(correct[in_bin].mean()) if n else math.nan
        if n:
            ece += n / len(confidence) * abs(mean_conf - precision)
        bins.append({"confidence_bin_lower": lo, "confidence_bin_upper": hi,
                     "mean_confidence": mean_conf, "empirical_precision": precision,
                     "detection_count": n})
    return bins, ece


def write_table(path: Path, rows: list[dict[str, Any]], note: str) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path}")
    columns = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    title = path.stem.replace("_", " ")
    lines = [f"# {title}", "", "Status: Lengkap dari diagnosis tujuh checkpoint pada VAL Roboflow resmi.", "",
             "| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        values = []
        for key in columns:
            value = row[key]
            values.append("[TIDAK ADA DETEKSI]" if isinstance(value, float) and math.isnan(value)
                          else f"{value:.4f}".replace(".", ",") if isinstance(value, float)
                          else str(value))
        lines.append("| " + " | ".join(values) + " |")
    lines.extend(["", note, ""])
    path.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")


def aggregate(output: Path, expected: set[str], fingerprint: dict[str, Any]) -> None:
    verify_val_bytes(fingerprint)
    table_rows: dict[str, list[dict[str, Any]]] = {key: [] for key in ("T09", "T10", "T11", "T14")}
    summary: dict[str, Any] = {}
    sources: dict[str, str] = {}
    for label in MODELS:
        path = output / f"{label}_predictions.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (payload["model"] != label or
            payload["val_split_fingerprint_sha256"] != fingerprint["split_fingerprint_sha256"] or
            {item["image"] for item in payload["images"]} != expected or
            len(payload["images"]) != len(expected)):
            raise RuntimeError(f"Incomplete or mismatched VAL capture: {path}")
        records = payload["images"]
        source = path.relative_to(ROOT).as_posix()
        sources[source] = sha256(path)
        error = Counter()
        confusion = Counter()
        for record in records:
            local_error, local_confusion = image_matches(record)
            error.update(local_error)
            confusion.update(local_confusion)
        false_positives = sum(error[key] for key in (
            "fp_background_count", "fp_wrong_class_count", "fp_localization_count", "fp_duplicate_count"))
        table_rows["T09"].append({
            "model": label, "split": "val", "confidence_threshold": OPERATING_CONFIDENCE,
            "match_iou_threshold": MATCH_IOU,
            "false_positives_per_image": false_positives / len(records),
            **{key: error[key] for key in ("fp_background_count", "fp_wrong_class_count",
                                         "fp_localization_count", "fp_duplicate_count",
                                         "fn_small_count", "fn_medium_count", "fn_large_count")},
            "source": source,
        })
        for actual in (*NAMES.values(), "background"):
            for predicted in (*NAMES.values(), "background"):
                table_rows["T10"].append({
                    "model": label, "split": "val", "actual_class": actual,
                    "predicted_class": predicted, "count": confusion[(actual, predicted)],
                    "confidence_threshold": OPERATING_CONFIDENCE,
                    "match_iou_threshold": MATCH_IOU, "source": source,
                })
        sweep = []
        for threshold in THRESHOLDS:
            metrics = operating_metrics(records, threshold)
            sweep.append((threshold, metrics))
        best_threshold, best_metrics = max(sweep, key=lambda item: (item[1]["F1"], -item[0]))
        for threshold, metrics in sweep:
            table_rows["T11"].append({
                "model": label, "split": "val", "confidence_threshold": threshold,
                **metrics, "best_F1_on_VAL": threshold == best_threshold,
                "source": source,
            })
        bins, ece = calibration(records)
        for item in bins:
            table_rows["T14"].append({"model": label, "split": "val", **item,
                                      "ECE_10bin": ece, "source": source})
        summary[label] = {
            "images": len(records), "false_positives_at_conf_0_25": false_positives,
            "false_positives_per_image_at_conf_0_25": false_positives / len(records),
            "error_counts": dict(error), "best_F1_threshold_on_VAL_grid": best_threshold,
            "best_F1_on_VAL_grid": best_metrics["F1"],
            "metrics_at_conf_0_25": operating_metrics(records, OPERATING_CONFIDENCE),
            "ECE_10bin_at_conf_0_25": ece,
        }
        print(f"Aggregated {label}: best VAL F1={best_metrics['F1']:.4f} at conf>{best_threshold:.2f}", flush=True)

    notes = {
        "T09": "Sumber setiap baris: JSON prediksi VAL pada kolom `source`. Matching kelas sama dilakukan satu-ke-satu pada IoU ≥0,50, urut confidence. Prediksi sisa yang cocok dengan kelas lain diberi kategori wrong class; sisanya duplicate bila IoU kelas sama ≥0,50, localization bila 0,10–<0,50, dan background selain itu. FN dihitung pada GT tanpa pasangan benar menurut luas kotak pada piksel input. Kategori FP saling eksklusif.",
        "T10": "Sumber setiap baris: JSON prediksi VAL pada kolom `source`. Matriks empat label mencakup background: pasangan kelas sama lebih dulu, lalu pasangan salah kelas pada IoU ≥0,50; prediksi/GT yang belum berpasangan dipetakan ke background. Ini matriks diagnostik satu-ke-satu, bukan mAP.",
        "T11": "Sumber setiap baris: JSON prediksi VAL pada kolom `source`. TP IoU 0,50 mengikuti `DetectionValidator` Ultralytics 8.4.130 pada confidence floor 0,001 dan NMS 0,7. Precision dan recall dirata-ratakan makro atas tiga kelas; F1 dihitung dari rerata itu, selaras evaluator TEST. Ambang terbaik hanya dipilih dari grid VAL 0,05–0,90 dan tidak mengubah hasil TEST historis.",
        "T14": "Sumber setiap baris: JSON prediksi VAL pada kolom `source`. Bin [bawah, atas), bin terakhir inklusif; hanya prediksi confidence >0,25. Kebenaran deteksi memakai TP IoU 0,50 dari validator. ECE = jumlah proporsi bin × |rerata confidence − precision empiris|. ECE pada tabel diulang per baris model dan tidak menilai kalibrasi probabilitas kelas secara penuh.",
    }
    paths = {
        "T09": TABLES / "T09_analisis_kesalahan.csv",
        "T10": TABLES / "T10_matriks_kebingungan.csv",
        "T11": TABLES / "T11_sapuan_confidence.csv",
        "T14": TABLES / "T14_kalibrasi_confidence.csv",
    }
    for key, path in paths.items():
        write_table(path, table_rows[key], notes[key])
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps({
        "scope": "VAL diagnosis only; no TRAIN or TEST inference",
        "val_split_fingerprint_sha256": fingerprint["split_fingerprint_sha256"],
        "script_sha256": sha256(Path(__file__)), "sources_sha256": sources,
        "models": summary,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path = ROOT / "analisis_performa/lab_server/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources_sha256"].update(sources)
    manifest["sources_sha256"][Path(__file__).relative_to(ROOT).as_posix()] = sha256(Path(__file__))
    manifest["outputs_sha256"][summary_path.relative_to(ROOT).as_posix()] = sha256(summary_path)
    for path in paths.values():
        manifest["outputs_sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
        manifest["outputs_sha256"][path.with_suffix(".md").relative_to(ROOT).as_posix()] = sha256(path.with_suffix(".md"))
    manifest["val_diagnosis_added_on"] = "2026-10-20"
    manifest["scope"] = "Curated lab/server tables T01-T14 from existing artifacts plus seven-checkpoint VAL diagnosis; no new training, TEST rerun, or robot operation"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote T09/T10/T11/T14 and {summary_path}", flush=True)


def main() -> int:
    args = arguments()
    if args.threads < 1:
        raise ValueError("--threads must be positive")
    images, expected, fingerprint = source_paths()
    args.output.mkdir(parents=True, exist_ok=True)
    if not args.aggregate_only:
        for label in args.models:
            capture_one(label, args.output, images, expected, fingerprint, args.threads)
    if all((args.output / f"{label}_predictions.json").is_file() for label in MODELS):
        aggregate(args.output, expected, fingerprint)
    else:
        print("Captures incomplete; run remaining models before aggregation", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
