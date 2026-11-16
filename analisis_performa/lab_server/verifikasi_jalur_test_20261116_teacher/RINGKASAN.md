# Verifikasi jalur inferensi pada TEST

Dijalankan 2026-11-16T06:41:46+00:00 UTC pada `labkc-l40-debian`, perangkat `cpu`, Ultralytics 8.4.130, torch 2.4.1+cu121. Commit repo: `ade031a89d0e9d5cb088c5615e31746fd9c43a4c`.

Angka **resmi** berasal dari evaluator TEST terkunci (`model.val`, batch 16, rect, GPU). Angka **predict** memakai `model.predict` per gambar dengan ambang yang sama (floor 0,001, NMS IoU 0,7). Angka **robot** memakai `model.predict` dengan confidence 0,25 dan NMS IoU 0,45 seperti runtime OP3. P/R/F1 memakai confidence > 0,25, pencocokan sekelas IoU ≥ 0,5, dan rerata makro; F1 = 2PR/(P+R).

## Rerata per kelompok

| Kelompok | n | mAP50-95 resmi | mAP50-95 predict | Δ | F1 resmi | F1 predict | Δ | F1 robot | Δ robot - resmi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 1 | 0,7800 | 0,7791 | -0,0009 | 0,9290 | 0,9120 | -0,0170 | 0,9354 | +0,0065 |

## Per checkpoint

| Model | mAP50-95 resmi | predict | F1 resmi | predict | robot | P robot | R robot |
|---|---:|---:|---:|---:|---:|---:|---:|
| teacher_fp32 | 0,7800 | 0,7791 | 0,9290 | 0,9120 | 0,9354 | 0,9087 | 0,9637 |

## Catatan pembacaan

- Pemanggilan NMS di `DetectionValidator.postprocess` pada versi terpasang: `non_max_suppression( preds, self.args.conf, self.args.iou, nc=0 if self.args.task == "detect" else self.nc, multi_label=True, agnostic=self.args.single_cls or self.args.agnostic_nms, max_det=self.args.max_det, end2end=self.end2end, rotated=self.args.task == "obb", )`.
- Bentuk tensor letterbox jalur predict (varian protokol_test, gabungan semua model): {'640x640': 592}.
- Sidik jari TEST cocok seluruhnya: ya.
- Selisih resmi vs predict pada ambang yang sama menunjukkan pengaruh jalur (letterbox, NMS, batch, perangkat). Selisih robot vs resmi menambahkan pengaruh ambang runtime 0,25/0,45.
- TEST sudah dibuka pada tahap sebelumnya. Hasil ini hanya pemeriksaan konsistensi dan tidak dipakai memilih ulang model atau ambang.
