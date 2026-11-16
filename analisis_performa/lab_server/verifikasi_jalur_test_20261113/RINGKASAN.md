# Verifikasi jalur inferensi pada TEST

Dijalankan 2026-11-13T10:01:58+00:00 UTC pada `labkc-l40-debian`, perangkat `cpu`, Ultralytics 8.4.130, torch 2.4.1+cu121. Commit repo: `f9647ae73907d113b8c4de3937c9ac6795c7f856`.

Angka **resmi** berasal dari evaluator TEST terkunci (`model.val`, batch 16, rect, GPU). Angka **predict** memakai `model.predict` per gambar dengan ambang yang sama (floor 0,001, NMS IoU 0,7). Angka **robot** memakai `model.predict` dengan confidence 0,25 dan NMS IoU 0,45 seperti runtime OP3. P/R/F1 memakai confidence > 0,25, pencocokan sekelas IoU ≥ 0,5, dan rerata makro; F1 = 2PR/(P+R).

## Rerata per kelompok

| Kelompok | n | mAP50-95 resmi | mAP50-95 predict | Δ | F1 resmi | F1 predict | Δ | F1 robot | Δ robot - resmi |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KD Hybrid full | 3 | 0,7469 | 0,7434 | -0,0035 | 0,9071 | 0,9090 | +0,0019 | 0,9334 | +0,0264 |
| Supervised | 3 | 0,7225 | 0,7248 | +0,0023 | 0,9121 | 0,9098 | -0,0024 | 0,9337 | +0,0216 |
| KD murni | 3 | 0,6630 | 0,6647 | +0,0016 | 0,8462 | 0,8467 | +0,0005 | 0,9203 | +0,0742 |

## Per checkpoint

| Model | mAP50-95 resmi | predict | F1 resmi | predict | robot | P robot | R robot |
|---|---:|---:|---:|---:|---:|---:|---:|
| hybrid_full_seed42 | 0,7447 | 0,7411 | 0,9057 | 0,9076 | 0,9307 | 0,9017 | 0,9616 |
| hybrid_full_seed1337 | 0,7468 | 0,7392 | 0,9065 | 0,9098 | 0,9373 | 0,9077 | 0,9688 |
| hybrid_full_seed2025 | 0,7492 | 0,7500 | 0,9089 | 0,9096 | 0,9324 | 0,9024 | 0,9644 |
| supervised_seed42 | 0,7203 | 0,7243 | 0,9095 | 0,9028 | 0,9293 | 0,8930 | 0,9688 |
| supervised_seed1337 | 0,7265 | 0,7291 | 0,9123 | 0,9153 | 0,9373 | 0,9094 | 0,9669 |
| supervised_seed2025 | 0,7208 | 0,7210 | 0,9146 | 0,9112 | 0,9345 | 0,9052 | 0,9657 |
| kd_seed42 | 0,6744 | 0,6763 | 0,8395 | 0,8484 | 0,9139 | 0,8771 | 0,9539 |
| kd_seed1337 | 0,6531 | 0,6555 | 0,8372 | 0,8398 | 0,9252 | 0,8922 | 0,9607 |
| kd_seed2025 | 0,6616 | 0,6622 | 0,8618 | 0,8517 | 0,9219 | 0,8828 | 0,9647 |

## Catatan pembacaan

- Pemanggilan NMS di `DetectionValidator.postprocess` pada versi terpasang: `non_max_suppression( preds, self.args.conf, self.args.iou, nc=0 if self.args.task == "detect" else self.nc, multi_label=True, agnostic=self.args.single_cls or self.args.agnostic_nms, max_det=self.args.max_det, end2end=self.end2end, rotated=self.args.task == "obb", )`.
- Bentuk tensor letterbox jalur predict (varian protokol_test, gabungan semua model): {'640x640': 5328}.
- Sidik jari TEST cocok seluruhnya: ya.
- Selisih resmi vs predict pada ambang yang sama menunjukkan pengaruh jalur (letterbox, NMS, batch, perangkat). Selisih robot vs resmi menambahkan pengaruh ambang runtime 0,25/0,45.
- TEST sudah dibuka pada tahap sebelumnya. Hasil ini hanya pemeriksaan konsistensi dan tidak dipakai memilih ulang model atau ambang.
