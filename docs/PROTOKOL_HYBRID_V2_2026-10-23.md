# Protokol terkunci: penyaringan KD hibrida v2 di VAL

Tanggal kunci: 23 Oktober 2026, sebelum pelatihan baru. Arahan Bhre untuk melanjutkan eksperimen dengan syarat semua model lama dipertahankan. Acuan adalah [prompt perbaikan](../prompt/PROMPT_PERBAIKAN_KD_JALUR_TENGAH.md) dan diagnosis [T39](../analisis_performa/tabel/T39_diagnosis_objektif_kd.md).

## Data dan batas inferensi

TRAIN/VAL memakai split resmi Roboflow Advance Vision dan sidik jari dataset yang sudah dikunci. Semua pemilihan memakai VAL; TEST lama sudah diketahui sehingga tidak akan disebut holdout independen. T34 OP3 tidak dipakai untuk memilih konfigurasi. Teacher YOLO11n, student skala t, resep 100 epoch, dan tiga seed 42/1337/2025 sama dengan Hybrid full. Hanya objektif KD yang berubah. `op3_default`, seluruh checkpoint lama, dan hasil lama tetap dipertahankan.

## Urutan dan aturan sebelum hasil dilihat

S1 memakai Smooth L1 dan bobot kotak skor maksimum teacher. S2 memakai KL distribusi DFL dengan temperatur kotak 1,0 tanpa bobot anchor. S3 menggabungkan S1 dan S2. Ketiganya memakai seed 42. S4 menambahkan bobot kelas dengan lantai 0,1 pada konfigurasi terbaik S1–S3. S5 dan S6 membandingkan temperatur kelas 1,0 dan 4,0 terhadap konfigurasi terbaik sejauh itu. S7 dan S8 membandingkan bobot KD kotak dan kelas masing-masing 0,5 dan 2,0 terhadap konfigurasi terbaik sejauh itu. Maksimal delapan run penyaringan. Bila kandidat baru gagal, konfigurasi terbaik tidak berubah. `box_tau=1,0` dipilih tanpa mengklaim reproduksi formulasi paper tertentu.

Aturan penyaringan: kandidat baru lebih baik bila mAP50-95 VAL naik sekurangnya 0,004, atau perubahan mAP50-95 kurang dari 0,004 dan F1 makro pada confidence 0,25 naik sekurangnya 0,005. Jika tidak, pertahankan yang lebih sederhana. Acuan awal Hybrid full seed 42: mAP50-95 0,7488, F1 0,9220. Semua hasil seed 42 bersifat eksploratif.

Maksimal dua kandidat hasil penyaringan dikonfirmasi pada seed 1337 dan 2025. Kandidat mengganti Hybrid full hanya bila pada rerata VAL tiga seed: mAP50-95 tidak turun lebih dari 0,002; F1@0,25 naik sekurangnya 0,005 atau mAP50-95 naik sekurangnya 0,004; peningkatan metrik tersebut positif pada minimal dua seed; mAP50-95 mengungguli Supervised pada semua seed. Bila tak ada yang lolos, Hybrid full tetap model hasil KD.

Ambang operasi utama 0,25 tetap. Analisis ambang alternatif dari VAL bersifat sekunder. Evaluasi OP3 dilakukan setelah model final dipilih. Ablasi teacher YOLO11s tetap terpisah dan membutuhkan kontrol YOLO11n dengan resep sama untuk klaim pengaruh ukuran teacher.

## Penyimpanan

Setiap run baru memakai `runs/kd_hybrid_v2/yolo11_tiny_hybrid_v2_s<id>_seed<seed>/`; kode pelatihan menolak direktori run yang sudah ada. Hasil evaluasi memakai direktori VAL baru dan menolak berkas yang sudah ada. Konfigurasi S4–S8 akan dibuat setelah hasil tahap sebelumnya menentukan induknya, tanpa mengubah S1–S3. Checkpoint teacher tidak dipublikasikan.
