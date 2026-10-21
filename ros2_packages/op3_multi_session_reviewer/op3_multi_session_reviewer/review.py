"""Browse multiple OP3 sessions while saving labels to each original session."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from op3_label_reviewer.review import CLASSES, Reviewer


class MultiSessionReviewer(Reviewer):
    def __init__(self, sessions: list[Path], reviewer: str, start: int) -> None:
        if not sessions:
            raise ValueError("At least one session is required")
        self.session_names: dict[Path, str] = {}
        images: list[Path] = []
        for session in sessions:
            if not (session / "labels_auto" / "prelabel_manifest.json").is_file():
                raise ValueError(f"Draft label manifest missing: {session}")
            group = sorted((session / "images").glob("*.jpg"))
            if not group:
                raise ValueError(f"No JPEGs in {session / 'images'}")
            images.extend(group)
            self.session_names.update((path, session.name) for path in group)
        if not 1 <= start <= len(images):
            raise ValueError(f"--start must be 1..{len(images)}")
        super().__init__(sessions[0], reviewer, 1)
        self.images = images
        self.index = start - 1
        self.load()

    def load(self) -> None:
        self.session = self.images[self.index].parent.parent
        self.reviewed = self.session / "labels_reviewed"
        super().load()

    def render(self):
        canvas = super().render()
        width = self.image.shape[1]
        cv2.rectangle(canvas, (width, 0), (canvas.shape[1], canvas.shape[0]), (24, 24, 24), -1)
        reviewed_count = sum(
            (image.parent.parent / "labels_reviewed" / f"{image.stem}.txt").is_file()
            for image in self.images
        )
        current = self.images[self.index]
        status = "REVIEWED" if (self.reviewed / f"{current.stem}.txt").is_file() else "DRAFT"
        lines = [
            f"Frame {self.index + 1}/{len(self.images)} | {status}",
            f"Session: {self.session_names[current]}",
            current.name,
            f"Progress: {reviewed_count}/{len(self.images)} saved",
            f"Boxes: {len(self.boxes)} | active: {CLASSES[self.active_class]}",
            "",
            "N/D or Right: next",
            "P/A or Left: previous",
            "Click box: select",
            "Drag empty area: add box",
            "0/1/2: class (selected/active)",
            "Delete: remove selected box",
            "R: discard unsaved edits",
            "S: save final label",
            "Q/Esc: close",
            "",
            f"Reviewer: {self.reviewer or '[PRESS S TO ENTER]'}",
            "Labels auto = draft only.",
            "Saving marks ONE frame reviewed.",
        ]
        for i, line in enumerate(lines):
            cv2.putText(canvas, line, (width + 12, 28 + 24 * i),
                        cv2.FONT_HERSHEY_SIMPLEX, .48, (230, 230, 230), 1, cv2.LINE_AA)
        return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", type=Path, action="append", required=True,
                        help="Session directory; repeat in the desired review order")
    parser.add_argument("--reviewer", default="", help="Name/initials recorded for saved labels")
    parser.add_argument("--start", type=int, default=1, help="Global 1-based frame number")
    args = parser.parse_args()
    MultiSessionReviewer(
        [path.expanduser().resolve() for path in args.session_dir], args.reviewer, args.start
    ).run()
    return 0
