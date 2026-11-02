# Teacher, berjalan ulangan 2 pada set uji ulang

Run mentah `20261102_eq_teacher_walk_retest_u2` direkam 2 November 2026 dengan teacher FP32, kamera OP3 640×480, BoT-SORT, dan preview SSH-X. Ack gait mulai 12:04:09,891 UTC dan stop 12:05:12,899 UTC. Jendela ukur 60 detik berada pada `[t_g + 2 s, t_g + 62 s]`.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 585 / 0 |
| Latensi callback rata-rata / P95 | 96,75 / 181,19 ms |
| FPS efektif | 9,75 frame/detik |
| CPU proses rata-rata | 1332,64% dari satu CPU logis |
| RAM RSS rata-rata | 367,92 MiB |
| Simpangan maksimum kepala | 0,001534 rad (sekitar 1 count) |
| Perubahan maksimum sendi badan | 0,276251 rad |

Bola dan robot masing-masing terdeteksi pada 585/585 frame (100%); gawang pada 541/585 frame (92,5%). Ini **cakupan keluaran**, bukan akurasi/precision berlabel. Median confidence dan jumlah ID tracker ada di [tabel deteksi](tabel_deteksi.csv). Pengawas gait, dua sampel sendi tengah, serta dua sampel setelah stop menunjukkan gerak kaki dan kestabilan kepala dalam batas cek otomatis. Suhu CPU paket awal 81 °C; pembacaan 50 °C pada 12:11:36 UTC disimpan sebagai `suhu_diagnostik_terlambat_utc.txt`, **bukan** suhu akhir run.

Bukti: [gambar saat gait](frame_deteksi_saat_gait.png), [gambar setelah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan metrik](summary_metrics.json), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik keluaran kelas](grafik_keluaran_kelas_id.png), `gait_guard.json`, dan `head_guard_samples.csv`. Log mentah lokal: `runs/op3_pytorch/20261102_eq_teacher_walk_retest_u2.*`. Audit akhir kontinuitas preview dan kondisi fisik masih diperlukan.
