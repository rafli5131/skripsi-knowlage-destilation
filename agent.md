# Panduan agent proyek BhreSkripsi

## Bahasa dan kolaborasi

- Gunakan Bahasa Indonesia untuk komunikasi dan dokumentasi baru, kecuali pengguna meminta bahasa lain.
- Lanjutkan pekerjaan yang sudah diizinkan. Jangan meminta persetujuan berulang untuk tugas lokal yang dapat dibatalkan.
- Jangan commit, push, unggah dataset/frame/log robot, atau mengirim pesan eksternal kecuali pengguna meminta secara eksplisit.
- Jangan menghapus, menimpa, atau mereset artefak eksperimen. Untuk hasil baru, gunakan direktori unik dan simpan manifest serta hash sumber.

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
- Alias `op3_default` masih menunjuk Pure KD seed 42. Jangan mengganti checkpoint default diam-diam. Runtime memiliki varian `model_variant:=hybrid`; ikuti prompt OP3 V2 dan verifikasi hash sebelum menjalankan.
- Artefak OP3 lama sudah ada, termasuk log live Pure KD dan evaluasi kamera eksploratif T27. T27 bukan evaluasi final bebas bias: label berawal dari draf prediksi KD, berasal dari sesi terbatas, dan 50 frame gawang parsial dipisahkan. Jangan menyatakan belum pernah ada uji OP3 sama sekali.
- Hybrid seed 1337 belum diuji di OP3. Status kesiapan robot bersifat terkini dan bisa berubah; pengguna terakhir menyatakan robot belum siap untuk sesi berikutnya. Jangan mengasumsikan robot aktif atau kondisi servo dari log lama.
- Untuk evaluasi OP3 yang dipilih sebagai Jalur Pertama, bekukan checkpoint/konfigurasi sebelum capture; gunakan sesi/frame baru yang tidak dipakai memilih model atau threshold; label harus ditinjau tanpa bergantung pada prediksi; bandingkan Hybrid seed 1337 dan supervised seed 1337 pada frame dan label identik. Laporkan semua hasil tanpa memilih ulang model dari metrik OP3 test.
- Tidak boleh mengirim perintah servo, gait, atau motor dari pekerjaan deteksi/evaluasi. Operator menetapkan dan memverifikasi kondisi fisik. Bila kondisi tidak terverifikasi, catat `unknown`.
- Frame auto-label adalah draf prediksi, bukan ground truth. Tinjau manusia semua frame, termasuk frame kosong, sebelum menghitung mAP/precision/recall/F1 kamera. Simpan data mentah, `labels_auto`, dan `labels_reviewed` terpisah.
- Jangan mengunggah gambar, video, label, atau log robot tanpa instruksi khusus pengguna.

## Environment dan reproduksibilitas

- Environment training yang dibekukan berada di `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv`; jalankan dengan `env -u PYTHONPATH` dan interpreter environment tersebut. Versi yang dikunci: Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NumPy 1.26.4.
- Akses GPU dapat berbeda antara sandbox workspace dan konteks host. Pada pemeriksaan 22 Oktober 2026, host melihat tiga L40 dan environment terkunci melihat CUDA; GPU saat itu digunakan proses lain. Periksa kondisi terbaru sebelum menjalankan job. Jangan mengubah driver sistem atau membuat environment duplikat tanpa kebutuhan.
- Simpan provenance dataset, checkpoint, YAML, config, skrip, seed, runtime, dan perangkat dalam manifest. Gunakan fingerprint dataset yang ada; jangan memasukkan TEST ke YAML training.
- Sebelum menambah training, pastikan eksperimen memang belum ada di manifest/registry dan protokolnya tidak menggunakan ulang TEST untuk seleksi. Gunakan direktori run baru.

## Peta sumber kebenaran

- Status dan rujukan terbaru: file tanggal terbaru di [`memory/`](memory/).
- Model/checkpoint/hash: [`configs/model_registry.yaml`](configs/model_registry.yaml) dan manifest masing-masing run.
- Data/split/provenance: [`AUDIT_DATASET_SKRIPSI.md`](AUDIT_DATASET_SKRIPSI.md), fingerprint di `artifacts/advance_vision_dataset_fingerprint.json`.
- Hasil tabel: [`analisis_performa/INDEKS.md`](analisis_performa/INDEKS.md) dan [`analisis_performa/lab_server/README.md`](analisis_performa/lab_server/README.md).
- Runtime robot dan instruksi sesi: [`OP3_PYTORCH_RUNTIME.md`](OP3_PYTORCH_RUNTIME.md), `prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3_V2.md`, serta README package yang terkait.
- Audit server terakhir: [`docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md`](docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md).

Jika ringkasan memory berbeda dari manifest, registry, atau artefak primer, periksa artefak primer dan perbarui memory dengan tanggal serta rujukan yang jelas.
