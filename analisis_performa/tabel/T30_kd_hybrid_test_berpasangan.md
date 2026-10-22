# T30. KD Hybrid full vs supervised pada TEST

Split TEST resmi 592 gambar. Semua tiga seed berpasangan; Δ = Hybrid full − supervised. Protokol dan checkpoint dikunci berdasarkan VAL sebelum evaluasi Hybrid.

| seed | metrik | Hybrid full | Supervised | Δ Hybrid − supervised |
| --- | --- | --- | --- | --- |
| 42 | mAP50 | 0,9592 | 0,9585 | +0,0008 |
| 42 | mAP50-95 | 0,7447 | 0,7203 | +0,0244 |
| 42 | precision | 0,8498 | 0,8573 | -0,0074 |
| 42 | recall | 0,9694 | 0,9685 | +0,0009 |
| 42 | F1 | 0,9057 | 0,9095 | -0,0038 |
| 1337 | mAP50 | 0,9577 | 0,9578 | -0,0001 |
| 1337 | mAP50-95 | 0,7468 | 0,7265 | +0,0203 |
| 1337 | precision | 0,8513 | 0,8632 | -0,0119 |
| 1337 | recall | 0,9694 | 0,9673 | +0,0021 |
| 1337 | F1 | 0,9065 | 0,9123 | -0,0058 |
| 2025 | mAP50 | 0,9579 | 0,9639 | -0,0060 |
| 2025 | mAP50-95 | 0,7492 | 0,7208 | +0,0284 |
| 2025 | precision | 0,8546 | 0,8622 | -0,0076 |
| 2025 | recall | 0,9707 | 0,9738 | -0,0031 |
| 2025 | F1 | 0,9089 | 0,9146 | -0,0057 |
| rerata ± SD (n=3) | mAP50 | 0,9583 ± 0,0008 | 0,9601 ± 0,0034 | -0,0018 ± 0,0037 |
| rerata ± SD (n=3) | mAP50-95 | 0,7469 ± 0,0022 | 0,7225 ± 0,0035 | +0,0244 ± 0,0040 |
| rerata ± SD (n=3) | precision | 0,8519 ± 0,0024 | 0,8609 ± 0,0032 | -0,0090 ± 0,0025 |
| rerata ± SD (n=3) | recall | 0,9698 ± 0,0007 | 0,9699 ± 0,0035 | -0,0000 ± 0,0028 |
| rerata ± SD (n=3) | F1 | 0,9071 ± 0,0017 | 0,9121 ± 0,0026 | -0,0051 ± 0,0011 |

CSV menyimpan angka lebih presisi dan interval bootstrap 95% per checkpoint; SD pada baris ringkasan adalah variasi antar tiga seed, bukan interval bootstrap.
