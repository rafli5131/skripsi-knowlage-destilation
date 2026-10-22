# Evaluasi eksploratif kamera OP3

60 frame dari 1 sesi telah ditinjau manusia oleh `bhre` (60/60 frame tercakup dalam log review). Label awal dibuat otomatis menggunakan checkpoint KD runtime `models/weights/kd_student_best.pt` (SHA-256 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`), lalu diperiksa dan disimpan oleh peninjau. Karena model KD yang dievaluasi juga membuat draf label, bias anchoring peninjau dapat menguntungkan KD.

| Model | Precision makro | Recall makro | F1 makro | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|
| KD runtime | 0.8618 | 1.0000 | 0.9128 | 0.9380 | 0.4790 |
| Hybrid seed 42 | 0.8333 | 0.6713 | 0.6757 | 0.8640 | 0.5666 |
| Supervised seed 42 | 0.3441 | 0.3444 | 0.3443 | 0.9414 | 0.5809 |

Precision, recall, dan F1 adalah hasil pada confidence 0.25 dengan pencocokan IoU 0.5; mAP dihitung dari kurva confidence (confidence minimum 0.001), jadi urutan mAP tidak harus sama dengan F1 pada satu threshold.

Angka ini bersifat **eksploratif**: hanya 60 frame dari satu sesi, diambil tiap satu detik sehingga frame berdekatan berkorelasi, dan kondisi sesi tercatat `unknown`. Hasil ini belum mengukur generalisasi pada sesi, pencahayaan, jarak, atau gerakan yang bervariasi. Lihat `input_manifest.json` untuk hash gambar/label, checkpoint, serta konfigurasi evaluasi; `summary.csv` dan `per_class.csv` memuat rincian metrik.
