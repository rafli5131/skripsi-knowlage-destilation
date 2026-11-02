# Teacher, berjalan ulangan 3 pada set uji ulang

Run mentah `20261102_eq_teacher_walk_retest_u3` direkam 2 November 2026 dengan teacher FP32, kamera OP3 640×480, BoT-SORT, dan preview SSH-X. Ack gait mulai 12:10:04,931 UTC dan stop 12:11:07,939 UTC. Jendela ukur 60 detik berada pada `[t_g + 2 s, t_g + 62 s]`.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 604 / 0 |
| Latensi callback rata-rata / P95 | 94,40 / 180,01 ms |
| FPS efektif | 10,07 frame/detik |
| CPU proses rata-rata | 1337,99% dari satu CPU logis |
| RAM RSS rata-rata | 377,97 MiB |
| Simpangan maksimum kepala | 0,001534 rad (sekitar 1 count) |
| Perubahan maksimum sendi badan | 0,490874 rad |

Bola dan robot masing-masing terdeteksi pada 604/604 frame (100%); gawang pada 574/604 frame (95,0%). Ini **cakupan keluaran**, bukan akurasi/precision berlabel. Median confidence dan jumlah ID tracker ada di [tabel deteksi](tabel_deteksi.csv). Pengawas gait, dua sampel sendi tengah, serta dua sampel setelah stop menunjukkan gerak kaki dan kestabilan kepala dalam batas cek otomatis. Suhu CPU paket 81 °C sebelum run dan 51 °C pada pembacaan setelah detektor berhenti sekitar 19 detik; pembacaan itu bukan suhu pada detik terakhir gait.

Bukti: [gambar saat gait](frame_deteksi_saat_gait.png), [gambar setelah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik keluaran kelas](grafik_keluaran_kelas_id.png), `gait_guard.json`, dan `head_guard_samples.csv`. Log mentah lokal: `runs/op3_pytorch/20261102_eq_teacher_walk_retest_u3.*`. Audit akhir kontinuitas preview dan kondisi fisik masih diperlukan.
