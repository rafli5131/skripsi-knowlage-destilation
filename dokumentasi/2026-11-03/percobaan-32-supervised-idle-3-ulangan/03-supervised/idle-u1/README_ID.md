# Supervised seed 1337 — idle ulangan 1

Run `20261103_eq_sup1337_idle_u1` memakai kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, empat thread intra-op dan dua inter-op, 30 frame warm-up, serta preview SSH-X. Jendela ukur 60 detik: 05:59:09–06:00:09 UTC. Tidak ada perintah gerak robot.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 729 / 0 |
| Latensi callback rata-rata / P95 | 72,50 / 159,81 ms |
| FPS efektif | 12,15 frame/detik |
| CPU proses rata-rata | 1296,01% dari satu CPU logis |
| RAM RSS rata-rata | 355,58 MiB |
| Simpangan kepala maksimum | 0,001534 rad (1 count) |
| Simpangan badan maksimum pada lima sampel | 0,006139 rad (4 count) |

Bola, gawang, dan robot masing-masing muncul pada 729/729 frame ukur menurut keluaran model. **Ini cakupan prediksi, bukan akurasi berlabel.** Dua sampel tengah menunjukkan badan bergeser paling banyak satu count, tetapi sampel kedua **sesudah jendela** menunjukkan `r_sho_pitch` bergeser empat count dari baseline. Oleh karena itu status otomatis `perlu_audit`; run ini tidak boleh dipakai sebagai run sah tanpa meninjau penyebabnya. Run mentah tetap disimpan.

[Overlay sesudah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik runtime HD](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), dan sampel [pra](telemetry_pre.txt), [tengah 1](telemetry_mid1.txt), [tengah 2](telemetry_mid2.txt), [sesudah 1](telemetry_after.txt), [sesudah 2](telemetry_after2.txt) tersedia. CSV mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_idle_u1.*`.
