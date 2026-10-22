# Evaluasi VAL KD Hybrid full multi-seed — 22 Oktober 2026

## Protokol

Enam checkpoint `best.pt` dibandingkan pada VAL resmi yang sama, 1.213 gambar. Per pasangan seed, arsitektur student, split, dan resep training supervised cocok dengan KD Hybrid; perbedaan objective-nya adalah ada/tidaknya loss distilasi. Kontrol supervised seed 1337 melanjutkan run terhenti dari `last.pt`; manifest merekam resume dan penyelesaian resep 100 epoch yang sama. Fingerprint split VAL: `117e61befe2d0b2fe7cab5b5a81812572c7100281a4edc6912c3681c45362710`. Inferensi FP32 pada CPU, imgsz 640, batch 16, rectangular validation, tanpa augmentasi; AP memakai confidence floor 0,001 dan NMS IoU 0,7. Precision/recall/F1 memakai confidence tetap 0,25 dan matching IoU 0,50. Tidak ada training saat evaluasi dan **TEST tidak dibuka**.

## Hasil keseluruhan

Nilai berikut adalah rerata ± simpangan baku sampel antar tiga seed. Δ dihitung berpasangan sebagai KD Hybrid full dikurangi supervised pada seed yang sama.

| metrik | Hybrid full, rerata ± SD | Supervised, rerata ± SD | Δ berpasangan, rerata ± SD |
| --- | --- | --- | --- |
| mAP50 | 0,9733 ± 0,0008 | 0,9704 ± 0,0030 | +0,0029 ± 0,0035 |
| mAP50-95 | 0,7505 ± 0,0018 | 0,7208 ± 0,0041 | +0,0297 ± 0,0047 |
| precision@0.25 | 0,8739 ± 0,0064 | 0,8790 ± 0,0034 | -0,0051 ± 0,0074 |
| recall@0.25 | 0,9724 ± 0,0063 | 0,9678 ± 0,0028 | +0,0046 ± 0,0083 |
| F1@0.25 | 0,9205 ± 0,0021 | 0,9213 ± 0,0025 | -0,0008 ± 0,0006 |

Selisih mAP50–95 per seed:

| seed | Hybrid full | Supervised | Δ Hybrid − supervised |
| --- | --- | --- | --- |
| 42 | 0,7488 | 0,7189 | +0,0298 |
| 1337 | 0,7523 | 0,7179 | +0,0343 |
| 2025 | 0,7505 | 0,7255 | +0,0250 |

## Hasil per kelas

| kelas | Δ AP50–95, rerata ± SD | Δ precision@0,25, rerata ± SD | Δ recall@0,25, rerata ± SD | Δ F1@0,25, rerata ± SD |
| --- | --- | --- | --- | --- |
| ball | +0,0543 ± 0,0139 | -0,0146 ± 0,0108 | +0,0128 ± 0,0138 | -0,0013 ± 0,0110 |
| gawang | +0,0072 ± 0,0019 | -0,0103 ± 0,0172 | +0,0010 ± 0,0053 | -0,0060 ± 0,0083 |
| robot | +0,0277 ± 0,0014 | +0,0095 ± 0,0134 | +0,0000 ± 0,0122 | +0,0051 ± 0,0104 |

## Interpretasi dan langkah berikutnya

KD Hybrid full menaikkan mAP50–95 VAL terhadap kontrol supervised pada ketiga seed. Rerata selisihnya `+0,0297 ± 0,0047`. Pada confidence 0,25, F1 makro hampir sama tetapi sedikit lebih rendah (Δ `-0,0008 ± 0,0006`); precision rata-rata turun dan recall rata-rata naik. Jadi hasil VAL mendukung KD Hybrid full untuk dipertimbangkan pada evaluasi TEST terkunci, tetapi tidak menunjukkan peningkatan F1 pada operating point tersebut.

Simpangan baku dari tiga seed bersifat deskriptif dengan `n=3`; ini bukan uji signifikansi. Metrik VAL mengukur dataset Advance Vision pada level gambar, bukan kamera atau runtime OP3. Checkpoint deployment OP3 tidak berubah dari hasil ini. Evaluasi TEST terkunci adalah langkah berikutnya setelah pemilihan metode; jangan menggunakannya untuk mengubah objective atau threshold.

## Artefak sumber

- Evaluasi JSON: [`runs/val_ablation/hybrid_20261022_multiseed/`](../../runs/val_ablation/hybrid_20261022_multiseed/)
- Tabel hasil keseluruhan: [T04](../tabel/T04_ablasi_kd_val.md)
- Perbandingan berpasangan: [T28](../tabel/T28_selisih_kd_hybrid_val.md)
- Perbandingan per kelas: [T29](../tabel/T29_kd_hybrid_val_per_kelas.md)
- Skrip evaluasi: [`evaluate_val_ablation.py`](../../scripts/evaluate_val_ablation.py)
- Skrip pembaruan tabel: [`build_kd_hybrid_multiseed_val_tables.py`](../../scripts/build_kd_hybrid_multiseed_val_tables.py)
