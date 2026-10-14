# Ringkasan Analisis Skripsi

Sumber kebenaran metrik TEST adalah manifest evaluasi locked-test; ukuran/latensi/FLOPs berasal dari benchmark FP32 batch 1 pada NVIDIA L40. Precision/recall/F1 memakai confidence tetap >0,25 dan IoU pencocokan 0,50 yang dikunci sebelum TEST; confidence floor 0,001 dipakai untuk menghitung kurva AP, dengan NMS IoU 0,7. Student KD dan supervised menggunakan arsitektur student yang sama, sehingga kontras utama di antara keduanya adalah objective training; kompresi student KD dinilai terpisah terhadap teacher. Hasil hanya mengukur split level-gambar Advance Vision dan bukan klaim deployment robot.
Jumlah parameter pada tabel dihitung dari checkpoint sebelum predictor melakukan fusi Conv-BN, dan jumlah student dicocokkan dengan manifest training. Jumlah pascafusi yang dicatat validator tersedia terpisah di `per_model.csv` sebagai diagnostik; rasio kompresi memakai jumlah parameter checkpoint.

## Hasil per model dan seed

| Model | Metode | Seed | VAL mAP50–95 | TEST P | TEST R | TEST F1 | TEST mAP50 | TEST mAP50–95 | Δ mAP50–95 vs teacher | Parameter | Size MiB | GFLOPs | Median ms | P95 ms | Speedup | Img/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| kd_seed1337 | Pure KD | 1337 | 0.6757 | 0.7404 | 0.9632 | 0.8372 | 0.9403 | 0.6531 | -0.1269 | 810,649 | 1.82 | 2.429 | 24.813 | 25.916 | 1.04× | 41.77 |
| kd_seed2025 | Pure KD | 2025 | 0.6789 | 0.7787 | 0.9648 | 0.8618 | 0.9455 | 0.6616 | -0.1184 | 810,649 | 1.82 | 2.429 | 24.923 | 26.376 | 1.03× | 41.37 |
| kd_seed42 | Pure KD | 42 | 0.6825 | 0.7451 | 0.9613 | 0.8395 | 0.9481 | 0.6744 | -0.1056 | 810,649 | 1.82 | 2.429 | 25.284 | 29.582 | 1.02× | 39.30 |
| supervised_seed1337 | Supervised student | 1337 | 0.7181 | 0.8632 | 0.9673 | 0.9123 | 0.9578 | 0.7265 | -0.0535 | 810,649 | 1.82 | 2.429 | 25.262 | 30.410 | 1.02× | 40.51 |
| supervised_seed2025 | Supervised student | 2025 | 0.7252 | 0.8622 | 0.9738 | 0.9146 | 0.9639 | 0.7208 | -0.0592 | 810,649 | 1.82 | 2.429 | 24.850 | 26.254 | 1.03× | 41.14 |
| supervised_seed42 | Supervised student | 42 | 0.7189 | 0.8573 | 0.9685 | 0.9095 | 0.9585 | 0.7203 | -0.0597 | 810,649 | 1.82 | 2.429 | 24.886 | 26.665 | 1.03× | 41.00 |
| teacher_fp32 | Teacher | — | 0.7785 | 0.8915 | 0.9697 | 0.9290 | 0.9642 | 0.7800 | 0.0000 | 2,590,425 | 5.23 | 6.502 | 25.716 | 28.686 | 1.00× | 39.60 |

## Mean dan simpangan baku antar-run

| Metode | Metrik | n | Mean | SD sampel |
| --- | --- | ---: | ---: | ---: |
| Teacher | test_mAP50 | 1 | 0.9642 | — |
| Teacher | test_mAP50_95 | 1 | 0.7800 | — |
| Teacher | test_precision | 1 | 0.8915 | — |
| Teacher | test_recall | 1 | 0.9697 | — |
| Teacher | test_F1 | 1 | 0.9290 | — |
| Teacher | parameters | 1 | 2590425.0000 | — |
| Teacher | checkpoint_size_MiB | 1 | 5.2279 | — |
| Teacher | GFLOPs | 1 | 6.5017 | — |
| Teacher | latency_median_ms | 1 | 25.7160 | — |
| Teacher | latency_p95_ms | 1 | 28.6861 | — |
| Teacher | throughput_images_s | 1 | 39.6020 | — |
| Teacher | test_mAP50_95_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | mAP50_95_retention_vs_teacher_percent | 1 | 100.0000 | — |
| Teacher | parameter_reduction_vs_teacher_percent | 1 | 0.0000 | — |
| Teacher | checkpoint_size_reduction_vs_teacher_percent | 1 | 0.0000 | — |
| Teacher | latency_speedup_vs_teacher | 1 | 1.0000 | — |
| Teacher | GFLOPs_reduction_vs_teacher_percent | 1 | 0.0000 | — |
| Teacher | test_ball_precision | 1 | 0.9647 | — |
| Teacher | test_ball_mAP50 | 1 | 0.9848 | — |
| Teacher | test_ball_mAP50_95 | 1 | 0.9131 | — |
| Teacher | test_ball_recall | 1 | 0.9880 | — |
| Teacher | test_ball_F1 | 1 | 0.9762 | — |
| Teacher | test_gawang_precision | 1 | 0.7349 | — |
| Teacher | test_gawang_mAP50 | 1 | 0.9234 | — |
| Teacher | test_gawang_mAP50_95 | 1 | 0.5684 | — |
| Teacher | test_gawang_recall | 1 | 0.9380 | — |
| Teacher | test_gawang_F1 | 1 | 0.8241 | — |
| Teacher | test_robot_precision | 1 | 0.9750 | — |
| Teacher | test_robot_mAP50 | 1 | 0.9846 | — |
| Teacher | test_robot_mAP50_95 | 1 | 0.8585 | — |
| Teacher | test_robot_recall | 1 | 0.9832 | — |
| Teacher | test_robot_F1 | 1 | 0.9791 | — |
| Teacher | test_ball_precision_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_ball_mAP50_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_ball_mAP50_95_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_ball_recall_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_ball_F1_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_gawang_precision_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_gawang_mAP50_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_gawang_mAP50_95_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_gawang_recall_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_gawang_F1_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_robot_precision_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_robot_mAP50_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_robot_mAP50_95_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_robot_recall_delta_vs_teacher | 1 | 0.0000 | — |
| Teacher | test_robot_F1_delta_vs_teacher | 1 | 0.0000 | — |
| Supervised student | test_mAP50 | 3 | 0.9601 | 0.0034 |
| Supervised student | test_mAP50_95 | 3 | 0.7225 | 0.0035 |
| Supervised student | test_precision | 3 | 0.8609 | 0.0032 |
| Supervised student | test_recall | 3 | 0.9699 | 0.0035 |
| Supervised student | test_F1 | 3 | 0.9121 | 0.0026 |
| Supervised student | parameters | 3 | 810649.0000 | 0.0000 |
| Supervised student | checkpoint_size_MiB | 3 | 1.8210 | 0.0000 |
| Supervised student | GFLOPs | 3 | 2.4291 | 0.0000 |
| Supervised student | latency_median_ms | 3 | 24.9993 | 0.2286 |
| Supervised student | latency_p95_ms | 3 | 27.7765 | 2.2900 |
| Supervised student | throughput_images_s | 3 | 40.8819 | 0.3317 |
| Supervised student | test_mAP50_95_delta_vs_teacher | 3 | -0.0575 | 0.0035 |
| Supervised student | mAP50_95_retention_vs_teacher_percent | 3 | 92.6327 | 0.4428 |
| Supervised student | parameter_reduction_vs_teacher_percent | 3 | 68.7059 | 0.0000 |
| Supervised student | checkpoint_size_reduction_vs_teacher_percent | 3 | 65.1674 | 0.0007 |
| Supervised student | latency_speedup_vs_teacher | 3 | 1.0287 | 0.0094 |
| Supervised student | GFLOPs_reduction_vs_teacher_percent | 3 | 62.6387 | 0.0000 |
| Supervised student | test_ball_precision | 3 | 0.9415 | 0.0107 |
| Supervised student | test_ball_mAP50 | 3 | 0.9760 | 0.0046 |
| Supervised student | test_ball_mAP50_95 | 3 | 0.8241 | 0.0040 |
| Supervised student | test_ball_recall | 3 | 0.9679 | 0.0070 |
| Supervised student | test_ball_F1 | 3 | 0.9545 | 0.0031 |
| Supervised student | test_gawang_precision | 3 | 0.7531 | 0.0083 |
| Supervised student | test_gawang_mAP50 | 3 | 0.9266 | 0.0086 |
| Supervised student | test_gawang_mAP50_95 | 3 | 0.5486 | 0.0004 |
| Supervised student | test_gawang_recall | 3 | 0.9417 | 0.0038 |
| Supervised student | test_gawang_F1 | 3 | 0.8369 | 0.0059 |
| Supervised student | test_robot_precision | 3 | 0.8882 | 0.0114 |
| Supervised student | test_robot_mAP50 | 3 | 0.9776 | 0.0047 |
| Supervised student | test_robot_mAP50_95 | 3 | 0.7949 | 0.0062 |
| Supervised student | test_robot_recall | 3 | 1.0000 | 0.0000 |
| Supervised student | test_robot_F1 | 3 | 0.9407 | 0.0064 |
| Supervised student | test_ball_precision_delta_vs_teacher | 3 | -0.0232 | 0.0107 |
| Supervised student | test_ball_mAP50_delta_vs_teacher | 3 | -0.0088 | 0.0046 |
| Supervised student | test_ball_mAP50_95_delta_vs_teacher | 3 | -0.0890 | 0.0040 |
| Supervised student | test_ball_recall_delta_vs_teacher | 3 | -0.0201 | 0.0070 |
| Supervised student | test_ball_F1_delta_vs_teacher | 3 | -0.0217 | 0.0031 |
| Supervised student | test_gawang_precision_delta_vs_teacher | 3 | 0.0182 | 0.0083 |
| Supervised student | test_gawang_mAP50_delta_vs_teacher | 3 | 0.0032 | 0.0086 |
| Supervised student | test_gawang_mAP50_95_delta_vs_teacher | 3 | -0.0198 | 0.0004 |
| Supervised student | test_gawang_recall_delta_vs_teacher | 3 | 0.0038 | 0.0038 |
| Supervised student | test_gawang_F1_delta_vs_teacher | 3 | 0.0128 | 0.0059 |
| Supervised student | test_robot_precision_delta_vs_teacher | 3 | -0.0868 | 0.0114 |
| Supervised student | test_robot_mAP50_delta_vs_teacher | 3 | -0.0069 | 0.0047 |
| Supervised student | test_robot_mAP50_95_delta_vs_teacher | 3 | -0.0636 | 0.0062 |
| Supervised student | test_robot_recall_delta_vs_teacher | 3 | 0.0168 | 0.0000 |
| Supervised student | test_robot_F1_delta_vs_teacher | 3 | -0.0383 | 0.0064 |
| Pure KD | test_mAP50 | 3 | 0.9446 | 0.0040 |
| Pure KD | test_mAP50_95 | 3 | 0.6630 | 0.0108 |
| Pure KD | test_precision | 3 | 0.7547 | 0.0209 |
| Pure KD | test_recall | 3 | 0.9631 | 0.0017 |
| Pure KD | test_F1 | 3 | 0.8462 | 0.0136 |
| Pure KD | parameters | 3 | 810649.0000 | 0.0000 |
| Pure KD | checkpoint_size_MiB | 3 | 1.8191 | 0.0000 |
| Pure KD | GFLOPs | 3 | 2.4291 | 0.0000 |
| Pure KD | latency_median_ms | 3 | 25.0065 | 0.2463 |
| Pure KD | latency_p95_ms | 3 | 27.2915 | 1.9972 |
| Pure KD | throughput_images_s | 3 | 40.8113 | 1.3282 |
| Pure KD | test_mAP50_95_delta_vs_teacher | 3 | -0.1169 | 0.0108 |
| Pure KD | mAP50_95_retention_vs_teacher_percent | 3 | 85.0069 | 1.3786 |
| Pure KD | parameter_reduction_vs_teacher_percent | 3 | 68.7059 | 0.0000 |
| Pure KD | checkpoint_size_reduction_vs_teacher_percent | 3 | 65.2047 | 0.0007 |
| Pure KD | latency_speedup_vs_teacher | 3 | 1.0284 | 0.0101 |
| Pure KD | GFLOPs_reduction_vs_teacher_percent | 3 | 62.6387 | 0.0000 |
| Pure KD | test_ball_precision | 3 | 0.7447 | 0.0431 |
| Pure KD | test_ball_mAP50 | 3 | 0.9560 | 0.0084 |
| Pure KD | test_ball_mAP50_95 | 3 | 0.7302 | 0.0190 |
| Pure KD | test_ball_recall | 3 | 0.9639 | 0.0000 |
| Pure KD | test_ball_F1 | 3 | 0.8397 | 0.0272 |
| Pure KD | test_gawang_precision | 3 | 0.7371 | 0.0054 |
| Pure KD | test_gawang_mAP50 | 3 | 0.9139 | 0.0034 |
| Pure KD | test_gawang_mAP50_95 | 3 | 0.5382 | 0.0041 |
| Pure KD | test_gawang_recall | 3 | 0.9311 | 0.0029 |
| Pure KD | test_gawang_F1 | 3 | 0.8228 | 0.0023 |
| Pure KD | test_robot_precision | 3 | 0.7824 | 0.0241 |
| Pure KD | test_robot_mAP50 | 3 | 0.9640 | 0.0060 |
| Pure KD | test_robot_mAP50_95 | 3 | 0.7207 | 0.0151 |
| Pure KD | test_robot_recall | 3 | 0.9944 | 0.0049 |
| Pure KD | test_robot_F1 | 3 | 0.8756 | 0.0167 |
| Pure KD | test_ball_precision_delta_vs_teacher | 3 | -0.2200 | 0.0431 |
| Pure KD | test_ball_mAP50_delta_vs_teacher | 3 | -0.0288 | 0.0084 |
| Pure KD | test_ball_mAP50_95_delta_vs_teacher | 3 | -0.1828 | 0.0190 |
| Pure KD | test_ball_recall_delta_vs_teacher | 3 | -0.0241 | 0.0000 |
| Pure KD | test_ball_F1_delta_vs_teacher | 3 | -0.1364 | 0.0272 |
| Pure KD | test_gawang_precision_delta_vs_teacher | 3 | 0.0022 | 0.0054 |
| Pure KD | test_gawang_mAP50_delta_vs_teacher | 3 | -0.0095 | 0.0034 |
| Pure KD | test_gawang_mAP50_95_delta_vs_teacher | 3 | -0.0302 | 0.0041 |
| Pure KD | test_gawang_recall_delta_vs_teacher | 3 | -0.0069 | 0.0029 |
| Pure KD | test_gawang_F1_delta_vs_teacher | 3 | -0.0013 | 0.0023 |
| Pure KD | test_robot_precision_delta_vs_teacher | 3 | -0.1926 | 0.0241 |
| Pure KD | test_robot_mAP50_delta_vs_teacher | 3 | -0.0205 | 0.0060 |
| Pure KD | test_robot_mAP50_95_delta_vs_teacher | 3 | -0.1378 | 0.0151 |
| Pure KD | test_robot_recall_delta_vs_teacher | 3 | 0.0112 | 0.0049 |
| Pure KD | test_robot_F1_delta_vs_teacher | 3 | -0.1034 | 0.0167 |

## Dampak metrik per kelas relatif terhadap teacher

Nilai negatif menunjukkan student berada di bawah teacher untuk metrik tersebut; nilai positif menunjukkan student berada di atas teacher pada split TEST level-gambar.

| Metode student | Kelas | Metrik | n | Mean delta | SD sampel |
| --- | --- | --- | ---: | ---: | ---: |
| Supervised student | ball | precision | 3 | -0.0232 | 0.0107 |
| Supervised student | ball | mAP50 | 3 | -0.0088 | 0.0046 |
| Supervised student | ball | mAP50_95 | 3 | -0.0890 | 0.0040 |
| Supervised student | ball | recall | 3 | -0.0201 | 0.0070 |
| Supervised student | ball | F1 | 3 | -0.0217 | 0.0031 |
| Supervised student | gawang | precision | 3 | 0.0182 | 0.0083 |
| Supervised student | gawang | mAP50 | 3 | 0.0032 | 0.0086 |
| Supervised student | gawang | mAP50_95 | 3 | -0.0198 | 0.0004 |
| Supervised student | gawang | recall | 3 | 0.0038 | 0.0038 |
| Supervised student | gawang | F1 | 3 | 0.0128 | 0.0059 |
| Supervised student | robot | precision | 3 | -0.0868 | 0.0114 |
| Supervised student | robot | mAP50 | 3 | -0.0069 | 0.0047 |
| Supervised student | robot | mAP50_95 | 3 | -0.0636 | 0.0062 |
| Supervised student | robot | recall | 3 | 0.0168 | 0.0000 |
| Supervised student | robot | F1 | 3 | -0.0383 | 0.0064 |
| Pure KD | ball | precision | 3 | -0.2200 | 0.0431 |
| Pure KD | ball | mAP50 | 3 | -0.0288 | 0.0084 |
| Pure KD | ball | mAP50_95 | 3 | -0.1828 | 0.0190 |
| Pure KD | ball | recall | 3 | -0.0241 | 0.0000 |
| Pure KD | ball | F1 | 3 | -0.1364 | 0.0272 |
| Pure KD | gawang | precision | 3 | 0.0022 | 0.0054 |
| Pure KD | gawang | mAP50 | 3 | -0.0095 | 0.0034 |
| Pure KD | gawang | mAP50_95 | 3 | -0.0302 | 0.0041 |
| Pure KD | gawang | recall | 3 | -0.0069 | 0.0029 |
| Pure KD | gawang | F1 | 3 | -0.0013 | 0.0023 |
| Pure KD | robot | precision | 3 | -0.1926 | 0.0241 |
| Pure KD | robot | mAP50 | 3 | -0.0205 | 0.0060 |
| Pure KD | robot | mAP50_95 | 3 | -0.1378 | 0.0151 |
| Pure KD | robot | recall | 3 | 0.0112 | 0.0049 |
| Pure KD | robot | F1 | 3 | -0.1034 | 0.0167 |

## Selisih berpasangan: pure KD minus supervised

Kontras ini membandingkan objective pada arsitektur student yang sama. Mean dan SD selisih tiga pasangan seed bersifat deskriptif dan bukan uji signifikansi formal; seluruh pasangan seed ditampilkan.

| Metrik TEST | Pasangan seed | Mean selisih | SD sampel |
| --- | ---: | ---: | ---: |
| test_mAP50 | 3 | -0.0154 | 0.0044 |
| test_mAP50_95 | 3 | -0.0595 | 0.0138 |
| test_precision | 3 | -0.1062 | 0.0203 |
| test_recall | 3 | -0.0068 | 0.0025 |
| test_F1 | 3 | -0.0660 | 0.0116 |
| test_ball_precision | 3 | -0.1969 | 0.0535 |
| test_ball_mAP50 | 3 | -0.0200 | 0.0053 |
| test_ball_mAP50_95 | 3 | -0.0939 | 0.0218 |
| test_ball_recall | 3 | -0.0040 | 0.0070 |
| test_ball_F1 | 3 | -0.1147 | 0.0294 |
| test_gawang_precision | 3 | -0.0159 | 0.0105 |
| test_gawang_mAP50 | 3 | -0.0128 | 0.0120 |
| test_gawang_mAP50_95 | 3 | -0.0104 | 0.0042 |
| test_gawang_recall | 3 | -0.0107 | 0.0060 |
| test_gawang_F1 | 3 | -0.0141 | 0.0059 |
| test_robot_precision | 3 | -0.1058 | 0.0282 |
| test_robot_mAP50 | 3 | -0.0136 | 0.0022 |
| test_robot_mAP50_95 | 3 | -0.0742 | 0.0214 |
| test_robot_recall | 3 | -0.0056 | 0.0049 |
| test_robot_F1 | 3 | -0.0651 | 0.0184 |

## Interval kepercayaan bootstrap 95% pada TEST

Interval dihitung dengan bootstrap nonparametrik pada tingkat gambar (592 gambar, sampling dengan pengembalian), 1.000 replikasi, seed 20261009, dan persentil 2,5–97,5. Interval bersyarat pada checkpoint yang diuji: interval menggambarkan variasi sampling gambar dan tidak mencakup variasi akibat mengulang training atau mengganti seed. Precision/recall/F1 memakai confidence tetap >0,25 dan IoU pencocokan 0,50 pada setiap replikasi; confidence threshold tidak dioptimalkan pada TEST. Untuk interval keseluruhan, hanya replikasi yang memuat ketiga kelas digunakan agar penyebut macro tetap tiga. Replikasi tanpa objek pada suatu kelas tidak berkontribusi pada interval kelas tersebut. Jumlah replikasi valid dicantumkan untuk setiap interval.

| Model | Cakupan | Metrik | Batas bawah | Batas atas | Replikasi valid |
| --- | --- | --- | ---: | ---: | ---: |
| kd_seed1337 | keseluruhan | precision | 0.7034 | 0.7877 | 1000 |
| kd_seed1337 | keseluruhan | recall | 0.9467 | 0.9783 | 1000 |
| kd_seed1337 | keseluruhan | F1 | 0.8119 | 0.8682 | 1000 |
| kd_seed1337 | keseluruhan | mAP50 | 0.9239 | 0.9569 | 1000 |
| kd_seed1337 | keseluruhan | mAP50–95 | 0.6343 | 0.6834 | 1000 |
| kd_seed1337 | ball | precision | 0.6565 | 0.8176 | 1000 |
| kd_seed1337 | ball | recall | 0.9204 | 1.0000 | 1000 |
| kd_seed1337 | ball | F1 | 0.7805 | 0.8842 | 1000 |
| kd_seed1337 | ball | mAP50 | 0.9074 | 0.9782 | 1000 |
| kd_seed1337 | ball | mAP50–95 | 0.6717 | 0.7657 | 1000 |
| kd_seed1337 | gawang | precision | 0.7045 | 0.7595 | 1000 |
| kd_seed1337 | gawang | recall | 0.9103 | 0.9547 | 1000 |
| kd_seed1337 | gawang | F1 | 0.8000 | 0.8427 | 1000 |
| kd_seed1337 | gawang | mAP50 | 0.8916 | 0.9379 | 1000 |
| kd_seed1337 | gawang | mAP50–95 | 0.5174 | 0.5702 | 1000 |
| kd_seed1337 | robot | precision | 0.6957 | 0.8393 | 1000 |
| kd_seed1337 | robot | recall | 0.9746 | 1.0000 | 1000 |
| kd_seed1337 | robot | F1 | 0.8193 | 0.9091 | 1000 |
| kd_seed1337 | robot | mAP50 | 0.9335 | 0.9809 | 1000 |
| kd_seed1337 | robot | mAP50–95 | 0.6672 | 0.7548 | 1000 |
| kd_seed2025 | keseluruhan | precision | 0.7389 | 0.8238 | 1000 |
| kd_seed2025 | keseluruhan | recall | 0.9498 | 0.9782 | 1000 |
| kd_seed2025 | keseluruhan | F1 | 0.8357 | 0.8899 | 1000 |
| kd_seed2025 | keseluruhan | mAP50 | 0.9285 | 0.9617 | 1000 |
| kd_seed2025 | keseluruhan | mAP50–95 | 0.6362 | 0.6916 | 1000 |
| kd_seed2025 | ball | precision | 0.7260 | 0.8640 | 1000 |
| kd_seed2025 | ball | recall | 0.9204 | 1.0000 | 1000 |
| kd_seed2025 | ball | F1 | 0.8241 | 0.9128 | 1000 |
| kd_seed2025 | ball | mAP50 | 0.9168 | 0.9839 | 1000 |
| kd_seed2025 | ball | mAP50–95 | 0.6732 | 0.7736 | 1000 |
| kd_seed2025 | gawang | precision | 0.7127 | 0.7651 | 1000 |
| kd_seed2025 | gawang | recall | 0.9042 | 0.9516 | 1000 |
| kd_seed2025 | gawang | F1 | 0.8026 | 0.8446 | 1000 |
| kd_seed2025 | gawang | mAP50 | 0.8845 | 0.9358 | 1000 |
| kd_seed2025 | gawang | mAP50–95 | 0.5086 | 0.5618 | 1000 |
| kd_seed2025 | robot | precision | 0.7265 | 0.8936 | 1000 |
| kd_seed2025 | robot | recall | 1.0000 | 1.0000 | 1000 |
| kd_seed2025 | robot | F1 | 0.8416 | 0.9438 | 1000 |
| kd_seed2025 | robot | mAP50 | 0.9444 | 0.9937 | 1000 |
| kd_seed2025 | robot | mAP50–95 | 0.6841 | 0.7756 | 1000 |
| kd_seed42 | keseluruhan | precision | 0.7074 | 0.7894 | 1000 |
| kd_seed42 | keseluruhan | recall | 0.9452 | 0.9762 | 1000 |
| kd_seed42 | keseluruhan | F1 | 0.8148 | 0.8677 | 1000 |
| kd_seed42 | keseluruhan | mAP50 | 0.9318 | 0.9642 | 1000 |
| kd_seed42 | keseluruhan | mAP50–95 | 0.6553 | 0.7005 | 1000 |
| kd_seed42 | ball | precision | 0.6339 | 0.7869 | 1000 |
| kd_seed42 | ball | recall | 0.9204 | 1.0000 | 1000 |
| kd_seed42 | ball | F1 | 0.7633 | 0.8671 | 1000 |
| kd_seed42 | ball | mAP50 | 0.9279 | 0.9889 | 1000 |
| kd_seed42 | ball | mAP50–95 | 0.7086 | 0.7946 | 1000 |
| kd_seed42 | gawang | precision | 0.7143 | 0.7672 | 1000 |
| kd_seed42 | gawang | recall | 0.9026 | 0.9517 | 1000 |
| kd_seed42 | gawang | F1 | 0.8033 | 0.8453 | 1000 |
| kd_seed42 | gawang | mAP50 | 0.8923 | 0.9400 | 1000 |
| kd_seed42 | gawang | mAP50–95 | 0.5149 | 0.5686 | 1000 |
| kd_seed42 | robot | precision | 0.7160 | 0.8750 | 1000 |
| kd_seed42 | robot | recall | 0.9747 | 1.0000 | 1000 |
| kd_seed42 | robot | F1 | 0.8293 | 0.9318 | 1000 |
| kd_seed42 | robot | mAP50 | 0.9332 | 0.9900 | 1000 |
| kd_seed42 | robot | mAP50–95 | 0.6931 | 0.7768 | 1000 |
| supervised_seed1337 | keseluruhan | precision | 0.8434 | 0.8872 | 1000 |
| supervised_seed1337 | keseluruhan | recall | 0.9521 | 0.9808 | 1000 |
| supervised_seed1337 | keseluruhan | F1 | 0.8981 | 0.9273 | 1000 |
| supervised_seed1337 | keseluruhan | mAP50 | 0.9436 | 0.9722 | 1000 |
| supervised_seed1337 | keseluruhan | mAP50–95 | 0.7081 | 0.7493 | 1000 |
| supervised_seed1337 | ball | precision | 0.8900 | 0.9878 | 1000 |
| supervised_seed1337 | ball | recall | 0.9204 | 1.0000 | 1000 |
| supervised_seed1337 | ball | F1 | 0.9220 | 0.9823 | 1000 |
| supervised_seed1337 | ball | mAP50 | 0.9350 | 0.9950 | 1000 |
| supervised_seed1337 | ball | mAP50–95 | 0.7870 | 0.8690 | 1000 |
| supervised_seed1337 | gawang | precision | 0.7254 | 0.7827 | 1000 |
| supervised_seed1337 | gawang | recall | 0.9162 | 0.9586 | 1000 |
| supervised_seed1337 | gawang | F1 | 0.8137 | 0.8579 | 1000 |
| supervised_seed1337 | gawang | mAP50 | 0.9071 | 0.9481 | 1000 |
| supervised_seed1337 | gawang | mAP50–95 | 0.5269 | 0.5774 | 1000 |
| supervised_seed1337 | robot | precision | 0.8591 | 0.9340 | 1000 |
| supervised_seed1337 | robot | recall | 1.0000 | 1.0000 | 1000 |
| supervised_seed1337 | robot | F1 | 0.9242 | 0.9659 | 1000 |
| supervised_seed1337 | robot | mAP50 | 0.9526 | 0.9944 | 1000 |
| supervised_seed1337 | robot | mAP50–95 | 0.7686 | 0.8405 | 1000 |
| supervised_seed2025 | keseluruhan | precision | 0.8370 | 0.8873 | 1000 |
| supervised_seed2025 | keseluruhan | recall | 0.9603 | 0.9851 | 1000 |
| supervised_seed2025 | keseluruhan | F1 | 0.8993 | 0.9296 | 1000 |
| supervised_seed2025 | keseluruhan | mAP50 | 0.9494 | 0.9756 | 1000 |
| supervised_seed2025 | keseluruhan | mAP50–95 | 0.7026 | 0.7433 | 1000 |
| supervised_seed2025 | ball | precision | 0.8780 | 0.9765 | 1000 |
| supervised_seed2025 | ball | recall | 0.9390 | 1.0000 | 1000 |
| supervised_seed2025 | ball | F1 | 0.9210 | 0.9814 | 1000 |
| supervised_seed2025 | ball | mAP50 | 0.9350 | 0.9947 | 1000 |
| supervised_seed2025 | ball | mAP50–95 | 0.7801 | 0.8616 | 1000 |
| supervised_seed2025 | gawang | precision | 0.7325 | 0.7903 | 1000 |
| supervised_seed2025 | gawang | recall | 0.9246 | 0.9660 | 1000 |
| supervised_seed2025 | gawang | F1 | 0.8215 | 0.8658 | 1000 |
| supervised_seed2025 | gawang | mAP50 | 0.9167 | 0.9544 | 1000 |
| supervised_seed2025 | gawang | mAP50–95 | 0.5270 | 0.5771 | 1000 |
| supervised_seed2025 | robot | precision | 0.8526 | 0.9344 | 1000 |
| supervised_seed2025 | robot | recall | 1.0000 | 1.0000 | 1000 |
| supervised_seed2025 | robot | F1 | 0.9204 | 0.9661 | 1000 |
| supervised_seed2025 | robot | mAP50 | 0.9669 | 0.9946 | 1000 |
| supervised_seed2025 | robot | mAP50–95 | 0.7591 | 0.8302 | 1000 |
| supervised_seed42 | keseluruhan | precision | 0.8395 | 0.8795 | 1000 |
| supervised_seed42 | keseluruhan | recall | 0.9534 | 0.9818 | 1000 |
| supervised_seed42 | keseluruhan | F1 | 0.8974 | 0.9240 | 1000 |
| supervised_seed42 | keseluruhan | mAP50 | 0.9469 | 0.9714 | 1000 |
| supervised_seed42 | keseluruhan | mAP50–95 | 0.7044 | 0.7429 | 1000 |
| supervised_seed42 | ball | precision | 0.9070 | 1.0000 | 1000 |
| supervised_seed42 | ball | recall | 0.9204 | 1.0000 | 1000 |
| supervised_seed42 | ball | F1 | 0.9286 | 0.9855 | 1000 |
| supervised_seed42 | ball | mAP50 | 0.9568 | 0.9950 | 1000 |
| supervised_seed42 | ball | mAP50–95 | 0.7837 | 0.8640 | 1000 |
| supervised_seed42 | gawang | precision | 0.7173 | 0.7716 | 1000 |
| supervised_seed42 | gawang | recall | 0.9226 | 0.9613 | 1000 |
| supervised_seed42 | gawang | F1 | 0.8104 | 0.8524 | 1000 |
| supervised_seed42 | gawang | mAP50 | 0.8962 | 0.9447 | 1000 |
| supervised_seed42 | gawang | mAP50–95 | 0.5256 | 0.5762 | 1000 |
| supervised_seed42 | robot | precision | 0.8435 | 0.9151 | 1000 |
| supervised_seed42 | robot | recall | 1.0000 | 1.0000 | 1000 |
| supervised_seed42 | robot | F1 | 0.9151 | 0.9557 | 1000 |
| supervised_seed42 | robot | mAP50 | 0.9553 | 0.9939 | 1000 |
| supervised_seed42 | robot | mAP50–95 | 0.7613 | 0.8301 | 1000 |
| teacher_fp32 | keseluruhan | precision | 0.8717 | 0.9112 | 1000 |
| teacher_fp32 | keseluruhan | recall | 0.9557 | 0.9823 | 1000 |
| teacher_fp32 | keseluruhan | F1 | 0.9140 | 0.9428 | 1000 |
| teacher_fp32 | keseluruhan | mAP50 | 0.9530 | 0.9755 | 1000 |
| teacher_fp32 | keseluruhan | mAP50–95 | 0.7623 | 0.7974 | 1000 |
| teacher_fp32 | ball | precision | 0.9109 | 1.0000 | 1000 |
| teacher_fp32 | ball | recall | 0.9620 | 1.0000 | 1000 |
| teacher_fp32 | ball | F1 | 0.9398 | 1.0000 | 1000 |
| teacher_fp32 | ball | mAP50 | 0.9643 | 0.9950 | 1000 |
| teacher_fp32 | ball | mAP50–95 | 0.8855 | 0.9387 | 1000 |
| teacher_fp32 | gawang | precision | 0.7089 | 0.7628 | 1000 |
| teacher_fp32 | gawang | recall | 0.9151 | 0.9598 | 1000 |
| teacher_fp32 | gawang | F1 | 0.8029 | 0.8458 | 1000 |
| teacher_fp32 | gawang | mAP50 | 0.9013 | 0.9486 | 1000 |
| teacher_fp32 | gawang | mAP50–95 | 0.5437 | 0.5966 | 1000 |
| teacher_fp32 | robot | precision | 0.9487 | 1.0000 | 1000 |
| teacher_fp32 | robot | recall | 0.9565 | 1.0000 | 1000 |
| teacher_fp32 | robot | F1 | 0.9585 | 0.9961 | 1000 |
| teacher_fp32 | robot | mAP50 | 0.9686 | 0.9950 | 1000 |
| teacher_fp32 | robot | mAP50–95 | 0.8239 | 0.8913 | 1000 |

Semua model student terpilih melalui VAL sebelum evaluasi TEST. TEST hanya dipakai untuk pelaporan akhir; jangan gunakan tabel ini untuk mengubah konfigurasi atau memilih seed.
