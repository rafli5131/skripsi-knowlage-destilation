# Supervised berjalan — ulangan 2

Run `20261103_eq_sup1337_walk_u2` dilakukan setelah operator menyatakan siap. Preview SSH-X aktif, kamera 640×480 dan model Supervised seed 1337 dengan parameter sama seperti ulangan 1. Gait menerima ack mulai 09:53:18 UTC dan berhenti 09:54:21 UTC. Kepala ID 19/20 tidak diberi perintah posisi; guard mencatat simpangan maksimum satu count.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 794 / 0 |
| Latensi rata-rata / P95 | 67,77 / 159,98 ms |
| FPS efektif | 13,23 frame/detik |
| CPU proses | 1307,93% satu CPU logis |
| RAM RSS | 362,18 MiB |

Status `lulus_cek_otomatis` untuk CSV dan telemetry; audit protokol akhir masih terbuka. [Tabel deteksi](tabel_deteksi.csv) mencatat keluaran model, bukan akurasi berlabel.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [guard gait](gait_guard.json), [tabel performa](tabel_performa.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), telemetry [sebelum](telemetry_pre.txt), [sesudah](telemetry_after.txt), [sesudah kedua](telemetry_after2.txt), serta [sampel kepala dan kaki](head_guard_samples.csv). Log mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_walk_u2.*`.
