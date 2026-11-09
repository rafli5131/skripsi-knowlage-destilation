> **Bahan kerja, belum naskah final.** Sesuaikan susunan dan penomoran dengan pedoman kampus serta hasil bimbingan.

# Draf bahan Bab IV–V: hasil utama, T38 dan T42

**Status draf:** sumber dan angka sudah ditautkan; penomoran, judul final, sitasi, dan persetujuan pembimbing masih perlu dilengkapi. Hasil audit teacher T42 telah tersedia. Naskah ini tidak menimpa draf sebelumnya.

## BAB IV — Hasil dan pembahasan

### 4.1 Implementasi sistem

Sistem deteksi objek berbasis ROS 2 pada ROBOTIS OP3 menerima citra kamera dan menjalankan model deteksi untuk kelas bola, gawang, dan robot. Model pembanding terdiri atas teacher YOLO11n dan student YOLO11 skala t kustom dengan 810.649 parameter; student dilatih secara supervised, KD murni, dan KD Hybrid full. KD murni teacher-only berbeda dari Hybrid full, yang menggabungkan loss deteksi berlabel dengan distilasi fitur, kotak dan kelas. Implementasi, pengaturan perangkat, dan bukti uji perlu dijelaskan dengan merujuk [dokumentasi runtime](../../OP3_PYTORCH_RUNTIME.md) dan [audit uji robot](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md). Pengujian ini menilai keluaran deteksi dan kinerja runtime sesuai tujuan penelitian.

### 4.2 Hasil akurasi pada TEST

Split TEST resmi terdiri atas 592 gambar. Nilai student berikut adalah rerata tiga seed dan teacher satu checkpoint; standar deviasi dan rincian tersedia pada [T05](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md). Precision dan recall dihitung pada confidence >0,25 dan IoU pencocokan 0,50; F1 pada tabel ini adalah harmonic mean dari precision dan recall makro, sedangkan AP memakai confidence floor 0,001 dan NMS IoU 0,7.

| Model | mAP50 | mAP50–95 | Precision | Recall | F1 dari P/R makro |
|---|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0,9642 | 0,7800 | 0,8915 | 0,9697 | 0,9290 |
| Supervised | 0,9601 | 0,7225 | 0,8609 | 0,9699 | 0,9121 |
| KD murni | 0,9446 | 0,6630 | 0,7547 | 0,9631 | 0,8462 |
| KD Hybrid full | 0,9583 | 0,7469 | 0,8519 | 0,9698 | 0,9071 |

Pada TEST, Hybrid memperoleh rerata mAP50–95 lebih tinggi daripada supervised sebesar 0,0244, sementara F1-nya lebih rendah sebesar 0,0050. Hasil tiga seed bersifat eksploratif; teacher hanya satu checkpoint. TEST sudah digunakan dalam tahap eksperimen sebelumnya dan bukan holdout yang belum pernah disentuh. Asal data dan resep training teacher utama belum seluruhnya terverifikasi; evaluasi ini tidak serta-merta menunjukkan performa kamera OP3.

### 4.3 Evaluasi retrospektif frame kamera OP3

[T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) membandingkan empat checkpoint pada 260 frame yang sama: 200 berobjek dan 60 negatif, dengan 400 kotak acuan yang ditinjau manusia. Sebanyak 50 frame gawang parsial dianalisis terpisah. AP menggunakan confidence floor 0,001 dan NMS IoU 0,7. Precision, recall dan F1 dihitung pada confidence >0,25 dan pencocokan IoU ≥0,5; **F1 makro pada T38 adalah rata-rata F1 per kelas**, berbeda dari definisi pada tabel TEST di atas.

| Checkpoint | mAP50 | mAP50–95 | F1 makro per kelas | Frame negatif dengan false positive |
|---|---:|---:|---:|---:|
| Teacher YOLO11n | 0,7058 | 0,5004 | 0,6829 | 2/60 |
| KD Hybrid seed 1337 | 0,7526 | 0,4885 | 0,5121 | 21/60 |
| Supervised seed 1337 | 0,7045 | 0,4414 | 0,6054 | 0/60 |
| KD murni seed 42 | 0,6301 | 0,4218 | 0,5008 | 0/60 |

Teacher memiliki mAP50–95 dan F1 makro tertinggi pada set ini, sedangkan Hybrid memiliki mAP50 tertinggi. Pada confidence operasi yang disebutkan, Hybrid mencocokkan 2/80 kotak gawang dan supervised 21/80; AP dan recall pada satu ambang mengukur hal yang berbeda. Label awal dibantu KD murni sebelum ditinjau, frame berasal dari satu rangkaian termasuk sesi objek bergerak, dan evaluasi dilakukan retrospektif; karena itu generalisasi ke adegan lain tidak terbukti. Model dan threshold tidak dipilih ulang berdasarkan T38. Grafik: [Indonesia](../../dokumentasi/2026-11-05/percobaan-37-evaluasi-t38-empat-model/grafik_t38_empat_model_id_hd.png) · [English](../../dokumentasi/2026-11-05/percobaan-37-evaluasi-t38-empat-model/grafik_t38_empat_model_en_hd.png).

### 4.4 Runtime OP3 saat idle dan berjalan

Empat checkpoint diuji pada dua kondisi, masing-masing tiga ulangan, sehingga terdapat 24 run aktif. Pemeriksaan log dan sampel telemetry yang tersedia lulus untuk 24 run. Rata-rata ± SD berikut adalah agregasi tiga rerata run; FPS berasal dari timestamp kamera valid dan tidak diperoleh dengan membalik latensi. Lihat [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), [T37](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md), serta [audit](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

| Model | Kondisi | Latensi (ms) | FPS | CPU proses (% satu CPU logis) | RSS proses (MiB) |
|---|---|---:|---:|---:|---:|
| Teacher | Idle | 96,24 ± 3,60 | 9,88 ± 0,31 | 1338,90 ± 9,65 | 370,58 ± 1,29 |
| Hybrid | Idle | 64,70 ± 1,92 | 13,60 ± 0,35 | 1305,97 ± 4,91 | 358,87 ± 1,24 |
| Teacher | Berjalan | 95,85 ± 1,27 | 9,87 ± 0,17 | 1333,54 ± 4,08 | 372,42 ± 5,11 |
| Hybrid | Berjalan | 71,47 ± 2,98 | 12,54 ± 0,38 | 1303,77 ± 3,88 | 356,31 ± 2,09 |

Hasil supervised dan KD murni tersedia dalam T37. CPU multithread dapat melampaui 100% satu CPU logis; RSS adalah penggunaan memori proses detektor, bukan total RAM robot. Hasil pengukuran dianalisis secara deskriptif. Urutan run dalam blok lintas dua hari, perubahan set teacher berjalan setelah melihat cakupan gawang, screenshot dan telemetry yang tidak lengkap, serta status torque sebagian run yang tidak dibaca langsung membatasi klaim kesetaraan kondisi fisik dan sebab-akibat. Lihat [grafik 24 run](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/grafik_runtime_24_run_id_hd.png).

### 4.5 Waktu training dan pengujian

[T35](../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) melaporkan durasi training sembilan run student, durasi sesi TEST multi-model, dan benchmark inferensi server. Durasi sesi TEST mencakup beberapa checkpoint dan overhead; tidak dapat diperlakukan sebagai durasi per model. Waktu teacher utama dengan provenance setara belum tersedia. Perbedaan beban server dan skrip membatasi perbandingan biaya training atau latensi antarperiode; benchmark L40 tidak disamakan dengan runtime OP3.

### 4.6 Ablasi kapasitas teacher di VAL

[T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md) memakai dua teacher yang dilatih ulang serta enam student Hybrid full pada tiga seed berpasangan, dievaluasi pada 1.213 gambar VAL. Teacher YOLO11n dan YOLO11s mencapai mAP50–95 0,7760 dan 0,7843. Student terkait mencapai 0,7482 ± 0,0003 dan 0,7473 ± 0,0003; selisih berpasangan s − n adalah −0,0009 ± 0,0006. Pada percobaan ini teacher s yang lebih tinggi akurasinya tidak menghasilkan rerata mAP student lebih tinggi. Satu checkpoint teacher per ukuran dan tiga seed student tidak mendukung klaim signifikansi kuat. Kontrol supervised berasal dari eksperimen VAL sebelumnya. Data ini bukan hasil TEST atau kamera OP3 dan tidak mengganti checkpoint penelitian utama.

Status audit: manifest student dan JSON tersedia serta hash yang dicatat konsisten. Keluaran [audit server](../../dokumentasi/2026-11-09/AUDIT_TEACHER_T42_SERVER.md) menunjukkan semua cek manifest dan checkpoint teacher lulus; berkas privat tidak diperiksa ulang langsung dari robot dan seluruh byte dataset tidak dihitung ulang. F1 T42 dihitung dari precision dan recall makro, berbeda dari rata-rata F1 per kelas pada T38. Memori puncak teacher dan student dicatat dengan metode berbeda sehingga tidak dibandingkan tanpa kualifikasi.

## BAB V — Kesimpulan dan saran

1. Sistem ROS 2 untuk deteksi tiga kelas pada OP3 telah diimplementasikan dan didokumentasikan; bukti uji live dan audit runtime tersedia dengan keterbatasan pencatatan yang dijelaskan pada Bab IV.
2. Pada TEST yang telah digunakan sebelumnya, teacher memperoleh mAP50–95 0,7800; rerata Hybrid, supervised, dan KD murni masing-masing 0,7469, 0,7225, dan 0,6630. Hasil kamera retrospektif disajikan terpisah dan tidak membuktikan generalisasi lintas adegan.
3. Precision, recall dan F1 tersedia pada tabel TEST dan T38. Pada TEST, F1 Hybrid sedikit lebih rendah daripada supervised meskipun mAP50–95 lebih tinggi. Definisi agregasi F1 perlu disebutkan untuk setiap tabel.
4. Pada pengukuran deskriptif OP3, rerata latensi/FPS teacher dan Hybrid masing-masing 96,24 ms/9,88 FPS dan 64,70 ms/13,60 FPS saat idle; saat berjalan 95,85 ms/9,87 FPS dan 71,47 ms/12,54 FPS. Temuan ini tidak membuktikan penyebab perbedaannya.
5. CPU proses dan RSS telah dicatat pada kedua kondisi dalam T37. Data tersebut menggambarkan proses detektor dan bukan keseluruhan penggunaan sistem robot.

Saran meliputi verifikasi arsip teacher, evaluasi independen lintas adegan jika diperlukan, serta pengukuran runtime yang lebih terkendali apabila pembimbing memerlukan klaim kausal. Penulisan final mengikuti pedoman kampus dan persetujuan pembimbing.

## Lampiran yang perlu disiapkan

- Gambar implementasi dan contoh deteksi: [contoh screenshot live supervised](../../dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/supervised_berjalan_u1_sesudah.png) (frame setelah jendela pengukuran berjalan), serta identitas model dan waktu pengambilan dari manifest terkait.
- Tabel TEST T05/T30, tabel runtime T36/T37, tabel kamera T38, tabel ablasi T42, dan grafik HD yang terkait. Gunakan penomoran naskah final.
- [Matriks bukti dan celah](../../dokumentasi/2026-11-09/MATRIKS_BUKTI_DAN_CELAH.md), riwayat run pengganti, definisi metrik dan audit provenance; jangan menuliskan nilai yang tidak terdokumentasi.
