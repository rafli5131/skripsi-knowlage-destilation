# KF-04 Mencatat runtime per frame

**Kebutuhan:** setiap frame yang diproses dicatat beserta timestamp, durasi tahap pemrosesan,
penggunaan CPU, RSS, dan status error.

**Implementasi:** node menulis CSV per frame dengan 22 kolom, antara lain
`capture_stamp_ns`, `receive_time_utc`, `preprocess_ms`, `inference_ms`, `postprocess_ms`,
`end_to_end_ms`, `process_cpu_percent`, `process_rss_bytes`, dan `error`.

**Prosedur:**

1. Memeriksa 24 log jendela (`jendela_runtime.csv`) yang tersimpan di repositori:
   kelengkapan kolom, sel wajib yang kosong pada baris tanpa error, dan kecocokan jumlah baris
   dengan T36.
2. Untuk 24 run, log mentah di OP3 dibaca ulang pada percobaan 41 (T45); rerata `end_to_end_ms`
   tiap run cocok dengan T36 pada toleransi 1e-6 dan hash CSV mentahnya sama dengan yang tercatat
   di T36.

**Kriteria lulus:** semua kolom tersedia, sel wajib terisi, dan log mentah cocok dengan T36.

**Hasil:** 24/24 log jendela lengkap
([`bukti_kolom_log_jendela_repo.csv`](bukti_kolom_log_jendela_repo.csv)).
24/24 log mentah cocok dengan T36
([`bukti_log_mentah_24_run_T45.csv`](bukti_log_mentah_24_run_T45.csv),
[T45](../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md)).

**Batas:** log jendela 24 run tersedia di repositori; sebagian diekstrak kemudian dari log mentah OP3 ke `log_op3_pelengkap/` setelah hash log mentah dicocokkan dengan T36.

**Log pendukung** di [`../log/`](../log/README.md): `run_live_24/<run_id>/jendela_runtime.csv` (24 log per frame) dan `cek_log_mentah_T45/runtime_stages_manifest.json`.
