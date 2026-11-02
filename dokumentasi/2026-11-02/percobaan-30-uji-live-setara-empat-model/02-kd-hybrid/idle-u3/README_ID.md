# KD Hybrid full seed 1337 — idle ulangan 3

Run mentah `20261102_eq_hybrid1337_idle_u3` memakai kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, dan preview SSH-X aktif. Robot tanpa gait; ID 19/20 tidak diberi perintah posisi. Jendela ukur 60 detik adalah 12:51:40,572–12:52:40,572 UTC setelah 30 frame warm-up; jeda dari run sebelumnya melebihi 120 detik.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 830 / 0 |
| Latensi callback rata-rata / P95 | 64,21 / 162,58 ms |
| FPS efektif | 13,85 frame/detik |
| CPU proses rata-rata | 1311,58% dari satu CPU logis |
| RAM RSS rata-rata | 360,21 MiB |
| Simpangan maksimum kepala | 0,001534 rad (sekitar 1 count) |
| Simpangan maksimum badan | 0,001535 rad |

Cakupan keluaran: bola 830/830 frame (100%), gawang 821/830 (98,9%), robot 830/830 (100%). Ini bukan metrik akurasi/precision berlabel. Lima sampel telemetri dan [waktu pengambilannya](sampling_times.json) tersimpan. Pemeriksaan otomatis CSV/telemetri lulus; audit akhir kontinuitas preview dan kondisi fisik tetap diperlukan.

Bukti: [overlay sebelum run](preview_sebelum_run.png), [overlay setelah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), dan [grafik kelas](grafik_keluaran_kelas_id.png). Log mentah lokal: `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u3.*`.
