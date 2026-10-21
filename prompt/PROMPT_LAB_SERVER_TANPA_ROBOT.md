# Prompt Kerja Lab/Server Tanpa Robot

> Salin seluruh isi bagian **Prompt** ke agen koding yang membuka *repository* ini di server lab (`/mnt/nas-hpg9/rafli5131/bre`). Versi 21 Oktober 2026, disusun dari analisis repo pada *commit* `fafe2aa`. Prompt ini mencakup pekerjaan kelompok A: semua pekerjaan yang tidak memerlukan robot, kamera, maupun komputer OP3. Bila bertentangan dengan `prompt/PROMPT_PERBAIKAN_KODE_DAN_ANALISIS_PERFORMA.md` atau `prompt/PROMPT_TABEL_LAB_SERVER_KD.md`, ikuti prompt ini dan laporkan pertentangannya.

> **Pembaruan 21 Oktober 2026:** pembimbing menyetujui KD hibrida. **Fase 2 dan Fase 3 (pilot `pure_box_weighted`) tidak dijalankan**, kecuali Bhre memintanya secara tertulis. Sebagai gantinya, jalankan `prompt/PROMPT_KD_HIBRIDA_LAB_SERVER.md`. Fase 0, 1, 4, 5, dan 6 di prompt ini tetap berlaku.

---

## Prompt

### 0. Peran dan prinsip kerja

Anda adalah agen koding dan analisis yang membantu Bhre (Teknik Komputer FILKOM Universitas Brawijaya) menyelesaikan skripsi *Knowledge Distillation* (KD) untuk deteksi `ball`, `gawang`, dan `robot` pada ROBOTIS OP3. Semua angka akan dipertanggungjawabkan di sidang, sehingga berlaku prinsip berikut.

1. Keabsahan eksperimen lebih penting daripada kecepatan.
2. Verifikasi dari kode sumber Ultralytics 8.4.130 yang terpasang sebelum memakai API apa pun, lalu sebutkan berkas dan barisnya di laporan.
3. Berhenti di setiap titik henti (TH) dan tunggu persetujuan tertulis Bhre sebelum lanjut, kecuali bagian yang secara eksplisit boleh berjalan sejajar.
4. Tulis kode sederhana dan eksplisit agar Bhre dapat menjelaskannya baris per baris.
5. Tidak ada jalan pintas diam-diam. Bila gagal, berhenti dan laporkan.
6. Jangan mengarang angka, rujukan, atau hasil. Sel tanpa data diisi `[BELUM DIUKUR]`.
7. Bila Anda tidak yakin pada suatu fakta teknis, nyatakan tidak yakin dan tunjukkan cara memverifikasinya.

### 1. Konteks yang sudah diverifikasi pada `fafe2aa`

- **Keputusan terkunci** (`docs/DECISIONS.md`, `configs/analysis.yaml`): D1 *teacher* YOLO11n dan *student* YOLO11 kustom skala `t` (810.649 parameter); D2 *pure teacher-only KD* `pure_v4`. D3 sampai D10 belum dikunci.
- **Pilot `pure_weighted` cacat rancangan.** Spesifikasinya berasal dari bagian 5.2 prompt perbaikan: *loss* kotak **dan** *loss* kelas dibobot w_i = max_c σ(z_teacher). Pada *anchor* latar w_i ≈ 0, sehingga BCE kelas hampir tidak memberi sinyal untuk menekan skor latar. Hasil VAL sesuai dugaan itu: *precision* 0,0473 (`pure_v4` *seed* 42: 0,7899), *recall* 0,9906, mAP50-95 0,5907 (`pure_v4` *seed* 42: 0,6826). Hasil negatif ini tidak membuktikan bahwa pembobotan lokasi tidak berguna.
- **Diagnosis VAL** (`analisis_performa/lab_server/DIAGNOSIS_VAL_2026-10-20.md`): pada ambang 0,25, KD menghasilkan 0,348 FP per gambar dibanding *supervised* 0,261, dengan duplikasi rata-rata 223 berbanding 133.
- **T27, evaluasi kamera OP3 eksploratif**: mAP50-95 KD 0,422 dan *supervised* 0,419 pada 260 frame. Recall `gawang` 0,150 dan 0,250; kedua model 0/40 `gawang` pada sesi `robot_gawang_01`. Padahal pada uji *tracking* live `gawang` terdeteksi di 100% frame. Set gawang parsial (label satu tiang) memberi KD 40/50 dan *supervised* 0/50, tetapi label awal dibuat dari prediksi KD. Kotak `robot` 5,7 sampai 7 kali lebih luas dari label manusia. *Teacher* belum dievaluasi pada frame OP3. Evaluasi offline memakai NMS 0,7, sedangkan runtime memakai 0,45.
- **Definisi F1 belum seragam**: T04 dan T05 memakai F1 = 2·P_makro·R_makro / (P_makro + R_makro), mengikuti evaluator TEST. T27 memakai rerata F1 per kelas.
- **Jalur runtime OP3 terpecah**: `scripts/op3_pytorch_detector.py` (QoS BEST_EFFORT kedalaman 1, *callback* serial, BoT-SORT), `ros2_packages/op3_idle_trial` (QoS *reliable*), `ros2_packages/op3_live_monitor` (QoS RELIABLE kedalaman 5, *worker thread*, BoT-SORT), dan `ros2_packages/op3_head_ball_tracking` (memakai `op3_live_monitor` dan menggerakkan servo kepala 19/20). Hasilnya tidak setara: sesi `op3_idle_trial` 24,90 FPS dan CPU 1.022%; uji *tracking* `20261021_tracking_live_01` 12,09 FPS dan CPU 1.349,8% dari 16 CPU logis. T26 saat ini mengambil kolom runtime dari `op3_idle_trial`.
- **Audit hash** (`artifacts/phase_a_hash_audit_final_20261019.json`): 172 PASS, 9 MISMATCH. Selisih muncul karena skrip diubah setelah run. Versi asli `scripts/train_supervised_baseline.py` (SHA-256 `a6dc2bf8ec10c426e01c75123129b1507e94e2e83c50fbca0e8ce48e22b173c1`) dan `scripts/evaluate_locked_test.py` untuk `pure_kd_official_split_locked_retry1` (SHA-256 `6719973e1db8211b03b2b25e6fc6fd40bdf8face02af64566313d50c0fa79e60`) sudah diverifikasi ada di *commit* `965e8d8`.
- **Naskah**: `DRAF_PROPOSAL_BAB_I-III.md`, `DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`, `DRAF_ABSTRAK_SKRIPSI.md`, `KERANGKA_BAB_SKRIPSI.md`, `PLANNING_SKRIPSI.md`, dan `PROTOKOL_EKSPERIMEN_SKRIPSI.md` belum berubah sejak `965e8d8` (14 Oktober 2026).
- **Data OP3**: 310 frame berlabel manusia dan labelnya hanya ada di komputer OP3 (`data/op3_camera_eval/sessions/`, diabaikan Git). Di server, folder itu mungkin belum ada.

### 2. Batasan dan larangan

- Jangan menjalankan robot, kamera, servo, atau sesi ROS live. Jangan menyentuh `op3_head_ball_tracking`.
- Tanpa OpenVINO, ONNX untuk penerapan, INT8, PTQ, QAT, atau argumen `quantize`.
- TEST tidak boleh dipakai untuk memilih apa pun. Jangan membaca label TEST untuk audit definisi kotak. Semua seleksi di VAL.
- Jangan menimpa, memindahkan, atau menghapus run, *manifest*, log, *checkpoint*, atau draf naskah lama. Run dan dokumen baru memakai nama baru.
- Jangan menjalankan `git clean`, `git reset --hard`, atau perintah lain yang membuang berkas tak terlacak. Workspace server berisi banyak berkas eksperimen yang belum terlacak.
- Kode ROS 2 baru harus berada di **paket baru**. Paket lama boleh diimpor sebagai *shared dependency*, tetapi isinya tidak boleh diubah.
- Mode KD yang sudah ada (`pure_v4`, `pure_weighted`) harus tetap berperilaku sama persis. Mode baru ditambahkan tanpa mengubah fungsi lama.
- D9 (penyimpanan artefak) belum dikunci: jangan memigrasikan riwayat Git ke LFS atau mengompres berkas yang sudah terlacak.
- Jangan memasang atau memutakhirkan paket di venv pelatihan tanpa izin. Bila `pytest` tidak tersedia, tanyakan dulu.
- Jangan `push` tanpa izin. Buat *commit* kecil per tugas dengan pesan yang jelas.

### 3. Alur kerja dan titik henti

```
Fase 0  Persiapan dan pemeriksaan lingkungan
Fase 1  Perbaikan T27, definisi F1, catatan pilot             -> TH-1
Fase 2  Mode loss pure_box_weighted dan tes                    -> TH-2 (izin training)
Fase 3  Pilot pure_box_weighted seed 42 dan evaluasi VAL       -> TH-3
Fase 4  Persiapan protokol runtime OP3 dan alat benchmark      -> TH-4
Fase 5  Kerapian repo dan provenance                           (dilaporkan di TH-4)
Fase 6  Naskah: proposal Bab I-III dan Bab IV sementara        -> TH-akhir
```

Selama pelatihan Fase 3 berjalan di `tmux`, Fase 4, 5, dan 6 boleh dikerjakan sejajar.

Fase 2 dan Fase 3 diganti oleh `prompt/PROMPT_KD_HIBRIDA_LAB_SERVER.md` (lihat pembaruan di awal berkas). Pelatihan KD hibrida dari prompt itu juga boleh berjalan sejajar dengan Fase 4, 5, dan 6.

### 4. Fase 0: persiapan

1. Jalankan `git status`, lalu `git pull --ff-only`. Catat *commit* awal. Jangan menyentuh berkas tak terlacak.
2. Pakai interpreter `env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python`. Catat versi Python, PyTorch, dan Ultralytics.
3. Jalankan `nvidia-smi`. Bila gagal, Fase 3 tidak boleh dimulai; laporkan.
4. Periksa apakah `data/op3_camera_eval/sessions/` ada di server dan apakah hash berkasnya cocok dengan `runs/op3_multi_session_eval/20261021_primary260_partial50_v1/input_manifest.json`. Hasil pemeriksaan ini menentukan langkah 5.5.

### 5. Fase 1: tabel dan dokumentasi

**5.1 Penyeragaman definisi F1.** Usulkan F1 utama = 2·P_makro·R_makro / (P_makro + R_makro), sama dengan evaluator TEST yang terkunci, dan rerata F1 per kelas sebagai kolom sekunder dengan nama berbeda. Catat usulan ini sebagai D11 di `configs/analysis.yaml` dengan status `BELUM DIKUNCI`. Perbarui `analisis_performa/DEFINISI.md`. Hitung ulang baris makro T27 dari TP/FP/FN per kelas yang tersimpan di `summary.csv` dan `results.json`, tanpa inferensi ulang. Periksa bahwa T04, T05, dan T27 memakai definisi yang sama.

**5.2 Audit definisi kotak `gawang`.** Tulis `scripts/audit_gawang_box_geometry.py`:

- baca label YOLO TRAIN dan VAL dari path di `configs/data_train_val.yaml` (folder `labels` sejajar `images`), tanpa label TEST;
- untuk setiap kelas, hitung jumlah kotak, jumlah kotak per gambar, lebar dan tinggi dalam piksel pada 640, rasio tinggi/lebar, dan luas, masing-masing dengan persentil 5, 25, 50, 75, 95;
- buat lembar gambar 30 potongan kotak `gawang` TRAIN yang dipilih acak dengan *seed* tetap;
- bila data OP3 tersedia dan hash cocok, hitung statistik yang sama dari `labels_reviewed/` untuk set utama dan set parsial secara terpisah;
- bila data OP3 belum ada, periksa apakah `per_frame_*.jsonl` atau `results.json` menyimpan kotak *ground truth*. Bila tidak, isi bagian OP3 dengan `[BELUM DIUKUR]` dan tuliskan perintah yang harus dijalankan setelah data disalin.

Simpan hasil di `analisis_performa/lab_server/AUDIT_DEFINISI_GAWANG_<tanggal>.md` beserta CSV dan lembar gambar. Kesimpulan hanya boleh menyatakan konvensi label yang terlihat, misalnya per tiang atau seluruh rangka. Jangan mengklaim penyebab kegagalan deteksi tanpa bukti.

**5.3 Asal frame negatif.** Telusuri cara `negative_candidate_01` dipilih dari `runs/op3_camera_eval/20261021_negative_candidate_01_fp_audit/`, `dokumentasi/2026-10-21/percobaan-02-frame-negatif/`, `dokumentasi/2026-10-21/percobaan-12-peninjauan-60-frame-negatif/`, dan *manifest capture* bila ada. Tentukan apakah pemilihan frame bergantung pada keluaran model. Bila tidak dapat dipastikan, tulis "tidak dapat dipastikan dari artefak".

**5.4 Status set gawang parsial dan bias anotasi.** Perbarui catatan T27 dan `analisis_performa/INDEKS.md`: set parsial dilaporkan sebagai catatan, **bukan** perbandingan KD dan *supervised*, karena definisi kotaknya berbeda dan label awalnya dibuat dari prediksi KD. Tonjolkan juga risiko bias anotasi pada set utama. Dokumentasi percobaan lama tidak diubah.

**5.5 Bersyarat: evaluasi tambahan frame OP3.** Hanya bila langkah 0.4 memastikan data lengkap dan hash cocok:

- evaluasi *teacher* pada set utama dan set parsial memakai paket `op3_multi_session_eval` dengan pengaturan yang sama persis, di direktori run baru;
- evaluasi ketiga model sekali lagi dengan NMS 0,45 sebagai konfigurasi runtime, dilaporkan sebagai baris sekunder;
- perbarui T27 dan *manifest*-nya.

Bila data belum ada, lewati dan tulis perintahnya untuk dijalankan setelah data disalin.

**5.6 Catatan pilot `pure_weighted`.** Tambahkan baris baru di `docs/DECISIONS.md` (baris lama tidak dihapus) dan catatan di T04: kegagalan pilot berasal dari spesifikasi yang membobot *loss* kelas sehingga sinyal penekanan skor latar hilang, bukan dari kesalahan implementasi.

**TH-1:** laporkan hasil 5.1 sampai 5.6, termasuk usulan D11, dan tunggu konfirmasi.

### 6. Fase 2: mode `pure_box_weighted`

1. Tambahkan fungsi baru di `scripts/kd_losses.py` tanpa mengubah `pure_weighted_head_losses`:
   - *loss* kotak: Smooth L1 per elemen, dibobot w_i = max_c σ(z_teacher), dinormalkan dengan Σw_i dan jumlah kanal, sama seperti `pure_weighted`;
   - *loss* kelas: BCE bertemperatur dengan rerata seragam atas **semua** *anchor* dan kanal, dikali T², identik dengan `pure_v4`.
2. Perluas `scripts/train_kd.py` agar menerima `mode: pure_box_weighted`. *Manifest* mencatat mode, deskripsi pembobotan, dan *snapshot* `kd_losses.py`. Perilaku `pure_v4` dan `pure_weighted` tidak berubah.
3. Buat `configs/kd_pure_box_weighted.yaml`, salinan `configs/kd_pure_weighted.yaml` yang hanya berbeda pada `mode` dan nama run `yolo11_tiny_pure_box_weighted_pilot_seed42`.
4. Tulis `tests/test_kd_losses.py` (tanpa GPU dan dataset, memakai tensor acak dengan *seed* tetap):
   - *loss* kelas mode baru sama persis dengan *loss* kelas `pure_v4`;
   - *loss* kotak mode baru sama persis dengan *loss* kotak `pure_weighted`;
   - gradien *loss* kelas terhadap *logit student* pada *anchor* latar (skor *teacher* mendekati nol) bernilai nyata pada mode baru dan mendekati nol pada `pure_weighted`; tes ini mendokumentasikan cacat pilot lama;
   - validasi bentuk tensor dan T ≤ 0 menghasilkan galat.
5. Uji asap 1 *epoch* dengan konfigurasi terpisah di `runs/kd_smoke/`. Catat sebagai uji asap; hasilnya tidak masuk tabel.
6. Tulis `docs/PILOT_PURE_BOX_WEIGHTED_<tanggal>.md` **sebelum** pelatihan, berisi kriteria keputusan yang dikunci lebih dulu:
   - metrik utama: mAP50-95 VAL dibanding `pure_v4` *seed* 42 (0,6826 pada evaluasi ulang T04), dengan pengaturan evaluasi yang sama;
   - metrik pendamping: P, R, F1 pada ambang 0,25, FP per gambar, dan duplikasi;
   - kandidat hanya layak dipertimbangkan bila mAP50-95 lebih tinggi. Pengulangan tiga *seed* tetap memerlukan keputusan baru Bhre;
   - TEST tidak dipakai.

**TH-2:** tampilkan *diff*, hasil tes, hasil uji asap, dan dokumen pra-registrasi. Tunggu izin pelatihan.

### 7. Fase 3: pilot dan evaluasi VAL

1. Jalankan pelatihan di `tmux`: `env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_kd.py --config configs/kd_pure_box_weighted.yaml`. Satu run `pure_v4` pada L40 sebelumnya memerlukan sekitar 5,4 jam.
2. Setelah selesai, evaluasi ulang memakai `scripts/evaluate_val_ablation.py` dengan pengaturan yang sama seperti pilot `pure_weighted` (1.213 gambar VAL, FP32, `imgsz` 640, NMS 0,7, *confidence floor* 0,001) ke `runs/val_ablation/pure_box_weighted_<tanggal>/`.
3. Jalankan diagnosis kategori FP pada VAL untuk *checkpoint* ini dengan `scripts/analyze_val_detections.py`.
4. Perbarui T04 dan T04 per kelas dengan `scripts/build_kd_ablation_table.py`, lalu perbarui *manifest* tabel.
5. Ambil keputusan sesuai kriteria pra-registrasi, tulis hasilnya di dokumen pilot, dan tambahkan baris baru di `docs/DECISIONS.md` serta kunci baru di `configs/analysis.yaml`. Kunci lama tidak dihapus.
6. *Checkpoint* deploy `models/weights/kd_student_best.pt` tidak boleh diganti.

**TH-3:** laporkan hasil dan keputusan.

### 8. Fase 4: persiapan runtime OP3

**8.1 Usulan protokol runtime tunggal.** Tulis `docs/USULAN_PROTOKOL_RUNTIME_OP3.md`. Bandingkan empat jalur runtime dalam satu tabel: QoS, model *threading*, *tracker*, *preview*, kolom log, dan kecocokannya untuk T16 sampai T26. Usulkan satu jalur beserta parameter yang dikunci: QoS, `conf` 0,25, NMS 0,45, `imgsz` 640, *preview* mati saat pengukuran, *tracker* hidup atau mati, dan jumlah *thread* dari T17. Ini usulan untuk D6 dan D7, bukan keputusan.

**8.2 Paket baru `ros2_packages/op3_runtime_benchmark/`.** Isinya:

- `benchmark_frames`: memuat folder frame tetap beserta *manifest* SHA-256; menjalankan varian dari `configs/model_registry.yaml` × `imgsz` × jumlah *thread*; memuat model sekali per blok di bawah `torch.inference_mode()`; mencatat *preprocess*, *inference*, *postprocess*, dan total per frame; membuang frame *warm-up*; mengacak urutan blok dengan *seed* tetap; mencatat suhu dan frekuensi CPU bila tersedia; menulis CSV per frame, CSV per blok, dan JSON metadata (hash *checkpoint*, jumlah *thread* aktual, model CPU);
- `camera_probe`: *subscriber* ROS tanpa model yang mencatat *timestamp* dan jeda frame, dengan QoS sebagai parameter.

Tulis tes untuk fungsi murni (persentil, urutan blok, statistik jeda) di `tests/`. Validasi kode `benchmark_frames` di CPU server memakai 30 gambar VAL sebagai pengganti frame. Simpan hasilnya di `runs/runtime_benchmark_smoke/` dengan label "uji kode, bukan data OP3", dan jangan masukkan ke T16 atau T17. Tuliskan perintah lengkap untuk dijalankan Bhre di OP3.

**8.3 T26.** Hentikan pencampuran protokol: tambahkan kolom protokol runtime atau kosongkan kolom runtime sampai protokol dikunci. Pilih opsi yang paling tidak menyesatkan dan jelaskan alasannya.

**8.4 T15.** Isi jumlah CPU logis (16) dari log percobaan 15 dan JSON run. Sel lain tetap `[BELUM DIUKUR]`. Tambahkan daftar perintah untuk Bhre di OP3: `lscpu`, `free -h`, *governor* CPU, dan mode daya.

**TH-4:** laporkan Fase 4 dan Fase 5.

### 9. Fase 5: kerapian dan provenance

1. Tulis `docs/PROVENANCE_SKRIP_PELATIHAN.md` yang menjelaskan 9 MISMATCH dan memetakan setiap hash ke *commit* asalnya. Dua hash di bagian 1 sudah terverifikasi di `965e8d8`; telusuri sisanya dengan `git log`. Selisih hash `last.pt` setelah *resume* dijelaskan sebagai perilaku normal bila memang demikian. Tambahkan tautannya di bagian *provenance* `README.md`, tanpa mengubah isi `PROTOKOL_EKSPERIMEN_SKRIPSI.md`.
2. Tulis tes untuk fungsi murni paket ROS 2 lama (IoU, baca label, ringkasan log) di `tests/`, mengimpor paket lewat `sys.path` tanpa mengubah paket. Modul yang memerlukan `rclpy` dilewati dengan `pytest.importorskip`. Fungsi yang tidak dapat diuji tanpa mengubah paket cukup dicatat.
3. Tulis `docs/USULAN_PENYIMPANAN_ARTEFAK_D9.md`: daftar berkas terlacak di atas 5 MB, ukuran *pack* Git, proyeksi pertumbuhan per sesi live, serta pilihan Git LFS, kompresi log baru di paket baru, rilis GitHub, atau penyimpanan NAS dengan hash. Jangan melakukan migrasi.
4. Tulis `scripts/verify_op3_data_copy.py` yang memeriksa salinan data OP3 di server terhadap hash di `input_manifest.json` evaluasi T27. Skrip ini dipakai setelah Bhre menyalin data dari OP3.
5. Tambahkan prompt ini dan dokumen baru ke `prompt/inventaris_tabel_dan_prompt.md`.

### 10. Fase 6: naskah

1. Jalankan `prompt/PROMPT_PROPOSAL_BAB_I-III_KD_OP3.md` secara utuh, dengan keluaran `DRAF_PROPOSAL_BAB_I-III_KD_OP3_REVISI.md`. Tambahkan aturan berikut:
   - rumusan masalah berbentuk "Bagaimana perbandingan …", satu pertanyaan per nomor, sesuai permintaan pembimbing;
   - usulkan 2 sampai 3 alternatif judul yang menyebut *student* sebagai YOLO11 skala `t` atau YOLO11 yang diperkecil, ditandai `[PERLU PERSETUJUAN PEMBIMBING]`;
   - masukkan hasil Fase 1 sampai 3: definisi F1, audit definisi `gawang`, cacat pilot `pure_weighted`, dan hasil pilot baru bila sudah ada;
   - penanda sitasi memakai format `[BUTUH SITASI: <apa yang dicari>]`, menggantikan `[SITASI PERLU VERIFIKASI]`.
2. Tulis `DRAF_BAB_IV_HASIL_SEMENTARA_KD_OP3.md` yang hanya memuat hasil yang sudah ada: TEST (T05 sampai T07), diagnosis VAL (T08 sampai T14), ablasi (T04), T27 sebagai bukti eksploratif, dan observasi runtime per sesi dengan protokolnya masing-masing. Perbandingan runtime antarvarian dan kondisi `walking` ditulis `[BELUM DIUKUR]`. Setiap angka disertai path sumbernya.
3. Draf lama tidak diubah.

**TH-akhir:** laporkan berkas naskah baru, daftar klaim beserta sumbernya, dan keputusan yang masih menunggu pembimbing.

### 11. Standar kode dan dokumen

- Python bertipe dengan *docstring* Bahasa Indonesia singkat, modul `logging`, dan `pathlib`.
- Jalankan tes sebelum setiap *commit*.
- Dokumen dan naskah ditulis dalam Bahasa Indonesia ragam baku akademis:
  - tanpa tanda pisah *em dash*;
  - memakai "algoritme" (bukan "algoritma") dan "analisis" (bukan "analisa"), serta tidak memakai "rancang bangun";
  - istilah asing dicetak miring kecuali nama produk;
  - setiap klaim faktual bersitasi atau diberi penanda `[BUTUH SITASI: ...]`;
  - dilarang mengarang nama penulis, tahun, judul, atau DOI.

### 12. Format laporan di setiap titik henti

1. Yang dikerjakan, ringkas.
2. Berkas yang dibuat atau diubah, beserta *commit*-nya.
3. Perintah yang dijalankan dan hasilnya; setiap angka disertai path berkas sumber.
4. Penyimpangan dari prompt ini beserta alasannya.
5. Keputusan atau informasi yang dibutuhkan dari Bhre.

### 13. Mulai dari sini

Baca `docs/DECISIONS.md`, `configs/analysis.yaml`, `analisis_performa/INDEKS.md`, `analisis_performa/DEFINISI.md`, `analisis_performa/tabel/T04_ablasi_kd_val.md`, `analisis_performa/tabel/T27_akurasi_frame_kamera_op3.md`, `analisis_performa/lab_server/DIAGNOSIS_VAL_2026-10-20.md`, `docs/PILOT_PURE_WEIGHTED_2026-10-20.md`, `scripts/kd_losses.py`, `scripts/train_kd.py`, dan `dokumentasi/2026-10-21/percobaan-13-evaluasi-deteksi-multi-sesi/README.md`. Kerjakan Fase 0 dan Fase 1, lalu berhenti di TH-1.
