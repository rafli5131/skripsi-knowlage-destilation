"""Render a few offline KD detections from saved OP3 camera JPEGs."""

import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    samples = [args.session_dir / "images" / f"frame_{number:06d}.jpg"
               for number in (1, 60, 120)]
    for sample in samples:
        if not sample.is_file():
            raise FileNotFoundError(sample)
    model = YOLO(str(args.model), task="detect")
    panels = []
    for sample in samples:
        result = model.predict(source=str(sample), imgsz=640, conf=0.25, iou=0.7,
                               device="cpu", verbose=False)[0]
        panel = result.plot()
        cv2.rectangle(panel, (0, 0), (panel.shape[1], 32), (245, 245, 245), -1)
        cv2.putText(panel, f"{sample.stem} | KD offline, conf > 0.25", (8, 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2, cv2.LINE_AA)
        panels.append(panel)
    montage = cv2.hconcat(panels)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), montage):
        raise OSError(f"Could not write {args.output}")


if __name__ == "__main__":
    main()
