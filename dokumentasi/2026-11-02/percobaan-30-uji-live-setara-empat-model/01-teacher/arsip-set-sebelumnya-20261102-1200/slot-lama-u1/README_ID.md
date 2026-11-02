# Teacher, berjalan ulangan 1

Run `20261102_eq_teacher_walk_u1` direkam 2 November 2026 dengan model teacher FP32, kamera OP3 640×480, tracking BoT-SORT, dan preview SSH-X. Jendela ukur 60 detik dimulai dua detik setelah ack `Start walking` (11:34:11,772 UTC); perintah stop dikirim 63 detik setelah ack dan diterima pada 11:35:14,787 UTC.

| Parameter | Hasil |
|---|---:|
| Frame jendela ukur | 611 |
| Error frame | 0 |
| Latensi callback rata-rata | 90,88 ms |
| Latensi callback P95 | 181,31 ms |
| FPS efektif kamera | 10,19 frame/detik |
| CPU proses rata-rata | 1338,94% dari satu CPU logis |
| RAM proses RSS rata-rata | 375,68 MiB |
| Simpangan maksimum kepala | 0,001534 rad (sekitar 1 count) |
| Perubahan maksimum sendi badan | 0,389631 rad |

Cakupan keluaran pada jendela ukur: bola 611/611 frame (100%), gawang 112/611 (18,3%), robot 611/611 (100%). Angka ini adalah frekuensi keluaran model, **bukan akurasi** karena frame berjalan ini tidak diberi ground truth manusia. Gawang sering luput saat robot bergerak; penyebab visual perlu ditinjau dari adegan dan rekaman.

Log pengawas [head_guard_samples.csv](head_guard_samples.csv) memuat sampel tengah sekitar detik 20 dan 40, termasuk pan/tilt serta sendi pinggul/lutut. Dua sampel setelah gait berhenti ada di `telemetry_after.txt` dan `telemetry_after2.txt`; kaki stabil dalam dua sampel tersebut. [gait_guard.json](gait_guard.json) memuat ack dan batas kepala. [Ringkasan metrik](summary_metrics.json) lulus pemeriksaan otomatis berbasis CSV dan telemetri. Pemeriksaan akhir kontinuitas preview, suhu, dan kondisi fisik tetap perlu dicatat.

[Grafik runtime 2160×1800](grafik_runtime_hd.png) dan [grafik matriks 24 run 2880×1800](../../05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png) tersedia. [Preview setelah ulangan](preview_setelah_u1.png) diambil **setelah detektor ulangan ini berhenti** saat preview pemantauan dimulai lagi; screenshot sesudah jendela tetapi sebelum detektor selesai tidak tersimpan pada ulangan ini. Log mentah: `runs/op3_pytorch/20261102_eq_teacher_walk_u1.csv`, `.json`, dan `_detections.csv` (lokal).
