# Log progres — 23 November 2026

[Prompt pelengkap log OP3](../../prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md) dijalankan dari laptop melalui SSH. Robot hanya dibaca: tidak ada kamera, ROS, servo, gait, training, inferensi, atau perekaman frame, dan `git status` repositori robot tidak berubah. Hasilnya ada di [`log_op3_pelengkap/`](../../log_op3_pelengkap/README.md), dengan [laporan sesi](../../log_op3_pelengkap/LAPORAN_SESI.md) dan package baru [`op3_log_pelengkap`](../../ros2_packages/op3_log_pelengkap/README.md).

- **Log jendela 15 run live:** 15 dari 15 diekstrak. Hash log mentah dan metadata cocok dengan T36. Jumlah baris, error, rerata latensi, dan FPS juga cocok dengan T36; selisih terbesar 1,4e-14 ms. Sebagai kontrol, 9 run yang sudah ada di repositori diekstrak ulang, dan hasilnya identik byte demi byte.
- **Metadata capture T38:** 11 sesi, ditambah 4 sesi sumber dari dua sesi kurasi.
- **Metadata capture T43:** 5 sesi yang dipakai, 3 sesi yang dikecualikan, dan 14 berkas eksperimen. Hash manifest kelima sesi yang dipakai cocok dengan manifest T43.
- **Timestamp capture:** tercatat untuk semua sesi di [`ringkasan_capture.csv`](../../log_op3_pelengkap/ringkasan_capture.csv).
- **Catatan training teacher:** `manifest.json`, `args.yaml`, dan `results.csv` disalin dari robot. Salinan laptop hanya berbeda akhir baris. Menurut skrip training yang tersimpan, `timestamp` teacher (2 September 2026, 17:04 WIB) menandai awal training. Versi skrip yang dipakai saat itu tidak terverifikasi, dan waktu selesai tidak tercatat.
- **Hasil build ulang:** [`jejak_waktu/`](../../jejak_waktu/README.md) dan [`bukti_kebutuhan/`](../../bukti_kebutuhan/README.md) dibangkitkan ulang. Log per frame kini tersedia untuk 24 run, baris teacher terisi beserta 100 epoch, dan KF-04 menghitung 24/24 log jendela. `build_jejak_waktu.py` menempatkan `timestamp` teacher sebagai waktu mulai (atas persetujuan Bhre) dan tidak menggambar baris teacher pada grafik.
- **Tes:** `pytest` dipasang atas izin Bhre. Hasilnya 28 lulus. Ada 2 gagal pada `test_server_paths.py` (pemisah path Windows) dan 2 galat collection pada tes T42 (modul `fcntl` khusus Unix). Keempatnya terkait platform laptop, dan tesnya tidak diubah.
- **Berkas yang tidak ditemukan:** tidak ada. `SHA256SUMS.txt` teacher memang tidak ada di robot.
- **Berkas yang sengaja tidak disalin:** gambar, label, contact sheet, `predictions.jsonl`, `prelabel_manifest.json`, `review_log.jsonl`, bobot `.pt`, dan kode.
- **Direktori sementara di robot:** sudah dihapus.

## Pindah ke laptop Ubuntu

[Prompt pindah laptop](../../prompt/PROMPT_PINDAH_LAPTOP_UBUNTU_DAN_UJI_2026-11-23.md) dijalankan di laptop Ubuntu 24.04.5 (Python 3.12.3) dengan venv `~/.venvs/skripsi-uji` di luar repositori. Rincian ada di [laporan uji](LAPORAN_UJI_LAPTOP_UBUNTU.md).

- **Tes:** 40 lulus, 0 gagal, 0 galat (`--ignore=tests/test_kd_hybrid.py`). Keempat masalah Windows (dua galat `fcntl` pada tes T42 dan dua kegagalan pemisah path pada `test_server_paths.py`) lulus di Linux. Tes tidak diubah.
- **Syarat lingkungan:** `PYTHONPATH` ROS 2 Jazzy di shell laptop membuat pytest memuat plugin `launch_testing` yang gagal karena modul `lark` tidak ada. Pytest harus dijalankan dengan `env -u PYTHONPATH`.
- **`test_kd_hybrid.py`:** tidak dijalankan karena bobot teacher tidak ada pada path yang dirujuk tes; lebih tepat di server lab.
- **Skrip build:** keluaran `jejak_waktu/` dan `bukti_kebutuhan/` identik dengan yang di-commit kecuali PNG garis waktu (versi matplotlib), baris commit pembangkit di README, dan manifest yang mencatat keduanya.
- **Koreksi log 13 November:** "TP gawang hanya turun 3 sampai 13 dibanding jalur prediksi pada ambang TEST" diperiksa terhadap hasil 13 November dan benar.
- **`test_kd_hybrid.py` di server lab:** 5 dari 5 lulus di CPU dengan `.venv-train` (torch 2.4.1, ultralytics 8.4.130), lewat `unittest discover` karena pytest tidak ada di venv itu. Path teacher `/mnt/nas-hpg9/rafli5131/...` tidak dapat diakses karena akun `rafli5131` sudah dihapus; tes memakai path cadangan yang ditautkan ke `models_local/teacher_utama/best.pt` dengan hash cocok. Rincian di [laporan uji](LAPORAN_UJI_LAPTOP_UBUNTU.md#7-tindak-lanjut-test_kd_hybridpy-di-server-lab).
