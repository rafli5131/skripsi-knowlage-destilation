"""Evaluate fixed checkpoints on reviewed OP3 sessions without robot I/O."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import ultralytics
from ultralytics import YOLO

from op3_camera_eval.evaluate import CLASSES, iou_xyxy, read_labels, sha256

IMGSZ = 640
MAP_CONF = 0.001
OPERATING_CONF = 0.25
NMS_IOU = 0.7
MATCH_IOU = 0.5


def inspect_sessions(groups: dict[str, list[Path]]) -> tuple[list[dict], dict]:
    frames: list[dict] = []
    manifest: dict = {"sessions": {}, "frames": {}}
    seen_names: set[str] = set()
    seen_hashes: dict[str, str] = {}
    for role, sessions in groups.items():
        for session in sessions:
            if not session.is_dir():
                raise ValueError(f"Session missing: {session}")
            sid = session.name
            if sid in seen_names:
                raise ValueError(f"Duplicate session ID: {sid}")
            seen_names.add(sid)
            images = sorted((session / "images").glob("*.jpg"))
            label_dir = session / "labels_reviewed"
            label_paths = sorted(label_dir.glob("frame_*.txt"))
            if not images or {p.stem for p in images} != {p.stem for p in label_paths}:
                raise ValueError(f"Images and reviewed labels differ: {sid}")
            log_path = label_dir / "review_log.jsonl"
            log = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
            if {entry["image"] for entry in log} != {image.name for image in images}:
                raise ValueError(f"Review log does not cover every image: {sid}")
            if {entry.get("reviewer") for entry in log} != {"bhre"}:
                raise ValueError(f"Unexpected reviewer metadata: {sid}")
            manifest["sessions"][sid] = {
                "role": role, "path": str(session.resolve()), "image_count": len(images),
                "review_log_sha256": sha256(log_path),
            }
            for image in images:
                label = label_dir / f"{image.stem}.txt"
                gt = read_labels(label)
                if role == "negative" and gt:
                    raise ValueError(f"Negative image has target label: {image}")
                image_hash = sha256(image)
                if image_hash in seen_hashes:
                    raise ValueError(f"Duplicate image content: {image} and {seen_hashes[image_hash]}")
                seen_hashes[image_hash] = str(image)
                key = f"{sid}__{image.stem}"
                if key in manifest["frames"]:
                    raise ValueError(f"Duplicate output key: {key}")
                frames.append({"key": key, "role": role, "session": sid,
                               "image": image, "label": label, "gt": gt})
                manifest["frames"][key] = {
                    "image": str(image.resolve()), "image_sha256": image_hash,
                    "label": str(label.resolve()), "label_sha256": sha256(label),
                    "role": role, "session": sid,
                }
    return frames, manifest


def build_dataset(output: Path, frames: list[dict], roles: set[str]) -> Path:
    dataset = output / "dataset"
    images_dir = dataset / "images" / "val"
    labels_dir = dataset / "labels" / "val"
    images_dir.mkdir(parents=True)
    labels_dir.mkdir(parents=True)
    for frame in frames:
        if frame["role"] not in roles:
            continue
        shutil.copy2(frame["image"], images_dir / f"{frame['key']}.jpg")
        shutil.copy2(frame["label"], labels_dir / f"{frame['key']}.txt")
    yaml = dataset / "data.yaml"
    yaml.write_text(f"path: {dataset.resolve()}\ntrain: images/val\nval: images/val\n"
                    "names: [ball, gawang, robot]\n")
    return yaml


def ap_metrics(model: YOLO, yaml: Path, output: Path, name: str) -> dict:
    result = model.val(data=str(yaml), split="val", imgsz=IMGSZ, batch=1, workers=0,
                       device="cpu", conf=MAP_CONF, iou=NMS_IOU, augment=False,
                       plots=False, verbose=False, project=str(output), name=name,
                       exist_ok=True)
    per_class = {}
    for index, class_id in enumerate(result.box.ap_class_index):
        _, _, ap50, ap5095 = result.box.class_result(index)
        per_class[CLASSES[int(class_id)]] = {"mAP50": float(ap50), "mAP50-95": float(ap5095)}
    return {"mAP50": float(result.box.map50), "mAP50-95": float(result.box.map),
            "per_class": per_class}


def empty_counts() -> dict:
    return {name: {"ground_truth": 0, "predictions": 0, "true_positives": 0,
                   "false_positives": 0, "false_negatives": 0} for name in CLASSES}


def add_counts(target: dict, source: dict) -> None:
    for name in CLASSES:
        for key in target[name]:
            target[name][key] += source[name][key]


def score_counts(counts: dict) -> dict:
    classes = {}
    for name in CLASSES:
        row = dict(counts[name])
        gt, pred, tp = row["ground_truth"], row["predictions"], row["true_positives"]
        row["precision"] = tp / pred if pred else (0.0 if gt else None)
        row["recall"] = tp / gt if gt else None
        if gt:
            p, r = row["precision"], row["recall"]
            row["F1"] = 2 * p * r / (p + r) if p + r else 0.0
        else:
            row["F1"] = None
        classes[name] = row
    present = [row for row in classes.values() if row["ground_truth"] > 0]
    macro = {key: float(np.mean([row[key] for row in present])) if present else None
             for key in ("precision", "recall", "F1")}
    tp = sum(row["true_positives"] for row in classes.values())
    pred = sum(row["predictions"] for row in classes.values())
    gt = sum(row["ground_truth"] for row in classes.values())
    p = tp / pred if pred else (0.0 if gt else None)
    r = tp / gt if gt else None
    micro = {"precision": p, "recall": r,
             "F1": 2 * p * r / (p + r) if p is not None and r is not None and p + r else None}
    return {"per_class": classes, "macro": macro, "micro": micro,
            "ground_truth": gt, "predictions": pred, "true_positives": tp,
            "false_positives": pred - tp, "false_negatives": gt - tp}


def score_frame(gt: list, detections: list) -> tuple[dict, list]:
    counts = empty_counts()
    for class_id, *_ in gt:
        counts[CLASSES[class_id]]["ground_truth"] += 1
    used = set()
    details = []
    for det in sorted(detections, key=lambda d: d["confidence"], reverse=True):
        class_id = det["class_id"]
        if class_id not in range(len(CLASSES)):
            raise ValueError(f"Unexpected predicted class: {class_id}")
        name = CLASSES[class_id]
        counts[name]["predictions"] += 1
        candidates = []
        for i, (gt_class, x, y, w, h) in enumerate(gt):
            if gt_class != class_id or i in used:
                continue
            box = [(x - w / 2) * 640, (y - h / 2) * 480,
                   (x + w / 2) * 640, (y + h / 2) * 480]
            candidates.append((iou_xyxy(det["xyxy"], box), i))
        matched = False
        if candidates:
            overlap, index = max(candidates)
            if overlap >= MATCH_IOU:
                used.add(index)
                counts[name]["true_positives"] += 1
                matched = True
        details.append({**det, "matched": matched})
    for name in CLASSES:
        row = counts[name]
        row["false_positives"] = row["predictions"] - row["true_positives"]
        row["false_negatives"] = row["ground_truth"] - row["true_positives"]
    return counts, details


def predict_frames(model: YOLO, frames: list[dict], output: Path) -> dict:
    by_role: dict[str, dict] = defaultdict(empty_counts)
    by_session: dict[str, dict] = defaultdict(empty_counts)
    negative_with_fp = 0
    with output.open("w") as stream:
        for i, frame in enumerate(frames, 1):
            result = model.predict(source=str(frame["image"]), imgsz=IMGSZ,
                                   conf=OPERATING_CONF, iou=NMS_IOU, device="cpu",
                                   augment=False, verbose=False)[0]
            if result.orig_shape != (480, 640):
                raise ValueError(f"Unexpected image size: {frame['image']}: {result.orig_shape}")
            detections = [{"class_id": int(cls), "confidence": float(conf),
                           "xyxy": [float(v) for v in xyxy]}
                          for cls, conf, xyxy in zip(result.boxes.cls.cpu().tolist(),
                                                     result.boxes.conf.cpu().tolist(),
                                                     result.boxes.xyxy.cpu().tolist())
                          if conf > OPERATING_CONF]
            counts, details = score_frame(frame["gt"], detections)
            add_counts(by_role[frame["role"]], counts)
            add_counts(by_session[frame["session"]], counts)
            if frame["role"] == "negative" and detections:
                negative_with_fp += 1
            stream.write(json.dumps({"key": frame["key"], "role": frame["role"],
                                     "session": frame["session"], "counts": counts,
                                     "detections": details}) + "\n")
            if i % 50 == 0 or i == len(frames):
                print(f"Operating threshold: {i}/{len(frames)} frames", flush=True)
    main_counts = empty_counts()
    add_counts(main_counts, by_role["primary"])
    add_counts(main_counts, by_role["negative"])
    return {"main": score_counts(main_counts),
            "by_role": {name: score_counts(value) for name, value in by_role.items()},
            "by_session": {name: score_counts(value) for name, value in by_session.items()},
            "negative_frames_with_false_positive": negative_with_fp}


def make_plot(result: dict, output: Path) -> None:
    models = list(result["models"])
    classes = list(CLASSES)
    x = np.arange(len(classes))
    width = 0.32
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for i, model in enumerate(models):
        primary = result["models"][model]["primary"]
        p = [primary["operating"]["per_class"][name]["precision"] for name in classes]
        r = [primary["operating"]["per_class"][name]["recall"] for name in classes]
        axes[0].bar(x + (i - .5) * width, p, width, label=model)
        axes[1].bar(x + (i - .5) * width, r, width, label=model)
    for axis, title in zip(axes, ("Precision", "Recall")):
        axis.set_title(f"{title} @ conf > 0,25; IoU ≥ 0,5")
        axis.set_xticks(x, classes)
        axis.set_ylim(0, 1.08)
        axis.legend()
        axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Set utama: 200 frame objek + 60 frame negatif")
    fig.tight_layout()
    fig.savefig(output, dpi=170)
    plt.close(fig)


def make_ap_plot(result: dict, output: Path) -> None:
    models = list(result["models"])
    labels = ["mAP50", "mAP50–95"]
    x = np.arange(len(labels))
    width = 0.32
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for i, model in enumerate(models):
        ap = result["models"][model]["primary"]["ap"]
        values = [ap["mAP50"], ap["mAP50-95"]]
        bars = ax.bar(x + (i - .5) * width, values, width, label=model)
        ax.bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=3)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Average precision")
    ax.set_title("Set utama: 200 frame objek + 60 frame negatif")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(output, dpi=170)
    plt.close(fig)


def write_summary_csv(result: dict, output: Path) -> None:
    fields = ["model", "set", "class", "ground_truth", "predictions", "TP", "FP", "FN",
              "precision", "recall", "F1", "mAP50", "mAP50-95", "FP_frames"]
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for model, report in result["models"].items():
            for split in ("primary", "partial"):
                data = report[split]
                operating = data["operating"]
                writer.writerow({"model": model, "set": split, "class": "macro",
                                 "ground_truth": operating["ground_truth"],
                                 "predictions": operating["predictions"],
                                 "TP": operating["true_positives"],
                                 "FP": operating["false_positives"],
                                 "FN": operating["false_negatives"],
                                 **operating["macro"],
                                 "mAP50": data["ap"]["mAP50"],
                                 "mAP50-95": data["ap"]["mAP50-95"]})
                for name in CLASSES:
                    row = operating["per_class"][name]
                    ap = data["ap"]["per_class"].get(name, {})
                    writer.writerow({"model": model, "set": split, "class": name,
                                     "ground_truth": row["ground_truth"],
                                     "predictions": row["predictions"],
                                     "TP": row["true_positives"],
                                     "FP": row["false_positives"],
                                     "FN": row["false_negatives"],
                                     "precision": row["precision"],
                                     "recall": row["recall"], "F1": row["F1"],
                                     "mAP50": ap.get("mAP50"),
                                     "mAP50-95": ap.get("mAP50-95")})
            neg = report["negative"]
            writer.writerow({"model": model, "set": "negative", "class": "all",
                             "ground_truth": 0, "predictions": neg["predictions"],
                             "TP": 0, "FP": neg["false_positives"], "FN": 0,
                             "FP_frames": neg["frames_with_false_positive"]})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-session", action="append", required=True, type=Path)
    parser.add_argument("--negative-session", action="append", required=True, type=Path)
    parser.add_argument("--partial-session", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--models", nargs="+", required=True, metavar="NAME=CHECKPOINT")
    args = parser.parse_args()
    models = {}
    for item in args.models:
        name, sep, path = item.partition("=")
        if not sep or not name.isidentifier() or name in models:
            parser.error(f"Invalid model specification: {item}")
        models[name] = Path(path)
    for path in models.values():
        if not path.is_file():
            parser.error(f"Missing checkpoint: {path}")
    groups = {"primary": args.primary_session, "negative": args.negative_session,
              "partial": args.partial_session}
    frames, manifest = inspect_sessions(groups)
    counts = Counter(frame["role"] for frame in frames)
    if counts != {"primary": 200, "negative": 60, "partial": 50}:
        raise ValueError(f"Unexpected frame composition: {counts}")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=False)
    manifest.update({"created_at_utc": datetime.now(timezone.utc).isoformat(),
                     "status": "exploratory_op3_multi_session_evaluation",
                     "runtime": {"python": platform.python_version(), "torch": torch.__version__,
                                 "ultralytics": ultralytics.__version__},
                     "settings": {"imgsz": IMGSZ, "device": "cpu", "precision": "FP32",
                                  "map_conf_floor": MAP_CONF, "operating_conf_strictly_above": OPERATING_CONF,
                                  "nms_iou": NMS_IOU, "match_iou": MATCH_IOU},
                     "checkpoints": {name: {"path": str(path.resolve()), "sha256": sha256(path)}
                                     for name, path in models.items()}})
    (output / "input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    primary_yaml = build_dataset(output / "primary", frames, {"primary", "negative"})
    partial_yaml = build_dataset(output / "partial", frames, {"partial"})
    report = {"status": manifest["status"], "composition": dict(counts), "models": {}}
    for name, checkpoint in models.items():
        print(f"Evaluating {name}", flush=True)
        model = YOLO(str(checkpoint), task="detect")
        actual = tuple(model.names.values())
        if actual != CLASSES:
            raise ValueError(f"Unexpected class order for {name}: {actual}")
        primary_ap = ap_metrics(model, primary_yaml, output, f"val_primary_{name}")
        partial_ap = ap_metrics(model, partial_yaml, output, f"val_partial_{name}")
        operating = predict_frames(model, frames, output / f"per_frame_{name}.jsonl")
        report["models"][name] = {
            "primary": {"ap": primary_ap, "operating": operating["main"]},
            "negative": {**operating["by_role"]["negative"],
                         "frames_with_false_positive": operating["negative_frames_with_false_positive"]},
            "partial": {"ap": partial_ap, "operating": operating["by_role"]["partial"]},
            "by_session": operating["by_session"],
        }
        (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    make_plot(report, output / "grafik_precision_recall.png")
    make_ap_plot(report, output / "grafik_map.png")
    write_summary_csv(report, output / "summary.csv")
    print(json.dumps({name: {"primary_mAP50-95": item["primary"]["ap"]["mAP50-95"],
                             "primary_F1_macro": item["primary"]["operating"]["macro"]["F1"],
                             "negative_FP_frames": item["negative"]["frames_with_false_positive"]}
                      for name, item in report["models"].items()}, indent=2), flush=True)
    return 0
