# BAB 6 — PENGUJIAN DAN PEMBAHASAN

> Draf berbasis bukti yang tersedia. Pengujian fungsional berikut adalah penilaian retrospektif, bukan klaim bahwa seluruh skenario dijalankan sebagai uji kotak hitam baru.

## 6.1 Uji fungsional

| ID | Skenario dan keluaran yang diharapkan | Bukti aktual | Penilaian dan batas |
|---|---|---|---|
| KF-01 | Menerima citra dan memproses frame tanpa kesalahan tercatat | T36 mencatat frame dan 0 error frame pada 24 run | Didukung untuk run yang diaudit; tidak membuktikan semua frame kamera diterima |
| KF-02 | Menghasilkan prediksi bola, gawang dan robot | Log kelas enam run Hybrid dan screenshot; [T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) menyediakan pembandingan dengan acuan | Keluaran kelas didukung; benar atau salahnya deteksi harus dinilai dengan label T38, bukan hanya keberadaan kotak |
| KF-03 | Menampilkan ID pada mode pelacakan tambahan dan mempertahankannya ketika objek bergerak | Log ID tersedia pada sebagian run | Kemunculan ID tidak membuktikan kestabilan ID pada objek bergerak. Evaluasi tracking bukan tujuan wajib skripsi; kriteria kestabilan belum dinyatakan lulus |
| KF-04 | Mencatat timestamp dan metrik runtime per frame | 24 CSV jendela ukur tersedia dan dicocokkan dengan T36 | Didukung untuk data dan kolom yang diperiksa |
| KF-05 | Menampilkan preview beranotasi | Screenshot keluaran dan contoh video tersedia | Didukung untuk contoh yang tersedia; bukan bukti preview bebas freeze sepanjang semua run |
| KNF-01 | FPS efektif rata-rata per run ≥8 FPS | Nilai 24 run pada T36 di atas 8 FPS | Lulus untuk kriteria rerata run yang diperiksa; bukan jaminan setiap bin 2 detik ≥8 |

Bukti utama: [audit 24 run](../../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md), [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), dan [media](../../dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/README.md).

## 6.2 Akurasi pada TEST

Nilai student adalah rerata tiga seed; teacher memakai satu checkpoint. F1 adalah harmonic mean precision dan recall makro. TEST terdiri dari 592 gambar dan sudah digunakan pada tahap sebelumnya.

| Model | mAP50 | mAP50–95 | Precision | Recall | F1 utama |
|---|---:|---:|---:|---:|---:|
| Teacher YOLO11n | 0,9642 | 0,7800 | 0,8915 | 0,9697 | 0,9290 |
| Hybrid full | 0,9583 | 0,7469 | 0,8519 | 0,9698 | 0,9071 |
| Supervised | 0,9601 | 0,7225 | 0,8609 | 0,9699 | 0,9121 |
| KD murni | 0,9446 | 0,6630 | 0,7547 | 0,9631 | 0,8462 |

Hybrid memperoleh rerata mAP50–95 lebih tinggi 0,0244 daripada supervised, tetapi F1-nya sekitar 0,005 lebih rendah. Tiga seed mendukung analisis eksploratif, bukan kesimpulan signifikansi yang kuat. Rincian simpangan baku dan sumber: [T05](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

## 6.3 Evaluasi frame kamera OP3 T38

T38 menggunakan 260 frame yang sama untuk empat checkpoint, meliputi 200 frame berobjek dan 60 negatif. Sebanyak 50 frame gawang parsial dilaporkan terpisah. F1 utama dihitung ulang sebagai `2 × precision makro × recall makro / (precision makro + recall makro)` dari nilai presisi penuh CSV T38; F1 pelengkap adalah rerata F1 per kelas yang sudah dilaporkan T38. [CSV turunan dan hash](../../dokumentasi/2026-11-12/T38_F1_D11_turunan.csv) menyimpan angka sebelum pembulatan tampilan; [manifest](../../dokumentasi/2026-11-12/T38_F1_D11_manifest.json) mencatat sumbernya.

| Model | mAP50–95 | Precision makro | Recall makro | F1 utama D11 | F1 per kelas T38 | Frame negatif dengan FP |
|---|---:|---:|---:|---:|---:|---:|
| Teacher | 0,5004 | 0,8690 | 0,6833 | 0,7651 | 0,6829 | 2/60 |
| Hybrid seed 1337 | 0,4885 | 0,6836 | 0,5583 | 0,6146 | 0,5121 | 21/60 |
| Supervised seed 1337 | 0,4414 | 0,7855 | 0,5729 | 0,6626 | 0,6054 | 0/60 |
| KD murni seed 42 | 0,4218 | 0,7386 | 0,4729 | 0,5766 | 0,5008 | 0/60 |

Pada confidence >0,25 dan pencocokan IoU ≥0,5, Hybrid mencocokkan 2 dari 80 kotak gawang, sedangkan supervised 21 dari 80. AP dan recall pada satu ambang menjawab hal berbeda. Set ini retrospektif, label awal dibantu KD murni, berasal dari satu rangkaian dan termasuk sesi objek bergerak; hasil tidak membuktikan generalisasi lintas adegan atau bahwa seluruh set merepresentasikan objek statis. [T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) dan [confusion matrix](../../dokumentasi/model/README.md) memuat detail.

## 6.4 Runtime pada OP3

Nilai berikut adalah rerata ± simpangan baku sampel dari tiga rerata run, bersumber dari [T37](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md).

| Model | Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---|---:|---:|---:|---:|
| Teacher | Diam | 96,24 ± 3,60 | 9,88 ± 0,31 | 1338,90 ± 9,65 | 370,58 ± 1,29 |
| Hybrid | Diam | 64,70 ± 1,92 | 13,60 ± 0,35 | 1305,97 ± 4,91 | 358,87 ± 1,24 |
| Supervised | Diam | 73,12 ± 3,27 | 12,14 ± 0,29 | 1299,18 ± 3,32 | 355,93 ± 3,32 |
| KD murni | Diam | 74,09 ± 1,04 | 12,07 ± 0,05 | 1300,21 ± 2,44 | 356,97 ± 5,92 |
| Teacher | Berjalan | 95,85 ± 1,27 | 9,87 ± 0,17 | 1333,54 ± 4,08 | 372,42 ± 5,11 |
| Hybrid | Berjalan | 71,47 ± 2,98 | 12,54 ± 0,38 | 1303,77 ± 3,88 | 356,31 ± 2,09 |
| Supervised | Berjalan | 70,80 ± 2,71 | 12,64 ± 0,52 | 1301,13 ± 6,03 | 359,16 ± 4,76 |
| KD murni | Berjalan | 72,65 ± 2,55 | 12,21 ± 0,15 | 1295,65 ± 1,35 | 360,18 ± 4,69 |

Pada sampel ini, Hybrid memiliki latensi lebih rendah dan FPS lebih tinggi daripada teacher pada kedua kondisi. CPU semua model sekitar 1.300% satu CPU logis, sehingga bukan pembeda efisiensi yang jelas pada pengukuran ini. RSS hanya mencerminkan proses detektor. Run dikelompokkan lintas hari dan tidak dilakukan serentak; hasil ini tidak membuktikan penyebab perbedaan atau kesetaraan fisik sepenuhnya. [Grafik per waktu dan per ulangan](../../dokumentasi/model/gabungan/README.md) menggunakan bin 2 detik.

## 6.5 Waktu dan ablasi tambahan

[T35](../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) memisahkan waktu training student, satu sesi TEST multi-model, dan benchmark L40. Durasi sesi multi-model bukan durasi per checkpoint; waktu teacher utama dengan provenance setara tidak tersedia. Benchmark server bukan runtime OP3.

Pada VAL T42, teacher YOLO11n/s mencapai mAP50–95 0,7760/0,7843 dan student masing-masing 0,7482 ± 0,0003/0,7473 ± 0,0003. Teacher s yang lebih tinggi tidak menghasilkan rerata mAP student yang lebih tinggi dalam eksperimen ini. T42 memakai teacher yang dilatih ulang, hanya satu teacher per ukuran, dan tiga seed student; ia bukan TEST atau pengganti checkpoint utama. Lihat [T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md).
