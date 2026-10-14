# Bhre-Knowledge-Distillation

## Pure Teacher-Only Knowledge Distillation

This workspace evaluates a narrower YOLO11 student trained from the frozen
FP32 teacher in `/mnt/nas-hpg9/rafli5131/rafli/advance_vision`. The KD objective
uses teacher-only feature and detection-output distillation: there is no NNCF,
fake quantization, or supervised detection loss in the student update. TEST was
excluded from all student training and checkpoint selection; it was opened only
after the six student checkpoints had been locked by VAL. Training uses FP32.

## Current OP3 direction

The completed experiments below use Advance Vision data and establish the
current pure-KD checkpoints. The planned next phase is to evaluate the selected
student `.pt` on ROBOTIS OP3 using PyTorch/Ultralytics on CPU. OpenVINO and
QAT/INT8 are not part of the current deployment plan. The checkpoint has not yet
been tested on the OP3 camera. The proposal and planning drafts in this repo
describe the completed Advance Vision study and need revision before serving as
the final OP3 thesis proposal.

## Final result status

The six paired student runs, locked TEST evaluation, NVIDIA L40 inference
benchmark, and analysis are complete. The working hypothesis that pure KD
would beat the supervised student on TEST mAP50–95 was not supported: the means
are 0.6630 ± 0.0108 for pure KD and 0.7225 ± 0.0035 for supervised, across
three seeds. Pure KD reduced checkpoint parameters by 68.71%, checkpoint size
by 65.20%, and GFLOPs by 62.64% versus the teacher. Mean median latency was
25.01 ms for KD versus 25.72 ms for the teacher on this host.

Use [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md)
for the current Indonesian results/discussion draft and
[`artifacts/thesis_analysis_final_corrected/`](artifacts/thesis_analysis_final_corrected/)
for the hash-registered tables. The corrected tables use checkpoint parameter
counts before Conv-BN fusion. The earlier analysis directory is retained as an
audit trail and should not be used for final parameter counts.

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
checkpoint has not yet been validated on the ROBOTIS OP3 camera or runtime.

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
