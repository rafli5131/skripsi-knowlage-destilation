# BAB 7 PENUTUP

> Isi berkas ini disalin dari naskah skripsi **Skripsi_KD_OP3_v35 (27 November 2026)**. Sumber kebenaran tetap berkas DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Gambar tidak disertakan; keterangan gambar tetap dicantumkan supaya nomor dan rujukannya dapat dicocokkan dengan PDF.

## 7.1 Kesimpulan

Sistem deteksi objek berbasis ROS 2 Jazzy yang menjalankan *student* YOLO11 skala t hasil KD sebagai berkas .pt FP32 pada CPU komputer *onboard* OP3 telah diimplementasikan. Sistem menerima citra kamera, melakukan *publish* hasil deteksi bola, gawang, dan robot, menampilkan *preview*, dan mencatat data *runtime* per *frame*. Seluruh kasus uji kebutuhan lulus dengan catatan pada pelacakan dan *preview*. Berdasarkan hasil pengujian, jawaban atas rumusan masalah adalah sebagai berikut.

1.  Pada citra TEST, KD hibrida lebih akurat daripada *supervised* dan mendekati *teacher*, tetapi keunggulan ini tidak konsisten pada citra kamera OP3. Rata-rata mAP50-95 KD hibrida penuh pada 592 citra TEST adalah 0,7469, lebih tinggi 0,0244 ± 0,0040 daripada *supervised* (0,7225) pada ketiga pasangan *seed* dan setara dengan 95,8% *teacher* YOLO11n (0,7800); mAP50 ketiganya berada pada 0,958 sampai 0,964. Pada *predict path* yang dipakai robot, mAP50-95 KD hibrida pada Set Kamera 1 adalah 0,4307, di bawah *teacher* (0,5041) dan KD murni (0,4729), sedangkan pada Set Kamera 2 KD hibrida tertinggi (0,8900), tetapi keunggulannya bergantung pada konvensi kotak gawang. Urutan model pada kamera OP3 juga berubah antara *validator path* dan *predict path*.

2.  KD hibrida tidak memberi keunggulan pada *precision*, *recall*, dan F1: pada TEST nilainya setara dengan *supervised* dan sedikit di bawah *teacher*, sedangkan pada citra kamera OP3 urutannya bergantung pada set dan konvensi kotak. Pada TEST, F1 KD hibrida penuh 0,9071, *supervised* 0,9121, dan *teacher* 0,9290 pada *validator path*; pada ambang *runtime* F1 KD hibrida dan *supervised* setara (0,9334 dan 0,9337), sedikit di bawah *teacher* (0,9354). *Precision* KD hibrida lebih rendah 0,0090 daripada *supervised* dengan *recall* yang sama. Pada Set Kamera 1, F1 KD hibrida 0,6146 berada di bawah *supervised* (0,6626) dan *teacher* (0,7651) karena *false detection* pada 21 dari 60 *frame* tanpa objek, sedangkan pada Set Kamera 2 F1 KD hibrida tertinggi (0,9950), tetapi turun menjadi 0,6711 pada konvensi rangka gawang utuh.

3.  Kedua *student* lebih cepat daripada *teacher* pada kedua kondisi, tetapi KD hibrida tidak konsisten lebih cepat daripada *supervised*. Latensi rata-rata KD hibrida 64,70 ms dengan 13,60 FPS saat diam dan 71,47 ms dengan 12,54 FPS saat berjalan, sedangkan *teacher* 96,24 ms dengan 9,88 FPS saat diam dan 95,85 ms dengan 9,87 FPS saat berjalan. Median latensi KD hibrida 50,46 dan 59,18 ms dibandingkan dengan 77,76 dan 77,03 ms pada *teacher*, sedangkan P95 KD hibrida sekitar 20 ms di bawah *teacher*. *Supervised* mencapai 73,12 ms dengan 12,14 FPS saat diam dan 70,80 ms dengan 12,64 FPS saat berjalan, sehingga kecepatan kedua *student* berdekatan dan urutannya berganti antarkondisi. Keunggulan kecepatan terhadap *teacher* karena itu berasal dari ukuran *student*, bukan dari KD. Semua model melampaui 8 FPS.

4.  Penggunaan CPU dan RAM ketiga model berdekatan, sehingga tidak membedakan efisiensi model secara jelas. Penggunaan CPU proses ketiga model sekitar 1.300% satu CPU logis (81 sampai 84% dari 16 CPU logis) pada kedua kondisi. RSS KD hibrida dan *supervised* sama-sama 356 sampai 359 MiB, dibandingkan dengan 371 sampai 372 MiB pada *teacher*. *Replay offline* menunjukkan bahwa kombinasi pelacakan dan OpenBLAS menjadi faktor besar penggunaan CPU, tetapi jumlah *thread* pada *run* asli tidak terekam.

## 7.2 Saran

Saran untuk penelitian berikutnya adalah sebagai berikut.

1.  Mengevaluasi model pada set *frame* kamera OP3 baru dari beberapa adegan dan sesi, dengan label yang dibuat independen dari prediksi model, sebelum memilih model untuk pemakaian di robot.

2.  Menetapkan jalur inferensi yang sama dengan *runtime* robot sebagai jalur evaluasi utama sejak awal, karena urutan model pada kamera OP3 berubah antarjalur.

3.  Mengulang pengukuran *runtime* dengan urutan model yang digilir dalam satu hari, mencatat jumlah *thread* PyTorch dan OpenBLAS selama *run*, serta membatasi *thread* OpenBLAS agar beban model dapat dipisahkan dari beban pelacakan.

4.  Menambahkan data pelatihan dari kamera OP3, terutama gawang parsial dan *frame* tanpa objek, untuk menekan *false detection*.

5.  Mengukur kinerja pelacakan dengan label identitas acuan dan metrik seperti MOTA atau IDF1 pada beberapa objek bergerak bila sistem akan dipakai untuk perilaku yang bergantung pada ID objek.
