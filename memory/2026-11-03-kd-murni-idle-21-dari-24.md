# Memory — KD murni idle, 21/24 slot

Pengguna meminta tiga ulangan idle KD murni seed 42 tanpa konfirmasi antar-run. Ulangan 1–3 selesai dan lulus cek otomatis CSV/telemetry, tanpa perintah gerak. Checkpoint `models/weights/kd_student_best.pt` SHA-256 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`. Rerata ± SD sampel: 74,09 ± 1,04 ms, 12,07 ± 0,05 FPS, CPU 1300,21 ± 2,44% satu CPU logis, RSS 356,97 ± 5,92 MiB; 2.172 frame ukur tanpa error. [Dokumentasi](../dokumentasi/2026-11-03/percobaan-34-kd-murni-idle-3-ulangan/README_ID.md) memuat keterbatasan protokol.

Matriks kampanye 21/24 slot lulus cek otomatis; tersisa tiga ulangan KD murni berjalan. Preview KD murni dinyalakan kembali; periksa ulang keadaan proses dan fisik sebelum melanjutkan. Uji berjalan tetap memerlukan konfirmasi operator setiap run, preview segar, area kosong, dan penjagaan posisi kepala ID 19/20. Audit protokol akhir dan T36/T37 final menunggu semua run.
