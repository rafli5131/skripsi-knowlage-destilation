# Ringkasan akurasi TEST resmi

Tabel ini menyatukan angka dari [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md). Nilai student merupakan rerata tiga seed; teacher satu checkpoint. TEST resmi berisi 592 gambar. P/R/F1 memakai confidence >0,25 dan IoU 0,50; AP memakai confidence floor 0,001 dan NMS 0,7. SD dan rincian per seed tersedia pada tabel sumber.

| Model/metode | mAP50 | mAP50–95 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| Teacher YOLO11n, satu checkpoint | 0,9642 | 0,7800 | 0,8915 | 0,9697 | 0,9290 |
| Supervised student, rerata 3 seed | 0,9601 | 0,7225 | 0,8609 | 0,9699 | 0,9121 |
| KD murni, rerata 3 seed | 0,9446 | 0,6630 | 0,7547 | 0,9631 | 0,8462 |
| KD Hybrid full, rerata 3 seed | 0,9583 | 0,7469 | 0,8519 | 0,9698 | 0,9071 |

Hybrid full memiliki rerata mAP50–95 lebih tinggi daripada supervised, sedangkan F1-nya sedikit lebih rendah. Tiga seed memberi bukti eksploratif; teacher hanya satu checkpoint. Provenance data training teacher belum sepenuhnya tersedia, dan TEST sudah pernah digunakan sebelum evaluasi Hybrid lanjutan. Hasil ini tidak otomatis menunjukkan akurasi kamera OP3. Evaluasi kamera [T34](../../../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.md) adalah analisis eksploratif terpisah dan menggunakan definisi F1 makro per kelas; jangan mencampur definisinya dengan tabel ini.

Waktu training dan durasi sesi TEST tersedia pada [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md); latency dan FPS onboard robot tersedia pada [T36](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) dan [T37](../../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md).
