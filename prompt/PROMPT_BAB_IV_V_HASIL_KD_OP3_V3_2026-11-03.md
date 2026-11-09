# Prompt penyusunan Bab IV–V skripsi KD dan ROBOTIS OP3 — V3

Gunakan prompt ini untuk menyusun draf baru Bab IV dan V berdasarkan progres per 3 November 2026. V3 memperbarui status pada prompt V2: **24 slot runtime OP3 sudah diukur**, T36/T37 sudah disusun, dan peneliti menerima hasil untuk analisis deskriptif dengan keterbatasan. Persetujuan pembimbing belum dicatat. Jangan menjalankan robot, kamera, training, atau pengujian ulang hanya untuk menulis laporan.

## Instruksi siap pakai

Bertindak sebagai penulis ilmiah teknik komputer. Tulis draf **Bab IV Hasil dan Pembahasan** serta **Bab V Kesimpulan dan Saran** skripsi implementasi deteksi objek YOLO11 skala t berbasis *Knowledge Distillation* (KD) pada ROBOTIS OP3 menggunakan ROS 2. Gunakan bahasa Indonesia akademis yang jelas, istilah Knowledge Distillation, serta rumusan masalah dan judul terbaru yang dapat diverifikasi pada dokumen pengguna. Jangan mengarang sitasi, angka, konfigurasi, hasil, persetujuan, atau kondisi eksperimen. Tandai informasi yang belum tersedia dengan `[BUTUH SUMBER: ...]` atau `[PERLU KONFIRMASI: ...]`.

## Sumber yang wajib diperiksa

1. `dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md`, `KEPUTUSAN_PENGGUNA.md`, `DRAF_PEMBAHASAN.md`, dan `audit_telemetry.csv`.
2. `analisis_performa/tabel/T36_runtime_live_setara_per_run.{md,csv}` dan `T37_runtime_live_setara_ringkasan.{md,csv}`; grafik `grafik_runtime_24_run_id_hd.png` dan `grafik_runtime_24_run_en_hd.png` di folder audit. Gunakan run aktif pada tabel dan jelaskan run yang diganti sesuai lampiran audit.
3. `analisis_performa/tabel/T05_akurasi_test_keseluruhan.md`, `T30_kd_hybrid_test_berpasangan.md`, `T34_akurasi_op3_hybrid_supervised_seed1337.md`, `T35_waktu_training_dan_pengujian.md`, `T38_akurasi_op3_empat_model_260.md`, dan `T42_ablasi_teacher_yolo11s_val.md`; ringkasan `TABEL_AKURASI_TEST.md`, dokumentasi T38, `audit_teacher_t42_LTOW7Xw5.json` dan indeks visualisasi 9 November.
4. `OP3_PYTORCH_RUNTIME.md`, `configs/model_registry.yaml`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `AUDIT_DATASET_SKRIPSI.md`, `DRAF_PROPOSAL_BAB_I-III.md`, serta draf Bab IV–V yang sudah ada. Artefak mentah kamera dan log robot dapat hanya tersedia di mesin OP3; bila tidak ada, pakai tabel ringkasan yang tersedia dan nyatakan batas verifikasinya.

## Isi dan batas penelitian

- Jelaskan implementasi ROS 2, alur kamera, inferensi, deteksi/tracking, dan perangkat OP3 berdasarkan bukti. Student YOLO11 t adalah arsitektur kustom, bukan YOLO11n standar. KD murni dan KD Hybrid full adalah dua objective yang berbeda; Hybrid memakai loss berlabel dan distilasi.
- Jawab rumusan masalah tentang mAP, precision, recall, F1 pada TEST resmi, dan runtime OP3 (latensi, FPS, CPU, RAM) pada kondisi idle dan berjalan. Pisahkan hasil TEST dari pengamatan kamera OP3 dan runtime live. Jangan sebut jumlah frame dengan kotak prediksi sebagai akurasi.
- Semua **24 slot aktif** lulus pemeriksaan otomatis CSV/telemetry, dengan tiga ulangan untuk setiap pasangan empat model dan dua kondisi. Pengguna menerima hasil sebagai **analisis deskriptif** dengan keterbatasan; jangan tulis bahwa kondisi fisik setara telah dibuktikan atau pembimbing sudah menyetujui.
- Jelaskan bahwa urutan run berbentuk blok lintas dua hari, bukan rotasi; set teacher berjalan dipilih ulang setelah melihat cakupan gawang; dua screenshot teacher idle yang sesuai waktu protokol tidak tersedia; baseline Hybrid berjalan u1 hanya enam sendi; sebagian torque, jarak, pencahayaan, suhu dan kontinuitas preview tidak terukur lengkap. Laporkan run pengganti dan sumbernya tanpa menghapus sejarah. Jangan menarik kesimpulan kausal atau signifikansi dari tiga ulangan.
- Nyatakan latency sebagai rata-rata dan FPS efektif sesuai T36/T37; CPU adalah persen terhadap satu CPU logis dan juga dapat dinormalisasi ke kapasitas 16 CPU logis, RAM adalah RSS. Jangan menghitung FPS sebagai 1000/latensi. Waktu training, durasi sesi TEST, dan latency per frame memiliki cakupan berbeda; jangan campurkan.
- TEST resmi telah digunakan pada tahap sebelumnya, bukan holdout yang belum pernah disentuh. Rata-rata tiga seed bersifat eksploratif; teacher satu checkpoint dan provenance data training teacher belum lengkap. Hybrid TEST mAP50–95 lebih tinggi dari supervised, tetapi F1 sedikit lebih rendah; rujuk sumber dan jangan melebih-lebihkan.
- T34 adalah evaluasi eksploratif Hybrid versus Supervised pada 260 frame OP3 yang telah ditinjau Bhre dengan bantuan pra-label. T38 empat model pada frame dan label yang sama **selesai pada 5 November 2026**; hasil Hybrid dan supervised identik dengan T34. Lima puluh frame gawang parsial dipisahkan; label bukan anotasi independen penuh. T38 bersifat retrospektif, bukan pengujian eksternal lintas adegan. Bedakan definisi F1 makro T34/T38 dari tabel TEST.
- T42 server2 selesai: dua teacher yang dilatih ulang dan enam student dibandingkan pada VAL; audit teacher yang dijalankan di server dilaporkan lulus. Ablasi ini tidak mengganti checkpoint OP3 dan tidak boleh disajikan sebagai hasil TEST atau kamera OP3. F1 T42 adalah F1 dari precision/recall makro, berbeda dari rata-rata F1 per kelas pada T38.

## Keluaran dan pemeriksaan akhir

Simpan draf baru yang tidak menimpa naskah pengguna kecuali diminta. Bab IV mencakup pengaturan, hasil TEST, waktu training/pengujian, implementasi OP3, T36/T37, grafik dan pembahasan keterbatasan. Bab V menjawab rumusan masalah sesuai bukti serta memberi saran. Sertakan daftar tabel/gambar dengan sumber dan daftar hal yang masih memerlukan arahan pembimbing. Periksa ulang setiap angka terhadap CSV/manifest, satuan sumbu, penomoran, tautan, dan batas klaim; sertakan daftar ketidakpastian yang tidak dapat dipastikan dari sumber.
