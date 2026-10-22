"""Review multiple OP3 sessions over SSH-X with a lower redraw rate."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import cv2

from op3_label_reviewer.review import CLASSES, WINDOW
from op3_multi_session_reviewer.review import MultiSessionReviewer


class LowLagReviewer(MultiSessionReviewer):
    """Keep full-resolution annotations while limiting X11 redraws to 5 Hz."""

    def run(self) -> None:
        if not os.environ.get("DISPLAY"):
            raise EnvironmentError("DISPLAY is empty; run from SSH -X or desktop")
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW, 1020, 600)
        cv2.setMouseCallback(WINDOW, self.mouse)
        try:
            while True:
                cv2.imshow(WINDOW, self.render())
                key = cv2.waitKeyEx(200)
                if self.entering_name:
                    if key in (13, 10):
                        name = self.name_buffer.strip()
                        if name:
                            self.reviewer = name
                            self.entering_name = False
                            self.save()
                        else:
                            self.message = "Enter a nonempty name or initials."
                    elif key == 27:
                        self.entering_name = False
                        self.message = "Name entry canceled; no label saved."
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
                elif key in (ord("n"), ord("d"), 65363, 2555904):
                    self.move(1)
                elif key in (ord("p"), ord("a"), 65361, 2424832):
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
    parser.add_argument("--session-dir", type=Path, action="append", required=True,
                        help="Session directory; repeat in review order")
    parser.add_argument("--reviewer", default="", help="Name/initials recorded with saved labels")
    parser.add_argument("--start", type=int, default=1, help="Global 1-based frame number")
    args = parser.parse_args()
    LowLagReviewer(
        [path.expanduser().resolve() for path in args.session_dir], args.reviewer, args.start
    ).run()
    return 0
