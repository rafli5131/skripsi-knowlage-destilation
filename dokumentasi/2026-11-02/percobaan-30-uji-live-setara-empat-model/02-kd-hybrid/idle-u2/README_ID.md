# KD Hybrid full seed 1337 — idle ulangan 2

Run mentah `20261102_eq_hybrid1337_idle_u2` memakai kamera OP3 640×480, CPU FP32, BoT-SORT, confidence 0,25, IoU NMS 0,45, dan preview SSH-X aktif. Robot tanpa gait; ID 19/20 tidak diberi perintah posisi. Jendela ukur 60 detik adalah 12:47:50,865–12:48:50,865 UTC setelah 30 frame warm-up; jeda dari run sebelumnya melebihi 120 detik.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 825 / 0 |
| Latensi callback rata-rata / P95 | 63,08 / 161,77 ms |
| FPS efektif | 13,75 frame/detik |
| CPU proses rata-rata | 1302,47% dari satu CPU logis |
| RAM RSS rata-rata | 357,76 MiB |
| Simpangan maksimum kepala | 0 rad pada sampel |
| Simpangan maksimum badan | 0,001535 rad |

Cakupan keluaran: bola 825/825 frame (100%), gawang 816/825 (98,9%), robot 825/825 (100%). Ini bukan metrik akurasi/precision berlabel. Lima sampel telemetri dan [waktu pengambilannya](sampling_times.json) tersimpan. Pemeriksaan otomatis CSV/telemetri lulus; audit akhir kontinuitas preview dan kondisi fisik tetap diperlukan.

Bukti: [overlay sebelum run](preview_sebelum_run.png), [overlay setelah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), dan [grafik kelas](grafik_keluaran_kelas_id.png). Log mentah lokal: `runs/op3_pytorch/20261102_eq_hybrid1337_idle_u2.*`.
