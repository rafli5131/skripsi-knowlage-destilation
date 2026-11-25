# Panduan agent proyek BhreSkripsi

## Bahasa dan kolaborasi

- Gunakan Bahasa Indonesia untuk komunikasi dan dokumentasi baru, kecuali pengguna meminta bahasa lain.
- Lanjutkan pekerjaan yang sudah diizinkan. Jangan meminta persetujuan berulang untuk tugas lokal yang dapat dibatalkan.
- Jangan commit, push, unggah dataset/frame/log robot, atau mengirim pesan eksternal kecuali pengguna meminta secara eksplisit.
- Jangan menghapus, menimpa, atau mereset artefak eksperimen. Untuk hasil baru, gunakan direktori unik dan simpan manifest serta hash sumber.
- Untuk kode baru terkait percobaan robot, buat package baru; bila membutuhkan fungsi package lama, gunakan sebagai fungsi bersama tanpa mengubah package yang sudah ada.

## Ruang lingkup penelitian

- Kelas deteksi: `ball`, `gawang`, `robot`.
- Teacher: YOLO11n FP32 dari proyek `rafli/advance_vision`.
- Student: YOLO11 skala `t` kustom, 810.649 parameter; **bukan YOLO11n standar**. Kontrol supervised memakai arsitektur student yang sama.
- Eksperimen yang tersedia mencakup Pure KD teacher-only, supervised, dan KD Hybrid full. Hybrid full menggabungkan loss deteksi berlabel dengan distilasi fitur, kotak, dan kelas. Jangan menyebut objective Hybrid sebagai Pure KD.
- Dataset adalah export Roboflow `advance_vision_human` v1 dengan split resmi train/valid/test. Jumlah gambar 4.600/1.213/592. Kelas mayoritas adalah `gawang`.

## Protokol dan batas klaim

- Gunakan VAL untuk seleksi model, threshold, atau konfigurasi. Split TEST resmi sudah pernah dibuka untuk evaluasi teacher dan KD murni sebelum evaluasi lanjutan Hybrid. Jangan menyebutnya holdout yang belum pernah disentuh, jangan mengubah model berdasarkan hasil TEST, dan jelaskan kronologinya apa adanya.
- Ada nama dasar sumber berulang lintas split (326 train–val, 176 train–test, 155 val–test). Itu bukan bukti duplikat piksel, tetapi metadata yang tersedia belum membuktikan pemisahan video/sesi/adegan. Batasi klaim generalisasi ke split gambar resmi.
- Provenance teacher belum lengkap: manifest menyimpan `dataset_version: null` dan YAML/data path lama tidak tersedia. Hash checkpoint terverifikasi, tetapi jangan mengklaim byte-level kesamaan data TRAIN/VAL teacher dengan snapshot saat ini.
- Hasil TEST Hybrid: mAP50–95 0,7469 ± 0,0022 vs supervised 0,7225 ± 0,0035; F1 makro pada confidence 0,25 adalah 0,9071 ± 0,0017 vs 0,9121 ± 0,0026. Laporkan bahwa mAP50–95 lebih tinggi dan F1 sedikit lebih rendah; tiga seed memberi bukti eksploratif, bukan klaim signifikansi kuat.
- Benchmark NVIDIA L40 adalah karakterisasi server, bukan FPS/latensi OP3. Bedakan parameter/ukuran student dari pengaruh metode KD.
- Pengguna memilih Jalur Pertama pada 22 Oktober 2026: pertahankan eksperimen saat ini, dokumentasikan keterbatasan secara terbuka, dan jangan retrain pada split yang sama hanya untuk mencoba menghapus riwayat TEST. Uji OP3 baru menjadi evaluasi eksternal tambahan, bukan perbaikan retroaktif atas TEST atau provenance teacher.

## Status model dan OP3

- Pure KD, supervised, dan Hybrid full tiga seed sudah selesai dilatih. Tabel lab/server T01–T14 dan T28–T33 serta benchmark L40 tersedia. Jangan mengulang training tanpa protokol baru yang jelas.
- Kandidat OP3 yang dipilih berdasarkan VAL adalah Hybrid full seed 1337: `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt`, SHA-256 `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`.
- Bhre melaporkan persetujuan lisan pembimbing pada 12 November 2026 (D18, baris keputusan bertanggal 11 November): Hybrid full seed 1337 sebagai model KD utama, protokol uji live dan hasil runtime deskriptif, daftar KF/KNF dengan pengujian retrospektif, serta nilai D3, D4, D6, D7, D8, D11. Naskah memakai struktur tujuh bab (D17). Bukti uji KF/KNF per kebutuhan ada di [`bukti_kebutuhan/`](bukti_kebutuhan/README.md) dan dibangkitkan ulang dengan `scripts/build_bukti_kebutuhan.py`. Kronologi waktu training, evaluasi, dan run live ada di [`jejak_waktu/`](jejak_waktu/README.md) (`scripts/build_jejak_waktu.py`). Teacher utama dilatih di server lab, bukan di robot; robot hanya menyimpan salinan bobotnya. Catatan training teacher (`manifest.json`, `args.yaml`, `results.csv`) kini ada di [`log_op3_pelengkap/teacher_training/`](log_op3_pelengkap/teacher_training/): mulai 2 September 2026 10:04 UTC (menurut skrip yang tersimpan; versi skrip saat training tidak terverifikasi), 100 epoch, 3.385,5 detik, NVIDIA L40.
- Alias `op3_default` masih menunjuk Pure KD seed 42. Jangan mengganti checkpoint default diam-diam. Runtime memiliki varian `model_variant:=hybrid`; ikuti prompt OP3 V2 dan verifikasi hash sebelum menjalankan.
- Artefak OP3 lama sudah ada, termasuk log live Pure KD dan evaluasi kamera eksploratif T27. T27 bukan evaluasi final bebas bias: label berawal dari draf prediksi KD, berasal dari sesi terbatas, dan 50 frame gawang parsial dipisahkan. Jangan menyatakan belum pernah ada uji OP3 sama sekali.
- Hybrid seed 1337 telah diuji pada percobaan 27 dan T34. Pengukuran live T36/T37 mencakup 24 run aktif, dengan batas audit yang dicatat; T38 mencakup 260 frame OP3 retrospektif, bukan set independen lintas adegan. Status kesiapan robot bersifat terkini dan bisa berubah. Jangan mengasumsikan robot aktif atau kondisi servo dari log lama.
- Untuk evaluasi OP3 yang dipilih sebagai Jalur Pertama, bekukan checkpoint/konfigurasi sebelum capture; gunakan sesi/frame baru yang tidak dipakai memilih model atau threshold; bandingkan keempat checkpoint pada frame dan label identik. Sejak D19 (11 November 2026) pra-label prediksi boleh dipakai bila pemberi pra-label bukan model yang dievaluasi (utama teacher YOLO11s T42, cadangan gabungan keempat model), semua frame ditinjau manusia, dan 20% frame acak dilabeli buta lebih dulu untuk mengukur bias; lihat `prompt/PROMPT_EVALUASI_SET_FRAME_BARU_OP3_2026-11-11.md`. Laporkan semua hasil tanpa memilih ulang model dari metrik OP3 test.
- Teacher utama (`e05b2b21…420b8c`) ada di OP3 pada `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt`, di repo server akun `dindarosyidah` pada `models_local/teacher_utama/best.pt`, dan sebagai cadangan di laptop. Bobot teacher tidak masuk Git; verifikasi hash sebelum dipakai.
- Tidak boleh mengirim perintah servo, gait, atau motor dari pekerjaan deteksi/evaluasi. Operator menetapkan dan memverifikasi kondisi fisik. Bila kondisi tidak terverifikasi, catat `unknown`.
- Frame auto-label adalah draf prediksi, bukan ground truth. Tinjau manusia semua frame, termasuk frame kosong, sebelum menghitung mAP/precision/recall/F1 kamera. Simpan data mentah, `labels_auto`, dan `labels_reviewed` terpisah.
- Jangan mengunggah gambar, video, label, atau log robot tanpa instruksi khusus pengguna.
- Naskah skripsi terbaru adalah `Skripsi_KD_OP3_v20` (24 November 2026), dengan DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Naskah memakai empat rumusan masalah (D25): mAP, P/R/F1, latensi/FPS, dan CPU/RAM. Sebutan "RM5" pada dokumen lama sekarang RM4. Di naskah, T38 disebut Set Kamera 1 dan T43 Set Kamera 2. Naskah tidak menyebut kode T-nn, nama orang, atau alat bantu AI, dan tidak membandingkan hasil dengan penelitian lain. Salinan Markdown ada di [`laporan/draf-7-bab/`](laporan/draf-7-bab/README.md).

## Environment dan reproduksibilitas

- Environment training yang dibekukan berada di `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv`; jalankan dengan `env -u PYTHONPATH` dan interpreter environment tersebut. Versi yang dikunci: Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NumPy 1.26.4.
- Pada repo server akun `dindarosyidah`, environment setara ada di `.venv-train` (Ultralytics 8.4.130, PyTorch 2.4.1+cu121); `~/rf-venv` tidak berisi Ultralytics. Verifikasi jalur TEST 13 dan 16 November memakai `.venv-train`.
- Spesifikasi server lab `labkc-l40-debian` per 16 November 2026: VM KVM Debian 12 (kernel 6.1.0-43), AMD EPYC 7413 80 vCPU, RAM 283 GiB, 3 × NVIDIA L40 46.068 MiB, driver 535.261.03, CUDA 12.2 menurut driver. Sumbernya [`environment/spesifikasi_server_20261116.txt`](environment/spesifikasi_server_20261116.txt). Angka 40 core per soket adalah topologi virtual; jangan menyebutnya core fisik. Snapshot ini diambil sesudah training dan TEST, jadi jangan dipakai sebagai bukti konfigurasi pada tanggal sebelumnya.
- Verifikasi jalur TEST di CPU server memakan sekitar 20 menit per checkpoint (batch 1, dua varian, 592 gambar). Jalankan job panjang dengan `nohup` atau `tmux` dan catat PID serta lokasi log.
- Di laptop Ubuntu, shell memuat `PYTHONPATH` ROS 2 Jazzy. Jalankan pytest dan skrip repo dengan `env -u PYTHONPATH` dan venv `~/.venvs/skripsi-uji`; tanpa itu plugin pytest ROS gagal dimuat.
- Akses GPU dapat berbeda antara sandbox workspace dan konteks host. Pada pemeriksaan 22 Oktober 2026, host melihat tiga L40 dan environment terkunci melihat CUDA; GPU saat itu digunakan proses lain. Periksa kondisi terbaru sebelum menjalankan job. Jangan mengubah driver sistem atau membuat environment duplikat tanpa kebutuhan.
- Simpan provenance dataset, checkpoint, YAML, config, skrip, seed, runtime, dan perangkat dalam manifest. Gunakan fingerprint dataset yang ada; jangan memasukkan TEST ke YAML training.
- Sebelum menambah training, pastikan eksperimen memang belum ada di manifest/registry dan protokolnya tidak menggunakan ulang TEST untuk seleksi. Gunakan direktori run baru.

## Peta sumber kebenaran

- Status dan rujukan terbaru: file tanggal terbaru di [`memory/`](memory/).
- Naskah skripsi: DOCX/PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\` (sumber kebenaran), catatan sunting `CATATAN_SUNTING_vNN.md` di folder yang sama, dan salinan Markdown di [`laporan/draf-7-bab/`](laporan/draf-7-bab/README.md).
- Model/checkpoint/hash: [`configs/model_registry.yaml`](configs/model_registry.yaml) dan manifest masing-masing run.
- Data/split/provenance: [`AUDIT_DATASET_SKRIPSI.md`](docs/AUDIT_DATASET_SKRIPSI.md), fingerprint di `artifacts/advance_vision_dataset_fingerprint.json`.
- Hasil tabel: [`analisis_performa/INDEKS.md`](analisis_performa/INDEKS.md) dan [`analisis_performa/lab_server/README.md`](analisis_performa/lab_server/README.md).
- Runtime robot dan instruksi sesi: [`OP3_PYTORCH_RUNTIME.md`](docs/OP3_PYTORCH_RUNTIME.md), `prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3_V2.md`, serta README package yang terkait.
- Audit server terakhir: [`docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md`](docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md).
- Environment dan perangkat server: [`environment/README.md`](environment/README.md), termasuk spesifikasi perangkat 16 November 2026.

Jika ringkasan memory berbeda dari manifest, registry, atau artefak primer, periksa artefak primer dan perbarui memory dengan tanggal serta rujukan yang jelas.
