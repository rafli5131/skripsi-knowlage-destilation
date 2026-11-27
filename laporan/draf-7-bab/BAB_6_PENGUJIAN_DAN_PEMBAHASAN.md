# BAB 6 PENGUJIAN

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v35 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

Bab ini menyajikan pengujian dengan urutan mengikuti rumusan masalah. Subbab 6.1 memuat pengujian fungsional yang memastikan sistem berjalan sesuai kebutuhan sebelum hasil lainnya dianalisis. Subbab 6.2 sampai Subbab 6.5 menjawab rumusan masalah nomor 1 sampai 4 secara berurutan, yaitu akurasi berdasarkan mAP, *precision*, *recall*, dan *F1-score*, latensi dan FPS, serta penggunaan CPU dan RAM. Subbab 6.6 memuat pengujian tambahan, dan Subbab 6.7 mengevaluasi hasil terhadap setiap rumusan masalah. Setiap pengujian diuraikan dalam empat bagian, yaitu tujuan, prosedur, hasil, dan analisis hasil pengujian.

## 6.1 Pengujian Fungsional

### 6.1.1 Tujuan Pengujian

Pengujian ini bertujuan memeriksa apakah sistem memenuhi kebutuhan fungsional KF-01 sampai KF-05 dan kebutuhan nonfungsional KNF-01 pada Bab 4. Pengujian ini memastikan sistem berjalan sesuai kebutuhan sebelum hasil akurasi dan *runtime* dianalisis.

### 6.1.2 Prosedur Pengujian

Pengujian memakai metode kotak hitam atau *black-box testing*, yaitu sistem dinilai dari masukan dan keluarannya tanpa memeriksa struktur kode di dalamnya (Khan dan Khan, 2012; Nidhra dan Dondeti, 2012). Penilaian dilakukan secara retrospektif dari *log* 24 *run* pengujian *runtime* pada Subbab 6.4 dan satu sesi pelacakan bola bergerak. Prosedurnya sebagai berikut.

1.  Menyusun kasus uji untuk setiap kebutuhan, berisi masukan, hasil yang diharapkan, dan kriteria lulus sesuai indikator pada Tabel 4.2 dan Tabel 4.3.

2.  Mengumpulkan *metadata* JSON, CSV per *frame*, CSV per deteksi, dan tangkapan *preview* dari 24 *run*, serta *log* deteksi sesi pelacakan bola bergerak dengan KD hibrida *seed* 1337.

3.  Mencocokkan hasil aktual dengan hasil yang diharapkan, termasuk mencocokkan *log* mentah 24 *run* di OP3 dengan rekapitulasi hasil *runtime*.

4.  Menyatakan kasus uji lulus bila hasil aktual sesuai, dan mencatat batas bukti bila bukti yang tersedia tidak mencakup seluruh kondisi.

### 6.1.3 Hasil Pengujian

Hasil kasus uji disajikan pada Tabel 6.1. Contoh *preview* keempat model disajikan pada Gambar 6.1, dan lintasan bola pada sesi pelacakan disajikan pada Gambar 6.2.

**Tabel 6.1** Hasil kasus uji kebutuhan fungsional dan nonfungsional

| **ID uji** | **Kebutuhan**                             | **Hasil yang diharapkan**                                                         | **Hasil aktual**                                                                                                                                                  | **Status**           |
|------------|-------------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
| UJ-KF-01   | KF-01 Menerima citra kamera OP3           | Setiap *run* memproses *frame* dan tidak ada *error frame*                        | 24 dari 24 *run* memenuhi; 17.090 *frame* diproses tanpa *error*                                                                                                  | Lulus                |
| UJ-KF-02   | KF-02 Mendeteksi bola, gawang, dan robot  | Ketiga kelas muncul sebagai kotak berlabel kelas pada setiap *run*                | 24 dari 24 *run* memuat ketiga kelas; cakupan *frame* terendah 100% untuk bola, 92,5% untuk gawang, dan 100% untuk robot                                          | Lulus                |
| UJ-KF-03   | KF-03 Menyediakan ID pelacakan            | Bola memiliki ID dan ID yang sama muncul pada setiap *frame* selama bola bergerak | ID 2 muncul pada 382 dari 382 *frame* dengan pergeseran pusat 257,2 piksel (X) dan 130,8 piksel (Y); kotak bola tambahan dengan ID lain muncul pada 13 *frame*    | Lulus dengan catatan |
| UJ-KF-04   | KF-04 Mencatat data *runtime* per *frame* | Setiap baris memuat *timestamp*, durasi tahap, CPU, RSS, dan kolom *error*        | 24 dari 24 *log* lengkap, dan 24 dari 24 *log* mentah di OP3 cocok dengan rekapitulasi hasil *runtime*                                                            | Lulus                |
| UJ-KF-05   | KF-05 Menampilkan *preview*               | Kotak, nama kelas, *confidence*, dan ID tampak pada *preview*                     | Enam tangkapan dari keempat model menampilkan kotak, kelas, *confidence*, dan ID (Gambar 6.1); dinilai dari tangkapan yang tersedia, bukan sepanjang setiap *run* | Lulus dengan catatan |
| UJ-KNF-01  | KNF-01 Laju pemrosesan                    | FPS efektif rata-rata setiap *run* minimal 8 FPS                                  | 24 dari 24 *run* memenuhi; terendah 9,69 FPS (*teacher*, diam, *repetition* ketiga)                                                                               | Lulus                |

**Gambar 6.1** *Preview* deteksi keempat model pada kondisi berjalan

**Gambar 6.2** Lintasan pusat bola ber-ID 2 pada sesi pelacakan bola bergerak

### 6.1.4 Analisis Hasil Pengujian

Kelima kasus uji kebutuhan fungsional dan kasus uji KNF-01 lulus, dengan catatan pada KF-03 dan KF-05. Pada sesi pelacakan, bola berpindah sekitar 257 piksel secara horizontal dan 131 piksel secara vertikal tanpa pergantian ID. Kotak bola tambahan dengan ID lain pada 13 *frame* menunjukkan adanya kotak ganda atau *false detection* sesaat. Sesi ini hanya berlangsung sekitar 30 detik dengan satu model dan satu objek bergerak, dan tidak ada label acuan identitas, sehingga hasilnya tidak mengukur metrik pelacakan seperti MOTA atau IDF1. FPS efektif terendah 9,69 FPS masih di atas kriteria KNF-01.

Bukti KF-05 berupa tangkapan pada waktu tertentu, sehingga tidak membuktikan bahwa *preview* bebas macet sepanjang setiap *run*. Angka *confidence* pada kotak adalah skor model, bukan akurasi. Kriteria lulus pada Tabel 6.1 dirumuskan dari indikator Bab 4 setelah data tersedia, sehingga penilaiannya bersifat retrospektif.

## 6.2 Pengujian Akurasi Berdasarkan mAP

### 6.2.1 Tujuan Pengujian

Pengujian ini menjawab rumusan masalah nomor 1, yaitu tingkat akurasi berdasarkan nilai mAP model *student* hasil KD hibrida dibandingkan dengan *student* *supervised* berarsitektur sama dan dengan *teacher* YOLO11n. Akurasi diukur dengan mAP50 dan mAP50-95 pada TEST serta pada citra kamera OP3.

### 6.2.2 Prosedur Pengujian

Langkah pengujian adalah sebagai berikut.

1.  Menyaring varian KD pada VAL dengan *seed* 42, lalu mengulang varian terpilih dan pembandingnya dengan *seed* 1337 dan 2025.

2.  Memilih *seed* KD hibrida dan KD murni yang digunakan pada OP3 berdasarkan mAP50-95 tertinggi pada VAL, sebelum TEST dievaluasi. *Supervised* memakai *seed* yang sama dengan KD hibrida agar keduanya berpasangan.

3.  Memverifikasi *hash* SHA-256 592 citra dan label TEST, lalu mengevaluasi sembilan *checkpoint* *student* dan *teacher* dengan *confidence floor* 0,001 dan NMS IoU 0,7.

4.  Menghitung mAP50 dan mAP50-95 setiap model serta selisih berpasangan KD hibrida penuh dikurangi *supervised* pada *seed* yang sama.

5.  Mengevaluasi ulang seluruh *checkpoint* melalui *predict path* yang dipakai *node* di robot untuk memeriksa pengaruh jalur evaluasi.

6.  Menyiapkan Set Kamera 1 (260 *frame* retrospektif) dan Set Kamera 2 (260 *frame*, 130 untuk setiap kondisi) beserta label hasil tinjauan manual seperti dijelaskan pada Subbab 3.3.5, lalu memverifikasi *hash* *checkpoint*, citra, dan label.

7.  Menjalankan keempat *checkpoint* yang dipakai pada pengujian *runtime*, yaitu *teacher*, KD hibrida penuh *seed* 1337, *supervised* *seed* 1337, dan KD murni *seed* 42, secara *offline* pada CPU komputer *onboard* dengan masukan 640.

8.  Pada Set Kamera 2, menghitung ulang mAP50-95 dengan label peninjau kedua dan dengan konvensi kotak alternatif pada 52 *frame* sampel.

### 6.2.3 Hasil Pengujian

#### 6.2.3.1 Hasil Seleksi pada VAL

Hasil penyaringan varian dengan *seed* 42 disajikan pada Tabel 6.2. KD hibrida penuh memberi mAP50-95 VAL tertinggi, sedangkan varian KD murni berbobot lokasi *teacher* menurunkan *precision* pada *confidence* 0,25 menjadi 0,0473 sehingga tidak diteruskan. Pada tiga *seed*, mAP50-95 VAL KD hibrida penuh lebih tinggi daripada *supervised* dengan rata-rata selisih +0,0297 ± 0,0047. *Seed* 1337 memberi mAP50-95 VAL tertinggi di antara ketiga *seed* KD hibrida penuh (0,7523), sehingga *checkpoint* ini digunakan pada OP3.

**Tabel 6.2** Hasil penyaringan varian *student* pada VAL dengan *seed* 42

| **Varian**                         | **mAP50** | **mAP50-95** | ***Precision*** | ***Recall*** | **F1** |
|------------------------------------|-----------|--------------|-----------------|--------------|--------|
| KD murni                           | 0,9620    | 0,6826       | 0,7899          | 0,9623       | 0,8676 |
| KD murni berbobot lokasi *teacher* | 0,7755    | 0,5907       | 0,0473          | 0,9906       | 0,0903 |
| KD hibrida fitur                   | 0,9691    | 0,7436       | 0,8658          | 0,9684       | 0,9142 |
| KD hibrida penuh                   | 0,9725    | 0,7488       | 0,8721          | 0,9780       | 0,9220 |
| *Supervised*                       | 0,9733    | 0,7189       | 0,8829          | 0,9679       | 0,9235 |

Perkembangan mAP50, mAP50-95, dan F1 pada VAL selama pelatihan ketiga metode *student* disajikan pada Gambar 6.3. Garis menunjukkan rata-rata tiga *seed*, sedangkan pita menunjukkan rentang nilai terendah sampai tertinggi. Pada mAP50 dan F1, KD hibrida penuh dan *supervised* hampir berimpit setelah sekitar *epoch* ke-40. Pada mAP50-95, KD hibrida penuh berada di atas *supervised* sepanjang pelatihan dan selisihnya bertahan sampai *epoch* ke-100. KD murni berada paling bawah pada ketiga metrik. Kurva ini dicatat oleh *validator* Ultralytics pada akhir setiap *epoch*, sehingga nilai *epoch* terakhir dapat sedikit berbeda dari hasil evaluasi ulang *checkpoint* pada Tabel 6.2.

**Gambar 6.3** mAP50, mAP50-95, dan F1 VAL per *epoch* tiga metode *student*

#### 6.2.3.2 Hasil mAP pada TEST

mAP pada 592 citra TEST disajikan pada Tabel 6.3 dan Gambar 6.4. Nilai *student* adalah rata-rata dan simpangan baku tiga *seed*, sedangkan *teacher* diwakili satu *checkpoint*. TEST pernah digunakan untuk mengevaluasi *teacher* dan KD murni sebelum KD hibrida dirancang, sehingga hasil ini tidak diklaim sebagai hasil pada data yang belum pernah dibuka. Nilai setiap *seed* disajikan pada Tabel D.1 di Lampiran D.

**Tabel 6.3** mAP50 dan mAP50-95 model pada TEST

| **Model**         | **mAP50**       | **mAP50-95**    |
|-------------------|-----------------|-----------------|
| *Teacher* YOLO11n | 0,9642          | 0,7800          |
| KD hibrida penuh  | 0,9583 ± 0,0008 | 0,7469 ± 0,0022 |
| *Supervised*      | 0,9601 ± 0,0034 | 0,7225 ± 0,0035 |
| KD murni          | 0,9446 ± 0,0040 | 0,6630 ± 0,0108 |

**Gambar 6.4** mAP50 dan mAP50-95 keempat model pada TEST; *error bar* menunjukkan simpangan baku tiga *seed*

Selisih berpasangan KD hibrida penuh terhadap *supervised* disajikan pada Tabel 6.4 dan Gambar 6.5. mAP50-95 KD hibrida lebih tinggi pada ketiga pasangan *seed*, dengan rata-rata +0,0244 ± 0,0040, sedangkan selisih mAP50 berganti tanda dan rata-ratanya hanya -0,0018 ± 0,0037.

**Tabel 6.4** Selisih berpasangan mAP KD hibrida penuh dikurangi *supervised* pada TEST

| ***Seed***     | **Δ mAP50**      | **Δ mAP50-95**   |
|----------------|------------------|------------------|
| 42             | +0,0008          | +0,0244          |
| 1337           | -0,0001          | +0,0203          |
| 2025           | -0,0060          | +0,0284          |
| Rata-rata ± SD | -0,0018 ± 0,0037 | +0,0244 ± 0,0040 |

**Gambar 6.5** Selisih berpasangan mAP KD hibrida penuh dikurangi *supervised* pada TEST untuk setiap *seed*

mAP50-95 per kelas pada Tabel 6.5 dan Gambar 6.6 memperlihatkan asal keunggulan tersebut. Kenaikan terbesar KD hibrida terhadap *supervised* terjadi pada bola (+0,0513), sedangkan pada gawang hanya +0,0083 dan pada robot +0,0136. Gawang adalah kelas dengan mAP50-95 terendah pada ketiga model.

**Tabel 6.5** mAP50-95 per kelas pada TEST

| **Kelas** | ***Teacher*** | **KD hibrida penuh** | ***Supervised*** |
|-----------|---------------|----------------------|------------------|
| Bola      | 0,9131        | 0,8754 ± 0,0058      | 0,8241 ± 0,0040  |
| Gawang    | 0,5684        | 0,5569 ± 0,0027      | 0,5486 ± 0,0004  |
| Robot     | 0,8585        | 0,8085 ± 0,0084      | 0,7949 ± 0,0062  |

**Gambar 6.6** mAP50-95 per kelas pada TEST

Evaluator TEST menghitung mAP melalui *validator path* Ultralytics, yang menggunakan tensor 672 × 672 piksel akibat penyusunan *batch* persegi panjang dengan *padding* 0,5 dan NMS *multi-label*. *Node* di robot memakai *predict path* dengan tensor 640 × 640 piksel untuk citra TEST dan NMS tanpa *multi-label*. Untuk memastikan angka TEST tidak bergantung pada perbedaan tersebut, sepuluh *checkpoint* dievaluasi ulang melalui *predict path* pada CPU. Hasilnya disajikan pada Tabel 6.6. Selisih rata-rata kelompok paling besar 0,0035, dan urutan mAP50-95 keempat model tidak berubah.

**Tabel 6.6** mAP50-95 pada TEST menurut jalur evaluasi

| **Kelompok**      | ***Validator path*** | ***Predict path*** | **Selisih** |
|-------------------|----------------------|--------------------|-------------|
| *Teacher* YOLO11n | 0,7800               | 0,7791             | -0,0009     |
| KD hibrida penuh  | 0,7469               | 0,7434             | -0,0035     |
| *Supervised*      | 0,7225               | 0,7248             | +0,0023     |
| KD murni          | 0,6630               | 0,6647             | +0,0017     |

#### 6.2.3.3 Hasil mAP pada Citra Kamera OP3

mAP keempat model pada kedua set kamera OP3 disajikan pada Tabel 6.7 dan Gambar 6.7. Pada Set Kamera 1, *teacher* memberi mAP50-95 tertinggi (0,5004), diikuti KD hibrida (0,4885), *supervised* (0,4414), dan KD murni (0,4218), sedangkan mAP50 tertinggi dicapai KD hibrida (0,7526). Pada Set Kamera 2, mAP50 *teacher*, KD hibrida, dan *supervised* hampir sama, yaitu sekitar 0,995, sedangkan mAP50-95 tertinggi dicapai KD hibrida (0,8275). Seluruh nilai mAP pada Set Kamera 1 jauh lebih rendah daripada nilai pada TEST.

**Tabel 6.7** mAP keempat model pada citra kamera OP3

| **Model**                | **Set 1 mAP50** | **Set 1 mAP50-95** | **Set 2 mAP50** | **Set 2 mAP50-95** |
|--------------------------|-----------------|--------------------|-----------------|--------------------|
| *Teacher* YOLO11n        | 0,7058          | 0,5004             | 0,9949          | 0,7462             |
| KD hibrida *seed* 1337   | 0,7526          | 0,4885             | 0,9949          | 0,8275             |
| *Supervised* *seed* 1337 | 0,7045          | 0,4414             | 0,9950          | 0,7865             |
| KD murni *seed* 42       | 0,6301          | 0,4218             | 0,8658          | 0,7074             |

**Gambar 6.7** mAP50 dan mAP50-95 keempat model pada kedua set kamera OP3

Kepekaan mAP50-95 terhadap pelabelan pada 52 *frame* sampel Set Kamera 2 disajikan pada Tabel 6.8 dan Gambar 6.8. Peninjau kedua menghasilkan 40 dari 40 pasangan kotak pada IoU ≥ 0,5 untuk setiap kelas, dengan IoU rata-rata 0,6811 untuk bola, 0,6389 untuk gawang, dan 0,8882 untuk robot. Meskipun semua kotak berpasangan, mAP50-95 seluruh model turun sekitar 0,27 sampai 0,38 pada label peninjau kedua, dan urutan model berubah: *supervised* menjadi tertinggi, sedangkan KD hibrida turun ke urutan ketiga. Pada konvensi alternatif, yaitu seluruh rangka gawang dan seluruh tubuh robot, mAP50-95 seluruh model berada pada 0,26 sampai 0,31.

**Tabel 6.8** Kepekaan mAP50-95 terhadap label pada 52 *frame* sampel Set Kamera 2

| **Model**         | **Label penulis** | **Label peninjau kedua** | **Konvensi alternatif** |
|-------------------|-------------------|--------------------------|-------------------------|
| *Teacher* YOLO11n | 0,7409            | 0,4625                   | 0,2900                  |
| KD hibrida        | 0,8134            | 0,4328                   | 0,2649                  |
| *Supervised*      | 0,7888            | 0,5230                   | 0,3094                  |
| KD murni          | 0,7056            | 0,3995                   | 0,2913                  |

**Gambar 6.8** mAP50-95 pada tiga set label Set Kamera 2

mAP pada Tabel 6.7 dihitung melalui *validator path*. Untuk memperoleh angka dari jalur yang sama dengan robot, keempat model dievaluasi ulang secara *offline* pada komputer *onboard* melalui *predict path* dengan *frame* dan label yang sama. Uji identitas 48 pemeriksaan lulus, yaitu AP *validator path* dan hitungan per kelas *predict path* mereproduksi hasil sebelumnya. Hasilnya disajikan pada Tabel 6.9 dan Gambar 6.9.

**Tabel 6.9** mAP50-95 kamera OP3 menurut jalur evaluasi

| **Model**                | **Set 1 *validator path*** | **Set 1 *predict path*** | **Set 2 *validator path*** | **Set 2 *predict path*** |
|--------------------------|----------------------------|--------------------------|----------------------------|--------------------------|
| *Teacher* YOLO11n        | 0,5004                     | 0,5041                   | 0,7462                     | 0,5473                   |
| KD hibrida *seed* 1337   | 0,4885                     | 0,4307                   | 0,8275                     | 0,8900                   |
| *Supervised* *seed* 1337 | 0,4414                     | 0,4216                   | 0,7865                     | 0,7828                   |
| KD murni *seed* 42       | 0,4218                     | 0,4729                   | 0,7074                     | 0,7239                   |

**Gambar 6.9** mAP50-95 keempat model pada kedua set kamera OP3 menurut jalur evaluasi

Berbeda dengan TEST, urutan mAP50-95 pada kamera OP3 berubah antarjalur. Pada Set Kamera 1, *predict path* menempatkan *teacher* di urutan pertama, diikuti KD murni, KD hibrida, dan *supervised*, sedangkan *validator path* menempatkan KD hibrida di urutan kedua. Pada Set Kamera 2, *predict path* menempatkan KD hibrida di urutan pertama dan *teacher* di urutan terakhir. Pemisahan faktor pada *teacher* Set Kamera 2 menunjukkan bahwa bentuk *letterbox* jauh lebih berpengaruh daripada NMS *multi-label*. AP50 gawang *teacher* adalah 0,1112 pada bentuk 480 × 640 piksel dan 0,9946 pada bentuk 512 × 672 piksel, sedangkan NMS *multi-label* tidak mengubah angka tersebut. *Confidence sweep* pada *predict path* juga menunjukkan bahwa gawang yang dapat dicocokkan pada *confidence floor* 0,001 hanya 68 dari 200 untuk *teacher*, dibandingkan dengan 200 untuk KD hibrida, 200 untuk *supervised*, dan 191 untuk KD murni. Pada sebagian besar gawang parsial, *teacher* sama sekali tidak menghasilkan kotak di *predict path*. Pada tiga *student* di Set Kamera 1, pemisahan faktor *validator path* tidak mereproduksi AP *validator path* dalam batas toleransi, sehingga faktor pada bagian itu tidak ditafsirkan.

### 6.2.4 Analisis Hasil Pengujian

Pada TEST, KD hibrida penuh mempertahankan 95,8% mAP50-95 *teacher* dengan jumlah parameter 31% dan GFLOPs 37% dari *teacher*, sedangkan *supervised* mempertahankan 92,6% dan KD murni 85,0%. Ketiga *student* berarsitektur identik, sehingga selisih di antara ketiganya berasal dari fungsi objektif pelatihan. Keunggulan KD hibrida terletak pada ketepatan letak kotak. Hal ini terlihat dari selisih mAP50-95 yang positif pada ketiga pasangan *seed*, sementara mAP50 hampir sama, dan dari kenaikan terbesar pada bola. KD murni, yang tidak memakai label, berada di bawah *supervised*. Hasil ini sejalan dengan temuan bahwa KD dapat memperbaiki generalisasi *student* tanpa membuat *student* benar-benar meniru *teacher* (Stanton, et al., 2021, p. 6906) dan bahwa kapasitas *student* yang jauh lebih kecil membatasi apa yang dapat dipelajarinya dari *teacher* (Cho dan Hariharan, 2019). Dengan tiga *seed*, hasil ini deskriptif; konsistensi tanda selisih pada ketiga pasangan menjadi dasar klaim, bukan uji signifikansi.

Keunggulan mAP50-95 KD hibrida pada TEST tidak berulang secara konsisten pada citra kamera OP3. Peringkat model bergantung pada set *frame*, konvensi label, dan jalur evaluasi. Pada *predict path* yang dipakai robot, KD hibrida berada di urutan ketiga pada Set Kamera 1 dan pertama pada Set Kamera 2, sedangkan *teacher* berada di urutan pertama pada Set Kamera 1 dan terakhir pada Set Kamera 2. Kelemahan *teacher* pada gawang parsial di *predict path* berkaitan dengan bentuk *letterbox* 480 × 640 piksel, bukan dengan ambang *confidence*. Walaupun peringkat berubah antarjalur, arah dua perbandingan utama tetap sama: KD hibrida lebih tinggi daripada *supervised* pada kedua set, serta berada di bawah *teacher* pada Set Kamera 1 dan di atasnya pada Set Kamera 2. Angka *predict path* dipakai sebagai acuan utama karena paling mewakili kondisi *runtime* robot.

Kedua set kamera berasal dari satu lingkungan laboratorium dengan *frame* berurutan yang saling berkorelasi. Label awal Set Kamera 1 dibantu KD murni dan label awal Set Kamera 2 dibantu gabungan keempat model, sehingga label tidak sepenuhnya independen dari model yang diuji. Turunnya mAP50-95 pada label peninjau kedua menunjukkan bahwa mAP50-95 pada set kecil ini peka terhadap ketelitian batas kotak. Hasil pada kamera OP3 karena itu bersifat eksploratif: cukup untuk menunjukkan bahwa peringkat mAP di kamera OP3 berbeda dari peringkat di TEST, tetapi tidak cukup untuk menetapkan model terbaik di luar adegan yang diuji.

## 6.3 Pengujian *Precision*, *Recall*, dan *F1-Score*

### 6.3.1 Tujuan Pengujian

Pengujian ini menjawab rumusan masalah nomor 2, yaitu kinerja *student* KD hibrida, *student* *supervised*, dan *teacher* YOLO11n jika ditinjau dari nilai *precision*, *recall*, dan *F1-score* pada TEST dan pada citra kamera OP3.

### 6.3.2 Prosedur Pengujian

Langkah pengujian adalah sebagai berikut.

1.  Memakai *checkpoint*, citra, dan label yang sama dengan pengujian pada Subbab 6.2.

2.  Menghitung *precision* dan *recall* setiap kelas pada *confidence* \> 0,25 dan IoU 0,50, lalu merata-ratakannya antarkelas. F1 dihitung sebagai rata-rata harmonik *precision* dan *recall* rata-rata kelas.

3.  Menghitung selisih berpasangan KD hibrida penuh dikurangi *supervised* pada *seed* yang sama.

4.  Menghitung ulang F1 melalui *predict path* pada ambang *runtime*, yaitu *confidence* 0,25 dan NMS IoU 0,45 seperti pada *node* di robot.

5.  Menyapu ambang *confidence* dari 0,05 sampai 0,90 pada VAL untuk melihat perubahan *precision*, *recall*, dan F1 terhadap ambang.

6.  Pada citra kamera OP3, menghitung prediksi pada *frame* tanpa objek sebagai FP dan menyusun *confusion matrix* setiap model.

7.  Pada Set Kamera 2, menghitung ulang F1 dengan label peninjau kedua dan dengan konvensi kotak alternatif pada 52 *frame* sampel.

### 6.3.3 Hasil Pengujian

#### 6.3.3.1 Hasil *Precision*, *Recall*, dan F1 pada TEST

*Precision*, *recall*, dan F1 pada TEST disajikan pada Tabel 6.10 dan Gambar 6.10, sedangkan nilai setiap *seed* disajikan pada Tabel D.1. *Recall* keempat model hampir sama, yaitu 0,963 sampai 0,970, sehingga perbedaan F1 terutama berasal dari *precision*. *Teacher* memberi *precision* dan F1 tertinggi, diikuti *supervised*, KD hibrida penuh, dan KD murni.

**Tabel 6.10** *Precision*, *recall*, dan F1 model pada TEST

| **Model**         | ***Precision*** | ***Recall***    | **F1**          |
|-------------------|-----------------|-----------------|-----------------|
| *Teacher* YOLO11n | 0,8915          | 0,9697          | 0,9290          |
| KD hibrida penuh  | 0,8519 ± 0,0024 | 0,9698 ± 0,0007 | 0,9071 ± 0,0017 |
| *Supervised*      | 0,8609 ± 0,0032 | 0,9699 ± 0,0035 | 0,9121 ± 0,0026 |
| KD murni          | 0,7547 ± 0,0209 | 0,9631 ± 0,0017 | 0,8462 ± 0,0136 |

**Gambar 6.10** *Precision*, *recall*, dan F1 keempat model pada TEST; *error bar* menunjukkan simpangan baku tiga *seed*

Selisih berpasangan KD hibrida penuh terhadap *supervised* disajikan pada Tabel 6.11 dan Gambar 6.11. *Precision* KD hibrida lebih rendah pada ketiga pasangan *seed*, dengan rata-rata -0,0090 ± 0,0025, dan F1 lebih rendah -0,0051 ± 0,0011. Selisih *recall* berganti tanda dengan rata-rata mendekati nol.

**Tabel 6.11** Selisih berpasangan *precision*, *recall*, dan F1 KD hibrida penuh dikurangi *supervised* pada TEST

| ***Seed***     | **Δ *Precision*** | **Δ *Recall***   | **Δ F1**         |
|----------------|-------------------|------------------|------------------|
| 42             | -0,0074           | +0,0009          | -0,0038          |
| 1337           | -0,0119           | +0,0021          | -0,0058          |
| 2025           | -0,0076           | -0,0031          | -0,0057          |
| Rata-rata ± SD | -0,0090 ± 0,0025  | -0,0000 ± 0,0028 | -0,0051 ± 0,0011 |

**Gambar 6.11** Selisih berpasangan *precision*, *recall*, dan F1 KD hibrida penuh dikurangi *supervised* pada TEST untuk setiap *seed*

*Precision*, *recall*, dan F1 per kelas disajikan pada Tabel 6.12. Selisih *precision* KD hibrida terhadap *supervised* terbesar terjadi pada gawang, yaitu -0,0259, sedangkan pada bola -0,0033 dan pada robot +0,0022. F1 gawang KD hibrida juga lebih rendah 0,0193, sedangkan F1 bola dan robot hampir sama (+0,0022 dan +0,0012). Gawang adalah 72,5% anotasi TEST (Tabel B.1), sehingga penurunan *precision* gawang paling berpengaruh pada F1 keseluruhan. Sebagai pelengkap, rata-rata F1 per kelas adalah 0,9265 untuk *teacher*, 0,9107 untuk *supervised*, 0,9054 untuk KD hibrida, dan 0,8460 untuk KD murni, dengan urutan yang sama dengan F1 keseluruhan pada Tabel 6.10.

**Tabel 6.12** *Precision*, *recall*, dan F1 per kelas pada TEST

| **Kelas** | **Model**         | ***Precision*** | ***Recall***    | **F1**          |
|-----------|-------------------|-----------------|-----------------|-----------------|
| Bola      | *Teacher* YOLO11n | 0,9647          | 0,9880          | 0,9762          |
|           | KD hibrida penuh  | 0,9383 ± 0,0063 | 0,9759 ± 0,0000 | 0,9567 ± 0,0033 |
|           | *Supervised*      | 0,9415 ± 0,0107 | 0,9679 ± 0,0070 | 0,9545 ± 0,0031 |
|           | KD murni          | 0,7447 ± 0,0431 | 0,9639 ± 0,0000 | 0,8397 ± 0,0272 |
| Gawang    | *Teacher* YOLO11n | 0,7349          | 0,9380          | 0,8241          |
|           | KD hibrida penuh  | 0,7272 ± 0,0037 | 0,9336 ± 0,0022 | 0,8176 ± 0,0031 |
|           | *Supervised*      | 0,7531 ± 0,0083 | 0,9417 ± 0,0038 | 0,8369 ± 0,0059 |
|           | KD murni          | 0,7371 ± 0,0054 | 0,9311 ± 0,0029 | 0,8228 ± 0,0023 |
| Robot     | *Teacher* YOLO11n | 0,9750          | 0,9832          | 0,9791          |
|           | KD hibrida penuh  | 0,8904 ± 0,0102 | 1,0000 ± 0,0000 | 0,9420 ± 0,0057 |
|           | *Supervised*      | 0,8882 ± 0,0114 | 1,0000 ± 0,0000 | 0,9407 ± 0,0064 |
|           | KD murni          | 0,7824 ± 0,0241 | 0,9944 ± 0,0049 | 0,8756 ± 0,0167 |

F1 pada *validator path*, *predict path*, dan ambang *runtime* disajikan pada Tabel 6.13. Pada ambang yang sama, selisih F1 rata-rata kelompok *student* antarjalur paling besar 0,0024. Pada ambang *runtime*, F1 semua model naik 0,02 sampai 0,07, terutama dari *precision*: prediksi gawang yang lolos berkurang dari sekitar 640 sampai 690 menjadi sekitar 540 sampai 570 per model, sedangkan TP gawang hanya berkurang 3 sampai 13. Selisih F1 KD hibrida terhadap *supervised* menyusut dari -0,0050 pada *validator path* menjadi -0,0003 pada ambang *runtime*, sehingga F1 keduanya pada ambang *runtime* dapat dinyatakan setara.

**Tabel 6.13** F1 pada TEST menurut jalur evaluasi dan ambang

| **Kelompok**      | **F1 *validator path*** | **F1 *predict path*** | **F1 ambang *runtime*** |
|-------------------|-------------------------|-----------------------|-------------------------|
| *Teacher* YOLO11n | 0,9290                  | 0,9120                | 0,9354                  |
| KD hibrida penuh  | 0,9071                  | 0,9090                | 0,9334                  |
| *Supervised*      | 0,9121                  | 0,9098                | 0,9337                  |
| KD murni          | 0,8462                  | 0,8467                | 0,9203                  |

Pada *teacher*, F1 *predict path* turun 0,0170 dari *validator path*. Penurunan ini paling besar di antara sepuluh *checkpoint* dan berasal dari *precision*, yang turun dari 0,8915 menjadi 0,8600, sedangkan *recall* tetap sekitar 0,97. Pada rata-rata kelompok, *teacher* tetap tertinggi pada ketiga jalur. Per *checkpoint*, F1 ambang *runtime* *supervised* dan KD hibrida *seed* 1337 (0,9373) sedikit melampaui *teacher* dengan selisih kurang dari 0,004.

Kenaikan F1 pada ambang yang lebih tinggi sejalan dengan *confidence threshold sweep* pada VAL yang disajikan pada Gambar 6.12. Data *sweep* tersedia untuk KD hibrida penuh *seed* 42 dan *supervised* *seed* 1337, sehingga KD hibrida pada gambar ini bukan *checkpoint* yang digunakan di robot. Pada keempat model, *precision* naik dan *recall* turun seiring naiknya ambang, dan F1 mencapai puncak pada ambang 0,40 sampai 0,50, yaitu 0,9476 untuk *teacher*, 0,9392 untuk KD hibrida, 0,9262 untuk *supervised*, dan 0,8962 untuk KD murni. Pada ambang 0,25, F1 berada 0,008 sampai 0,029 di bawah puncak tersebut karena *precision* yang lebih rendah. Titik ambang 0,90 tidak ditampilkan karena pada ambang itu *precision* KD hibrida dan *supervised* turun ke sekitar 0,66, nilai yang sesuai dengan satu kelas tanpa prediksi dalam rata-rata kelas, bukan dengan bertambahnya prediksi yang salah.

**Gambar 6.12** *Precision*, *recall*, dan F1 VAL terhadap ambang *confidence*; garis putus-putus menandai ambang 0,25

#### 6.3.3.2 Hasil *Precision*, *Recall*, dan F1 pada Citra Kamera OP3

Hasil pada Set Kamera 1 disajikan pada Tabel 6.14. *Teacher* memberi *precision*, *recall*, dan F1 tertinggi. KD hibrida memiliki *precision* terendah (0,6836) karena menghasilkan *false detection* pada 21 dari 60 *frame* tanpa objek, sehingga F1-nya (0,6146) berada di bawah *supervised* (0,6626). KD murni memiliki *recall* terendah (0,4729). Hasil Set Kamera 2 disajikan pada Tabel 6.15. Pada konvensi kotak bagian bawah gawang, KD hibrida memberi F1 0,9950 dan mendeteksi 196 dari 200 gawang parsial, sedangkan *teacher* dan KD murni tidak mendeteksi satu pun gawang di atas *confidence* 0,25. *Supervised* mendeteksi 99 dari 100 gawang pada kondisi berjalan, tetapi 0 dari 100 pada kondisi diam. Tidak ada model yang menghasilkan FP pada 60 *frame* tanpa objek Set Kamera 2. Kolom F1 ambang *runtime* pada kedua tabel dihitung melalui *predict path* dengan NMS IoU 0,45, dan urutan modelnya sama dengan kolom F1. Ringkasan kedua set disajikan pada Gambar 6.13.

**Tabel 6.14** *Precision*, *recall*, dan F1 pada Set Kamera 1

| **Model**                | ***Precision*** | ***Recall*** | **F1** | **F1 ambang *runtime*** | ***Frame* negatif dengan FP** |
|--------------------------|-----------------|--------------|--------|-------------------------|-------------------------------|
| *Teacher* YOLO11n        | 0,8690          | 0,6833       | 0,7651 | 0,7728                  | 2/60                          |
| KD hibrida *seed* 1337   | 0,6836          | 0,5583       | 0,6146 | 0,6186                  | 21/60                         |
| *Supervised* *seed* 1337 | 0,7855          | 0,5729       | 0,6626 | 0,6626                  | 0/60                          |
| KD murni *seed* 42       | 0,7386          | 0,4729       | 0,5766 | 0,5835                  | 0/60                          |

**Tabel 6.15** *Precision*, *recall*, dan F1 pada Set Kamera 2

| **Model**                | ***Precision*** | ***Recall*** | **F1** | **F1 ambang *runtime*** | **TP gawang** |
|--------------------------|-----------------|--------------|--------|-------------------------|---------------|
| *Teacher* YOLO11n        | 0,6667          | 0,6567       | 0,6616 | 0,6616                  | 0/200         |
| KD hibrida *seed* 1337   | 0,9983          | 0,9917       | 0,9950 | 0,9958                  | 196/200       |
| *Supervised* *seed* 1337 | 1,0000          | 0,8317       | 0,9081 | 0,9081                  | 99/200        |
| KD murni *seed* 42       | 0,6667          | 0,6667       | 0,6667 | 0,6667                  | 0/200         |

**Gambar 6.13** *Precision*, *recall*, dan F1 keempat model pada kedua set kamera OP3

*Confusion matrix* Set Kamera 1 disajikan pada Gambar 6.14. Baris menunjukkan label acuan dan kolom menunjukkan prediksi pada *confidence* \> 0,25 dan IoU ≥ 0,5. Baris latar berisi prediksi yang tidak memiliki pasangan label (FP), dan kolom terlewat berisi label yang tidak terdeteksi (FN). Kesalahan KD hibrida didominasi 152 prediksi robot tanpa pasangan label, sedangkan kesalahan *teacher* didominasi 73 gawang yang tidak terdeteksi. *Supervised* dan KD murni juga menghasilkan banyak FP robot, yaitu 130 dan 116, dan melewatkan lebih banyak robot daripada KD hibrida. Seluruh model lemah pada gawang utuh: TP gawang hanya 6, 2, 21, dan 12 dari 80 untuk *teacher*, KD hibrida, *supervised*, dan KD murni.

**Gambar 6.14** *Confusion matrix* keempat model pada Set Kamera 1

*Confusion matrix* Set Kamera 2 pada Gambar 6.15 memperlihatkan bahwa bola terdeteksi seluruhnya oleh keempat model, sehingga perbedaan F1 pada set ini hampir seluruhnya berasal dari gawang parsial.

**Gambar 6.15** *Confusion matrix* keempat model pada Set Kamera 2

Kepekaan F1 terhadap pelabelan disajikan pada Tabel 6.16 dan Gambar 6.16. Berbeda dengan mAP50-95 pada Tabel 6.8, F1 setiap model identik pada label penulis dan label peninjau kedua. Pada konvensi alternatif, *supervised* memberi F1 tertinggi (0,8675), sedangkan F1 KD hibrida turun dari 0,9876 menjadi 0,6711 dengan hanya 1 dari 40 gawang lolos ambang.

**Tabel 6.16** Kepekaan F1 terhadap label pada 52 *frame* sampel Set Kamera 2

| **Model**         | **Label penulis** | **Label peninjau kedua** | **Konvensi alternatif** |
|-------------------|-------------------|--------------------------|-------------------------|
| *Teacher* YOLO11n | 0,6582            | 0,6582                   | 0,6582                  |
| KD hibrida        | 0,9876            | 0,9876                   | 0,6711                  |
| *Supervised*      | 0,9041            | 0,9041                   | 0,8675                  |
| KD murni          | 0,6667            | 0,6667                   | 0,6583                  |

**Gambar 6.16** F1 pada tiga set label Set Kamera 2

### 6.3.4 Analisis Hasil Pengujian

Pada TEST, KD hibrida penuh tidak unggul pada *precision*, *recall*, dan F1. *Recall* ketiga model hampir sama, sedangkan *precision* KD hibrida lebih rendah daripada *supervised* secara konsisten, terutama pada gawang. Dengan demikian, keunggulan KD hibrida pada mAP50-95 di Subbab 6.2 tidak disertai keunggulan pada metrik berambang tetap. Pada ambang *runtime*, F1 KD hibrida dan *supervised* setara dan keduanya sedikit di bawah *teacher*. *Threshold sweep* pada VAL menunjukkan bahwa F1 seluruh model masih dapat naik bila ambang *confidence* dinaikkan ke sekitar 0,40 sampai 0,50.

Pada citra kamera OP3, F1 model bergantung pada jenis kesalahan yang dominan di setiap set. Pada Set Kamera 1, F1 KD hibrida rendah karena FP robot dan deteksi pada *frame* tanpa objek. Pada Set Kamera 2, F1 KD hibrida tertinggi karena gawang parsial terdeteksi hampir seluruhnya, tetapi keunggulan ini hilang pada konvensi rangka utuh, sejalan dengan rendahnya TP gawang utuh KD hibrida pada Set Kamera 1. *Supervised* paling tahan terhadap perubahan konvensi. Nilai mAP50 yang tinggi pada Set Kamera 2, sementara *recall* *teacher* dan KD murni pada ambang 0,25 rendah, menunjukkan bahwa skor *confidence* tidak sebanding antarmodel, sebagaimana *confidence* jaringan saraf modern tidak selalu terkalibrasi (Guo, et al., 2017, p. 1321). Seperti pada Subbab 6.2, hasil kamera OP3 bersifat eksploratif karena berasal dari satu lingkungan dengan label yang dibantu prediksi model.

## 6.4 Pengujian Latensi dan FPS

### 6.4.1 Tujuan Pengujian

Pengujian ini menjawab rumusan masalah nomor 3, yaitu rata-rata latensi dan FPS ketiga model, yaitu KD hibrida, *supervised*, dan *teacher* YOLO11n, saat beroperasi secara *real-time* pada komputer *onboard* OP3 dalam kondisi robot diam dan berjalan. KD murni diukur sebagai pembanding pelengkap.

### 6.4.2 Prosedur Pengujian

Langkah pengujian adalah sebagai berikut.

1.  Menata bola, gawang, dan robot pada posisi bertanda di depan kamera OP3.

2.  Menjalankan *node* deteksi dengan parameter pada Tabel 5.2 dan label kondisi yang diverifikasi operator.

3.  Pada kondisi berjalan, menjalankan skrip pengujian yang memulai *gait* setelah *warm-up* 30 *frame* dan menghentikannya setelah *measurement window*.

4.  Merekam *log* per *frame* selama *measurement window* 60 detik setelah *warm-up*, tiga *repetition* untuk setiap model dan kondisi, sehingga diperoleh 24 *run* aktif.

5.  Mengaudit setiap *run* terhadap *hash* *checkpoint*, parameter, *measurement window*, *error frame*, dan data status *servo*.

6.  Menghitung rata-rata, median, dan P95 latensi serta FPS efektif menurut Persamaan 2.15 untuk setiap *run*, lalu menghitung rata-rata dan simpangan baku antar-*repetition*.

Urutan pelaksanaan berbeda dari rencana pada Subbab 3.3.5: *run* dikelompokkan per model dalam blok selama 2 dan 3 November 2026, bukan digilir per putaran, dan set *teacher* pada kondisi berjalan direkam ulang setelah objek ditata kembali. *Run* yang gagal kriteria diganti, dan *run* yang diganti tetap diarsipkan di luar perhitungan.

### 6.4.3 Hasil Pengujian

Latensi dan FPS efektif disajikan pada Tabel 6.17 dan Gambar 6.17. Pada kedua kondisi, latensi KD hibrida lebih rendah dan FPS-nya lebih tinggi daripada *teacher*. Seluruh 24 *run* memenuhi KNF-01, dengan FPS efektif terendah 9,69 FPS pada *teacher*.

**Tabel 6.17** Latensi dan FPS efektif pada OP3

| **Model**    | **Kondisi** | **Latensi (ms)** | **FPS efektif** |
|--------------|-------------|------------------|-----------------|
| *Teacher*    | Diam        | 96,24 ± 3,60     | 9,88 ± 0,31     |
| KD hibrida   | Diam        | 64,70 ± 1,92     | 13,60 ± 0,35    |
| *Supervised* | Diam        | 73,12 ± 3,27     | 12,14 ± 0,29    |
| KD murni     | Diam        | 74,09 ± 1,04     | 12,07 ± 0,05    |
| *Teacher*    | Berjalan    | 95,85 ± 1,27     | 9,87 ± 0,17     |
| KD hibrida   | Berjalan    | 71,47 ± 2,98     | 12,54 ± 0,38    |
| *Supervised* | Berjalan    | 70,80 ± 2,71     | 12,64 ± 0,52    |
| KD murni     | Berjalan    | 72,65 ± 2,55     | 12,21 ± 0,15    |

**Gambar 6.17** Latensi dan FPS efektif per model dan kondisi dari tiga *repetition*

Median dan P95 latensi disajikan pada Tabel 6.18, sedangkan nilai setiap *run* disajikan pada Tabel C.1 di Lampiran C. Median latensi semua model lebih rendah daripada rata-ratanya, dan P95 sekitar 2,3 sampai 3,2 kali median. Distribusi latensi karena itu menjulur ke kanan, yaitu sebagian kecil *frame* jauh lebih lambat daripada *frame* pada umumnya. Median KD hibrida 50,46 ms saat diam dan 59,18 ms saat berjalan, dibandingkan dengan 77,76 dan 77,03 ms pada *teacher*. P95 ketiga *student* hampir sama, yaitu 160,48 sampai 163,91 ms, dan berada sekitar 17 sampai 21 ms di bawah P95 *teacher*. Penyebab *frame* yang lambat tidak diuraikan lebih lanjut pada penelitian ini.

**Tabel 6.18** Median dan P95 latensi pada OP3 (ms)

| **Model**    | **Kondisi** | **Median latensi** | **P95 latensi** |
|--------------|-------------|--------------------|-----------------|
| *Teacher*    | Diam        | 77,76 ± 1,13       | 181,26 ± 0,91   |
| KD hibrida   | Diam        | 50,46 ± 1,59       | 160,62 ± 2,72   |
| *Supervised* | Diam        | 58,72 ± 1,23       | 160,61 ± 1,82   |
| KD murni     | Diam        | 59,22 ± 0,24       | 163,91 ± 0,90   |
| *Teacher*    | Berjalan    | 77,03 ± 1,68       | 180,69 ± 0,61   |
| KD hibrida   | Berjalan    | 59,18 ± 2,33       | 160,48 ± 1,45   |
| *Supervised* | Berjalan    | 57,18 ± 2,44       | 161,17 ± 1,03   |
| KD murni     | Berjalan    | 57,85 ± 1,13       | 161,34 ± 1,88   |

Perilaku latensi dan FPS selama *measurement window* disajikan pada Gambar 6.18. Setiap garis adalah rata-rata tiga *repetition* untuk setiap selang 2 detik, dan pita menunjukkan rentang nilai terendah sampai tertinggi tiga *repetition*. Latensi *teacher* berada di atas ketiga *student* hampir sepanjang *measurement window* pada kedua kondisi, dan FPS seluruh model tetap di atas 8 FPS. Tidak tampak kenaikan latensi yang terus-menerus dari awal sampai akhir *measurement window*. Fluktuasi antarselang yang dapat mencapai 10 sampai 20 ms lebih besar daripada selisih rata-rata antar-*student*.

**Gambar 6.18** Latensi dan FPS efektif per selang 2 detik selama *measurement window* 60 detik

Rincian latensi per tahap disajikan pada Tabel 6.19 dan Gambar 6.19, dihitung dari seluruh *frame* gabungan tiga *run* sehingga dapat berbeda sedikit dari rata-rata tiga rata-rata *run* pada Tabel 6.17. Kolom sisa dihitung per *frame* sebagai latensi *callback* keseluruhan dikurangi ketiga tahap yang dilaporkan Ultralytics. Sisa ini mencakup waktu untuk mengonversi pesan kamera, memanggil pelacak, membentuk dan melakukan *publish* hasil deteksi, menggambar dan melakukan *publish* *preview*, serta menulis CSV deteksi, sehingga bukan waktu pelacak saja.

**Tabel 6.19** Rincian rata-rata latensi per tahap (ms)

| **Model**    | **Kondisi** | **Prapemrosesan** | **Inferensi** | **Pascapemrosesan** | **Sisa** | **Keseluruhan** |
|--------------|-------------|-------------------|---------------|---------------------|----------|-----------------|
| *Teacher*    | Diam        | 5,43              | 76,55         | 0,83                | 13,37    | 96,17           |
| KD hibrida   | Diam        | 4,13              | 45,28         | 0,85                | 14,42    | 64,67           |
| *Supervised* | Diam        | 5,57              | 53,14         | 0,95                | 13,40    | 73,06           |
| KD murni     | Diam        | 5,35              | 53,02         | 0,97                | 14,75    | 74,09           |
| *Teacher*    | Berjalan    | 5,69              | 76,79         | 0,84                | 12,51    | 95,84           |
| KD hibrida   | Berjalan    | 4,98              | 51,06         | 0,95                | 14,42    | 71,41           |
| *Supervised* | Berjalan    | 5,05              | 50,13         | 0,96                | 14,59    | 70,73           |
| KD murni     | Berjalan    | 5,28              | 52,57         | 0,96                | 13,83    | 72,63           |

**Gambar 6.19** Komposisi latensi rata-rata per tahap untuk setiap model dan kondisi

### 6.4.4 Analisis Hasil Pengujian

Latensi KD hibrida lebih rendah daripada *teacher* pada kedua kondisi, yaitu 1,49 kali lebih cepat saat diam dan 1,34 kali saat berjalan, dengan FPS efektif 1,38 dan 1,27 kali *teacher*. Selisih ini terutama berasal dari tahap inferensi (45,28 berbanding 76,55 ms saat diam), sesuai dengan GFLOPs *student* yang 37% dari *teacher*, sedangkan tahap sisa hampir sama pada semua model. Latensi *teacher* praktis tidak berubah dari kondisi diam ke kondisi berjalan, sedangkan latensi KD hibrida naik 6,77 ms. Ketiga *student* berarsitektur identik, tetapi rata-rata waktu inferensinya berbeda sampai sekitar 8 ms dan urutannya berganti antarkondisi. Selisih antar-*student*, termasuk kenaikan KD hibrida saat berjalan, karena itu lebih mungkin berasal dari hari dan urutan pengukuran daripada dari fungsi objektif pelatihan, sehingga klaim kecepatan yang sah hanya *student* dibandingkan dengan *teacher*.

Hasil ini bersifat deskriptif. Urutan *run* berbentuk blok lintas hari, suhu dan pencahayaan tidak dikendalikan secara kuantitatif, dan beberapa bukti fisik seperti tangkapan *preview* tepat setelah *measurement window* tidak lengkap untuk semua *run*. Sesuai anjuran pelaporan kinerja yang nondeterministik (Hoefler dan Belli, 2015), hasil dilaporkan per *repetition* beserta sebarannya, bukan sebagai satu angka tunggal.

## 6.5 Pengujian Penggunaan CPU dan RAM

### 6.5.1 Tujuan Pengujian

Pengujian ini menjawab rumusan masalah nomor 4, yaitu penggunaan CPU dan RAM ketiga model, yaitu KD hibrida, *supervised*, dan *teacher* YOLO11n, pada komputer *onboard* OP3. RAM diukur sebagai RSS proses *node* deteksi. KD murni diukur sebagai pembanding pelengkap.

### 6.5.2 Prosedur Pengujian

Langkah pengujian adalah sebagai berikut.

1.  Menggunakan 24 *run* aktif yang sama dengan pengujian pada Subbab 6.4.

2.  Mencatat penggunaan CPU dan RSS proses *node* deteksi pada setiap *frame*. CPU dinyatakan sebagai persentase terhadap satu CPU logis, sehingga dapat melebihi 100% pada proses yang menggunakan banyak *thread*.

3.  Menghitung rata-rata setiap *run*, lalu rata-rata dan simpangan baku antar-*repetition*.

4.  Untuk menelusuri penggunaan CPU, memutar ulang (*replay*) proses deteksi secara *offline* pada komputer *onboard* dengan 300 *frame* dari Set Kamera 2, tanpa ROS dan kamera, dengan satu pengulangan untuk setiap varian. Varian yang diuji adalah pelacakan dan *preview* aktif, tanpa pelacakan, OpenCV dibatasi satu *thread*, pelacakan tanpa kompensasi gerak global (GMC), dan OpenBLAS dibatasi satu *thread*.

### 6.5.3 Hasil Pengujian

Penggunaan CPU dan RSS disajikan pada Tabel 6.20 dan Gambar 6.20, dan nilai setiap *run* disajikan pada Tabel C.1. Angka dalam kurung adalah persentase terhadap 16 CPU logis komputer *onboard*. CPU proses semua model berada di sekitar 1.300% satu CPU logis, atau 81 sampai 84% dari 16 CPU logis. Dibanding KD hibrida, CPU proses *teacher* lebih tinggi sekitar 30 sampai 33 poin persentase satu CPU logis dan RSS-nya lebih besar sekitar 12 sampai 16 MiB.

**Tabel 6.20** Penggunaan CPU proses dan RSS pada OP3

| **Model**    | **Kondisi** | **CPU proses (%)**     | **RSS (MiB)** |
|--------------|-------------|------------------------|---------------|
| *Teacher*    | Diam        | 1.338,90 ± 9,65 (83,7) | 370,58 ± 1,29 |
| KD hibrida   | Diam        | 1.305,97 ± 4,91 (81,6) | 358,87 ± 1,24 |
| *Supervised* | Diam        | 1.299,18 ± 3,32 (81,2) | 355,93 ± 3,32 |
| KD murni     | Diam        | 1.300,21 ± 2,44 (81,3) | 356,97 ± 5,92 |
| *Teacher*    | Berjalan    | 1.333,54 ± 4,08 (83,3) | 372,42 ± 5,11 |
| KD hibrida   | Berjalan    | 1.303,77 ± 3,88 (81,5) | 356,31 ± 2,09 |
| *Supervised* | Berjalan    | 1.301,13 ± 6,03 (81,3) | 359,16 ± 4,76 |
| KD murni     | Berjalan    | 1.295,65 ± 1,35 (81,0) | 360,18 ± 4,69 |

**Gambar 6.20** Penggunaan CPU proses dan RSS per model dan kondisi dari tiga *repetition*

*Node* mencatat 4 *thread* operasi dan 2 *thread* antaroperasi PyTorch, tetapi penggunaan CPU proses setara dengan sekitar 13 CPU logis. Hasil *replay* untuk menelusuri selisih ini disajikan pada Tabel 6.21 dan Gambar 6.21.

**Tabel 6.21** Penggunaan CPU proses pada *replay offline* per varian

| **Varian**                     | ***Teacher* CPU (%)** | ***Teacher* *frame*/detik** | **KD hibrida CPU (%)** | **KD hibrida *frame*/detik** |
|--------------------------------|-----------------------|-----------------------------|------------------------|------------------------------|
| Pelacakan dan *preview*        | 977,1                 | 16,30                       | 965,7                  | 24,61                        |
| Tanpa pelacakan                | 399,7                 | 27,13                       | 400,0                  | 56,10                        |
| Pelacakan, OpenCV 1 *thread*   | 970,4                 | 16,18                       | 958,1                  | 27,46                        |
| Pelacakan tanpa GMC            | 1.013,8               | 18,21                       | 1.012,3                | 33,34                        |
| Pelacakan, OpenBLAS 1 *thread* | 399,5                 | 21,40                       | 399,3                  | 35,24                        |

**Gambar 6.21** Penggunaan CPU proses dan laju *replay offline* per varian

Tabel 6.21 memperlihatkan dua hal. Pertama, pada *replay* awal, inisialisasi *backend* CPU Ultralytics pada inferensi pertama mengubah jumlah *thread* operasi PyTorch dari 4 menjadi 8, sehingga *replay* utama mengembalikan dan memverifikasi nilai 4 dan 2 pada setiap *frame*. Angka 4 dan 2 pada *metadata* *run* dicatat sebelum inferensi pertama, sehingga belum membuktikan jumlah *thread* selama *run*. Kedua, dengan PyTorch 4 dan 2, penggunaan CPU sekitar 970% ketika pelacakan aktif dan turun menjadi sekitar 400% ketika pelacakan dimatikan atau ketika pustaka OpenBLAS dibatasi satu *thread*. OpenBLAS bawaan teramati memakai 16 *thread*, sedangkan membatasi OpenCV satu *thread* atau mematikan GMC tidak menurunkan penggunaan CPU. Pada varian yang sama, penggunaan CPU *teacher* dan KD hibrida hampir sama, tetapi laju *replay* KD hibrida 1,5 sampai 2,1 kali *teacher*.

### 6.5.4 Analisis Hasil Pengujian

Pada pengukuran *live*, CPU dan RSS tidak membedakan efisiensi model secara jelas. Selisih CPU KD hibrida terhadap *teacher* hanya sekitar 2 sampai 3% dari nilainya, dan selisih RSS sekitar 3 sampai 4%. Hasil *replay* menunjukkan kombinasi pelacakan dan OpenBLAS sebagai faktor besar penggunaan CPU, sedangkan model menentukan berapa *frame* yang selesai diproses dengan beban CPU tersebut. Dengan kata lain, efisiensi KD hibrida terlihat pada jumlah *frame* per satuan beban CPU, bukan pada persentase CPU itu sendiri. Jumlah *thread* PyTorch dan OpenBLAS pada 24 *run* tidak terekam, sehingga penyebab pasti penggunaan CPU pada *run* tersebut belum dapat dipastikan. CPU dan RSS juga hanya mencerminkan proses detektor, bukan beban total robot.

## 6.6 Pengujian Tambahan

### 6.6.1 Tujuan Pengujian

Pengujian tambahan bertujuan memeriksa dua hal yang dapat mengubah pilihan model KD, yaitu ukuran *teacher* dan bentuk fungsi objektif KD hibrida. Pengujian ini tidak mengganti model utama yang diuji pada robot.

### 6.6.2 Prosedur Pengujian

Langkah pengujian adalah sebagai berikut.

1.  Melatih ulang *teacher* YOLO11n dan YOLO11s dengan pengaturan yang sama, lalu melatih *student* KD hibrida penuh dari masing-masing *teacher* dengan tiga *seed*.

2.  Menguji delapan konfigurasi perbaikan fungsi objektif KD hibrida dengan *seed* 42, lalu mengulang konfigurasi terbaik dengan tiga *seed*.

3.  Membandingkan seluruh hasil pada VAL dengan aturan seleksi yang ditetapkan sebelum pelatihan.

### 6.6.3 Hasil Pengujian

Hasil ablasi ukuran *teacher* disajikan pada Tabel 6.22, dan nilai setiap *seed* disajikan pada Gambar 6.22. *Teacher* YOLO11s lebih akurat daripada YOLO11n, tetapi *student* yang dilatih dari YOLO11s tidak lebih baik. Pada ketiga *seed*, *student* dari YOLO11s lebih rendah 0,0002 sampai 0,0014 daripada *student* dari YOLO11n dengan *seed* yang sama.

**Tabel 6.22** Ablasi ukuran *teacher* pada VAL

| ***Teacher***           | **mAP50-95 *teacher*** | **mAP50-95 *student* (rata-rata ± SD)** |
|-------------------------|------------------------|-----------------------------------------|
| YOLO11n (dilatih ulang) | 0,7760                 | 0,7482 ± 0,0003                         |
| YOLO11s (dilatih ulang) | 0,7843                 | 0,7473 ± 0,0003                         |

**Gambar 6.22** mAP50-95 VAL *student* KD hibrida penuh per *seed* menurut ukuran *teacher*; garis titik-titik menunjukkan rata-rata

Pada perbaikan fungsi objektif, konfigurasi terbaik adalah divergensi KL pada distribusi DFL tanpa pembobotan *anchor*. Dengan tiga *seed*, konfigurasi ini memberi mAP50-95 VAL 0,7475 ± 0,0013 dibandingkan dengan 0,7505 ± 0,0018 pada KD hibrida penuh, dengan F1 0,9251 berbanding 0,9205.

### 6.6.4 Analisis Hasil Pengujian

Selisih *student* dari kedua *teacher* jauh lebih kecil daripada selisih KD hibrida dan *supervised* pada VAL (0,0297), sehingga kedua *teacher* dapat dianggap memberi hasil yang setara. *Teacher* yang lebih akurat tidak otomatis menghasilkan *student* yang lebih akurat, sejalan dengan temuan bahwa *teacher* yang lebih besar tidak selalu menjadi *teacher* yang lebih baik (Cho dan Hariharan, 2019). Perbaikan fungsi objektif menaikkan F1 tetapi menurunkan mAP50-95, dan konfigurasi ini tidak memenuhi aturan seleksi yang ditetapkan sebelum pelatihan. Karena itu, KD hibrida penuh dengan *teacher* YOLO11n tetap menjadi model KD utama.

## 6.7 Evaluasi Keseluruhan

Sistem deteksi berbasis ROS 2 berhasil berjalan pada komputer *onboard* OP3, dan seluruh kasus uji kebutuhan lulus, dengan catatan pada pelacakan dan *preview*. Hasil Subbab 6.2 sampai Subbab 6.5 karena itu berasal dari sistem yang telah diverifikasi berjalan sesuai kebutuhan, meskipun penilaian kasus uji dilakukan secara retrospektif dari *log* yang ada.

Untuk rumusan masalah nomor 1, KD hibrida penuh lebih baik daripada *supervised* pada mAP50-95 TEST dan konsisten pada ketiga pasangan *seed*, tetapi keunggulan itu tidak berpindah begitu saja ke kamera OP3. Untuk rumusan masalah nomor 2, KD hibrida tidak unggul pada *precision*, *recall*, dan F1; pada ambang *runtime*, F1-nya setara dengan *supervised*. Model yang dipilih dari VAL dan TEST karena itu belum tentu menjadi model terbaik pada adegan robot, dan pemilihan model untuk pemakaian di robot memerlukan evaluasi pada citra kamera robot itu sendiri.

Untuk rumusan masalah nomor 3, KD hibrida dan *supervised* lebih cepat daripada *teacher* pada kedua kondisi robot, latensi kedua *student* berdekatan dengan urutan yang berganti antarkondisi, dan seluruh model memenuhi KNF-01. Untuk rumusan masalah nomor 4, CPU dan RSS proses tidak membedakan model secara jelas, karena penggunaan CPU didominasi pelacakan dan OpenBLAS. Keuntungan *runtime* yang terukur berasal dari ukuran *student* dibandingkan dengan *teacher*; KD menentukan mutu deteksi, bukan kecepatan.

Beberapa ancaman terhadap validitas membatasi kesimpulan. TEST pernah dibuka sebelum KD hibrida dirancang, nama sumber yang sama ditemukan di lebih dari satu bagian himpunan data (Tabel B.2), dan asal-usul himpunan data pelatihan *teacher* utama tidak terdokumentasi lengkap. Set kamera OP3 berasal dari satu lingkungan dengan label yang dibantu prediksi model. Pengukuran *runtime* dilakukan dalam blok lintas hari. Jumlah *seed* dan *repetition* yang masing-masing tiga hanya mendukung analisis deskriptif (Bouthillier, et al., 2021).
