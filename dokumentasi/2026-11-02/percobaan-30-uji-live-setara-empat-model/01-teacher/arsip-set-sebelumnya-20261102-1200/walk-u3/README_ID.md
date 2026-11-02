# Teacher, berjalan ulangan 3

Run `20261102_eq_teacher_walk_u3` direkam 2 November 2026 memakai teacher FP32, kamera 640×480, BoT-SORT, dan preview SSH-X. Ack gait mulai 11:49:36,483 UTC; stop diterima 11:50:39,490 UTC. Jendela ukur `[t_g + 2 s, t_g + 62 s]` penuh 60 detik.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 589 / 0 |
| Latensi callback rata-rata / P95 | 96,41 / 180,86 ms |
| FPS efektif | 9,80 frame/detik |
| CPU proses rata-rata | 1329,97% dari satu CPU logis |
| RAM RSS rata-rata | 371,36 MiB |
| Simpangan maksimum kepala | 0,001534 rad (sekitar 1 count) |
| Perubahan maksimum sendi badan | 0,377544 rad |

Cakupan keluaran deteksi: bola 589/589 frame (100%), gawang 561/589 (95,2%), robot 589/589 (100%). Ini **bukan akurasi berlabel**. Dua sampel tengah gait dan dua sesudah stop tersimpan; pengawas gait juga mencatat sendi kepala serta empat sendi kaki sekitar setiap detik. Pemeriksaan otomatis CSV dan stabilitas kaki setelah stop lulus. Suhu CPU paket tercatat 74 °C sebelum run dan 71 °C pada pengukuran setelah run; pengukuran akhir dilakukan sekitar 10 detik setelah detektor berhenti.

Bukti gambar: [saat gait](frame_deteksi_saat_gait.png) dan [sesudah jendela sebelum detektor selesai](frame_deteksi_sesudah_jendela.png). Data dan grafik: [ringkasan JSON](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel keluaran kelas](tabel_deteksi.csv), [grafik latensi ID](grafik_latensi_id.png), [grafik CPU/RAM ID](grafik_cpu_ram_id.png), [grafik kelas ID](grafik_keluaran_kelas_id.png), serta `gait_guard.json`, `head_guard_samples.csv`, dan `telemetry_*.txt`. Log mentah lokal: `runs/op3_pytorch/20261102_eq_teacher_walk_u3.*`. Kontinuitas preview dan kondisi fisik memerlukan audit akhir.
