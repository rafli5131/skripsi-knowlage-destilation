"""Compare fixed checkpoints on reviewed OP3 frames without touching the robot."""

import argparse
import csv
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import ultralytics
from ultralytics import YOLO


CLASSES = ("ball", "gawang", "robot")
IMGSZ = 640
MAP_CONF = 0.001
OPERATING_CONF = 0.25
NMS_IOU = 0.7
MATCH_IOU = 0.5


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_labels(path):
    rows = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"{path}:{line_no}: expected five YOLO fields")
        class_id = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        if class_id not in range(len(CLASSES)) or not all(np.isfinite((x, y, w, h))):
            raise ValueError(f"{path}:{line_no}: invalid class or coordinate")
        epsilon = 1e-6  # Eight-decimal YOLO coordinates can round a boundary past 0 or 1.
        if not (0 < w <= 1 and 0 < h <= 1 and -epsilon <= x - w / 2
                and x + w / 2 <= 1 + epsilon and -epsilon <= y - h / 2
                and y + h / 2 <= 1 + epsilon):
            raise ValueError(f"{path}:{line_no}: box outside normalized image")
        rows.append((class_id, x, y, w, h))
    return rows


def iou_xyxy(a, b):
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0


def fixed_metrics(model, images, labels):
    counts = {name: {"ground_truth": 0, "predictions": 0, "true_positives": 0}
              for name in CLASSES}
    for image in images:
        result = model.predict(source=str(image), imgsz=IMGSZ, conf=OPERATING_CONF,
                               iou=NMS_IOU, device="cpu", half=False, verbose=False)[0]
        width, height = result.orig_shape[1], result.orig_shape[0]
        ground_truth = []
        for class_id, x, y, w, h in labels[image.stem]:
            ground_truth.append((class_id, ((x - w / 2) * width, (y - h / 2) * height,
                                            (x + w / 2) * width, (y + h / 2) * height)))
            counts[CLASSES[class_id]]["ground_truth"] += 1
        used = set()
        boxes = result.boxes
        detections = sorted(zip(boxes.conf.cpu().tolist(), boxes.cls.cpu().tolist(),
                                boxes.xyxy.cpu().tolist()), reverse=True)
        for confidence, raw_class, xyxy in detections:
            if confidence <= OPERATING_CONF:
                continue
            class_id = int(raw_class)
            if class_id not in range(len(CLASSES)):
                raise ValueError(f"Unexpected predicted class: {class_id}")
            record = counts[CLASSES[class_id]]
            record["predictions"] += 1
            candidates = [(iou_xyxy(xyxy, gt_box), i) for i, (gt_class, gt_box)
                          in enumerate(ground_truth) if gt_class == class_id and i not in used]
            if candidates:
                overlap, index = max(candidates)
                if overlap >= MATCH_IOU:
                    record["true_positives"] += 1
                    used.add(index)
    for record in counts.values():
        p = record["true_positives"] / record["predictions"] if record["predictions"] else 0.0
        r = record["true_positives"] / record["ground_truth"] if record["ground_truth"] else 0.0
        record.update(precision=p, recall=r, F1=2 * p * r / (p + r) if p + r else 0.0)
    p = float(np.mean([counts[name]["precision"] for name in CLASSES]))
    r = float(np.mean([counts[name]["recall"] for name in CLASSES]))
    return counts, {"precision": p, "recall": r, "F1": 2 * p * r / (p + r) if p + r else 0.0}


def evaluate(session, output, models):
    images = sorted((session / "images").glob("*.jpg"))
    label_paths = sorted((session / "labels_reviewed").glob("*.txt"))
    if not images or {p.stem for p in images} != {p.stem for p in label_paths}:
        raise ValueError("Images and reviewed labels must have matching stems")
    if len(images) != len({p.stem for p in images}):
        raise ValueError("Duplicate image stems")
    labels = {path.stem: read_labels(path) for path in label_paths}
    review_log = session / "labels_reviewed" / "review_log.jsonl"
    reviews = [json.loads(line) for line in review_log.read_text().splitlines() if line.strip()]
    if {entry["image"] for entry in reviews} != {p.name for p in images}:
        raise ValueError("Review log must cover every image")
    if {entry.get("reviewer") for entry in reviews} != {"bhre"}:
        raise ValueError("Reviewer metadata has not been corrected to bhre")
    for name, path in models.items():
        if not path.is_file():
            raise FileNotFoundError(path)
    output.mkdir(parents=True, exist_ok=False)
    dataset = output / "dataset"
    image_dir = dataset / "images" / "val"
    label_dir = dataset / "labels" / "val"
    image_dir.mkdir(parents=True)
    label_dir.mkdir(parents=True)
    for image in images:
        os.link(image, image_dir / image.name)
        os.link(session / "labels_reviewed" / f"{image.stem}.txt", label_dir / f"{image.stem}.txt")
    yaml_path = dataset / "data.yaml"
    yaml_path.write_text(f"path: {dataset.resolve()}\ntrain: images/val\nval: images/val\n"
                         "names: [ball, gawang, robot]\n")
    manifest = {
        "status": "exploratory_single_servo_idle_session",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "session": str(session.resolve()), "reviewer": "bhre", "image_count": len(images),
        "class_order": list(CLASSES),
        "settings": {"imgsz": IMGSZ, "device": "cpu", "precision": "FP32",
                     "map_conf_floor": MAP_CONF, "fixed_precision_recall_confidence_strictly_above": OPERATING_CONF,
                     "nms_iou": NMS_IOU, "match_iou": MATCH_IOU},
        "runtime": {"python": platform.python_version(), "torch": torch.__version__,
                    "ultralytics": ultralytics.__version__, "numpy": np.__version__},
        "review_log_sha256": sha256(review_log),
        "images": {p.name: sha256(p) for p in images},
        "reviewed_labels": {p.name: sha256(p) for p in label_paths},
        "checkpoints": {name: {"path": str(path.resolve()), "sha256": sha256(path)}
                        for name, path in models.items()},
    }
    (output / "input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    report = {"status": manifest["status"], "image_count": len(images), "models": {}}
    for name, checkpoint in models.items():
        print(f"Evaluating {name} ({len(images)} frames)", flush=True)
        model = YOLO(str(checkpoint), task="detect")
        if tuple(model.names.values()) != CLASSES:
            raise ValueError(f"Unexpected model class order for {name}: {model.names}")
        validation = model.val(data=str(yaml_path), split="val", imgsz=IMGSZ, batch=1,
                               workers=0, device="cpu", conf=MAP_CONF, iou=NMS_IOU,
                               augment=False, half=False, plots=False, verbose=False,
                               project=str(output), name=f"val_{name}", exist_ok=True)
        per_class = {}
        for index, class_id in enumerate(validation.box.ap_class_index):
            _, _, ap50, ap5095 = validation.box.class_result(index)
            per_class[CLASSES[int(class_id)]] = {"mAP50": float(ap50), "mAP50-95": float(ap5095)}
        counts, operating = fixed_metrics(model, images, labels)
        for class_name in CLASSES:
            per_class.setdefault(class_name, {"mAP50": 0.0, "mAP50-95": 0.0})
            per_class[class_name].update(counts[class_name])
        overall = {**operating, "mAP50": float(validation.box.map50),
                   "mAP50-95": float(validation.box.map)}
        report["models"][name] = {"overall": overall, "per_class": per_class}
        (output / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    with (output / "summary.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["model", "level", "class", "precision", "recall", "F1", "mAP50", "mAP50-95",
                         "ground_truth", "predictions", "true_positives"])
        for name, result in report["models"].items():
            overall = result["overall"]
            writer.writerow([name, "overall", "", *(overall[key] for key in
                           ("precision", "recall", "F1", "mAP50", "mAP50-95")), "", "", ""])
            for class_name, row in result["per_class"].items():
                writer.writerow([name, "class", class_name, *(row[key] for key in
                                ("precision", "recall", "F1", "mAP50", "mAP50-95", "ground_truth",
                                 "predictions", "true_positives"))])
    print(json.dumps({name: item["overall"] for name, item in report["models"].items()}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--models", nargs="+", required=True, metavar="NAME=CHECKPOINT")
    args = parser.parse_args()
    models = {}
    for entry in args.models:
        name, separator, checkpoint = entry.partition("=")
        if not separator or not name.isidentifier() or name in models:
            parser.error(f"Invalid or duplicate model NAME=CHECKPOINT: {entry}")
        models[name] = Path(checkpoint)
    evaluate(args.session_dir, args.output_dir, models)
