# T04. ablasi KD pada VAL

Status: Lengkap untuk pilot satu seed; `pure_v4` tiga seed dan `pure_weighted` seed 42.

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

Perubahan pilot terhadap `pure_v4` seed 42: mAP50–95 -0.0919, F1 pada confidence 0,25 -0.7773 (skala 0–1).
Recall `gawang` berubah +0.0258, tetapi precision makro berubah -0.7426 pada confidence yang sama. Menurut kriteria mAP50–95 VAL yang ditetapkan sebelum pilot, `pure_v4` tetap model utama.
Perbandingan satu seed ini bersifat eksploratif. Angka ini adalah akurasi VAL
Advance Vision, bukan akurasi kamera OP3. Model utama tiga seed dan hasil
TEST historis tidak diubah oleh pilot ini.
