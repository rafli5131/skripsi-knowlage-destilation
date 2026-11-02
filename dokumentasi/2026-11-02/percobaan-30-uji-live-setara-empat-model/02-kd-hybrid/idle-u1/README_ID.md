# KD Hybrid full seed 1337 — idle ulangan 1

Run mentah `20261102_eq_hybrid1337_idle_u1` memakai kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, dan preview SSH-X aktif. Robot tanpa gait; ID 19/20 tidak diberi perintah posisi. Jendela ukur 60 detik adalah 12:44:04,464–12:45:04,464 UTC setelah 30 frame warm-up.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 792 / 0 |
| Latensi callback rata-rata / P95 | 66,82 / 157,52 ms |
| FPS efektif | 13,20 frame/detik |
| CPU proses rata-rata | 1303,85% dari satu CPU logis |
| RAM RSS rata-rata | 358,63 MiB |
| Simpangan maksimum kepala | 0,001534 rad (sekitar 1 count) |
| Simpangan maksimum badan | 0,001535 rad |

Cakupan keluaran deteksi: bola 792/792 frame (100%), gawang 784/792 (99,0%), robot 792/792 (100%). Ini bukan accuracy, precision, atau recall berlabel. Lima sampel telemetri (`pre`, dua tengah, dua sesudah) dan [waktu pengambilannya](sampling_times.json) tersimpan. Pemeriksaan otomatis CSV/telemetri lulus; kontinuitas preview dan kondisi fisik masih perlu audit akhir.

Bukti: [overlay sebelum run](preview_sebelum_run.png), [overlay setelah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), dan [grafik kelas](grafik_keluaran_kelas_id.png). Log mentah lokal: `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u1.*`.
