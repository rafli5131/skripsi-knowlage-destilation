# Laptop Ubuntu dan uji ulang — 23 November 2026

Laptop kerja sekarang Ubuntu 24.04.5 dengan Python 3.12.3. Venv uji ada di `~/.venvs/skripsi-uji` (pytest 9.2.0, numpy 1.26.4, PyYAML 6.0.3, matplotlib 3.11.2), di luar repositori.

- Shell laptop memuat `PYTHONPATH` ROS 2 Jazzy. Jalankan pytest dan skrip repo dengan `env -u PYTHONPATH`; tanpa itu pytest berhenti karena plugin `launch_testing` membutuhkan `lark`.
- Dengan `env -u PYTHONPATH`, `pytest -q tests --ignore=tests/test_kd_hybrid.py` menghasilkan 40 lulus. Masalah `fcntl` dan pemisah path hanya terjadi di Windows.
- `tests/test_kd_hybrid.py` membutuhkan torch, ultralytics, dan bobot teacher pada path server; jalankan di server lab.
- PNG `jejak_waktu/` berbeda hash bila dibangkitkan dengan matplotlib lain; CSV identik.
- Laptop belum punya kunci SSH dan tidak bisa push ke GitHub (HTTPS tanpa kredensial). Akses OP3 memakai koneksi bersama dari login password Bhre.

Rincian: [laporan uji](../dokumentasi/2026-11-23/LAPORAN_UJI_LAPTOP_UBUNTU.md).

Pembaruan: `tests/test_kd_hybrid.py` lulus 5/5 di server lab pada CPU dengan `env -u PYTHONPATH CUDA_VISIBLE_DEVICES="" .venv-train/bin/python -m unittest discover -s tests -p test_kd_hybrid.py -v` (pytest tidak ada di `.venv-train`). Akun `rafli5131` sudah dihapus, sehingga path teacher `/mnt/nas-hpg9/rafli5131/...` di tes dan di `configs/model_registry.yaml` tidak dapat diakses. Di server, path cadangan `~/skripsi/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt` adalah tautan ke `models_local/teacher_utama/best.pt`. Pembaruan path di registry menunggu keputusan Bhre.
