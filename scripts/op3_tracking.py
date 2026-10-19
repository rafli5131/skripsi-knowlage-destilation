"""Helper sederhana untuk meneruskan ID tracker YOLO ke pesan ROS."""

from __future__ import annotations

from typing import Any


def track_ids_for_boxes(boxes: Any, enabled: bool) -> list[int | None]:
    """Kembalikan satu ID tracker per kotak, atau None bila belum terlacak."""
    if boxes is None:
        return []
    count = len(boxes)
    if not enabled:
        return [None] * count
    ids = getattr(boxes, "id", None)
    if ids is None:
        return [None] * count
    values = ids.int().cpu().tolist()
    if len(values) != count:
        raise ValueError(f"Jumlah ID tracker ({len(values)}) tidak cocok dengan jumlah kotak ({count}).")
    return [int(value) for value in values]


def detection_identifier(class_name: str, track_id: int | None) -> str:
    """Buat ID ROS yang memisahkan nama kelas dan ID dalam satu sesi."""
    if track_id is None:
        return ""
    return f"{class_name}:{int(track_id)}"
