# Matriks bukti rumusan masalah dan celah — 9 November 2026

Matriks ini memisahkan data yang tersedia dari klaim yang dapat disimpulkan; bukan pengesahan pembimbing.

| Tujuan | Sumber utama | Status dan batas |
|---|---|---|
| 1. Kebutuhan, rancangan, implementasi dan uji ROS 2 OP3 | [Dokumentasi runtime OP3](../../OP3_PYTORCH_RUNTIME.md), [audit runtime](../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md), [contoh fungsi live](../2026-10-22/percobaan-22-supervised-live-function/README_ID.md) | Implementasi dan bukti uji tersedia. Lengkapi keterlacakan kebutuhan → rancangan → hasil uji di naskah; jangan klaim uji kontrol kepala berhasil. Foto, video, dan sebagian log hanya lokal. |
| 2. Perbandingan mAP model KD, supervised dan teacher | [T05 TEST](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md), [T30 TEST Hybrid](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md), [T38 kamera](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) | Tersedia untuk TEST resmi dan frame OP3 retrospektif; bedakan keduanya. TEST pernah digunakan sebelumnya; provenance teacher utama tidak lengkap dan set OP3 berasal dari satu rangkaian. |
| 3. Precision, recall dan F1 | T05/T30 dan T38 di atas | Tersedia; TEST menghitung F1 dari P/R makro, T38 merata-ratakan F1 per kelas. Sebut confidence, IoU, dan definisi. Cakupan deteksi live bukan metrik akurasi. |
| 4. Latensi dan FPS KD dan teacher ketika idle/berjalan | [T36 per run](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), [T37 ringkasan](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md) | 24/24 slot aktif dan pemeriksaan otomatis tersedia untuk analisis deskriptif. Run dalam blok lintas hari, pemilihan ulang teacher berjalan, dan bukti yang tidak lengkap membatasi kesetaraan fisik/kausalitas. |
| 5. CPU dan RAM onboard | T36/T37 | CPU adalah persen proses terhadap satu CPU logis; RSS adalah memori resident proses detektor, bukan RAM keseluruhan robot. Tiga run bukan uji signifikansi. |
| Pendukung: biaya training dan pengujian | [T35](../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) | Training sembilan student tercatat. Durasi sesi TEST meliputi beberapa model; waktu teacher utama setara dan waktu TEST per checkpoint tidak tersedia. Benchmark server lintas sesi dengan skrip berbeda tidak dibandingkan secara kausal. |
| Pendukung: ablasi ukuran teacher | [T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md), [audit teacher](AUDIT_TEACHER_T42_SERVER.md) | Dua teacher dan enam student selesai pada VAL. Hasil audit server yang dijalankan pengguna menyatakan semua cek lulus; byte dataset tidak dihitung ulang. Tiga seed student, satu teacher per ukuran; supervised kontrol berasal dari eksperimen sebelumnya. T42 tidak mengganti model utama. |

## Pekerjaan yang masih terbuka

1. [Audit teacher read-only di server](AUDIT_TEACHER_T42_SERVER.md) sudah dilaporkan lulus dan JSON disimpan dalam repo. Pemeriksaan byte penuh dataset dan verifikasi ulang mandiri di robot tidak dilakukan.
2. Konfirmasi pembimbing untuk varian Hybrid full, pemakaian runtime deskriptif, format naskah, rumusan masalah final, serta keputusan apakah keterbatasan data diterima. Persetujuan tersebut belum tercatat.
3. Periksa sumber primer dan sitasi ilmiah serta kesesuaian diagram, ilustrasi, nomor tabel/gambar, lampiran, dan pedoman kampus sebelum penyerahan.
4. Bila pembimbing mensyaratkan generalisasi lintas adegan, perlu data OP3 independen baru dengan anotasi sesuai protokol. Bila mensyaratkan perbandingan biaya inferensi per model yang terkontrol pada server, perlu benchmark satu sesi dengan frame, skrip, lingkungan, urutan dan kondisi host yang sama. Ini opsi penguatan, bukan bukti yang sudah dimiliki.
5. Cadangkan data mentah dan checkpoint di lokasi yang disetujui; tabel T38 dan grafik terkurasi sudah dipublikasikan, dan draf terpadu tersedia dalam [folder laporan](../../laporan/draf-bab-iv-v/README.md); sebagian data mentah masih lokal.

Tidak semua keterbatasan dapat diperbaiki tanpa pengukuran baru. Jangan merekonstruksi kondisi yang tidak tercatat atau menggunakan hasil VAL/T38 untuk memilih ulang model secara diam-diam.
