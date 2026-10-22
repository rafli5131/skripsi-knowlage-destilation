# T31. KD Hybrid full vs supervised pada TEST per kelas

Split TEST resmi: ball 83 anotasi, gawang 532, robot 119. Metrik AP dan operating point mengikuti protokol TEST yang dikunci.

| kelas | seed | metrik | Hybrid full | Supervised | Δ Hybrid − supervised |
| --- | --- | --- | --- | --- | --- |
| ball | 42 | mAP50 | 0,9793 | 0,9813 | -0,0019 |
| ball | 42 | mAP50-95 | 0,8749 | 0,8222 | +0,0527 |
| ball | 42 | precision | 0,9419 | 0,9524 | -0,0105 |
| ball | 42 | recall | 0,9759 | 0,9639 | +0,0120 |
| ball | 42 | F1 | 0,9586 | 0,9581 | +0,0005 |
| ball | 1337 | mAP50 | 0,9749 | 0,9736 | +0,0013 |
| ball | 1337 | mAP50-95 | 0,8698 | 0,8287 | +0,0412 |
| ball | 1337 | precision | 0,9419 | 0,9412 | +0,0007 |
| ball | 1337 | recall | 0,9759 | 0,9639 | +0,0120 |
| ball | 1337 | F1 | 0,9586 | 0,9524 | +0,0062 |
| ball | 2025 | mAP50 | 0,9786 | 0,9730 | +0,0055 |
| ball | 2025 | mAP50-95 | 0,8814 | 0,8214 | +0,0600 |
| ball | 2025 | precision | 0,9310 | 0,9310 | 0,0000 |
| ball | 2025 | recall | 0,9759 | 0,9759 | 0,0000 |
| ball | 2025 | F1 | 0,9529 | 0,9529 | 0,0000 |
| ball | rerata ± SD (n=3) | mAP50 | 0,9776 ± 0,0024 | 0,9760 ± 0,0046 | +0,0016 ± 0,0037 |
| ball | rerata ± SD (n=3) | mAP50-95 | 0,8754 ± 0,0058 | 0,8241 ± 0,0040 | +0,0513 ± 0,0095 |
| ball | rerata ± SD (n=3) | precision | 0,9383 ± 0,0063 | 0,9415 ± 0,0107 | -0,0033 ± 0,0063 |
| ball | rerata ± SD (n=3) | recall | 0,9759 ± 0,0000 | 0,9679 ± 0,0070 | +0,0080 ± 0,0070 |
| ball | rerata ± SD (n=3) | F1 | 0,9567 ± 0,0033 | 0,9545 ± 0,0031 | +0,0022 ± 0,0034 |
| gawang | 42 | mAP50 | 0,9228 | 0,9186 | +0,0042 |
| gawang | 42 | mAP50-95 | 0,5599 | 0,5482 | +0,0117 |
| gawang | 42 | precision | 0,7262 | 0,7444 | -0,0182 |
| gawang | 42 | recall | 0,9323 | 0,9417 | -0,0094 |
| gawang | 42 | F1 | 0,8165 | 0,8315 | -0,0151 |
| gawang | 1337 | mAP50 | 0,9208 | 0,9255 | -0,0047 |
| gawang | 1337 | mAP50-95 | 0,5547 | 0,5488 | +0,0059 |
| gawang | 1337 | precision | 0,7241 | 0,7538 | -0,0297 |
| gawang | 1337 | recall | 0,9323 | 0,9380 | -0,0056 |
| gawang | 1337 | F1 | 0,8151 | 0,8358 | -0,0207 |
| gawang | 2025 | mAP50 | 0,9219 | 0,9358 | -0,0139 |
| gawang | 2025 | mAP50-95 | 0,5559 | 0,5488 | +0,0071 |
| gawang | 2025 | precision | 0,7313 | 0,7610 | -0,0297 |
| gawang | 2025 | recall | 0,9361 | 0,9455 | -0,0094 |
| gawang | 2025 | F1 | 0,8211 | 0,8433 | -0,0221 |
| gawang | rerata ± SD (n=3) | mAP50 | 0,9218 ± 0,0010 | 0,9266 ± 0,0086 | -0,0048 ± 0,0090 |
| gawang | rerata ± SD (n=3) | mAP50-95 | 0,5569 ± 0,0027 | 0,5486 ± 0,0004 | +0,0083 ± 0,0031 |
| gawang | rerata ± SD (n=3) | precision | 0,7272 ± 0,0037 | 0,7531 ± 0,0083 | -0,0259 ± 0,0066 |
| gawang | rerata ± SD (n=3) | recall | 0,9336 ± 0,0022 | 0,9417 ± 0,0038 | -0,0081 ± 0,0022 |
| gawang | rerata ± SD (n=3) | F1 | 0,8176 ± 0,0031 | 0,8369 ± 0,0059 | -0,0193 ± 0,0037 |
| robot | 42 | mAP50 | 0,9755 | 0,9755 | +0,0000 |
| robot | 42 | mAP50-95 | 0,7993 | 0,7904 | +0,0089 |
| robot | 42 | precision | 0,8815 | 0,8750 | +0,0065 |
| robot | 42 | recall | 1,0000 | 1,0000 | 0,0000 |
| robot | 42 | F1 | 0,9370 | 0,9333 | +0,0037 |
| robot | 1337 | mAP50 | 0,9775 | 0,9744 | +0,0031 |
| robot | 1337 | mAP50-95 | 0,8159 | 0,8020 | +0,0139 |
| robot | 1337 | precision | 0,8881 | 0,8947 | -0,0067 |
| robot | 1337 | recall | 1,0000 | 1,0000 | 0,0000 |
| robot | 1337 | F1 | 0,9407 | 0,9444 | -0,0037 |
| robot | 2025 | mAP50 | 0,9734 | 0,9830 | -0,0096 |
| robot | 2025 | mAP50-95 | 0,8102 | 0,7922 | +0,0181 |
| robot | 2025 | precision | 0,9015 | 0,8947 | +0,0068 |
| robot | 2025 | recall | 1,0000 | 1,0000 | 0,0000 |
| robot | 2025 | F1 | 0,9482 | 0,9444 | +0,0038 |
| robot | rerata ± SD (n=3) | mAP50 | 0,9755 ± 0,0021 | 0,9776 ± 0,0047 | -0,0022 ± 0,0066 |
| robot | rerata ± SD (n=3) | mAP50-95 | 0,8085 ± 0,0084 | 0,7949 ± 0,0062 | +0,0136 ± 0,0046 |
| robot | rerata ± SD (n=3) | precision | 0,8904 ± 0,0102 | 0,8882 ± 0,0114 | +0,0022 ± 0,0077 |
| robot | rerata ± SD (n=3) | recall | 1,0000 ± 0,0000 | 1,0000 ± 0,0000 | 0,0000 ± 0,0000 |
| robot | rerata ± SD (n=3) | F1 | 0,9420 ± 0,0057 | 0,9407 ± 0,0064 | +0,0012 ± 0,0043 |

CSV menyimpan angka lebih presisi dan interval bootstrap 95% per checkpoint; SD pada baris ringkasan adalah variasi antar tiga seed, bukan interval bootstrap.
