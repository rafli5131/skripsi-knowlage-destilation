# T38 — Evaluasi eksploratif empat model pada 260 frame OP3

**Status:** evaluasi offline retrospektif pada 200 frame berobjek dan 60 negatif yang sama; 50 frame gawang parsial dianalisis terpisah dan tidak masuk tabel utama. Label ditinjau Bhre setelah pra-label dibantu KD murni. Hasil bukan evaluasi independen lintas adegan.

| Model | mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro | F1 mikro | TP / FP / FN | Frame negatif dengan FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0.7058 | 0.5004 | 0.8690 | 0.6833 | 0.6829 | 0.8587 | 322 / 28 / 78 | 2/60 |
| KD Hybrid seed 1337 | 0.7526 | 0.4885 | 0.6836 | 0.5583 | 0.5121 | 0.6464 | 266 / 157 / 134 | 21/60 |
| Supervised seed 1337 | 0.7045 | 0.4414 | 0.7855 | 0.5729 | 0.6054 | 0.6471 | 254 / 131 / 146 | 0/60 |
| KD murni seed 42 | 0.6301 | 0.4218 | 0.7386 | 0.4729 | 0.5008 | 0.5803 | 215 / 126 / 185 | 0/60 |

## Hasil per kelas pada 260 frame

| Model | Kelas | GT | Precision | Recall | F1 | AP50 | AP50–95 | TP / FP / FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | ball | 160 | 1.0000 | 1.0000 | 1.0000 | 0.9950 | 0.8273 | 160 / 0 / 0 |
| Teacher YOLO11n | gawang | 80 | 0.7500 | 0.0750 | 0.1364 | 0.1919 | 0.1224 | 6 / 2 / 74 |
| Teacher YOLO11n | robot | 160 | 0.8571 | 0.9750 | 0.9123 | 0.9304 | 0.5516 | 156 / 26 / 4 |
| KD Hybrid seed 1337 | ball | 160 | 0.9755 | 0.9938 | 0.9845 | 0.9950 | 0.8367 | 159 / 4 / 1 |
| KD Hybrid seed 1337 | gawang | 80 | 0.6667 | 0.0250 | 0.0482 | 0.4874 | 0.2508 | 2 / 1 / 78 |
| KD Hybrid seed 1337 | robot | 160 | 0.4086 | 0.6562 | 0.5036 | 0.7755 | 0.3780 | 105 / 152 / 55 |
| Supervised seed 1337 | ball | 160 | 0.9938 | 0.9938 | 0.9938 | 0.9949 | 0.8027 | 159 / 1 / 1 |
| Supervised seed 1337 | gawang | 80 | 1.0000 | 0.2625 | 0.4158 | 0.5822 | 0.3069 | 21 / 0 / 59 |
| Supervised seed 1337 | robot | 160 | 0.3627 | 0.4625 | 0.4066 | 0.5365 | 0.2145 | 74 / 130 / 86 |
| KD murni seed 42 | ball | 160 | 0.9408 | 0.9938 | 0.9666 | 0.9950 | 0.9232 | 159 / 10 / 1 |
| KD murni seed 42 | gawang | 80 | 1.0000 | 0.1500 | 0.2609 | 0.3285 | 0.1160 | 12 / 0 / 68 |
| KD murni seed 42 | robot | 160 | 0.2750 | 0.2750 | 0.2750 | 0.5668 | 0.2263 | 44 / 116 / 116 |

Pengaturan: 640 piksel, CPU FP32, NMS IoU 0,7; AP memakai confidence floor 0,001, sedangkan precision/recall/F1 pada confidence >0,25 dan pencocokan IoU ≥0,5. F1 makro adalah rerata F1 per kelas. Angka Hybrid dan Supervised identik dengan T34; empat checkpoint, sesi, hash gambar dan label telah diverifikasi.

[CSV lengkap per model/kelas](T38_akurasi_op3_empat_model_260.csv) · [Dokumentasi dan grafik](../../dokumentasi/2026-11-05/percobaan-37-evaluasi-t38-empat-model/README_ID.md). Hasil per kelas dan per sesi, termasuk 50 parsial, ada pada `runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/results.json` di mesin lokal.
