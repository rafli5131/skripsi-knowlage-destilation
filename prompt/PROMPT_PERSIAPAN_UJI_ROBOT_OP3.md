# Prompt Persiapan Sebelum Uji Robot OP3

> Salin seluruh isi bagian **Prompt** ke agen koding yang membuka *repository* ini di server lab (`/mnt/nas-hpg9/rafli5131/bre`). Versi 22 Oktober 2026, disusun dari analisis repo pada *commit* `e0ebb91`. Prompt ini menyiapkan semua yang harus beres **sebelum** sesi di robot: dokumen konfirmasi rumusan masalah, pencatatan keputusan model, pemindahan *teacher* ke OP3, parameter runtime yang terkunci, dan prompt robot versi baru. Tidak ada sesi robot yang dijalankan dari prompt ini.

---

## Prompt

### 0. Peran dan prinsip kerja

Anda adalah agen koding yang membantu Bhre (Teknik Komputer FILKOM Universitas Brawijaya) menyiapkan uji robot skripsi *knowledge distillation* (KD) untuk deteksi `ball`, `gawang`, dan `robot` pada ROBOTIS OP3.

1. Keabsahan eksperimen lebih penting daripada kecepatan.
2. Verifikasi dari kode yang ada sebelum mengubahnya, lalu sebutkan berkas dan barisnya di laporan.
3. Berhenti di setiap titik henti (TH) dan tunggu persetujuan tertulis Bhre.
4. Tulis kode sederhana dan eksplisit agar Bhre dapat menjelaskannya baris per baris.
5. Jangan mengarang angka, rujukan, atau keputusan. Sel tanpa data diisi `[BELUM DIUKUR]`.
6. Bila Anda tidak yakin pada suatu fakta teknis, nyatakan tidak yakin dan tunjukkan cara memverifikasinya.

### 1. Konteks yang sudah diverifikasi pada `e0ebb91`

**Rumusan masalah** (disetujui Bhre pada 22 Oktober 2026, **belum** dikonfirmasi pembimbing; tipe penelitian implementatif-pengembangan):

1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil *knowledge distillation* (KD) pada robot humanoid ROBOTIS OP3?
2. Bagaimana tingkat akurasi, berdasarkan nilai *mean average precision* (mAP), model YOLO11 skala t hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?
3. Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?
4. Berapa rata-rata latensi dan *frames per second* (FPS) yang dicapai model hasil KD dan *teacher* YOLO11n saat beroperasi secara *real-time* pada kondisi robot diam dan berjalan?
5. Bagaimana tingkat efisiensi penggunaan CPU dan RAM model hasil KD dan *teacher* YOLO11n saat dijalankan secara penuh pada komputer *onboard* robot?

Menurut keputusan Bhre, "model hasil KD" adalah varian yang terpilih di VAL antara KD murni dan KD hibrida; varian lain dilaporkan sebagai ablasi. Pembanding runtime pada rumusan 4 dan 5 adalah *teacher*, bukan *supervised*, karena arsitektur *supervised* identik dengan model hasil KD.

**Hasil lab yang sudah ada:**
- VAL, rerata 3 *seed*: mAP50-95 `hybrid_full` 0,7505 ± 0,0018, *supervised* 0,7208 ± 0,0041, `pure_v4` sekitar 0,679 (T04, T28).
- TEST: `hybrid_full` 0,7469 ± 0,0022, *supervised* 0,7225 ± 0,0035, *teacher* 0,7800, `pure_v4` 0,6630 (T05, T30). F1 pada ambang 0,25: `hybrid_full` 0,9071, *supervised* 0,9121.
- Kandidat OP3: `hybrid_full_seed1337`, `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt`, SHA-256 `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`, dipilih dari VAL sebelum TEST dibuka.

**Celah yang ditangani prompt ini:**
- `prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3.md` membandingkan runtime hibrida dengan *supervised*, bukan *teacher*, sehingga rumusan 4 dan 5 tidak terjawab.
- *Teacher* belum pernah dijalankan di OP3. Entri `teacher_fp32` di `configs/model_registry.yaml` menunjuk path absolut NAS, sedangkan `validate_checkpoint` di `scripts/model_registry.py` mensyaratkan path yang sama persis. Akibatnya, *teacher* di path lain di OP3 akan ditolak.
- `scripts/op3_pytorch_detector.py` belum punya parameter jumlah *thread*, penanda *warm-up*, atau durasi sesi. Sesi sebelumnya memakai 7 sampai 13 *logical CPU* tanpa batas, yang berisiko mengganggu kendali gerak saat berjalan.
- Ambang runtime (D4) dan jumlah *thread* (D6) belum dikunci.

### 2. Batasan dan larangan

- Jangan menjalankan robot, kamera, servo, atau sesi ROS live dari prompt ini.
- Jangan menimpa, memindahkan, atau menghapus *checkpoint*, run, *manifest*, atau entri registri yang sudah ada. Alias `op3_default` tetap menunjuk KD murni *seed* 42.
- **Bobot *teacher* tidak boleh di-*commit* atau di-*push*.** Repo bersifat publik, dan *teacher* berasal dari proyek Advance Vision. Pemindahan hanya lewat jalur privat.
- Perubahan kode harus menjaga perilaku bawaan: perintah lama tanpa parameter baru menghasilkan perilaku yang sama, kecuali tambahan kolom log di akhir.
- Kode ROS 2 baru di `ros2_packages/` harus berada di paket baru. Paket lama tidak diubah.
- Jangan menjalankan `git clean` atau `git reset --hard`. Jangan `push` tanpa izin. Buat *commit* kecil per tugas.

### 3. Alur kerja dan titik henti

```
Fase 0  Persiapan
Fase 1  Dokumen konfirmasi rumusan masalah untuk pembimbing
Fase 2  Pencatatan keputusan model                           -> TH-1
Fase 3  Teacher di OP3: override path lokal dan prosedur transfer
Fase 4  Parameter runtime detektor dan usulan D4, D6         -> TH-2
Fase 5  Prompt robot versi 2                                 -> TH-3
Fase 6  Opsional: benchmark frame tetap
```

### 4. Fase 0: persiapan

1. Jalankan `git status` dan `git pull --ff-only`, lalu catat *commit* awal.
2. Baca `docs/DECISIONS.md`, `configs/analysis.yaml`, `configs/model_registry.yaml`, `scripts/model_registry.py`, `scripts/op3_pytorch_detector.py`, `OP3_PYTORCH_RUNTIME.md`, `prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3.md`, `analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md`, dan `analisis_performa/INDEKS.md`.

### 5. Fase 1: dokumen konfirmasi untuk pembimbing

Tulis `docs/KONFIRMASI_RUMUSAN_MASALAH_2026-10-22.md` berisi:

- lima rumusan masalah di bagian 1, apa adanya, dengan status "disetujui Bhre, menunggu konfirmasi pembimbing";
- tabel rumusan, bukti yang sudah ada (dengan path sumber), dan bukti yang belum ada;
- pertanyaan untuk pembimbing:
  1. apakah pembanding runtime cukup *teacher*, atau *supervised* juga perlu diukur;
  2. apakah akurasi pada frame kamera OP3 termasuk rumusan 2 dan 3, atau hanya data pendukung;
  3. apakah "model hasil KD" = `hybrid_full` dengan `pure_v4` sebagai ablasi dapat diterima;
  4. definisi kondisi "berjalan": berjalan di tempat, berjalan maju di area aman, atau di atas *stand*;
  5. jumlah dan durasi sesi runtime yang dianggap cukup.

Dokumen ini tidak boleh menyatakan rumusan sudah disetujui pembimbing.

### 6. Fase 2: pencatatan keputusan model

Tambahkan baris baru di `docs/DECISIONS.md` dan kunci baru di `configs/analysis.yaml`, tanpa menghapus yang lama:

- "Model hasil KD" dalam naskah = `hybrid_full` (3 *seed*), sesuai aturan pemilihan VAL yang disetujui Bhre. Sertakan angka VAL dan path sumbernya.
- `pure_v4` dan `hybrid_feature` dilaporkan sebagai ablasi.
- Kandidat runtime OP3 = `hybrid_full_seed1337`. Alias `op3_default` belum diganti sampai ada bukti robot dan keputusan Bhre.

**TH-1:** laporkan dokumen Fase 1 dan baris keputusan Fase 2.

### 7. Fase 3: *teacher* di OP3

**7.1 Override path lokal yang tetap memeriksa hash.** Perluas `scripts/model_registry.py`:

- baca berkas opsional `configs/model_registry_local.yaml` (masukkan ke `.gitignore`) yang hanya berisi pemetaan nama model ke path lokal, misalnya `teacher_fp32: models_local/teacher_fp32_best.pt`;
- bila berkas ada, path lokal menggantikan path registri **hanya** untuk model yang disebut, dan SHA-256 berkas lokal **wajib** sama dengan `sha256` di registri utama;
- bila berkas tidak ada, perilaku tidak berubah;
- detektor mencatat di JSON run apakah *override* dipakai, path lokalnya, dan hash yang terverifikasi;
- tambahkan `models_local/` ke `.gitignore`;
- tulis tes di `tests/` dengan registri dan berkas *checkpoint* palsu di direktori sementara: tanpa *override*, *override* dengan hash cocok, dan *override* dengan hash salah (harus gagal).

Periksa juga bahwa `model_variant:=supervised` dengan path `supervised_seed1337` lolos validasi. Bila tidak, perbaiki tanpa mengubah pemetaan bawaan dan tambahkan tesnya.

**7.2 Prosedur transfer.** Tulis `docs/TRANSFER_TEACHER_KE_OP3.md`:

- hitung SHA-256 *teacher* di server dan cocokkan dengan `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`;
- perintah `scp` atau `rsync` ke `<repo OP3>/models_local/teacher_fp32_best.pt`, atau lewat laptop atau USB bila server tidak dapat menjangkau OP3;
- perintah `sha256sum` di OP3 dan contoh isi `configs/model_registry_local.yaml`;
- larangan *commit* dan *push* bobot *teacher*.

Jalankan transfer sendiri hanya bila Bhre mengizinkan dan jaringan serta kredensialnya sudah tersedia. Bila tidak, cukup tuliskan perintahnya.

### 8. Fase 4: parameter runtime dan usulan D4 serta D6

**8.1 Parameter baru di `scripts/op3_pytorch_detector.py`**, semuanya dengan bawaan yang mempertahankan perilaku lama:

- `torch_num_threads` (bawaan 0, artinya tidak diubah) dan `torch_interop_threads` (bawaan 0). Bila lebih dari 0, panggil `torch.set_num_threads` dan `torch.set_num_interop_threads` sebelum model dimuat;
- `warmup_frames` (bawaan 30): menandai kolom `is_warmup` di CSV tanpa mengubah pemrosesan;
- `duration_s` (bawaan 0, artinya tanpa batas): node berhenti sendiri dengan rapi setelah durasi itu, dihitung sesudah *warm-up*;
- JSON run mencatat jumlah *thread* aktual (`torch.get_num_threads()`), jumlah *logical CPU*, model CPU, dan FPS efektif dari *timestamp* kamera setelah *warm-up* sebagai kolom baru (`effective_fps_after_warmup`). Kolom dan nilai lama tidak diubah.

Pindahkan perhitungan FPS efektif dan penanda *warm-up* ke fungsi murni yang bisa diuji tanpa ROS, lalu tulis tesnya di `tests/`.

**8.2 Usulan D6 (jumlah *thread*)** di `configs/analysis.yaml`, status `BELUM DIKUNCI`:

- kandidat 2, 4, 6, dan 8 *thread*, diukur dengan hibrida pada kondisi diam, 60 detik per kandidat setelah *warm-up*, *preview* mati;
- aturan pemilihan: pilih jumlah *thread* terkecil yang median latensi *end-to-end*-nya paling banyak 10% di atas kandidat terbaik **dan** FPS efektifnya minimal 95% dari kandidat terbaik;
- nilai terpilih dipakai sama untuk semua model dan kondisi. Alasannya: menyisakan CPU untuk `op3_manager` saat berjalan.

**8.3 Usulan D4 (ambang runtime)**, status `BELUM DIKUNCI`: *confidence* 0,25 dan NMS IoU 0,45 untuk semua model di robot, agar sebanding dengan sesi sebelumnya. Ambang F1 terbaik dari VAL hanya dilaporkan sebagai analisis kepekaan offline.

**TH-2:** tampilkan *diff*, hasil tes, serta usulan D4 dan D6. Tunggu persetujuan.

### 9. Fase 5: prompt robot versi 2

Tulis `prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3_V2.md`. Jangan menghapus versi lama; tambahkan satu catatan di awal berkas lama yang menunjuk ke versi 2. Versi 2 wajib memuat:

1. **Audit awal di OP3:** *commit*, `git status`, OS, Python, ROS, versi PyTorch, Ultralytics, dan OpenCV, `lscpu`, `free -h`, *governor* CPU (dicatat, tidak diubah), status `op3_manager`, topic kamera beserta tipe dan lajunya, serta SHA-256 hibrida 1337, *teacher* (lewat `configs/model_registry_local.yaml`), dan *supervised* 1337 bila dipakai.
2. **Sesi 0, pemilihan *thread*:** jalankan aturan D6 yang sudah disetujui, lalu minta konfirmasi Bhre atas nilai terpilih sebelum sesi utama.
3. **Sesi A, fungsi dan *capture*:** hibrida pada kondisi diam dengan *viewer* dan *capture* frame mentah. Hasilnya bukti fungsi untuk rumusan 1 dan sumber gambar, bukan *benchmark*.
4. **Sesi B, matriks runtime bersih** untuk rumusan 4 dan 5:
   - model hibrida 1337 dan *teacher* × kondisi `servo_idle` dan `walking` × 3 ulangan × 60 detik setelah *warm-up*;
   - *preview* mati, tanpa *viewer* dan *capture*, *thread* sesuai D6, ambang sesuai D4, pengaturan *tracking* sama;
   - urutan model bergantian di dalam setiap kondisi (misalnya hibrida, *teacher*, *teacher*, hibrida, hibrida, *teacher*);
   - jeda antarsesi minimal 2 menit, dengan suhu CPU dicatat di awal dan akhir sesi;
   - *supervised* 1337 opsional, cukup 1 sesi per kondisi untuk menunjukkan runtime-nya setara dengan hibrida.
5. **Protokol `walking`:** operator menjalankan modul jalan ROBOTIS lewat `op3_manager` sesuai definisi kondisi berjalan yang dikonfirmasi pembimbing. Agen tidak pernah mengirim perintah gerak dan tidak menjalankan `op3_head_ball_tracking`. Catat waktu mulai dan berhenti berjalan dari operator, dan hentikan sesi bila robot tidak stabil. Label `walking` hanya dipakai bila kondisi itu terverifikasi.
6. **Sesi C, evaluasi offline di OP3, tanpa gerak robot:**
   - evaluasi hibrida 1337, *supervised* 1337, dan *teacher* pada set berlabel 260 + 50 frame yang sudah ada, ditambah set baru setelah ditinjau manusia;
   - pakai evaluator, label, dan pengaturan yang sama dengan T27;
   - catat bahwa label lama dibuat dari draf KD murni.
7. **Penanganan data:** jangan *commit* atau *push* gambar, label, atau log robot. Cadangkan ke server lab lewat jalur yang disetujui Bhre beserta *manifest* hash.
8. **Pelaporan:** dokumen per sesi di `dokumentasi/<tanggal>/`, pembaruan T15, T18, T19, T20, T21, T23, T26, dan T27 hanya dari bukti robot, serta `[BELUM DIUKUR]` untuk yang belum ada. Rumusan 4 dan 5 dilaporkan per kondisi dan per model dalam bentuk median dan p95 dari ketiga ulangan.

**TH-3:** tampilkan prompt versi 2. Tunggu persetujuan Bhre sebelum prompt itu dipakai di robot. Ingatkan bahwa rumusan masalah masih menunggu konfirmasi pembimbing.

### 10. Fase 6 (opsional): *benchmark* frame tetap

Bila Bhre meminta T16 dan T17, kerjakan Fase 4.2 dari `prompt/PROMPT_LAB_SERVER_TANPA_ROBOT.md` (paket baru `ros2_packages/op3_runtime_benchmark/`). Rumusan 4 dan 5 tetap dijawab dari sesi live bersih di Sesi B, sehingga fase ini tidak wajib.

### 11. Standar kode dan dokumen

- Python bertipe dengan *docstring* Bahasa Indonesia singkat, modul `logging`, dan `pathlib`. Jalankan tes sebelum setiap *commit*.
- Dokumen ditulis dalam Bahasa Indonesia ragam baku akademis:
  - tanpa tanda pisah *em dash*;
  - memakai "algoritme" (bukan "algoritma") dan "analisis" (bukan "analisa"), serta tidak memakai "rancang bangun";
  - istilah asing dicetak miring kecuali nama produk;
  - setiap klaim faktual bersitasi atau diberi penanda `[BUTUH SITASI: ...]`;
  - dilarang mengarang nama penulis, tahun, judul, atau DOI.

### 12. Format laporan di setiap titik henti

1. Yang dikerjakan, ringkas.
2. Berkas yang dibuat atau diubah, beserta *commit*-nya.
3. Perintah yang dijalankan dan hasilnya; setiap angka disertai path sumber.
4. Penyimpangan dari prompt ini beserta alasannya.
5. Keputusan atau informasi yang dibutuhkan dari Bhre.

### 13. Mulai dari sini

Kerjakan Fase 0 sampai Fase 2, lalu berhenti di TH-1.
