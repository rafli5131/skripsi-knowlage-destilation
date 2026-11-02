# Interpreting accuracy and precision in the teacher walking tests

These live runs contain model predictions and overlays, but **no human ground-truth boxes for every measured frame**. Accordingly, accuracy, precision, recall, F1, AP, and mAP **are not computed** for these walking runs. The fraction of frames with a class output is not accuracy: an output may refer to the wrong object, and a frame without an output may have no target.

The per-run class charts and `../01-teacher/graph_output_coverage_confidence_teacher_walk_hd.png` show quantities available from the logs: the share of measured frames with at least one class prediction and the median model confidence. Confidence is neither accuracy probability nor precision.

To calculate detection precision (`TP / (TP + FP)`) and recall (`TP / (TP + FN)`), a human reviewer must label boxes and empty frames, then predictions must be matched to those labels using a predefined class and IoU rule. Any mAP from another labeled dataset must be reported separately with its dataset and protocol, not transferred to these walking runs.

The active walking set uses the raw sources listed in `active_run_sources.json`; displayed repetition 1 comes from the previous repetition-3 run. Between-run class coverage can change with object placement and camera motion, and does not establish a change in model quality.

**Selection of the active set:** repetition 1 was replaced with the previous repetition-3 run, and the two subsequent runs were collected after the old goal-output results were known. These repetitions were therefore not selected without looking at outcomes. The active set's 94.3% goal-output coverage may be optimistic relative to all runs collected. Disclose the selection rule and previous-set archive in the thesis; do not attribute the increase to the model or gait.
