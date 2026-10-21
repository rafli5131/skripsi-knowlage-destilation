"""Classify saved TP/FN/FP cases and draw contact sheets; no model inference."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from op3_camera_eval.evaluate import CLASSES, iou_xyxy, read_labels, sha256

MATCH_IOU = 0.5
RECHECK_LOWER_IOU = 0.4
RECHECK_UPPER_IOU = 0.6


def gt_xyxy(label: tuple, width: int = 640, height: int = 480) -> list[float]:
    _, x, y, w, h = label
    return [(x - w / 2) * width, (y - h / 2) * height,
            (x + w / 2) * width, (y + h / 2) * height]


def classify_ground_truth(label: tuple, detections: list[dict]) -> dict:
    class_id = label[0]
    box = gt_xyxy(label)
    same = [(iou_xyxy(box, det["xyxy"]), det) for det in detections
            if det["class_id"] == class_id]
    other = [(iou_xyxy(box, det["xyxy"]), det) for det in detections
             if det["class_id"] != class_id]
    matched = [(overlap, det) for overlap, det in same if det["matched"] and overlap >= MATCH_IOU]
    best_same = max(same, key=lambda x: x[0]) if same else None
    best_other = max(other, key=lambda x: x[0]) if other else None
    if matched:
        status = "matched"
    elif same:
        status = "same_class_wrong_box"
    elif best_other and best_other[0] >= MATCH_IOU:
        status = "wrong_class"
    else:
        status = "no_matching_prediction"
    return {"status": status,
            "best_same_class_iou": round(best_same[0], 6) if best_same else None,
            "best_same_class_confidence": round(best_same[1]["confidence"], 6) if best_same else None,
            "best_other_class_iou": round(best_other[0], 6) if best_other else None,
            "recheck_geometry": bool(best_same and RECHECK_LOWER_IOU <= best_same[0] < RECHECK_UPPER_IOU)}


def classify_false_positive(det: dict, labels: list[tuple]) -> str:
    if det["matched"]:
        return "matched"
    same = [iou_xyxy(det["xyxy"], gt_xyxy(gt)) for gt in labels
            if gt[0] == det["class_id"]]
    other = [iou_xyxy(det["xyxy"], gt_xyxy(gt)) for gt in labels
             if gt[0] != det["class_id"]]
    if same and max(same) >= MATCH_IOU:
        return "duplicate"
    if other and max(other) >= MATCH_IOU:
        return "wrong_class"
    if max(same + other, default=0) >= 0.1:
        return "mislocalized"
    return "background_or_unrelated"


def draw_sheet(rows: list[dict], model: str, session: str, root: Path, output: Path) -> None:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    tile_w, tile_h = 330, 280
    sheet = Image.new("RGB", (tile_w * 4, tile_h * 10), "#202020")
    for i, row in enumerate(rows):
        image_path = root / session / "images" / f"{row['frame']}.jpg"
        label_path = root / session / "labels_reviewed" / f"{row['frame']}.txt"
        image = Image.open(image_path).convert("RGB")
        if image.size != (640, 480):
            raise ValueError(f"Unexpected image size: {image_path}: {image.size}")
        image = image.resize((320, 240))
        draw = ImageDraw.Draw(image)
        for gt in read_labels(label_path):
            box = [v / 2 for v in gt_xyxy(gt)]
            draw.rectangle(box, outline="#00f060", width=3)
            draw.text((box[0], max(0, box[1] - 13)), f"GT {CLASSES[gt[0]]}",
                      fill="#00ff60", font=font, stroke_width=1, stroke_fill="black")
        for det in row["detections"]:
            box = [v / 2 for v in det["xyxy"]]
            draw.rectangle(box, outline="#ff4848", width=2)
            draw.text((box[0], min(226, box[3] + 2)),
                      f"P {CLASSES[det['class_id']]} {det['confidence']:.2f}",
                      fill="#ff4848", font=font, stroke_width=1, stroke_fill="black")
        tile = Image.new("RGB", (tile_w, tile_h), "#202020")
        tile.paste(image, (5, 24))
        ImageDraw.Draw(tile).text((5, 3), f"{row['frame']} | {row['focus_status']}",
                                  fill="white", font=font)
        sheet.paste(tile, ((i % 4) * tile_w, (i // 4) * tile_h))
    sheet.save(output, quality=88)


def draw_chart(summary: dict, focus: dict[str, str], output: Path) -> None:
    models = sorted(summary)
    statuses = ["matched", "same_class_wrong_box", "wrong_class", "no_matching_prediction"]
    names = ["Cocok", "Kotak meleset", "Kelas salah", "Tidak ada prediksi sesuai"]
    colors = ["#258a51", "#e6a13b", "#be4b5d", "#6c79a1"]
    fig, axes = plt.subplots(1, len(focus), figsize=(11, 4))
    if len(focus) == 1:
        axes = [axes]
    for ax, (session, class_name) in zip(axes, focus.items()):
        bottoms = [0] * len(models)
        for status, name, color in zip(statuses, names, colors):
            values = [summary[model][session][class_name].get(status, 0) for model in models]
            ax.bar(models, values, bottom=bottoms, label=name, color=color)
            bottoms = [a + b for a, b in zip(bottoms, values)]
        ax.set_title(f"{class_name}: {session.removeprefix('20261021_')}")
        ax.set_ylim(0, 44)
        ax.set_ylabel("Jumlah dari 40 frame")
        ax.spines[["top", "right"]].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2)
    fig.tight_layout(rect=(0, .12, 1, 1))
    fig.savefig(output, dpi=170)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--session-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir
    if output.exists():
        parser.error(f"Output exists: {output}")
    manifest = json.loads((args.run_dir / "input_manifest.json").read_text())
    models = tuple(manifest["checkpoints"])
    focus = {"20261021_robot_gawang_01": "gawang",
             "20261021_robot_ball_moving_01": "robot"}
    predictions = {}
    for model in models:
        rows = [json.loads(line) for line in (args.run_dir / f"per_frame_{model}.jsonl").read_text().splitlines()]
        predictions[model] = {row["key"]: row for row in rows}
    cases = []
    visual_rows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    summary: dict[str, dict] = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    fp_summary: dict[str, dict] = defaultdict(lambda: defaultdict(Counter))
    recheck = []
    for session, focus_class in focus.items():
        session_dir = args.session_root / session
        images = sorted((session_dir / "images").glob("frame_*.jpg"))
        if len(images) != 40:
            raise ValueError(f"Expected 40 frames: {session}")
        for image in images:
            label_path = session_dir / "labels_reviewed" / f"{image.stem}.txt"
            key = f"{session}__{image.stem}"
            source = manifest["frames"].get(key)
            if source is None or sha256(image) != source["image_sha256"] or sha256(label_path) != source["label_sha256"]:
                raise ValueError(f"Input changed since evaluation: {key}")
            labels = read_labels(label_path)
            for model in models:
                record = predictions[model].get(key)
                if record is None:
                    raise ValueError(f"Prediction missing: {model}: {key}")
                detections = record["detections"]
                focus_status = "no_gt"
                for label in labels:
                    class_name = CLASSES[label[0]]
                    info = classify_ground_truth(label, detections)
                    summary[model][session][class_name][info["status"]] += 1
                    if class_name == focus_class:
                        focus_status = info["status"]
                    row = {"model": model, "session": session, "frame": image.stem,
                           "class": class_name, **info,
                           "false_positive_boxes": sum(not d["matched"] for d in detections)}
                    cases.append(row)
                    if info["recheck_geometry"]:
                        recheck.append(row)
                for det in detections:
                    fp_summary[model][session][classify_false_positive(det, labels)] += 1
                visual_rows[(model, session)].append({"frame": image.stem,
                                                       "focus_status": focus_status,
                                                       "detections": detections})
    output.mkdir(parents=True)
    report = {"status": "offline_error_audit_no_relabeling",
              "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_run": str(args.run_dir.resolve()), "focus": focus,
              "ground_truth_status": {m: {s: {c: dict(v) for c, v in cs.items()}
                                          for s, cs in ss.items()} for m, ss in summary.items()},
              "prediction_status": {m: {s: dict(v) for s, v in ss.items()}
                                    for m, ss in fp_summary.items()},
              "geometry_recheck_candidates": len(recheck)}
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    fields = ["model", "session", "frame", "class", "status", "best_same_class_iou",
              "best_same_class_confidence", "best_other_class_iou",
              "recheck_geometry", "false_positive_boxes"]
    for name, rows in (("cases.csv", cases), ("geometry_recheck.csv", recheck)):
        with (output / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    for (model, session), rows in visual_rows.items():
        draw_sheet(rows, model, session, args.session_root,
                   output / f"lembar_{session}_{model}.jpg")
    draw_chart(report["ground_truth_status"], focus, output / "grafik_jenis_kesalahan.png")
    print(json.dumps({"focus": focus, "geometry_recheck_candidates": len(recheck),
                      "ground_truth_status": report["ground_truth_status"]}, indent=2))
    return 0
