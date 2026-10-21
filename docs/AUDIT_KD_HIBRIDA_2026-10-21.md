# Audit persiapan KD hibrida, 21 Oktober 2026

## Lingkungan dan sumber implementasi

Interpreter: `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python` dengan Python 3.11.2, PyTorch 2.4.1+cu121, dan Ultralytics 8.4.130. GPU tersedia pada proses di luar *sandbox*: tiga NVIDIA L40. Uji asap dijalankan berurutan pada perangkat logis CUDA 0, bukan bersamaan.

Pemeriksaan langsung pada sumber versi terpasang:

| Berkas dalam venv Ultralytics 8.4.130 | Baris | Hasil pemeriksaan |
| --- | --- | --- |
| `ultralytics/nn/distill_model.py` | 207–249 | Pada latihan, `student_model.loss(batch, preds)` menghitung *loss* berlabel, kemudian distilasi fitur berbobot `dis` ditambahkan. Pada validasi, komponen KD nol dan *loss* deteksi tetap dihitung. |
| `ultralytics/nn/tasks.py` | 402–414 | `student_model.loss(batch, preds)` memakai prediksi yang diberikan; *forward* baru hanya terjadi bila `preds` kosong. |
| `ultralytics/engine/trainer.py` | 502–516 | Nama komponen log diambil dari kamus `loss_items` pada *batch* pertama. |
| `ultralytics/engine/validator.py` | 264–268 | Nilai `loss_items` pada validasi dijumlahkan *in-place*; bentuk `dis_loss` harus sama dengan saat inisialisasi. |
| `ultralytics/cfg/default.yaml` | 103–104 | `distill_model` tersedia dan nilai bawaan `dis` adalah 6,0. |

## Data dan konfigurasi

Kedua konfigurasi pilot merujuk `models/yolo11_tiny_kd.yaml` dan `configs/data_train_val.yaml`, sama dengan `configs/kd.yaml` dan `configs/supervised_baseline.yaml`. Seluruh parameter di bagian `training`, selain penulisan eksplisit `pretrained: false`, sama dengan kedua konfigurasi lama. Hash byte seluruh gambar dan label TRAIN/VAL cocok dengan `artifacts/advance_vision_dataset_fingerprint.json`; fingerprint split TRAIN `a460ec3f6b16bacde012374846e8bd88b51bfdd38bc591433d16517251b198bb` dan VAL `117e61befe2d0b2fe7cab5b5a81812572c7100281a4edc6912c3681c45362710`. Split TEST tidak dibaca untuk pemilihan mode.

## Pemeriksaan sebelum pilot

`python -m unittest discover -s tests -p test_kd_hybrid.py -v` lulus 5 pemeriksaan CPU: rumus `pure_v4` cocok dengan *snapshot* historis pada batch tetap, `hybrid_full` berbobot KD nol mempertahankan *loss* deteksi, bagian KD `hybrid_full` cocok dengan `pure_v4`, gradien hanya mengalir ke student dan proyektor, mode fitur memakai fungsi bawaan, serta bentuk log validasi satu elemen.

Evaluasi ulang supervised *seed* 42 pada VAL tersimpan di [`runs/val_ablation/hybrid_20261021_baseline/supervised_seed42_val.json`](../runs/val_ablation/hybrid_20261021_baseline/supervised_seed42_val.json): mAP50–95 0,718930, precision makro 0,882900, recall makro 0,967939, dan F1 0,923466 pada confidence 0,25. Ini acuan VAL, bukan hasil pilot hibrida.

## Uji asap dan jejak kegagalan

- `hybrid_feature`, satu *epoch*: [`manifest.json`](../runs/kd_smoke/yolo11_tiny_hybrid_feature_smoke_20261021/manifest.json) berstatus `complete`; `results.csv` mempunyai satu baris, komponen *loss* berhingga, dan kolom `train/dis_loss` serta `val/dis_loss`. Nilai akurasinya **tidak masuk tabel penelitian**.
- `hybrid_full`, percobaan awal satu *epoch*: [manifest gagal](../runs/kd_smoke/.yolo11_tiny_hybrid_full_smoke_20261021.manifest.json) berstatus `failed`. Pelatihan selesai, tetapi validasi gagal karena `dis_loss` latihan berbentuk skalar sedangkan fungsi bawaan pada validasi mengembalikan tensor satu elemen. Tidak ada hasil pilot dari run ini. Berkas run gagal tidak ditimpa atau dihapus.
- `hybrid_full`, uji ulang dengan nama run baru `yolo11_tiny_hybrid_full_smoke_20261021_retry1`: [`manifest.json`](../runs/kd_smoke/yolo11_tiny_hybrid_full_smoke_20261021_retry1/manifest.json) berstatus `complete`; `results.csv` mempunyai satu baris, komponen *loss* berhingga, dan kolom `train/dis_loss` serta `val/dis_loss`. Perbaikan hanya mengubah bentuk log `dis_loss` menjadi satu elemen; rumus dan nilainya tidak berubah. Nilai akurasinya **tidak masuk tabel penelitian**.

*Snapshot* `train_kd.py` pada uji fitur dan percobaan penuh awal mempunyai SHA-256 `e7c9555184cfc19fd1d1073de28a88d76c09436df056335ea82160473d4c8393`; uji penuh ulang memakai SHA-256 `5deec9a2abca030e58e4adee8b7226fb933dc1dadd9eaaf499d77aeaea8d91da`. Keduanya disimpan agar perubahan bentuk log dapat ditelusuri. Pilot utama nanti memakai versi kedua untuk **kedua** varian.

Semua uji asap memakai TRAIN/VAL yang sama dan hanya satu *epoch*. *Checkpoint* uji asap disimpan lokal di subfolder `weights/` masing-masing run `runs/kd_smoke/` dan tidak digunakan untuk model OP3.
