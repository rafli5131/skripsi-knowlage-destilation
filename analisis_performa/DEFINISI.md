# Definisi metrik dan batas interpretasi

- **Latensi per tahap**: preprocess, inference, dan postprocess/NMS; total = jumlah ketiga tahap. End-to-end = awal callback gambar sampai keluaran deteksi diterbitkan.
- **Capture-to-publish** = waktu terbit dikurangi timestamp header kamera hanya jika keduanya memakai clock yang sama. Nilai itu belum tersedia pada log lama.
- **FPS efektif** = (n - 1) / (t_n - t_1), berdasarkan timestamp frame yang diproses. Tabel sesi lama memakai semua frame karena penanda warm-up belum direkam.
- **FPS turunan** = 1000 / rerata latensi total (ms); tidak sama dengan FPS stream kamera.
- **CPU ternormalisasi** = CPU% proses / jumlah logical CPU. Jumlah logical CPU OP3 belum tercatat dalam sesi lama.
- **Persentil**: interpolasi linear NumPy, sama dengan posisi (n - 1)q.
- **Kepatuhan tenggat** = proporsi frame dengan latensi <= 33,3 ms dan <= 66,7 ms. T23 kini memuat proporsi deskriptif dari sesi live tersimpan; benchmark frame tetap belum tersedia.
- **P, R, F1**: dihitung pada IoU 0,5 dan confidence 0,25 untuk evaluasi historis; mAP50-95 dirata-ratakan pada IoU 0,50 sampai 0,95.
- **Usulan D11, F1 utama**: `F1 = 2 × P_makro × R_makro / (P_makro + R_makro)`, dengan nilai nol bila penyebut nol. P dan R makro adalah rerata tak berbobot atas kelas `ball`, `gawang`, dan `robot` pada ambang operasi yang sama. Ini mengikuti evaluator TEST historis dan definisi T04/T05. Rerata aritmetika F1 masing-masing kelas dilaporkan terpisah sebagai `F1_mean_per_class`; kedua angka tidak boleh diberi nama yang sama. D11 belum dikunci oleh pengguna.
- **mAP/akurasi Advance Vision**: valid untuk evaluasi gambar pada dataset Advance Vision. Angka tidak mengukur akurasi kamera OP3.
- **Sesi kamera live tanpa anotasi per frame**: jumlah deteksi dan runtime tidak sama dengan precision/recall. Evaluasi offline T27 memakai frame kamera yang telah diberi label manusia dan mempunyai protokol pencocokan tersendiri.
- **Tracking**: ID BoT-SORT menghubungkan deteksi lintas frame dan hanya berlaku selama satu proses node. ID tidak menunjukkan kebenaran kelas. Sesi `servo_idle` 20261019T123737Z_023704 dan sesi live 20261021_tracking_live_01 mencatat kontinuitas ID; akurasi tracking terhadap *ground truth* identitas temporal belum diukur.
- **Ukuran objek**: kecil < 32^2 piksel; sedang 32^2 sampai 96^2; besar > 96^2 pada citra referensi 640. T08 menghitung luas kotak VAL setelah menormalkan sisi tensor validator ke 640 piksel; kelompok tanpa GT ditandai tidak berlaku.

- **Perbedaan scope waktu pada log baru**: `processing_ms` pada `op3_idle_trial` dihitung sejak worker mengambil frame hingga hasil siap dicatat, bukan callback-ke-publish. `processing_ms` pada uji kepala juga mencakup komunikasi servo pada frame berperintah. Jangan menggantinya dengan end-to-end legacy.

Metrik P/R/F1/mAP ditampilkan sebagai fraksi 0 sampai 1; kolom T23 yang bersatuan percent memakai skala 0 sampai 100. CSV memakai titik desimal dan Markdown memakai koma desimal. Sel yang belum punya sumber diberi `[BELUM DIUKUR]`.
