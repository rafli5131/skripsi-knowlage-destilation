# Targeted reviewed-frame error audit

Reads saved per-frame detections from `op3_reviewed_session_eval` and compares them with `labels_reviewed`. It does not rerun inference, change labels, or access ROS/robot hardware. It produces CSVs for missed `gawang` ground-truth boxes and unmatched `robot` detections, plus contact sheets showing reviewed labels in green and predictions in red.
