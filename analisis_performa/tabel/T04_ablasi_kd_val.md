# T04. ablasi KD pada VAL

Status: Mencakup KD pure tiga seed, pilot pure_weighted seed 42, hybrid_feature seed 42, dan hybrid_full tiga seed.

Seluruh checkpoint terbaik dievaluasi ulang pada 1.213 gambar VAL resmi dengan FP32, imgsz 640,
confidence floor 0,001, dan NMS IoU 0,7. AP memakai validator Ultralytics; P/R/F1 memakai
confidence tetap >0,25 dan matching IoU 0,50, dirata-ratakan makro atas tiga kelas.
F1 keseluruhan adalah harmonic mean dari precision makro dan recall makro,
mengikuti evaluator TEST. Metrik tiap kelas ada pada
[T04 per kelas](T04_ablasi_kd_val_per_kelas.md).
Pemilihan kandidat hanya memakai VAL; TEST tidak dipakai dalam tabel ini.

| model | seed | mode | feature_weight | box_weight | class_weight | temperature | best_epoch | val_mAP50 | val_mAP50_95 | val_precision_conf025 | val_recall_conf025 | val_F1_conf025 | gawang_recall_conf025 | source_run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed42 | 42 | pure_v4 | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 90 | 0,9620 | 0,6826 | 0,7899 | 0,9623 | 0,8676 | 0,9494 | runs/val_ablation/pure_weighted_20261020/kd_seed42_val.json |
| kd_seed1337 | 1337 | pure_v4 | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 96 | 0,9509 | 0,6760 | 0,7772 | 0,9566 | 0,8576 | 0,9427 | runs/val_ablation/pure_weighted_20261020/kd_seed1337_val.json |
| kd_seed2025 | 2025 | pure_v4 | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 88 | 0,9628 | 0,6786 | 0,8160 | 0,9624 | 0,8832 | 0,9485 | runs/val_ablation/pure_weighted_20261020/kd_seed2025_val.json |
| pure_weighted_seed42 | 42 | pure_weighted | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 89 | 0,7755 | 0,5907 | 0,0473 | 0,9906 | 0,0903 | 0,9752 | runs/val_ablation/pure_weighted_20261020/pure_weighted_seed42_val.json |
| hybrid_feature_seed42 | 42 | hybrid_feature | 6,0000 | 0,0000 | 0,0000 | 2,0000 | 100 | 0,9691 | 0,7436 | 0,8658 | 0,9684 | 0,9142 | 0,9466 | runs/val_ablation/hybrid_20261022/hybrid_feature_seed42_val.json |
| hybrid_full_seed42 | 42 | hybrid_full | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 100 | 0,9725 | 0,7488 | 0,8721 | 0,9780 | 0,9220 | 0,9599 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed42_val.json |
| hybrid_full_seed1337 | 1337 | hybrid_full | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 98 | 0,9734 | 0,7523 | 0,8686 | 0,9735 | 0,9181 | 0,9532 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed1337_val.json |
| hybrid_full_seed2025 | 2025 | hybrid_full | 1,0000 | 1,0000 | 1,0000 | 2,0000 | 93 | 0,9741 | 0,7505 | 0,8810 | 0,9656 | 0,9214 | 0,9437 | runs/val_ablation/hybrid_20261022_multiseed/hybrid_full_seed2025_val.json |

Perubahan pilot `pure_weighted` terhadap `pure_v4` seed 42: mAP50–95 turun 0,0919 dan F1 pada confidence 0,25 turun 0,7773. Pilot `pure_weighted` tidak diteruskan ke seed tambahan.

KD Hybrid full dibandingkan dengan student supervised pada tiga seed berpasangan. Rerata Δ mAP50–95 VAL adalah **+0,0297 ± 0,0047**, dengan Δ positif pada seed 42, 1337, dan 2025. Pada confidence 0,25, rerata Δ precision -0,0051 ± 0,0074, Δ recall +0,0046 ± 0,0083, dan Δ F1 -0,0008 ± 0,0006. Hasil mendukung Hybrid full sebagai kandidat untuk evaluasi TEST terkunci berdasarkan mAP50–95, dengan trade-off P/R/F1 tetap dilaporkan. Ini hasil VAL Advance Vision level gambar, bukan evaluasi kamera OP3; model deployment OP3 belum diganti.

Catatan mekanisme: `pure_weighted` membobot loss kotak dan kelas pada setiap lokasi
dengan skor maksimum teacher. Pada lokasi latar dengan skor teacher mendekati nol,
kontribusi BCE kelas untuk menekan skor student juga mengecil. Penurunan precision
VAL konsisten dengan rancangan loss tersebut, bukan bukti salah implementasi;
pilot ini tidak menguji varian yang hanya membobot loss kotak.
