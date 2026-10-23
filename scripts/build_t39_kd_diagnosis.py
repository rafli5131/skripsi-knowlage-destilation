"""Summarize existing locked VAL predictions for the KD objective diagnosis.

This reads six frozen prediction files. It never trains or reads TEST images.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "runs/val_diagnostics/official_split_20261020"
OUT = ROOT / "analisis_performa/tabel"
CLASSES = ("ball", "gawang", "robot")
LABELS = tuple(f"{mode}_seed{seed}" for mode in ("hybrid_full", "supervised") for seed in (42, 1337, 2025))
THRESHOLDS = tuple(round(index * 0.05, 2) for index in range(1, 19))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(images: list[dict], threshold: float) -> dict:
    predictions = [0, 0, 0]
    true_positives = [0, 0, 0]
    ground_truth = [0, 0, 0]
    for image in images:
        for category in image["gt_cls"]:
            ground_truth[int(category)] += 1
        for category, confidence, correct in zip(
            image["pred_cls"], image["pred_conf"], image["tp_iou50_validator"], strict=True
        ):
            if confidence > threshold:
                category = int(category)
                predictions[category] += 1
                true_positives[category] += int(correct)
    precision_by_class = [tp / pred if pred else 0.0 for tp, pred in zip(true_positives, predictions, strict=True)]
    recall_by_class = [tp / gt if gt else 0.0 for tp, gt in zip(true_positives, ground_truth, strict=True)]
    f1_by_class = [
        2 * precision * recall / (precision + recall) if precision + recall else 0.0
        for precision, recall in zip(precision_by_class, recall_by_class, strict=True)
    ]
    precision = sum(precision_by_class) / len(CLASSES)
    recall = sum(recall_by_class) / len(CLASSES)
    return {
        "precision_macro": precision,
        "recall_macro": recall,
        "F1_harmonic_macro_PR": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "F1_mean_per_class": sum(f1_by_class) / len(CLASSES),
        "predictions": sum(predictions),
        "true_positives": sum(true_positives),
        "false_positives": sum(predictions) - sum(true_positives),
    }


def main() -> None:
    table = OUT / "T39_diagnosis_objektif_kd.csv"
    histogram = OUT / "T39_histogram_confidence_tp_fp.csv"
    if table.exists() or histogram.exists():
        raise FileExistsError("T39 exists; refuse to overwrite an experiment result")
    payloads = {}
    fingerprints = set()
    for label in LABELS:
        source = ROOT / "runs/val_diagnostics/hybrid_objective_20261023" if label in {
            "hybrid_full_seed1337", "hybrid_full_seed2025"
        } else SOURCE
        path = source / f"{label}_predictions.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if len(payload["images"]) != 1213 or len({row["image"] for row in payload["images"]}) != 1213:
            raise RuntimeError(f"VAL capture is incomplete: {label}")
        fingerprints.add(payload["val_split_fingerprint_sha256"])
        payloads[label] = (path, payload)
    if len(fingerprints) != 1:
        raise RuntimeError("VAL fingerprints differ among models")

    fields = ["model", "seed", "VAL_images", "VAL_fingerprint_sha256", "prediction_source", "prediction_sha256",
              "F1_at_0_25", "precision_at_0_25", "recall_at_0_25", "F1_mean_class_at_0_25",
              "FP_at_0_25", "best_threshold_VAL", "best_F1_VAL", "delta_F1_best_minus_0_25",
              "best_precision_VAL", "best_recall_VAL", "ECE_10bin_at_0_25"]
    rows = []
    hist_rows = []
    for label, (path, payload) in payloads.items():
        images = payload["images"]
        fixed = score(images, 0.25)
        sweep = [(threshold, score(images, threshold)) for threshold in THRESHOLDS]
        best_threshold, best = max(sweep, key=lambda item: (item[1]["F1_harmonic_macro_PR"], -item[0]))
        bins = {(class_name, number): [0, 0, 0.0] for class_name in CLASSES for number in range(10)}
        for image in images:
            for category, confidence, correct in zip(
                image["pred_cls"], image["pred_conf"], image["tp_iou50_validator"], strict=True
            ):
                if confidence <= 0.25:
                    continue
                bucket = min(int(float(confidence) * 10), 9)
                cell = bins[(CLASSES[int(category)], bucket)]
                cell[0 if correct else 1] += 1
                cell[2] += float(confidence)
        total = sum(item[0] + item[1] for item in bins.values())
        ece = 0.0
        for number in range(10):
            selected = [bins[(class_name, number)] for class_name in CLASSES]
            tp = sum(item[0] for item in selected)
            fp = sum(item[1] for item in selected)
            confidence_sum = sum(item[2] for item in selected)
            if tp + fp:
                ece += (tp + fp) / total * abs(confidence_sum / (tp + fp) - tp / (tp + fp))
        for (class_name, number), (tp, fp, confidence_sum) in bins.items():
            hist_rows.append({"model": label, "class": class_name, "bin_lower_inclusive": number / 10,
                              "bin_upper_exclusive_except_last": (number + 1) / 10, "TP": tp, "FP": fp,
                              "mean_confidence": confidence_sum / (tp + fp) if tp + fp else "",
                              "source": str(path.relative_to(ROOT))})
        rows.append({
            "model": label, "seed": label.rsplit("seed", 1)[1], "VAL_images": len(images),
            "VAL_fingerprint_sha256": payload["val_split_fingerprint_sha256"],
            "prediction_source": str(path.relative_to(ROOT)), "prediction_sha256": digest(path),
            "F1_at_0_25": fixed["F1_harmonic_macro_PR"], "precision_at_0_25": fixed["precision_macro"],
            "recall_at_0_25": fixed["recall_macro"], "F1_mean_class_at_0_25": fixed["F1_mean_per_class"],
            "FP_at_0_25": fixed["false_positives"], "best_threshold_VAL": best_threshold,
            "best_F1_VAL": best["F1_harmonic_macro_PR"],
            "delta_F1_best_minus_0_25": best["F1_harmonic_macro_PR"] - fixed["F1_harmonic_macro_PR"],
            "best_precision_VAL": best["precision_macro"], "best_recall_VAL": best["recall_macro"],
            "ECE_10bin_at_0_25": ece,
        })
    OUT.mkdir(parents=True, exist_ok=True)
    with table.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with histogram.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(hist_rows[0]))
        writer.writeheader()
        writer.writerows(hist_rows)
    print(f"Created {table.relative_to(ROOT)} and {histogram.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
