# Kerangka Bab Skripsi

**Judul kerja:** *Kompresi Model YOLO untuk Deteksi Objek Advance Vision Menggunakan Pure Teacher-Only Knowledge Distillation*  
Kerangka ini mengikuti eksperimen dan batas klaim yang sudah ditetapkan. Draf abstrak tersedia di [`DRAF_ABSTRAK_SKRIPSI.md`](DRAF_ABSTRAK_SKRIPSI.md), draf proposal Bab I–III di [`DRAF_PROPOSAL_BAB_I-III.md`](DRAF_PROPOSAL_BAB_I-III.md), dan draf hasil serta simpulan Bab IV–V berbasis TEST terkunci di [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md). Format akhir perlu disesuaikan dengan pedoman prodi dan arahan pembimbing.

## Benang merah penelitian

Penelitian menguji apakah student YOLO yang lebih kecil dapat mempelajari deteksi dari keluaran dan fitur teacher YOLO11n melalui **pure teacher-only knowledge distillation (KD)**. Student KD tidak menerima loss ground-truth. Student berarsitektur sama yang dilatih supervised dijadikan kontrol terpisah untuk mengukur dampak objective, sedangkan teacher menjadi acuan kualitas dan biaya model.

Pertanyaan penelitian yang dijawab:

1. Bagaimana performa student pure KD dibandingkan teacher dan student supervised dengan arsitektur sama?
2. Bagaimana trade-off mAP, jumlah parameter, ukuran checkpoint, FLOPs, latensi, dan throughput?
3. Kelas apa yang paling banyak kehilangan atau memperoleh performa setelah kompresi?

## Bab I — Pendahuluan

1. **Latar belakang:** kebutuhan deteksi objek dengan sumber daya komputasi terbatas; kompresi model; distilasi untuk memindahkan perilaku model teacher ke student. Klaim tentang deployment harus menunggu pengukuran pada perangkat sasaran.
2. **Identifikasi dan rumusan masalah:** rumuskan masalah utama sebagai evaluasi empiris kompresi detector, bukan pengembangan algoritma KD baru.
3. **Tujuan penelitian:** ukur kualitas student pure KD, bandingkan dengan teacher dan kontrol supervised, lalu analisis trade-off ukuran serta inferensi.
4. **Manfaat:** kontribusi empiris yang transparan untuk deteksi robot pada dataset Advance Vision dan prosedur eksperimen yang dapat ditelusuri.
5. **Batasan:** tiga kelas (`ball`, `gawang`, `robot`); split resmi Roboflow; klaim generalisasi pada level gambar di dataset ini. Kemiripan sumber/adegan lintas split membatasi klaim generalisasi ke sesi atau adegan baru.
6. **Sistematika penulisan.**

## Bab II — Tinjauan Pustaka dan Landasan Teori

1. Deteksi objek, bounding box, precision, recall, F1, IoU, mAP50, dan mAP50–95.
2. Keluarga YOLO dan arsitektur YOLO11 yang digunakan; bedakan dokumentasi implementasi dengan sumber akademik primer.
3. Knowledge distillation: teacher/student, target lunak, temperatur, distilasi fitur, dan distilasi keluaran untuk deteksi.
4. Fungsi objektif penelitian: peniruan fitur P3/P4/P5, keluaran box, dan keluaran kelas; jelaskan secara eksplisit bahwa objective KD tidak memakai label ground-truth.
5. Kompresi dan biaya inferensi: parameter, ukuran checkpoint, FLOPs, latensi, throughput, serta keterbatasan masing-masing ukuran sebagai proksi deployment.
6. Penelitian terkait: bandingkan tugas, dataset, arsitektur, target distilasi, penggunaan data berlabel, baseline, dan metrik. Bedakan objective teacher-only seperti DIODE, training pseudo-label teacher seperti Banitalebi-Dehkordi, serta metode hibrida. Bahas metode mutakhir CanKD (WACV 2026) dan FD-CanKD (arXiv 2026) yang tetap memakai loss tugas deteksi. Audit terarah tersedia di [`TINJAUAN_PUSTAKA_KD_DETEKSI.md`](TINJAUAN_PUSTAKA_KD_DETEKSI.md), tetapi bukan systematic review. Posisikan studi sebagai evaluasi terapan, bukan metode KD baru; jangan membuat klaim novelty yang belum didukung telaah sistematis.
7. Kerangka pemikiran dan hipotesis kerja: bandingkan mAP50–95 pure KD dengan supervised pada arsitektur student sama; perlakukan tiga pasangan seed sebagai eksploratif. Bandingkan biaya student KD terhadap teacher secara terpisah. Jangan menyatakan keunggulan ukuran/latensi KD atas supervised yang berarsitektur sama atau memakai hipotesis sebagai hasil.

## Bab III — Metodologi Penelitian

1. **Rancangan eksperimen:** teacher sebagai acuan; dua kelompok student terpisah, yaitu pure KD dan supervised; tiga seed berpasangan `42`, `1337`, `2025`.
2. **Dataset dan datasheet:** sumber Roboflow, lisensi CC BY 4.0, definisi kelas, ukuran split dan distribusi objek, integritas label, preprocessing, fingerprint file, serta provenance yang belum lengkap.
3. **Protokol split:** split resmi Roboflow dipakai karena sesuai keputusan peneliti. Tulis overlap nama sumber/adegan sebagai risiko kemiripan, bukan bukti bahwa seluruh pasangan adalah duplikat. Batas inferensi adalah generalisasi level-gambar, bukan generalisasi sesi baru.
4. **Teacher:** checkpoint FP32 YOLO11n yang dibekukan, hash dan sumbernya; jelaskan provenance historis dan fakta bahwa TEST pernah dipakai untuk evaluasi model lama setelah checkpoint dipilih.
5. **Student:** YAML arsitektur custom, inisialisasi acak, `pretrained=False`, dan jumlah parameter. KD dan baseline supervised memakai arsitektur student yang sama.
6. **Objective pure KD:**

   \[
   L_{KD}=L_{feature}+L_{box}+L_{class}, \qquad T=2.
   \]

   Uraikan teacher forward tanpa gradien, fitur P3/P4/P5, box teacher, soft class teacher, bobot loss, dan bahwa tidak ada GT loss, pseudo-label loss, atau QAT pada student KD.

7. **Kontrol supervised:** objective deteksi supervised dari label TRAIN hanya pada run kontrol terpisah; jangan menyebutnya sebagai bagian dari objective KD.
8. **Resep training:** optimizer, learning rate, warmup, epoch maksimum, early stopping, batch, resolusi, augmentasi, precision, perangkat, versi software, seed, dan pemilihan `best.pt` lewat VAL.
9. **Evaluasi:** metrik utama mAP50–95; metrik pendamping mAP50 dan metrik per kelas. Precision, recall, dan F1 dihitung pada confidence tetap 0,25 serta IoU pencocokan 0,50; confidence floor 0,001 digunakan untuk kurva AP, sedangkan NMS memakai IoU 0,7. Ambang operating point ditetapkan sebelum TEST. TEST hanya dibuka setelah keenam checkpoint student dikunci berdasarkan VAL.
10. **Analisis ukuran dan kecepatan:** parameter, byte checkpoint, FLOPs, latensi median/p95 dan throughput, memakai FP32, batch 1, resolusi 640, frame VAL tetap, warm-up 30 iterasi dan 200 iterasi ukur pada satu perangkat. Simpan sampel mentah latensi dan metadata perangkat. Hasil host L40 adalah diagnostik, bukan bukti real-time pada robot.
11. **Analisis antar-seed dan ketidakpastian TEST:** tampilkan tiap run, mean ± simpangan baku sampel, selisih berpasangan KD–supervised, serta interval bootstrap gambar 95%. Dengan tiga pasangan, inferensi antar-seed bersifat eksploratif.
12. **Reproduksibilitas dan etika data:** simpan konfigurasi, hash, manifest, log dan hasil; patuhi atribusi lisensi dataset; jangan memakai hasil TEST untuk tuning.

## Bab IV — Hasil dan Pembahasan

Gunakan draf hasil terkunci di [`DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`](DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md) dan tabel terverifikasi di [`artifacts/thesis_analysis_final_corrected/`](artifacts/thesis_analysis_final_corrected/). Jangan menyalin angka pilot atau tabel awal sebelum audit hitungan parameter sebagai hasil utama.

1. Hasil audit data dan keterbatasan provenance teacher.
2. Ringkasan training dan pemilihan checkpoint VAL untuk setiap seed.
3. Hasil TEST teacher, pure KD dan supervised, keseluruhan serta per kelas.
4. Perbandingan mean ± simpangan baku dan selisih berpasangan antar-seed.
5. Trade-off mAP, parameter, ukuran checkpoint, FLOPs, latensi dan throughput.
6. Analisis kelas yang paling terdampak kompresi dengan selisih mAP50, mAP50–95, dan recall terhadap teacher serta selisih berpasangan KD–baseline per seed; bahas ketidakseimbangan kelas, jumlah sampel TEST yang terbatas, dan kemungkinan kemiripan sumber/adegan.
7. Implikasi dan batas interpretasi; hasil satu host tidak membuktikan deployment pada perangkat robot.

Tabel minimal: hasil per model/seed, ringkasan per metode, metrik per kelas, delta KD–supervised berpasangan, serta tabel biaya model/inferensi. Semua tabel harus dapat ditelusuri ke CSV/JSON yang dicatat dalam manifest analisis.

## Bab V — Kesimpulan dan Saran

1. Jawab setiap pertanyaan penelitian berdasarkan hasil terkunci, tanpa generalisasi di luar data dan protokol.
2. Nyatakan apakah hipotesis kerja didukung, sebagian didukung, atau tidak didukung oleh bukti.
3. Jelaskan keterbatasan split level-gambar, kemiripan sumber/adegan, provenance dataset teacher, variasi tiga seed, dan perangkat benchmark.
4. Saran lanjutan: split group-held-out serta retraining teacher bila ingin menguji adegan/sesi baru; pengujian pada perangkat robot bila ingin membuat klaim deployment.

## Keterlacakan pertanyaan penelitian ke bukti

| Pertanyaan | Bukti utama | Artefak sumber |
| --- | --- | --- |
| Performa pure KD terhadap teacher dan student supervised | mAP50–95, mAP50, precision, recall, F1 keseluruhan; hasil per run dan ringkasan paired seed | Manifest locked-test, `per_model.csv`, `summary_mean_sd.csv`, `paired_seed_deltas.csv` |
| Trade-off kualitas dan biaya | delta mAP, parameter, byte checkpoint, GFLOPs, median/p95 latensi, throughput | Manifest TEST dan benchmark, `per_model.csv`, `ANALISIS.md` |
| Dampak terhadap kelas | mAP50, mAP50–95, precision, recall dan F1 per kelas; selisih terhadap teacher dan selisih berpasangan KD–baseline | Manifest TEST, `per_model.csv`, `summary_mean_sd.csv`, `paired_seed_deltas.csv`, `paired_summary.csv` |

## Lampiran yang disarankan

- Datasheet dan audit dataset.
- Konfigurasi KD/supervised, YAML arsitektur student, perintah training dan evaluasi.
- Hash fingerprint, checkpoint, konfigurasi, manifest run, serta snapshot skrip KD dan implementasi `DistillationModel`.
- CSV metrik VAL lengkap, manifest TEST, benchmark dan tabel analisis.
- Versi Python, PyTorch, Ultralytics, CUDA, serta perangkat yang digunakan.
- Catatan reproduksi dan daftar keterbatasan/provenance.
