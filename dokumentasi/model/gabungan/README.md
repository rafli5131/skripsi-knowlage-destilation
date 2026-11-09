# Confusion matrix gabungan empat model

Semua gambar membandingkan empat checkpoint pada **260 frame OP3 T38 yang sama**. Skala warna dalam setiap gambar disamakan agar antar-panel dapat dibandingkan.

| Jenis | Bahasa Indonesia | English |
|---|---|---|
| Jumlah kotak | [Lihat](confusion_matrix_empat_model_jumlah_id.png) | [View](confusion_matrix_empat_model_jumlah_en.png) |
| Persen per kelas acuan | [Lihat](confusion_matrix_empat_model_persen_id.png) | [View](confusion_matrix_empat_model_persen_en.png) |

Data seluruh model juga tersedia dalam [CSV jumlah](confusion_matrix_empat_model_jumlah.csv) dan [CSV persentase](confusion_matrix_empat_model_persen.csv).

Label acuan adalah baris dan prediksi adalah kolom. Diagonal menunjukkan pasangan benar. Salah kelas yang dipasangkan pada sisa prediksi/label dihitung sebagai FP dan FN; prediksi tanpa pasangan termasuk duplikasi dan kotak yang lokasinya tidak cukup cocok. Baris latar bukan jumlah frame kosong, dan latar–latar tidak didefinisikan sebagai true negative. Pada grafik persen, baris latar sengaja tidak dinormalisasi.

Set ini terdiri dari 200 frame berobjek dan 60 negatif; 50 frame parsial dikeluarkan. Pencocokan sekelas mengikuti T38 sebelum pencocokan lintas kelas sisa; aturan ini mempertahankan TP/FP/FN T38 dan dapat berbeda dari matriks bawaan Ultralytics. Lihat [indeks model](../README.md) untuk penjelasan, sumber, dan tautan per model.
