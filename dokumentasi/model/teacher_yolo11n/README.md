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
