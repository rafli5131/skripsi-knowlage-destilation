# OP3 blind manual label reviewer

This separate package starts labels from blank frames and reuses the existing `op3_label_reviewer` box, validation, and save helpers without modifying that package. It does not load `labels_auto` or model predictions. Each saved frame is written to the session's `labels_reviewed/` and recorded in `review_log.jsonl`.

Run from the repository root over SSH-X:

```bash
source .venv-op3-pytorch/bin/activate
export DISPLAY=localhost:11.0  # use the active SSH-X display
export PYTHONPATH="$PWD/ros2_packages/op3_label_reviewer:$PWD/ros2_packages/op3_blind_label_reviewer${PYTHONPATH:+:$PYTHONPATH}"
python -m op3_blind_label_reviewer \
  --session-dir data/op3_camera_eval/sessions/20261022_independent_validation_01 \
  --reviewer bhre
```

Controls: drag on empty image area to draw a box; `0`, `1`, `2` select `ball`, `gawang`, `robot`; click a box to select it; `Delete` removes it; `N`/Right and `P`/Left change frames; `S` saves the current frame; `R` reloads the last saved frame; `Q`/Esc exits. Check every target object, including multiple balls and objects clipped by the image edge. Press `S` even for a frame with no target so that the review log covers all 60 images.
