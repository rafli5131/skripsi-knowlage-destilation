# T28. KD Hybrid full vs supervised pada VAL

Perbandingan berpasangan pada split VAL resmi yang sama. Nilai seed adalah checkpoint `best.pt`; baris ringkasan menunjukkan rerata ± simpangan baku sampel tiga seed. Δ = Hybrid full − supervised.

| seed | metrik | KD Hybrid full | Student supervised | Δ Hybrid − supervised |
| --- | --- | --- | --- | --- |
| 42 | mAP50 | 0,9725 | 0,9733 | -0,0008 |
| 42 | mAP50-95 | 0,7488 | 0,7189 | +0,0298 |
| 42 | precision@0.25 | 0,8721 | 0,8829 | -0,0108 |
| 42 | recall@0.25 | 0,9780 | 0,9679 | +0,0101 |
| 42 | F1@0.25 | 0,9220 | 0,9235 | -0,0014 |
| 1337 | mAP50 | 0,9734 | 0,9674 | +0,0060 |
| 1337 | mAP50-95 | 0,7523 | 0,7179 | +0,0343 |
| 1337 | precision@0.25 | 0,8686 | 0,8765 | -0,0079 |
| 1337 | recall@0.25 | 0,9735 | 0,9649 | +0,0087 |
| 1337 | F1@0.25 | 0,9181 | 0,9186 | -0,0005 |
| 2025 | mAP50 | 0,9741 | 0,9706 | +0,0035 |
| 2025 | mAP50-95 | 0,7505 | 0,7255 | +0,0250 |
| 2025 | precision@0.25 | 0,8810 | 0,8778 | +0,0033 |
| 2025 | recall@0.25 | 0,9656 | 0,9706 | -0,0050 |
| 2025 | F1@0.25 | 0,9214 | 0,9218 | -0,0004 |
| mean ± SD (n=3) | mAP50 | 0,9733 ± 0,0008 | 0,9704 ± 0,0030 | +0,0029 ± 0,0035 |
| mean ± SD (n=3) | mAP50-95 | 0,7505 ± 0,0018 | 0,7208 ± 0,0041 | +0,0297 ± 0,0047 |
| mean ± SD (n=3) | precision@0.25 | 0,8739 ± 0,0064 | 0,8790 ± 0,0034 | -0,0051 ± 0,0074 |
| mean ± SD (n=3) | recall@0.25 | 0,9724 ± 0,0063 | 0,9678 ± 0,0028 | +0,0046 ± 0,0083 |
| mean ± SD (n=3) | F1@0.25 | 0,9205 ± 0,0021 | 0,9213 ± 0,0025 | -0,0008 ± 0,0006 |
