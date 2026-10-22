"""Uji fungsi FPS efektif tanpa ROS atau model deteksi."""

from __future__ import annotations

import unittest

from scripts.op3_runtime_metrics import effective_fps_after_warmup


class EffectiveFpsTests(unittest.TestCase):
    def test_skips_warmup_and_uses_processed_capture_timestamps(self) -> None:
        timestamps = [0, 1_000_000_000, 2_000_000_000, 2_500_000_000, 3_000_000_000]
        self.assertEqual(effective_fps_after_warmup(timestamps, 2), 2.0)

    def test_returns_none_until_two_measured_frames_exist(self) -> None:
        self.assertIsNone(effective_fps_after_warmup([1, 2], 1))

    def test_returns_none_for_non_monotonic_timestamps(self) -> None:
        self.assertIsNone(effective_fps_after_warmup([1, 3, 2], 0))

    def test_rejects_negative_warmup_count(self) -> None:
        with self.assertRaises(ValueError):
            effective_fps_after_warmup([1, 2], -1)


if __name__ == "__main__":
    unittest.main()
