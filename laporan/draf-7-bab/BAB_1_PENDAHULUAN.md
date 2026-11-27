# BAB 1 PENDAHULUAN

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v33 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

## 1.1 Latar Belakang

Robot humanoid yang bermain sepak bola harus memahami keadaan lapangan secara mandiri dari sensor di tubuhnya sendiri, karena robot dituntut otonom dan hanya memakai sensor pasif seperti manusia (Barry, et al., 2019). Pada RoboCup Humanoid Soccer, pengenalan objek yang andal menjadi fondasi keberhasilan permainan, dan sistem visinya mendeteksi antara lain bola, robot, dan tiang gawang (Fiedler, et al., 2019). Aturan yang kini mewajibkan bola sebagian berwarna putih membuat pendeteksi berbasis ekstraksi warna dan bentuk memiliki keterbatasan, sehingga sistem visi beralih ke jaringan saraf konvolusional (*convolutional neural network*, CNN) (Bordado, Silveria, dan Laureano, 2023). Peralihan ini memindahkan beban ke sisi komputasi. Detektor harus cepat sekaligus hemat memori dan daya komputasi, padahal dijalankan pada perangkat keras robot yang terbatas (Barry, et al., 2019; Narayanaswami, et al., 2023).

Keluarga detektor YOLO (*You Only Look Once*) banyak dipilih untuk menjawab tuntutan tersebut. YOLO memprediksi kotak pembatas (*bounding box*) dan probabilitas kelas secara langsung dengan satu jaringan, sehingga model dasarnya mampu memproses citra secara waktu nyata pada 45 *frames per second* (FPS) (Redmon, et al., 2016). Generasi YOLO11 diperkenalkan Ultralytics pada 27 September 2024 (Ultralytics, n.d.d). Khanam dan Hussain (2024) menjelaskan bahwa generasi ini menambahkan blok C3k2 serta *convolutional block with parallel spatial attention* (C2PSA), dengan tetap memakai blok *spatial pyramid pooling - fast* (SPPF). Keluarga ini telah diterapkan pada robot humanoid. Jati, Ilyasa, dan Dominic (2024) memakai YOLO-NAS untuk pelacakan bola, penyelarasan terhadap gawang, dan penghindaran robot. Addufairi dan Setyawan (2026) menerapkan YOLO11 untuk mendeteksi manusia pada robot BRONE yang memakai NVIDIA Jetson Orin Nano. Pada ROBOTIS OP3, Adipratama (2026) memakai YOLOv5 untuk mendeteksi bola dengan rata-rata 34,3 FPS dan waktu inferensi 28,26 ms.

Kemampuan komputasi di tubuh robot menjadi batas yang menentukan. Spesifikasi produsen ROBOTIS OP3 mencantumkan komputer Intel NUC dengan prosesor Intel Core i3 *dual core*, *random access memory* (RAM) 8 GB, dan kamera Logitech C920 (ROBOTIS, n.d.a). Sejumlah penelitian pada perangkat sejenis menjalankan detektor sepenuhnya pada *central processing unit* (CPU). Setyawan, et al. (2026) menguji deteksi bola seluruhnya pada Intel NUC dengan *Robot Operating System* (ROS) tanpa akselerasi *graphics processing unit* (GPU), sedangkan Meneghetti, et al. (2021) mencatat bahwa implementasi resmi YOLO tidak cocok untuk inferensi pada CPU. Lau dan Pottier (2026) membangun sistem visi berbasis YOLOv9 pada OP3 yang dioptimalkan untuk inferensi CPU dan memperoleh 4 sampai 8 FPS. Angka itu dicapai setelah model dikonversi ke ONNX dan OpenVINO serta dikuantisasi. Bahkan tanpa objek yang terdeteksi, laju YOLOv9-T hanya sekitar 8 FPS, lalu turun menjadi 5,92 sampai 6,22 FPS pada uji statis dan 4,41 sampai 6,68 FPS pada uji dinamis (Lau dan Pottier, 2026). Adipratama (2026) juga mengukur penggunaan CPU dan memori sistem deteksi pada OP3, baik saat robot diam maupun saat berjalan.

Saltık, et al. (2025) menyebut adanya tarik-menarik antara kapasitas model dan kecepatan inferensi, karena akurasi detektor cenderung turun ketika model dipangkas atau dikuantisasi agar dapat berjalan pada *edge device*. Kuantisasi mengubah bobot dan aktivasi dari bilangan titik mengambang 32 bit menjadi representasi bit yang lebih rendah, sehingga inferensi dapat dijalankan dengan aritmetika bilangan bulat (Jacob, et al., 2018, p. 2705). Representasi empat bit atau kurang berpotensi menekan kebutuhan memori dan latensi (Gholami, et al., 2021), dan algoritmenya terbagi menjadi *post-training quantization* (PTQ) dan *quantization-aware training* (QAT) (Nagel, et al., 2021). Penelitian ini menempuh jalur lain yang tidak mengubah representasi bobot maupun *runtime* model, yaitu melatih model yang lebih kecil dengan bimbingan model yang lebih besar.

Cara melatih tersebut dikenal sebagai *knowledge distillation* (KD). Hinton, Vinyals, dan Dean (2015) memakai probabilitas kelas yang dihasilkan model besar sebagai target lunak (*soft target*) untuk melatih model kecil. Gou, et al. (2021) menempatkan KD sebagai salah satu jenis kompresi dan percepatan model dalam kerangka *teacher-student*, yaitu model besar sebagai *teacher* membimbing model kecil sebagai *student*. Karena yang diubah hanya cara pelatihan, arsitektur *student* tetap dan biaya inferensinya tidak bertambah (Arik dan Ağgül, 2026; Ultralytics, n.d.a). Penerapan KD pada deteksi objek bahkan telah dirangkum dalam survei tersendiri, dari detektor berbasis CNN sampai *Transformer* (Shehzadi, et al., 2026).

Hasil KD pada keluarga YOLO beragam. Pada deteksi gulma, *channel-wise knowledge distillation* (CWD) dengan *teacher* YOLO11x menaikkan *mean average precision* (mAP) pada ambang *intersection over union* (IoU) 0,50, atau mAP50, milik *student* YOLO11n dari 0,838 menjadi 0,859 (Saltık, et al., 2025). Jung dan Nam (2025) menerapkan KD pada peta fitur YOLOv11 untuk deteksi jatuh dan memperoleh kenaikan mAP sekaligus pemangkasan waktu proses 0,8 ms. Sharma, et al. (2026) melaporkan *student* yang mAP-nya lebih rendah 1,4 poin daripada *teacher* YOLOv8-L dan berjalan pada 61 FPS dengan presisi titik mengambang 16 bit (FP16) di NVIDIA Jetson Nano. Hasil KD tidak selalu menonjol. Pada deteksi retakan struktur, Arik dan Ağgül (2026) mendapati *pseudo-labeling* memberi kenaikan yang lebih besar dan lebih stabil daripada KD yang memadukan label dengan sinyal lunak *teacher*. Di Indonesia, KD pernah diterapkan pada YOLO untuk robot *service* (Billy, 2019) dan pada YOLOv5 untuk rambu lalu lintas dengan mAP50 sebesar 0,953 pada 25 kelas (Zaini, 2024).

Sepanjang penelusuran penulis, penelitian KD pada keluarga YOLO tersebut dievaluasi pada domain di luar sepak bola robot (Billy, 2019; Zaini, 2024; Saltık, et al., 2025; Jung dan Nam, 2025; Arik dan Ağgül, 2026; Sharma, et al., 2026), sedangkan penelitian deteksi objek pada OP3 belum memakai KD (Adipratama, 2026; Lau dan Pottier, 2026). Belum ditemukan penelitian yang mengevaluasi model YOLO11 hasil KD pada komputer yang terpasang di tubuh OP3 (komputer *onboard*) dan hanya mengandalkan CPU dengan *Robot Operating System 2* (ROS 2), baik dari sisi akurasi maupun dari sisi latensi dan penggunaan sumber daya saat robot diam dan berjalan. Celah ini relevan karena versi OP3 tahun 2025 dikembangkan untuk ROS 2 (ROBOTIS, n.d.a).

Berdasarkan celah tersebut, penelitian ini mengimplementasikan sistem deteksi objek berbasis ROS 2 yang menjalankan *student* YOLO11 hasil KD dari *teacher* YOLO11n pada komputer *onboard* ROBOTIS OP3. *Student* memakai skala khusus yang lebih kecil daripada YOLO11n, yang dalam penelitian ini disebut skala t. Model hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised*, yaitu hanya dengan label himpunan data tanpa bimbingan *teacher*, agar pengaruh KD terpisah dari pengaruh ukuran model, serta dengan *teacher* sebagai acuan. Perbandingan mencakup akurasi pada himpunan data dan pada citra kamera OP3, latensi, FPS, serta penggunaan CPU dan RAM. Pengujian pada robot dilakukan saat robot diam dan berjalan.

## 1.2 Rumusan Masalah

Berdasarkan latar belakang tersebut, rumusan masalah penelitian ini adalah sebagai berikut.

1.  Bagaimana tingkat akurasi, berdasarkan nilai mAP, model *student* hasil KD hibrida dibandingkan dengan *student* berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?

2.  Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?

3.  Berapa rata-rata latensi dan FPS ketiga model tersebut saat beroperasi secara *real-time* pada komputer *onboard* OP3 dalam kondisi robot diam dan berjalan?

4.  Bagaimana penggunaan CPU dan RAM ketiga model tersebut pada komputer *onboard* OP3?

## 1.3 Tujuan

Untuk menjawab rumusan masalah tersebut, penelitian ini mengimplementasikan sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil KD pada robot humanoid ROBOTIS OP3. Tujuan penelitian ini adalah sebagai berikut.

1.  Mengetahui tingkat akurasi berdasarkan nilai mAP model *student* hasil KD hibrida dibandingkan dengan *student* berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n.

2.  Mengetahui kinerja ketiga model tersebut berdasarkan nilai *precision*, *recall*, dan *F1-score*.

3.  Mengukur rata-rata latensi dan FPS ketiga model tersebut saat beroperasi secara *real-time* pada komputer *onboard* OP3 dalam kondisi robot diam dan berjalan.

4.  Mengukur penggunaan CPU dan RAM ketiga model tersebut pada komputer *onboard* OP3.

## 1.4 Manfaat

Bagi tim ROBOTIIK Divisi Humanoid, penelitian ini diharapkan menghasilkan sistem deteksi bola, gawang, dan robot berbasis ROS 2 yang dapat dijalankan pada komputer *onboard* OP3, beserta data akurasi, latensi, FPS, serta penggunaan CPU dan RAM yang dapat dipakai sebagai dasar pemilihan model.

Bagi penelitian KD pada sistem tertanam (*embedded system*), penelitian ini diharapkan memberi gambaran tentang pengaruh KD terhadap *student* berukuran kecil pada robot yang hanya mengandalkan CPU. Pembanding berupa *student* berarsitektur sama yang dilatih secara *supervised* memisahkan pengaruh KD dari pengaruh ukuran model, sedangkan prosedur pelatihan dan pengujian yang terdokumentasi dapat dipakai ulang untuk menilai metode lain.

## 1.5 Batasan Masalah

Ruang lingkup penelitian ini dibatasi sebagai berikut.

1.  Objek yang dideteksi terbatas pada tiga kelas, yaitu bola (label *ball*), gawang, dan robot.

2.  Himpunan data yang digunakan adalah himpunan data Roboflow advance_vision_human versi 1 (Humanoid-Atom, 2026) dengan pembagian bagian latih, validasi, dan uji bawaan himpunan data tersebut.

3.  *Teacher* yang digunakan adalah YOLO11n yang telah dilatih sebelumnya lalu dibekukan. *Student* adalah YOLO11 berskala khusus dengan faktor kedalaman 0,50 dan faktor lebar 0,125 (810.649 parameter sebelum *Conv-BN fusion*), yang dalam penelitian ini disebut skala t. Skala ini bukan salah satu skala resmi YOLO11, yaitu n, s, m, l, dan x (Ultralytics, n.d.d), sehingga *student* berbeda dari YOLO11n standar.

4.  Model hasil KD yang dimaksud pada rumusan masalah adalah *student* KD hibrida penuh. *Student* KD murni disertakan sebagai pembanding tambahan, sehingga ketiga model yang dibandingkan adalah KD hibrida, *supervised*, dan *teacher* YOLO11n.

5.  Seluruh model dijalankan sebagai berkas .pt PyTorch dengan presisi titik mengambang 32 bit (FP32). Konversi ke ONNX atau OpenVINO serta kuantisasi, termasuk representasi bilangan bulat 8 bit (INT8), PTQ, dan QAT, tidak termasuk dalam penelitian ini.

6.  Pelatihan model dilakukan di server laboratorium yang memakai GPU, sedangkan komputer *onboard* robot hanya menjalankan inferensi.

7.  Unit ROBOTIS OP3 yang digunakan memakai komputer *onboard* Intel NUC dengan prosesor Intel Core i5-1240P (12 inti fisik dan 16 *thread* logis) dan kamera Logitech C920, berbeda dari spesifikasi produsen yang mencantumkan Intel Core i3 (ROBOTIS, n.d.a). Inferensi dijalankan pada CPU tanpa akselerator.

8.  Perangkat lunak robot memakai ROS 2 Jazzy pada sistem operasi Ubuntu 24.04.

9.  Kondisi robot yang diuji adalah diam dan berjalan. Definisi operasional kedua kondisi dijelaskan pada Bab 3.

10. Ukuran sisi masukan model (imgsz) adalah 640 piksel. Pada *predict path*, *frame* kamera 640 × 480 piksel diubah dengan *letterbox* menjadi tensor 480 × 640 piksel.

11. Objek uji pada pengujian *runtime* ditempatkan statis. Pelacakan objek dijalankan pada *node* deteksi, tetapi akurasi pelacakan tidak termasuk tujuan penelitian.

12. Pengujian akurasi pada citra kamera OP3 dilakukan secara *offline* pada set *frame* dari lingkungan laboratorium yang sama, sehingga hasilnya tidak mewakili generalisasi lintas adegan.

## 1.6 Sistematika Pembahasan

Skripsi ini disusun dalam tujuh bab dengan uraian singkat sebagai berikut.

BAB 1 Pendahuluan memuat latar belakang, rumusan masalah, tujuan, manfaat, batasan masalah, dan sistematika pembahasan.

BAB 2 Landasan Kepustakaan memuat kajian pustaka tentang penelitian KD pada detektor objek dan penelitian deteksi objek pada robot humanoid, serta dasar teori tentang ROBOTIS OP3, YOLO11, KD, ROS 2, dan metrik akurasi serta kinerja yang digunakan.

BAB 3 Metodologi Penelitian memuat tipe penelitian, strategi dan rancangan penelitian, serta metode setiap tahap mulai dari studi pustaka sampai analisis dan penarikan kesimpulan.

BAB 4 Rekayasa Kebutuhan memuat kajian masalah, identifikasi *stakeholder*, kebutuhan fungsional sistem, spesifikasi sistem, serta analisis kebutuhan perangkat keras dan perangkat lunak sistem deteksi objek pada OP3.

BAB 5 Perancangan dan Implementasi memuat perancangan perangkat keras dan perangkat lunak setiap subsistem, yaitu pelatihan model, inferensi, dan *node* ROS 2, beserta implementasinya pada server dan robot.

BAB 6 Pengujian memuat pengujian fungsional, lalu pengujian yang menjawab rumusan masalah secara berurutan, yaitu akurasi berdasarkan mAP, *precision*, *recall*, dan *F1-score*, latensi dan FPS, serta penggunaan CPU dan RAM pada kondisi robot diam dan berjalan, diikuti pengujian tambahan. Setiap pengujian diuraikan dari tujuan, prosedur, hasil, dan analisis hasil, lalu bab ini ditutup dengan evaluasi keseluruhan.

BAB 7 Penutup memuat kesimpulan yang menjawab rumusan masalah dan saran untuk penelitian berikutnya.
