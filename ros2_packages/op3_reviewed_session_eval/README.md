# Reviewed OP3 session evaluator

Evaluates complete human-reviewed camera sessions with an arbitrary frame count. Reuses the existing `op3_camera_eval` and `op3_multi_session_eval` packages for label validation, hash manifests, AP calculation, and fixed-threshold matching; neither shared package is modified.

Output includes `input_manifest.json`, `metrics.json`, `summary.csv`, per-image prediction journals, an aggregate per-class plot, and a concise README. The result is exploratory and should describe that Hybrid generated the draft labels when Hybrid is among the evaluated checkpoints.
