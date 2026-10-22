# Konfirmasi rumusan masalah dan cakupan evaluasi OP3

**Status:** Bhre melaporkan bahwa pembimbing telah menyetujui lima rumusan masalah ini. Tanggal persetujuan pembimbing belum dicatat. Detail operasional pengukuran robot masih perlu ditetapkan. Hasil lab/server yang diringkas di sini tidak membuktikan kinerja pada kamera OP3.

## Rumusan masalah yang disetujui pembimbing

1. Bagaimana implementasi sistem deteksi objek berbasis ROS 2 yang menjalankan model YOLO11 skala t hasil *knowledge distillation* (KD) pada robot humanoid ROBOTIS OP3?
2. Bagaimana tingkat akurasi, berdasarkan nilai *mean average precision* (mAP), model YOLO11 skala t hasil KD dibandingkan dengan model berarsitektur sama yang dilatih secara *supervised* dan dengan *teacher* YOLO11n?
3. Bagaimana kinerja ketiga model tersebut jika ditinjau dari nilai *precision*, *recall*, dan *F1-score*?
4. Berapa rata-rata latensi dan *frames per second* (FPS) yang dicapai model hasil KD dan *teacher* YOLO11n saat beroperasi secara *real-time* pada kondisi robot diam dan berjalan?
5. Bagaimana tingkat efisiensi penggunaan CPU dan RAM model hasil KD dan *teacher* YOLO11n saat dijalankan secara penuh pada komputer *onboard* robot?

Dalam draf ini, “model hasil KD” berarti `hybrid_full` sebagai varian yang dipilih berdasarkan VAL. `pure_v4` dan `hybrid_feature` dilaporkan sebagai ablasi. Kandidat OP3 adalah `hybrid_full_seed1337`; alias runtime `op3_default` masih menunjuk KD murni seed 42. Perubahan kandidat belum berarti checkpoint robot sudah diganti.

## Bukti yang tersedia dan yang masih diperlukan

| Rumusan | Bukti yang tersedia | Bukti yang belum tersedia |
| --- | --- | --- |
| 1. Implementasi ROS 2 pada OP3 | Node PyTorch ROS 2 dan runtime robot KD murni terdokumentasi di [`OP3_PYTORCH_RUNTIME.md`](../OP3_PYTORCH_RUNTIME.md) dan [`scripts/op3_pytorch_detector.py`](../scripts/op3_pytorch_detector.py). Runtime sudah dapat memilih varian `hybrid` sejak commit `e0ebb91`. Sesi kamera terdahulu menjalankan KD seed 42; lihat [laporan sesi idle](../dokumentasi/2026-10-21/percobaan-01-monitor-rekam-servo-idle/README.md). | Bukti eksekusi Hybrid seed 1337 pada OP3, verifikasi overlay tiga kelas, dan hasil tracking Hybrid. Sesi KD lama tidak membuktikan implementasi Hybrid berjalan di perangkat. |
| 2. mAP KD vs supervised dan teacher | Advance Vision VAL memuat Hybrid full vs supervised tiga seed pada [T28](../analisis_performa/tabel/T28_selisih_kd_hybrid_val.md); T04 memuat ablasi KD murni dan Hybrid. TEST lanjutan ada pada [T30](../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md), sedangkan ringkasan TEST terdahulu termasuk teacher dan pure KD ada pada [T05](../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md). | mAP kamera OP3 untuk Hybrid, supervised, dan teacher pada gambar serta label final yang sama. T27 saat ini hanya evaluasi eksploratif KD murni seed 42 dan supervised seed 42; setnya belum final. |
| 3. Precision, recall, F1 ketiga model | Advance Vision menyediakan P/R/F1 untuk Hybrid dan supervised (T28/T30), serta teacher/pure KD pada hasil TEST terdahulu (T05). | P/R/F1 kamera OP3 untuk semua model pada set final berlabel yang sama, dengan ambang dan definisi metrik yang dikunci. |
| 4. Latensi/FPS KD dan teacher saat diam/berjalan | T18 dan T26 memuat pengukuran historis KD seed 42 saat servo idle. T32 adalah benchmark L40 pada server, bukan runtime OP3. | Pengukuran Hybrid dan teacher yang berpasangan saat servo idle dan walking; pengulangan, durasi, warm-up, dan definisi FPS harus dikunci. Belum ada sesi walking terverifikasi yang sebanding. |
| 5. CPU/RAM KD dan teacher pada OP3 | T18/T26 memuat CPU dan RSS untuk beberapa sesi KD lama; sesi idle utama memakai KD seed 42. | CPU/RAM Hybrid dan teacher pada OP3 untuk sesi bersih yang sama, pada kondisi diam dan berjalan, dengan pengulangan yang ditetapkan. Data L40 tidak dapat menggantikannya. |

### Angka lab/server sebagai konteks

- Pada VAL, rerata mAP50–95 tiga seed Hybrid full adalah **0,7505 ± 0,0018**, dibanding supervised **0,7208 ± 0,0041**; beda berpasangan **+0,0297 ± 0,0047**. Pure KD `pure_v4` berada sekitar **0,679**. Lihat T04 dan T28.
- Pada TEST lanjutan, Hybrid full memperoleh **0,7469 ± 0,0022** dan supervised **0,7225 ± 0,0035**; beda berpasangan **+0,0244 ± 0,0040**. F1@0,25 Hybrid **0,9071 ± 0,0017** dan supervised **0,9121 ± 0,0026**. Teacher memperoleh mAP50–95 **0,7800** pada hasil TEST terdahulu (T05).
- Official TEST Advance Vision telah digunakan pada eksperimen teacher dan KD murni sebelum evaluasi Hybrid. Karena itu, hasil Hybrid tersebut merupakan evaluasi lanjutan pada split yang sama, bukan holdout yang sama sekali belum pernah dilihat.
- Rincian protokol dan batas interpretasi tersedia dalam [laporan TEST Hybrid](../analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md) dan [indeks tabel](../analisis_performa/INDEKS.md).

## Rincian protokol yang masih perlu ditetapkan

1. Untuk rumusan 4 dan 5, apakah pembanding runtime cukup *teacher* YOLO11n, atau model *supervised* juga perlu diukur?
2. Apakah akurasi pada frame kamera OP3 termasuk dalam rumusan 2 dan 3, atau ditempatkan sebagai evaluasi pendukung terpisah dari Advance Vision?
3. Apakah `hybrid_full` sebagai model KD utama, dengan `pure_v4` dan `hybrid_feature` sebagai ablasi, dapat diterima berdasarkan pemilihan checkpoint di VAL?
4. Apa definisi operasional kondisi “berjalan”: berjalan di tempat, berjalan maju pada area aman, atau berjalan di atas *stand*?
5. Berapa jumlah ulangan dan durasi per sesi yang dianggap memadai untuk pengukuran latensi, FPS, CPU, dan RAM?

Persetujuan rumusan masalah tidak dengan sendirinya menetapkan rincian protokol di atas. Konfigurasi runtime dan jumlah sesi tetap berstatus usulan sampai diputuskan. Tidak ada metrik yang belum tersedia yang diisi dengan perkiraan.
