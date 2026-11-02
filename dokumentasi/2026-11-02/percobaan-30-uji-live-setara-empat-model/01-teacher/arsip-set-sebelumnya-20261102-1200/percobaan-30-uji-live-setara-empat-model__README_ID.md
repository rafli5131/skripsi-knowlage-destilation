# Percobaan 30: uji live setara empat model OP3

Status 2 November 2026: tiga ulangan teacher idle dan tiga ulangan teacher berjalan telah direkam; 18 slot lain dalam matriks 24 run belum diukur. U2 idle pertama diganti atas permintaan Bhre setelah gawang sering tidak terdeteksi. Ini adalah sesi runtime dengan preview SSH-X dan tracking BoT-SORT aktif; belum ada pengukuran akurasi berlabel.

Prasyarat yang sudah diperiksa: teacher SHA-256 cocok registry, kamera 640×480, `op3_manager` aktif dengan `auto_start_init_pose=false`, dan ID 19/20 menahan posisi awal. Saat manager perlu inisialisasi EEPROM, operator menopang badan dan kepala selama torque dimatikan sementara; setelah startup posisi kepala cocok dengan posisi awal. Bukti persiapan ada di [folder persiapan](00-persiapan/) dan [catatan aktivasi servo](../persiapan-uji-live-setara/README.md).

| Model/kondisi | Ulangan selesai | Ulangan tersisa |
| --- | ---: | ---: |
| Teacher idle | 3 | 0 |
| Teacher berjalan | 3 | 0 |
| Enam pasangan model/kondisi lain | 0 | 18 |

Lihat [ringkasan teacher](01-teacher/README_ID.md), [tabel 24 slot](05-ringkasan/tabel_24_run.csv), [grafik 24 run beresolusi 2880×1800](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), dan [log penyimpangan](log_penyimpangan.md). Warna biru berarti lulus pemeriksaan otomatis CSV dan sampel telemetry; tanda × berarti belum diukur. Status protokol akhir masih memerlukan audit kontinuitas preview, suhu, dan catatan kondisi fisik. Ketiga gait menerima ack stop; preview teacher pemantauan tetap menyala setelah pengujian.
