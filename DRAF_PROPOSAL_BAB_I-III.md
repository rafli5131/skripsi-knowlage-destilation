# Draf Proposal Skripsi: Bab I–III

**Judul kerja:** *Implementasi dan Evaluasi YOLO11 Skala t Hasil Knowledge Distillation pada ROBOTIS OP3*

> Pembaruan 30 Oktober 2026: fokus metode adalah KD Hybrid full sesuai D16; Pure KD menjadi ablasi. Judul kerja dan rincian protokol masih memerlukan pengesahan pembimbing. Uji live setara T36/T37 dan set OP3 baru belum tersedia.

> Draf ini disusun dari audit datasheet dan protokol eksperimen yang dibekukan. Nama prodi, pedoman sitasi, format subbab, dan persetujuan pembimbing masih perlu disesuaikan. Eksperimen multi-seed, TEST, dan benchmark selesai; draf Bab IV–V berbasis hasil terkunci tersedia di [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md). Bab I–III tetap perlu ditelaah dan disahkan bersama pembimbing.

## BAB I — PENDAHULUAN

### 1.1 Latar belakang

Deteksi objek menggunakan jaringan saraf dalam dapat menghasilkan prediksi kelas dan lokasi objek secara bersamaan (Redmon et al., 2016). Model yang lebih besar umumnya membutuhkan lebih banyak parameter dan komputasi. Kebutuhan tersebut dapat membatasi pemakaian model pada perangkat dengan sumber daya komputasi atau konsumsi daya terbatas. Karena itu, pengurangan biaya model perlu dinilai bersama kualitas deteksi dan waktu inferensinya, bukan hanya berdasarkan ukuran jaringan.

Knowledge distillation (KD) adalah pendekatan untuk melatih model berukuran lebih kecil, yang disebut student, dengan memanfaatkan informasi dari model yang lebih kuat, yang disebut teacher. Pada klasifikasi, informasi teacher sering dinyatakan sebagai distribusi keluaran lunak (Hinton et al., 2015). Pada deteksi objek, informasi yang dapat dipindahkan mencakup fitur internal, prediksi kelas, dan lokasi kotak pembatas. Perancangan KD untuk deteksi menjadi lebih rumit karena model harus menangani banyak lokasi prediksi, ketidakseimbangan objek dan latar, serta ketepatan lokasi.

Penelitian terdahulu memakai bentuk objective yang beragam. Fine-Grained Feature Imitation memilih lokasi fitur berdasarkan kotak ground truth dan menggabungkan imitation loss dengan loss deteksi berlabel. Focal and Global Distillation juga memakai informasi foreground berbasis anotasi untuk membentuk distilasi fitur. Rank Mimicking dan Prediction-Guided Feature Imitation (KD-RP) mentransfer peringkat kandidat dan memandu feature imitation berdasarkan selisih prediksi; meskipun PFI tidak menggunakan label GT untuk membagi foreground/background, objective total KD-RP tetap memuat `Loss_task` (Li et al., 2022, Pers. 10). ScaleKD memindahkan fitur multi-skala dan memurnikan target box melalui cross-scale assistant, tetapi objective totalnya juga memasukkan detection loss standar `L_det` (Zhu et al., 2023, Pers. 7). CrossKD menggunakan cross-head prediction imitation sebagai loss distilasi; persamaan objective totalnya juga memasukkan loss deteksi student terhadap target ground truth (Wang et al., 2024, Pers. 3). Dengan demikian, sinyal distilasi yang berasal dari teacher atau pemilihan lokasi KD yang tidak memakai GT belum cukup untuk menyebut objective total *teacher-only*. Sumber setiap loss yang memperbarui student perlu dibedakan secara eksplisit (Wang et al., 2019; Yang et al., 2022; Li et al., 2022; Zhu et al., 2023; Wang et al., 2024).

Penelitian ini mengevaluasi KD Hybrid full yang menggabungkan loss deteksi berlabel TRAIN dengan distilasi fitur, kotak, dan kelas dari teacher yang dibekukan. Pure teacher-only KD, yang tidak menggunakan label TRAIN untuk loss student, menjadi ablasi. Kontrol supervised memakai arsitektur student yang sama dan loss deteksi berlabel tanpa distilasi. Ketiga metode dibandingkan pada seed 42, 1337, dan 2025. Model utama untuk OP3 adalah Hybrid full seed 1337 yang dipilih dari VAL; konfirmasi Hybrid v2 S2 tidak memenuhi aturan penggantian pada T41.

Eksperimen menggunakan dataset Advance Vision Human dari proyek Roboflow `humanoid-atom/advance_vision_human`, dengan kelas `ball`, `gawang`, dan `robot`. Metadata ekspor lokal mencatat versi `v1` (V1-Base), ekspor 31 Agustus 2026, ukuran gambar 640 × 640, dan lisensi CC BY 4.0; skrip unduh sumber memakai `ROBOFLOW_VERSION=1` untuk mengambil versi tersebut (humanoid-atom, 2026). Split yang tersedia berisi 4.600 gambar TRAIN, 1.213 gambar VAL, dan 592 gambar TEST. Audit anotasi menemukan distribusi objek yang tidak seimbang; kelas `gawang` merupakan mayoritas, terutama pada TEST. Oleh sebab itu, evaluasi penelitian perlu melaporkan metrik keseluruhan sekaligus metrik per kelas.

Audit juga menemukan kemiripan nama sumber dan adegan di antara split. Pemeriksaan tidak menemukan pasangan piksel identik pada pasangan bernama sumber sama yang diperiksa, tetapi inspeksi sampel menunjukkan beberapa gambar atau frame yang sangat mirip. Peneliti mengonfirmasi pemakaian split resmi Roboflow karena lebih hemat dan sebanding dengan teacher yang telah tersedia. Dengan demikian, hasil hanya ditafsirkan sebagai generalisasi tingkat gambar pada dataset ini; hasil tidak mendukung klaim generalisasi ke sesi atau adegan baru.

Teacher yang digunakan adalah checkpoint FP32 YOLO11n dari proyek sumber. Checkpoint dapat diverifikasi dengan SHA-256, dan catatan lama menunjukkan model dipilih berdasarkan VAL serta dievaluasi pada TEST setelah pemilihan. Namun, provenance versi dataset teacher tidak lengkap: `dataset_version` lama bernilai `null`, dan berkas YAML yang dirujuk oleh `args.yaml` teacher tidak tersedia saat audit. Karena itu, kesamaan byte data TRAIN/VAL yang pernah dilihat teacher dengan snapshot penelitian sekarang tidak dapat dibuktikan ulang. Keterbatasan ini akan dicantumkan saat menafsirkan hasil.

### 1.2 Identifikasi masalah

1. Student dengan jumlah parameter lebih kecil dapat kehilangan kualitas deteksi; besarnya perubahan pada dataset Advance Vision perlu diukur.
2. Efektivitas objective KD Hybrid full dan ablasi teacher-only perlu dibandingkan dengan teacher dan student berarsitektur sama yang dilatih secara supervised.
3. Kinerja student mungkin berbeda antar kelas, sedangkan distribusi objek dalam dataset tidak seimbang.
4. Pengurangan parameter belum tentu menghasilkan inferensi lebih cepat; ukuran file, FLOPs, latensi, dan throughput perlu diukur pada perangkat yang dinyatakan.
5. Kemiripan sumber/adegan lintas split dan keterbatasan provenance teacher membatasi interpretasi hasil dan harus disajikan secara eksplisit.

### 1.3 Rumusan masalah

1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil *knowledge distillation* (KD) pada robot humanoid ROBOTIS OP3?
2. Bagaimana tingkat akurasi, berdasarkan nilai *mean average precision* (mAP), model YOLO11 skala t hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?
3. Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?
4. Berapa rata-rata latensi dan *frames per second* (FPS) yang dicapai model hasil KD dan *teacher* YOLO11n saat beroperasi secara *real-time* pada kondisi robot diam dan berjalan?
5. Bagaimana tingkat efisiensi penggunaan CPU dan RAM model hasil KD dan *teacher* YOLO11n saat dijalankan secara penuh pada komputer *onboard* robot?

### 1.4 Tujuan penelitian

1. Mendokumentasikan implementasi deteksi dan tracking tiga kelas melalui ROS 2 pada OP3.
2. Membandingkan mAP, precision, recall, dan F1 Hybrid full, supervised, dan teacher; Pure KD menjadi ablasi.
3. Mengukur latensi, FPS, CPU, dan RAM pada OP3 dalam kondisi diam dan berjalan dengan protokol setara.
4. Menilai biaya arsitektur student serta keterbatasan generalisasi dari split gambar resmi dan bukti kamera OP3.

### 1.5 Manfaat penelitian

Penelitian ini diharapkan memberikan evaluasi empiris yang dapat ditelusuri tentang pemindahan pengetahuan teacher ke student kecil untuk deteksi tiga kelas Advance Vision. Dokumentasi objective, konfigurasi, seed, hash data dan checkpoint, serta gerbang penggunaan TEST dapat menjadi dasar replikasi atau pengembangan eksperimen lanjutan. Penelitian ini tidak mengajukan algoritma KD baru dan tidak menyimpulkan kesiapan deployment pada robot tanpa pengukuran di perangkat sasaran.

### 1.6 Batasan penelitian

1. Dataset memuat tiga kelas: `ball`, `gawang`, dan `robot`; eksperimen memakai split resmi Roboflow TRAIN/VAL/TEST.
2. Klaim generalisasi dibatasi pada tingkat gambar. Split belum terbukti memisahkan sumber video, sesi, atau adegan.
3. Teacher adalah checkpoint YOLO11n FP32 yang telah tersedia dan tidak dilatih ulang dalam studi utama. Provenance versi data teacher tidak lengkap.
4. Student menggunakan arsitektur YOLO11 custom kecil, 810.649 parameter, random initialization, dan `pretrained=false`; konfigurasi teacher memiliki 2.590.425 parameter.
5. Hybrid full memakai loss deteksi berlabel bersama distilasi fitur P3/P4/P5, box, dan kelas. Ablasi Pure KD memakai target teacher saja. QAT tidak menjadi metode penelitian ini.
6. Supervised dan Hybrid full memakai label TRAIN dalam loss; Pure KD tidak. Ketiga metode memiliki arsitektur student yang sama.
7. Checkpoint dipilih berdasarkan VAL. TEST resmi pernah digunakan untuk teacher dan Pure KD sebelum evaluasi lanjutan Hybrid; hasilnya sudah diketahui saat pengembangan Hybrid v2. TEST ini tidak disebut holdout yang belum pernah disentuh.
8. Benchmark pada NVIDIA L40 merupakan karakterisasi host; tidak digunakan sebagai bukti performa real-time pada perangkat robot.

## BAB II — TINJAUAN PUSTAKA DAN LANDASAN TEORI

### 2.1 Deteksi objek

Deteksi objek menghasilkan kelas dan koordinat kotak pembatas untuk setiap objek yang terdeteksi (Redmon et al., 2016). Penelitian ini menggunakan precision, recall, F1, mAP50, dan mAP50–95. mAP50 menghitung average precision pada ambang IoU 0,50, sedangkan mAP50–95 merata-ratakan evaluasi pada ambang IoU 0,50 sampai 0,95 dengan kenaikan 0,05, mengikuti konvensi evaluasi COCO dan dokumentasi metrik Ultralytics (Lin et al., 2014; COCO, n.d.; Ultralytics, n.d.-a). F1 dihitung evaluator sebagai `2PR/(P+R)` dari precision dan recall yang dilaporkan, atau `0` bila `P+R=0`. Metrik tersebut dilaporkan untuk seluruh kelas dan per kelas. Definisi implementasi dan konfigurasi evaluator harus dicocokkan dengan versi Ultralytics yang dipakai.

### 2.2 YOLO dan model teacher–student

YOLO adalah keluarga detektor satu tahap yang menghasilkan prediksi kelas dan lokasi melalui satu rangkaian inferensi (Redmon et al., 2016). Studi ini menggunakan implementasi YOLO11 dari Ultralytics; istilah YOLO11 merujuk pada implementasi perangkat lunak yang digunakan, bukan klaim arsitektur baru dalam penelitian (Ultralytics, n.d.-b). Teacher YOLO11n FP32 menjadi sumber pengetahuan dan acuan kualitas. Student YOLO11 custom memakai struktur lebih kecil dengan pemetaan kelas identik.

### 2.3 Knowledge distillation untuk deteksi

Secara umum, KD meminimalkan perbedaan antara perilaku teacher dan student. Pengetahuan dapat direpresentasikan sebagai keluaran prediksi, fitur internal, relasi antarlokasi/instance, atau kombinasi beberapa bentuk tersebut. Pada deteksi, beberapa metode memakai label ground truth untuk membentuk area atau instance distilasi, atau memasukkan loss deteksi supervised ke objective total. Bahkan bila suatu komponen KD hanya mencocokkan prediksi teacher, hal itu tidak dengan sendirinya berarti objective total bebas dari label ground truth. Karena itu, penelitian harus menyebutkan sumber setiap sinyal loss dan penggunaan label secara operasional.

Ringkasan studi terarah berikut membedakan **sinyal loss distilasi** dari **objective total training student**. Pemetaan diperbarui sampai 10 Oktober 2026 dan tidak dimaksudkan sebagai telaah sistematis atau perbandingan hasil lintas-paper; batas pencarian dan bukti per studi ada di [audit pustaka](TINJAUAN_PUSTAKA_KD_DETEKSI.md).

| Studi | Sinyal/mekanisme distilasi | Peran ground truth dalam mekanisme/objective | Relevansi bagi definisi penelitian |
| --- | --- | --- | --- |
| Fine-Grained Feature Imitation (Wang et al., 2019) | Imitasi fitur pada anchor informatif di sekitar objek | Ground-truth box membantu menentukan lokasi fitur sasaran; paper juga memakai loss deteksi supervised | Bukan teacher-only pada objective total |
| Data-Free Knowledge Distillation for Object Detection (Chawla et al., 2021) | DIODE mensintesis gambar dari detector teacher, lalu student meniru prediksi teacher dengan loss L2 | Objective student pada tahap distilasi hanya mencocokkan keluaran teacher; eksperimen memakai detector berbasis YOLOv3 dan berfokus pada transfer data-free, bukan kompresi | Preseden langsung untuk objective teacher-only; penelitian ini tidak mengklaim kebaruan metode KD |
| Knowledge Distillation for Low-Power Object Detection (Banitalebi-Dehkordi, 2021) | Student pertama dilatih memakai pseudo-label dari teacher, lalu dapat di-fine-tune pada label yang tersedia | Tahap awal bebas anotasi ground-truth, tetapi menggunakan loss deteksi atas pseudo-label; ini berbeda dari pencocokan langsung fitur/output teacher yang menjadi definisi ketat penelitian ini | Preseden training tanpa label asli pada tahap awal, bukan preseden persis untuk objective direct teacher-target yang digunakan di sini |
| Focal and Global Distillation (Yang et al., 2022) | Distilasi fitur fokal serta relasi global antarpiksel | Ground-truth box dipakai membentuk mask foreground untuk distilasi fitur | Mekanisme area KD bergantung pada anotasi |
| General Instance Distillation (Dai et al., 2021) | Fitur, relasi, dan respons pada general instances terpilih | Abstrak menyatakan pemilihan instance tidak membedakan positif/negatif berdasarkan GT; pernyataan ini hanya menjelaskan modul seleksi dan tidak cukup untuk menyimpulkan objective total bebas label | Contoh bahwa label-independence dalam pemilihan target KD tidak otomatis berarti pure teacher-only training |
| Rank Mimicking dan Prediction-Guided Feature Imitation / KD-RP (Li et al., 2022) | Peringkat kandidat box teacher dan imitasi fitur yang dibobot oleh selisih prediksi teacher–student | PFI tidak memakai GT untuk mempartisi foreground/background, tetapi objective total menambahkan `Loss_task` ke loss RM dan PFI (Pers. 10) | Mekanisme PFI yang independen dari mask GT tidak menjadikan keseluruhan training teacher-only |
| ScaleKD (Zhu et al., 2023) | Feature distillation terpisah skala (SDF) dan cross-scale assistant (CSA) untuk memurnikan target klasifikasi/regresi | Objective total menambahkan `L_det`, yaitu loss training standar detektor, pada komponen feature, class, dan box distillation (Pers. 7) | Metode KD untuk small-object detection; objective totalnya bukan teacher-only |
| CrossKD (Wang et al., 2024) | Prediksi cross-head student dipaksa meniru prediksi teacher | Persamaan objective total (Eq. 3) menjumlahkan loss deteksi student terhadap ground truth dan loss CrossKD terhadap teacher | Frasa abstrak “only prediction mimicking losses” merujuk pada mekanisme KD; objective total yang ditulis tetap memuat supervisi ground truth, sehingga bukan teacher-only |
| [MKD (Xu et al., 2025)](https://proceedings.mlr.press/v304/xu26b.html) | Distilasi multi-skala, frequency-mask, dan feature-alignment untuk deteksi edge | Abstrak PMLR menyatakan loss total menggabungkan komponen distilasi dengan traditional detection loss | Pembanding mutakhir yang relevan untuk efisiensi edge; objective totalnya bukan pure teacher-only |
| [CanKD (Sun & Ohyama, 2026)](https://openaccess.thecvf.com/content/WACV2026/html/Sun_CanKD_Cross-Attention-based_Non-local_Operation_for_Feature-based_Knowledge_Distillation_WACV_2026_paper.html) | Feature distillation menggunakan cross-attention non-local pada fitur student dan teacher | Persamaan objective totalnya adalah `L_student = L_task + μ L_feat` (Pers. 8); komponen `L_task` tetap dipakai | Rujukan mutakhir untuk transfer relasi fitur, tetapi objective total bukan teacher-only |
| [FD-CanKD (Cheong & An, 2026)](https://arxiv.org/html/2608.18590) | Manuskrip arXiv menggabungkan distilasi head, transfer fitur cross-attention, dan alignment fitur berbasis frekuensi | Objective pada bagian 3.6 adalah `L_total = L_det + λ_head L_head + λ_fd L_fd`; Algoritme 1 menghitung `YOLOLoss(O_S,Y)` | Contoh mutakhir objective hibrida yang menggunakan label deteksi; status publikasi perlu diverifikasi sebelum naskah akhir |
| Penelitian ini | Fitur P3/P4/P5, box, dan kelas | Hybrid full menggabungkan loss deteksi berlabel dan distilasi; Pure KD memakai target teacher saja | Supervised berarsitektur sama sebagai kontrol; tanpa klaim algoritma KD baru |

Fine-Grained Feature Imitation memakai ground-truth box untuk memilih anchor yang menjadi target imitation (Wang et al., 2019). Banitalebi-Dehkordi memulai training student tanpa anotasi ground-truth menggunakan pseudo-label dari teacher, kemudian menawarkan fine-tuning berlabel; karena tahap awalnya tetap memakai loss deteksi pseudo-label, pola itu tidak sama dengan pencocokan langsung tensor teacher pada definisi ketat penelitian ini (Banitalebi-Dehkordi, 2021). DIODE memakai data sintetis dan pencocokan L2 prediksi teacher–student sebagai objective tahap student; eksperimennya memakai YOLOv3 dan berfokus pada transfer data-free, bukan kompresi (Chawla et al., 2021). Focal and Global Distillation memakai mask foreground berbasis anotasi, sementara General Instance Distillation menunjukkan bahwa seleksi instance yang tidak memakai label belum cukup untuk menyimpulkan objective total bebas label (Yang et al., 2022; Dai et al., 2021). Objective total KD-RP, ScaleKD, CrossKD, dan MKD tetap memuat loss tugas deteksi berbasis label (Li et al., 2022, Pers. 10; Zhu et al., 2023, Pers. 7; Wang et al., 2024, Pers. 3; Xu et al., 2025). CanKD menambahkan feature loss pada loss tugas deteksi (Sun & Ohyama, 2026, Pers. 8). Manuskrip FD-CanKD yang tersedia di arXiv juga menulis YOLO detection loss berbasis anotasi bersama beberapa loss distilasi (Cheong & An, 2026). Rincian batas pencarian, bukti primer, dan status klaim dirangkum dalam [audit pustaka terarah](TINJAUAN_PUSTAKA_KD_DETEKSI.md); audit ini bukan telaah sistematis. Studi-studi di atas memberi konteks desain, bukan pembanding langsung karena arsitektur, dataset, dan protokolnya berbeda.

### 2.4 Objective Hybrid full dan ablasi Pure KD

Objective utama ialah `L_hybrid = L_det + L_feature + L_box + L_class` dengan bobot distilasi 1:1:1 dan temperatur 2, sesuai `configs/kd_hybrid_full.yaml`. `L_det` menggunakan label TRAIN. Definisi teacher-only berikut khusus menjelaskan ablasi Pure KD.

Istilah *pure teacher-only* dalam penelitian ini berarti bahwa gradien yang memperbarui student KD berasal hanya dari target teacher. Teacher dalam mode evaluasi dan forward tanpa gradien. Loss KD didefinisikan sebagai:

\[
L_{KD}=L_{feature}+L_{box}+L_{class}, \qquad T=2.
\]

`L_feature` menjumlahkan score-weighted L2 antara fitur teacher dan fitur student sesudah projector kanal pada level P3, P4, dan P5. Bobot lokasi adalah skor kelas teacher maksimum setelah rata-rata logit kelas teacher one-to-many dan one-to-one, lalu sigmoid. Pada setiap level, squared error tak tereduksi dikalikan bobot lokasi dan dinormalisasi dengan jumlah bobot dikali jumlah kanal, ditambah `1e-9`; loss tiga level dijumlahkan. `L_box` memakai Smooth L1 (\(\beta=1\), reduksi mean) antara tensor logit regresi box mentah teacher/student pada head Detect, sebelum distribusi DFL diubah menjadi koordinat box. `L_class` memakai BCE-with-logits (reduction mean) dengan target lunak \(\sigma(z_t/T)\), logit kelas student dan teacher dibagi \(T=2\), lalu loss dikalikan \(T^2\). `L_box` dan `L_class` dihitung hanya dari output cabang Detect `one2one`, karena `decouple_outputs` dipanggil tanpa argumen cabang dan default implementasinya adalah `one2one`; reduksi mean berlaku pada tensor loss, bukan antar-cabang. Ketiga bobot loss bernilai 1. Tidak ada loss deteksi ground truth yang ditambahkan ke objective KD.

### 2.5 Kompresi dan biaya inferensi

Jumlah parameter mengukur banyaknya nilai terlatih, ukuran checkpoint menunjukkan ukuran artefak model tersimpan, dan FLOPs memperkirakan operasi aritmetika pada input yang ditetapkan. Latensi dan throughput mengukur biaya inferensi teramati pada perangkat serta implementasi tertentu. Metrik tersebut tidak saling menggantikan; model dengan parameter lebih sedikit belum tentu lebih cepat pada seluruh perangkat. Karena itu, pengukuran penelitian melaporkan resolusi, presisi numerik, batch, perangkat, dan bagian pipeline yang termasuk dalam waktu ukur.

### 2.6 Kerangka pemikiran dan hipotesis kerja

Teacher YOLO11n memberikan target fitur dan prediksi untuk student kecil. Hybrid full menggabungkannya dengan loss berlabel; Pure KD dan supervised menjadi pembanding. Checkpoint dipilih memakai VAL. Evaluasi TEST berlangsung bertahap, dengan hasil teacher/Pure KD mendahului Hybrid. Kualitas deteksi dibandingkan dengan biaya model dan runtime OP3.

Hipotesis awal tahap Pure KD adalah student dengan objective pure teacher-only KD memperoleh mAP50–95 lebih tinggi daripada baseline supervised pada arsitektur student yang sama. Perbandingan KD–supervised karena itu menguji dampak objective terhadap kualitas deteksi; parameter dan FLOPs nominal kedua student ditentukan oleh arsitektur yang sama dan bukan keunggulan yang diharapkan dari KD. Klaim kompresi dinilai terpisah dengan membandingkan student KD terhadap teacher melalui parameter, ukuran checkpoint, FLOPs, latensi, dan kualitas deteksi. Tidak ditetapkan ambang numerik “material” atau toleransi mAP sebagai kriteria lulus; seluruh hasil per seed, ringkasan, dan interval yang ditetapkan protokol akan dilaporkan. Dengan tiga pasangan seed, hipotesis ini dievaluasi secara eksploratif dan tidak menjadi klaim signifikansi statistik kuat. Hipotesis awal ini tidak didukung hasil Pure KD. Tahap Hybrid dilaporkan beserta kronologi perluasan metode; hipotesis awal tidak ditulis ulang seolah sejak awal hanya menguji Hybrid.

## BAB III — METODOLOGI PENELITIAN

### 3.1 Rancangan eksperimen

Penelitian memakai eksperimen kuantitatif terkontrol dengan empat kelompok: teacher FP32, student supervised, student Pure KD, dan student Hybrid full. Ketiga metode student menggunakan YAML arsitektur yang sama, random initialization, resolusi input yang sama, konfigurasi training yang sama selain objective, dan tiga seed berpasangan: 42, 1337, dan 2025. Perangkat dan durasi tiap run mengikuti manifest masing-masing. Semua run yang sah dilaporkan; pemilihan checkpoint menggunakan fitness VAL Ultralytics.

### 3.2 Dataset dan pengelolaan data

Dataset berasal dari Roboflow Universe, proyek `humanoid-atom/advance_vision_human`, sebagaimana metadata lokal `advance_vision_human - v1 V1-Base` (humanoid-atom, 2026). Metadata ekspor menyebut lisensi CC BY 4.0, 6.405 gambar, resize stretch 640 × 640, dan tidak menerapkan augmentasi saat ekspor. Versi yang dapat diunduh tercatat sebagai `v1` (`ROBOFLOW_VERSION=1`); identitas byte dataset yang benar-benar dipakai dikunci melalui fingerprint SHA-256 per gambar dan label. Keterbatasan versi dataset teacher lama (`dataset_version: null`) tetap dicatat terpisah.

Inventaris split hasil audit:

| Split | Gambar | Objek | Ball | Gawang | Robot | Background |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TRAIN | 4.600 | 6.143 | 881 | 3.662 | 1.600 | 4 gambar |
| VAL | 1.213 | 1.525 | 182 | 1.048 | 295 | 2 gambar |
| TEST | 592 | 734 | 83 | 532 | 119 | 1 gambar |

Audit menemukan setiap gambar memiliki pasangan label, tidak ada label orphan, tidak ada baris anotasi invalid, dan seluruh split berisi data. Distribusi kelas tidak seimbang. Sidik jari SHA-256 per gambar dan label disimpan pada `artifacts/advance_vision_dataset_fingerprint.json`; fingerprint agregat mengunci file data yang dipakai eksperimen.

### 3.3 Split, risiko kemiripan, dan batas inferensi

Penelitian memakai split resmi Roboflow v1 yang dipilih dan dikonfirmasi peneliti karena lebih hemat dan paling sebanding secara praktis dengan teacher dari proyek Advance Vision yang tersedia. Namun manifest teacher tidak mencatat versi dataset (`dataset_version=null`) dan YAML training lamanya tidak tersedia, sehingga kesamaan byte TRAIN/VAL teacher dengan v1 tidak dapat diverifikasi. Setelah suffix hash Roboflow dihapus, audit menemukan 326 nama sumber bersama TRAIN–VAL, 176 TRAIN–TEST, dan 155 VAL–TEST. Angka tersebut adalah irisan nama dasar, bukan bukti bahwa semua pasangan duplikat. Pemeriksaan piksel pasangan yang memiliki nama dasar sama tidak menemukan pasangan identik; inspeksi visual sampel menemukan beberapa gambar serupa dan frame dengan arena/gawang yang sama. Karena sumber video dan pengelompokan sesi tidak dapat diverifikasi, hasil tidak ditafsirkan sebagai pengujian adegan baru.

TEST sudah pernah dipakai untuk evaluasi historis teacher FP32 dan QAT pada 24 September 2026 setelah pemilihan checkpoint. Dalam penelitian KD, TEST tidak digunakan untuk loss training, tuning, pemilihan checkpoint, atau perubahan ambang. Evaluasi akhir teacher dan enam student dijalankan setelah semua keputusan checkpoint dikunci dari VAL. Jika hasil TEST memerlukan perubahan metodologi, perubahan tersebut harus menjadi eksperimen terpisah dan tidak boleh menggantikan hasil protokol terkunci.

### 3.4 Teacher dan student

Teacher adalah YOLO11n FP32 dari proyek sumber dengan SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` dan 2.590.425 parameter. Teacher dibekukan selama KD. Kekurangan byte-level provenance dataset teacher dinyatakan sebagai limitasi.

Student menggunakan arsitektur YOLO11 custom pada `models/yolo11_tiny_kd.yaml`, 810.649 parameter, random initialization, dan `pretrained=false`. Perbandingan utama memakai student berarsitektur sama pada kelompok KD dan supervised. Arsitektur student memiliki sekitar 68,7% parameter lebih sedikit daripada teacher; ini adalah perbandingan jumlah parameter arsitektur, bukan hasil kecepatan atau kualitas.

### 3.5 Prosedur training dan kontrol

Ketiga metode student memakai maksimal 100 epoch, patience 30, AdamW, `lr0=0.001`, `lrf=0.01`, warmup 3 epoch, weight decay `0.0005`, batch 16, resolusi 640, dua workers, FP32 (`amp=false`), dan `close_mosaic=10`. Data YAML training hanya memuat TRAIN dan VAL. VAL dipakai untuk metrik dan memilih `best.pt`.

Pada kelompok supervised, student diperbarui dengan objective deteksi standar dan label TRAIN. Pada kelompok Hybrid full, label TRAIN digunakan bersama loss distilasi. Pada ablasi Pure KD, label TRAIN tidak digunakan dalam loss. Untuk KD seed 1337, snapshot `train_kd.py` yang direkam saat run mengganti `DistillationModel.loss` dengan `teacher_only_loss`: cabang training melakukan forward teacher di dalam `torch.no_grad()` dan menghitung feature, box, serta class KD dari keluaran teacher; batch label tidak dibaca dan detection criterion tidak dipanggil. Cabang validasi mengembalikan loss bantu nol, sementara label VAL hanya dipakai validator untuk menghitung metrik. SHA-256 snapshot kode cocok dengan manifest run. Seed berpasangan dimaksudkan untuk mengendalikan variasi inisialisasi student. Pada Ultralytics 8.4.130, RNG diinisialisasi dari seed saat trainer dibuat, sebelum trainer membuat student; kedua kelompok memakai YAML arsitektur yang sama dan `pretrained=false`, sementara wrapper distilasi ditambahkan setelah student dibuat. Pemeriksaan `args.yaml` seed 42 juga mengonfirmasi opsi training bersama yang sama, dengan perbedaan pada output dan argumen khusus distilasi. Supervised seed 1337 sempat terhenti saat validasi dan dilanjutkan dari `last.pt` dengan optimizer serta EMA tersimpan; manifest mencatat hash checkpoint resume dan kedua segmen durasi. Karena tensor awal student tidak diarsipkan atau di-hash secara terpisah, kesepadanan inisialisasi didukung urutan kode dan konfigurasi seed, tetapi tidak diverifikasi langsung dari checkpoint awal. Run seed 42 juga merupakan pengecualian provenance: hash YAML dan metadata runtime tidak direkam saat mulai; `args.yaml`, path data, fingerprint prarun, dan konfigurasi saat penautan pascarun diperiksa, tetapi identitas byte YAML saat training tidak dapat dipastikan. Nilai seed, arsitektur, `pretrained`, objective, dan penggunaan label harus diperiksa dari manifest dan `args.yaml` setiap run.

### 3.6 Evaluasi kualitas deteksi

Metrik utama adalah mAP50–95. Metrik sekunder meliputi precision, recall, F1, mAP50, dan metrik per kelas. Tahap awal mengevaluasi teacher dan enam student Pure KD/supervised pada 592 gambar TEST. Evaluasi lanjutan Hybrid tiga seed dilakukan sesudah pemilihan VAL dan dicatat dalam protokol 22 Oktober; TEST sudah pernah dibuka sebelumnya. AP dihitung dengan confidence floor 0,001; precision, recall, dan F1 dihitung pada confidence tetap `>0,25` dan IoU pencocokan 0,50, dengan nilai 0,25 ditetapkan dari default prediction Ultralytics sebelum TEST dibuka. NMS memakai IoU 0,7. Pengaturan lain dikunci pada FP32, input 640, batch 16, dua workers, tanpa augmentasi, dan perangkat NVIDIA L40 yang sama dengan benchmark. Runtime dicatat bersama versi Python, NumPy, PyTorch, dan Ultralytics di protokol. Evaluasi menyimpan manifest, checksum checkpoint, versi evaluator, konfigurasi, perangkat, dan fingerprint split. Hasil TEST final digunakan untuk pelaporan, bukan untuk memilih salah satu seed atau mengubah model.

### 3.7 Evaluasi biaya model dan analisis statistik

Biaya model meliputi jumlah parameter, FLOPs pada input 640, ukuran checkpoint, latensi median, latensi p95, dan throughput batch 1. Benchmark memakai model FP32 pada satu NVIDIA L40, frame VAL tetap, warm-up 30 iterasi, dan 200 iterasi terukur. Manifest menyimpan semua sampel latensi terukur, versi software, serta metadata perangkat. Waktu mencakup preprocessing, forward, dan NMS, tetapi tidak mencakup pembacaan disk atau pemuatan checkpoint. Hasil ini merupakan karakterisasi host; klaim deployment memerlukan pengujian pada perangkat robot.

Hasil TEST dilaporkan per seed dan diringkas sebagai mean serta simpangan baku sampel antar-seed. Perbedaan KD–supervised dihitung berpasangan berdasarkan seed; selisih per kelas terhadap teacher juga dilaporkan. Interval bootstrap persentil 95% dihitung pada tingkat gambar dari 1.000 replikasi dengan pengembalian (seed `20261009`) untuk metrik keseluruhan dan per kelas. Interval metrik keseluruhan hanya memakai replikasi yang memuat ketiga kelas supaya penyebut macro konsisten; jumlah replikasi valid juga dilaporkan untuk interval per kelas. Interval bootstrap bersyarat pada checkpoint yang dievaluasi: interval menggambarkan variasi sampling gambar pada split TEST, tidak mencakup variasi akibat mengulang training, dan tidak mendukung generalisasi ke sesi atau adegan baru. Dengan tiga pasangan seed, inferensi statistik antar-seed dianggap eksploratif dan tidak digunakan untuk klaim signifikansi kuat.

### 3.8 Reproducibility dan artefak

Untuk setiap run disimpan konfigurasi, seed, hash model/config/script, versi perangkat lunak, metadata runtime perangkat, CSV training, manifest, dan checkpoint. Setiap run KD seed 1337/2025 juga menyimpan snapshot `train_kd.py` serta file sumber `DistillationModel` yang diimpor; evaluator memeriksa hash dan konsistensi implementasi di antara seed KD sebelum membuka TEST. Untuk KD seed 42, snapshot skrip yang dibuat pascarun cocok dengan hash skrip run-time yang sudah tercatat, tetapi hash file `distill_model.py` baru dihitung pascarun. Hash `scripts/train_kd.py` pada working tree saat ini berbeda karena penambahan logika snapshot untuk seed selanjutnya; validasi seed 42 merujuk snapshot spesifik yang ditautkan manifest. Timestamp modifikasi file sumber `distill_model.py` lebih awal dari run, namun kesamaan byte saat training tidak dapat dibuktikan. Run supervised seed 42 merupakan pengecualian legacy lain karena dimulai sebelum hash konfigurasi, kode, YAML, fingerprint, dan metadata GPU terstruktur dicatat. Provenance supervised seed 42 ditautkan pascarun melalui pemeriksaan `args.yaml`, waktu fingerprint, kelas, path split, dan hash file data; catatan pascarun tidak menyatakan hash tersedia saat run mulai.

Rincian audit, protokol, audit pustaka, peta Bab I–V, dan bibliografi tersedia di [`AUDIT_DATASET_SKRIPSI.md`](AUDIT_DATASET_SKRIPSI.md), [`PROTOKOL_EKSPERIMEN_SKRIPSI.md`](PROTOKOL_EKSPERIMEN_SKRIPSI.md), [`TINJAUAN_PUSTAKA_KD_DETEKSI.md`](TINJAUAN_PUSTAKA_KD_DETEKSI.md), [`KERANGKA_BAB_SKRIPSI.md`](KERANGKA_BAB_SKRIPSI.md), dan [`REFERENSI_SKRIPSI.bib`](REFERENSI_SKRIPSI.bib). Draf hasil dan simpulan Bab IV–V telah disusun dari output TEST terkunci, benchmark inferensi, dan analisis terverifikasi. Draf abstrak tersedia di [`DRAF_ABSTRAK_SKRIPSI.md`](DRAF_ABSTRAK_SKRIPSI.md).


### 3.9 Evaluasi OP3 dan ablasi tambahan

Uji live setara mengikuti `prompt/PROMPT_UJI_ROBOT_OP3_SETELAH_KONFIRMASI_KD_2026-10-24.md`: teacher, Hybrid full seed 1337, supervised seed 1337, dan Pure KD seed 42; dua kondisi dan tiga ulangan. T36/T37 akan menjadi bukti utama runtime OP3. Pengumpulan frame baru dilakukan pada sesi terpisah dengan sampling yang tidak bergantung prediksi, aturan anotasi yang dibekukan, serta tinjauan setiap frame termasuk frame kosong. Semua model dievaluasi pada gambar dan label identik. Operator mengendalikan kondisi fisik.

T34 pada 260 frame lama adalah evaluasi eksploratif dengan draf label awal dibantu Pure KD; hasilnya tidak menggantikan evaluasi eksternal baru. T42 menguji pasangan teacher YOLO11n/YOLO11s dengan resep setara pada TRAIN/VAL, terpisah dari pemilihan model OP3. Teacher YOLO11n T42 telah selesai; tahap sisanya dilanjutkan pada 30 Oktober 2026. T43 tidak diperlukan karena model utama tidak diganti.
