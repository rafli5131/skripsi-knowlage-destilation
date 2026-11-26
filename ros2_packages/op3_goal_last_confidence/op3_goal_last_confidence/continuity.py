"""Tambahkan confidence deteksi sebelumnya pada estimasi visual gawang."""

import cv2

from op3_goal_continuity.continuity import GoalContinuity


class GoalWithLastConfidence(GoalContinuity):
    def __init__(self, match_threshold=0.90, max_age=0.0):
        super().__init__(match_threshold, max_age)
        self.last_confidence = None

    def update(self, frame, result, now=None):
        super().update(frame, result, now)
        if self.mode != 'detected':
            return
        h, w = frame.shape[:2]
        confidences = []
        for item in result.boxes:
            if int(item.cls.item()) != 1:
                continue
            x1, y1, x2, y2 = (round(float(v)) for v in item.xyxy[0].tolist())
            candidate = (max(0, x1), max(0, y1), min(w, x2), min(h, y2))
            if candidate == self.box:
                confidences.append(float(item.conf.item()))
        self.last_confidence = max(confidences) if confidences else None

    def draw(self, frame):
        if self.estimate is None:
            return frame
        x1, y1, x2, y2 = self.estimate['box']
        color = (0, 190, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        score = 'N/A' if self.last_confidence is None else f'{self.last_confidence:.2f}'
        lines = [f"GAWANG ESTIMASI {self.estimate['age_seconds']:.1f}s",
                 f'CONF TERAKHIR {score} (BUKAN SAAT INI)']
        font, scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1
        sizes = [cv2.getTextSize(line, font, scale, thickness)[0] for line in lines]
        panel_w = min(frame.shape[1], max(s[0] for s in sizes) + 8)
        panel_h = sum(s[1] for s in sizes) + 15
        left = max(0, min(x1, frame.shape[1] - panel_w))
        top = max(0, min(y1 - panel_h, frame.shape[0] - panel_h))
        cv2.rectangle(frame, (left, top), (left + panel_w - 1, top + panel_h - 1), color, -1)
        y = top + sizes[0][1] + 3
        for line, (_, height) in zip(lines, sizes):
            cv2.putText(frame, line, (left + 3, y), font, scale, (10, 10, 10), thickness, cv2.LINE_AA)
            y += height + 5
        return frame
