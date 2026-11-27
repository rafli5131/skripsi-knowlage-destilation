# BAB 5 PERANCANGAN DAN IMPLEMENTASI

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v34 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

Bab ini menjelaskan rancangan perangkat keras dan perangkat lunak yang memenuhi kebutuhan pada Bab 4, lalu implementasinya pada server laboratorium dan pada robot. Bagian perancangan disusun dari gambaran umum sistem, perangkat keras, lalu perangkat lunak. Bagian implementasi mengikuti urutan yang sama dan disertai potongan kode program yang paling menentukan perilaku sistem.

## 5.1 Perancangan Sistem

Sistem tersusun atas masukan, proses, dan keluaran seperti pada Gambar 5.1. Masukan berupa citra kamera Logitech C920. Proses berlangsung pada komputer *onboard* Intel NUC, yaitu *node* deteksi yang menjalankan model YOLO11 pada CPU dan op3_manager yang menjalankan *gait*. Keluaran berupa hasil deteksi, *preview* beranotasi, dan *log* setiap *frame*. Model yang dijalankan *node* deteksi dihasilkan lebih dahulu oleh subsistem pelatihan di server laboratorium.

**Gambar 5.1** Diagram blok sistem deteksi objek pada OP3

### 5.1.1 Perancangan Perangkat Keras

Perangkat keras dibagi menjadi dua kelompok, yaitu perangkat pada robot yang menjalankan inferensi dan perangkat di laboratorium yang menjalankan pelatihan. Kedua kelompok tidak terhubung selama pengujian; model berpindah dari server ke robot sebagai berkas *checkpoint* yang *hash*-nya diperiksa.

#### 5.1.1.1 Desain Robot Humanoid

Robot yang digunakan adalah ROBOTIS OP3 dengan tinggi sekitar 510 mm, berat sekitar 3,5 kg, dan 20 derajat kebebasan (ROBOTIS, n.d.a). Kamera Logitech C920 berada di kepala robot, sehingga arah pandang kamera mengikuti posisi aktuator kepala dan ikut bergoyang ketika robot menjalankan *gait*. Desain robot ditunjukkan pada Gambar 5.2. Penelitian ini tidak mengubah struktur mekanik robot.

**Gambar 5.2** Desain robot humanoid ROBOTIS OP3

Sumber: Brilliant (2024)

Dimensi robot dari beberapa sisi disajikan pada Gambar 5.3. Tinggi keseluruhan robot sekitar 51 cm dengan panjang kaki sekitar 33 cm, sedangkan bagian badan memiliki tinggi sekitar 9,5 cm dan lebar sekitar 11,7 cm (Brilliant, 2024).

**Gambar 5.3** Dimensi robot ROBOTIS OP3 dari delapan sisi

Sumber: Brilliant (2024)

#### 5.1.1.2 Koneksi Antarkomponen

Koneksi antarkomponen robot disajikan pada Gambar 5.4. Komputer *onboard* sebagai pengendali utama terhubung ke U2D2 melalui USB, U2D2 terhubung ke OpenCR melalui RS-485, dan setiap aktuator terhubung ke OpenCR melalui jalur RS-485 (Brilliant, 2024). Penyambungan fisik OpenCR dan komputer *onboard* disajikan pada Gambar 5.5. Gambar 5.4 menggambarkan susunan bawaan robot dengan baterai LiPo sebagai sumber daya.

**Gambar 5.4** Koneksi antarkomponen robot humanoid

Sumber: Brilliant (2024)

**Gambar 5.5** Penyambungan OpenCR dan Intel NUC

Sumber: Brilliant (2024)

Konfigurasi perangkat keras saat pengujian disajikan pada Gambar 5.6. Kamera terhubung ke komputer *onboard* melalui USB dan menjadi satu-satunya sensor yang dipakai *node* deteksi. Komputer *onboard* mengirim perintah sendi ke *sub-controller* OpenCR, yang kemudian menggerakkan 20 aktuator DYNAMIXEL XM430-W350-R melalui bus RS-485 (ROBOTIS, n.d.a; ROBOTIS, n.d.c). Komputer *onboard* terhubung ke OpenCR melalui U2D2, pengubah USB untuk bus DYNAMIXEL (ROBOTIS, n.d.d). Selama pengujian, OpenCR dicatu adaptor 12 V dan komputer *onboard* dicatu adaptor 19 V, sedangkan baterai LiPo tidak dipakai. Laptop terhubung ke komputer *onboard* dan ke server melalui SSH, sedangkan model berpindah dari server ke robot sebagai berkas.

**Gambar 5.6** Konfigurasi perangkat keras saat pengujian

#### 5.1.1.3 Tata Letak Pengujian

Pada kondisi berjalan, badan OP3 ditopang tatakan robot sehingga kaki dapat menjalankan *gait* di tempat tanpa menanggung seluruh berat badan. Rancangan ini mengurangi beban *servo* selama pengujian berulang dan menjaga posisi kamera terhadap objek uji tetap sama di antara *run*. Bola, gawang, dan robot lain ditempatkan statis pada posisi bertanda di depan kamera. Tata letak tersebut ditunjukkan pada Gambar 5.7. Gambar ini merupakan ilustrasi tampak atas yang tidak berskala, dengan susunan objek mengikuti dokumentasi pengujian pada Gambar 5.16. Kamera diarahkan ke tiang kiri gawang sehingga tiang tersebut berada di tengah *field of view* dan gawang hanya terlihat sebagian. Bola berada di sisi kiri *field of view*, sedangkan robot lain berada di sisi kanan.

**Gambar 5.7** Tata letak pengujian pada robot

#### 5.1.1.4 Perangkat Pelatihan dan Pengoperasian

Pelatihan dan evaluasi model dijalankan pada server laboratorium dengan GPU NVIDIA L40 (Tabel 3.1). Laptop hanya berperan sebagai terminal: laptop terhubung ke komputer *onboard* melalui SSH untuk menjalankan perintah dan menampilkan *preview*, serta terhubung ke server untuk menjalankan pelatihan. Tidak ada pemrosesan deteksi yang dijalankan di laptop selama pengujian pada robot.

### 5.1.2 Perancangan Perangkat Lunak

Perangkat lunak terdiri atas lima rancangan, yaitu model *student*, pelatihan KD, *node* deteksi, komunikasi ROS 2, dan data *log*. Dua rancangan pertama berjalan di server, sedangkan tiga rancangan terakhir berjalan di komputer *onboard*.

#### 5.1.2.1 Perancangan Model *Student*

*Student* dirancang dengan topologi yang sama dengan *teacher* YOLO11n, yaitu *backbone*, *neck*, dan *head* Detect pada tiga skala keluaran P3, P4, dan P5. Perbedaannya hanya pada faktor lebar: lebar kanal *student* separuh lebar *teacher*, sedangkan kedalamannya sama. Karena topologinya sama, setiap peta fitur *student* memiliki pasangan pada *teacher* dengan resolusi spasial yang sama, sehingga distilasi fitur hanya membutuhkan *channel projector* dan tidak membutuhkan penyelarasan resolusi.

#### 5.1.2.2 Perancangan Pelatihan KD

Mekanisme satu langkah pelatihan KD hibrida penuh disajikan dalam diagram blok pada Gambar 5.8. Setiap *batch* citra TRAIN diteruskan ke *teacher* dan *student*. *Teacher* YOLO11n FP32 dibekukan dan dijalankan tanpa perhitungan gradien, sehingga keluarannya hanya menjadi acuan. Fitur *neck* *student* pada skala P3, P4, dan P5 diproyeksikan ke jumlah kanal *teacher* melalui *projector*, lalu dibandingkan dengan fitur *teacher* menggunakan *loss* L2 berbobot (Persamaan 2.4). Bobot setiap titik diambil dari skor kelas *teacher* (Persamaan 2.3). Keluaran kotak dan *logit* kelas *student* dibandingkan dengan keluaran *teacher* melalui *loss* kotak (Persamaan 2.5) dan *loss* kelas bertemperatur (Persamaan 2.6). Ketiga suku dijumlahkan menjadi *loss* KD murni (Persamaan 2.7), lalu ditambah *loss* deteksi berlabel sehingga menjadi *loss* KD hibrida (Persamaan 2.8). Propagasi balik memperbarui bobot *student* dan *projector*, sedangkan bobot *teacher* tidak berubah.

**Gambar 5.8** Diagram blok satu langkah pelatihan KD hibrida penuh

Varian lain memakai sebagian blok pada Gambar 5.8. *Supervised* hanya memakai *loss* deteksi berlabel, KD murni menggunakan *loss* KD murni tanpa *loss* berlabel, dan KD hibrida fitur memakai *loss* berlabel dengan distilasi fitur bawaan Ultralytics, seperti pada Tabel 3.3.

Urutan pelatihan dan pemilihan model di server laboratorium disajikan pada Gambar 5.9. *Student* YOLO11 skala t diinisialisasi acak, dan seluruh varian *student* dilatih dengan pengaturan yang sama. Varian, *seed*, dan *checkpoint* hasil KD dipilih hanya pada VAL dengan aturan seleksi yang ditetapkan sebelum pelatihan, sedangkan *checkpoint* *supervised* mengikuti *seed* KD hibrida terpilih. Berkas konfigurasi data untuk pelatihan tidak memuat entri TEST, sehingga TEST tidak dapat terbaca selama pelatihan. Sidik jari SHA-256 setiap citra dan label diperiksa sebelum pelatihan dan sebelum evaluasi agar himpunan data yang digunakan dapat dipastikan sama.

**Gambar 5.9** Diagram alir pelatihan dan seleksi model

#### 5.1.2.3 Perancangan *Node* Deteksi

*Node* deteksi dirancang sebagai satu proses Python yang menerima citra, menjalankan model, melakukan *publish* hasil, dan mencatat *log*, dengan alur pada Gambar 5.10. Saat mulai, *node* memeriksa SHA-256 *checkpoint* terhadap daftar model tepercaya (*model registry*) dan memastikan urutan kelas tetap 0 untuk bola, 1 untuk gawang, dan 2 untuk robot. Setiap *callback* memproses satu *frame*: citra diubah ke format OpenCV, diproses Ultralytics dengan *letterbox* 640, NMS, dan asosiasi BoT-SORT, lalu hasilnya di-*publish* dan dicatat. *Frame* awal sebanyak jumlah *warm-up* ditandai dan tidak dihitung dalam FPS efektif.

**Gambar 5.10** Diagram alir *node* deteksi

#### 5.1.2.4 Perancangan Komunikasi ROS 2

Komunikasi antarkomponen memakai *topic* ROS 2 seperti pada Gambar 5.11. *Node* kamera melakukan *publish* citra pada /thesis/image_raw, *node* deteksi melakukan *publish* hasil pada /vision/detections dan *preview* pada /vision/debug_image, sedangkan skrip pengujian kondisi berjalan mengirim perintah mulai dan berhenti ke /robotis/walking/command. *Node* deteksi melakukan *subscribe* citra dengan QoS *best-effort*, *keep-last* dengan *depth* 1, dan *callback* serial. Pengaturan ini sesuai untuk data sensor yang cepat digantikan data baru (Macenski, et al., 2022): bila inferensi tertinggal, *frame* lama dilewati alih-alih ditumpuk.

**Gambar 5.11** Komunikasi *topic* ROS 2 pada sistem

#### 5.1.2.5 Perancangan Data *Log*

Setiap peluncuran *node* menghasilkan berkas *metadata* JSON dan berkas CSV per *frame*. *Metadata* mencatat konfigurasi aktual, *hash* *checkpoint*, pemetaan kelas, versi perangkat lunak, jumlah *thread* PyTorch aktual, kondisi uji, dan alasan sesi berhenti. Kolom CSV per *frame* disajikan pada Tabel 5.1. Data ini menjadi sumber pengujian KF-01, KF-04, KNF-01, dan pengujian *runtime*.

**Tabel 5.1** Kolom berkas CSV per *frame*

| **Kolom**                                                 | **Isi**                                              |
|-----------------------------------------------------------|------------------------------------------------------|
| capture_stamp_ns, receive_time_utc                        | *Timestamp* kamera dan waktu penerimaan *frame*      |
| width, height                                             | Ukuran citra masukan                                 |
| preprocess_ms, inference_ms, postprocess_ms               | Waktu tiga tahap menurut Results.speed Ultralytics   |
| end_to_end_ms                                             | Durasi keseluruhan *callback*                        |
| process_cpu_percent, process_rss_bytes                    | Penggunaan CPU dan RSS proses detektor               |
| detection_count, tracked_count, n_ball, n_gawang, n_robot | Jumlah deteksi, deteksi ber-ID, dan jumlah per kelas |
| is_warmup, error                                          | Penanda *frame* *warm-up* dan *error message*        |

## 5.2 Implementasi Sistem

Implementasi dijelaskan dalam dua bagian, yaitu perangkat keras dan perangkat lunak. Kode program dicantumkan hanya pada bagian yang menentukan hasil penelitian, yaitu definisi *student*, fungsi objektif KD hibrida, serta pemuatan model dan *callback* inferensi pada *node* deteksi. Nomor baris pada setiap kode program dihitung dari awal potongan, bukan dari awal berkas.

### 5.2.1 Implementasi Perangkat Keras

#### 5.2.1.1 Implementasi Tubuh Robot

Tubuh robot dipakai dalam konfigurasi bawaan OP3 tanpa perubahan mekanik. Kamera C920 terpasang pada kepala, komputer *onboard* berada di badan, dan seluruh aktuator terhubung ke OpenCR. Robot yang dipakai ditunjukkan pada Gambar 5.12, yaitu tampak depan (Gambar 5.12a) dan tampak samping (Gambar 5.12b) saat robot berada pada tatakan.

**Gambar 5.12** Implementasi tubuh robot tampak depan dan samping

#### 5.2.1.2 Implementasi Rangkaian Elektronika

Rangkaian elektronika mengikuti susunan bawaan OP3, yaitu komputer *onboard*, U2D2, OpenCR, aktuator, dan kamera seperti pada Gambar 5.4 dan Gambar 5.6. Penelitian ini tidak menambah sensor atau papan elektronika baru. Susunan rangkaian elektronika OP3 dari sisi depan, belakang, dan atas disajikan pada Gambar 5.13 sampai Gambar 5.15 \[PERLU DICEK: kesamaan unit pada foto dengan unit OP3 yang digunakan, karena komputer *onboard* unit penelitian tercatat sebagai NUC12WSHi5\].

Pada sisi depan, U2D2 terhubung ke komputer *onboard*, dan tampak tombol daya serta *port* USB komputer *onboard* (Gambar 5.13). Pada sisi belakang tampak sakelar OpenCR, *port* USB, Ethernet, HDMI, kipas, serta *power jack* OpenCR dan komputer *onboard* (Gambar 5.14). Kedua *power jack* inilah yang menerima adaptor 12 V dan 19 V selama pengujian. Pada sisi atas tampak OpenCR beserta *port* *servo*, sakelar, sambungan baterai, dan U2D2 yang terhubung melalui kabel RS-485 (Gambar 5.15) (Brilliant, 2024).

**Gambar 5.13** Rangkaian elektronika tampak depan

Sumber: Brilliant (2024)

**Gambar 5.14** Rangkaian elektronika tampak belakang

Sumber: Brilliant (2024)

**Gambar 5.15** Rangkaian elektronika tampak atas

Sumber: Brilliant (2024)

#### 5.2.1.3 Implementasi Tatakan dan Area Uji

Selama pengujian kondisi berjalan, badan robot diletakkan pada tatakan dan objek uji ditempatkan statis di depan kamera. Komputer *onboard* diakses dari laptop melalui SSH, sedangkan server laboratorium diakses secara terpisah untuk pelatihan dan evaluasi *offline*. Tatakan dan area uji ditunjukkan pada Gambar 5.16.

**Gambar 5.16** Implementasi tatakan dan area uji

### 5.2.2 Implementasi Perangkat Lunak

#### 5.2.2.1 Implementasi Model *Student*

*Student* didefinisikan dalam berkas YAML Ultralytics pada Kode Program 5.1. Hasilnya adalah model berparameter 810.649 sebelum *Conv-BN fusion* dengan 2,43 GFLOPs pada masukan 640, dibandingkan dengan 2.590.425 parameter dan 6,50 GFLOPs pada *teacher*. Ukuran *checkpoint* *student* sekitar 1,82 MiB, sedangkan *teacher* 5.481.875 bait.

**Kode Program 5.1** Konfigurasi model *student*

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 92%" />
</colgroup>
<thead>
<tr class="header">
<th><pre><code>No</code></pre></th>
<th><pre><code>Kode Program</code></pre></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><pre><code></code></pre></td>
<td><pre><code>models/yolo11_tiny_kd.yaml</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>1</code></pre></td>
<td><pre><code>nc: 3</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>2</code></pre></td>
<td><pre><code>scale: t</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>3</code></pre></td>
<td><pre><code>scales:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>4</code></pre></td>
<td><pre><code>  t: [0.50, 0.125, 1024]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>5</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>6</code></pre></td>
<td><pre><code>backbone:</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>7</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [64, 3, 2]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>8</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [128, 3, 2]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>9</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [256, false, 0.25]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>10</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [256, 3, 2]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>11</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [512, false, 0.25]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>12</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [512, 3, 2]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>13</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [512, true]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>14</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [1024, 3, 2]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>15</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [1024, true]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>16</code></pre></td>
<td><pre><code>  - [-1, 1, SPPF, [1024, 5]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>17</code></pre></td>
<td><pre><code>  - [-1, 2, C2PSA, [1024]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>18</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="even">
<td><pre><code>19</code></pre></td>
<td><pre><code>head:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>20</code></pre></td>
<td><pre><code>  - [-1, 1, nn.Upsample, [null, 2, nearest]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>21</code></pre></td>
<td><pre><code>  - [[-1, 6], 1, Concat, [1]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>22</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [512, false]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>23</code></pre></td>
<td><pre><code>  - [-1, 1, nn.Upsample, [null, 2, nearest]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>24</code></pre></td>
<td><pre><code>  - [[-1, 4], 1, Concat, [1]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>25</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [256, false]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>26</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [256, 3, 2]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>27</code></pre></td>
<td><pre><code>  - [[-1, 13], 1, Concat, [1]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>28</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [512, false]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>29</code></pre></td>
<td><pre><code>  - [-1, 1, Conv, [512, 3, 2]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>30</code></pre></td>
<td><pre><code>  - [[-1, 10], 1, Concat, [1]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>31</code></pre></td>
<td><pre><code>  - [-1, 2, C3k2, [1024, true]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>32</code></pre></td>
<td><pre><code>  - [[16, 19, 22], 1, Detect, [nc]]</code></pre></td>
</tr>
</tbody>
</table>

Baris 1 menetapkan jumlah kelas, yaitu bola, gawang, dan robot.

Baris 2 sampai 4 memilih skala t dengan faktor kedalaman 0,50, faktor lebar 0,125, dan batas kanal 1024. Skala nano yang dipakai *teacher* memiliki faktor kedalaman yang sama dan faktor lebar 0,25, sehingga lebar kanal *student* menjadi separuhnya.

Baris 6 sampai 17 mendefinisikan *backbone*. Setiap baris berisi indeks masukan, jumlah pengulangan, jenis modul, dan argumen modul. Lapisan Conv dengan langkah 2 menurunkan resolusi, sedangkan SPPF dan C2PSA berada di ujung *backbone*.

Baris 19 sampai 31 berada pada bagian *head* berkas YAML dan berfungsi sebagai *neck*. Bagian ini menaikkan resolusi dengan nn.Upsample, lalu menggabungkan fitur dari *backbone* melalui Concat.

Baris 32 menempatkan *head* Detect pada lapisan 16, 19, dan 22, yaitu keluaran P3, P4, dan P5. Ketiga lapisan ini juga menjadi titik pengambilan fitur untuk distilasi.

#### 5.2.2.2 Implementasi Fungsi Objektif KD Hibrida

Fungsi objektif KD diimplementasikan dalam skrip train_kd.py sebagai pengganti metode *loss* pada kelas DistillationModel milik Ultralytics. Nilai bobot dan temperatur dibaca dari berkas konfigurasi pada Kode Program 5.2, sedangkan perhitungan *loss* disajikan pada Kode Program 5.3. *Teacher* dimuat dari *checkpoint* FP32 hasil pelatihan sebelumnya yang alamatnya tercatat pada baris awal berkas konfigurasi.

**Kode Program 5.2** Konfigurasi pelatihan KD hibrida penuh

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 92%" />
</colgroup>
<thead>
<tr class="header">
<th><pre><code>No</code></pre></th>
<th><pre><code>Kode Program</code></pre></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><pre><code></code></pre></td>
<td><pre><code>configs/kd_hybrid_full.yaml</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>1</code></pre></td>
<td><pre><code>distillation:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>2</code></pre></td>
<td><pre><code>  mode: hybrid_full</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>3</code></pre></td>
<td><pre><code>  dis: 1.0</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>4</code></pre></td>
<td><pre><code>  feature_weight: 1.0</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>5</code></pre></td>
<td><pre><code>  box_weight: 1.0</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>6</code></pre></td>
<td><pre><code>  class_weight: 1.0</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>7</code></pre></td>
<td><pre><code>  temperature: 2.0</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>8</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="even">
<td><pre><code>9</code></pre></td>
<td><pre><code>training:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>10</code></pre></td>
<td><pre><code>  epochs: 100</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>11</code></pre></td>
<td><pre><code>  batch: 16</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>12</code></pre></td>
<td><pre><code>  workers: 2</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>13</code></pre></td>
<td><pre><code>  imgsz: 640</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>14</code></pre></td>
<td><pre><code>  device: &quot;0&quot;</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>15</code></pre></td>
<td><pre><code>  seed: 42</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>16</code></pre></td>
<td><pre><code>  optimizer: AdamW</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>17</code></pre></td>
<td><pre><code>  lr0: 0.001</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>18</code></pre></td>
<td><pre><code>  lrf: 0.01</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>19</code></pre></td>
<td><pre><code>  warmup_epochs: 3.0</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>20</code></pre></td>
<td><pre><code>  weight_decay: 0.0005</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>21</code></pre></td>
<td><pre><code>  close_mosaic: 10</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>22</code></pre></td>
<td><pre><code>  amp: false</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>23</code></pre></td>
<td><pre><code>  patience: 30</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>24</code></pre></td>
<td><pre><code>  pretrained: false</code></pre></td>
</tr>
</tbody>
</table>

Baris 1 sampai 7 memilih mode hybrid_full dan menetapkan bobot fitur, kotak, dan kelas sebesar 1,0 serta temperatur 2,0 sesuai Persamaan 2.8.

Baris 9 sampai 24 berisi pengaturan pelatihan yang sama untuk semua varian *student*, yaitu 100 *epoch*, *batch* 16, ukuran masukan 640, *optimizer* AdamW, dan tanpa bobot *pretrained*. Pelatihan menggunakan FP32 karena AMP dimatikan. Berkas ini memuat *seed* 42; *run* dengan *seed* lain memakai pengaturan yang sama dengan nilai *seed* yang berbeda.

**Kode Program 5.3** Fungsi *loss* KD hibrida penuh

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 92%" />
</colgroup>
<thead>
<tr class="header">
<th><pre><code>No</code></pre></th>
<th><pre><code>Kode Program</code></pre></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><pre><code></code></pre></td>
<td><pre><code>scripts/train_kd.py, fungsi hybrid_full_loss</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>1</code></pre></td>
<td><pre><code>def hybrid_full_loss(self, batch, preds=None):</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>2</code></pre></td>
<td><pre><code>    if not self.training:</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>3</code></pre></td>
<td><pre><code>        return ORIGINAL_DISTILLATION_LOSS(self, batch, preds)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>4</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="even">
<td><pre><code>5</code></pre></td>
<td><pre><code>    self._teacher_feats.clear()</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>6</code></pre></td>
<td><pre><code>    self._student_feats.clear()</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>7</code></pre></td>
<td><pre><code>    with torch.no_grad():</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>8</code></pre></td>
<td><pre><code>        self.teacher_model(batch[&quot;img&quot;])</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>9</code></pre></td>
<td><pre><code>    student_preds = self.student_model(batch[&quot;img&quot;])</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>10</code></pre></td>
<td><pre><code>    regular_loss, loss_items = self.student_model.loss(batch, student_preds)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>11</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>12</code></pre></td>
<td><pre><code>    teacher_head = self._teacher_feats[self.feats_idx[-1]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>13</code></pre></td>
<td><pre><code>    student_head = self._student_feats[self.feats_idx[-1]]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>14</code></pre></td>
<td><pre><code>    teacher_scores = (</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>15</code></pre></td>
<td><pre><code>        self.decouple_outputs(teacher_head, branch=&quot;one2many&quot;)[&quot;scores&quot;]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>16</code></pre></td>
<td><pre><code>        + self.decouple_outputs(teacher_head, branch=&quot;one2one&quot;)[&quot;scores&quot;]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>17</code></pre></td>
<td><pre><code>    ) / 2</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>18</code></pre></td>
<td><pre><code>    neck_features = [self._teacher_feats[index] for index in self.feats_idx[:-1]]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>19</code></pre></td>
<td><pre><code>    score_parts = torch.split(</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>20</code></pre></td>
<td><pre><code>        teacher_scores,</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>21</code></pre></td>
<td><pre><code>        [feature.shape[-2] * feature.shape[-1] for feature in neck_features],</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>22</code></pre></td>
<td><pre><code>        dim=-1,</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>23</code></pre></td>
<td><pre><code>    )</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>24</code></pre></td>
<td><pre><code>    teacher_scores = tuple(part.sigmoid().max(dim=1, keepdim=True).values for part in score_parts)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>25</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>26</code></pre></td>
<td><pre><code>    feature_loss = torch.zeros((), device=batch[&quot;img&quot;].device)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>27</code></pre></td>
<td><pre><code>    for level, feature_index in enumerate(self.feats_idx[:-1]):</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>28</code></pre></td>
<td><pre><code>        teacher_feature = self.decouple_outputs(self._teacher_feats[feature_index])</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>29</code></pre></td>
<td><pre><code>        student_feature = self.projector[level](self.decouple_outputs(self._student_feats[feature_index]))</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>30</code></pre></td>
<td><pre><code>        feature_loss = feature_loss + self.loss_sl2(</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>31</code></pre></td>
<td><pre><code>            student_feature, teacher_feature, feat_idx=level, teacher_scores=teacher_scores</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>32</code></pre></td>
<td><pre><code>        )</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>33</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>34</code></pre></td>
<td><pre><code>    teacher_branches = head_branches(self.decouple_outputs(teacher_head))</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>35</code></pre></td>
<td><pre><code>    student_branches = head_branches(self.decouple_outputs(student_head))</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>36</code></pre></td>
<td><pre><code>    if not teacher_branches or len(teacher_branches) != len(student_branches):</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>37</code></pre></td>
<td><pre><code>        raise KDRunError(&quot;Teacher and student Detect head output branches do not match.&quot;)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>38</code></pre></td>
<td><pre><code>    box_losses: list[torch.Tensor] = []</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>39</code></pre></td>
<td><pre><code>    class_losses: list[torch.Tensor] = []</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>40</code></pre></td>
<td><pre><code>    for teacher_branch, student_branch in zip(teacher_branches, student_branches):</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>41</code></pre></td>
<td><pre><code>        teacher_boxes = teacher_branch[&quot;boxes&quot;].detach().float()</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>42</code></pre></td>
<td><pre><code>        student_boxes = student_branch[&quot;boxes&quot;].float()</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>43</code></pre></td>
<td><pre><code>        teacher_logits = teacher_branch[&quot;scores&quot;].detach().float()</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>44</code></pre></td>
<td><pre><code>        student_logits = student_branch[&quot;scores&quot;].float()</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>45</code></pre></td>
<td><pre><code>        if teacher_boxes.shape != student_boxes.shape or teacher_logits.shape != student_logits.shape:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>46</code></pre></td>
<td><pre><code>            raise KDRunError(&quot;Teacher/student Detect output shapes differ&quot;)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>47</code></pre></td>
<td><pre><code>        box_losses.append(F.smooth_l1_loss(student_boxes, teacher_boxes))</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>48</code></pre></td>
<td><pre><code>        soft_targets = torch.sigmoid(teacher_logits / temperature)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>49</code></pre></td>
<td><pre><code>        class_losses.append(</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>50</code></pre></td>
<td><pre><code>            F.binary_cross_entropy_with_logits(student_logits / temperature, soft_targets)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>51</code></pre></td>
<td><pre><code>            * (temperature**2)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>52</code></pre></td>
<td><pre><code>        )</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>53</code></pre></td>
<td><pre><code>    box_loss = torch.stack(box_losses).mean()</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>54</code></pre></td>
<td><pre><code>    class_loss = torch.stack(class_losses).mean()</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>55</code></pre></td>
<td><pre><code>    kd_loss = feature_weight * feature_loss + box_weight * box_loss + class_weight * class_loss</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>56</code></pre></td>
<td><pre><code>    # Validator Ultralytics menambahkan tensor ini in-place; bentuknya harus</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>57</code></pre></td>
<td><pre><code>    # sama dengan dis_loss bawaan, yaitu satu elemen, pada train dan VAL.</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>58</code></pre></td>
<td><pre><code>    loss_items[&quot;dis_loss&quot;] = kd_loss.detach().reshape(1)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>59</code></pre></td>
<td><pre><code>    return torch.cat([regular_loss, (kd_loss * batch[&quot;img&quot;].shape[0]).reshape(1)]), loss_items</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>60</code></pre></td>
<td><pre><code></code></pre></td>
</tr>
<tr class="even">
<td><pre><code>61</code></pre></td>
<td><pre><code>DistillationModel.loss = hybrid_full_loss</code></pre></td>
</tr>
</tbody>
</table>

Baris 1 sampai 3 mendefinisikan fungsi *loss*. Saat model tidak dalam mode pelatihan, fungsi memakai *loss* bawaan agar perhitungan pada validasi tidak berubah.

Baris 5 sampai 10 mengosongkan penyimpan fitur, menjalankan *teacher* tanpa perhitungan gradien, menjalankan *student*, lalu menghitung *loss* deteksi berlabel bawaan Ultralytics.

Baris 12 sampai 24 mengambil keluaran *head* kedua model, merata-ratakan skor kelas *teacher* dari dua cabang *head*, lalu membaginya menurut skala P3, P4, dan P5. Skor maksimum setelah *sigmoid* pada setiap posisi menjadi bobot *anchor point* menurut Persamaan 2.3.

Baris 26 sampai 32 menghitung *loss* fitur pada ketiga skala. Fitur *student* diproyeksikan ke jumlah kanal *teacher* oleh *projector*, lalu dibandingkan dengan fitur *teacher* menggunakan bobot *anchor point* (Persamaan 2.4).

Baris 34 sampai 52 menghitung *loss* kotak dengan Smooth L1 (Persamaan 2.5) dan *loss* kelas dengan BCE bertemperatur yang dikalikan kuadrat temperatur (Persamaan 2.6) untuk setiap cabang *head*. Keluaran *teacher* dilepas dari graf gradien sehingga hanya *student* yang diperbarui. Baris 36, 37, 45, dan 46 menghentikan pelatihan bila bentuk keluaran kedua model berbeda.

Baris 53 sampai 59 merata-ratakan *loss* kotak dan kelas, menjumlahkan ketiga suku KD sesuai bobotnya, lalu menggabungkannya dengan *loss* berlabel. Suku KD dikalikan ukuran *batch* agar mengikuti konvensi skala *loss* Ultralytics (Persamaan 2.8).

Baris 61 memasang fungsi ini sebagai metode *loss* DistillationModel sebelum pelatihan dimulai.

#### 5.2.2.3 Implementasi *Node* Deteksi

*Node* deteksi diimplementasikan dalam skrip op3_pytorch_detector.py dan dijalankan dengan interpreter Python 3.12 yang dapat mengimpor modul ROS 2 Jazzy sekaligus PyTorch dan Ultralytics. Parameter yang dipakai pada pengujian disajikan pada Tabel 5.2. Ambang *runtime* 0,25 dan 0,45 merupakan parameter eksplisit dan berbeda dari ambang evaluasi *offline* (*confidence floor* 0,001 dan NMS 0,7). *Node* hanya menerima citra dan melakukan *publish* hasil; tidak ada antarmuka ke *servo* atau modul gerak.

**Tabel 5.2** Parameter *node* deteksi pada pengujian

| **Parameter**                            | **Nilai**                       | **Kegunaan**                             |
|------------------------------------------|---------------------------------|------------------------------------------|
| model_variant                            | teacher, hybrid, supervised, kd | Memilih *checkpoint* terdaftar           |
| input_topic                              | /thesis/image_raw               | *Topic* citra kamera                     |
| imgsz                                    | 640                             | Ukuran sisi masukan model                |
| confidence_threshold                     | 0,25                            | Ambang *confidence* *runtime*            |
| iou_threshold                            | 0,45                            | Ambang IoU NMS *runtime*                 |
| enable_tracking, tracker_config          | true, botsort.yaml              | Asosiasi ID BoT-SORT                     |
| torch_num_threads, torch_interop_threads | 4, 2                            | Jumlah *thread* PyTorch                  |
| warmup_frames, duration_s                | 30, 60                          | *Warm-up* dan *measurement window*       |
| publish_debug_image                      | true                            | Melakukan *publish* *preview* beranotasi |
| experiment_condition                     | servo_idle atau walking         | Label kondisi dari operator              |

Pemuatan model saat *node* dimulai disajikan pada Kode Program 5.4. Bagian ini dijalankan sekali setelah keberadaan *checkpoint* dan pemetaan kelas pada berkas konfigurasi data diperiksa.

**Kode Program 5.4** Pemuatan model pada *node* deteksi

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 92%" />
</colgroup>
<thead>
<tr class="header">
<th><pre><code>No</code></pre></th>
<th><pre><code>Kode Program</code></pre></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><pre><code></code></pre></td>
<td><pre><code>scripts/op3_pytorch_detector.py, metode __init__</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>1</code></pre></td>
<td><pre><code>if self.requested_torch_threads &gt; 0:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>2</code></pre></td>
<td><pre><code>    torch.set_num_threads(self.requested_torch_threads)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>3</code></pre></td>
<td><pre><code>if self.requested_torch_interop_threads &gt; 0:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>4</code></pre></td>
<td><pre><code>    torch.set_num_interop_threads(self.requested_torch_interop_threads)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>5</code></pre></td>
<td><pre><code>if str(torch.__version__).startswith(&quot;2.4&quot;) is False:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>6</code></pre></td>
<td><pre><code>    self.get_logger().warning(f&quot;PyTorch runtime is {torch.__version__}; verify checkpoint compatibility&quot;)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>7</code></pre></td>
<td><pre><code>self.model = ultralytics.YOLO(str(self.model_path), task=&quot;detect&quot;)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>8</code></pre></td>
<td><pre><code>checkpoint_names = {int(k): str(v) for k, v in self.model.names.items()}</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>9</code></pre></td>
<td><pre><code>if checkpoint_names != EXPECTED_NAMES:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>10</code></pre></td>
<td><pre><code>    raise ValueError(f&quot;Checkpoint class mapping mismatch: {checkpoint_names}&quot;)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>11</code></pre></td>
<td><pre><code>self.model.model.eval()</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>12</code></pre></td>
<td><pre><code>self.model.to(&quot;cpu&quot;)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>13</code></pre></td>
<td><pre><code>self.model.model.float()</code></pre></td>
</tr>
</tbody>
</table>

Baris 1 sampai 4 menetapkan jumlah *thread* PyTorch dari parameter *node*, yaitu 4 *thread* operasi dan 2 *thread* antaroperasi pada pengujian. Nilai ini berlaku saat inisialisasi. *Replay* pada Subbab 6.5 menunjukkan bahwa inisialisasi *backend* CPU Ultralytics pada inferensi pertama dapat mengubah jumlah *thread* operasi.

Baris 5 dan 6 memberi peringatan bila versi PyTorch di robot berbeda dari versi yang digunakan saat *checkpoint* disimpan.

Baris 7 sampai 10 memuat *checkpoint* dan menghentikan *node* bila pemetaan kelas di dalamnya berbeda dari urutan bola, gawang, dan robot.

Baris 11 sampai 13 menempatkan model pada mode evaluasi, pada CPU, dan dalam presisi FP32.

Inti *callback* yang dijalankan untuk setiap *frame* disajikan pada Kode Program 5.5. Sebelum bagian ini, *callback* mengubah pesan citra ROS 2 menjadi larik BGR dengan cv_bridge dan memeriksa bahwa larik tersebut tidak kosong dan memiliki tiga kanal.

**Kode Program 5.5** Inferensi pada *callback* *node* deteksi

<table>
<colgroup>
<col style="width: 7%" />
<col style="width: 92%" />
</colgroup>
<thead>
<tr class="header">
<th><pre><code>No</code></pre></th>
<th><pre><code>Kode Program</code></pre></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><pre><code></code></pre></td>
<td><pre><code>scripts/op3_pytorch_detector.py, metode on_image</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>1</code></pre></td>
<td><pre><code>inference = self.model.track if self.enable_tracking else self.model.predict</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>2</code></pre></td>
<td><pre><code>inference_options = {</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>3</code></pre></td>
<td><pre><code>    &quot;source&quot;: frame, &quot;imgsz&quot;: self.imgsz, &quot;batch&quot;: 1, &quot;device&quot;: &quot;cpu&quot;,</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>4</code></pre></td>
<td><pre><code>    &quot;conf&quot;: self.conf, &quot;iou&quot;: self.iou, &quot;verbose&quot;: False, &quot;save&quot;: False, &quot;plots&quot;: False,</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>5</code></pre></td>
<td><pre><code>    &quot;stream&quot;: False, &quot;max_det&quot;: 300,</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>6</code></pre></td>
<td><pre><code>}</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>7</code></pre></td>
<td><pre><code>if self.enable_tracking:</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>8</code></pre></td>
<td><pre><code>    inference_options.update({&quot;tracker&quot;: self.tracker_config, &quot;persist&quot;: True})</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>9</code></pre></td>
<td><pre><code>results = inference(**inference_options)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>10</code></pre></td>
<td><pre><code>result = results[0]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>11</code></pre></td>
<td><pre><code>speed = result.speed</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>12</code></pre></td>
<td><pre><code>detections = Detection2DArray()</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>13</code></pre></td>
<td><pre><code>detections.header = message.header</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>14</code></pre></td>
<td><pre><code>boxes = result.boxes</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>15</code></pre></td>
<td><pre><code>track_ids = track_ids_for_boxes(boxes, self.enable_tracking)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>16</code></pre></td>
<td><pre><code>class_counts = {&quot;ball&quot;: 0, &quot;gawang&quot;: 0, &quot;robot&quot;: 0}</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>17</code></pre></td>
<td><pre><code>tracked_count = 0</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>18</code></pre></td>
<td><pre><code>if boxes is not None:</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>19</code></pre></td>
<td><pre><code>    for index, box in enumerate(boxes):</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>20</code></pre></td>
<td><pre><code>        class_id = int(box.cls.item())</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>21</code></pre></td>
<td><pre><code>        class_name = EXPECTED_NAMES[class_id]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>22</code></pre></td>
<td><pre><code>        confidence = float(box.conf.item())</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>23</code></pre></td>
<td><pre><code>        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>24</code></pre></td>
<td><pre><code>        track_id = track_ids[index]</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>25</code></pre></td>
<td><pre><code>        detection = Detection2D()</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>26</code></pre></td>
<td><pre><code>        detection.id = detection_identifier(class_name, track_id)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>27</code></pre></td>
<td><pre><code>        detection.header = message.header</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>28</code></pre></td>
<td><pre><code>        detection.bbox.center.position.x = (x1 + x2) / 2.0</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>29</code></pre></td>
<td><pre><code>        detection.bbox.center.position.y = (y1 + y2) / 2.0</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>30</code></pre></td>
<td><pre><code>        detection.bbox.size_x = max(0.0, x2 - x1)</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>31</code></pre></td>
<td><pre><code>        detection.bbox.size_y = max(0.0, y2 - y1)</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>32</code></pre></td>
<td><pre><code>        hypothesis = ObjectHypothesisWithPose()</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>33</code></pre></td>
<td><pre><code>        hypothesis.hypothesis.class_id = f&quot;{class_id}:{EXPECTED_NAMES[class_id]}&quot;</code></pre></td>
</tr>
<tr class="odd">
<td><pre><code>34</code></pre></td>
<td><pre><code>        hypothesis.hypothesis.score = confidence</code></pre></td>
</tr>
<tr class="even">
<td><pre><code>35</code></pre></td>
<td><pre><code>        detection.results.append(hypothesis)</code></pre></td>
</tr>
</tbody>
</table>

Baris 1 memilih fungsi *track* bila pelacakan aktif dan fungsi *predict* bila tidak aktif.

Baris 2 sampai 8 menyusun argumen inferensi, yaitu ukuran masukan 640, *batch* 1, CPU, ambang *confidence* dan IoU *runtime*, serta berkas konfigurasi BoT-SORT dengan status pelacak yang dipertahankan antar-*frame*.

Baris 9 sampai 11 menjalankan inferensi dan mengambil waktu tahap *preprocess*, inferensi, dan *postprocess* dari Results.speed untuk dicatat pada *log*.

Baris 12 sampai 17 menyiapkan pesan Detection2DArray dengan *header* yang sama dengan citra masukan, sehingga *timestamp* deteksi dapat dicocokkan dengan *timestamp* kamera.

Baris 18 sampai 35 mengubah setiap kotak prediksi dari koordinat sudut menjadi titik pusat dan ukuran, lalu mengisi ID kelas, nama kelas, *confidence*, dan ID pelacakan ke dalam pesan Detection2D.

Setelah seluruh kotak diproses, pesan hasil di-*publish* pada /vision/detections. Bila publish_debug_image aktif, citra beranotasi dari result.plot() di-*publish* pada /vision/debug_image. *Callback* kemudian menulis satu baris CSV per *frame* sesuai kolom pada Tabel 5.1.

#### 5.2.2.4 Implementasi Pendukung Pengujian

Kondisi berjalan dibangkitkan oleh skrip pengujian yang dijalankan peneliti, dengan badan OP3 ditopang tatakan robot agar beban *servo* berkurang. Skrip mengirim perintah mulai ke /robotis/walking/command setelah *warm-up* 30 *frame*, menunggu tanda terima, lalu menghentikan *gait* setelah 63 detik atau lebih awal bila *servo* kepala bergeser lebih dari dua *count* atau aliran data status *servo* terputus. *Servo* kepala tidak menerima perintah posisi selama pengujian. Kondisi diam dan berjalan dicatat sebagai label operator, karena *node* deteksi tidak membaca data gerak robot.

Label *frame* kamera OP3 ditinjau dengan op3_label_reviewer, yang menampilkan *frame* beserta kotak label awal lalu menyimpan label hasil tinjauan dan nama peninjau. Pelabelan buta pada sampel Set Kamera 2 menggunakan alat terpisah yang tidak menampilkan prediksi. Evaluasi akurasi kamera dijalankan secara *offline* oleh paket evaluasi tersendiri yang memverifikasi *hash* *checkpoint*, citra, dan label sebelum menghitung metrik.
