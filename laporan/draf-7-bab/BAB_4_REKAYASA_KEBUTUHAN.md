# BAB 4 REKAYASA KEBUTUHAN

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v34 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

Bab ini menjabarkan kebutuhan sistem deteksi objek pada ROBOTIS OP3 yang menjadi acuan perancangan pada Bab 5 dan pengujian pada Bab 6. Kebutuhan disusun dari rumusan masalah, keterbatasan komputer *onboard* OP3, dan antarmuka ROS 2 yang dipakai robot.

## 4.1 Kajian Masalah

Robot humanoid sepak bola memerlukan informasi letak bola, gawang, dan robot lain dari kamera di tubuhnya sendiri (Fiedler, et al., 2019). Pada unit OP3 yang digunakan, seluruh pemrosesan citra dijalankan pada CPU Intel Core i5-1240P di komputer *onboard* yang juga menjalankan *gait* robot, tanpa GPU atau akselerator lain (Subbab 1.5). Lau dan Pottier (2026) hanya memperoleh 4 sampai 8 FPS untuk YOLOv9 pada OP3 bahkan setelah model dikonversi dan dikuantisasi, sehingga ukuran model menjadi batas utama bagi detektor berbasis jaringan saraf pada robot ini.

Masalah yang dihadapi adalah memperoleh detektor kecil yang akurasinya tetap layak untuk tiga kelas dan dapat berjalan sebagai *node* ROS 2 pada CPU tersebut. Penelitian ini memakai *student* YOLO11 skala t dengan 810.649 parameter, yaitu sekitar 31% dari 2.590.425 parameter *teacher* YOLO11n, lalu melatihnya dengan KD. Karena arsitektur *student* sama untuk semua varian, biaya inferensinya tidak ditentukan oleh fungsi objektif pelatihan; yang diharapkan berubah melalui KD adalah mutu deteksinya.

Sistem juga harus dapat diukur. Rumusan masalah nomor 3 dan 4 menuntut data latensi, FPS, penggunaan CPU, dan RAM pada kondisi robot diam dan berjalan, sehingga *node* deteksi wajib mencatat waktu setiap tahap pemrosesan dan penggunaan sumber daya prosesnya pada setiap *frame*. *Node* deteksi tidak mengendalikan gerak robot; gerak diatur terpisah oleh op3_manager.

## 4.2 Identifikasi *Stakeholder*

Pemangku kepentingan (*stakeholder*) adalah pihak yang memanfaatkan atau berkepentingan dengan hasil sistem, sedangkan aktor adalah pihak atau komponen yang berinteraksi langsung dengan sistem saat dijalankan. Keduanya disajikan pada Tabel 4.1.

**Tabel 4.1** Pemangku kepentingan dan aktor sistem

| **Nama**                     | **Jenis**                      | **Peran atau kepentingan**                                                                                                                              |
|------------------------------|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| Tim ROBOTIIK Divisi Humanoid | Pemangku kepentingan           | Memakai hasil deteksi bola, gawang, dan robot serta data kinerja sebagai dasar pemilihan model untuk OP3                                                |
| Peneliti                     | Pemangku kepentingan dan aktor | Melatih model, bertindak sebagai operator saat pengujian, dan menganalisis hasil                                                                        |
| Operator robot               | Aktor                          | Menata objek uji, menyalakan robot dan kamera, menjalankan *node* deteksi dengan parameter yang ditetapkan, serta menetapkan kondisi diam atau berjalan |
| *Node* kamera USB            | Aktor (sistem eksternal)       | Melakukan *publish* citra kamera Logitech C920 pada *topic* ROS 2                                                                                       |
| op3_manager                  | Aktor (sistem eksternal)       | Menjalankan *gait* pada kondisi berjalan                                                                                                                |
| Penampil *preview*           | Aktor (sistem eksternal)       | Menampilkan citra beranotasi di laptop melalui SSH                                                                                                      |

## 4.3 Kebutuhan Fungsional Sistem

Kebutuhan fungsional adalah kebutuhan yang berkaitan dengan perilaku sistem, yaitu fungsi, data, masukan, dan reaksi sistem terhadap masukan, sedangkan kebutuhan nonfungsional adalah atribut atau batasan pada sistem (Glinz, 2007). Kebutuhan fungsional pada penelitian ini disusun agar sistem yang diimplementasikan dapat diverifikasi sebelum pengujian akurasi dan *runtime*. Setiap kebutuhan diberi kode, rumusan, dan indikator verifikasi agar dapat ditelusuri sampai skenario pengujiannya pada Subbab 6.1. Daftar kebutuhan fungsional disajikan pada Tabel 4.2.

**Tabel 4.2** Kebutuhan fungsional

| **Kode** | **Kebutuhan**                                                                              | **Indikator verifikasi**                                                                             |
|----------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| KF-01    | Sistem menerima citra kamera OP3 melalui *topic* ROS 2 dan memproses *frame* yang diterima | *Frame* masuk diproses dan *error frame* tercatat pada *log*                                         |
| KF-02    | Sistem mendeteksi bola, gawang, dan robot                                                  | Keluaran memuat kelas dan kotak pembatas; ketepatannya terhadap label dinilai pada pengujian akurasi |
| KF-03    | Sistem menyediakan ID pelacakan pada mode pelacakan                                        | ID tersedia pada keluaran dan kestabilannya diperiksa pada objek bergerak                            |
| KF-04    | Sistem mencatat data *runtime* setiap *frame*                                              | *Timestamp*, durasi tahap, CPU, RSS, dan *error* tersedia pada berkas CSV                            |
| KF-05    | Sistem menampilkan *preview* hasil deteksi                                                 | Kotak dan kelas tampak pada *preview*                                                                |

## 4.4 Spesifikasi Sistem

Spesifikasi sistem menjelaskan persyaratan nonfungsional yang harus dipenuhi agar kebutuhan fungsional dapat berjalan pada robot. Penelitian ini menetapkan satu kebutuhan nonfungsional yang diuji, yaitu laju pemrosesan, seperti pada Tabel 4.3. Batasan waktu dan kecepatan pemrosesan termasuk kebutuhan kinerja, yang oleh Glinz (2007) digolongkan sebagai salah satu atribut sistem. Nilai 8 FPS diambil dari batas atas rentang 4 sampai 8 FPS yang dinilai Lau dan Pottier (2026) memadai untuk tugas navigasi dan interaksi objek pada robot humanoid. Kriteria ini berlaku untuk FPS efektif rata-rata setiap *run*, bukan untuk setiap selang waktu pendek di dalam *run*.

**Tabel 4.3** Kebutuhan nonfungsional

| **Kode** | **Kebutuhan**                                              | **Kriteria**                                                                                             |
|----------|------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| KNF-01   | Laju pemrosesan *node* deteksi pada komputer *onboard* OP3 | FPS efektif rata-rata setiap *run*, menurut Persamaan 2.15, minimal 8 FPS pada kondisi diam dan berjalan |

Selain KNF-01, sistem dirancang dengan spesifikasi berikut agar kebutuhan fungsional dapat dipenuhi pada perangkat OP3.

1.  Karena komputer *onboard* OP3 tidak memiliki GPU diskret, inferensi dijalankan pada CPU dalam presisi FP32. *Node* deteksi menetapkan 4 *thread* operasi dan 2 *thread* antaroperasi PyTorch saat inisialisasi dengan nilai yang sama untuk semua model.

2.  Karena citra kamera cepat digantikan citra baru, *node* deteksi melakukan *subscribe* citra dengan QoS *best-effort* dan *keep-last* dengan *depth* 1, sehingga *frame* lama dilewati bila inferensi tertinggal.

3.  Karena CPU yang sama juga menjalankan *gait*, *node* deteksi hanya membaca citra dan melakukan *publish* hasil, tanpa mengirim perintah ke *servo*.

4.  Karena robot dioperasikan dari laptop, komputer *onboard* diakses melalui SSH dan *preview* ditampilkan di laptop tanpa pemrosesan deteksi di laptop.

5.  Karena model dipindahkan dari server ke robot sebagai berkas, *node* deteksi memeriksa SHA-256 *checkpoint* dan pemetaan kelas sebelum inferensi dimulai.

## 4.5 Analisis Kebutuhan Perangkat Keras dan Perangkat Lunak

Analisis kebutuhan perangkat keras dan perangkat lunak menjelaskan komponen yang dibutuhkan untuk melatih model di server, menjalankan model pada robot, dan mengoperasikan pengujian.

### 4.5.1 Kebutuhan Perangkat Keras

Rangkuman kebutuhan perangkat keras disajikan pada Tabel 4.4. Setiap komponen kemudian diuraikan pada subbab berikutnya.

**Tabel 4.4** Kebutuhan perangkat keras

| **Perangkat**                                           | **Kebutuhan yang dipenuhi**                                                     |
|---------------------------------------------------------|---------------------------------------------------------------------------------|
| Robot ROBOTIS OP3                                       | Platform robot humanoid yang membawa kamera, komputer *onboard*, dan aktuator   |
| Komputer *onboard* Intel NUC dengan Intel Core i5-1240P | Menjalankan inferensi pada CPU sekaligus *gait* robot                           |
| Antarmuka U2D2                                          | Menghubungkan komputer *onboard* dengan OpenCR pada bus DYNAMIXEL               |
| *Sub-controller* OpenCR 1.0                             | Meneruskan perintah sendi ke aktuator                                           |
| 20 aktuator DYNAMIXEL XM430-W350-R                      | Menggerakkan sendi robot pada kondisi berjalan                                  |
| Kamera Logitech C920                                    | Sumber citra berukuran 640 × 480 piksel bagi *node* deteksi                     |
| Baterai LiPo empat sel 14,8 V                           | Sumber daya robot saat beroperasi tanpa kabel; tidak digunakan selama pengujian |
| Adaptor 12 V dan adaptor 19 V                           | Catu daya OpenCR dan komputer *onboard* selama pengujian                        |
| Tatakan robot                                           | Menopang badan OP3 selama *gait* di tempat untuk mengurangi beban *servo*       |
| Server laboratorium dengan GPU NVIDIA L40               | Pelatihan dan evaluasi model pada VAL dan TEST                                  |
| Laptop                                                  | Akses SSH ke OP3, penampil *preview*, dan analisis data                         |

#### 4.5.1.1 Robot ROBOTIS OP3

ROBOTIS OP3 adalah robot humanoid dengan 20 derajat kebebasan yang digerakkan aktuator DYNAMIXEL XM430-W350-R, dengan komputer Intel NUC sebagai pengendali utama dan OpenCR sebagai *sub-controller* (ROBOTIS, n.d.a). Spesifikasi bawaan OP3 disajikan pada Tabel 4.5. Pengendali utama pada unit yang dipakai dalam penelitian ini berbeda dari spesifikasi bawaan, yaitu Intel NUC12WSHi5 dengan prosesor Intel Core i5-1240P. Seri ini terbaca dari nama host humanoid-NUC12WSHi5 pada *snapshot* sistem 22 Oktober 2026 (Tabel 3.1).

**Tabel 4.5** Spesifikasi bawaan ROBOTIS OP3

| **Komponen**      | **Spesifikasi**                                                                 |
|-------------------|---------------------------------------------------------------------------------|
| Tinggi            | Sekitar 510 mm                                                                  |
| Berat             | Sekitar 3,5 kg tanpa penutup badan                                              |
| Derajat kebebasan | 20                                                                              |
| Aktuator          | DYNAMIXEL XM430-W350-R                                                          |
| Pengendali utama  | Intel NUC dengan prosesor Intel Core i3 dua inti, RAM DDR4 8 GB, SSD M.2 250 GB |
| *Sub-controller*  | OpenCR                                                                          |
| Kamera            | Logitech C920 HD Pro Webcam                                                     |
| Sensor            | Giroskop tiga sumbu, akselerometer tiga sumbu, dan magnetometer tiga sumbu      |
| Baterai           | LiPo tiga sel 11,1 V 3.300 mAh                                                  |

Sumber: ROBOTIS (n.d.a)

Letak 20 aktuator beserta nomor ID-nya disajikan pada Gambar 4.1. Aktuator ID 19 dan 20 berada pada leher dan kepala robot, tempat kamera dipasang.

**Gambar 4.1** Kerangka robot OP3 dan letak ID aktuator XM430-W350-R

Sumber: ROBOTIS (2018, dikutip dalam Brilliant, 2024)

#### 4.5.1.2 Komputer *Onboard* Intel NUC

Komputer *onboard* menjalankan Ubuntu, ROS 2, *node* deteksi, dan op3_manager. Prosesornya adalah Intel Core i5-1240P dengan spesifikasi pada Tabel 4.6 (Intel Corporation, n.d.). Prosesor ini memiliki grafis terintegrasi, tetapi penelitian ini menjalankan inferensi pada CPU melalui PyTorch. Memori yang terbaca oleh sistem operasi pada unit yang dipakai adalah 7,33 GiB dengan sistem operasi Ubuntu 24.04.5 LTS (Tabel 3.1). Pada *snapshot* sistem 22 Oktober 2026, *governor* CPU berada pada mode powersave dengan intel_pstate aktif dan *turbo* diizinkan. *Snapshot* ini menggambarkan kondisi perangkat, tetapi tidak membuktikan bahwa pengaturan tersebut tetap sama sepanjang seluruh sesi pengujian. Karena *gait* dan *node* deteksi berbagi prosesor yang sama, ukuran model menentukan sisa kapasitas CPU bagi proses lain pada robot.

**Tabel 4.6** Spesifikasi prosesor Intel Core i5-1240P

| **Komponen**             | **Spesifikasi**                                  |
|--------------------------|--------------------------------------------------|
| Jumlah inti              | 12 (4 *Performance-core* dan 8 *Efficient-core*) |
| Jumlah *thread*          | 16                                               |
| Frekuensi turbo maksimum | 4,40 GHz                                         |
| *Cache*                  | 12 MB Intel Smart Cache                          |
| Daya dasar prosesor      | 28 W                                             |
| Grafis terintegrasi      | Intel Iris Xe Graphics                           |

Sumber: Intel Corporation (n.d.)

#### 4.5.1.3 OpenCR 1.0

OpenCR 1.0 adalah *sub-controller* yang meneruskan perintah sendi dari komputer *onboard* ke aktuator melalui *port* DYNAMIXEL (ROBOTIS, n.d.c). Spesifikasinya disajikan pada Tabel 4.7. Pada penelitian ini, OpenCR hanya digunakan op3_manager untuk menjalankan *gait*; *node* deteksi tidak berkomunikasi dengan OpenCR. Pada unit yang dipakai, komputer *onboard* berkomunikasi dengan OpenCR, yang memiliki ID 200 pada bus DYNAMIXEL, melalui U2D2. U2D2 adalah pengubah USB yang memungkinkan komputer berkomunikasi dengan perangkat DYNAMIXEL melalui antarmuka TTL (*transistor-transistor logic*) atau RS-485 (ROBOTIS, n.d.d). Pemeriksaan awal pada 19 Oktober 2026 membaca tegangan masuk OpenCR sebesar 12,7 V. Daya bus aktuator diatur oleh register dynamixel_power pada OpenCR, sehingga aktuator baru merespons setelah daya bus diaktifkan.

**Tabel 4.7** Spesifikasi OpenCR 1.0

| **Komponen**      | **Spesifikasi**                                                                           |
|-------------------|-------------------------------------------------------------------------------------------|
| Mikrokontroler    | STM32F746ZGT6, ARM Cortex-M7 32 bit dengan FPU, 216 MHz                                   |
| Sensor            | Giroskop tiga sumbu, akselerometer tiga sumbu, dan *digital motion processor* (ICM-20648) |
| Port komunikasi   | 1 USB Micro-B, 3 TTL dan 3 RS-485 untuk DYNAMIXEL, 2 UART, 1 CAN                          |
| Masukan daya      | 5 V melalui USB atau 5 sampai 24 V dari baterai atau catu daya                            |
| Dimensi dan berat | 105 mm × 75 mm, 60 g                                                                      |

Sumber: ROBOTIS (n.d.c)

#### 4.5.1.4 *Servo* DYNAMIXEL XM430-W350-R

OP3 menggunakan 20 aktuator DYNAMIXEL XM430-W350-R dengan spesifikasi pada Tabel 4.8 (ROBOTIS, n.d.b). Akhiran R menunjukkan antarmuka RS-485. Aktuator kepala, yaitu ID 19 dan 20 pada Gambar 4.1, menentukan arah kamera, sehingga resolusi *encoder* juga menentukan kepekaan pemeriksaan posisi kepala pada pengujian kondisi berjalan: dengan 4.096 pulsa per putaran, batas pergeseran dua *count* setara dengan sekitar 0,18 derajat.

**Tabel 4.8** Spesifikasi DYNAMIXEL XM430-W350-R

| **Komponen**          | **Spesifikasi**                          |
|-----------------------|------------------------------------------|
| Mikrokontroler        | ARM Cortex-M3, 72 MHz, 32 bit            |
| Sensor posisi         | *Encoder* absolut nirsentuh 12 bit, 360° |
| Resolusi              | 4.096 pulsa per putaran                  |
| Rasio roda gigi       | 353,5 : 1                                |
| Torsi henti           | 4,1 N·m pada 12,0 V dan 2,3 A            |
| Kecepatan tanpa beban | 46 rpm pada 12,0 V                       |
| Tegangan masukan      | 10,0 sampai 14,8 V (disarankan 12,0 V)   |
| Koneksi fisik         | Bus *multidrop* RS-485 atau TTL          |
| Berat                 | 82 g                                     |

Sumber: ROBOTIS (n.d.b)

#### 4.5.1.5 Kamera Logitech C920

Kamera Logitech C920 adalah kamera bawaan OP3 (ROBOTIS, n.d.a). Kamera ini mendukung resolusi 1920 × 1080 piksel pada 30 fps, memiliki fokus otomatis, dan bidang pandang diagonal 78 derajat (Logitech, n.d.). Pada penelitian ini, kamera diminta mengirim citra 640 × 480 piksel berformat YUYV pada 30 FPS, lalu *node* kamera melakukan *publish* citra tersebut sebagai pesan ROS 2 berpengodean rgb8 pada /thesis/image_raw. Nilai 30 FPS adalah permintaan konfigurasi, bukan laju yang terukur. Citra kemudian disesuaikan ke sisi panjang 640 dengan *letterbox* tanpa mengubah rasio aspeknya. Bentuk kamera disajikan pada Gambar 4.2.

**Gambar 4.2** Kamera Logitech C920

Sumber: Logitech (dikutip dalam Brilliant, 2024)

#### 4.5.1.6 Catu Daya

Spesifikasi bawaan OP3 memakai baterai LiPo tiga sel 11,1 V 3.300 mAh (ROBOTIS, n.d.a). Unit yang dipakai dalam penelitian ini terpasang baterai LiPo empat sel 14,8 V 2.200 mAh, sesuai label pada baterai (Gambar 4.3a). Selama pengujian pada robot, baterai tersebut tidak digunakan. OpenCR dicatu adaptor 12 V (Gambar 4.3b) dan komputer *onboard* dicatu adaptor 19 V (Gambar 4.3c), sehingga kedua bagian memiliki sumber daya terpisah. Pemeriksaan awal pada 19 Oktober 2026 membaca tegangan masuk OpenCR sebesar 12,7 V.

**Gambar 4.3** Baterai LiPo dan adaptor catu daya

#### 4.5.1.7 Tatakan Robot

Tatakan robot menopang badan OP3 selama *gait* di tempat sehingga kaki tidak menanggung seluruh berat badan. Tatakan dipakai untuk mengurangi beban *servo* selama pengujian berulang dan menjaga posisi kamera terhadap objek uji tetap sama di antara *run*.

#### 4.5.1.8 Server Laboratorium dan Laptop

Server laboratorium dibutuhkan karena pelatihan model memerlukan GPU. Server berupa mesin virtual KVM labkc-l40-debian dengan Debian 12, AMD EPYC 7413 80 CPU virtual, RAM 283 GiB, dan tiga GPU NVIDIA L40 bermemori 46.068 MiB dengan *driver* NVIDIA 535.261.03 (Tabel 3.1). Spesifikasi ini dicatat pada 16 November 2026, sesudah seluruh pelatihan dan pengujian TEST selesai. Setiap *run* pelatihan memakai satu GPU, dan *manifest* setiap *run*, termasuk *run* ablasi ukuran *teacher* yang dijalankan dengan akun server yang berbeda, mencatat GPU NVIDIA L40, Python 3.11.2, PyTorch 2.4.1+cu121, dan Ultralytics 8.4.130. Pemeriksaan jalur evaluasi TEST dijalankan pada CPU server yang sama.

Laptop dibutuhkan sebagai terminal untuk mengakses robot dan server, menampilkan *preview*, dan menganalisis data.

### 4.5.2 Kebutuhan Perangkat Lunak

Kebutuhan perangkat lunak ditentukan oleh fungsi yang harus dijalankan pada setiap subsistem. Versi yang dipakai telah disajikan pada Tabel 3.2; Tabel 4.9 menjelaskan alasan setiap perangkat lunak dibutuhkan.

**Tabel 4.9** Kebutuhan perangkat lunak

| **Perangkat lunak**                      | **Kebutuhan yang dipenuhi**                                                                           |
|------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Ubuntu 24.04 dan ROS 2 Jazzy             | Sistem operasi dan komunikasi *topic* antara kamera, *node* deteksi, dan penampil pada OP3            |
| Python, PyTorch, dan Ultralytics 8.4.130 | Menjalankan berkas .pt FP32 yang sama dengan hasil pelatihan, termasuk *letterbox*, NMS, dan BoT-SORT |
| OpenCV dan cv_bridge                     | Mengubah pesan citra ROS 2 menjadi larik citra masukan model                                          |
| vision_msgs                              | Format pesan Detection2DArray untuk hasil deteksi (KF-02)                                             |
| lap 0.5.12                               | Asosiasi deteksi lintas *frame* pada BoT-SORT (KF-03)                                                 |
| psutil                                   | Pengukuran penggunaan CPU dan RSS proses detektor (KF-04)                                             |
| op3_manager                              | Menjalankan *gait* pada kondisi berjalan                                                              |
