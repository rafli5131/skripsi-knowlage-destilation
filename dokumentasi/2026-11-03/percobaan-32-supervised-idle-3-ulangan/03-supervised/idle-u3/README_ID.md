# Supervised seed 1337 — idle ulangan 3

Run `20261103_eq_sup1337_idle_u3` memakai protokol yang sama dengan ulangan 1–2: kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, 30 frame warm-up, jendela ukur 60 detik, dan preview SSH-X. Jendela ukur 06:06:35–06:07:35 UTC. Tidak ada perintah gerak robot.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 746 / 0 |
| Latensi callback rata-rata / P95 | 71,47 / 159,53 ms |
| FPS efektif | 12,43 frame/detik |
| CPU proses rata-rata | 1300,11% dari satu CPU logis |
| RAM RSS rata-rata | 360,00 MiB |
| Simpangan kepala / badan maksimum | 1 / 3 encoder count |

Status otomatis **`perlu_audit`**: `r_sho_pitch` bergeser sekitar 0,004604 rad atau tiga count pada kedua sampel tengah dan sampel sesudah pertama. Batas idle adalah dua count. Run asli disimpan dan tidak dipakai sebagai run sah tanpa pemeriksaan lebih lanjut. Keluaran model per kelas ada di [tabel deteksi](tabel_deteksi.csv); angka cakupan **bukan akurasi berlabel**.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [tabel performa](tabel_performa.csv), [grafik runtime HD](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), serta telemetry [pra](telemetry_pre.txt), [tengah 1](telemetry_mid1.txt), [tengah 2](telemetry_mid2.txt), [sesudah 1](telemetry_after.txt), [sesudah 2](telemetry_after2.txt). CSV mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_idle_u3.*`.
