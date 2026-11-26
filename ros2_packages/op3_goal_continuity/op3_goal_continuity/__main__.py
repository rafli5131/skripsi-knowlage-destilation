"""Preview berbagi inferensi OP3, dengan estimasi gawang yang diberi label."""

import argparse
import sys

from op3_fullscreen_preview import preview
from op3_live_monitor.monitor import InferenceWorker, SharedState
from .continuity import GoalContinuity


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--goal-match', type=float, default=0.90)
    parser.add_argument('--goal-max-age', type=float, default=0.0,
                        help='Maksimum umur estimasi dalam detik; 0 selama gambar cocok')
    own, remaining = parser.parse_known_args()
    if not 0 < own.goal_match <= 1 or own.goal_max_age < 0:
        parser.error('goal-match harus dalam (0,1] dan goal-max-age tidak negatif')
    sys.argv = [sys.argv[0], *remaining]

    class ContinuityState(SharedState):
        def __init__(self):
            super().__init__()
            self.goal = GoalContinuity(own.goal_match, own.goal_max_age)
            self.previous_goal_mode = None

        def record(self, frame, values):
            mode = self.goal.mode
            if mode != self.previous_goal_mode and mode in ('detected', 'estimate', 'lost', 'expired'):
                print(f'GAWANG: {mode}', flush=True)
            self.previous_goal_mode = mode
            super().record(self.goal.draw(frame), values)

    class Proxy:
        def __init__(self, model, goal):
            self.model, self.goal = model, goal

        def track(self, *args, **kwargs):
            results = self.model.track(*args, **kwargs)
            self.goal.update(kwargs['source'], results[0])
            return results

    class ContinuityWorker(InferenceWorker):
        def __init__(self, state, checkpoint, args):
            super().__init__(state, checkpoint, args)
            self.model = Proxy(self.model, state.goal)

    preview.SharedState = ContinuityState
    preview.InferenceWorker = ContinuityWorker
    print('Gawang: kotak asli = deteksi; oranye ESTIMASI = template visual, bukan deteksi model.', flush=True)
    return preview.main()


if __name__ == '__main__':
    raise SystemExit(main())
