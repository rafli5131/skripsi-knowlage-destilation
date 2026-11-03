# KD murni berjalan — pengganti ulangan 3

Run `20261103_eq_kd42_walk_u3_ulang1` dilakukan setelah konfirmasi operator sebagai pengganti [ulangan 3 sebelumnya](../walk-u3/README_ID.md). Preview SSH-X aktif. Gait menerima ack mulai 10:31:37 UTC dan berhenti 10:32:40 UTC. ID 19/20 tidak diberi perintah posisi; guard mencatat simpangan maksimum satu count.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 742 / 0 |
| Latensi rata-rata / P95 | 69,82 / 159,18 ms |
| FPS efektif | 12,38 frame/detik |
| CPU proses | 1294,10% satu CPU logis |
| RAM RSS | 359,81 MiB |
| Simpangan badan maksimum pada sampel | 0,34208 rad |

Run **lulus cek otomatis** CSV/telemetry dan dipetakan ke slot ulangan 3. Bola, gawang, dan robot memiliki keluaran pada 742/742 frame; ini cakupan prediksi, bukan akurasi berlabel. Audit akhir protokol masih terbuka.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [guard gait](gait_guard.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [telemetry sebelum](telemetry_pre.txt), [sesudah](telemetry_after.txt), [sesudah kedua](telemetry_after2.txt), dan [sampel kepala/kaki](head_guard_samples.csv). Log mentah lokal: `runs/op3_pytorch/20261103_eq_kd42_walk_u3_ulang1.*`.
