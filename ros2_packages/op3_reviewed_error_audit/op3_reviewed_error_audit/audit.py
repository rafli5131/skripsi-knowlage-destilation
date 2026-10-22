"""Create targeted FN/FP tables and contact sheets from saved evaluation outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from op3_camera_eval.evaluate import CLASSES, iou_xyxy, read_labels, sha256

MATCH_IOU = 0.5


def gt_box(label: tuple, width: int = 640, height: int = 480) -> list[float]:
    _, x, y, w, h = label
    return [(x - w / 2) * width, (y - h / 2) * height,
            (x + w / 2) * width, (y + h / 2) * height]


def classify_gt(label: tuple, detections: list[dict]) -> dict:
    class_id = label[0]
    target = gt_box(label)
    same = [(iou_xyxy(target, d["xyxy"]), d) for d in detections if d["class_id"] == class_id]
    other = [(iou_xyxy(target, d["xyxy"]), d) for d in detections if d["class_id"] != class_id]
    matched = [(iou, d) for iou, d in same if d.get("matched") and iou >= MATCH_IOU]
    best_same = max(same, key=lambda item: item[0]) if same else None
    best_other = max(other, key=lambda item: item[0]) if other else None
    if matched:
        status = "matched"
    elif best_same and best_same[0] > 0:
        status = "same_class_wrong_box"
    elif best_other and best_other[0] >= MATCH_IOU:
        status = "wrong_class"
    else:
        status = "no_matching_detection_at_conf_threshold"
    return {
        "status": status,
        "best_same_class_iou": round(best_same[0], 4) if best_same else None,
        "best_same_class_confidence": round(best_same[1]["confidence"], 4) if best_same else None,
        "best_other_class_iou": round(best_other[0], 4) if best_other else None,
    }


def classify_fp(det: dict, labels: list[tuple]) -> dict:
    same = [(iou_xyxy(det["xyxy"], gt_box(gt)), gt) for gt in labels if gt[0] == det["class_id"]]
    other = [(iou_xyxy(det["xyxy"], gt_box(gt)), gt) for gt in labels if gt[0] != det["class_id"]]
    if same and max(same, key=lambda item: item[0])[0] >= MATCH_IOU:
        category = "duplicate_or_assignment_conflict"
    elif other and max(other, key=lambda item: item[0])[0] >= MATCH_IOU:
        category = "overlaps_other_class"
    elif max([iou for iou, _ in same + other], default=0.0) >= 0.1:
        category = "mislocalized"
    else:
        category = "no_gt_overlap"
    return {"fp_category": category,
            "best_same_class_iou": round(max((iou for iou, _ in same), default=0.0), 4),
            "best_other_class_iou": round(max((iou for iou, _ in other), default=0.0), 4)}


def save_contact_sheets(items: list[dict], session_root: Path, out: Path, title: str) -> list[str]:
    if not items:
        return []
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    font = ImageFont.truetype(str(font_path), 12) if font_path.exists() else ImageFont.load_default()
    tile_w, tile_h, per_page, cols = 330, 278, 20, 4
    names = []
    for page_start in range(0, len(items), per_page):
        page = items[page_start:page_start + per_page]
        sheet = Image.new("RGB", (cols * tile_w, 5 * tile_h), "#202020")
        for i, item in enumerate(page):
            img_path = session_root / item["session"] / "images" / f"{item['frame']}.jpg"
            label_path = session_root / item["session"] / "labels_reviewed" / f"{item['frame']}.txt"
            image = Image.open(img_path).convert("RGB").resize((320, 240))
            draw = ImageDraw.Draw(image)
            for label in read_labels(label_path):
                x1, y1, x2, y2 = [v / 2 for v in gt_box(label)]
                draw.rectangle((x1, y1, x2, y2), outline="#00f060", width=2)
                draw.text((x1, max(0, y1 - 13)), f"GT {CLASSES[label[0]]}", fill="#00ff60", font=font, stroke_width=1, stroke_fill="black")
            for det in item["detections"]:
                x1, y1, x2, y2 = [v / 2 for v in det["xyxy"]]
                draw.rectangle((x1, y1, x2, y2), outline="#ff4848", width=2)
                text = f"P {CLASSES[det['class_id']]} {det['confidence']:.2f}"
                draw.text((x1, min(226, y2 + 2)), text, fill="#ff5858", font=font, stroke_width=1, stroke_fill="black")
            x, y = (i % cols) * tile_w, (i // cols) * tile_h
            sheet.paste(image, (x + 5, y + 24))
            caption = f"{item['session']} / {item['frame']} — {item['reason']}"
            ImageDraw.Draw(sheet).text((x + 5, y + 5), caption[:50], fill="white", font=font)
        name = f"{title}_p{page_start // per_page + 1:02d}.jpg"
        sheet.save(out / name, quality=88)
        names.append(name)
    return names


def run_audit(run_dir: Path, session_root: Path, output: Path, model: str) -> dict:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    manifest = json.loads((run_dir / "input_manifest.json").read_text())
    if model not in manifest["checkpoints"]:
        raise ValueError(f"Model not in evaluation manifest: {model}")
    pred_path = run_dir / f"predictions_{model}.jsonl"
    predictions = {row["key"]: row for row in
                   (json.loads(line) for line in pred_path.read_text().splitlines() if line.strip())}
    output.mkdir(parents=True)
    gate_misses: list[dict] = []
    robot_fps: list[dict] = []
    all_status = defaultdict(Counter)
    fp_status = defaultdict(Counter)
    for key, source in manifest["frames"].items():
        row = predictions.get(key)
        if row is None:
            raise ValueError(f"Prediction missing from run: {key}")
        image = Path(source["image"])
        label = Path(source["label"])
        if sha256(image) != source["image_sha256"] or sha256(label) != source["label_sha256"]:
            raise ValueError(f"Image or reviewed label changed since evaluation: {key}")
        labels = read_labels(label)
        detections = row["detections"]
        base = {"session": row["session"], "frame": image.stem}
        for gt in labels:
            status = classify_gt(gt, detections)
            class_name = CLASSES[gt[0]]
            all_status[(row["session"], class_name)][status["status"]] += 1
            if class_name == "gawang" and status["status"] != "matched":
                gate_misses.append({**base, "class": class_name, **status})
        for det in detections:
            if det.get("matched") or det["class_id"] != 2:
                continue
            status = classify_fp(det, labels)
            fp_status[row["session"]][status["fp_category"]] += 1
            robot_fps.append({**base, "class": "robot", "confidence": round(det["confidence"], 4),
                              **status, "xyxy": json.dumps([round(v, 1) for v in det["xyxy"]])})

    # Keep one visualization row per frame while listing every error separately in CSV.
    miss_keys = {(x["session"], x["frame"]) for x in gate_misses}
    fp_keys = {(x["session"], x["frame"]) for x in robot_fps}
    sheet_items = {"gawang_missed": [], "robot_false_positive": []}
    for key, row in predictions.items():
        session = row["session"]
        frame = key.rsplit("__", 1)[-1]
        detections = row["detections"]
        if (session, frame) in miss_keys:
            sheet_items["gawang_missed"].append({"session": session, "frame": frame,
                "reason": "gawang FN", "detections": detections})
        if (session, frame) in fp_keys:
            sheet_items["robot_false_positive"].append({"session": session, "frame": frame,
                "reason": "robot FP", "detections": detections})
    sheets = {}
    for title, items in sheet_items.items():
        items.sort(key=lambda item: (item["session"], item["frame"]))
        sheets[title] = save_contact_sheets(items, session_root, output, title)

    def write_csv(name: str, rows: list[dict]) -> None:
        path = output / name
        fields = list(rows[0]) if rows else ["session", "frame", "class", "status"]
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    write_csv("gawang_missed.csv", gate_misses)
    write_csv("robot_false_positives.csv", robot_fps)
    report = {
        "status": "offline_targeted_error_audit_no_relabeling",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_run": str(run_dir.resolve()), "model": model,
        "thresholds": {"prediction_confidence": 0.25, "match_iou": MATCH_IOU},
        "scope": "160 reviewed frames; focus on unmatched gawang ground truth and unmatched robot predictions",
        "gawang_miss_count": len(gate_misses), "robot_false_positive_count": len(robot_fps),
        "ground_truth_status_by_session": {
            session: {cls: dict(counts) for (sid, cls), counts in all_status.items() if sid == session}
            for session in sorted({sid for sid, _ in all_status})
        },
        "robot_false_positive_types_by_session": {sid: dict(counts) for sid, counts in fp_status.items()},
        "contact_sheets": sheets,
        "note": "Green boxes are reviewed human labels; red boxes are Hybrid predictions above confidence 0.25. This audit categorizes model errors and does not request a second full review or change labels.",
    }
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    readme = ["# Targeted OP3 detection error audit", "",
              "Compared stored Hybrid predictions against the already reviewed human labels. No model was rerun and no labels were changed.",
              "", f"Unmatched gawang ground-truth boxes: {len(gate_misses)}.",
              f"Unmatched robot predictions: {len(robot_fps)}.",
              "Green rectangles in contact sheets are human labels; red rectangles are predictions above confidence 0.25.",
              "The sheets are for targeted visual error analysis, not a request to review every frame again.", ""]
    for title, files in sheets.items():
        readme.append(f"{title}: {', '.join(files) if files else 'none'}")
    (output / "README.md").write_text("\n".join(readme) + "\n")
    print(json.dumps({"gawang_misses": len(gate_misses), "robot_false_positives": len(robot_fps),
                      "robot_fp_types": report["robot_false_positive_types_by_session"],
                      "contact_sheets": sheets}, indent=2), flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--session-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="hybrid")
    args = parser.parse_args()
    run_audit(args.run_dir.resolve(), args.session_root.resolve(), args.output_dir.resolve(), args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
