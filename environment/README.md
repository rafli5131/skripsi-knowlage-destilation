# Environment provenance

This directory records the software environment evidence available for the
thesis runs. It distinguishes the source project's dependency lock from a
read-only snapshot of packages visible in the training virtual environment.

## Files

- `advance_vision_pyproject.toml` and `advance_vision_uv.lock` are copies of
  `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/pyproject.toml` and
  `uv.lock`. The source files were last modified on 2026-09-02. They preserve
  the source project's declared dependencies and lock resolution.
- `runtime_freeze_2026-10-09.txt` was captured on 2026-10-09 with `uv pip
  freeze` against the existing source-project virtual environment. The command
  used `env -u PYTHONPATH` so ROS or other inherited Python packages would not
  contaminate package discovery. `UV_CACHE_DIR` was directed to `/tmp` because
  the default cache location is read-only in this workspace. No packages were
  installed or changed.

SHA-256 checksums of these workspace copies:

| File | SHA-256 |
| --- | --- |
| `advance_vision_pyproject.toml` | `2ff6c15dd47c4d6d7bcbe9b47a62d52e268aa5a96495dce7351c214ea809eff4` |
| `advance_vision_uv.lock` | `a508b970ee19ec8cf6af1f64bfdd6dd047692cdb74e6d5c8518ae94ca34ba85d` |
| `runtime_freeze_2026-10-09.txt` | `01b664a10576442140be1316de44fc997c2a402b65c399c99f232668fa87a65a` |

## Runtime observed

The clean virtual-environment interpreter reports Python 3.11.2,
PyTorch 2.4.1+cu121, torchvision 0.19.1+cu121, Ultralytics 8.4.130, NumPy
1.26.4, OpenCV headless 4.10.0.84, and PyYAML 6.0.3. The active supervised
seed-42 run manifest also records PyTorch 2.4.1+cu121 and Ultralytics 8.4.130.
Queue launchers remove inherited `PYTHONPATH`; this matches the clean runtime
used to inspect the environment.

A package comparison performed on the saved artifacts found that all 114
packages in the runtime freeze are present in the source lock at exactly the
same versions. The lock has three additional entries absent from the freeze:
`colorama`, `pyreadline3`, and the virtual project package
`skripsi-yolo11-qat-openvino`.

## Provenance limit

The source lock snapshot predates the thesis runs. The runtime freeze file has
mtime 2026-10-09 06:59:14 +0700 (2026-10-08 23:59:14 UTC), about two hours
before locked KD seed 42 started at 2026-10-09 01:59:22 UTC. This is supporting
pre-run evidence for the KD environment; the run manifest also records key
runtime versions and CUDA/GPU metadata. The freeze was captured after
supervised seed 42 started at 2026-10-08 19:59:18 UTC, so it cannot establish
that run's complete package set at startup. The lockfile remains a
source-project snapshot, not a freeze generated from the active environment.
The virtual environment is external, so this workspace cannot rule out package
changes after the snapshot during the KD run or later queued runs. The virtual
environment itself was not modified here.
