# Status model dan tabel lab/server — 20 Oktober 2026

## Berapa model yang sudah ada?

Unit perbandingan eksperimen final adalah **tujuh checkpoint `best.pt`** yang tercatat dalam [`configs/model_registry.yaml`](../configs/model_registry.yaml): satu teacher YOLO11n FP32 dari proyek Advance Vision, tiga student KD murni (`seed` 42, 1337, 2025), dan tiga student supervised dengan arsitektur yang sama. Teacher adalah checkpoint sumber yang digunakan kembali; di repo ini ada **enam run training final student**, bukan tujuh run training final.

Di luar tujuh checkpoint final itu ada **satu run KD eksplorasi** di `runs/kd/yolo11_tiny_pure_kd_v4/`. File [`models/weights/kd_student_best.pt`](../models/weights/kd_student_best.pt) untuk OP3 mempunyai SHA-256 yang sama dengan `kd_seed42` pada registry, sehingga merupakan salinan checkpoint deploy, bukan training atau model kedelapan. Berkas `last.pt` adalah snapshot epoch terakhir dari run yang sama dan tidak dihitung sebagai model eksperimen tambahan.

Student yang dilatih adalah YOLO11 kustom skala `t` dengan 810.649 parameter; nama “YOLO11n” hanya tepat untuk teacher. Semua checkpoint final sekarang memakai PyTorch `.pt`; tidak ada hasil OpenVINO atau QAT pada eksperimen final.

## Apa akibat saran perbaikan KD?

Saran `pure_weighted` mengubah bobot lokasi pada loss box dan kelas berdasarkan keyakinan teacher. Ia tetap teacher-only KD, tetapi **memerlukan training student baru** dan akan menghasilkan checkpoint `best.pt` baru. Pilot yang masuk akal adalah satu `seed` dengan arsitektur, data, dan anggaran epoch yang sama; kandidat dibandingkan dengan `pure_v4` hanya pada VAL. Jika memenuhi kriteria yang ditetapkan, eksperimen utama baru perlu diulang pada tiga seed dan dievaluasi sesuai protokol. Checkpoint lama tetap menjadi baseline dan kontrol, sehingga jumlah model eksperimen akan bertambah. Mengisi T05/T08/T12/T13 dari artefak saat ini tidak melatih atau membuat model baru.

`pure_v4` masih keputusan D2 yang dikunci; kandidat objective baru memerlukan keputusan eksplisit di TH-D sesuai [`docs/DECISIONS.md`](DECISIONS.md). Keputusan jumlah epoch D3 juga belum dikunci. Diagnosis VAL menunjukkan kekurangan KD terhadap kontrol supervised, tetapi tidak membuktikan secara kausal bahwa `pure_weighted` akan memperbaikinya. Oleh karena itu T04 dapat memuat tiga baris baseline sekarang, sementara klaim **ablasi** baru sah setelah ada minimal satu kondisi training alternatif.

## Cara membaca hasil yang ada

Dalam cakupan yang dinyatakan pada tiap tabel, **13 dari 14 tabel lab/server T01–T14 sudah terisi**. T04 masih sebagian: tiga baseline `pure_v4` tersedia, tetapi belum ada run kandidat untuk membuat perbandingan ablasi. Pada pembaruan ini T05 diisi interval bootstrap antar-seed, T08 diisi 63 baris dari prediksi VAL, T12 diisi 15 kombinasi NMS, dan T13 memuat 12 kombinasi ukuran CPU server serta tujuh titik dasar L40. Tidak ada training baru untuk pelengkapan tabel ini.

T05 mempunyai dua jenis interval yang harus dibedakan: interval per checkpoint meresampling gambar TEST, sedangkan interval rerata tiga seed meresampling seed dan bersifat eksploratif karena `n=3`. T08 tidak mempunyai objek `gawang` kategori kecil pada VAL, sehingga metrik sel tersebut memang tidak berlaku. Pada T12, menurunkan NMS IoU untuk KD seed 42 dari 0,70 ke 0,30 mengubah duplikat diagnostik dari 240 menjadi 0, tetapi mAP50–95 VAL juga turun dari sekitar 0,683 ke 0,662. Ini adalah trade-off pada VAL, bukan keputusan konfigurasi robot.

- T05–T08 pada dataset Advance Vision menilai gambar berlabel dari split resmi Roboflow; angka TEST saat ini sudah pernah dilihat dan tidak boleh dipakai memilih objective baru.
- T12 dan T13 adalah diagnosis pada VAL. Sapuan memakai teacher, KD `seed` 42, dan supervised `seed` 42 sebagai perwakilan tiga varian. Hasil seed 1337/2025 pada ukuran 640 masih terdapat di titik dasar historis T13.
- Benchmark NVIDIA L40 historis, CPU server AMD EPYC, dan runtime CPU robot OP3 adalah tiga lingkungan berbeda. FPS turunan dari satu frame tetap tidak sama dengan FPS kamera robot.
- T15–T27 adalah tabel sisi OP3. mAP/P/R/F1 kamera OP3 tetap memerlukan frame kamera berlabel; sesi live tanpa anotasi hanya mendukung pengamatan runtime dan tracking.

Pintu masuk semua tabel dan sumbernya ada di [`analisis_performa/lab_server/README.md`](../analisis_performa/lab_server/README.md).
