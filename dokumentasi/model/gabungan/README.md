# Confusion matrix gabungan empat model

Semua gambar membandingkan empat checkpoint pada **260 frame OP3 T38 yang sama**. Skala warna dalam setiap gambar disamakan agar antar-panel dapat dibandingkan.

| Jenis | Bahasa Indonesia | English |
|---|---|---|
| Jumlah kotak | [Lihat](confusion_matrix_empat_model_jumlah_id.png) | [View](confusion_matrix_empat_model_jumlah_en.png) |
| Persen per kelas acuan | [Lihat](confusion_matrix_empat_model_persen_id.png) | [View](confusion_matrix_empat_model_persen_en.png) |

Data seluruh model juga tersedia dalam [CSV jumlah](confusion_matrix_empat_model_jumlah.csv) dan [CSV persentase](confusion_matrix_empat_model_persen.csv).

Label acuan adalah baris dan prediksi adalah kolom. Diagonal menunjukkan pasangan benar. Salah kelas yang dipasangkan pada sisa prediksi/label dihitung sebagai FP dan FN; prediksi tanpa pasangan termasuk duplikasi dan kotak yang lokasinya tidak cukup cocok. Baris latar bukan jumlah frame kosong, dan latar–latar tidak didefinisikan sebagai true negative. Pada grafik persen, baris latar sengaja tidak dinormalisasi.

Set ini terdiri dari 200 frame berobjek dan 60 negatif; 50 frame parsial dikeluarkan. Pencocokan sekelas mengikuti T38 sebelum pencocokan lintas kelas sisa; aturan ini mempertahankan TP/FP/FN T38 dan dapat berbeda dari matriks bawaan Ultralytics. Lihat [indeks model](../README.md) untuk penjelasan, sumber, dan tautan per model.

## Grafik garis kontinu gabungan (11 November 2026)

- **mAP50–95 VAL per epoch, tiga metode student** (rerata tiga seed, pita min–maks): [Indonesia](kurva_map50_95_val_per_epoch_id.png) · [English](kurva_map50_95_val_per_epoch_en.png).
- **Akurasi VAL per epoch lengkap** (mAP50, mAP50–95, precision, recall, F1): [Indonesia](garis_akurasi_val_per_epoch_tiga_metode_id.png) · [English](garis_akurasi_val_per_epoch_tiga_metode_en.png) · [data CSV](data_garis_akurasi_val_per_epoch_tiga_metode.csv).
- **Precision, recall, dan F1 terhadap ambang confidence, empat model (VAL):** [Indonesia](garis_sapuan_confidence_val_empat_model_id.png) · [English](garis_sapuan_confidence_val_empat_model_en.png). Hybrid diwakili seed 42 karena T11 tidak memuat seed 1337.
- **Runtime OP3 (latensi, FPS, CPU, RSS) per waktu:** [Indonesia](garis_runtime_op3_empat_model_id.png) · [English](garis_runtime_op3_empat_model_en.png) · [data CSV](data_garis_runtime_op3_empat_model.csv) · [manifest](../manifest_grafik_garis_runtime.json). Per bin 2 detik; batas 8 FPS dievaluasi sebagai rerata run, bukan jaminan setiap bin.

Kurva training teacher utama tidak tersedia di repo, sehingga grafik per epoch hanya memuat tiga metode student. Definisi: kurva per epoch memakai VAL (1.213 gambar) yang tercatat saat training, bukan TEST dan bukan confidence 0,25. Precision dan recall per epoch adalah keluaran validator Ultralytics 8.4.130 pada confidence yang memaksimalkan F1 rata-rata; F1 dihitung sebagai rerata harmonik keduanya. Sapuan confidence berasal dari T11 (VAL, IoU pencocokan 0,5). Hash sumber dan keluaran ada di [manifest](../manifest_grafik_garis_akurasi.json); generator `scripts/build_grafik_garis_model_20261111.py`.

> **Audit 12 November:** hash 18 grafik akurasi/sapuan pada manifest 11 November tidak cocok dengan file sejak commit asal. Sumber dan data gabungan cocok; lihat [audit serta hash aktual](../../2026-11-12/AUDIT_GRAFIK_AKURASI.md). Grafik runtime memiliki manifest terpisah.
