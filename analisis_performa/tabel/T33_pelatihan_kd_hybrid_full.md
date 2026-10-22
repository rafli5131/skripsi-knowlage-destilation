# T33. Pelatihan dan konvergensi KD Hybrid full

Tiga run memakai 100 epoch, batch 16, imgsz 640, AdamW, AMP mati, student YOLO11 skala `t` kustom, teacher FP32 beku, serta bobot distilasi fitur/kotak/kelas 1/1/1 pada temperatur kelas 2. Label TRAIN masuk loss deteksi student; TEST tidak masuk training. Kontrol supervised dengan resep bersama tercatat pada T02–T03.

| seed | durasi training (s) | epoch mAP tertinggi di log | VAL mAP50–95 tertinggi di log | VAL mAP50–95 best.pt menurut manifest | epoch 10 | epoch 25 | epoch 50 | epoch 75 | epoch 100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 4840.09 | 100 | 0.7486 | 0.7488 | 0.5611 | 0.6574 | 0.7155 | 0.7323 | 0.7486 |
| 1337 | 3779.57 | 98 | 0.7529 | 0.7523 | 0.5504 | 0.6603 | 0.7167 | 0.7385 | 0.7517 |
| 2025 | 3719.85 | 93 | 0.7503 | 0.7507 | 0.5768 | 0.6664 | 0.7154 | 0.7400 | 0.7490 |

Durasi diambil dari kolom `time` pada baris epoch terakhir `results.csv`. Epoch mAP tertinggi pada log bukan klaim tentang epoch checkpoint `best.pt`; angka checkpoint dari manifest dan evaluasi ulang `best.pt` pada T04/T28 dicatat terpisah. Perbedaan kecil di antara ketiganya tidak disamarkan. Perbedaan durasi antar-run pada server bersama tidak membuktikan perbedaan biaya komputasi kausal.
