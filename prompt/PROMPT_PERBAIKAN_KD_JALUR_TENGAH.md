# Prompt perbaikan objektif KD (jalur tengah) dengan ablasi *teacher* besar

> Versi 23 Oktober 2026, revisi diagnosis lab. Status: **Fase 0 selesai; Fase 1 sebagian selesai di server lab, belum ada training baru.** Keputusan Bhre pada 23 Oktober 2026:
> - **Jalur tengah:** jalur utama tetap A, yaitu *teacher* YOLO11n ke *student* YOLO11 skala t. D1 dan lima rumusan masalah tidak berubah. Objektif KD diperbaiki, dan *teacher* YOLO11s ke *student* skala t diuji sebagai ablasi **di VAL saja**.
> - **Uji live OP3 setara ditunda** sampai prompt ini selesai, agar model hasil KD yang diuji di robot adalah versi final. `prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md` baru dijalankan setelah TH5.

## Latar

Hasil saat ini (sumber T28, T30, T33, T34, `docs/DECISIONS.md`):

- VAL mAP50-95 KD Hybrid full 0,7505 ± 0,0018 dan *supervised* 0,7208 ± 0,0041. Pada *confidence* 0,25, *precision* Hybrid lebih rendah dan *recall* lebih tinggi daripada *supervised* pada dua dari tiga *seed*.
- TEST mAP50-95 Hybrid full 0,7469 ± 0,0022 dan *supervised* 0,7225 ± 0,0035 (selisih +0,0244 ± 0,0040, positif di 3/3 *seed*). F1@0,25 0,9071 dan 0,9121 (selisih −0,0051).
- Pada 260 *frame* kamera OP3 (T34), Hybrid seed 1337 unggul mAP50-95 (0,4885 lawan 0,4414), tetapi F1 makro lebih rendah (0,5121 lawan 0,6054). Hybrid juga memberi kotak palsu pada 21/60 *frame* kosong, dan *recall* gawang pada ambang 0,25 hanya 2/80 walaupun AP50 gawang 0,4874.
- Kurva VAL Hybrid masih naik di *epoch* 100 (T33); ini indikasi kemungkinan pelatihan belum jenuh, bukan bukti bahwa penambahan *epoch* pasti memperbaiki hasil.
- Pilot `pure_weighted` (*loss* kotak dan kelas dibobot skor *teacher*, tanpa *loss* label) gagal: VAL mAP50-95 0,5907 dan F1@0,25 0,0903. Dugaan penyebabnya, bobot kelas mendekati nol pada *anchor* latar sehingga *student* tidak lagi belajar menekan latar. Dugaan ini belum dibuktikan.

Masalah yang tersisa dari Prioritas 2 dokumen analisis 19 Oktober:

1. *Precision* dan F1 pada ambang operasi tidak ikut membaik walaupun mAP naik. Kemungkinan penyebabnya kalibrasi *confidence* atau ambang, bukan kualitas peringkat.
2. KD kotak memakai Smooth L1 pada keluaran `boxes` mentah. Bila `boxes` berupa *logit* DFL, perbandingan langsung *logit* kurang tepat karena softmax tidak berubah oleh pergeseran konstanta. Bentuknya belum diverifikasi.
3. KD kotak dan kelas dirata-ratakan atas semua *anchor*, padahal sebagian besar *anchor* adalah latar.
4. Bobot KD dan temperatur tidak pernah disetel di VAL.
5. Anggaran *epoch* mungkin terlalu pendek untuk semua metode.

## Prompt siap pakai

Bertindak sebagai *engineer* *machine learning* dan pencatat eksperimen pada server lab untuk skripsi Bhre (Teknik Komputer FILKOM UB). Tugasmu memperbaiki objektif KD hibrida untuk pasangan *teacher* YOLO11n dan *student* YOLO11 skala t, menguji *teacher* YOLO11s sebagai ablasi di VAL, dan menyiapkan model final untuk uji live OP3. Baca dulu prompt ini, `docs/DECISIONS.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `configs/analysis.yaml`, `configs/kd_hybrid_full.yaml`, `scripts/train_kd.py`, `scripts/kd_losses.py`, `scripts/evaluate_val_ablation.py`, `scripts/evaluate_hybrid_locked_test.py`, serta tabel T04, T28 sampai T33.

### 0. Aturan

- Lingkungan tetap: Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NVIDIA L40. Jangan memutakhirkan paket.
- Resep pelatihan tetap kecuali yang disebut berubah: 100 *epoch*, *batch* 16, `imgsz` 640, AdamW `lr0` 0,001, `lrf` 0,01, *warmup* 3, *weight decay* 0,0005, `close_mosaic` 10, AMP mati, `patience` 30, *seed* 42, 1337, 2025, *student* `pretrained: false`.
- **Tidak ada evaluasi TEST baru sebelum TH5.** TEST resmi sudah pernah dibuka untuk varian lama sebelum rancangan `hybrid_v2`; karena itu evaluasi lanjutan pada split yang sama tidak boleh disebut *holdout* bersih atau konfirmasi independen. Semua penyaringan, pemilihan konfigurasi, *seed*, dan ambang baru hanya memakai VAL. Hasil OP3 T34 telah diketahui saat hipotesis perbaikan disusun; 260 *frame* itu tidak boleh dipakai untuk memilih model maupun diklaim sebagai uji independen `hybrid_v2`.
- **Jangan menimpa apa pun.** *Run*, konfigurasi, tabel, dan entri registri lama tetap ada. Nama baru wajib unik. Alias `op3_default` dan entri `hybrid_full_*` tidak diubah.
- Perilaku mode lama (`pure_v4`, `pure_weighted`, `hybrid_feature`, `hybrid_full`) tidak boleh berubah. Kode baru ditambahkan sebagai mode baru dan dibuktikan dengan uji regresi.
- Bobot *teacher* (YOLO11n maupun YOLO11s) tidak boleh masuk repo publik. Jangan commit atau push tanpa izin Bhre.
- Unduhan dari internet (misalnya `yolo11s.pt`) hanya dari rilis resmi Ultralytics dan hanya setelah Bhre mengizinkan. Catat URL dan SHA-256.
- Bila satu langkah gagal, catat penyebab dan lanjutkan hanya pemeriksaan independen yang tidak memerlukan langkah gagal itu. Jangan menurunkan *batch*, mengubah resep, atau melewati langkah diam-diam.
- Dokumen ditulis dalam Bahasa Indonesia baku: tanpa tanda pisah *em dash*, "algoritme", "analisis", istilah asing miring, klaim pustaka bersitasi atau diberi `[BUTUH SITASI: ...]`.

### 1. Fase 0: audit dan reproduksi

1. Catat commit, `git status --short`, versi paket, GPU, `nvidia-smi`, dan sisa disk.
2. Verifikasi SHA-256 *teacher* YOLO11n (`e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`) dan sidik jari himpunan data sesuai cara yang dipakai `train_kd.py`.
3. Evaluasi ulang `best.pt` Hybrid full seed 42 dan *supervised* seed 42 pada VAL dengan `evaluate_val_ablation.py` (atau skrip yang dipakai T28). Hasilnya harus sama dengan T28 (mAP50-95 0,7488 dan 0,7189; F1@0,25 0,9220 dan 0,9235). Bila berbeda, berhenti dan laporkan.

### 2. Fase 1: diagnosis tanpa pelatihan

1. **Bentuk keluaran *head*.** Pada satu *batch* VAL, cetak bentuk `boxes` dan `scores` *teacher* dan *student* untuk setiap cabang yang **benar-benar ada** (`one2many` dan, bila tersedia, `one2one`), nilai `reg_max`, dan apakah `boxes` berupa *logit* DFL (kanal = 4 × `reg_max`). Kutip berkas dan baris kode Ultralytics yang membuktikannya. Audit 23 Oktober pada checkpoint yang tersedia menemukan hanya cabang `one2many`.
2. **Besaran suku *loss*.** Pada *checkpoint* Hybrid full seed 42 dan beberapa *batch* VAL tetap, hitung besaran *loss* label (kotak, kelas, DFL), *loss* fitur, KD kotak, dan KD kelas. Laporkan suku mana yang dominan **hanya jika semua komponennya berasal dari keadaan model yang sama**. Checkpoint `best.pt`/`last.pt` yang tersedia hanya memuat `DetectionModel` student dan tidak menyimpan proyektor fitur terlatih; jangan menggantinya dengan proyektor acak lalu mengklaim besaran *loss* fitur historis. Komponen yang tersedia boleh dilaporkan sebagai diagnosis parsial; instrumen pelatihan baru perlu mencatat seluruh komponen untuk run berikutnya.
3. **Proporsi latar.** Hitung proporsi *anchor* dengan skor maksimum *teacher* di atas 0,05; 0,25; dan 0,5.
4. **Kalibrasi dan ambang.** Untuk Hybrid full dan *supervised* (tiga *seed* masing-masing) di VAL, hitung *precision*, *recall*, dan F1 makro terhadap *confidence* 0,05 sampai 0,90; ambang yang memaksimalkan F1 per model; histogram *confidence* untuk TP dan FP per kelas; serta galat kalibrasi bila mudah dihitung. Rujukan kalibrasi yang ada di folder Paper: Guo, et al. (2017) dan Küppers, et al. (2020). Jangan mengubah D4; cukup laporkan apakah selisih F1 terhadap *supervised* hilang bila ambang dipilih per model di VAL.
5. Tulis hasil ke **T39** `analisis_performa/tabel/T39_diagnosis_objektif_kd.{csv,md}` dan dokumentasi percobaan.

**TH1.** Laporkan hasil Fase 0 dan 1, lalu ajukan untuk disetujui Bhre:

- daftar konfigurasi penyaringan final (bagian 3), disesuaikan dengan temuan diagnosis;
- aturan seleksi bagian 5 (boleh diusulkan perubahannya, tetapi harus dikunci sebelum pelatihan);
- perkiraan waktu GPU;
- apakah perlu *teacher* YOLO11n kontrol yang dilatih ulang dengan resep sama seperti YOLO11s (bagian 4b);
- apakah ambang per model dari VAL perlu diusulkan sebagai revisi D4 untuk uji live.

Jangan memulai pelatihan sebelum TH1 disetujui.

### 3. Fase 2: implementasi mode `hybrid_v2` dan penyaringan satu *seed*

**3.1 Implementasi.** Tambahkan mode `hybrid_v2` di `scripts/train_kd.py` melalui fungsi baru, dengan suku *loss* di modul baru `scripts/kd_losses_v2.py`. Kunci konfigurasi baru di blok `distillation`:

| Kunci | Pilihan | Arti |
|---|---|---|
| `box_kd` | `smooth_l1`, `kl_dfl` | `kl_dfl`: untuk setiap *anchor* dan sisi, KL antara softmax(`b_T / τ_b`) dan softmax(`b_S / τ_b`) atas *bin* `reg_max`, dikali τ_b². Hanya sah bila Fase 1 membuktikan `boxes` berupa *logit* DFL. Formulasi dicocokkan dengan Zheng, et al. (2022) dari PDF di folder Paper |
| `box_tau` | bilangan positif | Temperatur τ_b untuk `kl_dfl` |
| `box_fg_weighting` | `none`, `teacher_score` | `teacher_score`: bobot *anchor* w_i = maks_c σ(z_T,i,c), dinormalkan dengan Σw, **hanya untuk suku kotak** |
| `class_kd_weighting` | `none`, `floor` | `floor`: w_i = α + (1 − α) · maks_c σ(z_T,i,c) dengan α dari konfigurasi, agar *anchor* latar tetap mendapat bobot. Jangan memakai pembobotan murni seperti `pure_weighted` |
| `feature_weight`, `box_weight`, `class_weight`, `temperature` | seperti `hybrid_full` | |

*Loss* label Ultralytics tetap ikut, sama seperti `hybrid_full`.

Uji unit minimum:

- *loss* kotak dan fitur bernilai nol bila keluaran *student* sama dengan *teacher*; untuk klasifikasi BCE target lunak, nilai *loss* pada kondisi sama adalah entropi target dan umumnya **tidak nol**. Verifikasi nilainya minimum untuk target tersebut dan gradien terhadap *logit student* mendekati nol. Bila formulasi kelas diganti menjadi KL yang mengurangkan entropi *teacher*, barulah nilai nol dapat dituntut;
- gradien hanya mengalir ke *student* dan proyektor;
- bila semua bobot KD nol, *loss* sama dengan *loss* label pada *batch* yang sama;
- `hybrid_v2` dengan `box_kd: smooth_l1` dan pembobotan `none` menghasilkan *loss* yang sama dengan `hybrid_full` pada *batch* dan *seed* yang sama;
- *loss* `hybrid_full` dan mode lama tidak berubah dibanding sebelum perubahan kode (uji regresi pada *batch* tetap).

Konfigurasi baru disimpan sebagai `configs/kd_hybrid_v2_<id>.yaml`, keluaran di `runs/kd_hybrid_v2/`.

**3.2 Penyaringan.** *Seed* 42 saja, maksimal delapan *run*, berurutan. Acuan: Hybrid full seed 42 (VAL mAP50-95 0,7488; F1@0,25 0,9220) yang sudah ada, tidak dilatih ulang.

| Kode | Perubahan dari `hybrid_full` | Tujuan |
|---|---|---|
| S1 | `box_fg_weighting: teacher_score` | Memisahkan efek pembobotan *foreground* kotak |
| S2 | `box_kd: kl_dfl` (τ_b dari Zheng, et al., 2022 atau 1,0 bila tidak tertulis) | Memisahkan efek KL-DFL |
| S3 | S1 + S2 | Gabungan |
| S4 | Konfigurasi terbaik S1 sampai S3 + `class_kd_weighting: floor` (α = 0,1) | Menguji pembobotan kelas yang tetap menjaga latar |
| S5 | Terbaik sejauh ini, `temperature` 1,0 | Kepekaan temperatur kelas |
| S6 | Terbaik sejauh ini, `temperature` 4,0 | Kepekaan temperatur kelas |
| S7 | Terbaik sejauh ini, bobot KD kotak dan kelas 0,5 | Kepekaan bobot |
| S8 | Terbaik sejauh ini, bobot KD kotak dan kelas 2,0 | Kepekaan bobot |

Lewati S2 dan S3 bila `boxes` bukan *logit* DFL, dan catat alasannya. Evaluasi setiap `best.pt` di VAL dengan pengaturan T28 (mAP50, mAP50-95, *precision*, *recall*, F1@0,25 dengan definisi yang sama dengan T28, ditambah F1 rerata per kelas dan metrik per kelas).

Aturan penyaringan satu *seed*: perubahan dianggap lebih baik hanya bila mAP50-95 naik minimal 0,004, atau mAP50-95 berubah kurang dari 0,004 tetapi F1@0,25 naik minimal 0,005. Selain itu, pertahankan konfigurasi yang lebih sederhana. Nilai 0,004 kira-kira dua kali simpangan baku antar-*seed* Hybrid full di VAL (0,0018). Satu *seed* tetap rawan derau, sehingga hasil penyaringan hanya untuk memilih kandidat, bukan untuk klaim.

Tulis ke **T40** `T40_penyaringan_hybrid_v2_val.{csv,md}`.

**TH2.** Laporkan hasil penyaringan dan usulkan maksimal dua kandidat untuk Fase 3.

### 4. Fase 3: konfirmasi tiga *seed* dan ablasi *teacher* YOLO11s

**4a. Konfirmasi.** Latih kandidat terpilih pada *seed* 1337 dan 2025. *Run seed* 42 dari penyaringan dipakai ulang bila kode dan konfigurasinya identik. Bandingkan berpasangan per *seed* dengan Hybrid full dan *supervised* di VAL. Tulis ke **T41** `T41_konfirmasi_hybrid_v2_val.{csv,md}`.

**4b. Ablasi *teacher* YOLO11s (VAL saja).**

1. Latih *teacher* YOLO11s dari bobot pralatih COCO `yolo11s.pt` (setelah izin unduh) pada TRAIN dan VAL yang sama, `nc` 3, urutan kelas `ball`, `gawang`, `robot`, resep bagian 0 dengan `pretrained: true`, *seed* 42. Simpan di luar repo publik, misalnya `artifacts_local/teacher_yolo11s/`, catat SHA-256, jumlah parameter, VAL mAP50-95, waktu pelatihan, dan memori GPU puncak. *Teacher* ini **tidak** dievaluasi di TEST.
2. Untuk menyimpulkan **efek ukuran *teacher***, latih juga *teacher* YOLO11n dengan resep dan data yang sama. Resep *teacher* YOLO11n asal Advance Vision tidak tercatat lengkap. Bila kontrol ini tidak dibuat, tetap boleh menjalankan perbandingan eksploratif, tetapi sebut sebagai perbandingan dua *pipeline teacher*, bukan efek ukuran semata.
3. Latih *student* skala t dengan *teacher* YOLO11s memakai konfigurasi KD terbaik dari 4a (atau `hybrid_full` bila tidak ada kandidat yang lebih baik), tiga *seed*, di `runs/kd_teacher_ablation/`. Jika kontrol YOLO11n baru dibuat, latih pula *student* dengan kontrol itu memakai konfigurasi dan tiga *seed* yang sama agar perbandingan ukuran berpasangan.
4. Laporkan: VAL *teacher* YOLO11n dan YOLO11s; VAL *student* dengan masing-masing *teacher*; selisih terhadap *supervised*; rasio pemulihan (KD − *supervised*) / (*teacher* − *supervised*), dengan peringatan bila penyebutnya kecil; waktu pelatihan dan memori GPU. Tulis ke **T42** `T42_ablasi_teacher_yolo11s_val.{csv,md}`.
5. Saat membahas hasil, rujuk Cho dan Hariharan (2019) serta Mirzadeh, et al. (2020) di folder Paper tentang selisih kapasitas *teacher* dan *student*. Sebutkan bahwa keduanya studi klasifikasi.
6. Hasil ablasi **tidak** mengganti *teacher* utama, model hasil KD, atau rumusan masalah. Bila *teacher* YOLO11s jelas lebih baik, laporkan kepada Bhre sebagai bahan diskusi dengan pembimbing.

### 5. Aturan seleksi model hasil KD (dikunci di TH1)

Usulan awal yang harus disetujui Bhre sebelum Fase 2. Kandidat C menggantikan `hybrid_full` sebagai model hasil KD hanya bila **semua** syarat berikut terpenuhi pada VAL (rerata tiga *seed*):

1. mAP50-95 C tidak lebih rendah dari `hybrid_full` lebih dari 0,002;
2. F1@0,25 C lebih tinggi dari `hybrid_full` minimal 0,005, **atau** mAP50-95 C lebih tinggi minimal 0,004;
3. selisih berpasangan pada metrik yang membaik di syarat 2 positif pada minimal dua dari tiga *seed*;
4. mAP50-95 C lebih tinggi daripada *supervised* pada ketiga *seed*.

Bila tidak ada kandidat yang lolos, `hybrid_full` tetap menjadi model hasil KD dan semua varian baru dilaporkan sebagai ablasi. *Seed* untuk OP3 dipilih dengan aturan yang sama seperti pemilihan seed 1337 (verifikasi di `docs/DECISIONS.md`; seed 1337 memiliki VAL mAP50-95 tertinggi di antara tiga *seed* Hybrid full).

**TH3.** Laporkan T41, T42, hasil penerapan aturan seleksi, dan perkiraan biaya Fase 4. Tunggu keputusan Bhre tentang Fase 4.

### 6. Fase 4 (opsional): anggaran *epoch* lebih panjang

Jalankan hanya bila Bhre menyetujuinya di TH3. Latih *supervised* dan model hasil KD terpilih dengan anggaran *epoch* yang sama dan lebih panjang (usulan 200), tiga *seed* masing-masing, dengan nama *run* baru. Perkiraan biaya berdasarkan T33: sekitar 1 sampai 1,4 jam per *run* untuk 100 *epoch*, jadi enam *run* 200 *epoch* butuh sekitar 12 sampai 17 jam GPU. Jika versi 200 *epoch* dipakai untuk **perbandingan tiga metode**, latih juga KD murni pada tiga *seed* dengan anggaran yang sama; bila tidak, laporkan enam *run* itu sebagai eksperimen tambahan dua metode dan pertahankan perbandingan tiga metode 100 *epoch* sebagai analisis utama. Terapkan ulang aturan bagian 5 untuk versi panjang terhadap versi 100 *epoch*.

### 7. Fase 5: TEST lanjutan dan serah terima ke uji live (TH5)

1. Setelah semua keputusan seleksi dibekukan, evaluasi model hasil KD final (tiga *seed*) di TEST 592 gambar dengan pengaturan yang sama dengan T30, di folder baru `runs/final_test/hybrid_v2_<tanggal>/`. Bila pembanding *supervised* berubah (Fase 4), evaluasi juga pembanding itu. Bila model hasil KD tetap `hybrid_full`, TEST tidak perlu diulang. Catat bahwa split TEST sudah pernah dipakai. Jangan memilih apa pun berdasarkan TEST. Tulis ke **T43** `T43_test_lanjutan_hybrid_v2.{csv,md}`.
2. Tambahkan entri registri baru di `configs/model_registry.yaml` (nama, path, SHA-256, jumlah parameter). Jangan mengubah entri lama maupun `op3_default`.
3. Detektor OP3 saat ini memeriksa prefiks `hybrid_full_` untuk `model_variant:=hybrid`, sehingga nama baru seperti `hybrid_v2_seed<n>` akan ditolak. Bila model hasil KD berganti, tambahkan varian runtime baru di `scripts/model_registry.py` dan `scripts/op3_pytorch_detector.py` tanpa mengubah perilaku varian lama, beserta uji unitnya.
4. Setelah Bhre menyetujui, tambahkan catatan "Pembaruan model" di bagian atas `prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md`: kunci model baru, path *checkpoint*, SHA-256, dan argumen `model_variant`. Catat juga cara memindahkan *checkpoint* ke OP3 (repo publik hanya dengan izin Bhre, atau salinan privat). Bila ambang per model disetujui sebagai revisi D4, tulis nilainya untuk setiap model, termasuk *teacher*.
5. Catat keputusan di `docs/DECISIONS.md` dan `configs/analysis.yaml` hanya setelah Bhre menyetujuinya.

### 8. Dokumentasi

- Setiap fase punya dokumentasi di `dokumentasi/<tanggal>/percobaan-<nomor berikutnya>-<nama>/` dengan README_ID.md: tujuan, konfigurasi, hash, perintah, tabel, grafik (kurva VAL per *epoch*, kurva P/R/F1 terhadap *confidence*), batas interpretasi, dan tautan artefak.
- Laporan gabungan `analisis_performa/lab_server/HASIL_KD_HYBRID_V2_<tanggal>.md`.
- Perbarui `analisis_performa/INDEKS.md`, `analisis_performa/manifest.json`, dan `prompt/inventaris_tabel_dan_prompt.md`. Nomor T36 sampai T38 dicadangkan untuk uji live setara; prompt ini memakai T39 sampai T43.
- Tulis memory `memory/<tanggal>-perbaikan-kd-jalur-tengah.md` sesuai format folder `memory/`.

### 9. Titik henti

| Kode | Setelah | Yang ditunggu dari Bhre |
|---|---|---|
| TH1 | Audit, reproduksi, diagnosis | Persetujuan konfigurasi penyaringan, aturan seleksi, izin unduh `yolo11s.pt`, keputusan *teacher* YOLO11n kontrol, usulan ambang |
| TH2 | Penyaringan satu *seed* | Persetujuan kandidat untuk konfirmasi |
| TH3 | Konfirmasi tiga *seed* dan ablasi *teacher* | Hasil aturan seleksi; keputusan Fase 4 |
| TH4 | Fase 4 (bila dijalankan) | Persetujuan hasil anggaran panjang |
| TH5 | TEST lanjutan dan serah terima | Persetujuan registri, perubahan runtime, catatan untuk prompt uji live, publikasi *checkpoint* |

### 10. Format laporan di setiap titik henti

1. Yang dikerjakan.
2. Berkas yang dibuat atau diubah beserta path.
3. Perintah yang dijalankan dan hasilnya; setiap angka disertai path sumbernya.
4. Penyimpangan dari prompt ini dan alasannya.
5. Keputusan yang dibutuhkan dari Bhre.

Mulai dari Fase 0, lalu berhenti di TH1.
