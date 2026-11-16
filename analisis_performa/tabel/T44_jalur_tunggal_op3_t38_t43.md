# T44 — Evaluasi jalur tunggal OP3 T38/T43

Uji identitas 48 pemeriksaan lulus pada empat model: AP validator dan hitungan kelas pada jalur prediktor mereproduksi hasil beku. T38 memuat 200 frame berobjek, 60 negatif, dan 50 parsial yang dilaporkan terpisah. T43 memiliki 130 diam, 130 berjalan di tempat, termasuk masing-masing 30 negatif. Set dan label tidak digabung.

| Set | Model | mAP50–95 historis (val) | mAP50–95 predict | F1 predict protokol | F1 predict runtime | TP gawang runtime | Frame negatif FP runtime |
|---|---|---:|---:|---:|---:|---:|---:|
| t38_primary | Teacher | 0.5004 | 0.5041 | 0.7651 | 0.7728 | 6 | 2 |
| t38_primary | KD Hybrid | 0.4885 | 0.4307 | 0.6146 | 0.6186 | 2 | 21 |
| t38_primary | Supervised | 0.4414 | 0.4216 | 0.6626 | 0.6626 | 21 | 0 |
| t38_primary | KD Murni | 0.4218 | 0.4729 | 0.5766 | 0.5835 | 12 | 0 |
| t38_partial | Teacher | 0.5294 | 0.2859 | 0.3300 | 0.3300 | 0 | 0 |
| t38_partial | KD Hybrid | 0.5370 | 0.6096 | 0.6125 | 0.6125 | 0 | 0 |
| t38_partial | Supervised | 0.5641 | 0.5787 | 0.4884 | 0.4884 | 0 | 0 |
| t38_partial | KD Murni | 0.4847 | 0.5967 | 0.6316 | 0.6316 | 40 | 0 |
| t43_idle | Teacher | 0.7303 | 0.5259 | 0.6667 | 0.6667 | 0 | 0 |
| t43_idle | KD Hybrid | 0.8273 | 0.8981 | 0.9983 | 1.0000 | 100 | 0 |
| t43_idle | Supervised | 0.7374 | 0.7394 | 0.6667 | 0.6667 | 0 | 0 |
| t43_idle | KD Murni | 0.6812 | 0.9297 | 0.6667 | 0.6667 | 0 | 0 |
| t43_walking | Teacher | 0.7777 | 0.5899 | 0.6565 | 0.6565 | 0 | 0 |
| t43_walking | KD Hybrid | 0.8284 | 0.8837 | 0.9916 | 0.9916 | 96 | 0 |
| t43_walking | Supervised | 0.8697 | 0.8274 | 0.9983 | 0.9983 | 99 | 0 |
| t43_walking | KD Murni | 0.8582 | 0.6556 | 0.6667 | 0.6667 | 0 | 0 |
| t43_combined | Teacher | 0.7462 | 0.5473 | 0.6616 | 0.6616 | 0 | 0 |
| t43_combined | KD Hybrid | 0.8275 | 0.8900 | 0.9950 | 0.9958 | 196 | 0 |
| t43_combined | Supervised | 0.7865 | 0.7828 | 0.9081 | 0.9081 | 99 | 0 |
| t43_combined | KD Murni | 0.7074 | 0.7239 | 0.6667 | 0.6667 | 0 | 0 |

Historis menggunakan AP `model.val` dan P/R/F1 `model.predict`. Predict protokol memakai floor 0,001, NMS IoU 0,7; metrik P/R/F1 pada confidence >0,25. Predict runtime memakai confidence 0,25 dan NMS IoU 0,45. Seluruh F1 pada tabel memakai harmonik precision dan recall makro (D11). AP predict memakai `ap_per_class` dan pencocokan sekelas serakah berdasarkan IoU dari `scripts/verify_test_inference_path.py`; TP gawang pada IoU ≥0,5. T38 awal menerbitkan rerata F1 per kelas sebagai metrik tambahan. [CSV lengkap](T44_jalur_tunggal_op3_t38_t43.csv) memuat AP50, per kelas gawang, keempat sel faktor dan indikator validasi.

## Urutan mAP50–95

- t38_primary: historis Teacher > KD Hybrid > Supervised > KD Murni; predict Teacher > KD Murni > KD Hybrid > Supervised.
- t43_combined: historis KD Hybrid > Supervised > Teacher > KD Murni; predict KD Hybrid > Supervised > KD Murni > Teacher.

Urutan berbeda antarjalur; jangan memakai hasil ini untuk memilih ulang model.

## Faktor teacher pada T43 gabungan

Endpoint 512×672/multi-label dan 480×640/single-label teacher T43 sama dengan jalur val dan predict pada toleransi 1e-6.

| Bentuk dan NMS | AP50 gawang | AP50–95 gawang | TP gawang >0,25 | F1 D11 |
|---|---:|---:|---:|---:|
| 480_single | 0.1112 | 0.0580 | 0 | 0.6616 |
| 480_multi | 0.1112 | 0.0580 | 0 | 0.6616 |
| 512_single | 0.9946 | 0.6559 | 37 | 0.8338 |
| 512_multi | 0.9946 | 0.6559 | 37 | 0.8338 |

Pada teacher T43, perubahan bentuk/padding memiliki dampak jauh lebih besar daripada perubahan multi-label NMS pada empat sel tersebut. Ini merupakan temuan untuk set ini, bukan generalisasi lintas adegan. Endpoint 512×672 pada tiga student T38 tidak mereproduksi AP validator dalam toleransi; tabel faktornya disimpan tetapi **tidak ditafsirkan**. Selisih maksimum:

- KD Hybrid / t38_primary: sel val Δ maksimum 0.002095, sel predict Δ 0.000000
- KD Hybrid / t38_partial: sel val Δ maksimum 0.006113, sel predict Δ 0.000000
- Supervised / t38_primary: sel val Δ maksimum 0.001813, sel predict Δ 0.000000
- Supervised / t38_partial: sel val Δ maksimum 0.003368, sel predict Δ 0.000000
- KD Murni / t38_primary: sel val Δ maksimum 0.001171, sel predict Δ 0.000000
- KD Murni / t38_partial: sel val Δ maksimum 0.001772, sel predict Δ 0.000000

Semua frame, label dan prediksi per frame tetap lokal.
