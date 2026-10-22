"""Fungsi metrik runtime yang tidak bergantung pada ROS atau PyTorch."""

from __future__ import annotations

from collections.abc import Sequence


def effective_fps_after_warmup(capture_timestamps_ns: Sequence[int], warmup_frames: int) -> float | None:
    """Hitung FPS efektif dari timestamp frame sukses setelah warm-up."""
    if warmup_frames < 0:
        raise ValueError("warmup_frames tidak boleh negatif")
    measured = [int(value) for value in capture_timestamps_ns[warmup_frames:]]
    if len(measured) < 2:
        return None
    intervals = [right - left for left, right in zip(measured, measured[1:])]
    if any(interval <= 0 for interval in intervals):
        return None
    elapsed_ns = measured[-1] - measured[0]
    if elapsed_ns <= 0:
        return None
    return (len(measured) - 1) * 1_000_000_000 / elapsed_ns
