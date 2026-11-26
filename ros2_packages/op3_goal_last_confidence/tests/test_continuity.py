from types import SimpleNamespace
import unittest

import numpy as np

from op3_goal_last_confidence.continuity import GoalWithLastConfidence


def box(confidence):
    return SimpleNamespace(cls=np.array(1), conf=np.array(confidence),
                           xyxy=np.array([[30, 20, 90, 80]]))


class LastConfidenceTest(unittest.TestCase):
    def setUp(self):
        self.frame = np.random.default_rng(5).integers(0, 256, (120, 160, 3), dtype=np.uint8)
        self.goal = GoalWithLastConfidence()

    def test_confidence_is_last_detection_not_new_prediction(self):
        self.goal.update(self.frame, SimpleNamespace(boxes=[box(.31)]), now=1)
        self.assertAlmostEqual(self.goal.last_confidence, .31)
        self.assertIsNone(self.goal.estimate)
        self.goal.update(self.frame, SimpleNamespace(boxes=[]), now=3)
        self.assertEqual(self.goal.mode, 'estimate')
        self.assertEqual(self.goal.estimate['age_seconds'], 2)
        self.assertAlmostEqual(self.goal.last_confidence, .31)
        self.assertFalse(np.array_equal(self.frame, self.goal.draw(self.frame.copy())))
        self.goal.update(self.frame, SimpleNamespace(boxes=[box(.55)]), now=4)
        self.assertAlmostEqual(self.goal.last_confidence, .55)
        self.assertIsNone(self.goal.estimate)

    def test_visual_loss_removes_estimate(self):
        self.goal.update(self.frame, SimpleNamespace(boxes=[box(.31)]), now=1)
        self.goal.update(np.zeros_like(self.frame), SimpleNamespace(boxes=[]), now=2)
        self.assertEqual(self.goal.mode, 'lost')
        self.assertIsNone(self.goal.estimate)


if __name__ == '__main__':
    unittest.main()
