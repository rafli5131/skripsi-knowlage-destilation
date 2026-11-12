# T43 — sensitivitas confidence (bagian A)

Empat model dievaluasi ulang **offline** pada 260 frame dan label yang sama. Prediksi T43 sebelumnya disimpan hanya di atas 0,25, sehingga prediksi dihitung ulang dari confidence 0,001. AP gabungan dan hitungan setiap frame pada confidence >0,25 cocok dengan baseline untuk keempat model. Sapuan memakai confidence **lebih besar dari** 0,05–0,90 per 0,05, NMS IoU 0,7 dan pencocokan kelas + IoU ≥0,5. F1 makro mengikuti D11. Kondisi diam, berjalan di tempat, dan gabungan serta detail TP/FP/FN semua kelas ada di [CSV](T43_sensitivitas_confidence.csv).

Ambang tertinggi berikut hanya berasal dari grid dan bukan ambang baru yang disarankan. Kuartil dihitung dari prediksi gawang yang cocok pada floor 0,001; jumlah pasangan dapat kurang dari 200, sehingga bukan distribusi untuk seluruh gawang.

| Model | Ambang tertinggi recall ≥ 0,9 | Recall >0,05 | Recall >0,25 | Pasangan pada floor | Median | Q1–Q3 | Min–maks |
|---|---:|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | Tidak ada | 0.000 | 0.000 | 68/200 | 0.0035 | 0.0014–0.0093 | 0.0010–0.0362 |
| KD Hybrid | 0.35 | 1.000 | 0.980 | 200/200 | 0.4356 | 0.4053–0.4557 | 0.1591–0.5153 |
| Supervised | 0.15 | 1.000 | 0.495 | 200/200 | 0.2346 | 0.1966–0.3278 | 0.1560–0.4123 |
| KD Murni | Tidak ada | 0.005 | 0.000 | 191/200 | 0.0128 | 0.0072–0.0205 | 0.0011–0.0511 |

Pada jalur prediksi ini supervised mencapai recall 1,0 pada >0,05 seperti Hybrid; teacher tidak mencapai 0,9 pada grid, dengan recall 0 pada >0,05. KD Murni juga tidak mencapai 0,9 pada grid. Evaluasi ini bersifat deskriptif pada satu susunan adegan dengan frame berurutan dan pra-label gabungan dari model yang diuji.

## Temuan perbedaan jalur AP dan prediksi

AP T43 dihitung dengan `model.val`, sedangkan sapuan dan precision/recall/F1 menggunakan `model.predict`. Pada pemeriksaan lokal model teacher, validator menerima tensor **512 × 672** setelah padding, sedangkan prediktor menerima **480 × 640**. Kode Ultralytics validator juga menggunakan NMS `multi_label=True`; tidak dapat diasumsikan kedua jalur memiliki postprocessing yang identik. Pada satu frame yang sama, prediksi gawang teacher tidak muncul di atas 0,001 pada jalur operasi default, tetapi confidence berubah ketika ukuran/padding prediksi diubah. Diagnosis ini menunjukkan bahwa perbedaan preprocessing dan postprocessing **dapat memengaruhi** hasil; pengaruh masing-masing belum diisolasi.

Sebagai pemeriksaan tambahan, keluaran validator teacher yang disimpan dalam JSON (nilai dan kotak dibulatkan) menghasilkan 200/200 pasangan gawang pada floor 0,001 dan 37/200 pada confidence >0,25; pada jalur prediksi operasi hasilnya 68/200 dan 0/200. Hasil ini tidak menggantikan tabel utama karena jalurnya berbeda. Jangan menyimpulkan bahwa selisih AP dan F1 hanya akibat confidence atau kalibrasi, dan jangan mengganti ambang operasi berdasarkan set ini.

Grafik ID/EN per kelas dan dokumentasi tersedia pada [folder percobaan](../../dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/README_ID.md). Ambang operasi D4 tetap 0,25. Bagian B menunggu sesi peninjau kedua dan pelabelan konvensi alternatif.
