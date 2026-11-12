# Evaluasi offline T43

Package baru yang memakai fungsi evaluasi bersama `op3_camera_eval` dan `op3_multi_session_eval` tanpa mengubahnya. `evaluate.py` memeriksa hash label beku, gambar, log dan checkpoint, lalu menghitung AP serta metrik ambang tetap per kondisi dan gabungan. Output eksklusif menolak menimpa run yang ada. `visualize.py` dan `document.py` membuat grafik, confusion matrix, tabel, dan dokumentasi. Semuanya offline; tidak ada akses kamera atau servo. Lihat dokumentasi percobaan 39 untuk definisi dan keterbatasan.
