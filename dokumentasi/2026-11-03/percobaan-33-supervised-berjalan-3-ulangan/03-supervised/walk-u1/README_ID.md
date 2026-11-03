# Supervised berjalan — ulangan 1

Pada 3 November 2026, operator mengonfirmasi robot walk-ready, area kosong, dan pendampingan sebelum ulangan. Run `20261103_eq_sup1337_walk_u1` menggunakan preview SSH-X, kamera 640×480, CPU FP32, BoT-SORT, confidence 0,25, dan IoU 0,45. Gait menerima ack mulai 09:47:48 UTC dan ack berhenti 09:48:51 UTC. Kepala ID 19/20 tidak menerima perintah posisi; guard mencatat deviasi maksimal satu count.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 742 / 0 |
| Latensi rata-rata / P95 | 71,65 / 161,84 ms |
| FPS efektif | 12,36 frame/detik |
| CPU proses | 1296,41% satu CPU logis |
| RAM RSS | 361,63 MiB |

Status `lulus_cek_otomatis` untuk CSV dan telemetry; audit protokol akhir masih terbuka. Keluaran model per kelas pada [tabel deteksi](tabel_deteksi.csv) bukan akurasi berlabel.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay setelah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [guard gait](gait_guard.json), [tabel performa](tabel_performa.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), dan telemetry [sebelum](telemetry_pre.txt), [sesudah](telemetry_after.txt), [sesudah kedua](telemetry_after2.txt). Sampel kepala dan empat sendi kaki selama gait tersedia di [head guard](head_guard_samples.csv). CSV mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_walk_u1.*`.
