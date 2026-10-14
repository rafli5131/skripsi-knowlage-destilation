# Protokol Eksperimen Skripsi: Pure Teacher-Only KD YOLO

## Status dan batas protokol

Protokol ini mengunci eksperimen final student setelah konfigurasi eksplorasi awal. VAL boleh dipakai memilih checkpoint dan konfigurasi final; TEST hanya untuk evaluasi akhir setelah semua checkpoint tercatat. Jika perubahan metodologi diperlukan setelah hasil TEST dibuka, hasil baru harus dilaporkan sebagai eksperimen terpisah dan perubahan tersebut tidak boleh disamarkan sebagai protokol lama.

Keputusan peneliti, dikonfirmasi pada 9 Oktober 2026: gunakan split resmi Roboflow v1 karena lebih hemat dan paling sebanding secara praktis dengan teacher dari proyek Advance Vision yang tersedia. Manifest teacher tidak mencatat versi dataset (`dataset_version=null`) dan YAML training lamanya tidak tersedia, sehingga kesamaan byte TRAIN/VAL teacher dengan v1 tidak dapat diverifikasi; perbandingan dengan teacher memiliki keterbatasan provenance ini. Audit juga menemukan nama sumber dan adegan serupa lintas split, sehingga klaim dibatasi pada generalisasi level-gambar dan tidak mencakup sesi atau adegan baru. TEST sebelumnya pernah dipakai untuk evaluasi akhir teacher FP32 dan QAT pada 2026-09-24. Untuk eksperimen ini TEST tetap tidak digunakan dalam loss, tuning, pemilihan checkpoint student, atau perubahan ambang.

## Model dan data yang dikunci

| Komponen | Keputusan |
| --- | --- |
| Teacher | Checkpoint FP32 YOLO11n dari proyek sumber; SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. |
| Student | YOLO11 custom kecil, 810.649 parameter, random initialization, `pretrained=False`; YAML SHA-256 `981c68e80f6f804511c53aec702a892f35794ffd9d8761d503daa59780d4c439`. |
| Data | Split resmi Roboflow versi `v1` (V1-Base), sesuai metadata export lokal `advance_vision_human - v1 V1-Base`; untuk unduh ulang gunakan `ROBOFLOW_VERSION=1`. Identitas byte split eksperimen dikunci lewat fingerprint SHA-256 per gambar dan label. |
| Kelas | `ball`, `gawang`, `robot`. |
| Input | Gambar 640 × 640; konfigurasi model memakai augmentasi training Ultralytics default yang sama pada kedua kelompok. |
| Seed final | 42, 1337, 2025 untuk KD dan baseline, dengan satu run per seed per metode. Semua run dilaporkan. |

Fingerprint agregat dari [`artifacts/advance_vision_dataset_fingerprint.json`](artifacts/advance_vision_dataset_fingerprint.json): train `a460ec3f6b16bacde012374846e8bd88b51bfdd38bc591433d16517251b198bb`; val `117e61befe2d0b2fe7cab5b5a81812572c7100281a4edc6912c3681c45362710`; test `aa9685a022c7484ef94cbfe68b6d000585d29de752071967709de66bed1762f1`.

Runtime eksperimen student yang teramati: Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NVIDIA L40, logical CUDA device 0. Freeze paket dicatat sekitar dua jam sebelum KD final seed 42 dimulai; seluruh 114 entri freeze cocok persis versinya dengan source lock. Manifest training mencatat platform, runtime CUDA/cuDNN, nama GPU, indeks logis, memori, dan compute capability. Evaluator TEST dan benchmark juga menyimpan hash script serta metadata perangkat; pembuat analisis akan memverifikasi hash script evaluator dan benchmark sebelum menerima hasil. Baseline supervised seed 42 dimulai sebelum freeze dan hanya menyimpan versi software serta permintaan `device: "0"`; identitas GPU didukung oleh catatan pemantauan run, bukan oleh manifest run tersebut.

Snapshot lock proyek dan freeze runtime bersih disimpan bersama catatan batas provenance di [`environment/README.md`](environment/README.md).

## Kelompok dan objective

| Kelompok | Inisialisasi dan objective |
| --- | --- |
| Teacher | Checkpoint YOLO11n FP32 yang sudah dilatih dengan label. Tidak dilatih ulang dalam eksperimen KD ini. |
| Student supervised | Arsitektur student yang sama, random initialization; loss deteksi supervised dari label TRAIN. |
| Student pure KD | Arsitektur student yang sama, random initialization; loss hanya distilasi fitur P3/P4/P5, box output teacher, dan soft class output teacher. Tidak ada loss GT, pseudo-label loss, atau QAT. |

Teacher dibekukan dan dijalankan forward-only. Pada Ultralytics 8.4.130 yang dipakai, `DistillationModel._freeze_teacher()` menetapkan teacher ke mode `eval` dan `requires_grad=False`; override `train()` memanggil pembekuan itu kembali saat mode training berubah. Loss khusus dalam `scripts/train_kd.py` juga menjalankan forward teacher di dalam `torch.no_grad()`. Gambar TRAIN menjadi masukan untuk student KD; label TRAIN tidak dipakai dalam loss KD. Label VAL dipakai untuk metrik serta pemilihan checkpoint di kedua kelompok. Berkas konfigurasi data training tidak memuat split TEST.

Objective implementasi KD adalah

\[
L_{KD}=L_{feature}+L_{box}+L_{class}, \qquad T=2.
\]

Untuk setiap level leher \(\ell\in\{P3,P4,P5\}\), logit kelas teacher dari cabang one-to-many dan one-to-one dirata-ratakan sebelum sigmoid; bobot pada lokasi \(i\) adalah \(q^{(\ell)}_{b,i}=\max_c\sigma((z^{o2m}_{t,b,c,i}+z^{o2o}_{t,b,c,i})/2)\). `L_feature` menjumlahkan tiga loss level. Pada satu level, loss adalah jumlah squared error setelah projector kanal student, dibobot oleh \(q\), lalu dibagi \(C_\ell\sum_{b,i}q^{(\ell)}_{b,i}+10^{-9}\), dengan \(C_\ell\) jumlah kanal fitur teacher. `L_box` adalah Smooth L1 (\(\beta=1\), reduksi mean) antara tensor logit regresi box mentah teacher/student pada head Detect, sebelum distribusi DFL diubah menjadi koordinat box. `L_class` adalah BCE-with-logits (reduction mean) pada target lunak \(\sigma(z_t/T)\), dengan logit kelas student dan teacher dibagi \(T=2\), lalu dikalikan \(T^2\). `L_box` dan `L_class` dihitung hanya dari output cabang Detect `one2one`: `decouple_outputs` dipanggil tanpa argumen cabang dan default implementasinya adalah `one2one`; reduksi mean berlaku pada tensor loss, bukan antar-cabang. Target teacher dihentikan gradiennya. Semua bobot loss bernilai 1. Implementasi ada di `scripts/train_kd.py`; loss deteksi ground-truth bawaan tidak ikut dihitung untuk update student.

Audit statis `scripts/train_kd.py` mengonfirmasi loss hanya membaca `batch["img"]`: kriteria deteksi student diinisialisasi untuk kompatibilitas trainer tetapi tidak dipanggil, teacher forward berada di `torch.no_grad()`, dan tidak ada akses ke field label pada fungsi loss. YAML training hanya mencantumkan TRAIN dan VAL. Queue serta pipeline final menolak manifest yang tidak menyatakan `train_labels_used_for_loss=false` untuk KD dan `test_split_used=false`.

## Resep training bersama

- Epoch maksimum: 100; early stopping patience: 30.
- Optimizer: AdamW; `lr0=0.001`, `lrf=0.01`, warmup 3 epoch, weight decay `0.0005`.
- Batch 16, workers 2, resolusi 640, FP32 (`amp=false`), `close_mosaic=10`.
- Student selalu dibuat dari YAML dengan `pretrained=false`; seed dipasangkan antara KD dan supervised.
- Aturan checkpoint: `best.pt` yang memaksimalkan fitness validation Ultralytics. Fitness pada run KD seed 42 sama dengan mAP50–95; setiap hasil harus mencatat CSV lengkap dan manifest.
- Parameter training selain objective harus sama. Objective baseline supervised dan objective teacher-only KD sengaja berbeda.

Audit implementasi Ultralytics 8.4.130 mengonfirmasi RNG diinisialisasi dari seed pada konstruksi trainer sebelum trainer membuat student; pada KD, `DistillationModel` membungkus student setelah student dibuat. `args.yaml` seed 42 pada kedua kelompok mencatat `seed=42`, `deterministic=true`, `pretrained=false`, serta path YAML arsitektur dan data yang sama. Perbandingan file args menunjukkan seluruh opsi training bersama identik; perbedaan yang tersisa adalah direktori/nama output dan argumen khusus distilasi (`distill_model`, `dis`). Susunan kode dan seed yang sama ditujukan agar student mulai dari inisialisasi yang sepadan, tetapi tensor awal student tidak disimpan atau di-hash secara terpisah; kesamaan byte bobot awal tidak dapat diverifikasi langsung dari artefak. `cls_pw=0.0` tercatat di args dan menonaktifkan bobot kelas berbasis frekuensi label. Nilai seed, arsitektur, dan `pretrained` tetap diperiksa dari manifest/args untuk setiap run.

Nilai ini mengikuti `configs/kd.yaml` dan `configs/supervised_baseline.yaml`. Hash konfigurasi saat pembekuan protokol: KD `8296b558a1a6f01d90ab4af4b674c2cf3517f9316f8de1456df9e5098d6b66ff`; supervised `00576b53acc6d2391a2465e7884e168d3a6d802b91f9098b9cfac12e980e47ae`; data YAML train/val `e7e52327911a956df210f96c936870145321a0bfbc5ac6a4b52ab3df2cc4e9dd`.

## Metrik dan analisis

Metrik akurasi utama: mAP50–95. Metrik sekunder: mAP50, precision, recall, F1, serta mAP dan recall per kelas. mAP memakai semua prediksi di atas confidence floor 0,001; precision, recall, dan F1 dihitung pada operating point confidence tetap `>0,25` dan IoU pencocokan 0,50. Nilai 0,25 mengikuti default prediction Ultralytics 8.4.130 dan ditetapkan sama untuk semua model sebelum TEST dibuka. Precision dan recall keseluruhan adalah macro-average tiga kelas; F1 dihitung dari pasangan precision/recall itu (`0` bila jumlahnya nol). NMS tetap memakai IoU 0,7. Evaluasi TEST dikunci pada FP32, input 640, batch 16, dua workers, logical device 0 (NVIDIA L40), tanpa augmentasi. Evaluator dan benchmark menolak runtime yang berbeda dari Python 3.11.2, NumPy 1.26.4, PyTorch 2.4.1+cu121, atau Ultralytics 8.4.130. Sajikan selisih mAP50, mAP50–95, dan recall tiap kelas terhadap teacher, berikut selisih KD-supervised berpasangan keseluruhan dan per kelas. Sajikan tiap seed dan mean ± simpangan baku sampel per metode; dengan tiga seed, inferensi statistik dinyatakan eksploratif dan tidak disamakan dengan bukti kuat signifikansi. Untuk ketidakpastian sampling TEST, evaluator menghitung interval bootstrap persentil 95% dengan 1.000 replikasi bootstrap gambar dengan pengembalian (seed `20261009`). Interval metrik keseluruhan hanya memakai replikasi yang memuat ketiga kelas agar penyebut macro tetap sama; replikasi tanpa objek pada suatu kelas tidak masuk interval kelas itu. Jumlah replikasi valid disimpan untuk setiap interval. Manifest mencatat aturan cakupan kelas macro ini, dan pembuat analisis memverifikasinya. Interval bootstrap bersyarat pada checkpoint yang dievaluasi dan mengukur variasi sampling gambar; interval ini tidak mencakup variasi akibat mengulang training, tidak menggantikan simpangan baku antar-seed, dan tidak ditafsirkan sebagai ketidakpastian generalisasi sesi atau adegan baru. Kemiripan frame/adegan yang tidak dapat dikelompokkan dapat membuat interval bootstrap terlalu sempit.

Ukuran/biaya model mencakup jumlah parameter, FLOPs pada input 640, ukuran `best.pt`, latensi median dan p95, serta throughput batch 1. Benchmark memakai model FP32 yang sama-sama berada di perangkat yang sama, warm-up 30 iterasi dan 200 iterasi terukur, pada frame VAL yang sama di memori. Manifest menyimpan 200 sampel latensi mentah per model, versi Python/NumPy/OpenCV/PyTorch/Ultralytics, dan metadata perangkat agar ringkasan dapat dihitung ulang. Latensi mencakup preprocessing, forward, dan NMS, tidak mencakup pembacaan disk atau pemuatan checkpoint. Hasil NVIDIA L40 hanya karakterisasi host; klaim performa robot memerlukan pengukuran perangkat robot.

Laporan test memuat hasil keseluruhan dan per kelas untuk teacher, tiga checkpoint KD, dan tiga checkpoint supervised. Keenam checkpoint student ditetapkan lewat `best.pt` masing-masing run menggunakan VAL, lalu dievaluasi tanpa mengubah model. Sajikan hasil per run serta ringkasan mean ± simpangan baku antar-seed; jangan memilih satu seed berdasarkan hasil TEST.

## Urutan pelaksanaan dan gerbang

1. Keenam run student untuk seed 42, 1337, dan 2025 selesai; seluruh manifest menyatakan TEST tidak dipakai untuk training. Run supervised seed 1337 dipulihkan dari `last.pt` setelah gangguan validasi dan manifest mencatat kedua segmen waktunya.
2. Audit manifest, checksum checkpoint, hash arsitektur/config, serta objective KD lolos. Semua seed KD menggunakan teacher yang sama dan snapshot implementasi yang konsisten; hash implementasi seed 42 dicatat sebagai retrospektif.
3. Checkpoint `best.pt` dikunci dari VAL sebelum evaluasi akhir. Hash checkpoint, fingerprint dataset, versi runtime, dan perangkat evaluator tercatat.
4. Percobaan evaluator awal pada GPU sempat memindai label TEST lalu gagal di batch pertama karena validator menghitung loss training. Percobaan itu berstatus `failed`, memiliki `models: {}`, dan tidak menghasilkan metrik; artefaknya dipertahankan pada `runs/final_test/pure_kd_official_split_locked/`.
5. Evaluator diperbaiki untuk mode inferensi saja dan evaluasi final teacher serta keenam student selesai di direktori baru `runs/final_test/pure_kd_official_split_locked_retry1/`. Manifest final menghubungkan percobaan sebelumnya melalui path dan SHA-256; tidak ada model, threshold, atau hyperparameter yang diubah berdasarkan kegagalan harness.
6. Benchmark fixed-frame VAL selesai pada NVIDIA L40. Pipeline menandai evaluasi, benchmark, dan analisis awal sebagai `complete`; tabel final yang memakai hitungan parameter checkpoint setelah audit tambahan ada di `artifacts/thesis_analysis_final_corrected/`.

Gerbang integritas evaluator menghitung ulang SHA-256 `best.pt`, YAML arsitektur student, YAML training, konfigurasi training, dan skrip training, lalu mencocokkannya dengan manifest. Run supervised seed 42 sudah berjalan sebelum hash YAML, kode, konfigurasi, fingerprint, dan runtime perangkat terekam; run ini mempertahankan pengecualian legacy yang eksplisit dan tidak diberi hash retrospektif seolah-olah direkam saat mulai. Linker provenance sudah memeriksa `args.yaml`, path split, kelas, waktu snapshot prarun, dan hash semua file data. Karena hash YAML training tidak tercatat pada waktu mulai, identitas byte YAML pada saat itu tidak dapat diklaim. Generator analisis akhir mensyaratkan hash checkpoint di manifest TEST dan benchmark identik, hash YAML benchmark cocok, serta hash frame benchmark tercakup dalam VAL fingerprint sebelum menggabungkan akurasi, ukuran, FLOPs, dan latensi. Hitungan parameter utama di analisis memakai jumlah checkpoint sebelum fusi Conv-BN, dicocokkan dengan manifest training untuk student; jumlah pascafusi validator dipisahkan sebagai diagnostik. Warm-up 30 iterasi, 200 iterasi ukur, resolusi 640, confidence 0,001, dan IoU 0,7 divalidasi terhadap protokol. Evaluator dan analisis juga mengunci versi software, pengaturan TEST, serta kesamaan perangkat.

Sebelum run KD final pertama dimulai, 9 Oktober 2026, script KD ditambah dengan field `seed` tingkat atas pada manifest karena evaluator dan pipeline memeriksa seed itu. Kedua script training juga ditambah metadata platform dan perangkat aktual (jika tersedia). Perubahan ini hanya metadata; objective KD, konfigurasi training, dan pemilihan checkpoint tidak berubah. Mulai run KD seed 1337 dan 2025, trainer menyimpan snapshot `train_kd.py` dan file sumber `DistillationModel` yang diimpor di `artifacts/training_source_snapshots/<run>/`; manifest mencatat path serta SHA-256 keduanya. Preflight dan evaluator TEST memeriksa snapshot tersebut serta memastikan semua seed KD memakai implementasi `DistillationModel` yang sama. Untuk KD seed 42 yang sudah selesai, snapshot `train_kd.py` disalin setelah training tetapi SHA-256-nya cocok dengan hash run-time pada manifest. Hash `scripts/train_kd.py` di working tree sekarang berbeda karena penambahan logika snapshot untuk run seed berikutnya; verifikasi seed 42 menggunakan path snapshot yang ditunjuk manifest, bukan mengharuskan file working tree sama. Snapshot `distill_model.py` juga dibuat pascarun; timestamp file sumbernya (2 September 2026) mendahului training, tetapi hash implementasi tidak pernah dicatat saat training sehingga kesamaan byte implementasi yang benar-benar dimuat pada saat itu tidak dapat dibuktikan. Keterbatasan ini ditandai pada manifest, bukan diklaim sebagai provenance run-time. Baseline supervised seed 42 yang sudah berlangsung tidak diubah dan dicatat sebagai pengecualian legacy untuk metadata runtime.

Untuk pelaksanaan ulang yang bersih, entry point training serial adalah [`scripts/run_student_training_queue.py`](scripts/run_student_training_queue.py). Queue memeriksa fingerprint dan status TEST untuk tiap run, tetapi tidak menjalankan evaluasi TEST. Run seed 1337 yang terputus dalam eksperimen ini dilanjutkan melalui [`scripts/resume_interrupted_supervised.py`](scripts/resume_interrupted_supervised.py), yang memeriksa konfigurasi/data dan argumen checkpoint sebelum memakai optimizer serta EMA dari `last.pt`. [`scripts/continue_skripsi_pipeline.py`](scripts/continue_skripsi_pipeline.py) melanjutkan queue hanya jika belum complete; bila queue sudah complete, supervisor langsung menjalankan pipeline final. Status queue, supervisor, dan pipeline ada di `artifacts/`.

```bash
python3 scripts/run_student_training_queue.py
```

Pipeline pasca-training [`scripts/run_locked_final_pipeline.py`](scripts/run_locked_final_pipeline.py) menunggu queue `complete`, memeriksa enam manifest/checkpoint dan fingerprint, lalu menjalankan evaluasi TEST terkunci, benchmark diagnostik pada frame VAL, serta tabel analisis. Status pipeline workspace ini sekarang `complete`; output TEST final berada di `runs/final_test/pure_kd_official_split_locked_retry1/`, benchmark di `runs/benchmarks/pure_kd_final_inference.json`, dan analisis yang dikoreksi berada di `artifacts/thesis_analysis_final_corrected/`. Upaya TEST terdahulu disimpan sebagai manifest gagal tanpa metrik.

```bash
python3 scripts/run_locked_final_pipeline.py
```

Perintah khusus untuk KD seed 42 yang dikunci:

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_kd.py \
  --seed 42 --run-name yolo11_tiny_pure_kd_v4_locked_seed42
```

Perintah penautan provenance yang digunakan untuk baseline supervised seed 42 (run itu kini sudah complete dan tertaut):

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/link_run_dataset_provenance.py \
  --manifest runs/supervised/yolo11_tiny_supervised_seed42_retry1/manifest.json
```

Contoh pemanggilan ulang pada direktori keluaran baru setelah seluruh checkpoint tersedia. Evaluator menolak direktori keluaran yang sudah ada; pilih nama direktori kosong untuk setiap pengulangan.

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/evaluate_locked_test.py \
  --models \
  kd_seed42=runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42/weights/best.pt \
  supervised_seed42=runs/supervised/yolo11_tiny_supervised_seed42_retry1/weights/best.pt \
  kd_seed1337=runs/kd/yolo11_tiny_pure_kd_v4_seed1337/weights/best.pt \
  supervised_seed1337=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt \
  kd_seed2025=runs/kd/yolo11_tiny_pure_kd_v4_seed2025/weights/best.pt \
  supervised_seed2025=runs/supervised/yolo11_tiny_supervised_seed2025/weights/best.pt \
  --output runs/final_test/pure_kd_official_split_locked_reproduction
```

Jalankan benchmark setelah checkpoint sama terkunci, pada host/perangkat yang sama:

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/benchmark_inference.py \
  --models \
  teacher_fp32=/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt \
  kd_seed42=runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42/weights/best.pt \
  supervised_seed42=runs/supervised/yolo11_tiny_supervised_seed42_retry1/weights/best.pt \
  kd_seed1337=runs/kd/yolo11_tiny_pure_kd_v4_seed1337/weights/best.pt \
  supervised_seed1337=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt \
  kd_seed2025=runs/kd/yolo11_tiny_pure_kd_v4_seed2025/weights/best.pt \
  supervised_seed2025=runs/supervised/yolo11_tiny_supervised_seed2025/weights/best.pt \
  --device 0 --imgsz 640 --warmup 30 --iterations 200 \
  --output runs/benchmarks/pure_kd_final_inference_reproduction.json
```

Sesudah kedua artefak hasil tersedia, tabel laporan dapat dibuat tanpa memilih ulang model:

```bash
env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/build_thesis_analysis.py \
  --test-manifest runs/final_test/pure_kd_official_split_locked_reproduction/manifest.json \
  --benchmark runs/benchmarks/pure_kd_final_inference_reproduction.json \
  --output artifacts/thesis_analysis_reproduction
```

## Status akhir eksekusi (diperbarui 2026-10-10)

Queue training, evaluasi TEST, benchmark, dan analisis berstatus `complete`. Artefak final yang digunakan adalah `runs/final_test/pure_kd_official_split_locked_retry1/manifest.json`, `runs/benchmarks/pure_kd_final_inference.json`, dan `artifacts/thesis_analysis_final_corrected/`. Evaluasi TEST awal gagal sebelum menghasilkan metrik dan disimpan terpisah; run final menggunakan validator inference-only. Analisis awal menyimpan jumlah parameter pascafusi dari validator, sehingga analisis dikoreksi dengan hitungan checkpoint sebelum fusi dan hitungan pascafusi dipertahankan terpisah sebagai diagnostik.

## Arsip riwayat eksekusi

Kronologi progres per-run selama training disimpan sebagai catatan historis di [`artifacts/training_status_history_2026-10-09.md`](artifacts/training_status_history_2026-10-09.md). Status terkini dirangkum di bagian **Status akhir eksekusi** di atas.
