# Prompt sesi OP3 offline: teacher utama, jalur tunggal T38/T43, dan rincian runtime

Tanggal: 13 November 2026. Dijalankan oleh agen di **komputer OP3** (`/home/humanoid/bre_skripsi`), karena bobot teacher utama, frame dan label T38/T43, serta log mentah 24 run tersimpan lokal di sana. Pekerjaan ini **offline**: tanpa kamera, detektor live, servo, torque, modul, action, atau gait. Tidak ada pelatihan dan tidak ada perekaman frame baru.

## Latar

- D22 mencatat bahwa AP T38/T43 dihitung lewat `model.val` (tensor 512 x 672 setelah padding, NMS `multi_label=True`), sedangkan P/R/F1 dan runtime robot lewat `model.predict` (480 x 640, NMS tanpa multi-label). Pengaruh masing-masing belum dipisahkan.
- D23 (verifikasi TEST di server, `analisis_performa/lab_server/verifikasi_jalur_test_20261113/`): pada TEST, validator memakai 672 x 672 (rect, `pad=0.5`) dan prediktor 640 x 640, tetapi selisih rerata kelompok hanya sampai 0,0035 untuk mAP50-95 dan 0,0024 untuk F1. Pada OP3 selisihnya jauh lebih besar (contoh teacher T43: gawang 200/200 vs 68/200 pada floor 0,001), sehingga perlu diperiksa di frame OP3.
- Penguji kemungkinan menanyakan (a) mengapa latensi teacher di OP3 sekitar 96 ms padahal skripsi Ivan melaporkan YOLOv5 28,26 ms pada NUC7i3, dan (b) mengapa CPU proses sekitar 1.300% satu CPU logis padahal `torch_num_threads_actual=4` dan `torch_interop_threads_actual=2` (tercatat di metadata 24 run).

## Larangan

- Tidak ada perintah gerak, kamera, atau detektor live. Bila suatu langkah tampak membutuhkannya, berhenti dan laporkan.
- Jangan mengubah frame, label, prediksi, manifest, atau hasil T38, T43, T36, dan T37 yang sudah dibekukan. Semua keluaran baru ditulis ke direktori baru; folder yang sudah ada tidak boleh ditimpa.
- Jangan mengubah checkpoint, ambang operasi (0,25 dan 0,45), atau parameter evaluasi, dan jangan memilih ulang model atau ambang dari hasil ini.
- Kode baru dibuat sebagai package baru; package lama hanya dipakai sebagai fungsi bersama tanpa diubah.
- Bobot teacher, frame, label, prediksi per frame, dan log mentah tetap lokal dan tidak masuk Git. *Commit* dan *push* tabel atau dokumentasi hanya bila Bhre memintanya.
- Jangan memasang paket baru di environment OP3 tanpa izin Bhre.
- Bila tidak yakin pada fakta teknis, katakan tidak yakin. Jangan merekonstruksi data yang tidak ada.

## Persiapan

1. `git status --short`; bila bersih, `git pull --ff-only origin main`. Baca `agent.md`, `docs/DECISIONS.md` (D18 sampai D23), `analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md`, `analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md`, `analisis_performa/tabel/T43_sensitivitas_confidence.md`, `dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/README_ID.md`, `analisis_performa/lab_server/verifikasi_jalur_test_20261113/RINGKASAN.md`, dan `scripts/verify_test_inference_path.py` (acuan pencocokan dan pelaporan).
2. Verifikasi hash keempat checkpoint: teacher `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`, Hybrid seed 1337 `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`, supervised seed 1337 `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041`, KD murni seed 42 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`. Verifikasi juga manifest beku T38 (`runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/`), T43 (`runs/op3_t43_evaluation/20261112_reviewed_260/` beserta `review_260_audit_and_frozen_hashes.json`), dan sumber 24 run yang dipakai `ros2_packages/op3_runtime_audit_24`. Bila ada yang berbeda atau hilang, berhenti dan laporkan.

## Bagian A. Teacher utama

3. Jalankan `sha256sum models_local/teacher_fp32_best.pt` dan `stat -c %s` pada berkas yang sama; nilai yang benar adalah hash di atas dan 5.481.875 bait. Jangan menyalin berkas ke mana pun dari OP3. Laporkan path absolutnya beserta perintah yang bisa Bhre jalankan **dari laptop**:
   - `scp humanoid@<ip-op3>:<path-absolut> ./teacher_fp32_best.pt` lalu `sha256sum teacher_fp32_best.pt`;
   - salinan ke server untuk melengkapi baris teacher verifikasi TEST: `scp teacher_fp32_best.pt <server>:<repo-server>/models_local/teacher_utama/best.pt`.

## Bagian B. Jalur tunggal T38 dan T43

Buat package baru `ros2_packages/op3_single_path_eval/`. Untuk setiap set (T38: 260 frame, 50 parsial tetap dilaporkan terpisah seperti T38; T43: 260 frame, per kondisi diam, berjalan, dan gabungan) dan setiap model:

4. **Uji identitas.** Hitung ulang AP jalur `model.val` dan P/R/F1 jalur `model.predict` dengan fungsi evaluator lama. Hasilnya harus identik dengan `results.json` beku T38 dan T43. Bila tidak identik, berhenti dan laporkan.
5. **Jalur predict penuh, ambang protokol.** `model.predict` per frame, floor 0,001, NMS IoU 0,7, imgsz 640, CPU FP32. Hitung mAP50 dan mAP50-95 dengan `ultralytics.utils.metrics.ap_per_class` dan pencocokan sekelas serakah menurut IoU (sama dengan `scripts/verify_test_inference_path.py`), serta P/R/F1 pada confidence > 0,25 dan IoU 0,5: F1 utama D11 dan rerata F1 per kelas. Laporkan juga TP gawang dan frame negatif dengan FP.
6. **Jalur predict, ambang runtime.** Confidence 0,25 dan NMS IoU 0,45: P/R/F1 dengan definisi yang sama.
7. **Pemisahan faktor 2 x 2.** Jalankan model pada tensor yang di-letterbox sendiri, lalu panggil `ultralytics.utils.ops.non_max_suppression` langsung, dengan dua faktor:
   - bentuk tensor: 480 x 640 (letterbox prediktor) vs 512 x 672 (letterbox validator: gambar tidak diskalakan ulang dan diberi padding sesuai `rect`, `pad=0.5`);
   - NMS: `multi_label=True` vs `False`.
   Pastikan sel (512 x 672, multi-label) mereproduksi AP jalur val pada langkah 4 dan sel (480 x 640, tanpa multi-label) mereproduksi langkah 5. Bila salah satu tidak tereproduksi, laporkan selisihnya dan jangan menafsirkan tabel faktor. Laporkan AP50 dan mAP50-95 gawang, TP gawang pada > 0,25, serta F1 utama per sel.
8. Simpan tabel `analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.{csv,md}` dengan kolom yang menyebut jalur dan ambang secara eksplisit. Angka T38 dan T43 tidak diganti; tabel baru ditautkan dari keduanya tanpa mengubah angka lama.

## Bagian C. Rincian runtime 24 run

9. **Latensi per tahap.** Dari CSV mentah 24 run (`runs/op3_pytorch/<run_id>.csv` dan jendela ukur dari `jadwal_run.csv`, dengan seleksi baris yang sama seperti `op3_runtime_audit_24`), hitung per run dan per model x kondisi: rata-rata, median, dan P95 `preprocess_ms`, `inference_ms`, `postprocess_ms`, `end_to_end_ms`, serta sisa `end_to_end_ms - (preprocess_ms + inference_ms + postprocess_ms)`. Rerata `end_to_end_ms` harus sama dengan T36 (toleransi 1e-6); bila tidak, berhenti dan laporkan. Jelaskan dari kode node apa saja yang masuk ke tiap kolom, terutama apakah tracking BoT-SORT, penggambaran preview, dan penerbitan pesan termasuk `postprocess_ms` atau sisa.
10. **Diagnosis CPU sekitar 1.300%.** Catat dari metadata 24 run jumlah thread torch aktual, nilai `tracker_config`, dan isi `botsort.yaml` yang terpasang (terutama `gmc_method`). Lalu jalankan diagnosis replay offline: 300 frame T43 yang sudah ada diumpankan sebagai array ke jalur pemanggilan Ultralytics yang sama dengan node (checkpoint, imgsz, conf, iou, thread torch 4/2), dalam proses terpisah tanpa ROS kamera. Varian:
    - (i) sama dengan runtime: tracking BoT-SORT aktif, penggambaran preview aktif bila dilakukan di dalam proses node;
    - (ii) tracking mati;
    - (iii) tracking aktif dengan `cv2.setNumThreads(1)`;
    - (iv) tracking aktif dengan `gmc_method: none` melalui salinan konfigurasi tracker di direktori keluaran (bukan mengubah berkas terpasang).
    Untuk tiap varian dan untuk teacher serta Hybrid seed 1337, ukur waktu CPU proses per frame (ms CPU per frame, dari `psutil.Process().cpu_times()`), CPU proses rata-rata (% satu CPU logis), jumlah thread, dan waktu CPU per thread beserta namanya dari `/proc/<pid>/task/*/stat` dan `comm`. Laporkan juga latensi per tahap varian (i) agar bisa dibandingkan dengan hasil langkah 9. Diagnosis ini bukan pengganti T36/T37 karena tanpa kamera dan ROS; laju umpan dicatat.
11. Simpan `analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.{csv,md}` (rincian tahap 24 run dan hasil diagnosis replay dalam bagian terpisah). Tambahkan juga `cpu_percent_16_cores` yang sudah ada di keluaran audit 24 run, agar CPU bisa dibaca sebagai persentase dari 16 CPU logis.

## Keluaran dan laporan

12. Dokumentasi `dokumentasi/<tanggal>/percobaan-41-jalur-tunggal-dan-runtime-op3/README_ID.md` dan `README_EN.md`: metode, uji identitas, hasil, keterbatasan, dan manifest hash sumber serta keluaran. Tambahkan tautan pada `analisis_performa/INDEKS.md`.
13. Laporkan kepada Bhre dalam bahasa Indonesia:
    - Bagian A: path dan hash teacher, beserta perintah salin dari laptop;
    - Bagian B: apakah urutan model pada T38 dan T43 berubah antarjalur, faktor mana (padding atau NMS) yang menjelaskan selisih AP dan TP gawang teacher, serta F1 pada ambang runtime;
    - Bagian C: komposisi latensi per tahap teacher dan Hybrid, sumber utama CPU sekitar 1.300% menurut diagnosis replay, dan seberapa yakin kesimpulan itu;
    - `git status --short`, lalu tanyakan apa yang boleh di-*commit* dan di-*push*.

## Cara membaca hasil

- Bila sel (480 x 640, tanpa multi-label) mendekati sel (512 x 672, multi-label), perbedaan jalur kecil dan klaim T38/T43 tidak berubah. Bila salah satu faktor menjelaskan sebagian besar selisih, faktor itu disebut terbuka sebagai keterbatasan, dan angka utama Bab 6 sebaiknya memakai jalur predict karena jalur itulah yang dipakai robot.
- Bila latensi teacher didominasi tahap selain `inference_ms`, kontras dengan skripsi Ivan sebagian berasal dari definisi pengukuran (latensi callback penuh vs waktu inferensi). Kesimpulan ini tetap memerlukan pemeriksaan cara ukur Ivan dan tidak boleh dinyatakan sebagai fakta tanpa itu.
- Bila CPU turun tajam pada varian (iii) atau (iv), sumber CPU tambahan berasal dari OpenCV atau GMC BoT-SORT, bukan dari thread torch.
