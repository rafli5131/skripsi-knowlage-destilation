"""Review OP3 frames from blank labels, without model predictions."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import cv2

from op3_label_reviewer.review import Box, CLASSES, Reviewer, format_labels, read_labels


class BlindReviewer(Reviewer):
    """Reuse the shared box editing and save logic, starting each new frame blank."""

    def __init__(self, session: Path, reviewer: str, start: int) -> None:
        self.session = session
        self.reviewer = reviewer.strip()
        self.images = sorted((session / "images").glob("*.jpg"))
        if not self.images:
            raise ValueError(f"No JPEGs in {session / 'images'}")
        if not 1 <= start <= len(self.images):
            raise ValueError(f"--start must be 1..{len(self.images)}")
        self.reviewed = session / "labels_reviewed"
        self.recover_draft = None
        self.index = start - 1
        self.image = None
        self.boxes: list[Box] = []
        self.selected: int | None = None
        self.active_class = 0
        self.draw_start: tuple[int, int] | None = None
        self.draw_end: tuple[int, int] | None = None
        self.dirty = False
        self.entering_name = False
        self.name_buffer = ""
        self.message = "From-scratch label: box every visible target; press S to save."
        self.load()

    def load(self) -> None:
        image_path = self.images[self.index]
        self.image = cv2.imread(str(image_path))
        if self.image is None:
            raise OSError(f"Cannot open {image_path}")
        height, width = self.image.shape[:2]
        reviewed_path = self.reviewed / f"{image_path.stem}.txt"
        self.boxes = read_labels(reviewed_path, width, height) if reviewed_path.exists() else []
        self.selected = None
        self.draw_start = None
        self.draw_end = None
        self.dirty = False
        self.message = ("Saved manual label loaded." if reviewed_path.exists()
                        else "Blank frame: add every visible ball, gawang, and robot, then S.")

    def render(self):
        height, width = self.image.shape[:2]
        canvas = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        canvas = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        panel = cv2.copyMakeBorder(canvas, 0, max(0, 520 - height), 0, 380,
                                   cv2.BORDER_CONSTANT, value=(24, 24, 24))
        for i, box in enumerate(self.boxes):
            color = (0, 255, 255) if i == self.selected else (
                (30, 220, 30), (240, 180, 20), (20, 180, 240)
            )[box.class_id]
            cv2.rectangle(panel, (box.x1, box.y1), (box.x2, box.y2), color, 2)
            cv2.putText(panel, f"{i + 1}: {CLASSES[box.class_id]}",
                        (box.x1, max(16, box.y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX,
                        .55, color, 2, cv2.LINE_AA)
        if self.draw_start and self.draw_end:
            cv2.rectangle(panel, self.draw_start, self.draw_end,
                          (30, 220, 30) if self.active_class == 0 else
                          ((240, 180, 20) if self.active_class == 1 else (20, 180, 240)), 1)
        x = width + 12
        reviewed_count = sum((self.reviewed / f"{p.stem}.txt").is_file() for p in self.images)
        image_path = self.images[self.index]
        status = "SAVED" if (self.reviewed / f"{image_path.stem}.txt").is_file() else "UNREVIEWED"
        lines = [
            f"Frame {self.index + 1}/{len(self.images)} | {status}", image_path.name,
            f"Manual progress: {reviewed_count}/{len(self.images)}", "BLIND: no model boxes loaded",
            f"Boxes: {len(self.boxes)} | active: {CLASSES[self.active_class]}", "",
            "N/Right: next", "P/Left: previous", "Drag empty area: add box",
            "0/1/2: ball/gawang/robot", "Click box: select", "Delete: remove selected",
            "R: reload saved label", "S: save this frame", "Q/Esc: close", "",
            f"Reviewer: {self.reviewer or '[PRESS S TO ENTER]'}",
        ]
        for i, line in enumerate(lines):
            cv2.putText(panel, line, (x, 28 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX,
                        .47, (230, 230, 230), 1, cv2.LINE_AA)
        cv2.putText(panel, self.message[:80], (12, panel.shape[0] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 230, 255), 1, cv2.LINE_AA)
        return panel

    def run(self) -> None:
        if not os.environ.get("DISPLAY"):
            raise EnvironmentError("DISPLAY is empty; run from SSH -X or desktop")
        window = "OP3 blind manual review | q: exit"
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window, 1020, 600)
        cv2.setMouseCallback(window, self.mouse)
        try:
            while True:
                cv2.imshow(window, self.render())
                key = cv2.waitKeyEx(200)
                if self.entering_name:
                    if key in (13, 10):
                        name = self.name_buffer.strip()
                        if name:
                            self.reviewer = name
                            self.entering_name = False
                            self.save()
                        else:
                            self.message = "Enter reviewer name/initials."
                    elif key == 27:
                        self.entering_name = False
                        self.message = "Name entry canceled; frame not saved."
                    elif key in (8, 127, 65288):
                        self.name_buffer = self.name_buffer[:-1]
                    elif 32 <= key <= 126 and len(self.name_buffer) < 40:
                        self.name_buffer += chr(key)
                    continue
                if key in (ord("q"), 27):
                    if self.dirty:
                        self.message = "Unsaved edits: S saves, R discards; then Q."
                    else:
                        break
                elif key in (ord("n"), 65363, 2555904):
                    self.move(1)
                elif key in (ord("p"), 65361, 2424832):
                    self.move(-1)
                elif key == ord("s"):
                    self.save()
                elif key == ord("r"):
                    self.load()
                elif key in (8, 127, 65535) and self.selected is not None:
                    self.boxes.pop(self.selected)
                    self.selected = None
                    self.dirty = True
                    self.message = "Box removed. Press S to save."
                elif key in (ord("0"), ord("1"), ord("2")):
                    self.active_class = key - ord("0")
                    if self.selected is not None:
                        self.boxes[self.selected].class_id = self.active_class
                        self.dirty = True
                    self.message = f"Active class: {CLASSES[self.active_class]}"
        finally:
            cv2.destroyAllWindows()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--start", type=int, default=1)
    args = parser.parse_args()
    BlindReviewer(args.session_dir.expanduser().resolve(), args.reviewer, args.start).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
