# Exploratory OP3 camera evaluation

Frames: 160 across 2 sessions.
Metrics are exploratory and apply only to these reviewed sessions.
Hybrid seed 1337 generated labels_auto drafts; a human reviewer bhre reviewed every frame. Because the evaluated Hybrid checkpoint also generated the drafts, reviewer anchoring may favor it.

| Model | P macro | R macro | F1 macro | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|
| hybrid | 0.9646 | 0.8958 | 0.9196 | 0.7493 | 0.4687 |
| supervised | 0.5073 | 0.5042 | 0.5057 | 0.8265 | 0.4533 |
