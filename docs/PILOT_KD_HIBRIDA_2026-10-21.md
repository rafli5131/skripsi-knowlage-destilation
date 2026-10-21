# Pra-registrasi pilot KD hibrida, 21 Oktober 2026

## Tujuan dan desain

Penelitian membandingkan *student* YOLO11 skala `t` yang dilatih dengan label saja, KD *teacher-only* `pure_v4`, dan KD hibrida. Pembanding **utama** KD hibrida ialah *student supervised* dengan arsitektur, split, *seed*, dan resep pelatihan sama. *Teacher* YOLO11n dibekukan. KD hibrida menambahkan *loss* label TRAIN pada sinyal *teacher*. Model yang dipakai OP3 tidak diganti selama pilot.

Prinsip penggabungan target *teacher* dengan label asli dibahas oleh [Hinton, Vinyals, dan Dean (2015)](https://arxiv.org/pdf/1503.02531). Penerapan distilasi pada detektor objek dibahas oleh [Chen dkk. (2017)](https://proceedings.neurips.cc/paper/2017/file/e1e32e235eee1f970470a3a6658dfdd5-Paper.pdf). Kedua sumber ini mendukung dasar metode, bukan menjamin hasil pada dataset penelitian ini.

## Input dan resep yang dibekukan sebelum pilot

- Dataset: [`configs/data_train_val.yaml`](../configs/data_train_val.yaml), memakai TRAIN dan VAL resmi Advance Vision yang sama dengan run sebelumnya. Verifikasi byte terhadap [`advance_vision_dataset_fingerprint.json`](../artifacts/advance_vision_dataset_fingerprint.json) berhasil: TRAIN `a460ec3f6b16bacde012374846e8bd88b51bfdd38bc591433d16517251b198bb`, VAL `117e61befe2d0b2fe7cab5b5a81812572c7100281a4edc6912c3681c45362710`. TEST tidak dipakai memilih varian.
- *Teacher*: `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`, SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`.
- *Student*: [`models/yolo11_tiny_kd.yaml`](../models/yolo11_tiny_kd.yaml), inisialisasi acak. Resep kedua varian: 100 *epoch*, *batch* 16, `imgsz=640`, AdamW, `lr0=0,001`, `lrf=0,01`, *warm-up* 3 *epoch*, *weight decay* 0,0005, `close_mosaic=10`, AMP mati, `patience=30`, `pretrained=False`, *seed* 42. Anggaran 100 *epoch* adalah **usulan D3**, belum keputusan baru.
- `hybrid_feature`: `L_det + 6,0 × L_fitur` memakai [`DistillationModel.loss` bawaan](../artifacts/training_source_snapshots/kd_seed42/distill_model.py) dan `dis=6,0`. Nilai bawaan diverifikasi pada `ultralytics/cfg/default.yaml:104` di venv pelatihan.
- `hybrid_full`: `L_det + 1,0 × L_fitur + 1,0 × L_kotak + 1,0 × L_kelas`, temperatur kelas 2. Rumus KD identik dengan `pure_v4`.

Konfigurasi calon run: [`kd_hybrid_feature.yaml`](../configs/kd_hybrid_feature.yaml) dan [`kd_hybrid_full.yaml`](../configs/kd_hybrid_full.yaml). Semua run baru memakai `runs/kd_hybrid/`; uji asap 1 *epoch* ditandai terpisah dalam `runs/kd_smoke/` dan tidak masuk tabel hasil.

Saat pilot utama dijalankan, tetapkan `KD_DATA_ROOT=/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human` pada kedua perintah agar `resolve_training_data` memverifikasi hash TRAIN/VAL dan mencatat `dataset_split_fingerprints_verified: true` di setiap *manifest*. Ini hanya meresolusi path ke berkas yang sama, tanpa mengganti gambar atau label.

## Verifikasi implementasi terpasang

Pada Ultralytics 8.4.130 yang ada di venv pelatihan, `ultralytics/nn/distill_model.py:207-249` menghitung *loss* deteksi berlabel melalui `student_model.loss(batch, preds)` lalu menambahkan *loss* fitur berbobot `dis`. `ultralytics/nn/tasks.py:402-414` menerima prediksi yang sudah dihitung sehingga *loss* deteksi tidak memerlukan *forward* kedua. `ultralytics/engine/trainer.py:502-516` mengambil nama komponen dari kamus *loss* pada *batch* pertama untuk log. `ultralytics/cfg/default.yaml:104` menetapkan `dis: 6.0`. Versi dan jalur sumber diperiksa langsung di server, bukan diasumsikan dari dokumentasi daring.

## Metrik dan aturan keputusan yang ditetapkan sebelum pilot

Kedua varian dievaluasi **sekali pada VAL** dengan 1.213 gambar, FP32, `imgsz=640`, NMS IoU 0,7, dan *confidence floor* 0,001 untuk AP. Metrik pemilihan adalah mAP50–95 VAL. Jika selisih mAP50–95 kedua varian **kurang dari 0,005**, pilih `hybrid_feature` karena implementasinya lebih sederhana. Jika selisih mencapai 0,005 atau lebih, pilih varian dengan nilai lebih tinggi. Varian terpilih tetap dibawa ke dua *seed* tambahan walaupun hasil pilot di bawah supervised; hasil negatif tetap menjawab pertanyaan penelitian.

Metrik pendamping pada ambang confidence 0,25 dan IoU pencocokan 0,50: precision, recall, F1, FP per gambar, dan duplikasi. Evaluasi ulang supervised *seed* 42 pada VAL memakai skrip dan pengaturan yang sama sebagai acuan. Hasil `pure_v4` *seed* 42 dari T04 boleh dipakai ulang. TEST tidak digunakan untuk memilih varian, ambang, atau perubahan resep.

| Tahap | `hybrid_feature` | `hybrid_full` | Supervised seed 42 |
| --- | --- | --- | --- |
| mAP50–95 VAL pilot | 0,743554 | 0,748770 | 0,718930 |
| Precision / recall / F1 @0,25 | 0,865797 / 0,968356 / 0,914209 | 0,872100 / 0,978030 / 0,922032 | 0,882900 / 0,967939 / 0,923466 |
| FP per gambar / jumlah duplikasi | 0,281946 / 147 | 0,291014 / 166 | 0,255565 / 134 |

Semua nilai dihitung pada 1.213 gambar VAL resmi dengan pengaturan yang sama. Nilai supervised berasal dari [`supervised_seed42_val.json`](../runs/val_ablation/hybrid_20261021_baseline/supervised_seed42_val.json); FP dan duplikasi dihitung ulang dari prediksi VAL dengan confidence 0,25 dan pencocokan IoU 0,50. Hasil per kelas dan sumber lengkap ada di [T04](../analisis_performa/tabel/T04_ablasi_kd_val.md) serta [T09](../analisis_performa/tabel/T09_analisis_kesalahan.md).

Kedua pilot selesai pada 100 epoch; epoch checkpoint terbaik masing-masing adalah 100. Selisih mAP50–95 antara `hybrid_full` dan `hybrid_feature` adalah 0,005216. Sesuai aturan yang ditetapkan sebelum eksperimen, `hybrid_full` dipilih untuk evaluasi tiga *seed*; nilainya juga lebih tinggi daripada supervised seed 42 sebesar 0,029839. Pada confidence 0,25, `hybrid_full` menghasilkan FP per gambar dan duplikasi sedikit lebih banyak daripada `hybrid_feature` dan supervised, sehingga metrik pendamping tetap dilaporkan bersama mAP.

Hasil ini masih satu *seed* dan hanya mengukur split level-gambar Advance Vision. TEST tidak digunakan untuk memilih varian. Keputusan pemakaian pada OP3 memerlukan bukti kamera dan runtime OP3 tersendiri.

Checkpoint terbaik: [`hybrid_feature`](../runs/kd_hybrid/yolo11_tiny_hybrid_feature_seed42/weights/best.pt) dan [`hybrid_full`](../runs/kd_hybrid/yolo11_tiny_hybrid_full_seed42/weights/best.pt). Percobaan pertama `hybrid_feature` gagal sebelum epoch pertama karena direktori proyek belum dibuat; manifest gagal dipertahankan di `runs/kd_hybrid/failures/`, kemudian retry menyelesaikan 100 epoch.
