# Protokol evaluasi TEST lanjutan KD Hybrid full — 22 Oktober 2026

## Kedudukan eksperimen

Eksperimen ini melanjutkan pilot KD hibrida yang ditetapkan sebelum training pada [protokol pilot](PILOT_KD_HIBRIDA_2026-10-21.md). Pada VAL resmi, `hybrid_full` mengungguli kontrol supervised pada mAP50–95 untuk seed 42, 1337, dan 2025. Rerata kenaikan berpasangan `+0,0297`; F1 makro pada confidence 0,25 hampir sama, dengan selisih `−0,0008`. Keputusan membawa varian ini ke TEST dibuat berdasarkan VAL, sebelum metrik TEST Hybrid dilihat.

Split TEST resmi Advance Vision pernah dievaluasi untuk teacher FP32/QAT dan eksperimen KD murni. Karena itu, evaluasi ini adalah **perbandingan lanjutan pada split yang pernah digunakan**, bukan holdout yang sepenuhnya baru bagi proyek. Metrik TEST tidak digunakan untuk mengubah model, objective, checkpoint, confidence, atau hyperparameter. Hasil berlaku untuk gambar pada split resmi; pengujian kamera OP3 memerlukan data dan pengukuran terpisah.

## Model yang dikunci

Student memakai `models/yolo11_tiny_kd.yaml` (YOLO11 skala `t` kustom, 810.649 parameter), bukan YOLO11n standar. Teacher YOLO11n FP32 dibekukan saat training Hybrid. Kelas: `ball`, `gawang`, `robot`. Dataset memakai split resmi Roboflow v1 dengan fingerprint agregat TRAIN `a460ec3f6b16bacde012374846e8bd88b51bfdd38bc591433d16517251b198bb`, VAL `117e61befe2d0b2fe7cab5b5a81812572c7100281a4edc6912c3681c45362710`, dan TEST `aa9685a022c7484ef94cbfe68b6d000585d29de752071967709de66bed1762f1`.

Tiga checkpoint `hybrid_full_seed{42,1337,2025}` dibandingkan berpasangan dengan `supervised_seed{42,1337,2025}`. Semua adalah `best.pt` yang dipilih oleh VAL, tercatat dalam [registry model](../configs/model_registry.yaml) dan manifest training masing-masing. Tidak ada seed yang dikeluarkan berdasarkan hasil TEST. Untuk **kandidat deployment OP3 tunggal**, aturan sebelum TEST adalah memilih checkpoint Hybrid dengan mAP50–95 VAL tertinggi: seed **1337** (`0,7523`). Ini belum mengganti checkpoint OP3 yang sedang dipakai.

## Metrik dan perangkat yang dikunci

- Metrik utama: mAP50–95; metrik pendamping: mAP50, precision, recall, F1, dan hasil per kelas. Laporkan keenam model, rerata ± simpangan baku sampel tiga seed per metode, dan selisih Hybrid dikurangi supervised pada seed yang sama. Jangan menyatakan `n=3` sebagai bukti signifikansi kuat.
- AP memakai confidence floor `0,001` dan NMS IoU `0,7`. Precision/recall/F1 makro memakai confidence tetap `>0,25` dan matching IoU `0,50`. F1 keseluruhan adalah harmonic mean dari precision dan recall makro. Ambang ini sama dengan protokol TEST KD murni yang sudah ada.
- Inferensi FP32 tanpa augmentasi, ukuran masukan `640`, batch `16`, workers `2`, validasi rectangular, logical CUDA device `0` pada NVIDIA L40. Runtime terkunci: Python `3.11.2`, NumPy `1.26.4`, PyTorch `2.4.1+cu121`, Ultralytics `8.4.130`.
- Interval bootstrap persentil 95% memakai `1.000` pengambilan ulang gambar dengan pengembalian, seed `20261009`, aturan cakupan kelas makro yang sama dengan evaluator lama. Interval ini hanya menggambarkan variasi sampling gambar bersyarat pada checkpoint, bukan variasi training atau generalisasi sesi baru.
- Evaluator harus memeriksa hash checkpoint, manifest training, YAML data/arsitektur, snapshot kode KD, versi runtime, perangkat, dan fingerprint TEST sebelum inferensi. Cache label berada dalam direktori hasil yang baru. Direktori hasil lama tidak ditimpa.

## Pelaporan dan aturan setelah hasil keluar

Sajikan TEST Hybrid sebagai eksperimen lanjutan dan bandingkan dengan kontrol supervised pada protokol identik. Hasil teacher dan pure KD yang lebih lama boleh dipakai sebagai konteks dengan tanggal dan sumbernya, bukan dicampur sebagai run baru. Jika TEST berbeda arah dari VAL, laporkan perbedaannya; jangan menjalankan pencarian threshold, mengganti seed, atau retraining memakai TEST. Akurasi kamera, tracking, latensi, FPS, CPU, dan RAM pada OP3 dinilai terpisah ketika robot tersedia.

Skrip pelaksanaan: `scripts/evaluate_hybrid_locked_test.py`. Berkas protokol ini dan checksum evaluator direkam dalam manifest evaluasi. Output yang direncanakan: `runs/final_test/hybrid_full_official_split_20261022/`.
