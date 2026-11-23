#!/bin/bash
cd ~/skripsi/skripsi-knowlage-destilation
env -u PYTHONPATH .venv-train/bin/python scripts/verify_test_inference_path.py \
  --test-images /mnt/nas-hpg9/dindarosyidah/skripsi/data/advance_vision_human/test/images \
  --teacher models_local/teacher_utama/best.pt \
  --models teacher_fp32 \
  --device cpu \
  --output analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher \
  2>&1 | tee /tmp/verifikasi_teacher.log
echo "EXIT=${PIPESTATUS[0]}" | tee -a /tmp/verifikasi_teacher.log
