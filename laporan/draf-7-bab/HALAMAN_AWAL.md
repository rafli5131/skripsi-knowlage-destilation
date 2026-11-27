# HALAMAN AWAL

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v31 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

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

Robot humanoid ROBOTIS OP3 menjalankan seluruh pemrosesan citra pada CPU komputer *onboard*, sehingga detektor objek untuk bola, gawang, dan robot harus ringan tanpa kehilangan banyak akurasi. Model yang lebih kecil dapat berjalan lebih cepat, tetapi akurasinya dapat turun bila hanya dilatih dengan label. Penelitian ini bertujuan mengimplementasikan *knowledge distillation* (KD) untuk melatih *student* YOLO11 yang jumlah parameternya sekitar sepertiga *teacher* YOLO11n, lalu menjalankannya sebagai *node* ROS 2 pada komputer *onboard* OP3. KD hibrida, yang menggabungkan *loss* berlabel dengan distilasi fitur, kotak, dan kelas, dibandingkan dengan *student* berarsitektur sama yang dilatih secara *supervised*, *student* hasil KD murni, dan *teacher*. Ketiga varian *student* dilatih dengan tiga nilai awal acak (*seed*) dan dipilih hanya berdasarkan himpunan validasi, kemudian diuji pada himpunan uji, pada dua set citra kamera OP3, serta pada 24 *run* pengujian langsung saat robot diam dan berjalan. Pada himpunan uji, KD hibrida mencapai mAP50-95, yaitu ukuran ketepatan deteksi dan letak kotak, sebesar 0,7469, lebih tinggi daripada *supervised* pada ketiga pasangan *seed* dan setara dengan 95,8% akurasi *teacher*. F1, yaitu gabungan *precision* dan *recall*, kedua *student* setara pada ambang yang dipakai di robot. Pada citra kamera OP3, keunggulan tersebut tidak konsisten karena KD hibrida menghasilkan *false detection* pada sepertiga *frame* tanpa objek di set citra pertama. Pada robot, latensi rata-rata KD hibrida 64,70 ms saat diam dan 71,47 ms saat berjalan, dibanding sekitar 96 ms pada *teacher*, dengan laju 13,60 dan 12,54 FPS dibanding sekitar 9,9 FPS. Seluruh model memenuhi kebutuhan minimal 8 FPS, sedangkan penggunaan CPU dan memori tidak membedakan model secara jelas. Dengan demikian, KD hibrida meningkatkan akurasi *student* pada himpunan data, tetapi peningkatan tersebut belum konsisten pada citra kamera robot. Kecepatan yang lebih tinggi daripada *teacher* berasal dari ukuran *student* yang lebih kecil, bukan dari KD.

Kata kunci: *knowledge distillation*, deteksi objek, YOLO11, robot humanoid, ROBOTIS OP3, ROS 2

## Abstract

The ROBOTIS OP3 humanoid robot runs all image processing on its onboard CPU, so its detector for the ball, goal, and robots must be lightweight without losing much accuracy. This study aims to implement knowledge distillation (KD) to train a YOLO11 student with about one third of the parameters of a YOLO11n teacher, and to deploy it as a ROS 2 node on the OP3. Hybrid KD, which combines the labelled loss with feature, box, and class distillation, is compared with a supervised student of the same architecture, a pure KD student, and the teacher. The three student variants are trained with three random seeds and selected on the validation set only, then tested on the test set, on two sets of OP3 camera frames, and in 24 live runs with the robot idle and walking. On the test set, hybrid KD reaches an mAP50-95, an accuracy measure that also rewards precise boxes, of 0.7469, higher than the supervised student on all three seed pairs and equal to 95.8% of the teacher. The F1 score, combining precision and recall, is equal for both students at the thresholds used on the robot. On OP3 camera frames this advantage is not consistent, because hybrid KD produces false detections on one third of the empty frames in the first set. On the robot, the mean latency of hybrid KD is 64.70 ms when idle and 71.47 ms when walking, against about 96 ms for the teacher, at 13.60 and 12.54 FPS against about 9.9 FPS. All models meet the 8 FPS requirement, and CPU and memory usage barely differ. Hybrid KD therefore improves student accuracy on the dataset, but this gain is not yet consistent on the robot camera frames. The speed advantage over the teacher comes from the smaller student, not from KD.

*Keywords: knowledge distillation, object detection, YOLO11, humanoid robot, ROBOTIS OP3, ROS 2*
