# BAB 2 LANDASAN KEPUSTAKAAN

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v23 (25 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

## 2.1 Kajian Pustaka

Subbab ini merangkum penelitian terdahulu yang paling dekat dengan penelitian ini dalam dua kelompok, yaitu penelitian KD pada detektor objek dan penelitian deteksi objek pada robot humanoid. Ringkasan kedua kelompok disajikan pada Tabel 2.1 dan Tabel 2.2, sedangkan posisi penelitian ini dijelaskan pada Subbab 2.1.3.

### 2.1.1 Penelitian KD pada Detektor Objek

Penelitian KD pada keluarga YOLO berbeda dalam pasangan *teacher* dan *student*, sinyal yang didistilasi, dan perangkat pengujian. Saltık, et al. (2025) mendistilasi YOLO11x ke YOLO11n untuk deteksi gulma dengan CWD dan *masked generative distillation* (MGD), lalu menguji *student* pada NVIDIA Jetson Orin Nano dan Raspberry Pi 5. Jung dan Nam (2025) memakai YOLOv11-M sebagai *teacher* serta YOLOv11-S dan YOLOv11-N sebagai *student*, dengan gabungan *mean squared error* (MSE) untuk keselarasan spasial dan divergensi Kullback-Leibler (KL) untuk distribusi per kanal pada peta fitur. Arik dan Ağgül (2026) membandingkan KD dengan *pseudo-labeling* untuk *student* YOLOv11-N dari *teacher* YOLOv11-L; hasil terbaiknya, mAP50 0,81 yang mendekati *teacher* (0,84), diperoleh dengan *pseudo-labeling*.

Penelitian lain memadukan KD dengan teknik kompresi atau memakai *student* dari keluarga arsitektur yang berbeda. Sabaghian, Keyvanrad, dan Moghadami (2025) memangkas kanal YOLOv8m lalu memulihkan akurasinya dengan CWD dari model asal, sehingga parameter turun dari 25,85 juta menjadi 6,85 juta, *average precision* (AP) pada ambang IoU 0,50, atau AP50, berkurang 2,7%, dan laju naik dari 26 menjadi 45 FPS pada GPU NVIDIA GeForce GTX 1080. Sharma, et al. (2026) memakai *teacher* YOLOv8-L dan *student* berbasis MobileNetV3-Large dengan tiga sinyal distilasi, lalu menjalankannya pada NVIDIA Jetson Nano. *Student* tersebut mencapai mAP50‑95, yaitu rata-rata mAP pada ambang IoU 0,50 sampai 0,95, sebesar 38,6. Di Indonesia, Billy (2019) menaikkan mAP detektor YOLO dengan *feature extractor* MobileNet pada himpunan data PASCAL VOC dari 0,3850 menjadi 0,4215 melalui KD, serta memakai *batchnorm fusion* untuk menaikkan laju dari 8,3 menjadi 16,66 FPS pada laptop dengan CPU i7. Zaini (2024) menerapkan KD pada YOLOv5 untuk 25 kelas rambu lalu lintas dengan mAP50 sebesar 0,953.

Ringkasan ketujuh penelitian tersebut disajikan pada Tabel 2.1. Pengujian kecepatan dilakukan pada GPU, perangkat NVIDIA Jetson, Raspberry Pi, atau laptop, dan tidak satu pun dari ketujuh penelitian ini menguji model hasil KD pada robot humanoid sepak bola.

**Tabel 2.1** Penelitian terdahulu tentang KD pada detektor objek

| **Penelitian**                             | **Objek dan perangkat**                            | ***Teacher* ke *student***                                | **Metode KD**                                                   | **Metrik dan hasil pokok**                                                     | **Perbedaan dengan penelitian ini**              |
|--------------------------------------------|----------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------|
| Billy (2019)                               | Robot *service*; himpunan data VOC; laptop CPU i7  | *Student* YOLO dengan *feature extractor* MobileNet       | KD pada keluaran bertemperatur; *batchnorm fusion*              | mAP 0,3850 menjadi 0,4215; 8,3 menjadi 16,66 FPS                               | Bukan robot humanoid; YOLO generasi lama         |
| Zaini (2024)                               | Rambu lalu lintas Indonesia, 25 kelas              | YOLOv5 (varian tidak tercantum pada berkas yang tersedia) | KD (rincian tidak tersedia pada berkas)                         | mAP50 0,953; inferensi 0,029 s                                                 | Domain rambu; tidak diuji pada robot             |
| Sabaghian, Keyvanrad, dan Moghadami (2025) | Citra udara VisDrone; GPU GTX 1080                 | YOLOv8m asal ke YOLOv8m terpangkas                        | *Pruning* kanal dan CWD                                         | Parameter 25,85 juta menjadi 6,85 juta; AP50 berkurang 2,7%; 26 menjadi 45 FPS | KD sebagai pemulih *pruning*; GPU                |
| Saltık, et al. (2025)                      | Gulma; Jetson Orin Nano dan Raspberry Pi 5         | YOLO11x ke YOLO11n                                        | CWD dan MGD                                                     | mAP50 0,838 menjadi 0,859                                                      | Domain pertanian; tanpa ROS 2                    |
| Jung dan Nam (2025)                        | Deteksi jatuh pada CCTV                            | YOLOv11-M ke YOLOv11-S dan YOLOv11-N                      | Peta fitur dengan MSE dan KL per kanal                          | mAP naik; waktu proses turun 0,8 ms                                            | Domain pengawasan; bukan robot                   |
| Arik dan Ağgül (2026)                      | Retakan struktur; Raspberry Pi 3B+ dan Jetson Nano | YOLOv11-L ke YOLOv11-N                                    | KD (label dan sinyal lunak *teacher*) dan *pseudo-labeling*     | Terbaik *pseudo-labeling*: mAP50 0,81 (*teacher* 0,84)                         | Uji perangkat tepi untuk model *pseudo-labeling* |
| Sharma, et al. (2026)                      | MS-COCO dan VisDrone; Jetson Nano                  | YOLOv8-L ke MobileNetV3-Large                             | KL bertemperatur, afinitas kanal, dan *detection fidelity loss* | 38,6 mAP50‑95; 61 FPS (FP16)                                                   | *Student* beda keluarga; GPU                     |

### 2.1.2 Penelitian Deteksi Objek pada Robot Humanoid

Penelitian deteksi objek pada robot humanoid berangkat dari keterbatasan perangkat. Barry, et al. (2019) mendapati Tiny-YOLO hanya mencapai 0,14 FPS pada Raspberry Pi 3 B, lalu merancang xYOLO yang mencapai 9,66 FPS pada perangkat yang sama dengan mengorbankan sebagian akurasi. Fiedler, et al. (2019) membangun *pipeline* visi ROS berbahasa Python yang memakai *fully convolutional neural network* (FCNN) untuk bola dan metode konvensional untuk robot serta tiang gawang, dan memproses 8,1 citra per detik pada NVIDIA Jetson TX2. Meneghetti, et al. (2021) membandingkan sejumlah arsitektur jaringan kecil untuk deteksi bola dan mendapati MobileNetV3 memberi keseimbangan yang baik antara mAP dan waktu inferensi pada perangkat terbatas, sedangkan implementasi resmi YOLO tidak cocok untuk CPU. Narayanaswami, et al. (2023) mengembangkan xYOLO dan SSD-MobileNet untuk robot NAO v6 yang memakai CPU Intel Atom E3845; salah satu varian xYOLO mencapai mAP50 95,6% dengan waktu jalan 7,7 ms pada CPU.

Penelitian yang lebih baru memakai YOLO generasi baru dan perangkat yang beragam. Bordado, Silveria, dan Laureano (2023) menjalankan YOLOv5 *nano* untuk deteksi dan pelacakan bola pada Intel NUC 11, NVIDIA Jetson Nano, dan Raspberry Pi 4 B; pada validasi, YOLOv5 *small* mencapai mAP50 kelas bola 0,988. Jati, Ilyasa, dan Dominic (2024) membandingkan YOLO-NAS dengan YOLOv8 dan YOLOv7 pada NVIDIA Jetson Nano; YOLOv7 memberi laju *pipeline* tertinggi, 28,9 FPS, sedangkan YOLO-NAS mencapai tingkat keberhasilan 53,3% pada tugas pelacakan bola. Addufairi dan Setyawan (2026) menerapkan YOLO11 dengan TensorRT pada robot BRONE yang memakai NVIDIA Jetson Orin Nano dan memperoleh mAP50 0,995 dengan laju 27,61 FPS. Setyawan, et al. (2026) mengembangkan *augmented Haar cascade classifier* pada Intel NUC tanpa GPU dengan ROS; metode ini mencapai akurasi 97% dengan 0,00849 s per *frame*, sedangkan YOLOv5 sebagai pembanding mencapai akurasi 99% tetapi memerlukan 0,0344 s per *frame* dan memori 22,3%.

Dua penelitian memakai ROBOTIS OP3. Lau dan Pottier (2026) menjalankan YOLOv9 pada OP3 dengan prosesor Intel Core i3-6100U dan ROS Kinetic setelah model dikonversi ke ONNX dan OpenVINO serta dikuantisasi, dan memperoleh 4 sampai 8 FPS. Adipratama (2026) memakai YOLOv5 dan Convex Hull pada OP3 dengan Intel NUC7i3BNK dan ROS Noetic; sistemnya mencapai *precision* 0,985, *recall* 1,000, mAP50 0,995, dan mAP50‑95 0,961 dengan rata-rata 34,3 FPS, dan penggunaan CPU serta memorinya diukur saat robot diam dan berjalan. Ringkasan penelitian kelompok ini disajikan pada Tabel 2.2.

**Tabel 2.2** Penelitian terdahulu tentang deteksi objek pada robot humanoid

| **Penelitian**                         | **Robot dan komputer**                                            | **Detektor**                                            | **Perangkat lunak dan *runtime***       | **Metrik dan hasil pokok**                            | **Perbedaan dengan penelitian ini** |
|----------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------|-----------------------------------------|-------------------------------------------------------|-------------------------------------|
| Barry, et al. (2019)                   | Robot humanoid berbiaya rendah; Raspberry Pi 3 B                  | xYOLO, turunan Tiny-YOLO                                | Tidak dirinci                           | 9,66 FPS (Tiny-YOLO 0,14 FPS)                         | Tanpa KD; hanya bola dan gawang     |
| Fiedler, et al. (2019)                 | Robot humanoid *kid-size*; Jetson TX2                             | FCNN untuk bola; metode konvensional untuk objek lain   | ROS, Python                             | 8,1 citra per detik                                   | Tanpa KD; GPU                       |
| Meneghetti, et al. (2021)              | Robot bergerak; Core i5, V100, dan Xeon                           | MobileNet dan YOLO                                      | Tidak dirinci                           | MobileNetV3 seimbang pada perangkat terbatas          | Hanya bola; tanpa KD                |
| Bordado, Silveria, dan Laureano (2023) | Robot humanoid Marta; Intel NUC 11, Jetson Nano, Raspberry Pi 4 B | YOLOv5 *nano* dan *optical flow*                        | Tidak dirinci                           | mAP50 bola 0,988 (YOLOv5 *small*, validasi)           | Tanpa KD                            |
| Narayanaswami, et al. (2023)           | NAO v6; Intel Atom E3845                                          | xYOLO dan SSD-MobileNet                                 | Tidak dirinci                           | mAP50 95,6%; 7,7 ms pada CPU                          | Robot NAO; tanpa KD                 |
| Jati, Ilyasa, dan Dominic (2024)       | Robot humanoid sepak bola; Jetson Nano                            | YOLO-NAS, YOLOv8, YOLOv7                                | PyTorch dan TensorRT, FP16              | YOLOv7 28,9 FPS; YOLO-NAS 53,3% berhasil melacak bola | GPU; tanpa KD                       |
| Addufairi dan Setyawan (2026)          | Robot BRONE; Jetson Orin Nano                                     | YOLO11                                                  | TensorRT                                | mAP50 0,995; 27,61 FPS                                | Deteksi manusia; GPU                |
| Setyawan, et al. (2026)                | Robot humanoid; Intel NUC tanpa GPU                               | *Augmented Haar cascade classifier* (pembanding YOLOv5) | ROS                                     | Akurasi 97%; 0,00849 s per *frame*                    | Metode klasik; tanpa KD             |
| Lau dan Pottier (2026)                 | ROBOTIS OP3; Core i3-6100U                                        | YOLOv9-T, YOLOv9-S, YOLOv9-M                            | ROS Kinetic; ONNX, OpenVINO, kuantisasi | 4 sampai 8 FPS                                        | Kuantisasi dan ROS 1; tanpa KD      |
| Adipratama (2026)                      | ROBOTIS OP3; NUC7i3BNK                                            | YOLOv5 dan Convex Hull                                  | ROS Noetic                              | mAP50 0,995; 34,3 FPS                                 | ROS 1; tanpa KD; hanya bola         |

### 2.1.3 Posisi Penelitian

Kedua kelompok penelitian tersebut jarang bersinggungan. Penelitian KD pada keluarga YOLO dievaluasi pada domain di luar sepak bola robot dan umumnya diuji kecepatannya di luar robot, sedangkan penelitian deteksi objek pada robot humanoid belum memakai KD. Penelitian ini mengambil posisi di antara keduanya dengan tiga keunikan. Dari sisi data, model dilatih pada citra robot sepak bola dengan tiga kelas dan diperiksa pada citra dari kamera OP3. Dari sisi metode, *student* YOLO11 skala t dilatih dengan KD dari *teacher* YOLO11n memakai resep pelatihan yang sama dengan *student* yang dilatih secara *supervised*, masing-masing dengan tiga *seed* acak, sehingga pengaruh KD dapat dipisahkan dari pengaruh ukuran model dan variasi pelatihan. Dari sisi arsitektur sistem, model dijalankan sebagai *node* ROS 2 Jazzy pada CPU komputer *onboard* OP3 dan diuji saat robot diam dan berjalan. Keunikan ini dinyatakan dalam batas pustaka yang ditelusuri penulis.

## 2.2 Dasar Teori

Subbab ini menguraikan teori yang mendasari penelitian, mulai dari robot yang digunakan sampai metrik pengujian.

### 2.2.1 Robot Humanoid ROBOTIS OP3

ROBOTIS OP3 adalah robot humanoid berukuran kecil buatan ROBOTIS dan merupakan penerus ROBOTIS OP (DARwIn-OP) serta ROBOTIS OP2 (ROBOTIS, n.d.a). DARwIn-OP sendiri dikembangkan sebagai robot humanoid terbuka dengan struktur modular berbasis jaringan dan arsitektur *personal computer* (PC) standar, sehingga sistemnya dapat dikembangkan, mudah dipelihara, memakai lingkungan pengembangan yang lazim, dan terjangkau harganya (Ha, Tamura, dan Asama, 2013).

Spesifikasi produsen OP3 mencakup tinggi sekitar 510 mm, bobot sekitar 3,5 kg, dan 20 derajat kebebasan (*degree of freedom*, DOF) dengan aktuator XM430‑W350‑R. Pengendali utamanya adalah Intel NUC dengan prosesor Intel Core i3 *dual core* dan RAM 8 GB, subpengendalinya OpenCR, kameranya Logitech C920, dan sensornya meliputi giroskop, akselerometer, serta magnetometer tiga sumbu (ROBOTIS, n.d.a). Versi OP3 tahun 2025 dikembangkan untuk ROS 2 (ROBOTIS, n.d.a). Unit yang digunakan dalam penelitian ini memakai komputer *onboard* yang berbeda dari spesifikasi tersebut, seperti dijelaskan pada Subbab 1.5. Gambar 2.1 memperlihatkan robot OP3.

**Gambar 2.1** Robot humanoid ROBOTIS OP3

### 2.2.2 Deteksi Objek dan YOLO11

YOLO merumuskan deteksi objek sebagai masalah regresi kotak pembatas yang terpisah secara spasial beserta probabilitas kelasnya. Citra dibagi menjadi *grid* $S \times S$, dan satu jaringan memprediksi kotak pembatas serta probabilitas kelas secara langsung dari citra utuh (Redmon, et al., 2016).

YOLO11 tersusun atas tiga komponen. *Backbone* mengubah citra menjadi peta fitur multiskala, *neck* menggabungkan dan memperkuat fitur antarskala, dan *head* menghasilkan prediksi (Khanam dan Hussain, 2024). Blok C3k2 menggantikan blok C2f pada versi sebelumnya, blok SPPF dipertahankan, dan blok C2PSA ditambahkan (Khanam dan Hussain, 2024). Ultralytics menyediakan beberapa skala YOLO11; skala terkecil, YOLO11n, berukuran 2,6 juta parameter dan 6,5 miliar operasi titik mengambang (*floating point operations*, FLOPs) pada masukan 640 piksel (Ultralytics, n.d.d). Pada konfigurasi model penelitian ini, *head* Detect menerima fitur dari tiga skala. Gambar 2.2 memperlihatkan susunan umum arsitektur tersebut.

**Gambar 2.2** Susunan umum arsitektur YOLO11

Sumber: Diadaptasi dari Khanam dan Hussain (2024)

Sejumlah detektor satu tahap memodelkan letak tepi kotak sebagai distribusi umum alih-alih satu nilai tunggal melalui *distribution focal loss* (DFL) yang diperkenalkan dalam *generalized focal loss* (Li, et al., 2020). Pendahulu YOLO11, yaitu YOLOv8, memakai *binary cross-entropy* (BCE) untuk klasifikasi, *complete* IoU (CIoU) untuk regresi, dan DFL dalam *loss*-nya (Sabaghian, Keyvanrad, dan Moghadami, 2025). Prediksi yang bertumpang tindih kemudian disaring dengan *non-maximum suppression* (NMS): kotak diurutkan menurut skornya, kotak berskor tertinggi dipilih, lalu kotak lain yang tumpang tindihnya dengan kotak itu melebihi ambang dibuang (Bodla, et al., 2017).

### 2.2.3 *Knowledge Distillation*

KD melatih model kecil agar meniru model besar. Hinton, Vinyals, dan Dean (2015) menaikkan temperatur $T$ pada fungsi *softmax* agar model besar menghasilkan distribusi probabilitas kelas yang lebih lunak, lalu memakainya sebagai target bagi model kecil. Probabilitas kelas ke-$i$ dihitung dengan Persamaan 2.1.

> $q_{i} = \frac{\exp\left( \frac{z_{i}}{T} \right)}{\sum_{j}^{}{\exp\left( \frac{z_{j}}{T} \right)}}$ (2.1)

Keterangan:

> $q_{i}$ : probabilitas kelas ke-$i$, yaitu peluang bernilai 0 sampai 1 bahwa objek termasuk kelas tersebut
>
> $z_{i}$ : *logit* kelas ke-$i$, yaitu nilai mentah keluaran model sebelum diubah menjadi probabilitas
>
> $T$ : temperatur; makin besar nilainya, makin rata sebaran probabilitas antarkelas
>
> $j$ : nomor kelas yang dijumlahkan pada penyebut, dari kelas pertama sampai kelas terakhir, sehingga jumlah probabilitas semua kelas sama dengan 1
>
> exp : fungsi eksponensial, yaitu bilangan Euler (sekitar 2,718) yang dipangkatkan dengan nilai di dalam kurung

Nilai $T = 1$ menghasilkan *softmax* biasa, sedangkan $T$ yang lebih besar menghasilkan distribusi yang lebih lunak (Hinton, Vinyals, dan Dean, 2015).

*Loss* pelatihan *student* merupakan rata-rata berbobot dari dua *cross-entropy*, yaitu terhadap target lunak *teacher* pada temperatur yang sama dan terhadap label yang benar pada temperatur 1. Karena besar gradien dari target lunak berskala $\frac{1}{T^{2}}$, suku tersebut dikalikan $T^{2}$ (Hinton, Vinyals, dan Dean, 2015). Bentuk ini dituliskan sebagai Persamaan 2.2.

> $L_{\text{KD}} = (1 - \alpha)H\left( y,q_{s}^{(1)} \right) + \alpha T^{2}H\left( q_{t}^{(T)},q_{s}^{(T)} \right)$ (2.2)

Keterangan:

> $L_{\text{KD}}$ : nilai *loss* KD, yaitu ukuran kesalahan yang diperkecil selama pelatihan *student*
>
> $\alpha$ : bobot bernilai 0 sampai 1 yang mengatur porsi suku label dan suku *teacher*
>
> $H$ : fungsi *cross-entropy*, yaitu ukuran perbedaan dua distribusi probabilitas; nilainya makin kecil bila kedua distribusi makin mirip
>
> $y$ : label yang benar dari himpunan data
>
> $q_{s}^{(1)}$ : distribusi probabilitas *student* pada $T = 1$ menurut Persamaan 2.1
>
> $q_{t}^{(T)}$, $q_{s}^{(T)}$ : distribusi probabilitas *teacher* dan *student* pada temperatur $T$ menurut Persamaan 2.1
>
> $T^{2}$ : faktor pengali agar besar gradien suku *teacher* tetap sebanding ketika temperatur dinaikkan

Gou, et al. (2021) mengelompokkan pengetahuan yang dipindahkan menjadi tiga jenis. Pengetahuan berbasis respons berasal dari keluaran lapisan akhir *teacher*, pengetahuan berbasis fitur berasal dari representasi lapisan tengah, dan pengetahuan berbasis relasi berasal dari hubungan antarlapisan atau antarsampel data.

Ukuran *teacher* tidak selalu sebanding dengan mutu *student*. Cho dan Hariharan (2019) mendapati bahwa model yang lebih besar sering kali bukan *teacher* yang lebih baik, karena kapasitas yang tidak sepadan membuat *student* kecil tidak mampu meniru *teacher* besar. Mirzadeh, et al. (2020) memakai *teacher assistant* untuk menjembatani kesenjangan antara *teacher* dan *student*, sedangkan Huang, et al. (2022, p. 33716) mendapati bahwa pencocokan persis prediksi dengan divergensi KL dapat mengganggu pelatihan bila *teacher* jauh lebih kuat, lalu menggantinya dengan *loss* berbasis korelasi. Temuan ini menjadi dasar uji ablasi *teacher* yang lebih besar pada Subbab 3.3.4.

Keberhasilan KD juga tidak berarti *student* benar-benar meniru *teacher*. Stanton, et al. (2021, p. 6906) menunjukkan bahwa KD dapat memperbaiki generalisasi *student*, tetapi sebaran prediksi *student* sering tetap berbeda cukup jauh dari sebaran prediksi *teacher*, bahkan ketika kapasitas *student* memadai. Karena itu, mutu *student* hasil KD pada penelitian ini dinilai dari metrik deteksi terhadap label, bukan dari kemiripannya dengan *teacher*.

### 2.2.4 KD pada Detektor Objek

Distilasi fitur memindahkan representasi lapisan tengah. FitNets memakai representasi tengah *teacher* sebagai *hint* dan menambahkan lapisan regresi pada lapisan *student* yang dipandu agar keluarannya sebanding dengan *hint* tersebut (Romero, et al., 2015). Chen, et al. (2017, p. 743) menerapkan gagasan ini pada detektor objek dengan *hint learning* dan lapisan adaptasi, serta *cross-entropy* berbobot untuk menangani ketidakseimbangan antara kelas latar dan objek. Wang, et al. (2019) membatasi imitasi fitur pada daerah di sekitar *anchor* objek melalui *imitation mask*, sedangkan Shu, et al. (2021) menormalkan peta aktivasi setiap kanal menjadi peta probabilitas lunak lalu meminimalkan divergensi KL antara *teacher* dan *student*.

Distilasi respons pada detektor padat perlu memperhatikan cara klasifikasinya. Detektor padat memakai fungsi *sigmoid* untuk setiap kelas, sehingga distilasi berbasis *softmax* mengabaikan skor absolut setiap kelas; karena itu, Yang, et al. (2023) memakai BCE untuk mendistilasi setiap peta klasifikasi biner hasil *sigmoid*. Untuk lokalisasi, Zheng, et al. (2022) mengubah kotak pembatas menjadi distribusi probabilitas lalu mendistilasi distribusi tepi kotak dari *teacher* ke *student*.

Ultralytics menyediakan KD bawaan melalui argumen distill_model untuk berkas *teacher* dan argumen dis untuk bobot *loss* distilasi dengan nilai bawaan 6,0. Fitur *student* diselaraskan ke jumlah kanal *teacher* oleh proyektor berupa dua konvolusi 1 × 1 dengan *rectified linear unit* (ReLU), lalu dibandingkan memakai *loss* L2 yang dibobot keyakinan kelas *teacher* (Ultralytics, n.d.a).

Penelitian ini memakai tiga suku distilasi. Bobot setiap titik prediksi $i$ diambil dari keyakinan kelas tertinggi *teacher* (Persamaan 2.3).

> $w_{i} = \max_{c}{\sigma\left( z_{t,i,c} \right)}$ (2.3)

Keterangan:

> $w_{i}$ : bobot titik prediksi ke-$i$; titik prediksi adalah setiap posisi pada peta keluaran tempat detektor menebak objek
>
> $z_{t,i,c}$ : *logit* kelas $c$ dari *teacher* pada titik $i$, yaitu rata-rata *logit* dua cabang *head* Detect
>
> $\sigma$ : fungsi *sigmoid*, yang mengubah *logit* menjadi nilai keyakinan 0 sampai 1
>
> max : nilai terbesar di antara semua kelas $c$, yaitu bola, gawang, dan robot

Dengan bobot ini, titik yang diyakini *teacher* berisi objek berpengaruh lebih besar daripada titik yang berisi latar.

*Loss* fitur pada setiap skala membandingkan fitur *student* yang telah diproyeksikan dengan fitur *teacher* (Persamaan 2.4). Bentuk ini sama dengan *loss* L2 berbobot pada KD bawaan Ultralytics (Ultralytics, n.d.a).

> $L_{\text{fitur}}^{l} = \frac{\sum_{i,c}^{}{w_{i}\left( G_{c,i}^{l} - F_{t,c,i}^{l} \right)^{2}}}{C_{l}\sum_{i}^{}w_{i} + \varepsilon}$ (2.4)

Keterangan:

> $L_{\text{fitur}}^{l}$ : *loss* fitur pada skala $l$
>
> $l$ : skala peta fitur; penelitian ini memakai tiga skala, yaitu P3, P4, dan P5
>
> $G_{c,i}^{l}$ : fitur *student* yang telah diproyeksikan ke jumlah kanal *teacher*, pada kanal $c$ dan posisi $i$
>
> $F_{t,c,i}^{l}$ : fitur *teacher* pada kanal $c$ dan posisi $i$
>
> $w_{i}$ : bobot titik $i$ menurut Persamaan 2.3
>
> $C_{l}$ : jumlah kanal fitur pada skala $l$
>
> $\varepsilon$ : bilangan positif yang sangat kecil agar tidak terjadi pembagian dengan nol
>
> $i$, $c$ : nomor posisi dan nomor kanal; penjumlahan mencakup seluruh posisi dan kanal pada semua citra dalam satu *batch*, yaitu kelompok citra yang diproses bersama dalam satu langkah pelatihan

Selisih fitur dikuadratkan agar selisih positif dan negatif sama-sama menambah *loss*, sedangkan penyebut menormalkan hasilnya terhadap jumlah kanal dan total bobot.

*Loss* kotak adalah rata-rata Smooth L1, *loss* regresi kotak yang lazim pada detektor (Chen, et al., 2017, p. 746; Li, et al., 2020), antara keluaran kotak *student* dan *teacher* (Persamaan 2.5).

> $L_{\text{kotak}} = \frac{1}{N}\sum_{n = 1}^{N}{\mathcal{l}_{\text{SL1}}\left( b_{s,n} - b_{t,n} \right)}$ (2.5)

Keterangan:

> $L_{\text{kotak}}$ : *loss* kotak
>
> $b_{s,n}$, $b_{t,n}$ : elemen keluaran kotak ke-$n$ dari *student* dan dari *teacher*
>
> $N$ : jumlah seluruh elemen keluaran kotak; nilai *loss* adalah rata-rata atas semua elemen tersebut
>
> $n$ : nomor elemen keluaran kotak, dari 1 sampai $N$
>
> $\mathcal{l}_{\text{SL1}}$ : fungsi Smooth L1 dengan ambang 1: selisih yang kurang dari 1 dihitung sebagai setengah kuadratnya, sedangkan selisih yang lebih besar dihitung sebagai nilai mutlaknya dikurangi 0,5, sehingga selisih yang sangat besar tidak mendominasi

*Loss* kelas adalah BCE bertemperatur antara target lunak *teacher* dan *logit* *student*, lalu dikalikan $T^{2}$ seperti pada Persamaan 2.2 (Persamaan 2.6).

> $L_{\text{kelas}} = - \frac{T^{2}}{M}\sum_{m = 1}^{M}\left\lbrack p_{m}\log{\sigma\left( \frac{z_{s,m}}{T} \right)} + \left( 1 - p_{m} \right)\log\left( 1 - \sigma\left( \frac{z_{s,m}}{T} \right) \right) \right\rbrack$ (2.6)

Keterangan:

> $L_{\text{kelas}}$ : *loss* kelas
>
> $p_{m}$ : target lunak *teacher* untuk elemen skor ke-$m$, yaitu $\sigma\left( \frac{z_{t,m}}{T} \right)$
>
> $z_{t,m}$, $z_{s,m}$ : *logit* *teacher* dan *student* pada elemen skor ke-$m$
>
> $M$ : jumlah seluruh elemen skor kelas dari semua titik prediksi; nilai *loss* adalah rata-rata atas semua elemen tersebut
>
> $m$ : nomor elemen skor, dari 1 sampai $M$
>
> $T$, $\sigma$ : temperatur seperti pada Persamaan 2.1 dan fungsi *sigmoid* seperti pada Persamaan 2.3
>
> log : logaritma natural

Suku pertama di dalam kurung siku menilai peluang suatu kelas ada, sedangkan suku kedua menilai peluang kelas itu tidak ada, karena detektor menilai setiap kelas secara terpisah.

KD murni menjumlahkan ketiga suku tanpa *loss* berlabel (Persamaan 2.7), sedangkan KD hibrida menambahkannya pada *loss* deteksi berlabel bawaan Ultralytics, $L_{\text{det}}$ (Persamaan 2.8). Pada implementasi, jumlah suku KD dikalikan ukuran *batch* agar sesuai dengan konvensi skala *loss* Ultralytics. Varian hibrida fitur memakai $L_{\text{det}}$ ditambah jumlah *loss* fitur yang dikalikan bobot dis, yaitu bentuk KD bawaan Ultralytics. Nilai bobot $\lambda$ dan temperatur $T$ dijelaskan pada Bab 3.

> $L_{\text{murni}} = \lambda_{f}\sum_{l = 3}^{5}L_{\text{fitur}}^{l} + \lambda_{b}L_{\text{kotak}} + \lambda_{c}L_{\text{kelas}}$ (2.7)
>
> $L_{\text{hibrida}} = L_{\text{det}} + L_{\text{murni}}$ (2.8)

Keterangan:

> $L_{\text{murni}}$, $L_{\text{hibrida}}$ : *loss* KD murni dan *loss* KD hibrida
>
> $L_{\text{fitur}}^{l}$ : *loss* fitur pada skala $l$ menurut Persamaan 2.4, dijumlahkan untuk $l = 3$ sampai 5, yaitu skala P3, P4, dan P5
>
> $L_{\text{kotak}}$, $L_{\text{kelas}}$ : *loss* kotak dan *loss* kelas menurut Persamaan 2.5 dan Persamaan 2.6
>
> $\lambda_{f}$, $\lambda_{b}$, $\lambda_{c}$ : bobot *loss* fitur, *loss* kotak, dan *loss* kelas
>
> $L_{\text{det}}$ : *loss* deteksi berlabel bawaan Ultralytics, yang membandingkan prediksi dengan label himpunan data melalui *loss* kotak, *loss* kelas, dan DFL (Lampiran A)

Penerapan ketiga suku distilasi tersebut dan *loss* berlabel pada penelitian ini digambarkan dalam diagram blok pada Gambar 5.8 di Subbab 5.1.2.2.

### 2.2.5 Robot Operating System 2

ROS 2 berbasis *Data Distribution Service* (DDS), yaitu standar terbuka untuk komunikasi (Macenski, et al., 2022). Program ROS 2 tersusun atas *node* dengan antarmuka *topic*, *service*, dan *action*. *Topic* adalah pertukaran pesan asinkron dengan arsitektur *publish-subscribe* anonim, dan perilaku pengirimannya diatur melalui pengaturan *Quality of Service* (QoS) (Macenski, et al., 2022).

Pengaturan QoS menentukan cara pesan dikirim. Pada pengaturan *reliability*, mode *best-effort* mengirim pesan satu kali dan cocok untuk data yang cepat digantikan data baru, seperti data sensor, sedangkan mode *reliable* terus mengirim pesan sampai penerima mengonfirmasi penerimaannya. Pengaturan *durability* menentukan apakah pesan dilupakan setelah dikirim (*volatile*) atau disimpan untuk *subscriber* yang bergabung belakangan (*transient-local*). Pengaturan *history* mengatur perilaku saat jaringan tidak mampu mengimbangi aliran data; mode *keep-last* yang umum dipakai menyimpan antrean berukuran tetap dan menimpa data terlama (Macenski, et al., 2022).

Cara *node* dijalankan juga memengaruhi kinerja komunikasi. Komunikasi antarproses paling fleksibel, tetapi menghasilkan latensi dan penggunaan CPU tertinggi. Komunikasi *intra-process* melewati tumpukan *middleware* dengan meneruskan *pointer* dari *publisher* ke *subscriber*, dan keuntungannya paling besar pada pesan berukuran sekitar 1 MB atau lebih yang umumnya berupa citra (Macenski, et al., 2022). Karena kamera dan *node* deteksi pada OP3 menerbitkan dan menerima citra melalui *topic*, pengaturan QoS dan cara *node* dijalankan ikut menentukan *frame* yang diproses ketika inferensi lebih lambat daripada laju kamera.

Latensi pada sistem ROS 2 multi-*node* dipengaruhi oleh lapisan ROS 2 dan *middleware* di antara publikasi pesan dan pemanggilan *callback* pada *subscriber* (Kronauer, et al., 2021). Karena itu, penelitian ini membedakan waktu pemrosesan model dari waktu yang dihabiskan sistem ROS 2.

### 2.2.6 Pelacakan Objek BoT-SORT

Pelacakan objek menjaga identitas setiap objek antar-*frame*. BoT-SORT adalah pelacak berbasis deteksi (*tracking-by-detection*) yang menggabungkan informasi gerak dan tampilan, kompensasi gerak kamera, serta vektor keadaan filter Kalman yang lebih akurat (Aharon, Orfaig, dan Bobrovsky, 2022). Dalam penelitian ini, BoT-SORT dijalankan pada *node* deteksi, tetapi akurasi pelacakan tidak termasuk metrik yang diuji.

### 2.2.7 Metrik Akurasi Deteksi

Setiap kotak hasil deteksi digolongkan sebagai *true positive* (TP) bila benar mendeteksi suatu kotak kebenaran, *false positive* (FP) bila mendeteksi objek yang tidak ada atau salah letak, dan *false negative* (FN) untuk kotak kebenaran yang tidak terdeteksi (Padilla, et al., 2021). Kebenaran letak ditentukan dengan IoU, yaitu perbandingan luas irisan dan luas gabungan kotak prediksi $B_{p}$ dan kotak kebenaran $B_{gt}$, seperti pada Persamaan 2.9 (Padilla, et al., 2021).

> $IoU = \frac{\text{luas}\left( B_{p} \cap B_{gt} \right)}{\text{luas}\left( B_{p} \cup B_{gt} \right)}$ (2.9)

Keterangan:

> IoU : nilai 0 sampai 1; bernilai 0 bila kedua kotak sama sekali tidak tumpang tindih dan bernilai 1 bila kedua kotak berimpit tepat
>
> $B_{p}$ : kotak hasil prediksi model
>
> $B_{gt}$ : kotak kebenaran (*ground truth*) dari label
>
> $\cap$, $\cup$ : irisan, yaitu daerah yang ditutupi kedua kotak sekaligus, dan gabungan, yaitu seluruh daerah yang ditutupi salah satu atau kedua kotak
>
> luas : luas daerah dalam satuan piksel persegi

IoU hanya dihitung antara kotak prediksi dan kotak kebenaran dari kelas yang sama. Ambang IoU yang mendekati 1 lebih ketat karena menuntut kotak yang hampir tepat, dan ambang yang paling sering dipakai adalah 50% dan 75%. *Precision* dan *recall* juga bergantung pada ambang *confidence*, karena hanya deteksi dengan *confidence* lebih besar daripada ambang tersebut yang dihitung sebagai deteksi positif (Padilla, et al., 2021).

Nilai *confidence* tidak selalu sebanding dengan peluang suatu prediksi benar. Guo, et al. (2017, pp. 1321-1322) mendapati bahwa jaringan saraf modern cenderung terlalu yakin, sehingga keyakinan prediksinya perlu dikalibrasi sebelum ditafsirkan sebagai peluang. Akibatnya, satu ambang *confidence* yang sama dapat meloloskan proporsi deteksi yang berbeda pada model yang berbeda. Karena itu, penelitian ini melaporkan AP, yang dihitung pada seluruh ambang *confidence*, bersama *precision* dan *recall* pada satu ambang tetap.

*Precision* dan *recall* dihitung dengan Persamaan 2.10 dan Persamaan 2.11 (Padilla, et al., 2021), sedangkan F1 adalah rata-rata harmonik keduanya, seperti pada Persamaan 2.12 (Ultralytics, n.d.c).

> $P = \frac{TP}{TP + FP}$ (2.10)
>
> $R = \frac{TP}{TP + FN}$ (2.11)
>
> $F1 = \frac{2 \cdot P \cdot R}{P + R}$ (2.12)

Keterangan:

> $P$ : *precision*, yaitu proporsi deteksi yang benar di antara seluruh deteksi
>
> $R$ : *recall*, yaitu proporsi objek pada label yang berhasil terdeteksi
>
> $F1$ : rata-rata harmonik *precision* dan *recall*; nilainya tinggi hanya bila keduanya tinggi
>
> $TP$, $FP$, $FN$ : jumlah TP, FP, dan FN seperti dijelaskan pada awal subbab ini

AP adalah luas daerah yang dibatasi kurva *precision* terhadap *recall*. Pasangan *precision* dan *recall* diurutkan menurut ambang *confidence*, *precision* diinterpolasi agar kurvanya monoton, lalu AP dihitung sebagai jumlah Riemann seperti pada Persamaan 2.13 (Padilla, et al., 2021).

> $AP = \sum_{k = 0}^{K}{\left( R_{r}(k) - R_{r}(k + 1) \right)P_{\text{interp}}\left( R_{r}(k) \right)}$ (2.13)

Keterangan:

> $AP$ : nilai AP untuk satu kelas
>
> $R_{r}(k)$ : nilai *recall* acuan ke-$k$
>
> $P_{\text{interp}}(R)$ : *precision* tertinggi pada *recall* yang lebih besar atau sama dengan $R$
>
> $k$, $K$ : nomor urut nilai *recall* acuan, dari 0 sampai $K$

Setiap suku penjumlahan adalah luas persegi panjang dengan lebar selisih dua nilai *recall* acuan yang berurutan dan tinggi *precision* terinterpolasi, sehingga jumlahnya mendekati luas daerah yang dibatasi kurva *precision* terhadap *recall*.

Jumlah Riemann pada Persamaan 2.13 dapat dihitung dengan interpolasi $N$ titik atau interpolasi semua titik. Interpolasi $N$ titik memakai nilai *recall* acuan yang berjarak sama pada selang 0 sampai 1, misalnya 101 titik pada kompetisi COCO dan 11 titik yang semula dipakai PASCAL VOC. Interpolasi semua titik memakai setiap nilai *recall* yang dihasilkan oleh seluruh ambang *confidence*, dan metode ini kemudian dipakai PASCAL VOC. Apa pun metode interpolasinya, AP dihitung untuk setiap kelas secara terpisah (Padilla, et al., 2021).

Nilai mAP adalah rata-rata AP atas $C$ kelas, seperti pada Persamaan 2.14 (Padilla, et al., 2021). mAP50 memakai ambang IoU 0,50, sedangkan mAP50‑95 merata-ratakan mAP pada ambang IoU 0,50 sampai 0,95 dengan selang 0,05. AP pada rentang ambang tersebut merupakan metrik utama himpunan data COCO (Lin, et al., 2014; COCO, n.d.; Ultralytics, n.d.c).

> $mAP = \frac{1}{C}\sum_{i = 1}^{C}{AP}_{i}$ (2.14)

Keterangan:

> $mAP$ : nilai mAP, yaitu rata-rata AP semua kelas
>
> $AP_{i}$ : nilai AP kelas ke-$i$ menurut Persamaan 2.13
>
> $C$ : jumlah kelas; pada penelitian ini $C = 3$, yaitu bola, gawang, dan robot

### 2.2.8 Metrik Kinerja *Runtime*

Waktu eksekusi pada komputer bersifat nondeterministik. Hoefler dan Belli (2015) menganjurkan agar hasil nondeterministik dilaporkan beserta selang kepercayaannya, dan agar data tidak diasumsikan berdistribusi normal tanpa pemeriksaan diagnostik. MLPerf memakai latensi persentil ke-90 sebagai metrik skenario *single-stream* (Reddi, et al., 2020).

Penelitian ini melaporkan rata-rata, median, dan persentil ke-95 latensi. Laju pemrosesan dinyatakan sebagai FPS efektif, yaitu jumlah selang antar-*frame* terproses dibagi rentang cap waktu kamera dalam jendela ukur (Persamaan 2.15). Penggunaan sumber daya dinyatakan dari penggunaan CPU dan memori proses detektor, dengan definisi operasional pada Bab 3.

> $FPS_{\text{efektif}} = \frac{N - 1}{t_{N} - t_{1}}$ (2.15)

Keterangan:

> $FPS_{\text{efektif}}$ : laju pemrosesan, dalam *frame* per detik
>
> $N$ : jumlah *frame* yang diproses dalam jendela ukur
>
> $t_{1}$, $t_{N}$ : cap waktu kamera, dalam detik, pada *frame* pertama dan *frame* terakhir
>
> $N - 1$ : jumlah selang antara dua *frame* yang berurutan

### 2.2.9 Variasi Antar-*Seed* dan Reproduksibilitas

Pelatihan dan inferensi dalam penelitian ini memakai PyTorch, pustaka pembelajaran mendalam dengan gaya pemrograman imperatif (Paszke, et al., 2019). Banyak langkah dalam pelatihan jaringan saraf memakai bilangan acak yang dihasilkan oleh pembangkit bilangan acak semu. *Seed* adalah nilai awal yang diberikan kepada pembangkit tersebut. Dengan *seed* yang sama, pembangkit menghasilkan deret bilangan yang sama sehingga langkah yang bergantung pada bilangan acak dapat diulang. PyTorch menyediakan fungsi manual_seed untuk menetapkan *seed* pada CPU dan GPU, sedangkan pustaka yang memiliki pembangkit sendiri, seperti NumPy, perlu diberi *seed* secara terpisah (PyTorch, 2026). Pada Ultralytics, argumen *seed* menetapkan *seed* pelatihan agar hasilnya dapat diulang pada konfigurasi yang sama, argumen *deterministic* memaksa pemakaian algoritme deterministik, dan pelatihan dengan argumen *pretrained* bernilai *false* dimulai dari bobot yang diinisialisasi secara acak (Ultralytics, n.d.b).

Hasil pelatihan jaringan saraf bervariasi menurut sumber keacakannya. Bouthillier, et al. (2021, pp. 1-3) menunjukkan bahwa variasi akibat pengambilan sampel data, inisialisasi parameter, dan pilihan hiperparameter dapat mengubah kesimpulan *benchmark*. Sumber variasi pada prosedur pelatihan dikelompokkan menjadi pengambilan sampel data, augmentasi data, inisialisasi model, *dropout*, dan urutan kunjungan data pada *stochastic gradient descent*. Picard (2021, pp. 1-2) memperlakukan variasi hasil antar-*seed* sebagai akumulasi seluruh faktor acak yang bergantung pada *seed*. Hasilnya menunjukkan bahwa walaupun variansnya tidak terlalu besar, *seed* yang menghasilkan nilai jauh di atas atau jauh di bawah rata-rata mudah ditemukan. Dokumentasi PyTorch versi 2.14 juga menyatakan bahwa hasil yang sepenuhnya dapat diulang tidak dijamin lintas versi PyTorch, *commit*, atau perangkat yang berbeda (PyTorch, 2026). Karena itu, model *supervised*, KD murni, dan varian KD hibrida terpilih dalam penelitian ini dilatih dengan tiga *seed* dan dilaporkan dengan rata-rata serta simpangan baku (Subbab 3.2.5).
