"""Uji helper ID tracking tanpa memerlukan ROS atau model YOLO."""

import unittest

from scripts.op3_tracking import detection_identifier, track_ids_for_boxes


class FakeTensor:
    def __init__(self, values):
        self.values = values

    def int(self):
        return self

    def cpu(self):
        return self

    def tolist(self):
        return self.values


class FakeBoxes:
    def __init__(self, count, ids=None):
        self.count = count
        self.id = None if ids is None else FakeTensor(ids)

    def __len__(self):
        return self.count


class TrackingHelpersTest(unittest.TestCase):
    def test_tracking_ids_are_aligned_to_boxes(self):
        self.assertEqual(track_ids_for_boxes(FakeBoxes(2, [4.0, 9.0]), True), [4, 9])

    def test_unconfirmed_boxes_keep_detection_without_track_id(self):
        self.assertEqual(track_ids_for_boxes(FakeBoxes(2), True), [None, None])

    def test_detection_only_mode_does_not_publish_track_ids(self):
        self.assertEqual(track_ids_for_boxes(FakeBoxes(2, [4.0, 9.0]), False), [None, None])

    def test_track_id_is_namespaced_by_class(self):
        self.assertEqual(detection_identifier("ball", 4), "ball:4")
        self.assertEqual(detection_identifier("gawang", None), "")

    def test_mismatched_tracker_output_fails_explicitly(self):
        with self.assertRaises(ValueError):
            track_ids_for_boxes(FakeBoxes(2, [4.0]), True)


if __name__ == "__main__":
    unittest.main()
