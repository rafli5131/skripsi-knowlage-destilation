# Definisi metrik dan batas interpretasi

- **Latensi per tahap**: preprocess, inference, dan postprocess/NMS; total = jumlah ketiga tahap. End-to-end = awal callback gambar sampai keluaran deteksi diterbitkan.
- **Capture-to-publish** = waktu terbit dikurangi timestamp header kamera hanya jika keduanya memakai clock yang sama. Nilai itu belum tersedia pada log lama.
- **FPS efektif** = (n - 1) / (t_n - t_1), berdasarkan timestamp frame yang diproses. Tabel sesi lama memakai semua frame karena penanda warm-up belum direkam.
- **FPS turunan** = 1000 / rerata latensi total (ms); tidak sama dengan FPS stream kamera.
- **CPU ternormalisasi** = CPU% proses / jumlah logical CPU. Jumlah logical CPU OP3 belum tercatat dalam sesi lama.
- **Persentil**: interpolasi linear NumPy, sama dengan posisi (n - 1)q.
- **Kepatuhan tenggat** = proporsi frame dengan latensi <= 33,3 ms dan <= 66,7 ms. T23 kini memuat proporsi deskriptif dari sesi live tersimpan; benchmark frame tetap belum tersedia.
- **P, R, F1**: dihitung pada IoU 0,5 dan confidence 0,25 untuk evaluasi historis; mAP50-95 dirata-ratakan pada IoU 0,50 sampai 0,95.
- **mAP/akurasi Advance Vision**: valid untuk evaluasi gambar pada dataset Advance Vision. Angka tidak mengukur akurasi kamera OP3.
- **Sesi kamera**: jumlah deteksi dan runtime tidak sama dengan precision/recall karena tidak ada anotasi ground truth pada frame kamera.
- **Tracking**: ID BoT-SORT menghubungkan deteksi lintas frame dan hanya berlaku selama satu proses node. ID tidak menunjukkan kebenaran kelas. Konsistensi ID pada objek relatif diam tercatat di sesi servo_idle 20261019T123737Z_023704; kestabilan ID pada objek bergerak belum diuji khusus.
- **Ukuran objek**: kecil < 32^2 piksel; sedang 32^2 sampai 96^2; besar > 96^2 pada citra 640. Tabel per ukuran belum dihasilkan.

- **Perbedaan scope waktu pada log baru**: `processing_ms` pada `op3_idle_trial` dihitung sejak worker mengambil frame hingga hasil siap dicatat, bukan callback-ke-publish. `processing_ms` pada uji kepala juga mencakup komunikasi servo pada frame berperintah. Jangan menggantinya dengan end-to-end legacy.

Metrik P/R/F1/mAP ditampilkan sebagai fraksi 0 sampai 1; kolom T23 yang bersatuan percent memakai skala 0 sampai 100. CSV memakai titik desimal dan Markdown memakai koma desimal. Sel yang belum punya sumber diberi `[BELUM DIUKUR]`.
