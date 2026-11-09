# Log progres skripsi — 9 November 2026

## Hasil dan bukti yang tersedia

- **Akurasi TEST:** [T05](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md) merangkum teacher, supervised, KD murni dan KD Hybrid. TEST telah dipakai sebelumnya.
- **Evaluasi kamera:** [T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) membandingkan empat checkpoint pada 260 frame yang sama; 50 frame gawang parsial dianalisis terpisah. Ini evaluasi retrospektif satu rangkaian, termasuk frame sesi objek bergerak.
- **Runtime OP3:** [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), [T37](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md), dan [audit](../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md) mencakup 24 run aktif: empat model, dua kondisi dan tiga ulangan. Interpretasi mengikuti batas bukti dalam audit.
- **Biaya eksperimen dan ablasi:** [T35](../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) menjelaskan durasi yang tersedia; [T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md) melaporkan dua teacher dan enam student pada VAL. [Audit teacher di server](AUDIT_TEACHER_T42_SERVER.md) mencatat cek yang lulus serta batas verifikasinya.
- **Materi visual:** [dokumentasi per model](../model/README.md) menyediakan confusion matrix per model dan gabungan; [visualisasi tambahan](visualisasi-tambahan-empat-model/README.md) memuat grafik, contoh screenshot empat model dan cuplikan video Supervised 10 detik. Lokasi file video berada pada folder media tersebut dan ditautkan dari halaman model.

## Penataan draf laporan

Dibuat [folder khusus draf Bab IV–V](../../laporan/draf-bab-iv-v/README.md), berisi draf terpadu T38/T42 serta salinan arsip draf terdahulu. Draf lama di root tetap disimpan dan diberi penanda historis. README utama, indeks dokumentasi, inventaris prompt, dan memory diperbarui agar rujukannya mudah ditemukan. Data percobaan dan naskah sumber terpadu lokal tidak dihapus.

Draf perlu disesuaikan dengan pedoman kampus, penomoran final, sumber primer dan hasil konsultasi pembimbing. [Matriks bukti dan celah](MATRIKS_BUKTI_DAN_CELAH.md) memisahkan bukti yang tersedia dari keterbatasannya. Tidak ada pengukuran baru, pelatihan, aktivasi kamera, atau gerakan robot dalam pekerjaan penataan dokumentasi ini.
