# BAB 3 — METODOLOGI PENELITIAN

> Draf berdasarkan eksperimen yang terdokumentasi, bukan protokol untuk mengulangi pengujian. Periksa dan sesuaikan susunan subbab dengan pedoman kampus.

## 3.1 Rancangan penelitian

Penelitian menggabungkan pengembangan sistem deteksi ROS 2 dan perbandingan model. Tahapnya meliputi analisis kebutuhan, perancangan sistem, pelatihan student, evaluasi kualitas deteksi, implementasi OP3, serta pengukuran runtime diam dan berjalan. Kebutuhan dan bukti retrospektif dibahas pada Bab 4 dan 6.

## 3.2 Dataset dan model

Dataset Advance Vision Human v1 memuat TRAIN 4.600, VAL 1.213, dan TEST 592 gambar dengan tiga kelas. VAL dipakai untuk pemilihan model; TEST telah digunakan pada tahap sebelumnya dan tidak boleh disebut holdout yang sepenuhnya belum pernah dibuka. Kemiripan nama sumber lintas split bukan bukti duplikasi piksel, tetapi pembagian sesi dan adegan tidak terjamin.

Teacher utama adalah YOLO11n FP32; student YOLO11 t kustom memiliki 810.649 parameter. Supervised, KD murni, dan Hybrid full dilatih menggunakan seed 42, 1337 dan 2025. Kandidat OP3 Hybrid full seed 1337 dipilih dari VAL. Provenance dataset teacher utama tidak lengkap; hash checkpoint tidak membuktikan kesamaan byte dataset training teacher.

## 3.3 Prosedur eksperimen

Student dilatih dengan anggaran maksimal 100 epoch berdasarkan konfigurasi dan catatan run. Hybrid full menggunakan loss deteksi berlabel dan distilasi, sedangkan KD murni tidak memakai label TRAIN dalam loss student. Rincian konfigurasi dan pengecualian provenance dijelaskan pada [proposal sumber](../../DRAF_PROPOSAL_BAB_I-III.md), [registry model](../../configs/model_registry.yaml), dan manifest eksperimen.

Akurasi TEST dilaporkan sebagai rerata tiga seed untuk student dan satu checkpoint teacher. Pengaturan evaluasi mencakup input 640, confidence floor AP 0,001, NMS IoU 0,7, serta precision/recall/F1 pada confidence >0,25 dan pencocokan IoU ≥0,5. F1 utama adalah harmonic mean precision dan recall makro. Sumber: [T05](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

### 3.3.4 Ablasi ukuran teacher

T42 merupakan percobaan pendamping pada 1.213 gambar VAL, dengan dua teacher yang dilatih ulang dan enam student Hybrid full pada tiga seed berpasangan. Teacher T42 bukan checkpoint teacher utama untuk OP3. Resep dan audit yang dilaporkan tercatat di [T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md) dan [audit server](../../dokumentasi/2026-11-09/AUDIT_TEACHER_T42_SERVER.md).

### 3.3.5 Evaluasi frame OP3 yang telah dilakukan

T38 mengevaluasi empat checkpoint pada 200 frame berobjek dan 60 frame negatif yang sama; 50 frame gawang parsial dianalisis terpisah. Pra-label awal berasal dari KD murni dan seluruh frame ditinjau manusia. Evaluasi bersifat retrospektif pada satu rangkaian pengambilan, termasuk sesi objek bergerak, sehingga tidak membuktikan generalisasi lintas adegan. Definisi F1 historis T38 adalah rerata F1 per kelas; F1 utama D11 dihitung terpisah dari precision dan recall makro tanpa mengubah hasil T38.

## 3.4 Runtime OP3

Empat checkpoint diukur pada kondisi diam dan berjalan, tiga ulangan per kondisi, sehingga ada 24 run aktif. Konfigurasi mencatat warm-up 30 frame, jendela ukur 60 detik, confidence runtime 0,25, NMS IoU 0,45, empat thread intra-op dan dua inter-op. Sapuan thread tidak dilakukan. Hasil per run dan rata-rata disajikan pada [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) dan [T37](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md).

CPU dan RSS diukur pada proses detektor, bukan sistem keseluruhan. Urutan berbentuk blok lintas hari, ada penggantian run dan bukti fisik yang tidak lengkap; interpretasi bersifat deskriptif sesuai [audit](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md). Model deteksi tidak digunakan untuk mengendalikan motor. Kebutuhan, realisasi, dan bukti uji fungsional dibahas dalam Bab 4–6.
