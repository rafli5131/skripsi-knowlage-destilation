# BAB 1 — PENDAHULUAN

> Draf kerja 12 November 2026. Judul, format, sitasi dan substansi akhir perlu ditelaah sesuai pedoman program studi dan arahan pembimbing.

## 1.1 Latar belakang

Robot humanoid yang berinteraksi dengan lingkungan membutuhkan informasi lokasi dan kelas objek dari citra. Deteksi berbasis jaringan saraf dapat menghasilkan kelas dan kotak pembatas, tetapi biaya komputasinya perlu diperhatikan pada komputer onboard robot. Pengurangan ukuran model harus dievaluasi bersama mutu deteksi dan performa saat sistem dijalankan.

Penelitian ini membandingkan teacher YOLO11n dengan student YOLO11 skala t kustom yang memiliki 810.649 parameter. Student dilatih menggunakan metode supervised, knowledge distillation (KD) murni, dan KD Hybrid full. Hybrid full menggabungkan loss deteksi dari label dengan distilasi fitur, kotak, dan kelas; KD murni digunakan sebagai pembanding tambahan. Pemilihan kandidat Hybrid full seed 1337 untuk OP3 didasarkan pada VAL sebelum evaluasi TEST lanjutan.

Sistem diimplementasikan melalui ROS 2 pada ROBOTIS OP3 untuk mendeteksi bola, gawang, dan robot. Akurasi model diperiksa pada split TEST dan secara terpisah pada frame kamera OP3 yang telah ditinjau. Latensi, FPS, CPU dan RAM proses detektor diukur ketika robot diam dan berjalan. Hasil dari masing-masing konteks tidak dipertukarkan: akurasi membutuhkan label acuan, sementara frekuensi kotak pada preview hanya menunjukkan keluaran model.

## 1.2 Rumusan masalah

1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil KD pada ROBOTIS OP3?
2. Bagaimana mAP model hasil KD dibandingkan dengan model supervised berarsitektur sama dan teacher YOLO11n?
3. Bagaimana precision, recall, dan F1-score model tersebut?
4. Berapa rata-rata latensi dan FPS model KD dan teacher ketika robot diam dan berjalan?
5. Bagaimana penggunaan CPU dan RAM model KD dan teacher pada komputer onboard robot?

## 1.3 Tujuan dan manfaat

Penelitian bertujuan merancang dan menguji sistem deteksi ROS 2; membandingkan mAP, precision, recall dan F1; serta mengukur latensi, FPS dan penggunaan sumber daya proses detektor. Hasilnya menyediakan bukti empiris untuk menilai keseimbangan kualitas deteksi dan biaya penggunaan model pada OP3. Penelitian ini tidak mengklaim metode KD baru atau keunggulan kausal yang tidak didukung rancangan pengujian.

## 1.4 Batasan

Kelas yang digunakan adalah `ball`, `gawang`, dan `robot`. Objek target untuk lingkup deteksi skripsi ditempatkan statis, sedangkan robot diuji dalam kondisi diam dan berjalan. T38 merupakan evaluasi retrospektif pendukung yang juga memuat frame dari sesi objek bergerak; seluruh T38 tidak boleh disebut set khusus objek statis. Pelacakan objek dan kontrol servo kepala tidak menjadi tujuan wajib skripsi.

Dataset resmi menggunakan split gambar TRAIN, VAL dan TEST; kesamaan sumber/adegan antar-split belum dapat disingkirkan. TEST telah dipakai pada eksperimen sebelumnya. Provenance dataset teacher utama tidak lengkap. Pengujian runtime bersifat deskriptif dan dilakukan lintas hari. Ruang lingkup detail dan sumber rumusan masalah tersedia pada [konfirmasi rumusan](../../docs/KONFIRMASI_RUMUSAN_MASALAH_2026-10-22.md), [audit dataset](../../AUDIT_DATASET_SKRIPSI.md), dan [audit runtime](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

## 1.5 Sistematika

Bab 1 memuat pendahuluan; Bab 2 landasan kepustakaan; Bab 3 metodologi; Bab 4 rekayasa kebutuhan; Bab 5 perancangan dan implementasi; Bab 6 pengujian dan pembahasan; Bab 7 penutup.
