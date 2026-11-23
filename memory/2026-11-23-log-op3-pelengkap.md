# Log OP3 pelengkap — 23 November 2026

Prompt `PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md` dijalankan dari laptop lewat SSH. Robot hanya dibaca, dan `git status` repo robot tidak berubah. Hasil ada di [`log_op3_pelengkap/`](../log_op3_pelengkap/README.md), dibuat dengan package [`op3_log_pelengkap`](../ros2_packages/op3_log_pelengkap/README.md).

- **Log jendela:** 15/15 run diekstrak ke `log_op3_pelengkap/live_24_run/`. Hash log mentah dan metadata sama dengan T36, dan jumlah baris, error, latensi, serta FPS cocok dengan T36. Ekstraksi ulang 9 run lama identik byte demi byte dengan berkas di repo.
- **Capture:** metadata T38 (11 sesi dan 4 sesi sumber kurasi) dan T43 (5 sesi dipakai dan 3 dikecualikan) ada di `t38_capture/` dan `t43_capture/`. Waktu capture per sesi ada di `ringkasan_capture.csv`, diambil dari `captured_at_utc`.
- **Teacher:** catatan training ada di `teacher_training/`. `timestamp` teacher ditafsirkan sebagai waktu mulai training menurut `step03_train_fp32.py` yang tersimpan; versi skrip saat training tidak terverifikasi.
- **Build ulang:** `jejak_waktu/` dan `bukti_kebutuhan/` dibangkitkan ulang dengan log ini.
- **Tes di laptop Windows:** 4 kegagalan tes terkait platform (`fcntl` dan pemisah path) dan tidak menyangkut skrip build.
- **Batas yang tetap berlaku:** gambar, label, prediksi, bobot, dan log mentah penuh tidak masuk Git.

Log pendukung KF/KNF (log jendela 24 run, sesi pelacakan percobaan 27, manifest T45) disalin ke `bukti_kebutuhan/log/` oleh `scripts/build_bukti_kebutuhan.py`; indeks sumber dan hash di `bukti_kebutuhan/log/indeks_log.csv`.
