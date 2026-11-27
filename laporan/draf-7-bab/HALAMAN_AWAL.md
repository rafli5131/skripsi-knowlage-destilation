# HALAMAN AWAL

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v36 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

> Data pribadi (nama, NIM, NIK, email, dan nama pihak dalam prakata) sengaja tidak dicantumkan di repositori publik. Bagian pengesahan, pernyataan, dan prakata hanya diringkas isinya; teks lengkapnya ada di naskah DOCX/PDF.

**Judul:** IMPLEMENTASI *KNOWLEDGE DISTILLATION* UNTUK DETEKSI OBJEK PADA ROBOT HUMANOID ROBOTIS OP3

## Lembar Pengesahan (ringkasan)

- Skripsi diajukan untuk memenuhi sebagian persyaratan memperoleh gelar Sarjana Teknik, Program Studi Teknik Komputer, Departemen Teknik Informatika, Fakultas Ilmu Komputer, Universitas Brawijaya, Malang, 2026.
- Disetujui oleh dosen pembimbing tunggal dan diketahui oleh Ketua Departemen Teknik Informatika.

## Pernyataan Orisinalitas (ringkasan)

- Penulis menyatakan naskah tidak memuat karya ilmiah orang lain yang pernah diajukan untuk gelar akademik, kecuali yang dikutip dan disebut dalam Daftar Referensi.
- Penulis bersedia skripsi digugurkan dan gelar dibatalkan bila terbukti ada unsur plagiasi.

## Prakata (ringkasan)

- Ucapan syukur dan penjelasan bahwa skripsi disusun untuk memenuhi persyaratan gelar Sarjana Teknik.
- Ucapan terima kasih kepada pihak yang membantu menurut perannya: Tuhan Yang Maha Esa, orang tua dan keluarga, dosen pembimbing tunggal, Ketua Departemen Teknik Informatika, Ketua Program Studi Teknik Komputer, dosen penasihat akademik, Kepala Laboratorium Robotika dan Embedded System, dosen dan staf FILKOM, teman sesama bimbingan, lembaga ROBOTIIK FILKOM dan tim robot humanoid yang menyediakan OP3, serta pengelola server laboratorium. Nama pihak tidak disalin.
- Penutup berisi harapan atas kritik dan saran dari dosen penguji dan pembaca.

## Abstrak

Robot humanoid ROBOTIS OP3 menjalankan seluruh pemrosesan citra pada CPU komputer *onboard*, sehingga detektor objek untuk bola, gawang, dan robot harus ringan tanpa kehilangan banyak akurasi. Model yang lebih kecil dapat berjalan lebih cepat, tetapi akurasinya dapat turun bila hanya dilatih dengan label. Penelitian ini bertujuan mengimplementasikan *knowledge distillation* (KD) untuk melatih *student* YOLO11 yang jumlah parameternya sekitar sepertiga *teacher* YOLO11n, lalu menjalankannya sebagai *node* ROS 2 pada komputer *onboard* OP3. KD hibrida, yang menggabungkan *loss* berlabel dengan distilasi fitur, kotak, dan kelas, dibandingkan dengan *student* berarsitektur sama yang dilatih secara *supervised*, *student* hasil KD murni, dan *teacher*. Ketiga varian *student* dilatih dengan tiga nilai awal acak (*seed*) dan dipilih hanya berdasarkan himpunan validasi, kemudian diuji pada himpunan uji, pada dua set citra kamera OP3, serta pada 24 *run* pengujian langsung saat robot diam dan berjalan. Pada himpunan uji, mAP50-95 KD hibrida, yaitu ukuran ketepatan deteksi dan letak kotak, lebih tinggi daripada *supervised* pada ketiga pasangan *seed* dan mencapai 95,8% nilai *teacher*. Pada ambang yang dipakai di robot, nilai F1 kedua *student*, yaitu gabungan *precision* dan *recall*, setara. Pada citra kamera OP3, keunggulan tersebut tidak konsisten karena KD hibrida menghasilkan *false detection* pada sepertiga *frame* tanpa objek di set citra pertama. Pada robot, latensi rata-rata KD hibrida sekitar 65 sampai 71 ms dengan laju 12,5 sampai 13,6 FPS, sedangkan *teacher* sekitar 96 ms dengan laju sekitar 9,9 FPS. Seluruh model memenuhi kebutuhan minimal 8 FPS, sedangkan penggunaan CPU dan memori tidak membedakan model secara jelas. Dengan demikian, KD hibrida meningkatkan akurasi *student* pada himpunan data, tetapi peningkatan tersebut belum konsisten pada citra kamera robot. Kecepatan yang lebih tinggi daripada *teacher* berasal dari ukuran *student* yang lebih kecil, bukan dari KD.

Kata kunci: *knowledge distillation*, deteksi objek, YOLO11, robot humanoid, ROBOTIS OP3, ROS 2

## Abstract

The ROBOTIS OP3 humanoid robot runs all image processing on its onboard CPU, so its detector for the ball, goal, and robots must be lightweight without losing much accuracy. A smaller model runs faster but may lose accuracy when trained with labels alone. This study aims to implement knowledge distillation (KD) to train a YOLO11 student with about one third of the parameters of a YOLO11n teacher, and to deploy it as a ROS 2 node on the OP3. Hybrid KD, which combines the labelled loss with feature, box, and class distillation, is compared with a supervised student of the same architecture, a pure KD student, and the teacher. The three student variants are trained with three random seeds and selected on the validation set only, then tested on the test set, on two sets of OP3 camera frames, and in 24 live runs with the robot idle and walking. On the test set, hybrid KD scores a higher mAP50-95, a measure that also rewards precise boxes, than the supervised student on all three seed pairs and reaches 95.8% of the teacher. At the thresholds used on the robot, both students have equal F1 scores. On OP3 camera frames this advantage is not consistent, because hybrid KD produces false detections on one third of the empty frames in the first set. On the robot, hybrid KD takes about 65 to 71 ms per frame, or 12.5 to 13.6 FPS, against about 96 ms and 9.9 FPS for the teacher. All models meet the 8 FPS requirement, and CPU and memory usage barely differ. Hybrid KD therefore improves student accuracy on the dataset, but this gain is not yet consistent on the robot camera frames. The speed advantage over the teacher comes from the smaller student, not from KD.

*Keywords: knowledge distillation, object detection, YOLO11, humanoid robot, ROBOTIS OP3, ROS 2*

## Daftar Istilah dan Singkatan

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
| *Field of view*            | Bidang yang terlihat oleh kamera                                                              |
| *Floating point*           | Format bilangan pecahan dengan titik desimal yang dapat bergeser                              |
| FN                         | *False negative*, objek berlabel yang tidak terdeteksi                                        |
| FP                         | *False positive*, deteksi yang tidak memiliki pasangan label                                  |
| FP32                       | Bilangan *floating point* 32 bit                                                              |
| FPS                        | *Frame per second*, jumlah *frame* yang diproses setiap detik                                 |
| *Frame*                    | Satu citra dari aliran kamera                                                                 |
| GFLOPs                     | Miliar operasi *floating point* untuk satu kali inferensi                                     |
| GMC                        | *Global motion compensation*, kompensasi gerak kamera pada pelacak                            |
| GPU                        | *Graphics processing unit*                                                                    |
| *Ground truth*             | Kotak dan kelas acuan dari label himpunan data                                                |
| *Hash*                     | Nilai ringkas hasil fungsi *hash* yang digunakan untuk memastikan berkas tidak berubah        |
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
| SHA-256                    | Fungsi *hash* 256 bit yang digunakan untuk memeriksa keutuhan berkas                          |
| *Soft target*              | Distribusi probabilitas kelas dari *teacher* yang dipakai sebagai target *student*            |
| SSH                        | *Secure Shell*                                                                                |
| *Student*                  | Model kecil yang dilatih                                                                      |
| *Sub-controller*           | Pengendali tingkat bawah yang meneruskan perintah ke *servo*, yaitu OpenCR                    |
| *Subscribe*                | Menerima pesan ROS 2 dari suatu *topic*                                                       |
| *Teacher*                  | Model besar yang menjadi acuan dalam KD                                                       |
| TEST, TRAIN, VAL           | Bagian uji, latih, dan validasi himpunan data                                                 |
| *Timestamp*                | Catatan waktu saat suatu *frame* diambil atau diproses                                        |
| TP                         | *True positive*, deteksi yang cocok dengan label                                              |
| *Trade-off*                | Hubungan saling mengorbankan antara dua sifat, misalnya akurasi dan kecepatan                 |
| *Validator path*           | Jalur evaluasi melalui fungsi *val* Ultralytics                                               |
| YOLO                       | *You Only Look Once*, keluarga detektor objek satu tahap                                      |
