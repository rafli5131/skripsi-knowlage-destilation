# Teacher YOLO11n

Dokumentasi terindeks untuk checkpoint `teacher_fp32`. SHA-256 checkpoint: `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Sumber tabel dan run: [T38](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) dan T36/T37. Tidak ada pengujian baru dalam pembuatan folder ini.

## Akurasi dataset TEST

Evaluasi pada 592 gambar dataset TEST, berbeda dari frame kamera OP3. Nilai teacher memakai satu checkpoint; tiga model student memakai **rerata tiga seed** (42, 1337, 2025), bukan hanya checkpoint OP3 yang menjadi judul halaman ini. F1 dihitung dari precision dan recall makro. Sumber: [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

| mAP50 | mAP50–95 | Precision | Recall | F1 dari P/R makro |
|---:|---:|---:|---:|---:|
| 0.9642 | 0.7800 | 0.8915 | 0.9697 | 0.9290 |

TEST sudah pernah digunakan sebelumnya, dan hasilnya tidak sama dengan hasil kamera OP3 di bawah. Tiga seed memberikan ringkasan deskriptif, sementara teacher hanya satu checkpoint.

## Confusion matrix kamera OP3

- [Jumlah kotak — Indonesia](confusion_matrix_teacher_yolo11n_jumlah_id.png) · [English](confusion_matrix_teacher_yolo11n_jumlah_en.png)
- [Persen per kelas acuan — Indonesia](confusion_matrix_teacher_yolo11n_persen_id.png) · [English](confusion_matrix_teacher_yolo11n_persen_en.png)
- [Data jumlah CSV](confusion_matrix_teacher_yolo11n.csv) · [Data persen CSV](confusion_matrix_teacher_yolo11n_persen.csv) · [Metadata JSON](confusion_matrix_teacher_yolo11n.json)

Data T38: 260 frame (200 berobjek + 60 negatif), 400 kotak acuan, confidence >0,25, IoU ≥0,5. Baris adalah label acuan; kolom adalah prediksi. Baris latar menunjukkan prediksi tanpa pasangan, termasuk duplikasi atau kotak yang lokasinya tidak mencapai IoU 0,5; tidak berarti semuanya berasal dari frame kosong. Kolom terlewat menunjukkan label tanpa pasangan. Pasangan sekelas ditetapkan sesuai T38, lalu sisa prediksi dan label berbeda kelas dipasangkan berdasarkan IoU. **FP suatu kelas adalah isi kolom kelas selain diagonal; FN adalah isi baris kelas selain diagonal**, sehingga salah kelas turut dihitung sebagai FP dan FN. Persentase hanya dinormalisasi pada tiga baris label, bukan baris latar. Sel latar–latar kosong karena true negative tidak terdefinisi.

| mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro per kelas | Frame negatif dengan FP |
|---:|---:|---:|---:|---:|---:|
| 0.7058 | 0.5004 | 0.8690 | 0.6833 | 0.6829 | 2/60 |

Ini evaluasi retrospektif satu rangkaian; label awal dibantu prediksi KD murni sebelum ditinjau manusia. Hasil bukan bukti generalisasi lintas adegan. Angka pada tabel ini berbeda lingkupnya dari TEST dan metrik runtime live.

## Runtime OP3

Rata-rata ± SD tiga run; sumber T37. CPU adalah persentase satu CPU logis, RSS adalah RAM proses detektor.

| Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---:|---:|---:|---:|
| Diam | 96.24 ± 3.60 | 9.88 ± 0.31 | 1338.90 ± 9.65 | 370.58 ± 1.29 |
| Berjalan | 95.85 ± 1.27 | 9.87 ± 0.17 | 1333.54 ± 4.08 | 372.42 ± 5.11 |

Run dilakukan pada sesi berbeda dan digunakan sebagai analisis deskriptif. Rincian pengukuran serta batasnya ada pada [audit runtime](../../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

## Waktu training

Durasi training teacher utama dengan provenance setara tidak tersedia. Waktu teacher yang dilatih ulang dalam T42 adalah eksperimen berbeda dan tidak menggantikan angka ini.

Sumber dan rincian pengukuran waktu: [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md).

## Grafik dan contoh kamera

[Ringkasan ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_teacher_id.png) · [Overview EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_teacher_en.png) · [Garis waktu ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_teacher_id.png) · [Timeline EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_teacher_en.png) · [Screenshot contoh](../../2026-11-09/visualisasi-tambahan-empat-model/media/teacher_berjalan_u1_sesudah.png)

Screenshot berasal dari frame sesudah jendela pengukuran berjalan, bukan bukti gerak dari gambar tunggal. Video, bila ada, adalah sesi Supervised lain dengan kondisi fisik `unknown`. [Indeks empat model](../README.md).

## Grafik garis kontinu (11 November 2026)

- **Akurasi per epoch:** tidak tersedia. Kurva training teacher utama tidak ada di repo karena teacher dilatih di repositori lain pada server lama.
- **Precision, recall, dan F1 terhadap ambang confidence (VAL):** [Indonesia](garis_sapuan_confidence_val_teacher_yolo11n_id.png) · [English](garis_sapuan_confidence_val_teacher_yolo11n_en.png).
- **Runtime OP3 (latensi, FPS, CPU, RSS) per waktu:** [Indonesia](garis_runtime_op3_teacher_yolo11n_id.png) · [English](garis_runtime_op3_teacher_yolo11n_en.png) · [manifest](../manifest_grafik_garis_runtime.json). Per bin 2 detik; batas 8 FPS dievaluasi sebagai rerata run, bukan jaminan setiap bin.

Definisi: kurva per epoch memakai VAL (1.213 gambar) yang tercatat saat training, bukan TEST dan bukan confidence 0,25. Precision dan recall per epoch adalah keluaran validator Ultralytics 8.4.130 pada confidence yang memaksimalkan F1 rata-rata; F1 dihitung sebagai rerata harmonik keduanya. Sapuan confidence berasal dari T11 (VAL, IoU pencocokan 0,5). Hash sumber dan keluaran ada di [manifest](../manifest_grafik_garis_akurasi.json); generator `scripts/build_grafik_garis_model_20261111.py`.

> **Audit 12 November:** hash 18 grafik akurasi/sapuan pada manifest 11 November tidak cocok dengan file sejak commit asal. Sumber dan data gabungan cocok; lihat [audit serta hash aktual](../../2026-11-12/AUDIT_GRAFIK_AKURASI.md). Grafik runtime memiliki manifest terpisah.
