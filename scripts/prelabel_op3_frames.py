#!/usr/bin/env python3
"""Write draft YOLO labels from a checkpoint; human review is still required."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


DATA_ROOT = Path(__file__).resolve().parents[1] / "data/op3_camera_eval/sessions"
EXPECTED_NAMES = {0: "ball", 1: "gawang", 2: "robot"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--model", type=Path, required=True, help="Teacher or student .pt checkpoint")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.session_id):
        parser.error("Invalid session-id")
    if args.imgsz < 1 or not 0 < args.conf <= 1 or not 0 < args.iou <= 1:
        parser.error("Invalid imgsz, conf, or iou")
    model_path = args.model.expanduser().resolve()
    if not model_path.is_file():
        parser.error(f"Checkpoint unavailable: {model_path}")
    session_dir = DATA_ROOT / args.session_id
    image_dir = session_dir / "images"
    if not (session_dir / "capture_manifest.json").is_file() or not image_dir.is_dir():
        parser.error(f"No captured session found at {session_dir}")
    images = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        parser.error("No images available for prelabeling")
    output_dir = session_dir / "labels_auto"
    if output_dir.exists():
        parser.error(f"Refusing to overwrite existing draft labels: {output_dir}")

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        parser.error(f"Activate an environment with Ultralytics first: {exc}")
    model = YOLO(str(model_path))
    names = model.names
    actual_names = {int(k): str(v) for k, v in (names.items() if isinstance(names, dict) else enumerate(names))}
    if actual_names != EXPECTED_NAMES:
        parser.error(f"Unexpected checkpoint classes: {actual_names}; expected {EXPECTED_NAMES}")

    output_dir.mkdir()
    predictions_path = output_dir / "predictions.jsonl"
    with predictions_path.open("x", encoding="utf-8") as journal:
        for image_path in images:
            result = model.predict(
                source=str(image_path), imgsz=args.imgsz, conf=args.conf,
                iou=args.iou, device="cpu", verbose=False,
            )[0]
            boxes = result.boxes
            lines = []
            predictions = []
            for class_id, xywhn, confidence in zip(
                boxes.cls.tolist(), boxes.xywhn.tolist(), boxes.conf.tolist()
            ):
                class_id = int(class_id)
                if class_id not in EXPECTED_NAMES:
                    raise ValueError(f"Invalid class {class_id} in {image_path}")
                lines.append(f"{class_id} " + " ".join(f"{value:.8f}" for value in xywhn))
                predictions.append({"class_id": class_id, "confidence": float(confidence), "xywhn": xywhn})
            (output_dir / f"{image_path.stem}.txt").write_text(
                "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
            )
            journal.write(json.dumps({"image": image_path.name, "predictions": predictions}) + "\n")
    manifest = {
        "status": "draft_requires_human_review",
        "session_id": args.session_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_path": str(model_path),
        "model_sha256": sha256_file(model_path),
        "classes": EXPECTED_NAMES,
        "imgsz": args.imgsz,
        "conf": args.conf,
        "iou": args.iou,
        "image_count": len(images),
        "label_format": "YOLO class x_center y_center width height, normalized",
    }
    (output_dir / "prelabel_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Draft labels for {len(images)} images saved in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
