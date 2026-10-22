"""Compare fixed detector checkpoints on manually reviewed OP3 camera sessions."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import ultralytics
from ultralytics import YOLO

from op3_camera_eval.evaluate import CLASSES, sha256
from op3_multi_session_eval.evaluate import (
    ap_metrics,
    build_dataset,
    inspect_sessions,
    predict_frames,
)

IMGSZ = 640
MAP_CONF = 0.001
OPERATING_CONF = 0.25
NMS_IOU = 0.7
MATCH_IOU = 0.5


def evaluate(sessions: list[Path], output: Path, models: dict[str, Path]) -> dict:
    groups = {"primary": sessions, "negative": [], "partial": []}
    frames, inputs = inspect_sessions(groups)
    if not frames:
        raise ValueError("No reviewed frames found")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    for session in sessions:
        capture = json.loads((session / "capture_manifest.json").read_text())
        if capture.get("frame_count") != len(list((session / "images").glob("*.jpg"))):
            raise ValueError(f"Capture manifest frame count mismatch: {session.name}")
    output.mkdir(parents=True)
    data_yaml = build_dataset(output / "dataset_build", frames, {"primary"})
    inputs.update({
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "exploratory_reviewed_op3_camera_evaluation",
        "capture_manifests": {
            session.name: json.loads((session / "capture_manifest.json").read_text())
            for session in sessions
        },
        "runtime": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "ultralytics": ultralytics.__version__,
        },
        "settings": {
            "imgsz": IMGSZ, "device": "cpu", "precision": "FP32",
            "map_conf_floor": MAP_CONF, "operating_confidence": OPERATING_CONF,
            "nms_iou": NMS_IOU, "match_iou": MATCH_IOU,
        },
        "label_provenance_note": (
            "Hybrid seed 1337 generated labels_auto drafts; a human reviewer bhre reviewed every frame. "
            "Because the evaluated Hybrid checkpoint also generated the drafts, reviewer anchoring may favor it."
        ),
        "checkpoints": {
            name: {"path": str(path.resolve()), "sha256": sha256(path)}
            for name, path in models.items()
        },
    })
    (output / "input_manifest.json").write_text(json.dumps(inputs, indent=2) + "\n")

    result = {
        "status": "exploratory_reviewed_op3_camera_evaluation",
        "frame_count": len(frames),
        "sessions": [session.name for session in sessions],
        "metrics": {},
    }
    for name, checkpoint in models.items():
        print(f"Evaluating {name} on {len(frames)} frames", flush=True)
        model = YOLO(str(checkpoint), task="detect")
        names = model.names
        class_names = tuple(names[i] for i in range(len(CLASSES)))
        if class_names != CLASSES:
            raise ValueError(f"Unexpected class order for {name}: {names}")
        ap = ap_metrics(model, data_yaml, output, f"val_{name}")
        operating = predict_frames(model, frames, output / f"predictions_{name}.jsonl")
        result["metrics"][name] = {
            "checkpoint": str(checkpoint.resolve()),
            "checkpoint_sha256": sha256(checkpoint),
            "combined": {"ap": ap, "operating": operating["by_role"]["primary"]},
            "by_session": operating["by_session"],
        }
        (output / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")

    rows = []
    for model_name, model_result in result["metrics"].items():
        for scope, item in [("combined", model_result["combined"]["operating"])] + list(model_result["by_session"].items()):
            for class_name, metrics in item["per_class"].items():
                ap_class = (model_result["combined"]["ap"]["per_class"].get(class_name, {})
                            if scope == "combined" else {})
                rows.append({
                    "model": model_name, "scope": scope, "class": class_name,
                    **metrics, "mAP50": ap_class.get("mAP50"),
                    "mAP50-95": ap_class.get("mAP50-95"),
                })
        overall = model_result["combined"]["operating"]
        ap_overall = model_result["combined"]["ap"]
        rows.append({"model": model_name, "scope": "combined", "class": "macro",
                     **overall["macro"], "mAP50": ap_overall["mAP50"],
                     "mAP50-95": ap_overall["mAP50-95"]})
    fields = ["model", "scope", "class", "ground_truth", "predictions",
              "true_positives", "false_positives", "false_negatives",
              "precision", "recall", "F1", "mAP50", "mAP50-95"]
    with (output / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    figure, axes = plt.subplots(1, 3, figsize=(12, 4))
    x = range(len(CLASSES))
    width = 0.36
    for model_index, (name, model_result) in enumerate(result["metrics"].items()):
        classes = model_result["combined"]["operating"]["per_class"]
        offset = (model_index - (len(models) - 1) / 2) * width
        for axis, metric in zip(axes, ("precision", "recall", "F1")):
            axis.bar([i + offset for i in x], [classes[class_name][metric] or 0 for class_name in CLASSES],
                     width, label=name)
    for axis, metric in zip(axes, ("precision", "recall", "F1")):
        axis.set_title(metric)
        axis.set_xticks(list(x), CLASSES)
        axis.set_ylim(0, 1.05)
        axis.legend()
    figure.suptitle(f"{len(frames)} reviewed OP3 camera frames; conf > {OPERATING_CONF}; IoU ≥ {MATCH_IOU}")
    figure.tight_layout()
    figure.savefig(output / "per_class_metrics.png", dpi=160)
    plt.close(figure)

    summary = [
        "# Exploratory OP3 camera evaluation",
        "",
        f"Frames: {len(frames)} across {len(sessions)} sessions.",
        "Metrics are exploratory and apply only to these reviewed sessions.",
        inputs["label_provenance_note"],
        "",
        "| Model | P macro | R macro | F1 macro | mAP50 | mAP50–95 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, data in result["metrics"].items():
        op = data["combined"]["operating"]["macro"]
        ap = data["combined"]["ap"]
        summary.append(f"| {name} | {op['precision']:.4f} | {op['recall']:.4f} | {op['F1']:.4f} | {ap['mAP50']:.4f} | {ap['mAP50-95']:.4f} |")
    (output / "README.md").write_text("\n".join(summary) + "\n")
    print(json.dumps({name: {"macro": data["combined"]["operating"]["macro"],
                             "mAP50": data["combined"]["ap"]["mAP50"],
                             "mAP50-95": data["combined"]["ap"]["mAP50-95"]}
                      for name, data in result["metrics"].items()}, indent=2), flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--models", nargs="+", required=True, metavar="NAME=CHECKPOINT")
    args = parser.parse_args()
    models = {}
    for item in args.models:
        name, separator, path = item.partition("=")
        if not separator or not name.isidentifier() or name in models:
            parser.error(f"Invalid model specification: {item}")
        models[name] = Path(path)
    for checkpoint in models.values():
        if not checkpoint.is_file():
            parser.error(f"Checkpoint not found: {checkpoint}")
    evaluate([session.expanduser().resolve() for session in args.session_dir],
             args.output_dir.expanduser().resolve(), models)
    return 0


if __name__ == "__main__":
    sys.exit(main())
