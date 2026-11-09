# Dokumentasi per model — hasil OP3

Pilih model untuk melihat confusion matrix, akurasi T38, runtime diam/berjalan, grafik tiga ulangan, dan contoh gambar kamera.

| Model | Folder | Checkpoint yang ditampilkan |
|---|---|---|
| Teacher YOLO11n | [Buka](teacher_yolo11n/README.md) | Teacher FP32 utama |
| KD Hybrid full | [Buka](kd_hybrid/README.md) | Seed 1337 |
| Supervised | [Buka](supervised/README.md) | Seed 1337 |
| KD Murni | [Buka](kd_murni/README.md) | Seed 42 |
| Empat model | [Matriks gabungan](gabungan/README.md) | Keempat checkpoint di atas |

```text
dokumentasi/model/
├── README.md                         Indeks ini
├── teacher_yolo11n/                  Ringkasan + confusion matrix teacher
├── kd_hybrid/                        Ringkasan + confusion matrix KD Hybrid
├── supervised/                       Ringkasan + confusion matrix Supervised
├── kd_murni/                         Ringkasan + confusion matrix KD Murni
├── gabungan/                         Empat model dalam satu gambar
└── manifest_confusion_matrix.json    Hash input dan file keluaran generator
```

Setiap folder model berisi `README.md`, matriks PNG versi jumlah dan persentase dalam bahasa Indonesia dan Inggris, CSV jumlah, CSV persentase, dan JSON metadata. Grafik runtime serta screenshot tetap berada di [folder visualisasi terkurasi](../2026-11-09/visualisasi-tambahan-empat-model/README.md) dan ditautkan dari setiap README agar berkas yang sama tidak digandakan. Contoh media kamera tidak menunjukkan akurasi keseluruhan.

## Cara membaca confusion matrix

Matriks memakai **T38 OP3**, bukan split TEST: 260 frame (200 berobjek dan 60 negatif) dengan 400 kotak acuan; 50 frame parsial tidak masuk. Confidence >0,25, NMS IoU 0,7 dan IoU pencocokan ≥0,5. Baris menunjukkan **label acuan**, kolom menunjukkan **prediksi**. Angka diagonal adalah deteksi sekelas yang cocok; kolom `Terlewat (FN)` adalah label tanpa pasangan. Baris `Latar (FP)` adalah prediksi yang tidak memiliki pasangan, termasuk deteksi ganda atau kotak dengan IoU kurang dari ambang; bukan hanya prediksi pada 60 frame kosong.

Pencocokan dilakukan dalam dua tahap: pertama mencocokkan kelas yang sama sesuai algoritma T38, lalu memasangkan prediksi dan label tersisa yang berbeda kelas berdasarkan IoU tertinggi. Sel di luar diagonal pada tiga kelas menunjukkan pasangan salah kelas; kesalahan itu merupakan FP untuk kelas prediksi **dan** FN untuk kelas acuan. Karena itu, untuk menghitung FP jumlahkan kolom kelas selain diagonal, sedangkan FN adalah jumlah baris kelas selain diagonal. Prosedur ini menjaga TP/FP/FN identik dengan T38; hasilnya bukan matriks bawaan Ultralytics yang bisa memakai aturan asosiasi berbeda.

Pada versi persentase, tiga baris kelas dinormalisasi menurut jumlah kotak acuan kelas tersebut. Baris latar dan sel latar–latar dibiarkan `—` karena tidak ada populasi *true negative* yang terdefinisi untuk kotak deteksi. Gunakan matriks jumlah untuk melihat prediksi tanpa pasangan. Sumber foto, label dan prediksi mentah tetap lokal; [package generator](../../ros2_packages/op3_confusion_matrix/README.md) memakai fungsi bersama dari package evaluasi yang sudah ada.

Frame T38 berasal dari satu rangkaian, dan label awal dibantu KD Murni sebelum ditinjau manusia. Hasil bersifat retrospektif dan tidak membuktikan generalisasi lintas adegan. Hasil TEST, runtime dan T42 VAL tersedia terpisah pada [indeks tabel](../../analisis_performa/INDEKS.md).
