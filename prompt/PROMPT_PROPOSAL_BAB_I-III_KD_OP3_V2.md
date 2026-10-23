# Prompt proposal skripsi Bab I–III: Knowledge Distillation dan ROBOTIS OP3

> **Digantikan 23 Oktober 2026 oleh [`PROMPT_PROPOSAL_BAB_1-3_TEMPLATE_FILKOM.md`](PROMPT_PROPOSAL_BAB_1-3_TEMPLATE_FILKOM.md)**, yang mengikuti template proposal dan Panduan Skripsi FILKOM v3.0. Berkas ini disimpan sebagai riwayat; jangan dipakai untuk draf baru.

Gunakan prompt ini untuk membuat draf proposal baru dari bukti repository. Jangan menimpa draf lama.

## Instruksi siap pakai

Bertindak sebagai penulis ilmiah bidang computer vision, Knowledge Distillation, dan robotika. Susun proposal skripsi Bahasa Indonesia Bab I–III yang runtut, akademik, dan dapat ditelusuri. Tulis hanya klaim yang didukung sumber. Jangan mengarang data, keputusan pembimbing, sitasi, DOI, hasil, atau spesifikasi.

### Audit sumber sebelum menulis

Baca:
- memory/2026-10-22-status-proposal-dan-tabel-robot.md
- docs/DECISIONS.md, configs/analysis.yaml, configs/model_registry.yaml
- README.md, PROTOKOL_EKSPERIMEN_SKRIPSI.md, docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md
- AUDIT_DATASET_SKRIPSI.md, KERANGKA_BAB_SKRIPSI.md, DRAF_PROPOSAL_BAB_I-III.md, DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md
- configs/kd_hybrid_full.yaml, configs/kd_hybrid_feature.yaml, configs/kd.yaml, configs/supervised_baseline.yaml
- REFERENSI_SKRIPSI.bib, TINJAUAN_PUSTAKA_KD_DETEKSI.md
- analisis_performa/INDEKS.md, tabel terkait T01–T33, dan laporan TEST Hybrid
- dokumentasi/INDEKS.md, dokumentasi/AUDIT_KELENGKAPAN_SKRIPSI_2026-10-22.md, laporan percobaan OP3 13–21, summary JSON, serta CSV sumber yang dirujuk.

Jika sumber bertentangan, utamakan keputusan/protokol bertanggal, manifest dan log primer, tabel terkini, laporan eksperimen, lalu draf lama. Catat konflik yang belum terselesaikan.

### Fokus penelitian

Keputusan 22 Oktober memilih KD Hybrid full sebagai fokus sementara draf berdasarkan VAL; pure KD dan hybrid_feature adalah pembanding/ablasi, supervised student adalah kontrol, dan teacher menjadi acuan. Konfirmasi pembimbing untuk menetapkan Hybrid full sebagai fokus skripsi masih perlu dicek. Nyatakan fokus dan judul sebagai sementara bila belum ada bukti persetujuan formal. Jangan menyebut penelitian ini knowledge development atau algoritma KD baru.

Judul kerja yang dapat diusulkan: “Evaluasi Knowledge Distillation pada Student YOLO untuk Deteksi Bola, Gawang, dan Robot serta Implementasi pada ROBOTIS OP3”. Selaraskan istilah dan rumusan masalah dengan keputusan resmi yang tersimpan. Lima rumusan masalah pernah disebut telah disetujui, tetapi jangan mengarang redaksinya jika tidak ditemukan di repository; tandai untuk konfirmasi.

### Fakta dan batas klaim

- Teacher adalah YOLO11n FP32 yang dibekukan. Student adalah YOLO11 kustom skala t dengan 810.649 parameter, bukan YOLO11n standar.
- Hybrid full memakai loss deteksi supervised dari label TRAIN bersama distilasi fitur P3/P4/P5, box, dan kelas teacher; bobot distilasi 1:1:1, temperatur 2. Pure KD hanya memakai sinyal teacher untuk loss student; hybrid_feature adalah varian lain. Kontrol supervised dilatih terpisah dengan label.
- Dataset Advance Vision Human Roboflow v1 berlisensi CC BY 4.0. Split resmi 4.600 TRAIN, 1.213 VAL, dan 592 TEST; kelas ball, gawang, robot. Verifikasi angka dan fingerprint di manifest/audit. Kelas tidak seimbang.
- TEST telah dipakai untuk evaluasi model terdahulu. Evaluasi Hybrid adalah lanjutan pada split yang sama; jangan menyebut TEST sebagai holdout yang belum pernah dibuka. Pemilihan checkpoint/metode Hybrid dilakukan lewat VAL dan hasil TEST tidak dipakai untuk tuning.
- Hasil TEST Hybrid: mAP50–95 0,7469 ± 0,0022 vs supervised 0,7225 ± 0,0035; delta berpasangan +0,0244 ± 0,0040. F1@0,25 Hybrid 0,9071 ± 0,0017 vs supervised 0,9121 ± 0,0026.
- Hasil TEST pure KD: mAP50–95 0,6630 ± 0,0108 vs supervised 0,7225 ± 0,0035; teacher satu checkpoint 0,7800. Jangan menyatakan pure KD lebih baik.
- Evaluasi kamera OP3 260 frame bersifat eksploratif: 200 positif, 60 negatif, 400 kotak GT; KD mAP50–95 0,422 dan supervised seed42 0,419. Lima puluh frame gawang parsial dipisahkan karena definisi bbox berbeda. Label manusia berawal dari draft prediksi KD, sehingga ada risiko bias anotasi. Satu hari/lingkungan tidak membuktikan generalisasi adegan.
- Runtime live adalah ukuran FPS, latensi, CPU/RAM, dan keluaran model, bukan akurasi. KD murni idle/walking: 13,011/12,365 FPS; KD Hybrid: 12,390/12,196 FPS. Hybrid servo-idle setelah OpenCR pulih: 708 frame, 11,795 FPS, nol error, tiga kelas muncul pada semua 708 frame ukur. Jangan mengubah coverage/confidence menjadi precision, recall, mAP, atau akurasi tracking.
- Walking dicatat dari operator/perintah gait; detector tidak memverifikasi gerakan. Benchmark satu run per kondisi dan target/adegan tidak dikonfirmasi independen selama interval. Run idle pasca-pemulihan OpenCR memiliki telemetry kecepatan joint nol sebelum/sesudah.
- NVIDIA L40 adalah benchmark server, bukan performa robot. T16/T17/T21/T22/T24/T27 memiliki batas atau celah pengukuran yang sudah ditandai di indeks tabel; jangan mengisi angka dengan estimasi.
- Kemiripan nama sumber/adegan lintas split dan provenance dataset teacher yang tidak lengkap membatasi klaim generalisasi.

### Susunan naskah

**Bab I — Pendahuluan:** latar belakang deteksi objek untuk OP3, kebutuhan model kecil, KD dan trade-off kualitas/biaya; identifikasi masalah; rumusan masalah terukur; tujuan; manfaat; batasan; sistematika. Bedakan hasil dataset resmi, evaluasi frame OP3, dan runtime live. Nyatakan kontribusi sebagai evaluasi terapan, bukan metode baru. Jangan tulis hipotesis sebagai fakta atau mengklaim Hybrid unggul pada semua metrik.

**Bab II — Tinjauan pustaka dan landasan teori:** deteksi objek dan bounding box; IoU, precision, recall, F1, AP, mAP50, mAP50–95; YOLO11; teacher/student; distilasi fitur dan prediksi; perbedaan objective teacher-only dan hybrid yang memakai label; parameter, FLOPs, ukuran checkpoint, FPS, dan latensi; BoT-SORT sebagai komponen tracking saja; penelitian terkait; kerangka pemikiran. Verifikasi sumber melalui REFERENSI_SKRIPSI.bib dan publikasi primer. Bedakan paper peer-reviewed dari dokumentasi software. Jangan membuat klaim novelty berdasarkan tinjauan terbatas.

**Bab III — Metodologi:** rancangan model dan tujuan tiap kelompok; dataset, split, lisensi, kelas, preprocessing, fingerprint, distribusi dan risiko provenance; arsitektur teacher/student; objective dan konfigurasi loss; seed 42/1337/2025; optimizer dan resep training; VAL untuk memilih checkpoint; protokol TEST dan riwayat penggunaannya; metrik utama dan per kelas; bootstrap dan rerata/SD tiga seed; benchmark server yang dilabeli jelas; deployment PyTorch FP32 di OP3, kamera ROS, threshold, BoT-SORT, preview, warm-up, durasi dan pencatatan metrik; evaluasi kamera berlabel sebagai sub-studi eksploratif; prosedur reproduksi dan batas keselamatan.

Tulis pengujian yang sudah terjadi sebagai metode/pekerjaan yang telah dilakukan, bukan rencana mendatang. Untuk proposal yang diwajibkan memakai bentuk rencana, jelaskan mana yang sudah dikerjakan dan mana yang belum. T16 fixed-frame OP3, sapuan thread terkendali T17, suhu berkelanjutan T21, kamera-only berpasangan T22, preview terisolasi T24, dan set evaluasi kamera lintas sesi T27 harus disebut sebagai belum dilakukan/batasan bila relevan.

### Sitasi dan keluaran

Gunakan daftar pustaka yang benar-benar disitasi. Verifikasi sumber primer dan dokumentasi resmi; tandai sumber yang perlu dicek. Sesuaikan format kampus setelah pedomannya tersedia. Jangan mengarang persetujuan pembimbing.

Simpan draf baru sebagai DRAF_PROPOSAL_BAB_I-III_KD_OP3_REVISI.md. Jangan mengubah DRAF_PROPOSAL_BAB_I-III.md atau draf Bab IV–V yang lama. Sertakan:
1. tabel rumusan masalah → metrik → sumber data;
2. tabel angka/klaim → berkas manifest/CSV/JSON;
3. keputusan yang menunggu konfirmasi pembimbing;
4. daftar batasan;
5. audit konsistensi istilah, jumlah dataset, model, seed, TEST, hasil OP3, dan batas akurasi live.

Periksa ulang angka terhadap sumber, validasi tautan lokal, dan pastikan hasil TEST, evaluasi kamera OP3, serta runtime robot tidak tercampur. Jangan menjalankan robot, kamera, training, atau evaluasi baru untuk membuat proposal.
