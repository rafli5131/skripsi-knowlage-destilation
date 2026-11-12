# BAB 2 — LANDASAN KEPUSTAKAAN

> Draf bahan kerja. Lengkapi kutipan akademik dan periksa kembali setiap sumber primer serta format daftar pustaka sebelum penyerahan.

## 2.1 Deteksi objek dan YOLO

Deteksi objek memprediksi kelas dan kotak pembatas pada citra. Kualitas lokalisasi dapat dinilai dengan intersection over union (IoU), yaitu perbandingan luas irisan dan luas gabungan antara kotak prediksi dan acuan. Penelitian menggunakan teacher YOLO11n serta student YOLO11 skala t kustom; nama skala t dalam penelitian ini tidak mengacu pada YOLO11n standar. Model menerima citra berukuran masukan 640 dan menghasilkan prediksi untuk tiga kelas.

## 2.2 Knowledge distillation

Dalam KD, student mempelajari informasi yang dihasilkan teacher yang dibekukan. Sinyal yang digunakan pada eksperimen ini mencakup fitur, kotak, dan kelas. Hybrid full juga memakai loss deteksi berlabel, sedangkan KD murni menggunakan objective teacher-only. Supervised menjadi kontrol berarsitektur student sama tanpa distilasi. Perbedaan jumlah parameter teacher dan student mencerminkan perbedaan arsitektur, bukan manfaat kompresi yang dapat diatribusikan semata-mata kepada loss KD.

## 2.3 Metrik kualitas

Precision adalah proporsi prediksi positif yang benar, sedangkan recall adalah proporsi objek acuan yang ditemukan. F1 dapat dihitung sebagai `2PR/(P+R)`. AP merangkum precision–recall pada berbagai ambang; mAP50 menggunakan IoU 0,50 dan mAP50–95 merata-ratakan AP pada rentang IoU yang dipakai evaluator.

Agregasi harus dinyatakan. F1 utama penelitian adalah rata-rata harmonik precision makro dan recall makro; T38 historis melaporkan rata-rata F1 per kelas sebagai metrik pelengkap. Nilai confidence pada satu kotak bukan akurasi model.

## 2.4 Runtime dan sumber daya

Latensi menyatakan waktu pemrosesan, sedangkan FPS efektif diturunkan dari timestamp frame yang diterima. CPU dalam hasil OP3 adalah persen proses detektor terhadap satu CPU logis; nilainya dapat melampaui 100% karena proses menggunakan lebih dari satu thread. RSS adalah memori resident proses, bukan jumlah seluruh RAM yang digunakan robot.

## 2.5 ROS 2 dan ROBOTIS OP3

ROS 2 menyediakan komunikasi topik untuk menghubungkan penerbit citra kamera dengan node deteksi. Pada implementasi ini node mengonsumsi citra, menjalankan model, dan menerbitkan hasil deteksi serta preview bila diaktifkan. Pengoperasian gerakan robot terpisah dari node deteksi.

## 2.6 Penelitian terkait

Bandingkan penelitian KD deteksi berdasarkan teacher/student, data, loss berlabel, jenis distilasi, metrik dan perangkat uji. Jangan menyebut suatu objective teacher-only hanya karena salah satu komponen loss distilasinya tidak memakai label. Bahan yang telah dihimpun tersedia di [tinjauan pustaka](../../TINJAUAN_PUSTAKA_KD_DETEKSI.md), [proposal terdahulu](../../DRAF_PROPOSAL_BAB_I-III.md), dan [bibliografi](../../REFERENSI_SKRIPSI.bib). Setiap sitasi masih perlu dicocokkan dengan sumber primer.
