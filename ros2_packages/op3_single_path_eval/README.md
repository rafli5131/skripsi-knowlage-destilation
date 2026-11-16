# Evaluasi jalur tunggal OP3

Package baru untuk uji identitas T38/T43, perbandingan jalur predict dan faktor padding/NMS, rincian 24 run, serta diagnosis replay CPU offline. Fungsi evaluator lama dipakai sebagai shared code; acuan TEST diambil dari objek Git revisi `ade031a` dan hash-nya dicatat. Tidak ada akses kamera, motor, ROS live, training, atau instalasi paket. Input dan keluaran disimpan dengan hash; dataset snapshot dan prediksi per frame tetap lokal. Baca dokumentasi percobaan 41 untuk interpretasi dan keterbatasan.
