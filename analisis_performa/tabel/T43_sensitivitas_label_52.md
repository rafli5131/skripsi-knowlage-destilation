# T43 — sensitivitas label pada 52 frame

Tiga set label pada **52 frame yang sama**: label final Bhre (T43 awal), label Dipo mengikuti aturan T43 yang diperjelas, dan label alternatif Dipo (seluruh rangka gawang dan seluruh tubuh robot terlihat). Dua sesi Dipo dilakukan berurutan; aturan awal diperjelas setelah anotasi Bhre, sehingga efek aturan dan peninjau tidak dapat dipisahkan. Tidak ada pelatihan atau pemilihan ulang model.

## Kesesuaian peninjau pada konvensi T43

Pasangan satu-ke-satu berkelas sama dengan IoU ≥0,5; jumlah pasangan dimaksimalkan, kemudian jumlah IoU. Label awal Bhre dan Dipo sama-sama memuat 40 kotak per kelas.

| Kelas | Pasangan/Bhre | Pasangan/Dipo | Bhre tanpa pasangan | Dipo tanpa pasangan | IoU rata-rata | IoU median |
|---|---:|---:|---:|---:|---:|---:|
| ball | 40/40 | 40/40 | 0 | 0 | 0.6811 | 0.6748 |
| gawang | 40/40 | 40/40 | 0 | 0 | 0.6389 | 0.6307 |
| robot | 40/40 | 40/40 | 0 | 0 | 0.8882 | 0.8969 |

## Hasil empat model

P, R dan F1 adalah makro pada confidence >0,25 dan IoU ≥0,5; F1 utama adalah harmonik P dan R makro (D11). AP menggunakan confidence floor 0,001. TP gawang adalah jumlah gawang terdeteksi pada ambang operasi. Per kelas, TP/FP/FN, dan negatif tersedia dalam [CSV](T43_sensitivitas_label_52.csv).

| Model | Bhre AP50 | Bhre AP50–95 | Bhre P | Bhre R | Bhre F1 | Bhre TP gawang | Dipo AP50 | Dipo AP50–95 | Dipo P | Dipo R | Dipo F1 | Dipo TP gawang | Alternatif AP50 | Alternatif AP50–95 | Alternatif P | Alternatif R | Alternatif F1 | Alternatif TP gawang |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0.9948 | 0.7409 | 0.6667 | 0.6500 | 0.6582 | 0 | 0.9872 | 0.4625 | 0.6667 | 0.6500 | 0.6582 | 0 | 0.6661 | 0.2900 | 0.6667 | 0.6500 | 0.6582 | 0 |
| KD Hybrid | 0.9928 | 0.8134 | 0.9919 | 0.9833 | 0.9876 | 38 | 0.9893 | 0.4328 | 0.9919 | 0.9833 | 0.9876 | 38 | 0.6539 | 0.2649 | 0.6673 | 0.6750 | 0.6711 | 1 |
| Supervised | 0.9950 | 0.7888 | 1.0000 | 0.8250 | 0.9041 | 19 | 0.9950 | 0.5230 | 1.0000 | 0.8250 | 0.9041 | 19 | 0.7722 | 0.3094 | 0.9474 | 0.8000 | 0.8675 | 16 |
| KD Murni | 0.8672 | 0.7056 | 0.6667 | 0.6667 | 0.6667 | 0 | 0.7918 | 0.3995 | 0.6667 | 0.6667 | 0.6667 | 0 | 0.6493 | 0.2913 | 0.6583 | 0.6583 | 0.6583 | 0 |

## Urutan model

- bhre — mAP50-95: KD Hybrid (0.8134) > Supervised (0.7888) > Teacher YOLO11n (0.7409) > KD Murni (0.7056)
- bhre — F1: KD Hybrid (0.9876) > Supervised (0.9041) > KD Murni (0.6667) > Teacher YOLO11n (0.6582)
- dipo — mAP50-95: Supervised (0.5230) > Teacher YOLO11n (0.4625) > KD Hybrid (0.4328) > KD Murni (0.3995)
- dipo — F1: KD Hybrid (0.9876) > Supervised (0.9041) > KD Murni (0.6667) > Teacher YOLO11n (0.6582)
- alternative — mAP50-95: Supervised (0.3094) > KD Murni (0.2913) > Teacher YOLO11n (0.2900) > KD Hybrid (0.2649)
- alternative — F1: Supervised (0.8675) > KD Hybrid (0.6711) > KD Murni (0.6583) > Teacher YOLO11n (0.6582)

Urutan dinyatakan untuk sampel dan konvensi ini, bukan untuk memilih ulang model. Perbandingan antarsesi Dipo juga dapat mengandung efek urutan dan ingatan. Frame diambil dari satu setup dan saling berkorelasi; 52 frame bukan 52 adegan independen. Pra-label T43 memakai gabungan model yang diuji dan Bhre telah melihat preview Hybrid. Konvensi alternatif tidak sama dengan anotasi awal.

Penghitungan AP menggunakan `model.val`, sedangkan P/R/F1 menggunakan `model.predict`; tensor padding dan NMS berbeda pada pemeriksaan teacher. Jangan menafsirkan selisih AP dan F1 semata sebagai perbedaan kalibrasi confidence. Lihat [sensitivitas confidence](T43_sensitivitas_confidence.md) dan [dokumentasi](../../dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/README_ID.md).
