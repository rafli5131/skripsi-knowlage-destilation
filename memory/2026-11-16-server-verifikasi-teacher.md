# Verifikasi jalur TEST baris teacher di server — 16 November 2026

Teacher utama `e05b2b21…420b8c` (5.481.875 bait) ada di OP3 pada `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt` (salinan identik di `.cache/hardware_models/fp32_pytorch/best.pt`), bukan di `bre_skripsi/models_local/`. Salinan: server `models_local/teacher_utama/best.pt` dan laptop `~/cadangan_teacher_utama/`; bobot T42 di laptop `~/cadangan_t42/`.

Run memakai `.venv-train` di repo server (Ultralytics 8.4.130, torch 2.4.1); `~/rf-venv` tidak berisi Ultralytics. Run 13 November dan 16 November memakai `--test-images` ke `/mnt/nas-hpg9/dindarosyidah/skripsi/data/advance_vision_human/test/images`, bukan `--data`. Hasil di [`verifikasi_jalur_test_20261116_teacher`](../analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher/RINGKASAN.md); keputusan di D24. Status `git_dirty: true` berasal dari file untracked lama di `artifacts/` dan `runs/`, bukan dari skrip.
