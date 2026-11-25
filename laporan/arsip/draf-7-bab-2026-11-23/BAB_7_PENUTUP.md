# BAB 7 PENUTUP

## 7.1 Kesimpulan

1. Sistem deteksi tiga kelas berbasis ROS 2 telah diimplementasikan pada OP3 dan menghasilkan deteksi, preview, serta log runtime. Uji kotak hitam retrospektif menyatakan KF-01, KF-02, KF-04, dan KNF-01 lulus pada 24 run, KF-03 lulus dengan catatan pada satu sesi bola bergerak, dan KF-05 lulus untuk contoh preview yang tersedia. Kelancaran preview sepanjang setiap run tidak direkam lengkap.
2. Pada 592 gambar TEST, mAP50–95 teacher adalah 0,7800; rerata Hybrid full, supervised, dan KD murni masing-masing 0,7469, 0,7225, dan 0,6630. TEST telah digunakan sebelumnya dan temuan dibatasi konteks split tersebut.
3. Precision, recall, dan F1 tiap model telah dihitung. F1 Hybrid pada TEST sedikit lebih rendah daripada supervised meskipun mAP50–95-nya lebih tinggi. Pada T38, F1 utama dan rerata F1 per kelas harus dibedakan karena agregasinya berbeda.
4. Dalam pengukuran OP3 deskriptif, latensi/FPS teacher dan Hybrid adalah 96,24 ms/9,88 FPS dan 64,70 ms/13,60 FPS saat diam; saat berjalan masing-masing 95,85 ms/9,87 FPS dan 71,47 ms/12,54 FPS.
5. CPU proses dan RSS tersedia pada kedua kondisi. CPU berada pada kisaran sekitar 1.300% satu CPU logis (81 sampai 84% dari 16 CPU logis) untuk keempat model, sehingga persentase CPU tidak membedakan model. Uji ulang offline menunjukkan bahwa angka ini banyak dipengaruhi thread pustaka aljabar linear selama pelacakan, meskipun penyebab pada run historis belum terbukti; RSS merupakan memori proses detektor. Nilai ini tidak mengukur total konsumsi sistem robot.

## 7.2 Saran

Pemeriksaan lanjutan dapat menggunakan anotasi independen pada adegan dan sesi baru, serta mengulang runtime dalam kondisi dan urutan yang lebih terkendali bila dibutuhkan klaim yang lebih kuat. Arsip checkpoint, konfigurasi, dan data mentah sebaiknya dicadangkan. Pembatasan thread OpenBLAS atau penonaktifan pelacakan pada mode deteksi statis dapat diuji untuk menurunkan beban CPU, karena uji ulang offline menunjukkan pengaruh besar kedua faktor tersebut. Pembahasan akhir perlu mempertahankan keterbatasan provenance teacher, split dataset, T38, dan uji runtime.
