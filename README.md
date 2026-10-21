# BhreSkripsi

## Pure Teacher-Only Knowledge Distillation

This workspace evaluates a narrower YOLO11 student trained from the frozen
FP32 teacher in `/mnt/nas-hpg9/rafli5131/rafli/advance_vision`. The KD objective
uses teacher-only feature and detection-output distillation: there is no NNCF,
fake quantization, or supervised detection loss in the student update. TEST was
excluded from all student training and checkpoint selection; it was opened only
after the six student checkpoints had been locked by VAL. Training uses FP32.

## Current OP3 direction

The completed experiments below use Advance Vision data and establish the
current pure-KD checkpoints. The selected student `.pt` has been run on
ROBOTIS OP3 using PyTorch/Ultralytics on CPU. OpenVINO and QAT/INT8 are not
part of the current deployment plan. In the operator-verified servo-idle
session with a C920 camera and a reliable ROS 2 subscriber, the trial package
processed 1,501 frames and logged 4,454 detections across the three classes.
This is one runtime observation, not camera accuracy or evidence of walking
performance. Motion state is not inferred by the detector. The proposal and
planning drafts in this repo describe the completed Advance Vision study and
need revision before serving as the final OP3 thesis proposal.

The native PyTorch/Ultralytics ROS 2 camera node for the KD student is
[`scripts/op3_pytorch_detector.py`](scripts/op3_pytorch_detector.py). It reads
an operator-selected image topic and publishes detections without controlling
the robot. Runtime setup, parameters, and logging are documented in
[`OP3_PYTORCH_RUNTIME.md`](OP3_PYTORCH_RUNTIME.md). A CPU camera-inference
session and its performance charts are documented in
[`dokumentasi/README.md`](dokumentasi/README.md), including one annotated
camera frame and its detection metadata.
The node supports BoT-SORT IDs within a run and per-detection CSV logging.
Three earlier camera logs predate this tracking change and contain no track IDs.
A later trial through `ros2_packages/op3_idle_trial/` recorded all three classes
and stable IDs for relatively stationary objects in one servo-idle session.
Tracking moving objects and walking performance remain unmeasured, and the
existing frame counts are not camera accuracy evidence.
An offline smoke run on one VAL image for each class detected `ball`,
`gawang`, and `robot`; repeated frames kept a BoT-SORT ID after confirmation.
This checks the model/tracker software path only. It does not verify camera
capture or tracking while the OP3 is moving. The runtime pins `lap==0.5.12`
and exits at startup if that tracker dependency is missing.
Recorded offline smoke details are in
[`artifacts/op3_tracking_offline_smoke_20261019.json`](artifacts/op3_tracking_offline_smoke_20261019.json).
Per-run reports grouped by date and trial are indexed in
[`dokumentasi/INDEKS.md`](dokumentasi/INDEKS.md).

## Final result status

The six paired student runs, locked TEST evaluation, NVIDIA L40 inference
benchmark, and analysis are complete. The working hypothesis that pure KD
would beat the supervised student on TEST mAP50–95 was not supported: the means
are 0.6630 ± 0.0108 for pure KD and 0.7225 ± 0.0035 for supervised, across
three seeds. Pure KD reduced checkpoint parameters by 68.71%, checkpoint size
by 65.20%, and GFLOPs by 62.64% versus the teacher. Mean median latency was
25.01 ms for KD versus 25.72 ms for the teacher on the historical NVIDIA L40 benchmark.

Use [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md)
for the current Indonesian results/discussion draft and
[`artifacts/thesis_analysis_final_corrected/`](artifacts/thesis_analysis_final_corrected/)
for the hash-registered tables. The corrected tables use checkpoint parameter
counts before Conv-BN fusion. The earlier analysis directory is retained as an
audit trail and should not be used for final parameter counts.
For thesis tables, start at the
[`analisis_performa` index](analisis_performa/INDEKS.md). The
[`lab/server T01–T14 index`](analisis_performa/lab_server/README.md) records
the current table status, source files, and remaining measurements; the
[`prompt inventory`](prompt/inventaris_tabel_dan_prompt.md) links the lab and
robot workflows. The [20 October repository audit](docs/AUDIT_REPO_DAN_LANGKAH_LAB_SERVER_2026-10-20.md)
summarizes current evidence and the next lab/server steps.
The [seven-checkpoint VAL diagnosis](analisis_performa/lab_server/DIAGNOSIS_VAL_2026-10-20.md)
records error categories, confidence sweeps, and the current KD improvement recommendation.
[The 20 October model and server-table status](docs/STATUS_MODEL_DAN_TABEL_SERVER_2026-10-20.md)
records the pre-pilot checkpoint count and open table work. The completed
[`pure_weighted` pilot](docs/PILOT_PURE_WEIGHTED_2026-10-20.md) and
[`T04` ablation](analisis_performa/tabel/T04_ablasi_kd_val.md) contain the newer
VAL result and decision.

## Teacher, student, and data

- Teacher: `rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`.
- Student: `models/yolo11_tiny_kd.yaml`, with the YOLO11n layer topology and
  half the nano model's channel width. It starts from random initialization.
- Distillation: score-weighted feature L2 over P3/P4/P5 plus Smooth L1 box-logit
  and soft-target class-logit losses from the teacher. The teacher is frozen;
  the trainer's ground-truth detection loss is omitted, so labels do not update
  the student. This also trains the student's Detect head.
- Dataset: the existing `advance_vision_human` TRAIN and VAL image folders.
  The KD data YAML deliberately has no TEST entry.

The final student has 810,649 parameters versus 2,590,425 for the teacher.
Checkpoint size, GFLOPs, and host latency are recorded in the corrected analysis
tables and benchmark manifest. The student starts from random initialization;
the final TEST result is lower than the separate supervised control. Any future
changes must be selected on VAL and evaluated on a new locked test protocol.

## Deployment checkpoint

`models/weights/kd_student_best.pt` is the selected seed-42 pure-KD checkpoint,
copied from `runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42/weights/best.pt`.
Seed 42 had the highest VAL mAP50–95 among the three final KD seeds. This
checkpoint has run through a C920 ROS image topic on the OP3 host, but
camera-specific accuracy and tracking stability have not been validated. The
existing sessions are inference/runtime observations without labeled frames.
For the next camera session, use the [OP3 frame and labeling prompt](prompt/PROMPT_KUMPUL_FRAME_DAN_LABEL_OP3.md).
The [OP3 camera dataset folder](data/op3_camera_eval/README.md) documents raw frames, automatic draft labels, and human-reviewed labels.
To monitor detections while capturing frames, follow the [combined OP3 camera prompt](prompt/PROMPT_MONITOR_DAN_REKAM_KAMERA_OP3_BERSAMAAN.md).

## Run

Use the Python 3.11 environment already installed in `rafli/advance_vision`:

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_kd.py
```

Edit `configs/kd.yaml` to change epochs, batch size, GPU device, or the
distillation weight. Training refuses to overwrite an existing run directory.
The initial checkpoint at `runs/kd/yolo11_tiny_pure_kd_v4/` is an exploratory
pilot: it finished before the current dataset fingerprint was captured, so the
locked TEST evaluator will reject it. The final seed-42 run uses a fresh output
directory and binds the fingerprint from the start:

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_kd.py \
  --seed 42 --run-name yolo11_tiny_pure_kd_v4_locked_seed42
```

Checkpoints, `results.csv`, and the provenance manifest are written under
`runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42/` for that final seed.

## Thesis control model

For a separate supervised control using the same student architecture and
training schedule, use `configs/supervised_baseline.yaml` with
`scripts/train_supervised_baseline.py`. This run trains from the labels in
TRAIN; its loss is not combined with the pure-KD objective. VAL selects its
checkpoint, and the TEST split is not included in the training YAML. Pass
`--seed 1337` or another seed to create a distinct run directory for repeated
experiments.

## Reproduce the paired final experiment

The final run is complete. For a fresh reproduction, train supervised seed 42 first with the run name
expected by the queue. Then launch the serial queue once; it runs KD seed 42,
the remaining supervised/KD pairs for seeds 1337 and 2025, and validates each
manifest without opening TEST. Launch the final pipeline once after the queue;
it waits for queue completion, checks all six student checkpoints, evaluates
the locked TEST set once, benchmarks inference, and builds the analysis tables.
Do not launch individual jobs alongside the queue. The queue/pipeline `--resume`
flags are only for states explicitly marked failed or interrupted, after
inspecting existing artifacts.

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_supervised_baseline.py \
  --seed 42 --run-name yolo11_tiny_supervised_seed42_retry1
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/run_student_training_queue.py
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/run_locked_final_pipeline.py
```

The source split inventory, label counts, provenance gaps, and possible
cross-split scene overlap are summarized in
[`AUDIT_DATASET_SKRIPSI.md`](AUDIT_DATASET_SKRIPSI.md). Exact image/label SHA-256
records are in
[`artifacts/advance_vision_dataset_fingerprint.json`](artifacts/advance_vision_dataset_fingerprint.json).
The thesis scope and work stages are in
[`PLANNING_SKRIPSI.md`](PLANNING_SKRIPSI.md); the frozen seed, loss, metric,
checkpoint-selection, and TEST gates are in
[`PROTOKOL_EKSPERIMEN_SKRIPSI.md`](PROTOKOL_EKSPERIMEN_SKRIPSI.md).
The Indonesian and English abstract drafts using the locked final results are
in [`DRAF_ABSTRAK_SKRIPSI.md`](DRAF_ABSTRAK_SKRIPSI.md).
The initial proposal draft for Chapters I–III is in
[`DRAF_PROPOSAL_BAB_I-III.md`](DRAF_PROPOSAL_BAB_I-III.md), and the chapter map
is in [`KERANGKA_BAB_SKRIPSI.md`](KERANGKA_BAB_SKRIPSI.md).
Dataset metadata copies and their source hashes are in [`datasheet/`](datasheet/README.md), and the initial academic bibliography is in [`REFERENSI_SKRIPSI.bib`](REFERENSI_SKRIPSI.bib).
The bounded literature audit distinguishing direct teacher-only objectives from
hybrid and pseudo-label objectives is in
[`TINJAUAN_PUSTAKA_KD_DETEKSI.md`](TINJAUAN_PUSTAKA_KD_DETEKSI.md); it is not a
systematic review and does not support a “first pure KD” novelty claim.
To compare checkpoint inference speed using the same in-memory VAL image, use
`scripts/benchmark_inference.py`; its report labels the result as a server
diagnostic, not as a robot deployment benchmark.

For a fresh experiment, after every student checkpoint is complete and selected using VAL, run
`scripts/evaluate_locked_test.py` with all six best student checkpoints. It
also evaluates the teacher after verifying its source training artifact,
validation-best checkpoint hash, and historical final-TEST evidence. This
records that the teacher was evaluated on TEST previously; the student
checkpoints remain selected using VAL only. The evaluator verifies the TEST
file hashes against the dataset fingerprint, writes its label cache inside a
new output directory, and refuses to reuse an existing evaluation directory.
Do not use its TEST metrics to make further model or hyperparameter changes.
After the locked TEST manifest and speed benchmark exist, create per-model and
mean/standard-deviation tables, per-class deltas against the teacher, and
paired KD-versus-supervised differences with `scripts/build_thesis_analysis.py`;
it checks their fingerprints, records SHA-256 for every generated table/report,
and requires the teacher plus every paired seed.

The supervised seed-42 baseline is complete and its dataset provenance was
linked after training by re-hashing the full snapshot and checking the training
YAML and pre-run timestamp. Its manifest still lacks run-time hashes for the
YAML/config and structured runtime metadata; this legacy limitation is recorded
in the run manifest and results draft.

Environment provenance (the source lock snapshot and clean runtime package
freeze) is documented in [`environment/README.md`](environment/README.md).
