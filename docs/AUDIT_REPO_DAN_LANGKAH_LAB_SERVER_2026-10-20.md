# Audit repo dan langkah lab/server — 20 Oktober 2026

**Snapshot historis pada commit `49f6c3b`.** Status tabel dan saran pilot di bawah sudah dilanjutkan. Lihat [indeks lab/server terkini](../analisis_performa/lab_server/README.md) dan [hasil pilot `pure_weighted`](PILOT_PURE_WEIGHTED_2026-10-20.md).

## Cakupan audit

Audit baca saja atas `main` pada commit `49f6c3b` (`Update OP3 runtime tables from saved trials`). Status kerja bersih saat audit. Dokumen ini membedakan hasil dataset Advance Vision, benchmark server, dan observasi kamera OP3. Tidak ada training, evaluasi baru, atau uji fisik robot yang dijalankan untuk menyusun audit ini.

## Peta repo dan status

| Bagian | Sumber utama | Temuan |
| --- | --- | --- |
| Data dan provenance | `AUDIT_DATASET_SKRIPSI.md`, `artifacts/advance_vision_dataset_fingerprint.json`, `configs/data_train_val.yaml` | Roboflow Advance Vision v1, kelas `ball`, `gawang`, `robot`; 4.600/1.213/592 gambar TRAIN/VAL/TEST. Audit label lulus. Ada sumber/adegan serupa lintas split; klaim hanya level gambar. YAML TRAIN/VAL sengaja tidak memuat TEST. |
| Arsitektur dan checkpoint | `models/yolo11_tiny_kd.yaml`, `configs/model_registry.yaml`, `models/weights/kd_student_best.pt` | Teacher adalah YOLO11n FP32 (2.590.425 parameter); student adalah YOLO11 kustom skala `t` (810.649 parameter), **bukan YOLO11n standar**. Checkpoint deploy adalah KD seed 42 dengan hash tercatat di registry. |
| Training | `scripts/train_kd.py`, `scripts/train_supervised_baseline.py`, `configs/kd.yaml`, `configs/supervised_baseline.yaml`, `artifacts/student_training_queue.json` | Tiga seed berpasangan 42/1337/2025 selesai. KD memakai teacher beku dan loss fitur, box, kelas dari teacher; label TRAIN tidak masuk loss KD. Kontrol supervised memakai student berarsitektur sama. Resep nominal 100 epoch maksimum, dengan pemilihan `best.pt` melalui VAL; tidak berarti semua run berhenti tepat pada epoch ke-100. |
| Evaluasi dan benchmark | `artifacts/final_evaluation_pipeline.json`, `runs/final_test/pure_kd_official_split_locked_retry1/`, `runs/benchmarks/pure_kd_final_inference.json`, `artifacts/thesis_analysis_final_corrected/` | Pipeline final berstatus `complete`. Hasil TEST, benchmark NVIDIA L40, dan koreksi hitungan parameter checkpoint tersedia. Direktori analisis tanpa akhiran `corrected` adalah arsip yang sudah digantikan. |
| Tabel skripsi | `analisis_performa/INDEKS.md`, `analisis_performa/lab_server/README.md` | T01–T03, T06–T07, T09–T11, T14 lengkap; T05 dan T13 sebagian; T04, T08, T12 belum diukur. T15–T27 adalah tabel OP3 dengan banyak pengukuran masih parsial/belum ada. |
| Runtime OP3 | `scripts/op3_pytorch_detector.py`, `ros2_packages/`, `dokumentasi/2026-10-19/`, `runs/op3_idle_trial/` | Inferensi CPU FP32 `.pt` dengan ROS 2 Jazzy sudah berjalan. Satu sesi baru `servo_idle` terverifikasi selama sekitar 60 detik memproses 1.501 frame dengan ketiga kelas dan ID track pada objek relatif diam. Belum ada akurasi mAP kamera berlabel, sesi walking yang sebanding, atau uji khusus kestabilan ID objek bergerak. |
| Naskah dan keputusan | `DRAF_PROPOSAL_BAB_I-III.md`, `DRAF_ABSTRAK_SKRIPSI.md`, `PLANNING_SKRIPSI.md`, `configs/analysis.yaml`, `docs/DECISIONS.md` | Draf masih berjudul studi Advance Vision. Tujuan pengguna kini adalah penerapan pada OP3. D1 dikunci pada 20 Oktober: teacher YOLO11n → student skala `t`; D2 menetapkan KD murni `pure_v4`. D3–D10 belum dikunci. |

## Hasil yang sudah dapat dipakai

- Mean TEST mAP50–95: KD `0,6630 ± 0,0108`, supervised student `0,7225 ± 0,0035` (masing-masing tiga seed), teacher `0,7800` (satu checkpoint). Selisih berpasangan KD − supervised `−0,0595 ± 0,0138`. Sumber: T05 dan T07.
- Mean TEST precision/recall/F1 KD `0,7547/0,9631/0,8462`; supervised `0,8609/0,9699/0,9121`. Nilai kelas terpisah ada pada T06. Pada konfigurasi ini KD belum mengungguli baseline supervised.
- Student KD mempunyai 68,71% lebih sedikit parameter, checkpoint 65,20% lebih kecil, dan GFLOPs 62,64% lebih rendah daripada teacher. Baseline supervised berarsitektur student yang sama juga mendapat penghematan ukuran ini; jangan mengatribusikannya ke loss KD. Benchmark L40: rerata median latensi KD sekitar 25,01 ms, supervised 25,00 ms, teacher 25,72 ms; ini bukan FPS OP3.
- Sesi OP3 `servo_idle` baru memproses 1.501 frame dalam sekitar 59,61 detik (sekitar 25,16 FPS berdasarkan interval frame terproses), 1.806 frame diterima, 304 tertimpa dalam antrean aplikasi, dan 4.454 baris deteksi. Angka tersebut merupakan pengamatan runtime satu sesi, bukan akurasi atau perbandingan kausal KD versus baseline. Rincian pada `dokumentasi/2026-10-19/percobaan-04-live-tracking-servo-idle/README.md`.

## Kesenjangan dan risiko interpretasi

1. **Nama model dan judul skripsi.** D1 kini diputuskan untuk memakai teacher YOLO11n → student skala `t`. Checkpoint sekarang tidak memenuhi definisi student YOLO11n standar; rumusan masalah sebaiknya menyebut “distilasi dari YOLO11n ke student YOLO11 yang diperkecil”.
2. **KD lebih rendah dari kontrol.** Selisih mAP50–95 dan precision menunjukkan trade-off nyata. Diagnosis VAL pada tujuh checkpoint kini tersedia di `analisis_performa/lab_server/DIAGNOSIS_VAL_2026-10-20.md`: FP duplikasi lebih banyak pada KD; memilih ambang confidence di VAL menaikkan F1 tetapi belum menyamai supervised. Ini observasi, belum membuktikan sebab dari objective.
3. **TEST telah dilihat.** TEST pernah dipakai untuk model sumber pada 24 September dan hasil eksperimen kini sudah diketahui. Jika objective/arsitektur dituning lagi, hasil pada split TEST yang sama perlu dinyatakan sebagai evaluasi lanjutan atas benchmark yang sudah diketahui; klaim konfirmasi independen memerlukan test baru yang benar-benar ditahan, idealnya sesi/adegan terpisah.
4. **Provenance teacher terbatas.** Hash checkpoint diketahui, tetapi manifest teacher tidak mencatat versi dataset dan YAML training lama hilang. Kesamaan byte TRAIN/VAL teacher dengan snapshot kini tidak dapat dibuktikan.
5. **OP3 belum menjawab seluruh rumusan masalah.** T16/T17 benchmark CPU frame tetap belum ada; T19 walking belum ada; T27 mAP/P/R/F1 frame kamera OP3 berlabel belum ada. Hasil OP3 sekarang hanya mendukung bahwa pipeline berjalan dan observasi runtime awal.
6. **Jalur runtime berbeda.** README dan `OP3_PYTORCH_RUNTIME.md` telah diperbarui dalam audit ini agar mengakui sesi `op3_idle_trial`. Node lama `scripts/op3_pytorch_detector.py` masih memakai QoS `BEST_EFFORT`, sedangkan sesi idle baru memakai subscriber `reliable`; hasil keduanya tidak boleh digabung sebagai protokol identik.
7. **Ketergantungan dan reproduksi.** Teacher, dataset, dan Python training direferensikan lewat path absolut di repo `rafli/advance_vision`; sumber tersebut ada pada host audit, tetapi repo ini saja belum cukup untuk reproduksi penuh di mesin lain. GPU NVIDIA tidak dapat diakses dari shell audit ini (`nvidia-smi` gagal), sehingga jangan memulai pilot/training sampai berada pada host GPU yang sesuai. Sebanyak 15 file `.pt` terlacak di Git; keputusan penyimpanan artefak D9 masih terbuka.
8. **Kurasi tabel.** `analisis_performa/lab_server/manifest.json` adalah jejak hash T01–T14. `scripts/build_performance_tables.py` dapat menimpa kurasi tersebut saat dijalankan ulang; tinjau diff dan manifest sebelum menerima regenerasi.

## Langkah lab/server yang disarankan

### 1. Kunci ruang lingkup model (D1) dan protokol — selesai 20 Oktober

Bhre menyetujui teacher YOLO11n → student YOLO11 skala `t` yang sudah selesai. Keputusan dicatat di `configs/analysis.yaml` dan `docs/DECISIONS.md`. Revisi judul dan rumusan masalah agar arsitektur disebut akurat. D2 tetap KD murni; mode hybrid dalam prompt lama berada di luar lingkup. Tidak ada kewajiban training ulang agar hasil eksperimen yang ada sah dilaporkan.

### 2. Diagnosis VAL menggunakan checkpoint yang ada — selesai 20 Oktober

Prediksi per gambar untuk teacher, tiga KD, dan tiga supervised pada VAL telah dibuat dan hash gambar/label cocok. T09 (FP/FN/duplikasi/lokalisasi), T10 (matriks kebingungan), T11 (sapu confidence), dan T14 (kalibrasi) telah diisi. Ringkasan serta batas interpretasi ada di `analisis_performa/lab_server/DIAGNOSIS_VAL_2026-10-20.md`. D4 belum dikunci untuk runtime OP3: ambang F1 VAL terbaik dapat menurunkan recall gawang dan perlu dinilai pada frame kamera berlabel. T08 dan T12 dapat menyusul jika diperlukan. T05 dapat dilengkapi dengan interval rerata lintas-seed yang metodologinya ditulis jelas; jangan mencampur bootstrap per checkpoint dengan SD antar-seed.

### 3. Jika ingin memperbaiki KD, siapkan pilot yang terpisah

Audit arti tensor Detect head pada versi Ultralytics yang dipakai. Pertahankan hasil `pure_v4` sebagai acuan saat memodularisasi loss; kandidat murni berbobot teacher dapat dicoba pada satu seed dan dinilai hanya di VAL. `pure_dfl_kl` baru masuk kandidat jika `boxes` terbukti logit DFL yang sesuai. Isi T04 dari pilot dan catat keputusan objective, epoch (D3), seed, hyperparameter, dan hash kode sebelum training utama. Jika tidak mengejar peningkatan, lewati pilot dan pertahankan model kini.

### 4. Siapkan paket pengukuran OP3 dari lab

Siapkan alat probe kamera tanpa model, perekaman frame tetap ber-hash, benchmark CPU dengan tahap preprocess/inference/postprocess serta sapuan thread, dan checklist sesi robot. Jalur `ros2_packages/op3_idle_trial` sudah memberi pengamatan live awal, tetapi T16/T17/T22/T23/T27 memerlukan protokol tambahan. Bekukan checkpoint, kelas, ukuran input, confidence, QoS, preview, dan jumlah thread untuk perbandingan teacher/KD/supervised. Operator robot kemudian mengumpulkan sesi `servo_idle` dan `walking` dengan prosedur sebanding serta frame kamera berlabel untuk mAP/P/R/F1 pada domain OP3.

### 5. Evaluasi akhir dan naskah

Jika eksperimen baru dijalankan, gunakan run dan manifest baru, pilih checkpoint di VAL, dan perlakukan TEST historis sesuai batas pada poin 3. Jangan menimpa artefak terkunci. Setelah bukti OP3 lengkap, gabungkan hasil dataset, benchmark CPU, live FPS/CPU/RAM, dan akurasi kamera dalam Bab IV–V dengan asal metrik jelas. Perbarui README, runtime, proposal, abstrak, serta indeks tabel agar judul dan status OP3 konsisten.

**Prioritas terdekat lab/server setelah diagnosis:** bila ingin menaikkan kualitas KD, rancang satu pilot `pure_weighted` pada VAL dengan `pure_v4` tetap sebagai acuan; jangan mulai training utama atau memakai TEST untuk memilih konfigurasi. Untuk skripsi dengan model saat ini, lanjutkan penyusunan naskah dan alat ukur OP3.
