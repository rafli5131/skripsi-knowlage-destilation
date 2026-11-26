"""Pertahankan estimasi gawang hanya saat template visual tetap cocok."""

from __future__ import annotations

import time

import cv2
import numpy as np


class GoalContinuity:
    def __init__(self, match_threshold: float = 0.90, max_age: float = 0.0):
        if not 0.0 < match_threshold <= 1.0 or max_age < 0:
            raise ValueError('Ambang pencocokan atau durasi tidak valid')
        self.match_threshold = match_threshold
        self.max_age = max_age  # nol: lanjut selama template masih cocok
        self.template = None
        self.box = None
        self.last_detection = None
        self.estimate = None
        self.mode = 'waiting'

    def update(self, frame, result, now=None):
        now = time.monotonic() if now is None else now
        self.estimate = None
        h, w = frame.shape[:2]
        candidates = []
        boxes = getattr(result, 'boxes', None)
        if boxes is not None:
            for item in boxes:
                if int(item.cls.item()) != 1:
                    continue
                x1, y1, x2, y2 = (round(float(v)) for v in item.xyxy[0].tolist())
                x1, x2 = max(0, x1), min(w, x2)
                y1, y2 = max(0, y1), min(h, y2)
                if x2 - x1 >= 12 and y2 - y1 >= 12:
                    candidates.append((float(item.conf.item()), (x1, y1, x2, y2)))
        if candidates:
            _, self.box = max(candidates, key=lambda x: x[0])
            x1, y1, x2, y2 = self.box
            gray = cv2.cvtColor(frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            # Area bertekstur rendah tidak aman untuk pencocokan template.
            self.template = gray.copy() if float(gray.std()) >= 8.0 else None
            self.last_detection = now
            self.mode = 'detected'
            return
        if self.template is None or self.box is None or self.last_detection is None:
            self.mode = 'waiting'
            return
        age = max(0.0, now - self.last_detection)
        if self.max_age and age > self.max_age:
            self.template = self.box = None
            self.mode = 'expired'
            return
        x1, y1, x2, y2 = self.box
        margin = max(16, min(80, round(max(x2-x1, y2-y1) * 0.15)))
        sx1, sy1 = max(0, x1-margin), max(0, y1-margin)
        sx2, sy2 = min(w, x2+margin), min(h, y2+margin)
        search = cv2.cvtColor(frame[sy1:sy2, sx1:sx2], cv2.COLOR_BGR2GRAY)
        th, tw = self.template.shape
        if search.shape[0] < th or search.shape[1] < tw:
            self.template = self.box = None
            self.mode = 'lost'
            return
        scores = cv2.matchTemplate(search, self.template, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(scores)
        if not np.isfinite(score) or score < self.match_threshold:
            self.template = self.box = None
            self.mode = 'lost'
            return
        x, y = sx1 + loc[0], sy1 + loc[1]
        self.box = (x, y, x+tw, y+th)
        self.estimate = {'box': self.box, 'age_seconds': age, 'match': float(score)}
        self.mode = 'estimate'

    def draw(self, frame):
        if self.estimate is None:
            return frame
        x1, y1, x2, y2 = self.estimate['box']
        color = (0, 190, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        text = f"GAWANG ESTIMASI {self.estimate['age_seconds']:.1f}s"
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_w, text_h), baseline = cv2.getTextSize(text, font, 0.48, 1)
        left = max(0, min(x1, frame.shape[1]-text_w-6))
        top = max(0, y1-text_h-baseline-8)
        cv2.rectangle(frame, (left, top), (min(frame.shape[1]-1, left+text_w+6),
                                          min(frame.shape[0]-1, top+text_h+baseline+8)), color, -1)
        cv2.putText(frame, text, (left+3, top+text_h+3), font, 0.48, (10, 10, 10), 1, cv2.LINE_AA)
        return frame
