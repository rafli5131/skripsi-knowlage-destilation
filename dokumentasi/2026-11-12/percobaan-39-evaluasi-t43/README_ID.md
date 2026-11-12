# T43 — evaluasi offline kamera OP3

[Tabel ringkasan](../../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md) · [CSV rinci](../../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.csv) · [Grafik mAP](grafik/perbandingan_map_id.png) · [Confusion matrix gabungan](confusion_matrix/empat_model_id.png)

Ini adalah evaluasi eksploratif **offline** pada satu susunan adegan; bukan pengukuran FPS/latensi dan bukan uji generalisasi lintas adegan. Set terdiri atas 100 frame berobjek dan 30 negatif per kondisi diam dan berjalan. Seluruh gawang pada frame berobjek bersifat parsial; kotak gawang adalah bagian bawah dan kotak robot hanya badan, sesuai keputusan operator setelah 52 label awal. Konvensi tersebut berbeda dari T38; jangan membandingkan nilainya sebagai pengaruh model atau kondisi yang setara.

| Model | mAP50 | mAP50–95 | Precision makro | Recall makro | F1 utama | Gawang TP |
|---|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0.9949 | 0.7462 | 0.6667 | 0.6567 | 0.6616 | 0/200 |
| KD Hybrid | 0.9949 | 0.8275 | 0.9983 | 0.9917 | 0.9950 | 196/200 |
| Supervised | 0.9950 | 0.7865 | 1.0000 | 0.8317 | 0.9081 | 99/200 |
| KD Murni | 0.8658 | 0.7074 | 0.6667 | 0.6667 | 0.6667 | 0/200 |

mAP menggunakan confidence floor 0,001; precision, recall, F1 dan TP menggunakan confidence **> 0,25** serta IoU ≥ 0,5; NMS IoU 0,7. F1 utama adalah harmonik precision makro dan recall makro; rerata F1 per kelas tersedia di CSV. Perbedaan kedua ambang menjelaskan mengapa mAP50 tinggi dapat terjadi meskipun tidak ada prediksi gawang di atas 0,25. Pada setiap model, 0/60 frame negatif menghasilkan prediksi di atas ambang tersebut; angka ini hanya untuk adegan dan set ini.

Pra-label berasal dari gabungan keempat model yang dievaluasi. Operator juga telah melihat preview Hybrid dan mendapat masukan selama pelabelan; tinjauan awal bukan independen sempurna. Pada 52 sampel, satu orang yang sama menghasilkan 40/40 pasangan IoU ≥0,5 di masing-masing kelas; itu bukan kesepakatan antarpeninjau dan tidak memastikan kotak benar. Batas atas kotak gawang bagian bawah belum dipatok pada landmark tetap, dan konvensi kotak berdampak pada AP terutama IoU tinggi. Frame berurutan tidak independen; jangan menafsirkan 260 frame sebagai 260 adegan.

Rincian per kondisi/kelas/TP/FP/FN tersedia dalam CSV pada tautan di atas. Hasil ini tidak menggantikan T38 atau hasil pengujian runtime yang ada.

## Berkas dan interpretasi

Grafik individual dan gabungan tersedia dalam `grafik/`; confusion matrix empat model, tiap model, dan hitungannya tersedia dalam `confusion_matrix/`, masing-masing bahasa Indonesia dan Inggris. Contoh frame berlabel manusia, data mentah dan prediksi per frame tetap lokal; hanya hasil agregat dan manifest hash dibagikan. Matriks memakai baris prediksi, kolom label manual, pencocokan antar kelas berdasarkan IoU tertinggi ≥ 0,5, confidence > 0,25, dan kategori latar untuk pasangan yang tidak cocok; aturan ini bisa menghasilkan rincian berbeda dari pencocokan per kelas untuk precision/recall.

Statistik tindakan edit tidak tercatat per tindakan pada antarmuka; tidak dapat menghitung secara andal jumlah kotak yang digeser atau diubah kelas hanya dari log. Label draf dan final tersimpan sehingga dapat dibandingkan, tetapi peristiwa edit tidak boleh direkayasa.
