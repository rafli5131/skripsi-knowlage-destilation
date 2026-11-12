# Grafik akurasi VAL hasil reproduksi — 12 November 2026

Grafik dalam folder ini dibuat ulang dari sumber yang hash-nya cocok dengan manifest 11 November, menggunakan generator yang sama dan Matplotlib 3.6.3. Ini merupakan versi baru dengan [manifest hash sendiri](manifest.json); file historis tidak diganti. Lihat [audit dan batasnya](../AUDIT_GRAFIK_AKURASI.md).

| Model | Akurasi per epoch ID / EN | Sapuan confidence ID / EN |
|---|---|---|
| Teacher | Kurva teacher utama tidak tersedia | [ID](teacher_yolo11n/garis_sapuan_confidence_val_teacher_yolo11n_id.png) · [EN](teacher_yolo11n/garis_sapuan_confidence_val_teacher_yolo11n_en.png) |
| Hybrid | [ID](kd_hybrid/garis_akurasi_val_per_epoch_kd_hybrid_id.png) · [EN](kd_hybrid/garis_akurasi_val_per_epoch_kd_hybrid_en.png) | [ID](kd_hybrid/garis_sapuan_confidence_val_kd_hybrid_id.png) · [EN](kd_hybrid/garis_sapuan_confidence_val_kd_hybrid_en.png) |
| Supervised | [ID](supervised/garis_akurasi_val_per_epoch_supervised_id.png) · [EN](supervised/garis_akurasi_val_per_epoch_supervised_en.png) | [ID](supervised/garis_sapuan_confidence_val_supervised_id.png) · [EN](supervised/garis_sapuan_confidence_val_supervised_en.png) |
| KD murni | [ID](kd_murni/garis_akurasi_val_per_epoch_kd_murni_id.png) · [EN](kd_murni/garis_akurasi_val_per_epoch_kd_murni_en.png) | [ID](kd_murni/garis_sapuan_confidence_val_kd_murni_id.png) · [EN](kd_murni/garis_sapuan_confidence_val_kd_murni_en.png) |
| Gabungan | [ID](gabungan/garis_akurasi_val_per_epoch_tiga_metode_id.png) · [EN](gabungan/garis_akurasi_val_per_epoch_tiga_metode_en.png) | [ID](gabungan/garis_sapuan_confidence_val_empat_model_id.png) · [EN](gabungan/garis_sapuan_confidence_val_empat_model_en.png) |

Kurva per epoch menggunakan VAL, bukan TEST; precision/recall merupakan keluaran validator pada confidence yang memaksimalkan F1 rata-rata. Sapuan Hybrid menggunakan seed 42 karena T11 tidak memuat seed 1337. Pita grafik gabungan adalah rentang minimum–maksimum tiga seed, bukan interval kepercayaan.
