# BAB 3 METODOLOGI PENELITIAN

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v20 (24 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

## 3.1 Tipe Penelitian

Penelitian ini bertipe implementatif-pengembangan pada bidang Rekayasa Perangkat Cerdas (RPC). Artefak utamanya adalah sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil KD pada komputer *onboard* robot humanoid ROBOTIS OP3. Hasil penelitian karena itu berupa sistem yang bekerja pada perangkat tertanam, bukan hanya model yang dievaluasi di server.

Tipe ini dipilih karena penelitian membuat artefak yang utuh melalui tahap analisis kebutuhan, perancangan, implementasi, dan pengujian. Metode KD diimplementasikan untuk menghasilkan model yang dijalankan pada *embedded system*, dan kinerja sistem dipengaruhi lebih dari satu variabel, yaitu varian model dan kondisi robot. Kecukupan tipe ini dipenuhi dengan menganalisis minimal empat kebutuhan fungsional dan satu kebutuhan nonfungsional, memodelkan perangkat keras dan perangkat lunak setiap subsistem, lalu menguji kebutuhan tersebut secara sistematis melalui skenario pengujian fungsional dan pengujian kinerja.

## 3.2 Strategi dan Rancangan Penelitian

Strategi penelitian ini adalah pembuatan artefak yang disertai eksperimen pembandingan model. Artefak berupa alur pelatihan KD dan sistem deteksi berbasis ROS 2 pada OP3, sedangkan eksperimen membandingkan model hasil KD dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher*. Subbab ini menguraikan metode penelitian, subjek, lokasi, teknik pengumpulan data, teknik analisis data, dan peralatan pendukung.

### 3.2.1 Metode Penelitian

Penelitian dilaksanakan mengikuti diagram alir pada Gambar 3.1. Tahap awal berupa studi pustaka serta pengumpulan dan audit himpunan data. Hasil kedua tahap itu menjadi masukan bagi analisis kebutuhan dan perancangan sistem. Setelah itu, *student* dilatih dengan beberapa varian objektif. Varian KD hibrida disaring dengan satu *seed* pada bagian validasi (VAL), lalu varian terpilih dan pembandingnya dilatih dengan tiga *seed*. *Seed* yang dibawa ke robot juga dipilih pada VAL, sebelum akurasi dievaluasi pada bagian uji (TEST). Model terpilih kemudian diimplementasikan sebagai *node* ROS 2 pada komputer *onboard* OP3.

Pengujian terdiri atas pengujian fungsional dan empat pengujian yang masing-masing menjawab satu rumusan masalah, yaitu mAP, *precision*, *recall*, dan *F1-score*, latensi dan FPS, serta penggunaan CPU dan RAM. Pengujian akurasi dilakukan pada TEST dan pada citra kamera OP3, sedangkan pengujian latensi, FPS, CPU, dan RAM dilakukan secara *live* pada kondisi robot diam dan berjalan. Gambar 3.1 menunjukkan tahapan penelitian beserta subbab dan bab yang menguraikannya, bukan urutan waktu pelaksanaan setiap pengujian. Pemenuhan kebutuhan fungsional dinilai dari *log* dan bukti yang dihasilkan selama pengujian *runtime*, sehingga pengujian fungsional bersifat retrospektif. Urutan pelaksanaan pengujian dan perbedaannya dengan rencana pada proposal dijelaskan pada Subbab 3.3.5.

**Gambar 3.1** Diagram alir penelitian

### 3.2.2 Subjek Penelitian

Subjek penelitian terdiri atas model deteksi objek dan robot. *Teacher* adalah YOLO11n FP32 tiga kelas dengan 2.590.425 parameter yang telah dilatih sebelumnya dan dibekukan selama pelatihan *student*. *Student* adalah YOLO11 skala t dengan faktor kedalaman 0,50 dan faktor lebar 0,125, berjumlah 810.649 parameter, dan diinisialisasi acak. Dari arsitektur *student* tersebut dilatih varian *supervised*, KD murni, dan KD hibrida yang diuraikan pada Subbab 3.3.4.

Robot yang digunakan adalah satu unit ROBOTIS OP3 dengan komputer *onboard* dan kamera sesuai Subbab 1.5. Penelitian ini tidak melibatkan partisipan manusia.

### 3.2.3 Lokasi Penelitian

Penelitian dilaksanakan di Fakultas Ilmu Komputer Universitas Brawijaya. Pelatihan dan evaluasi model dilakukan pada server laboratorium fakultas, sedangkan implementasi *node* dan pengujian pada robot bertempat di Lab A2.22 Ruang Kerja Humanoid.

### 3.2.4 Teknik Pengumpulan Data

Data citra berasal dari himpunan data Roboflow advance_vision_human versi 1 (Humanoid-Atom, 2026) berlisensi CC BY 4.0. Himpunan data ini berisi 6.405 citra berukuran 640 × 640 piksel tanpa augmentasi dengan tiga kelas, yaitu bola (label *ball*), gawang, dan robot. Pembagian bawaan himpunan data dipakai apa adanya: bagian latih (TRAIN) 4.600 citra (6.143 objek), VAL 1.213 citra (1.525 objek), dan TEST 592 citra (734 objek). Rincian per kelas disajikan pada Tabel B.1 di Lampiran B.

Sebelum pelatihan, himpunan data diaudit untuk memeriksa pasangan citra dan label, keabsahan anotasi, dan kemiripan sumber antarbagian. *Fingerprint* SHA-256 setiap citra dan label dicatat agar dapat dipastikan bahwa data tidak berubah selama eksperimen. Nama sumber yang sama ditemukan di lebih dari satu bagian (Tabel B.2), sehingga TEST hanya dipakai untuk mengukur generalisasi pada tingkat citra, bukan pada adegan baru. TEST juga pernah dipakai untuk mengevaluasi model terdahulu, sehingga hasil pada TEST tidak diklaim sebagai hasil pada data yang belum pernah dibuka.

Data lain dikumpulkan dari tiga sumber. Pertama, *log* pelatihan dan evaluasi setiap *run* beserta berkas konfigurasinya. Kedua, *log runtime* per *frame* dari *node* ROS 2 di OP3 yang mencatat cap waktu kamera; waktu prapemrosesan, inferensi, dan pascapemrosesan; penggunaan CPU proses; *resident set size* (RSS), yaitu memori fisik yang ditempati proses; serta jumlah deteksi per kelas. Ketiga, dua set *frame* kamera OP3 berlabel untuk pengujian akurasi pada robot, yang diuraikan pada Subbab 3.3.5.

### 3.2.5 Teknik Analisis Data

Analisis data bersifat deskriptif. Untuk akurasi, model *supervised*, KD murni, dan varian KD hibrida terpilih masing-masing dilatih dengan tiga *seed*, yaitu 42, 1337, dan 2025. Hasilnya dilaporkan per *seed* serta sebagai rata-rata dan simpangan baku antar-*seed*. Cara ini dipakai karena hasil pelatihan jaringan saraf bervariasi menurut sumber keacakannya, termasuk inisialisasi parameter dan pilihan *seed* (Bouthillier, et al., 2021; Picard, 2021). Pengaruh KD dinyatakan sebagai selisih berpasangan antara model hasil KD dan model *supervised* pada *seed* yang sama. Pada citra kamera OP3, setiap model diwakili oleh satu *checkpoint* yang juga dipakai pada pengujian *runtime*, sehingga hasilnya dilaporkan per model dan per kondisi.

Untuk *runtime*, setiap pasangan model dan kondisi diukur dalam tiga ulangan. Nilai yang dilaporkan per ulangan adalah rata-rata, median, dan persentil ke-95 (P95) latensi, FPS efektif, penggunaan CPU, dan RSS, lalu diringkas sebagai rata-rata dan simpangan baku antarulangan. Dengan tiga *seed* dan tiga ulangan, penelitian ini tidak memakai uji hipotesis statistik. Perbedaan antarmodel dibahas dari besar selisih dan konsistensinya pada setiap *seed* atau ulangan. Sebaran dilaporkan sebagai nilai setiap ulangan dan setiap *seed* (Lampiran C dan Lampiran D) beserta simpangan bakunya. Selang kepercayaan tidak dilaporkan karena jumlah *seed* dan ulangan hanya tiga.

### 3.2.6 Peralatan Pendukung

Perangkat keras dibagi menurut tempat penggunaannya. Server laboratorium dipakai untuk pelatihan model dan evaluasi pada VAL dan TEST karena pelatihan memerlukan GPU. Server ini berupa mesin virtual dengan tiga GPU NVIDIA L40 terpasang, dan pelatihan memakai satu GPU. Ablasi ukuran *teacher* dijalankan ulang dengan akun server yang berbeda setelah akun awal tidak lagi tersedia, dan pemeriksaan jalur evaluasi TEST dijalankan pada CPU server. Spesifikasi pada Tabel 3.1 dicatat dari server labkc-l40-debian pada 16 November 2026, sesudah seluruh pelatihan dan pengujian TEST selesai. Komputer *onboard* OP3 menjalankan *node* deteksi sekaligus *gait*, dengan kamera Logitech C920 sebagai sumber citra. Laptop dipakai untuk mengakses OP3 melalui *Secure Shell* (SSH), menampilkan *preview* deteksi, dan menulis laporan. Spesifikasi dan kegunaan setiap perangkat disajikan pada Tabel 3.1.

**Tabel 3.1** Spesifikasi perangkat keras

| **Perangkat**                           | **Spesifikasi**                                                                                                                                                                   | **Kegunaan**                                                                               |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Server laboratorium (mesin virtual KVM) | AMD EPYC 7413 dengan 80 CPU virtual, RAM 283 GiB, tiga GPU NVIDIA L40 46.068 MiB, *driver* NVIDIA 535.261.03 (CUDA 12.2 menurut *driver*), Debian 12                              | Pelatihan dan evaluasi model, ablasi ukuran *teacher*, dan pemeriksaan jalur evaluasi TEST |
| Robot ROBOTIS OP3                       | Komputer *onboard* Intel NUC12WSHi5 dengan Intel Core i5-1240P (12 inti fisik dan 16 *thread* logis), RAM 7,33 GiB, Ubuntu 24.04.5 LTS; subpengendali OpenCR diakses melalui U2D2 | Menjalankan *node* deteksi dan *gait*                                                      |
| Kamera Logitech C920                    | Resolusi 640 × 480 piksel, format YUYV, laju yang diminta 30 FPS                                                                                                                  | Sumber citra *live* pada robot                                                             |
| Tatakan robot                           | Penopang badan OP3                                                                                                                                                                | Menopang robot selama *gait* di tempat untuk mengurangi beban servo                        |
| Laptop ASUS TUF Gaming A14 FA401WV      | AMD Ryzen AI 9 HX 370 (12 inti, 24 *thread*), RAM 32 GB, NVIDIA GeForce RTX 4060 Laptop GPU, Windows 11                                                                           | Akses SSH ke OP3, penampil *preview* deteksi, dan penulisan laporan                        |

Perangkat lunak tersusun berlapis. Pada OP3, Ubuntu menjadi sistem operasi dan ROS 2 Jazzy menjadi dasar komunikasi antar-*node*. *Node* deteksi ditulis dengan Python dan menjalankan model melalui PyTorch dan Ultralytics, termasuk pelacak BoT-SORT yang tersedia di Ultralytics. OpenCV dan cv_bridge mengubah citra kamera menjadi masukan model, vision_msgs dipakai untuk pesan hasil deteksi, dan psutil mengukur penggunaan CPU serta RSS proses detektor. *Gait* pada kondisi berjalan dijalankan oleh op3_manager dari ROBOTIS. Label *frame* kamera OP3 ditinjau dan diperbaiki dengan op3_label_reviewer, yaitu alat peninjau yang menampilkan *frame* beserta kotak label awal, lalu menyimpan label hasil tinjauan dan nama peninjaunya. Pada server, pelatihan dan evaluasi berjalan pada Debian dengan Python, PyTorch, dan Ultralytics. Versi setiap perangkat lunak disajikan pada Tabel 3.2. Versi dicatat karena hasil yang sepenuhnya dapat diulang tidak dijamin lintas versi PyTorch atau perangkat yang berbeda (PyTorch, 2026).

**Tabel 3.2** Spesifikasi perangkat lunak

| **Perangkat lunak**       | **Versi**                                | **Kegunaan**                                                                                           |
|---------------------------|------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Ubuntu                    | 24.04.5                                  | Sistem operasi komputer *onboard* OP3                                                                  |
| Debian                    | 12 (Bookworm)                            | Sistem operasi server laboratorium                                                                     |
| ROS 2                     | Jazzy                                    | *Middleware* komunikasi antar-*node* pada OP3 (Macenski, et al., 2022)                                 |
| Python                    | 3.11.2 (server) dan 3.12.3 (OP3)         | Bahasa pemrograman pelatihan, evaluasi, dan *node*                                                     |
| PyTorch                   | 2.4.1+cu121 (server) dan 2.4.1+cpu (OP3) | Pustaka pembelajaran mendalam untuk pelatihan dengan GPU dan inferensi pada CPU (Paszke, et al., 2019) |
| Ultralytics               | 8.4.130                                  | Pelatihan, evaluasi, dan inferensi YOLO11 (Jocher dan Qiu, 2024)                                       |
| OpenCV                    | 4.11.0                                   | Pengolahan citra pada OP3                                                                              |
| cv_bridge dan vision_msgs | Jazzy                                    | Konversi citra ROS ke OpenCV dan pesan hasil deteksi                                                   |
| psutil                    | 7.2.2                                    | Pengukuran penggunaan CPU dan RSS proses detektor                                                      |
| op3_manager               | Jazzy                                    | Menjalankan *gait* standar pada kondisi berjalan                                                       |
| op3_label_reviewer        | Paket penelitian                         | Peninjauan dan perbaikan label *frame* kamera OP3                                                      |

## 3.3 Metode Setiap Tahap

Subbab ini menjelaskan metode yang dipakai pada setiap tahap dalam Gambar 3.1 beserta hasilnya.

### 3.3.1 Studi Pustaka

Studi pustaka dilakukan dengan menelusuri artikel jurnal, prosiding, skripsi, dan dokumentasi resmi tentang KD pada detektor objek, deteksi objek pada robot humanoid, arsitektur YOLO11, ROS 2, serta metrik akurasi dan kinerja *runtime*. Setiap klaim yang dipakai dicatat bersama sumber dan halamannya. Hasilnya adalah dasar teori dan posisi penelitian pada Bab 2, serta acuan nilai kebutuhan nonfungsional bagi tahap analisis kebutuhan.

### 3.3.2 Analisis Kebutuhan

Analisis kebutuhan dilakukan dengan mengkaji rumusan masalah, keterbatasan komputer *onboard* OP3 yang hanya mengandalkan CPU, antarmuka ROS 2 yang dipakai robot, dan kebutuhan tim terhadap deteksi bola, gawang, dan robot. Kebutuhan dikelompokkan menjadi kebutuhan perangkat keras, perangkat lunak, fungsional, dan nonfungsional. Setiap kebutuhan diberi kode, rumusan, dan cara verifikasi agar dapat ditelusuri sampai skenario pengujiannya.

Analisis kebutuhan menghasilkan lima kebutuhan fungsional dan satu kebutuhan nonfungsional yang dijabarkan pada Bab 4. Untuk kebutuhan nonfungsional laju pemrosesan, nilai acuan yang dipakai adalah FPS efektif rata-rata minimal 8 pada kondisi diam dan berjalan. Nilai ini diambil dari batas atas rentang 4 sampai 8 FPS yang dinilai Lau dan Pottier (2026) memadai untuk tugas navigasi dan interaksi objek pada robot humanoid.

### 3.3.3 Perancangan

Perancangan dilakukan per subsistem, yaitu subsistem pelatihan model di server, subsistem inferensi, dan subsistem *node* ROS 2 di robot. Perangkat keras dimodelkan dengan diagram blok yang menunjukkan hubungan kamera, komputer *onboard*, subpengendali, dan *servo*. Perangkat lunak dimodelkan dengan diagram blok untuk mekanisme pelatihan KD, diagram alir untuk alur pelatihan dan *node* deteksi, serta diagram komunikasi *topic* antara kamera, *node* deteksi, dan penampil. Rancangan tersebut disajikan pada Bab 5.

### 3.3.4 Implementasi

Implementasi pelatihan dilakukan pada server laboratorium memakai Ultralytics. Seluruh varian *student* memakai resep pelatihan yang sama, yaitu 100 *epoch*, ukuran *batch* 16, *optimizer* AdamW dengan laju belajar awal 0,001 dan faktor laju belajar akhir 0,01, *warmup* 3 *epoch*, *weight decay* 0,0005, augmentasi *mosaic* yang dimatikan pada 10 *epoch* terakhir, *automatic mixed precision* (AMP) yang dimatikan, *patience* 30, dan ukuran masukan 640. Kedua varian KD hibrida disaring lebih dahulu dengan *seed* 42 pada VAL memakai aturan yang ditetapkan sebelum pelatihan. Varian terpilih, model *supervised*, dan KD murni kemudian dilatih dengan ketiga *seed*. Perbedaan antarvarian hanya terletak pada objektif pelatihan seperti pada Tabel 3.3, sedangkan konfigurasi lengkapnya disajikan pada Tabel A.1 sampai Tabel A.3 di Lampiran A.

**Tabel 3.3** Varian pelatihan *student* dan objektifnya

| **Varian**       | **Objektif pelatihan**                                                                                           | **Peran dalam penelitian**                                                            |
|------------------|------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| *Supervised*     | $L_{\text{det}}$ dengan label TRAIN                                                                              | Pembanding berarsitektur sama untuk memisahkan pengaruh KD dari pengaruh ukuran model |
| KD murni         | $L_{\text{murni}}$ (Persamaan 2.7) tanpa label, dengan $\lambda_{f} = \lambda_{b} = \lambda_{c} = 1$ dan $T = 2$ | Varian KD tanpa *loss* label                                                          |
| KD hibrida penuh | $L_{\text{hibrida}}$ (Persamaan 2.8) dengan bobot dan temperatur yang sama                                       | Varian KD dengan *loss* label serta distilasi fitur, kotak, dan kelas                 |
| KD hibrida fitur | $L_{\text{det}}$ ditambah distilasi fitur bawaan Ultralytics dengan argumen dis 6,0                              | Varian KD dengan *loss* label dan distilasi fitur saja                                |

Model hasil KD dan *seed* yang dijalankan di robot dipilih hanya berdasarkan hasil pada VAL, dengan aturan seleksi yang ditetapkan sebelum pelatihan. TEST tidak dipakai untuk memilih varian, *checkpoint*, *seed*, maupun ambang, dan hanya dipakai untuk evaluasi akhir. Perbaikan objektif KD hibrida diuji pada delapan konfigurasi dengan *seed* 42, lalu konfigurasi terbaik dikonfirmasi dengan tiga *seed*; konfigurasi itu hanya menggantikan model hasil KD apabila memenuhi aturan seleksi di VAL. Sebagai pengujian tambahan, *student* juga dilatih dengan *teacher* YOLO11s dan dievaluasi di VAL saja untuk melihat pengaruh ukuran *teacher* yang dibahas pada Subbab 2.2.3. Hasil pengujian tambahan ini tidak menggantikan *teacher* utama.

Implementasi pada robot dilakukan dengan menjalankan model sebagai berkas .pt PyTorch FP32 pada CPU komputer *onboard* di dalam sebuah *node* ROS 2. *Node* tersebut menerima citra dari *topic* kamera, menjalankan deteksi dan pelacakan BoT-SORT, menerbitkan hasil deteksi, serta mencatat log *runtime* per *frame*. Rancangan rinci *node* disajikan pada Bab 5.

### 3.3.5 Pengujian

Pengujian terdiri atas pengujian fungsional, pengujian akurasi, dan pengujian *runtime*. Pengujian fungsional memakai metode pengujian kotak hitam (*black-box testing*), yaitu pengujian berdasarkan spesifikasi kebutuhan tanpa memeriksa struktur internal program (Khan dan Khan, 2012; Nidhra dan Dondeti, 2012). Setiap kebutuhan fungsional diberi skenario yang memuat prasyarat, masukan, langkah, dan keluaran yang diharapkan, dan skenario dinyatakan berhasil bila keluaran aktual sesuai dengan keluaran yang diharapkan. Penilaian dilakukan secara retrospektif dari *log*, *metadata*, dan tangkapan *preview* 24 *run* pengujian *runtime*.

Pengujian akurasi dilakukan pada TEST dan pada citra kamera OP3. Pada TEST, ketiga *seed* setiap varian *student* diuji bersama *teacher*. Metrik utamanya adalah mAP50‑95, dengan mAP50, *precision*, *recall*, dan F1 sebagai metrik pendukung, baik secara keseluruhan maupun per kelas (Subbab 2.2.7). mAP dihitung dari seluruh prediksi dengan *confidence* lebih besar daripada 0,001, sedangkan *precision*, *recall*, dan F1 dihitung pada ambang *confidence* 0,25 dan IoU 0,50, dengan NMS IoU 0,7. Ambang 0,25 ditetapkan sama untuk semua model sebelum evaluasi TEST. F1 keseluruhan dihitung sebagai rata-rata harmonik dari *precision* dan *recall* rata-rata kelas, sedangkan rata-rata F1 per kelas dilaporkan sebagai pelengkap.

Pengujian *runtime* dan pengujian akurasi pada citra kamera OP3 dilakukan pada dua kondisi robot. Pada kondisi diam, seluruh *servo* menyala tanpa *gait*. Pada kondisi berjalan, robot menjalankan *gait* di tempat dengan badan ditopang tatakan robot untuk mengurangi beban *servo*, sehingga robot tidak berpindah tempat; perintah mulai dan berhenti *gait* dikirim oleh skrip pengujian ke modul jalan op3_manager. Pada kedua kondisi, *servo* kepala menyala tetapi tidak menerima perintah posisi agar arah kamera tetap.

Pengujian *runtime* dilakukan secara *live* di OP3. Model hasil KD dan *teacher* menjadi pembanding utama, sedangkan model *supervised* dan KD murni menjadi pembanding pelengkap. Setiap model diuji pada kedua kondisi dengan adegan berisi bola, gawang, serta robot pada posisi bertanda.

Seluruh *run* memakai pengaturan yang sama: inferensi FP32 pada CPU dengan masukan 640, *confidence* 0,25, NMS IoU 0,45, pelacakan BoT-SORT, empat *thread* intra-op dan dua *thread* inter-op yang ditetapkan saat inisialisasi *node*, 30 *frame* *warm-up* yang tidak dianalisis, jendela ukur 60 detik, serta *preview* deteksi yang ditampilkan lewat SSH pada laptop. Setiap model diuji tiga kali pada setiap kondisi, sehingga terdapat 24 *run* aktif. Rencana awal menggilir urutan model pada setiap putaran dengan jeda minimal 120 detik. Pada pelaksanaannya, *run* dikelompokkan per model dalam blok selama 2 dan 3 November 2026, dan set *teacher* pada kondisi berjalan direkam ulang setelah objek ditata kembali; penyimpangan ini dilaporkan sebagai keterbatasan pada Bab 6. Sebuah *run* dinyatakan sah bila jendela ukurnya penuh, *frame* galat tidak lebih dari 1%, simpangan *servo* kepala tidak lebih dari 2 *count*, dan gerak sendi sesuai kondisi yang diuji. *Run* yang gagal kriteria diganti, dan *run* yang diganti tetap diarsipkan.

Metrik yang dihitung adalah rata-rata, median, dan P95 latensi untuk prapemrosesan, inferensi, pascapemrosesan, dan keseluruhan *callback*; FPS efektif menurut Persamaan 2.15 dari cap waktu kamera; penggunaan CPU proses; dan RSS.

Pengujian akurasi pada citra kamera OP3 mengukur kinerja model dengan kamera yang dipakai robot. Pengujian dilakukan secara *offline* pada komputer *onboard* terhadap dua set *frame* berlabel, dengan metrik dan ambang yang sama dengan pengujian pada TEST. Prediksi pada *frame* tanpa objek dihitung sebagai FP, dan hasil pengujian ini tidak dipakai untuk memilih ulang model maupun ambang.

Set Kamera 1 terdiri atas 260 *frame* dari satu rangkaian pengambilan, yaitu 200 *frame* berobjek dan 60 *frame* tanpa objek, ditambah 50 *frame* gawang parsial yang dianalisis terpisah. *Frame* dipilih dari sesi yang telah direkam sebelumnya, termasuk sesi dengan objek bergerak, sehingga set ini bersifat retrospektif dan tidak dipisahkan menurut kondisi robot. Label awal dibuat dengan bantuan prediksi KD murni, lalu seluruh *frame* ditinjau dan diperbaiki manual.

Set Kamera 2 direkam pada 12 November 2026 setelah model, ambang, dan protokol ditetapkan dan setelah pengujian *runtime* selesai, dengan 100 *frame* berobjek dan 30 *frame* tanpa objek pada setiap kondisi diam dan berjalan. Seluruh gawang pada set ini tampak sebagian; kotak gawang diberikan pada bagian bawah gawang dan kotak robot hanya pada badan. Label awal berasal dari gabungan prediksi keempat model, sebanyak 52 *frame* sampel dilabeli lebih dahulu tanpa melihat prediksi, dan seluruh *frame* ditinjau manual. Untuk memeriksa kepekaan hasil terhadap pelabelan, 52 *frame* sampel tersebut juga dilabeli oleh peninjau kedua dan dengan konvensi kotak alternatif, yaitu seluruh rangka gawang dan seluruh tubuh robot yang tampak.

### 3.3.6 Analisis dan Penarikan Kesimpulan

Hasil pengujian dianalisis dengan memetakan setiap rumusan masalah ke pengujian dan metriknya, seperti pada Tabel 3.4. Untuk rumusan masalah nomor 1 dan 2, model hasil KD dibandingkan dengan model *supervised* untuk melihat pengaruh KD dan dengan *teacher* untuk melihat sisa selisih terhadap model yang lebih besar. Perbandingan dilakukan pada TEST dan pada citra kamera OP3 untuk setiap kondisi robot. Untuk rumusan masalah nomor 3 dan 4, model hasil KD dibandingkan dengan *teacher* pada setiap kondisi, beserta perubahan dari kondisi diam ke kondisi berjalan. Pengujian fungsional tidak dipetakan ke rumusan masalah, tetapi dipakai untuk memastikan sistem berjalan sesuai kebutuhan sebelum pengujian akurasi dan *runtime*.

**Tabel 3.4** Pemetaan rumusan masalah ke pengujian dan metrik

| **Rumusan masalah** | **Pengujian**                                                             | **Metrik**                        | **Model yang dibandingkan**           |
|---------------------|---------------------------------------------------------------------------|-----------------------------------|---------------------------------------|
| Nomor 1             | Akurasi berdasarkan mAP pada TEST dan citra kamera OP3 (Subbab 6.2)       | mAP50 dan mAP50‑95                | Hasil KD, *supervised*, dan *teacher* |
| Nomor 2             | *Precision*, *recall*, dan F1 pada TEST dan citra kamera OP3 (Subbab 6.3) | *Precision*, *recall*, dan F1     | Hasil KD, *supervised*, dan *teacher* |
| Nomor 3             | Latensi dan FPS pada *runtime live* (Subbab 6.4)                          | Rata-rata latensi dan FPS efektif | Hasil KD dan *teacher*                |
| Nomor 4             | Penggunaan CPU dan RAM pada *runtime live* (Subbab 6.5)                   | Penggunaan CPU dan RSS            | Hasil KD dan *teacher*                |

Kesimpulan ditarik untuk menjawab setiap rumusan masalah berdasarkan hasil tersebut. Kesimpulan juga menyebut batas yang berasal dari jumlah *seed*, jumlah ulangan, kemiripan sumber antarbagian himpunan data, dan cara pengambilan set *frame* kamera OP3.
