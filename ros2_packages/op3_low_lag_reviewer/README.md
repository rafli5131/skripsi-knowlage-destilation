# OP3 low-lag label reviewer

This new package reuses `op3_label_reviewer` and `op3_multi_session_reviewer` without modifying either package. It keeps source images at 640×480 for precise box edits and caps X11 redraws at 5 Hz to reduce SSH-X traffic.

Run from the repository root:

```bash
source .venv-op3-pytorch/bin/activate
export DISPLAY=localhost:11.0  # use the active SSH-X display for this connection
export PYTHONPATH="$PWD/ros2_packages/op3_label_reviewer:$PWD/ros2_packages/op3_multi_session_reviewer:$PWD/ros2_packages/op3_low_lag_reviewer${PYTHONPATH:+:$PYTHONPATH}"
python -m op3_low_lag_reviewer \
  --session-dir data/op3_camera_eval/sessions/20261022_hybrid1337_three_objects_01 \
  --session-dir data/op3_camera_eval/sessions/20261022_hybrid1337_three_objects_extra_01 \
  --reviewer bhre
```

Controls and save behavior match the shared reviewer: inspect each full-resolution image, correct boxes, then press `S` to save only the current frame under its original session's `labels_reviewed/`. `N`/Right advances, `P`/Left goes back, `0`/`1`/`2` selects ball/gawang/robot, Delete removes a selected box, `R` discards unsaved edits, and `Q`/Esc exits.
