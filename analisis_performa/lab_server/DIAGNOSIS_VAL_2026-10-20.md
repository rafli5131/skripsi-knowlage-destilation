# Diagnosis VAL untuk keputusan KD — 20 Oktober 2026

## Metode

Tujuh checkpoint terdaftar (teacher, tiga student KD, tiga student supervised) dievaluasi ulang pada **1.213 gambar VAL / 1.525 objek** dari split resmi Roboflow. Semua pasangan gambar dan label cocok dengan hash pada `artifacts/advance_vision_dataset_fingerprint.json`. Inference memakai `DetectionValidator` Ultralytics 8.4.130, FP32 CPU, ukuran 640, `rect=True`, tanpa augmentasi, confidence floor 0,001, NMS IoU 0,7. CPU pada host audit dipakai hanya untuk diagnosis akurasi; waktu proses ini bukan benchmark server L40 atau OP3. Skrip dan prediksi per gambar ada di [`scripts/analyze_val_detections.py`](../../scripts/analyze_val_detections.py) dan [`runs/val_diagnostics/official_split_20261020/`](../../runs/val_diagnostics/official_split_20261020/). Ringkasan mesin ada di [`summary.json`](../../runs/val_diagnostics/official_split_20261020/summary.json).

T09 dan T10 memakai pencocokan satu-ke-satu kelas sama pada IoU ≥0,50, lalu memasangkan sisa yang salah kelas dan masih overlap. FP sisanya dikelompokkan secara eksklusif menjadi duplikasi, lokalisasi, atau latar. T11 dan T14 memakai TP pada IoU 0,50 dari validator resmi, sehingga cara hitung P/R/F1 selaras dengan evaluator TEST. Semua ambang alternatif dipilih **hanya dari VAL**. T09–T11 dan T14 adalah diagnosis image-level; tidak satu pun mengukur akurasi kamera OP3.

## Hasil utama

| Model | F1 VAL conf >0,25 | Ambang F1 tertinggi pada grid VAL | F1 pada ambang itu | FP/gambar conf >0,25 | FP duplikasi |
| --- | ---: | ---: | ---: | ---: | ---: |
| Teacher YOLO11n | 0,9336 | 0,40 | 0,9476 | 0,261 | 163 |
| KD seed 42 | 0,8676 | 0,50 | 0,8962 | 0,358 | 240 |
| KD seed 1337 | 0,8576 | 0,45 | 0,8860 | 0,364 | 231 |
| KD seed 2025 | 0,8832 | 0,40 | 0,9098 | 0,323 | 197 |
| Supervised seed 42 | 0,9235 | 0,40 | 0,9400 | 0,256 | 134 |
| Supervised seed 1337 | 0,9186 | 0,45 | 0,9262 | 0,262 | 131 |
| Supervised seed 2025 | 0,9218 | 0,40 | 0,9407 | 0,264 | 133 |

Rerata tiga seed KD pada conf >0,25 ialah F1 **0,8695** dan **0,348 FP/gambar**; kontrol supervised **0,9213** dan **0,261 FP/gambar**. Duplikasi KD rata-rata **223** per checkpoint, kontrol **133**. Pada ambang VAL terbaik masing-masing, rerata F1 menjadi **0,8973** untuk KD dan **0,9356** untuk supervised. Sapuan confidence memperbaiki F1 KD, tetapi belum menutup selisih dengan kontrol. Nilai ambang terbaik berasal dari grid yang sama dengan pelaporan hasil ini; jangan memperlakukannya sebagai estimasi performa pada data independen.

Pada seed deploy KD 42, menaikkan confidence dari 0,25 ke 0,50 mengubah precision/recall `gawang` pada VAL dari **0,751/0,949** menjadi **0,913/0,802**. Jadi ada penurunan recall gawang sekitar **0,147**. Sesi kamera OP3 idle yang tersimpan mempunyai rata-rata confidence gawang sekitar **0,290**; ambang 0,50 berisiko membuang deteksi gawang pada kondisi tersebut. **Jangan ubah threshold runtime OP3 menjadi 0,50** hanya dari optimum F1 dataset VAL. Keputusan deployment memerlukan frame kamera OP3 berlabel dan sasaran precision/recall yang dinyatakan jelas.

T10 mencatat nol pasangan salah kelas pada aturan IoU ≥0,50 untuk ketujuh model. Itu tidak berarti classifier sempurna: prediksi salah kelas yang tidak beririsan cukup besar dengan anotasi masuk kategori latar atau lokalisasi. Dari T09, latar dan lokalisasi juga masih ada; tetapi kelebihan FP KD terhadap supervised pada protokol ini sebagian besar bertepatan dengan jumlah duplikasi yang lebih tinggi. Penjelasan kausal terhadap objective training **belum terbukti** dari analisis observasional ini.

T14 menunjukkan ECE 10 bin pada conf >0,25 sekitar **0,105** untuk KD dan **0,177** untuk supervised (rerata tiga seed). ECE ini hanya menilai apakah confidence deteksi yang lolos threshold sesuai frekuensi TP, dengan sampel yang berbeda menurut model. Angka ECE lebih kecil tidak menghapus selisih mAP atau F1 dan bukan alasan sendiri untuk memilih model.

## Saran perbaikan KD murni

1. **Pertahankan `pure_v4` sebagai baseline tetap** dan simpan semua hasil yang sekarang. T03 menunjukkan epoch VAL terbaik KD pada 88–96 dari 100; data ini belum mendukung loncatan ke 300 epoch sebagai langkah pertama.
2. **Coba satu pilot `pure_weighted` pada VAL** bila target penelitian memang menaikkan kualitas KD. Loss box Smooth L1 dan class BCE saat ini dirata-ratakan pada semua 8.400 lokasi prediksi untuk citra 640 × 640 tanpa bobot perhatian teacher, sedangkan loss fitur sudah berbobot skor teacher. Beri bobot lokasi berbasis `max sigmoid(score_teacher)` pada loss box/kelas dan normalisasi terhadap jumlah bobot agar skala loss terkontrol. Ini tetap pure teacher-only KD. Gunakan arsitektur, data, augmentasi, seed, dan anggaran epoch sama; bandingkan F1/P/R, mAP50–95, dan kategori FP pada VAL. Jangan buka TEST untuk memilih kandidat.
3. **Jadikan DFL-KL kandidat kedua, bukan perubahan awal.** `Detect.forward_head` Ultralytics 8.4.130 menghasilkan `boxes` berupa 4 × `reg_max` logit DFL mentah dan `scores` berupa logit kelas; teacher dan student sama-sama `reg_max=16`, `nc=3`, `end2end=False`. Smooth L1 sekarang mencocokkan logit kotak mentah. KL atas distribusi per sisi dapat dicoba setelah bentuk tensor dan skala loss diaudit, tetapi mengubah objective lebih besar daripada menambah bobot teacher. Kode sumber: `ultralytics/nn/modules/head.py` baris 106–172, `ultralytics/nn/distill_model.py` baris 301–318, dan `scripts/train_kd.py` fungsi `install_teacher_only_kd_loss`.
4. **Jangan jalankan hybrid atau training utama baru saat ini.** D2 mengunci KD murni; T04 masih menunggu pilot. Jika pilot tidak memberi perbaikan konsisten di VAL, hasil KD yang lebih rendah daripada kontrol tetap merupakan temuan sah untuk skripsi.

## Batas keputusan OP3

Operator menyatakan perangkat OP3 siap, tetapi repo belum menyediakan `scripts/camera_stream_probe.py`, `scripts/record_fixed_frames.py`, `scripts/benchmark_cpu_frames.py`, atau set frame kamera OP3 berlabel. Paket `op3_idle_trial` sudah membuktikan satu sesi idle; ia belum memenuhi benchmark CPU frame tetap, perbandingan tanpa detektor, atau akurasi kamera untuk T16/T17/T22/T27. Bagian itu memerlukan konfirmasi prosedur dan alat ukur sebelum sesi robot berikutnya. Tidak ada perangkat OP3 yang dijalankan untuk diagnosis VAL ini.
