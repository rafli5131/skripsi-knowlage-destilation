# Percobaan 30: uji live setara empat model OP3

Status 2 November 2026: **9 dari 24 slot** pada rencana empat model × idle/berjalan × tiga ulangan telah diukur. Teacher idle, teacher berjalan, dan KD Hybrid full seed 1337 idle masing-masing selesai tiga ulangan; 15 slot model/kondisi lain belum diukur. Sesi ini memakai kamera OP3 640×480, tracking BoT-SORT, dan preview SSH-X aktif. Tidak ada pengukuran akurasi berlabel pada run live ini.

Atas permintaan Bhre, set teacher berjalan aktif disusun ulang: ulangan 1 memakai run mentah ulangan 3 sebelumnya, lalu ulangan 2 dan 3 direkam ulang. [Pemetaan sumber raw](active_run_sources.json) menjaga ID dan cap waktu asli. [Arsip set sebelumnya](01-teacher/arsip-set-sebelumnya-20261102-1200/) menyimpan artefak lama. Tidak ada log mentah yang ditimpa atau dipalsukan.

| Pasangan model/kondisi | Ulangan selesai | Tersisa |
|---|---:|---:|
| Teacher idle | 3 | 0 |
| Teacher berjalan | 3 | 0 |
| KD Hybrid idle | 3 | 0 |
| Lima pasangan lainnya | 0 | 15 |

Lihat [ringkasan teacher](01-teacher/README_ID.md), [jadwal 24 run](jadwal_run.csv), [tabel 24 slot](05-ringkasan/tabel_24_run.csv), [grafik matriks 2880×1800](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), [grafik teacher berjalan tiga ulangan](01-teacher/grafik_teacher_walk_ulangan_1_2_3_hd.png), dan [catatan akurasi/precision](05-ringkasan/CATATAN_AKURASI_PRECISION_ID.md). Warna biru pada grafik matriks berarti lulus pemeriksaan otomatis CSV/telemetri; tanda × berarti belum diukur. Status protokol akhir masih memerlukan audit kontinuitas preview, suhu, dan kondisi fisik. Ketiga gait aktif telah menerima ack stop; pada akhir uji idle, preview KD Hybrid pemantauan dinyalakan kembali. Periksa status proses saat melanjutkan sesi.

[Ringkasan KD Hybrid idle](02-kd-hybrid/README_ID.md) memuat tabel tiga ulangan, grafik HD, dan bukti gambar per run. Preview terakhir yang diverifikasi setelah uji idle memakai **KD Hybrid**.

[Peta rumusan masalah](PETA_RUMUSAN_MASALAH.md) menunjukkan hasil TEST berlabel yang sudah menjawab mAP, precision, recall, dan F1 skripsi, serta pekerjaan tersisa untuk benchmark runtime dan evaluasi kamera OP3.

[Log progres berurutan](log_progres.md) mencatat sembilan jendela ukur dan raw ID. [Memory sesi 2 November](../../../memory/2026-11-02-uji-live-setara-op3-9-dari-24.md) merangkum hasil, batas klaim, serta 15 slot berikutnya.
