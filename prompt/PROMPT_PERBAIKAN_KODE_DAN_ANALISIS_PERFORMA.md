# Prompt Perbaikan Kode dan Analisis Performa *Computer Vision*

> Salin seluruh isi bagian **Prompt** ke agen koding (misalnya Codex atau Claude Code) yang membuka *repository* ini. Versi 19 Oktober 2026, disusun dari analisis teknis *repo* pada *commit* `77d9afb`. Prompt ini melengkapi `prompt/PROMPT_IMPLEMENTASI_ROBOT_OP3.md`. Bila keduanya bertentangan, ikuti prompt ini dan laporkan pertentangannya.

---

## Prompt

### 0. Peran dan prinsip kerja

Anda adalah agen koding yang membantu Bhre (Teknik Komputer FILKOM Universitas Brawijaya) memperbaiki kode eksperimen skripsi *knowledge distillation* (KD) untuk deteksi `ball`, `gawang`, dan `robot` pada ROBOTIS OP3, lalu menyiapkan dokumen tabel untuk analisis performa *computer vision*. Semua angka akan dipertanggungjawabkan Bhre di sidang. Karena itu berlaku prinsip berikut.

1. Keabsahan eksperimen lebih penting daripada kecepatan. Perbedaan antarvarian selain faktor yang sedang diuji adalah cacat rancangan.
2. Verifikasi dari kode sumber Ultralytics 8.4.130 yang terpasang sebelum memakai API apa pun. Sebutkan berkas dan barisnya di laporan.
3. Jangan memutuskan sendiri butir di Bagian 3. Pakai nilai sementara yang tertulis, tandai, lalu tanyakan di titik henti.
4. Berhenti di setiap titik henti (TH) dan tunggu persetujuan tertulis Bhre sebelum lanjut.
5. Tulis kode yang sederhana dan eksplisit agar Bhre dapat menjelaskannya baris per baris.
6. Tidak ada jalan pintas diam-diam. Bila sesuatu gagal, berhenti dan laporkan; jangan mengubah resep, *batch*, atau metode agar alur "tetap jalan".
7. Jangan mengarang angka. Sel tabel yang datanya belum ada diisi `[BELUM DIUKUR]`.
8. Bila Anda tidak punya akses ke server lab atau OP3, tulis skrip dan perintah lengkap untuk dijalankan Bhre, lalu minta log keluarannya. Jangan menebak hasil.

### 1. Kondisi *repo* saat ini

Fakta berikut diverifikasi pada *commit* `77d9afb`. Periksa ulang sebelum dipakai.

- ***Teacher***: YOLO11n FP32 beku, 2.590.425 parameter, `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`, SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Berkas ini tidak ada di *repo*.
- ***Student***: `models/yolo11_tiny_kd.yaml`, topologi YOLO11n skala `t` (kedalaman 0,50, lebar 0,125), 810.649 parameter, inisialisasi acak. Arsitektur yang sama dipakai untuk KD dan kontrol *supervised*.
- ***Pure KD*** (`scripts/train_kd.py`, fungsi `teacher_only_loss`): menimpa `DistillationModel.loss` secara global. *Loss* = fitur P3/P4/P5 (L2 berbobot skor *teacher* melalui proyektor) + Smooth L1 pada keluaran `boxes` + BCE bertemperatur pada `scores`, bobot 1 : 1 : 1, T = 2, tanpa *loss* label. *Loss* kotak dan kelas dirata-ratakan pada semua 8.400 *anchor* tanpa pembobotan.
- **Hasil TEST terkunci** (3 *seed*: 42, 1337, 2025): mAP50-95 *pure KD* 0,6630 ± 0,0108, *supervised* 0,7225 ± 0,0035, *teacher* 0,7800. Selisih berpasangan KD − *supervised*: *precision* −0,106, *recall* −0,007. Sumber: `artifacts/thesis_analysis_final_corrected/`.
- **Konvergensi**: *epoch* terbaik KD 88 sampai 96, *supervised* 99 sampai 100 dari 100; `patience` 30 tidak pernah terpicu.
- ***Benchmark* L40** (`scripts/benchmark_inference.py`): median 24,8 sampai 25,7 ms untuk semua model karena didominasi *overhead* `predict()` *batch* 1 di GPU. Angka ini tidak boleh dipakai untuk klaim efisiensi.
- **OP3** (`scripts/op3_pytorch_detector.py`, 3 sesi pada 19 Oktober 2026, hanya *student* KD *seed* 42): FPS efektif yang dihitung ulang dari timestamp capture adalah 3,41; 14,11; dan 15,90 untuk tiga sesi. Run pertama memiliki kondisi yang tidak terverifikasi. Pada dua sesi terakhir, inferensi p50 sekitar 24 ms, *end-to-end* 26 sampai 28 ms, jeda *timestamp* kamera p95 sekitar 232 sampai 264 ms dengan maksimum 1,4 sampai 2,0 detik, CPU proses sekitar 738 sampai 762%, RSS sekitar 355 MiB. `mean_fps` dan `fps_running` pada log lama dihitung sejak node menyala. *Teacher*, *supervised*, dan kondisi `walking` belum diukur.
- **Tracking dan kelas per frame**: tiga log kamera tersebut direkam sebelum BoT-SORT dan CSV per deteksi ditambahkan, sehingga tidak membuktikan ID lintas frame atau deteksi per kelas. Uji offline citra VAL dapat memeriksa alur kode, tetapi bukan pengganti uji kamera OP3.
- **Lingkungan**: pelatihan memakai venv eksternal proyek `skripsi-yolo11-qat-openvino` (Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NVIDIA L40). OP3 memakai Python 3.12.3, PyTorch 2.4.1+cpu, Ultralytics 8.4.130, ROS 2 Jazzy, kamera C920 640×480 YUYV 30 FPS pada `/thesis/image_raw`.
- **Kerapian**: `configs/*.yaml` memakai path absolut NAS lab; `core.autocrlf=true` di salinan Windows mengubah SHA-256 berkas teks sehingga tidak cocok dengan *manifest*; tujuh log pelatihan (sekitar 24,8 MB) dan 15 berkas `.pt` tersimpan langsung di Git; `README.md` dan `dokumentasi/README.md` belum sinkron dengan status OP3 terbaru.

### 2. Batasan dan larangan

- Tanpa OpenVINO, ONNX untuk penerapan, INT8, PTQ, QAT, atau argumen `quantize`. Semua model dijalankan sebagai `.pt` dengan PyTorch.
- TEST tidak boleh dipakai untuk memilih apa pun: ambang, *epoch*, bobot KD, `imgsz`, jumlah *thread*, atau varian. Seluruh seleksi dan sapuan parameter dilakukan di VAL. TEST dibuka sekali per protokol baru, hanya bila berkas `TEST_UNLOCKED` sudah dibuat Bhre secara manual.
- Jangan menimpa, memindahkan, atau menghapus run, *manifest*, log, dan artefak lama. Itu jejak audit. Run baru memakai nama direktori baru.
- Jalur reproduksi lama (`train_kd.py` dengan `configs/kd.yaml` saat ini) harus tetap menghasilkan objektif yang sama persis. Varian baru ditambahkan sebagai mode, bukan dengan mengubah perilaku bawaan.
- Jangan mengirim perintah servo atau *gait*, mengubah pengaturan sistem OP3 (*governor*, *turbo*, isolasi inti), atau memasang paket ke Python sistem. Pengaturan sistem hanya dicatat.
- Frame kamera hanya disimpan oleh skrip yang dijalankan operator secara eksplisit.
- Jangan `push`, menjalankan `git reset --hard`, menghapus hasil, atau memutakhirkan paket tanpa izin.

### 3. Keputusan yang belum dikunci

Simpan nilai sementara di `configs/analysis.yaml` dengan komentar `# BELUM DIKUNCI`. Catat setiap keputusan Bhre di `docs/DECISIONS.md` beserta tanggalnya.

| Kode | Keputusan | Nilai sementara | Pilihan |
| --- | --- | --- | --- |
| D1 | Pasangan *teacher* dan *student* | Belum ada. Jangan melatih model baru sebelum dikunci. | (a) *teacher* YOLO11n dan *student* skala `t` seperti sekarang; (b) *teacher* YOLO11s atau YOLO11m dengan *student* YOLO11n |
| D2 | Objektif KD untuk pelatihan utama | `pure_v4` (keputusan Bhre: pure KD) | Pertahankan `pure_v4`; kandidat baru hanya boleh berupa objektif pure KD dan harus disetujui di TH-D. Objektif hybrid tidak termasuk lingkup. |
| D3 | Anggaran *epoch* | 100 | 100, 150, atau 200, sama untuk semua varian |
| D4 | Kebijakan ambang *confidence* untuk P, R, F1 | Laporkan keduanya: tetap 0,25 dan ambang F1 terbaik per model yang dipilih di VAL lalu dibekukan | Salah satu atau keduanya |
| D5 | Grid sapuan parameter | Bagian 6.3 | Disesuaikan Bhre |
| D6 | Jumlah *thread* PyTorch untuk uji utama OP3 | Dipilih dari T17 pada frame tetap | Satu angka tetap untuk semua varian |
| D7 | Protokol sesi *live* | 3 sesi × 60 detik per varian per kondisi, urutan diacak dengan *seed* tetap | Durasi dan jumlah sesi |
| D8 | Set frame kamera OP3 berlabel | `null` | Jalur set berlabel |
| D9 | Penyimpanan bobot dan log besar | Tetap di Git | Git LFS atau rilis GitHub |
| D10 | Batas ukuran objek | Kecil < 32² piksel, sedang 32² sampai 96², besar > 96² pada citra 640, mengikuti konvensi COCO [BUTUH SITASI: definisi area objek pada evaluasi deteksi COCO] | Ambang lain bila disetujui |

### 4. Alur kerja dan titik henti

```
Fase A  Kerapian repo, provenance, tabel awal dari data lama        -> TH-A
Fase B  Diagnosis KD di VAL dan mode loss baru (belum melatih)       -> TH-B
Fase C  Alat ukur OP3 dan benchmark CPU frame tetap                   -> TH-C
Fase D  Keputusan D1 sampai D3, pilot di VAL                          -> TH-D
Fase E  Pelatihan utama dan evaluasi TEST terkunci baru               -> TH-E
Fase F  Pengukuran OP3 (dijalankan Bhre)                              -> TH-F
Fase G  Tabel final dan ringkasan analisis performa                   -> TH-akhir
```

Fase C boleh dikerjakan sejajar dengan Fase B. Pengukuran final Fase F memakai *checkpoint* hasil Fase E.

### 5. Perbaikan kode

#### 5.1 Fase A: kerapian *repo* dan *provenance*

1. Tambahkan `.gitattributes` berisi `* text=auto eol=lf` serta `*.pt binary`, `*.png binary`, dan `*.pdf binary`. Jangan menjalankan perintah yang menimpa salinan kerja; tuliskan langkah *checkout* ulang untuk dijalankan Bhre.
2. Tulis `scripts/verify_artifact_hashes.py` yang membandingkan setiap SHA-256 yang tercatat di *manifest* dengan berkas di disk dan melaporkan yang tidak cocok. Jalankan di Linux, lalu siapkan perintah untuk salinan Windows.
3. Dukung variabel lingkungan atau argumen CLI `KD_DATA_ROOT` dan `KD_TEACHER_CHECKPOINT` tanpa mengubah nilai bawaan. Catat path hasil resolusi beserta hash-nya di *manifest*.
4. Buat `requirements/train-gpu.txt` berisi versi tersemat dari `environment/runtime_freeze_2026-10-09.txt` untuk paket yang benar-benar diimpor *repo*. `requirements-op3-pytorch.txt` tetap dipakai untuk OP3.
5. Tambahkan gerbang versi di `train_kd.py` dan `train_supervised_baseline.py`: gagal keras bila Ultralytics bukan 8.4.130, atau bila SHA-256 `ultralytics/nn/distill_model.py` yang terpasang berbeda dari nilai yang dikunci di konfigurasi.
6. Buat `configs/model_registry.yaml` untuk setiap varian (*teacher*, *supervised* per *seed*, KD per *seed*): path, SHA-256, parameter sebelum dan sesudah fusi, GFLOPs, dan *manifest* sumber. Skrip evaluasi, *benchmark*, dan node OP3 memvalidasi *checkpoint* melalui registri ini.
7. Pindahkan nama run yang ditulis mati di `run_student_training_queue.py`, `run_locked_final_pipeline.py`, dan `evaluate_locked_test.py` ke konfigurasi, dengan nilai bawaan yang sama persis dengan sekarang.
8. Sinkronkan `README.md` dan `dokumentasi/README.md` dengan status uji OP3 terbaru.
9. Buat tabel awal Bagian 6 dari data yang sudah ada (lihat 6.4), dan tandai eksplisit bahwa hasil Advance Vision bukan akurasi kamera OP3.
- **TH-A**: laporkan hasil verifikasi hash, berkas yang berubah, dan tabel awal.

#### 5.2 Fase B: objektif KD

1. Tulis `docs/ultralytics_kd_notes.md`. Cetak bentuk dan arti `boxes`, `scores`, dan `feats` dari Detect head YOLO11 dalam mode latih pada Ultralytics 8.4.130, termasuk `reg_max`, untuk *teacher* dan *student*. Rujuk berkas dan baris kode sumber.
2. Pindahkan logika *loss* ke modul tersendiri (misalnya `scripts/kd_losses.py`) dengan pilihan `kd.mode`:
   - `pure_v4`: identik dengan objektif sekarang;
   - `pure_weighted`: Smooth L1 dan BCE dibobot w_i = max_c σ(z_T,i,c), lalu dinormalkan dengan Σ w_i;
   - `pure_dfl_kl`: bila `boxes` terbukti berupa *logit* DFL, ganti Smooth L1 dengan KL(softmax(b_T / τ_b) ‖ softmax(b_S / τ_b)) × τ_b² per sisi, dibobot w_i [BUTUH SITASI: *localization distillation* untuk detektor *dense*];
   - `hybrid`: *loss* deteksi Ultralytics dengan label TRAIN ditambah λ × *loss* KD [BUTUH SITASI: KD deteksi objek yang menggabungkan *loss* label dan distilasi]. Tulis jelas bahwa varian ini bukan lagi *pure KD*.
3. Mode dipilih lewat `configs/kd.yaml`. *Manifest* mencatat mode, semua bobot, temperatur, dan SHA-256 modul *loss*.
4. Jelaskan cara pemasangan *loss* ke *trainer*: pertahankan *monkeypatch* atau ganti dengan subkelas `DistillationModel` yang dipasang terkendali. Uji juga jalur *resume*.
5. Uji `pytest` minimum:
   - nilai `pure_v4` pada *batch* tetap sama persis dengan implementasi lama;
   - *teacher* tidak menerima gradien, sedangkan *student* dan proyektor menerimanya;
   - pada `hybrid` dengan λ = 0, *loss* sama dengan *loss* deteksi biasa;
   - bentuk keluaran *teacher* dan *student* sejajar (jumlah *anchor* dan `nc` sama);
   - pengaman menolak `nc` atau nama kelas yang berbeda.
6. Diagnosis selisih *precision* hanya di VAL dengan tujuh *checkpoint* yang sudah ada: isi T09, T10, T11, dan T14.
- **TH-B**: Bhre meninjau kode *loss* dan hasil diagnosis sebelum ada pelatihan baru.

#### 5.3 Fase C: node OP3 dan alat ukur

1. Perluas `scripts/op3_pytorch_detector.py` tanpa mengubah perilaku bawaan selain kolom tambahan:
   - parameter `model_variant` (`teacher`, `supervised`, `kd`) yang divalidasi terhadap registri;
   - parameter `torch_num_threads`, `torch_interop_threads`, dan `cpu_affinity` (opsional), dicatat di JSON beserta nilai `torch.get_num_threads()` yang aktual;
   - kolom CSV baru: `is_warmup` (N frame awal, parameter `warmup_frames` bawaan 30), `publish_time_ns`, `capture_to_publish_ms`, `fps_window` (dari *timestamp* kamera, jendela N frame), `cpu_temp_c`, `cpu_freq_mhz`, `n_ball`, `n_gawang`, `n_robot`, dan *confidence* maksimum per kelas;
   - opsi `log_detections` yang menulis CSV terpisah per deteksi (frame, kelas, *confidence*, bbox) tanpa menyimpan gambar;
   - parameter `duration_s` dan `max_frames` agar sesi berhenti sendiri;
   - `mean_fps` di JSON dihitung dari *timestamp* kamera setelah membuang frame *warm-up*; nilai lama dipertahankan dengan nama `mean_fps_since_start`.
2. `scripts/camera_stream_probe.py`: berlangganan *topic* kamera tanpa model, mencatat *timestamp* dan jeda, untuk memisahkan masalah kamera dari beban detektor.
3. `scripts/record_fixed_frames.py`: dijalankan operator secara eksplisit, menyimpan 30 frame *warm-up* dan 300 frame uji dari C920 sebagai PNG beserta *manifest* SHA-256. Adegan statis memuat ketiga kelas.
4. `scripts/benchmark_cpu_frames.py`: *benchmark* CPU pada frame tetap untuk varian × `imgsz` × jumlah *thread*. Ukur *preprocess*, *inference*, dan *postprocess* dengan `time.perf_counter_ns()`, muat model sekali per blok, jalankan di bawah `torch.inference_mode()`, acak urutan blok dengan *seed* tetap, tunggu pendinginan berbasis suhu, dan tulis CSV per frame serta per blok. Skrip ini menggantikan *benchmark* L40 untuk klaim efisiensi.
5. `docs/checklist_op3.md`: perintah per sesi, pengaturan sistem yang dicatat (bukan diubah), serta prosedur `servo_idle` dan `walking`.
- **TH-C**: uji coba alat ukur di laptop atau server, lalu serahkan perintah OP3 ke Bhre.

#### 5.4 Fase D dan E: keputusan dan pelatihan ulang

1. **TH-D**: berhenti dan minta keputusan D1, D2, dan D3. Sertakan ringkasan Fase B.
2. Pilot di VAL dengan 1 *seed*: mode KD kandidat × grid bobot kecil × temperatur. Pilih hanya berdasarkan VAL dan isi T04.
3. Bila D1 = (b): latih *teacher* YOLO11s atau YOLO11m dari bobot COCO dengan resep yang sama, ukur memori GPU puncak, lalu latih *student* YOLO11n *supervised* dan KD dari berkas `yolo11n.pt` yang sama. Bila D1 = (a): pertahankan *teacher* dan arsitektur sekarang.
4. Pelatihan utama: 3 *seed*, nama run baru, resep identik kecuali suku *loss*.
5. Evaluasi TEST sekali dengan protokol dan direktori evaluasi baru. Catat bahwa TEST sudah pernah dilihat pada evaluasi *teacher* 24 September 2026.
- **TH-E**.

#### 5.5 Fase F: pengukuran OP3 (dijalankan Bhre)

Urutan: `camera_stream_probe.py` di `servo_idle` dan `walking`, perekaman frame tetap, `benchmark_cpu_frames.py` untuk semua varian, lalu sesi *live* sesuai D7 untuk setiap varian dan kondisi. Agen memeriksa log, menolak sesi yang tidak lengkap, dan menandai anomali seperti jeda kamera lebih dari 1 detik atau *throttling*.
- **TH-F**.

### 6. Dokumen tabel analisis performa

#### 6.1 Struktur dan aturan

Buat folder `analisis_performa/` berisi:

- `INDEKS.md`: daftar tabel, status (lengkap, sebagian, belum diukur), sumber data, dan tanggal pembaruan;
- `DEFINISI.md`: definisi dan rumus setiap metrik (6.2);
- `tabel/Txx_<nama>.csv` untuk mesin dan `tabel/Txx_<nama>.md` siap dikutip di skripsi;
- `manifest.json`: SHA-256 setiap tabel, berkas sumber beserta hash-nya, versi skrip, dan waktu pembuatan;
- generator `scripts/build_performance_tables.py` yang dapat dijalankan ulang, menolak sumber yang hash-nya tidak cocok, dan mengisi `[BELUM DIUKUR]` bila data belum ada.

Aturan setiap tabel: satuan di *header*; jumlah sampel (gambar, objek, frame, blok, atau sesi) dicantumkan; mean ± SD antar-*seed* dan IK 95% bila tersedia; latensi dilaporkan sebagai median dan p95; versi Markdown memakai koma desimal, versi CSV memakai titik; keterangan sumber di bawah tabel.

#### 6.2 Definisi wajib (`DEFINISI.md`)

- **Latensi tahap**: *preprocess*, *inference*, *postprocess* dari `perf_counter_ns` atau `Results.speed`; total = jumlah ketiganya; *end-to-end* = awal *callback* sampai deteksi diterbitkan.
- ***Capture-to-publish*** = waktu terbit − *timestamp header* kamera. Sebutkan sumber jam dan pastikan keduanya memakai jam yang sama.
- **FPS efektif** = (n − 1) / (t_n − t_1) dari *timestamp* kamera frame yang diproses, setelah frame *warm-up* dibuang.
- **FPS turunan** = 1000 / rerata latensi total (ms).
- **CPU ternormalisasi** = CPU% proses / jumlah *logical CPU*.
- **Persentil** memakai metode linear NumPy.
- **Kepatuhan tenggat** = proporsi frame dengan latensi ≤ 33,3 ms (30 FPS) dan ≤ 66,7 ms (15 FPS).
- **P, R, F1** dihitung pada IoU 0,5 dengan kebijakan ambang D4; mAP50-95 dirata-ratakan pada IoU 0,50 sampai 0,95.
- **Ukuran objek** mengikuti D10.

#### 6.3 Grid sapuan sementara (D5)

- *Confidence*: 0,05 sampai 0,90, langkah 0,05.
- IoU NMS: 0,30; 0,45; 0,50; 0,60; 0,70. `max_det` tetap 300.
- `imgsz`: 320, 416, 512, 640.
- *Thread* PyTorch: 1, 2, 4, 6, 8, dan bawaan.
- Sapuan akurasi hanya di VAL. TEST hanya untuk konfigurasi yang sudah dikunci.
- Sapuan latensi di CPU OP3 pada frame tetap: minimal 5 blok per sel, 300 frame per blok, 30 frame *warm-up*.

#### 6.4 Daftar tabel

**Kelompok A. Model dan pelatihan**

| Kode | Tabel | Kolom utama | Sumber data |
| --- | --- | --- | --- |
| T01 | Spesifikasi model | Varian, arsitektur, skala kedalaman dan lebar, parameter sebelum dan sesudah fusi, GFLOPs pada 640, ukuran *checkpoint* (MiB), SHA-256 | Registri model, *manifest* |
| T02 | Resep pelatihan | Per varian: *epoch*, *batch*, *optimizer*, `lr0`, `lrf`, *weight decay*, *warmup*, augmentasi, AMP, *seed*, mode KD, bobot dan T, waktu latih, memori GPU puncak | *Manifest*, `args.yaml` |
| T03 | Konvergensi | Per run: mAP50-95 VAL pada *epoch* 10, 25, 50, 75, 100, *epoch* terbaik, nilai terbaik | `results.csv` |
| T04 | Ablasi KD di VAL | Mode × bobot × T: mAP50, mAP50-95, P, R per kelas, *epoch* terbaik | Run pilot Fase D |

**Kelompok B. Akurasi pada dataset**

| Kode | Tabel | Kolom utama | Sumber data |
| --- | --- | --- | --- |
| T05 | Akurasi keseluruhan TEST | Per varian: P, R, F1, mAP50, mAP50-95, mean ± SD 3 *seed*, IK 95% *bootstrap* | Evaluasi TEST terkunci |
| T06 | Akurasi per kelas | `ball`, `gawang`, `robot` × varian: jumlah objek, AP50, AP50-95, P, R, F1 | Evaluasi TEST terkunci |
| T07 | Selisih berpasangan | Per *seed*: KD − *supervised*, KD − *teacher*, retensi terhadap *teacher* (%), tanda selisih | Tabel berpasangan |
| T08 | Akurasi per ukuran objek | Kecil, sedang, besar × kelas × varian: jumlah objek, *recall*, AP50-95 | Prediksi per gambar |
| T09 | Analisis kesalahan | Per varian: FP per gambar, FP latar, FP salah kelas, FP lokalisasi (IoU 0,1 sampai 0,5), duplikat, FN per ukuran objek | Prediksi per gambar (VAL) |
| T10 | Matriks kebingungan | 4 × 4 (tiga kelas dan latar) per varian pada ambang D4 | Validator |
| T11 | Sapuan ambang *confidence* | Ambang × varian: P, R, F1, deteksi per gambar; baris ambang F1 terbaik | VAL |
| T12 | Sapuan IoU NMS | IoU × varian: mAP50, mAP50-95, P, R, jumlah duplikat, waktu *postprocess* | VAL |
| T13 | Sapuan ukuran input | `imgsz` × varian: mAP50, mAP50-95 per kelas, GFLOPs, latensi CPU frame tetap, FPS turunan | VAL dan *benchmark* frame tetap |
| T14 | Kalibrasi *confidence* | Per varian: ECE 10 *bin*, tabel reliabilitas per *bin* (rerata *confidence*, *precision* aktual, jumlah deteksi) | Prediksi VAL |

**Kelompok C. Kinerja *runtime* di OP3**

| Kode | Tabel | Kolom utama | Sumber data |
| --- | --- | --- | --- |
| T15 | Lingkungan uji OP3 | CPU, inti dan *thread*, RAM, OS, kernel, Python, PyTorch, Ultralytics, OpenCV, ROS 2, *governor* dan mode daya (dicatat), kamera, resolusi, format piksel, FPS diminta, *topic*, QoS | JSON sesi, `checklist_op3.md` |
| T16 | Latensi per tahap pada frame tetap | Varian × `imgsz` × *thread*: *preprocess*, *inference*, *postprocess*, total (mean, median, p95, p99, SD), FPS turunan, jumlah frame dan blok | `benchmark_cpu_frames.py` |
| T17 | Sapuan *thread* | *Thread* × varian: median dan p95 total, FPS turunan, CPU% mentah dan ternormalisasi, FPS per inti | `benchmark_cpu_frames.py` |
| T18 | Sesi *live* per kondisi | Varian × kondisi × sesi: durasi, frame diproses, FPS efektif, perkiraan frame terlewat, jeda kamera p50/p95/maks, jumlah jeda > 1 detik, *end-to-end* median/p95, *capture-to-publish* median/p95, CPU%, RSS, suhu, frekuensi | CSV dan JSON `runs/op3_pytorch/` |
| T19 | `servo_idle` dibanding `walking` | Per varian: selisih `walking` − `servo_idle` untuk setiap metrik T18 beserta IK 95% antarsesi | T18 |
| T20 | Sumber daya dan *start-up* | Per varian: waktu muat model, latensi frame pertama, RSS median dan puncak, CPU% median dan p95 | JSON dan CSV sesi |
| T21 | Stabilitas termal | Per blok atau sesi: suhu awal, suhu maksimum, frekuensi rerata, kejadian *throttling*, lama pendinginan | CSV sesi dan *benchmark* |
| T22 | Aliran kamera tanpa dan dengan detektor | Kondisi × (tanpa model, setiap varian): laju *topic*, jeda p50/p95/maks, jumlah jeda > 1 detik | `camera_stream_probe.py`, CSV sesi |
| T23 | Kepatuhan tenggat *real-time* | Varian × kondisi: % frame ≤ 33,3 ms dan ≤ 66,7 ms, untuk latensi total dan *end-to-end* | T16, T18 |
| T24 | Pengaruh *preview* (opsional) | `publish_debug_image` mati dan hidup: latensi, CPU% | Sesi tambahan |
| T25 | Observasi deteksi *live* (bukan akurasi) | Varian × kondisi: deteksi per frame per kelas, *confidence* p10/median/p90, laju kedip (perubahan jumlah deteksi antarframe) | CSV deteksi per frame |

**Kelompok D. Ringkasan**

| Kode | Tabel | Kolom utama | Sumber data |
| --- | --- | --- | --- |
| T26 | *Trade-off* utama (tabel inti Bab IV) | Per varian: mAP50-95 TEST, F1, latensi median frame tetap pada `imgsz` dan *thread* terkunci, FPS efektif `servo_idle` dan `walking`, CPU%, RSS, parameter, GFLOPs | T05, T16, T18, T01 |
| T27 | Akurasi pada citra kamera OP3 | Sama dengan T05 dan T06, hanya bila D8 terisi | Set berlabel D8 |

#### 6.5 Yang dapat diisi sekarang

Pada Fase A, isi T01, T02, T03, T05, T06, dan T07 dari `artifacts/thesis_analysis_final_corrected/`, *manifest*, dan `results.csv` yang sudah ada. Isi T18, sebagian T15, dan baris "dengan detektor KD" pada T22 dari tiga sesi di `runs/op3_pytorch/`. Beri catatan bahwa percobaan 01 (`20261019T080757Z`) memiliki label kondisi yang tidak terverifikasi. Semua sel lain diisi `[BELUM DIUKUR]`.

### 7. Standar kode dan dokumen

- Python bertipe dengan *docstring* Bahasa Indonesia singkat, modul `logging`, dan `pathlib` agar berjalan di Windows maupun Linux.
- Jalankan `pytest` sebelum setiap *commit*. Buat *commit* kecil per tugas dengan pesan yang jelas.
- Dokumen di `docs/` dan `analisis_performa/` ditulis dalam Bahasa Indonesia ragam baku akademis:
  - tanpa tanda pisah *em dash*;
  - memakai "algoritme" (bukan "algoritma") dan "analisis" (bukan "analisa"), serta tidak memakai "rancang bangun";
  - istilah asing dicetak miring kecuali nama produk;
  - setiap klaim faktual bersitasi atau diberi penanda [BUTUH SITASI: ...];
  - dilarang mengarang nama penulis, tahun, judul, atau DOI.

### 8. Format laporan di setiap titik henti

1. Yang dikerjakan, ringkas.
2. Berkas yang dibuat atau diubah.
3. Perintah yang dijalankan beserta hasilnya; setiap angka disertai path berkas sumbernya.
4. Penyimpangan dari prompt ini beserta alasannya.
5. Keputusan atau informasi yang dibutuhkan dari Bhre.

### 9. Mulai dari sini

Baca `README.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `AUDIT_DATASET_SKRIPSI.md`, `OP3_PYTORCH_RUNTIME.md`, `scripts/train_kd.py`, `scripts/op3_pytorch_detector.py`, `artifacts/thesis_analysis_final_corrected/`, dan `runs/op3_pytorch/`. Kerjakan Fase A, lalu berhenti di TH-A.
