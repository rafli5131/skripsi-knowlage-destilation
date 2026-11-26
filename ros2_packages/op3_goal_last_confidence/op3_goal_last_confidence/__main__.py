"""Preview Teacher dengan estimasi dan confidence deteksi terakhir."""

import op3_goal_continuity.__main__ as continuity_preview
from .continuity import GoalWithLastConfidence


if __name__ == '__main__':
    continuity_preview.GoalContinuity = GoalWithLastConfidence
    raise SystemExit(continuity_preview.main())
