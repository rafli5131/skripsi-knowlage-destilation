# Percobaan 30: uji live setara empat model OP3

> Status terbaru: [pengganti KD murni berjalan ulangan 3](../../2026-11-03/percobaan-35-kd-murni-berjalan-3-ulangan/04-kd-murni/walk-u3-ulang1/README_ID.md) lulus cek otomatis; 24/24 slot aktif lulus cek otomatis. Audit protokol akhir masih terbuka; status di bawah adalah snapshot sebelumnya.

> Status terbaru: [KD murni berjalan tiga ulangan](../../2026-11-03/percobaan-35-kd-murni-berjalan-3-ulangan/README_ID.md) selesai; 24/24 slot terukur, 23 lulus cek otomatis dan satu perlu audit. Status sebelumnya di bawah merupakan snapshot historis.

> Status terbaru: [KD murni idle tiga ulangan](../../2026-11-03/percobaan-34-kd-murni-idle-3-ulangan/README_ID.md) selesai; kampanye 21/24 slot. Status sebelumnya di bawah adalah snapshot historis.

> Status terbaru: [tiga ulangan Supervised berjalan](../../2026-11-03/percobaan-33-supervised-berjalan-3-ulangan/README_ID.md) selesai. Matriks kini 18/24 slot; enam slot KD murni tersisa. Snapshot lama ada di bawah.

> Pembaruan terakhir: [Supervised berjalan ulangan 1](../../2026-11-03/percobaan-33-supervised-berjalan-3-ulangan/README_ID.md) selesai; matriks saat ini 16/24 slot. Status 15/24 dan 12/24 di bawah adalah snapshot sebelumnya.

> Pembaruan terbaru: [Supervised idle percobaan 32](../../2026-11-03/percobaan-32-supervised-idle-3-ulangan/README_ID.md) menambah tiga run; kampanye kini 15/24 slot, sembilan tersisa. Ringkasan 12/24 di bawah adalah snapshot sebelum percobaan 32.

Status kampanye per **3 November 2026: 12 dari 24 slot** pada rencana empat model × idle/berjalan × tiga ulangan telah diukur. Teacher idle/berjalan dan KD Hybrid full seed 1337 idle selesai pada 2 November; [KD Hybrid berjalan tiga ulangan](../../2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/README_ID.md) selesai pada 3 November. **12 slot Supervised dan KD murni** belum diukur. Semua run memakai kamera OP3 640×480, BoT-SORT, dan preview SSH-X aktif. Tidak ada pengukuran akurasi berlabel pada run live ini.

Atas permintaan Bhre, set teacher berjalan aktif disusun ulang: ulangan 1 memakai run mentah ulangan 3 sebelumnya, lalu ulangan 2 dan 3 direkam ulang. [Pemetaan sumber raw](active_run_sources.json) menjaga ID dan cap waktu asli. [Arsip set sebelumnya](01-teacher/arsip-set-sebelumnya-20261102-1200/) menyimpan artefak lama. Tidak ada log mentah yang ditimpa atau dipalsukan.

| Pasangan model/kondisi | Ulangan selesai | Tersisa |
|---|---:|---:|
| Teacher idle | 3 | 0 |
| Teacher berjalan | 3 | 0 |
| KD Hybrid idle | 3 | 0 |
| KD Hybrid berjalan, 3 November | 3 | 0 |
| Empat pasangan Supervised/KD murni | 0 | 12 |

Lihat [ringkasan teacher](01-teacher/README_ID.md), [jadwal 24 run](jadwal_run.csv), [tabel 24 slot](05-ringkasan/tabel_24_run.csv), [grafik matriks 2880×1800](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), [grafik teacher berjalan tiga ulangan](01-teacher/grafik_teacher_walk_ulangan_1_2_3_hd.png), dan [catatan akurasi/precision](05-ringkasan/CATATAN_AKURASI_PRECISION_ID.md). Warna biru pada grafik matriks berarti lulus pemeriksaan otomatis CSV/telemetri; tanda × berarti belum diukur. Status protokol akhir masih memerlukan audit kontinuitas preview, suhu, dan kondisi fisik. Ketiga gait aktif telah menerima ack stop; pada akhir uji idle, preview KD Hybrid pemantauan dinyalakan kembali. Periksa status proses saat melanjutkan sesi.

[Ringkasan KD Hybrid idle](02-kd-hybrid/README_ID.md) dan [ringkasan KD Hybrid berjalan 3 November](../../2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/README_ID.md) memuat tabel tiga ulangan, grafik HD, dan bukti gambar per run. Preview terakhir yang diverifikasi setelah uji berjalan memakai **KD Hybrid**.

[Peta rumusan masalah](PETA_RUMUSAN_MASALAH.md) menunjukkan hasil TEST berlabel yang sudah menjawab mAP, precision, recall, dan F1 skripsi, serta pekerjaan tersisa untuk benchmark runtime dan evaluasi kamera OP3.

[Log progres 2 November](log_progres.md) mencatat sembilan jendela ukur awal dan raw ID; [log 3 November](../../2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/log_penyimpangan.md) mencatat tiga ulangan berjalan berikutnya. [Memory 2 November](../../../memory/2026-11-02-uji-live-setara-op3-9-dari-24.md) adalah snapshot historis 9/24; [memory 3 November](../../../memory/2026-11-03-kd-hybrid-berjalan-12-dari-24.md) memuat status 12/24.
