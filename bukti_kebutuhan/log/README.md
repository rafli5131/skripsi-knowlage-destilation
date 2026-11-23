# Log pendukung bukti kebutuhan

Folder ini mengumpulkan salinan log yang menjadi dasar kasus uji KF-01 sampai KF-05 dan KNF-01. Semua berkas
adalah salinan identik dari dokumentasi percobaan dan `log_op3_pelengkap/`; berkas aslinya tetap di tempat semula
dan tidak diubah. Daftar lengkap beserta sumber asli dan SHA-256 ada di [`indeks_log.csv`](indeks_log.csv)
(101 berkas).

| Folder | Isi | Dipakai untuk |
|---|---|---|
| `run_live_24/<run_id>/` | Untuk 24 run live: `jendela_runtime.csv` (satu baris per frame: timestamp, durasi tiap tahap, CPU, RSS, error), `jendela_deteksi.csv` (satu baris per kotak: kelas, ID, confidence, koordinat), `summary_metrics.json`, dan `tabel_deteksi.csv` | KF-01, KF-02, KF-04, KNF-01 |
| `pelacakan_percobaan_27/` | Log jendela, ringkasan, dan tabel deteksi sesi bola bergerak | KF-03 |
| `cek_log_mentah_T45/` | Manifest pemeriksaan ulang 24 log mentah di OP3 terhadap T36 | KF-04 |

Log jendela berisi frame di dalam jendela ukur 60 detik, sama dengan yang dipakai T36. Log mentah penuh (termasuk
pemanasan) dan gambar kamera tetap di OP3.
