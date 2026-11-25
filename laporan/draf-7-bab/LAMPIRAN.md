# LAMPIRAN

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v30 (25 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

## LAMPIRAN A KONFIGURASI PELATIHAN

Lampiran ini memuat konfigurasi pelatihan yang sama untuk seluruh varian *student* pada Ultralytics 8.4.130. Nilainya disajikan pada Tabel A.1 sampai Tabel A.3. Parameter lain yang tidak tercantum memakai nilai bawaan Ultralytics 8.4.130.

### A.1 Hiperparameter Optimisasi dan *Loss*

**Tabel A.1** Hiperparameter optimisasi dan *loss*

| **Parameter**   | **Nilai**      | **Keterangan**                                             |
|-----------------|----------------|------------------------------------------------------------|
| epochs          | 100            | Jumlah *epoch*                                             |
| batch           | 16             | Ukuran *batch*                                             |
| imgsz           | 640            | Ukuran sisi citra masukan dalam piksel                     |
| optimizer       | AdamW          | *Optimizer*                                                |
| lr0             | 0,001          | Laju belajar awal                                          |
| lrf             | 0,01           | Faktor laju belajar akhir                                  |
| momentum        | 0,937          | *Momentum*                                                 |
| weight_decay    | 0,0005         | *Weight decay*                                             |
| warmup_epochs   | 3              | Jumlah *epoch warmup*                                      |
| warmup_momentum | 0,8            | *Momentum* awal selama *warmup*                            |
| warmup_bias_lr  | 0,1            | Laju belajar awal bias selama *warmup*                     |
| box             | 7,5            | Bobot *loss* kotak dalam $L_{\text{det}}$                  |
| cls             | 0,5            | Bobot *loss* kelas dalam $L_{\text{det}}$                  |
| dfl             | 1,5            | Bobot DFL dalam $L_{\text{det}}$                           |
| amp             | false          | AMP dimatikan                                              |
| patience        | 30             | Batas *epoch* tanpa perbaikan sebelum pelatihan dihentikan |
| pretrained      | false          | *Student* diinisialisasi acak                              |
| deterministic   | true           | Mode deterministik diaktifkan                              |
| seed            | 42, 1337, 2025 | Satu *run* per *seed*                                      |
| iou             | 0,7            | Ambang IoU NMS saat validasi                               |
| max_det         | 300            | Jumlah deteksi maksimum per citra                          |

### A.2 Augmentasi Data

**Tabel A.2** Augmentasi data

| **Parameter**               | **Nilai** | **Keterangan**                                |
|-----------------------------|-----------|-----------------------------------------------|
| hsv_h                       | 0,015     | Rentang perubahan *hue*                       |
| hsv_s                       | 0,7       | Rentang perubahan saturasi                    |
| hsv_v                       | 0,4       | Rentang perubahan kecerahan                   |
| translate                   | 0,1       | Rentang pergeseran citra                      |
| scale                       | 0,5       | Rentang perubahan skala citra                 |
| fliplr                      | 0,5       | Peluang pencerminan horizontal                |
| flipud                      | 0         | Pencerminan vertikal tidak dipakai            |
| degrees, shear, perspective | 0         | Rotasi, geseran, dan perspektif tidak dipakai |
| mosaic                      | 1,0       | Peluang augmentasi *mosaic*                   |
| close_mosaic                | 10        | *Mosaic* dimatikan pada 10 *epoch* terakhir   |
| mixup, cutmix, copy_paste   | 0         | Tidak dipakai                                 |

### A.3 Parameter Distilasi

**Tabel A.3** Parameter distilasi

| **Parameter**                 | **KD murni**      | **KD hibrida penuh** | **KD hibrida fitur**                       |
|-------------------------------|-------------------|----------------------|--------------------------------------------|
| *Loss* label $L_{\text{det}}$ | Tidak             | Ya                   | Ya                                         |
| Bobot fitur $\lambda_{f}$     | 1,0               | 1,0                  | 6,0 (dis)                                  |
| Bobot kotak $\lambda_{b}$     | 1,0               | 1,0                  | 0                                          |
| Bobot kelas $\lambda_{c}$     | 1,0               | 1,0                  | 0                                          |
| Temperatur $T$                | 2,0               | 2,0                  | Tidak berpengaruh karena $\lambda_{c} = 0$ |
| *Teacher*                     | YOLO11n FP32 beku | YOLO11n FP32 beku    | YOLO11n FP32 beku                          |

## LAMPIRAN B RINCIAN HIMPUNAN DATA

Lampiran ini merinci jumlah citra dan anotasi setiap bagian himpunan data berdasarkan audit sebelum pelatihan, seperti pada Tabel B.1 dan Tabel B.2.

### B.1 Distribusi Anotasi per Kelas

**Tabel B.1** Distribusi anotasi per kelas

| **Bagian** | **Citra** | **Anotasi** | **Bola** | **Gawang** | **Robot** | **Citra tanpa objek** |
|------------|-----------|-------------|----------|------------|-----------|-----------------------|
| TRAIN      | 4.600     | 6.143       | 881      | 3.662      | 1.600     | 4                     |
| VAL        | 1.213     | 1.525       | 182      | 1.048      | 295       | 2                     |
| TEST       | 592       | 734         | 83       | 532        | 119       | 1                     |
| Jumlah     | 6.405     | 8.402       | 1.146    | 5.242      | 2.014     | 7                     |

Kelas gawang mendominasi setiap bagian, yaitu sekitar 59,6% anotasi TRAIN dan 72,5% anotasi TEST. Jumlah anotasi bola dan robot pada TEST juga terbatas, sehingga metrik per kelas ikut dilaporkan.

### B.2 Nama Sumber Bersama Antarbagian

**Tabel B.2** Nama sumber bersama antarbagian

| **Pasangan bagian** | **Nama sumber bersama** |
|---------------------|-------------------------|
| TRAIN dan VAL       | 326                     |
| TRAIN dan TEST      | 176                     |
| VAL dan TEST        | 155                     |

Nama sumber diperoleh dengan membuang akhiran .rf.\<hash\> dari nama berkas Roboflow. Jumlah ini adalah irisan nama dasar, bukan jumlah citra yang pasti duplikat, dan perbandingan piksel tidak menemukan pasangan citra yang identik.

## LAMPIRAN C HASIL *RUNTIME* SETIAP *RUN*

Lampiran ini memuat hasil setiap *run* pengujian *runtime* pada Subbab 6.4 dan Subbab 6.5. Latensi dihitung dari seluruh *frame* dalam *measurement window* setelah *warm-up*, FPS efektif menurut Persamaan 2.15, CPU sebagai persentase satu CPU logis, dan RSS sebagai rata-rata selama *measurement window*.

**Tabel C.1** Hasil *runtime* setiap *run*

<table>
<colgroup>
<col style="width: 12%" />
<col style="width: 10%" />
<col style="width: 14%" />
<col style="width: 10%" />
<col style="width: 10%" />
<col style="width: 9%" />
<col style="width: 10%" />
<col style="width: 11%" />
<col style="width: 10%" />
</colgroup>
<thead>
<tr class="header">
<th><strong>Model</strong></th>
<th><strong>Kondisi</strong></th>
<th><em><strong>Repetition</strong></em></th>
<th><p><strong>Latensi</strong></p>
<p><strong>rata-rata</strong></p>
<p><strong>(ms)</strong></p></th>
<th><p><strong>Median</strong></p>
<p><strong>(ms)</strong></p></th>
<th><p><strong>P95</strong></p>
<p><strong>(ms)</strong></p></th>
<th><p><strong>FPS</strong></p>
<p><strong>efektif</strong></p></th>
<th><strong>CPU (%)</strong></th>
<th><p><strong>RSS</strong></p>
<p><strong>(MiB)</strong></p></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><em>Teacher</em></td>
<td>Diam</td>
<td>1</td>
<td>98,91</td>
<td>76,48</td>
<td>180,21</td>
<td>9,72</td>
<td>1.329,91</td>
<td>370,03</td>
</tr>
<tr class="even">
<td><em>Teacher</em></td>
<td>Diam</td>
<td>2</td>
<td>92,15</td>
<td>78,59</td>
<td>181,84</td>
<td>10,24</td>
<td>1.349,11</td>
<td>369,66</td>
</tr>
<tr class="odd">
<td><em>Teacher</em></td>
<td>Diam</td>
<td>3</td>
<td>97,67</td>
<td>78,19</td>
<td>181,73</td>
<td>9,69</td>
<td>1.337,67</td>
<td>372,06</td>
</tr>
<tr class="even">
<td>KD hibrida</td>
<td>Diam</td>
<td>1</td>
<td>66,82</td>
<td>52,26</td>
<td>157,52</td>
<td>13,20</td>
<td>1.303,85</td>
<td>358,63</td>
</tr>
<tr class="odd">
<td>KD hibrida</td>
<td>Diam</td>
<td>2</td>
<td>63,08</td>
<td>49,28</td>
<td>161,77</td>
<td>13,75</td>
<td>1.302,47</td>
<td>357,76</td>
</tr>
<tr class="even">
<td>KD hibrida</td>
<td>Diam</td>
<td>3</td>
<td>64,21</td>
<td>49,83</td>
<td>162,58</td>
<td>13,85</td>
<td>1.311,58</td>
<td>360,21</td>
</tr>
<tr class="odd">
<td><em>Supervised</em></td>
<td>Diam</td>
<td>1</td>
<td>74,48</td>
<td>58,74</td>
<td>161,82</td>
<td>12,00</td>
<td>1.300,69</td>
<td>354,96</td>
</tr>
<tr class="even">
<td><em>Supervised</em></td>
<td>Diam</td>
<td>2</td>
<td>69,39</td>
<td>57,48</td>
<td>158,52</td>
<td>12,47</td>
<td>1.295,37</td>
<td>359,63</td>
</tr>
<tr class="odd">
<td><em>Supervised</em></td>
<td>Diam</td>
<td>3</td>
<td>75,48</td>
<td>59,95</td>
<td>161,49</td>
<td>11,94</td>
<td>1.301,47</td>
<td>353,19</td>
</tr>
<tr class="even">
<td>KD murni</td>
<td>Diam</td>
<td>1</td>
<td>72,90</td>
<td>59,49</td>
<td>164,94</td>
<td>12,13</td>
<td>1.297,43</td>
<td>350,73</td>
</tr>
<tr class="odd">
<td>KD murni</td>
<td>Diam</td>
<td>2</td>
<td>74,60</td>
<td>59,04</td>
<td>163,53</td>
<td>12,04</td>
<td>1.301,98</td>
<td>357,65</td>
</tr>
<tr class="even">
<td>KD murni</td>
<td>Diam</td>
<td>3</td>
<td>74,78</td>
<td>59,13</td>
<td>163,25</td>
<td>12,05</td>
<td>1.301,21</td>
<td>362,52</td>
</tr>
<tr class="odd">
<td><em>Teacher</em></td>
<td>Berjalan</td>
<td>1</td>
<td>96,41</td>
<td>77,00</td>
<td>180,86</td>
<td>9,80</td>
<td>1.329,97</td>
<td>371,36</td>
</tr>
<tr class="even">
<td><em>Teacher</em></td>
<td>Berjalan</td>
<td>2</td>
<td>96,75</td>
<td>78,73</td>
<td>181,19</td>
<td>9,75</td>
<td>1.332,64</td>
<td>367,92</td>
</tr>
<tr class="odd">
<td><em>Teacher</em></td>
<td>Berjalan</td>
<td>3</td>
<td>94,40</td>
<td>75,37</td>
<td>180,01</td>
<td>10,07</td>
<td>1.337,99</td>
<td>377,97</td>
</tr>
<tr class="even">
<td>KD hibrida</td>
<td>Berjalan</td>
<td>1</td>
<td>68,37</td>
<td>56,70</td>
<td>158,92</td>
<td>12,87</td>
<td>1.299,77</td>
<td>358,13</td>
</tr>
<tr class="odd">
<td>KD hibrida</td>
<td>Berjalan</td>
<td>2</td>
<td>71,72</td>
<td>59,52</td>
<td>160,74</td>
<td>12,64</td>
<td>1.307,51</td>
<td>354,03</td>
</tr>
<tr class="even">
<td>KD hibrida</td>
<td>Berjalan</td>
<td>3</td>
<td>74,32</td>
<td>61,31</td>
<td>161,78</td>
<td>12,12</td>
<td>1.304,03</td>
<td>356,76</td>
</tr>
<tr class="odd">
<td><em>Supervised</em></td>
<td>Berjalan</td>
<td>1</td>
<td>71,65</td>
<td>56,90</td>
<td>161,84</td>
<td>12,36</td>
<td>1.296,41</td>
<td>361,63</td>
</tr>
<tr class="even">
<td><em>Supervised</em></td>
<td>Berjalan</td>
<td>2</td>
<td>67,77</td>
<td>54,89</td>
<td>159,98</td>
<td>13,23</td>
<td>1.307,93</td>
<td>362,18</td>
</tr>
<tr class="odd">
<td><em>Supervised</em></td>
<td>Berjalan</td>
<td>3</td>
<td>72,99</td>
<td>59,74</td>
<td>161,70</td>
<td>12,31</td>
<td>1.299,04</td>
<td>353,68</td>
</tr>
<tr class="even">
<td>KD murni</td>
<td>Berjalan</td>
<td>1</td>
<td>74,75</td>
<td>58,63</td>
<td>162,51</td>
<td>12,10</td>
<td>1.296,29</td>
<td>365,05</td>
</tr>
<tr class="odd">
<td>KD murni</td>
<td>Berjalan</td>
<td>2</td>
<td>73,39</td>
<td>58,37</td>
<td>162,35</td>
<td>12,17</td>
<td>1.296,56</td>
<td>355,69</td>
</tr>
<tr class="even">
<td>KD murni</td>
<td>Berjalan</td>
<td>3</td>
<td>69,82</td>
<td>56,56</td>
<td>159,18</td>
<td>12,38</td>
<td>1.294,10</td>
<td>359,81</td>
</tr>
</tbody>
</table>

## LAMPIRAN D AKURASI SETIAP *SEED* PADA TEST

Lampiran ini memuat akurasi setiap *checkpoint* pada 592 citra TEST yang diringkas pada Tabel 6.3 dan Tabel 6.10. *Teacher* diwakili satu *checkpoint*. *Precision*, *recall*, dan F1 dihitung pada *confidence* \> 0,25 dan IoU 0,50 lewat *validator path*.

**Tabel D.1** Akurasi setiap *seed* pada TEST

| **Model**         | ***Seed*** | **mAP50** | **mAP50-95** | ***Precision*** | ***Recall*** | **F1** |
|-------------------|------------|-----------|--------------|-----------------|--------------|--------|
| *Teacher* YOLO11n | \-         | 0,9642    | 0,7800       | 0,8915          | 0,9697       | 0,9290 |
| KD hibrida penuh  | 42         | 0,9592    | 0,7447       | 0,8498          | 0,9694       | 0,9057 |
| KD hibrida penuh  | 1337       | 0,9577    | 0,7468       | 0,8513          | 0,9694       | 0,9065 |
| KD hibrida penuh  | 2025       | 0,9579    | 0,7492       | 0,8546          | 0,9707       | 0,9089 |
| *Supervised*      | 42         | 0,9585    | 0,7203       | 0,8573          | 0,9685       | 0,9095 |
| *Supervised*      | 1337       | 0,9578    | 0,7265       | 0,8632          | 0,9673       | 0,9123 |
| *Supervised*      | 2025       | 0,9639    | 0,7208       | 0,8622          | 0,9738       | 0,9146 |
| KD murni          | 42         | 0,9481    | 0,6744       | 0,7451          | 0,9613       | 0,8395 |
| KD murni          | 1337       | 0,9403    | 0,6531       | 0,7404          | 0,9632       | 0,8372 |
| KD murni          | 2025       | 0,9455    | 0,6616       | 0,7787          | 0,9648       | 0,8618 |

## LAMPIRAN E DAFTAR ISTILAH DAN SINGKATAN

Lampiran ini memuat istilah dan singkatan yang dipakai dalam naskah beserta keterangannya, diurutkan menurut abjad.

Tabel E.1 Daftar istilah dan singkatan

| **Istilah atau singkatan** | **Keterangan**                                                                                |
|----------------------------|-----------------------------------------------------------------------------------------------|
| *Anchor point*             | Setiap posisi pada peta keluaran detektor tempat model membuat prediksi                       |
| AP                         | *Average precision*, luas di bawah kurva *precision*-*recall* untuk satu kelas                |
| BCE                        | *Binary cross-entropy*, *loss* untuk keputusan ada atau tidaknya satu kelas                   |
| BoT-SORT                   | Algoritme pelacakan objek yang dipakai *node* deteksi untuk memberi ID                        |
| *Checkpoint*               | Berkas bobot model hasil pelatihan                                                            |
| CNN                        | *Convolutional neural network*, jaringan saraf konvolusional                                  |
| *Confidence*               | Skor keyakinan model terhadap satu deteksi                                                    |
| *Confusion matrix*         | Tabel yang memasangkan kelas label dengan kelas prediksi model                                |
| CPU                        | *Central processing unit*                                                                     |
| CSV                        | *Comma-separated values*, format berkas teks berbentuk tabel                                  |
| DDS                        | *Data Distribution Service*, standar komunikasi yang mendasari ROS 2                          |
| DFL                        | *Distribution focal loss*, *loss* regresi kotak berbentuk distribusi pada YOLO11              |
| *Edge device*              | Perangkat berdaya komputasi terbatas tempat model dijalankan secara lokal                     |
| *Epoch*                    | Satu putaran pelatihan atas seluruh data latih                                                |
| *Error bar*                | Garis pada grafik yang menunjukkan sebaran nilai, di sini simpangan baku                      |
| *Error frame*              | *Frame* yang gagal diproses oleh *node* deteksi                                               |
| F1                         | *F1-score*, rata-rata harmonik *precision* dan *recall*                                       |
| FN                         | *False negative*, objek berlabel yang tidak terdeteksi                                        |
| FP                         | *False positive*, deteksi yang tidak memiliki pasangan label                                  |
| FP32                       | Bilangan titik mengambang 32 bit                                                              |
| FPS                        | *Frame per second*, jumlah *frame* yang diproses setiap detik                                 |
| *Frame*                    | Satu citra dari aliran kamera                                                                 |
| GFLOPs                     | Miliar operasi titik mengambang untuk satu kali inferensi                                     |
| GMC                        | *Global motion compensation*, kompensasi gerak kamera pada pelacak                            |
| GPU                        | *Graphics processing unit*                                                                    |
| *Ground truth*             | Kotak dan kelas acuan dari label himpunan data                                                |
| ID                         | Nomor identitas objek yang diberikan pelacak                                                  |
| IDF1                       | *ID F1 score*, metrik pelacakan yang menilai konsistensi identitas objek                      |
| INT8                       | Bilangan bulat 8 bit                                                                          |
| IoU                        | *Intersection over union*, rasio irisan dan gabungan dua kotak                                |
| KD                         | *Knowledge distillation*                                                                      |
| KD hibrida                 | KD yang menggabungkan *loss* berlabel dengan distilasi fitur, kotak, dan kelas                |
| KD murni                   | KD yang hanya memakai keluaran *teacher* tanpa *loss* berlabel                                |
| KF                         | Kebutuhan fungsional                                                                          |
| KL                         | Kullback-Leibler, ukuran perbedaan dua distribusi peluang                                     |
| KNF                        | Kebutuhan nonfungsional                                                                       |
| *Letterbox*                | Penskalaan citra dengan rasio tetap dan penambahan *padding*                                  |
| mAP                        | *Mean average precision*, rata-rata AP seluruh kelas                                          |
| mAP50                      | mAP pada ambang IoU 0,50                                                                      |
| mAP50-95                   | Rata-rata mAP pada ambang IoU 0,50 sampai 0,95                                                |
| *Measurement window*       | Rentang waktu pengukuran *runtime* setelah *warm-up*                                          |
| MOTA                       | *Multiple object tracking accuracy*, metrik akurasi pelacakan banyak objek                    |
| NMS                        | *Non-maximum suppression*, penghapusan kotak yang tumpang tindih                              |
| ONNX                       | *Open Neural Network Exchange*, format pertukaran model jaringan saraf                        |
| OP3                        | ROBOTIS OP3, robot humanoid yang dipakai dalam penelitian ini                                 |
| P95                        | Persentil ke-95                                                                               |
| *Predict path*             | Jalur evaluasi melalui fungsi *predict* Ultralytics, sama dengan jalur *runtime* robot        |
| *Projector*                | Lapisan yang menyamakan jumlah kanal fitur *student* dengan fitur *teacher*                   |
| PTQ                        | *Post-training quantization*, kuantisasi sesudah pelatihan                                    |
| *Publish*                  | Mengirim pesan ROS 2 ke suatu *topic*                                                         |
| QAT                        | *Quantization-aware training*, pelatihan yang memperhitungkan kuantisasi                      |
| QoS                        | *Quality of Service*, pengaturan cara pesan ROS 2 dikirim                                     |
| *Repetition*               | Pengulangan *run* dengan model dan kondisi yang sama                                          |
| *Replay*                   | Pemutaran ulang *frame* terekam secara *offline*                                              |
| ROS 2                      | *Robot Operating System 2*                                                                    |
| RSS                        | *Resident set size*, memori fisik yang dipakai proses                                         |
| *Run*                      | Satu kali pengujian *runtime* selama *measurement window*                                     |
| SD                         | Simpangan baku                                                                                |
| *Seed*                     | Nilai awal pembangkit bilangan acak semu yang menentukan deret bilangan acak selama pelatihan |
| SHA-256                    | Fungsi *hash* 256 bit yang dipakai sebagai sidik jari berkas                                  |
| SSH                        | *Secure Shell*                                                                                |
| *Student*                  | Model kecil yang dilatih                                                                      |
| *Sub-controller*           | Pengendali tingkat bawah yang meneruskan perintah ke *servo*, yaitu OpenCR                    |
| *Subscribe*                | Menerima pesan ROS 2 dari suatu *topic*                                                       |
| *Teacher*                  | Model besar yang menjadi acuan dalam KD                                                       |
| TEST, TRAIN, VAL           | Bagian uji, latih, dan validasi himpunan data                                                 |
| *Timestamp*                | Catatan waktu saat suatu *frame* diambil atau diproses                                        |
| TP                         | *True positive*, deteksi yang cocok dengan label                                              |
| *Validator path*           | Jalur evaluasi melalui fungsi *val* Ultralytics                                               |
| YOLO                       | *You Only Look Once*, keluarga detektor objek satu tahap                                      |
