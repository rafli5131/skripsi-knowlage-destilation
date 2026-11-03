# Supervised seed 1337 — idle ulangan 2

Run `20261103_eq_sup1337_idle_u2` memakai kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, empat thread intra-op dan dua inter-op, 30 frame warm-up, serta preview SSH-X. Jendela ukur 60 detik: 06:03:01–06:04:01 UTC. Tidak ada perintah gerak robot.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 749 / 0 |
| Latensi callback rata-rata / P95 | 69,39 / 158,52 ms |
| FPS efektif | 12,47 frame/detik |
| CPU proses rata-rata | 1295,37% dari satu CPU logis |
| RAM RSS rata-rata | 359,63 MiB |
| Simpangan kepala maksimum | 0,001534 rad (1 count) |
| Simpangan badan maksimum | 0,003069 rad (2 count) |

Kelima sampel JointState mencakup 20 sendi. Pemeriksaan otomatis memberi status `lulus_cek_otomatis`; audit protokol akhir tetap diperlukan. Bola, gawang, dan robot masing-masing muncul pada 749/749 frame ukur. **Cakupan keluaran ini bukan akurasi berlabel.** Angka CPU/RAM, P95, dan tahapan latensi lengkap ada di [ringkasan](summary_metrics.json) dan [tabel performa](tabel_performa.csv).

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay setelah jendela](frame_deteksi_sesudah_jendela.png), [grafik runtime HD](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), [tabel deteksi](tabel_deteksi.csv), serta telemetry [pra](telemetry_pre.txt), [tengah 1](telemetry_mid1.txt), [tengah 2](telemetry_mid2.txt), [sesudah 1](telemetry_after.txt), [sesudah 2](telemetry_after2.txt). CSV mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_idle_u2.*`.
