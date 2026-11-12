# BAB 7 — PENUTUP

## 7.1 Kesimpulan

1. Sistem deteksi tiga kelas berbasis ROS 2 telah diimplementasikan pada OP3 dan menghasilkan deteksi, preview, serta log runtime. Bukti fungsional yang tersedia dievaluasi secara retrospektif; beberapa rincian seperti kelancaran preview sepanjang setiap run tidak direkam lengkap.
2. Pada 592 gambar TEST, mAP50–95 teacher adalah 0,7800; rerata Hybrid full, supervised, dan KD murni masing-masing 0,7469, 0,7225, dan 0,6630. TEST telah digunakan sebelumnya dan temuan dibatasi konteks split tersebut.
3. Precision, recall, dan F1 tiap model telah dihitung. F1 Hybrid pada TEST sedikit lebih rendah daripada supervised meskipun mAP50–95-nya lebih tinggi. Pada T38, F1 utama dan rerata F1 per kelas harus dibedakan karena agregasinya berbeda.
4. Dalam pengukuran OP3 deskriptif, latensi/FPS teacher dan Hybrid adalah 96,24 ms/9,88 FPS dan 64,70 ms/13,60 FPS saat diam; saat berjalan masing-masing 95,85 ms/9,87 FPS dan 71,47 ms/12,54 FPS.
5. CPU proses dan RSS tersedia pada kedua kondisi. CPU berada pada kisaran sekitar 1.300% satu CPU logis untuk keempat model; RSS merupakan memori proses detektor. Nilai ini tidak mengukur total konsumsi sistem robot.

## 7.2 Saran

Pemeriksaan lanjutan dapat menggunakan anotasi independen pada adegan dan sesi baru, serta mengulang runtime dalam kondisi dan urutan yang lebih terkendali bila dibutuhkan klaim yang lebih kuat. Arsip checkpoint, konfigurasi, dan data mentah sebaiknya dicadangkan. Pembahasan akhir perlu mempertahankan keterbatasan provenance teacher, split dataset, T38, dan uji runtime.
