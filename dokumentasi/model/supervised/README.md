# Supervised seed 1337

Dokumentasi terindeks untuk checkpoint `supervised_seed1337`. SHA-256 checkpoint: `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041`. Sumber tabel dan run: [T38](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) dan T36/T37. Tidak ada pengujian baru dalam pembuatan folder ini.

## Akurasi dataset TEST

Evaluasi pada 592 gambar dataset TEST, berbeda dari frame kamera OP3. Nilai teacher memakai satu checkpoint; tiga model student memakai **rerata tiga seed** (42, 1337, 2025), bukan hanya checkpoint OP3 yang menjadi judul halaman ini. F1 dihitung dari precision dan recall makro. Sumber: [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

| mAP50 | mAP50–95 | Precision | Recall | F1 dari P/R makro |
|---:|---:|---:|---:|---:|
| 0.9601 | 0.7225 | 0.8609 | 0.9699 | 0.9121 |

TEST sudah pernah digunakan sebelumnya, dan hasilnya tidak sama dengan hasil kamera OP3 di bawah. Tiga seed memberikan ringkasan deskriptif, sementara teacher hanya satu checkpoint.

## Confusion matrix kamera OP3

- [Jumlah kotak — Indonesia](confusion_matrix_supervised_jumlah_id.png) · [English](confusion_matrix_supervised_jumlah_en.png)
- [Persen per kelas acuan — Indonesia](confusion_matrix_supervised_persen_id.png) · [English](confusion_matrix_supervised_persen_en.png)
- [Data jumlah CSV](confusion_matrix_supervised.csv) · [Data persen CSV](confusion_matrix_supervised_persen.csv) · [Metadata JSON](confusion_matrix_supervised.json)

Data T38: 260 frame (200 berobjek + 60 negatif), 400 kotak acuan, confidence >0,25, IoU ≥0,5. Baris adalah label acuan; kolom adalah prediksi. Baris latar menunjukkan prediksi tanpa pasangan, termasuk duplikasi atau kotak yang lokasinya tidak mencapai IoU 0,5; tidak berarti semuanya berasal dari frame kosong. Kolom terlewat menunjukkan label tanpa pasangan. Pasangan sekelas ditetapkan sesuai T38, lalu sisa prediksi dan label berbeda kelas dipasangkan berdasarkan IoU. **FP suatu kelas adalah isi kolom kelas selain diagonal; FN adalah isi baris kelas selain diagonal**, sehingga salah kelas turut dihitung sebagai FP dan FN. Persentase hanya dinormalisasi pada tiga baris label, bukan baris latar. Sel latar–latar kosong karena true negative tidak terdefinisi.

| mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro per kelas | Frame negatif dengan FP |
|---:|---:|---:|---:|---:|---:|
| 0.7045 | 0.4414 | 0.7855 | 0.5729 | 0.6054 | 0/60 |

Ini evaluasi retrospektif satu rangkaian; label awal dibantu prediksi KD murni sebelum ditinjau manusia. Hasil bukan bukti generalisasi lintas adegan. Angka pada tabel ini berbeda lingkupnya dari TEST dan metrik runtime live.

## Runtime OP3

Rata-rata ± SD tiga run; sumber T37. CPU adalah persentase satu CPU logis, RSS adalah RAM proses detektor.

| Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---:|---:|---:|---:|
| Diam | 73.12 ± 3.27 | 12.14 ± 0.29 | 1299.18 ± 3.32 | 355.93 ± 3.32 |
| Berjalan | 70.80 ± 2.71 | 12.64 ± 0.52 | 1301.13 ± 6.03 | 359.16 ± 4.76 |

Run dilakukan pada sesi berbeda dan digunakan sebagai analisis deskriptif. Rincian pengukuran serta batasnya ada pada [audit runtime](../../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

## Waktu training

| Seed | Durasi training (jam) |
|---:|---:|
| 42 | 5.597 |
| 1337 | 3.734 |
| 2025 | 3.234 |

Server dipakai bersama dan periode pengujian berbeda. Durasi seed 1337 menjumlahkan dua segmen dan mengecualikan jeda interupsi.

Sumber dan rincian pengukuran waktu: [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md).

## Grafik dan contoh kamera

[Ringkasan ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_sup1337_id.png) · [Overview EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_sup1337_en.png) · [Garis waktu ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_sup1337_id.png) · [Timeline EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_sup1337_en.png) · [Screenshot contoh](../../2026-11-09/visualisasi-tambahan-empat-model/media/supervised_berjalan_u1_sesudah.png) · [Video deteksi 10 detik](../../2026-11-09/visualisasi-tambahan-empat-model/media/supervised_deteksi_tracking_10detik.mp4)

Screenshot berasal dari frame sesudah jendela pengukuran berjalan, bukan bukti gerak dari gambar tunggal. Video, bila ada, adalah sesi Supervised lain dengan kondisi fisik `unknown`. [Indeks empat model](../README.md).

## Grafik garis kontinu (11 November 2026)

- **Akurasi VAL per epoch** (mAP50, mAP50–95, precision, recall, F1; tiga seed, seed 1337 yang dipakai di robot ditebalkan): [Indonesia](garis_akurasi_val_per_epoch_supervised_id.png) · [English](garis_akurasi_val_per_epoch_supervised_en.png). Bukti pendukung rumusan masalah 2 dan 3 dari sisi pelatihan.
- **Precision, recall, dan F1 terhadap ambang confidence (VAL):** [Indonesia](garis_sapuan_confidence_val_supervised_id.png) · [English](garis_sapuan_confidence_val_supervised_en.png).
- **Runtime OP3 (latensi, FPS, CPU, RSS) per waktu:** [Indonesia](garis_runtime_op3_supervised_id.png) · [English](garis_runtime_op3_supervised_en.png) · [manifest](../manifest_grafik_garis_runtime.json). Per bin 2 detik; batas 8 FPS dievaluasi sebagai rerata run, bukan jaminan setiap bin.

Definisi: kurva per epoch memakai VAL (1.213 gambar) yang tercatat saat training, bukan TEST dan bukan confidence 0,25. Precision dan recall per epoch adalah keluaran validator Ultralytics 8.4.130 pada confidence yang memaksimalkan F1 rata-rata; F1 dihitung sebagai rerata harmonik keduanya. Sapuan confidence berasal dari T11 (VAL, IoU pencocokan 0,5). Hash sumber dan keluaran ada di [manifest](../manifest_grafik_garis_akurasi.json); generator `scripts/build_grafik_garis_model_20261111.py`.

> **Audit 12 November:** hash 18 grafik akurasi/sapuan pada manifest 11 November tidak cocok dengan file sejak commit asal. Sumber dan data gabungan cocok; lihat [audit serta hash aktual](../../2026-11-12/AUDIT_GRAFIK_AKURASI.md). Grafik runtime memiliki manifest terpisah.
