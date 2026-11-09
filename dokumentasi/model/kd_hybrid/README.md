# KD Hybrid full seed 1337

Dokumentasi terindeks untuk checkpoint `hybrid_full_seed1337`. SHA-256 checkpoint: `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`. Sumber tabel dan run: [T38](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) dan T36/T37. Tidak ada pengujian baru dalam pembuatan folder ini.

## Akurasi dataset TEST

Evaluasi pada 592 gambar dataset TEST, berbeda dari frame kamera OP3. Nilai teacher memakai satu checkpoint; tiga model student memakai **rerata tiga seed** (42, 1337, 2025), bukan hanya checkpoint OP3 yang menjadi judul halaman ini. F1 dihitung dari precision dan recall makro. Sumber: [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

| mAP50 | mAP50–95 | Precision | Recall | F1 dari P/R makro |
|---:|---:|---:|---:|---:|
| 0.9583 | 0.7469 | 0.8519 | 0.9698 | 0.9071 |

TEST sudah pernah digunakan sebelumnya, dan hasilnya tidak sama dengan hasil kamera OP3 di bawah. Tiga seed memberikan ringkasan deskriptif, sementara teacher hanya satu checkpoint.

## Confusion matrix kamera OP3

- [Jumlah kotak — Indonesia](confusion_matrix_kd_hybrid_jumlah_id.png) · [English](confusion_matrix_kd_hybrid_jumlah_en.png)
- [Persen per kelas acuan — Indonesia](confusion_matrix_kd_hybrid_persen_id.png) · [English](confusion_matrix_kd_hybrid_persen_en.png)
- [Data jumlah CSV](confusion_matrix_kd_hybrid.csv) · [Data persen CSV](confusion_matrix_kd_hybrid_persen.csv) · [Metadata JSON](confusion_matrix_kd_hybrid.json)

Data T38: 260 frame (200 berobjek + 60 negatif), 400 kotak acuan, confidence >0,25, IoU ≥0,5. Baris adalah label acuan; kolom adalah prediksi. Baris latar menunjukkan prediksi tanpa pasangan, termasuk duplikasi atau kotak yang lokasinya tidak mencapai IoU 0,5; tidak berarti semuanya berasal dari frame kosong. Kolom terlewat menunjukkan label tanpa pasangan. Pasangan sekelas ditetapkan sesuai T38, lalu sisa prediksi dan label berbeda kelas dipasangkan berdasarkan IoU. **FP suatu kelas adalah isi kolom kelas selain diagonal; FN adalah isi baris kelas selain diagonal**, sehingga salah kelas turut dihitung sebagai FP dan FN. Persentase hanya dinormalisasi pada tiga baris label, bukan baris latar. Sel latar–latar kosong karena true negative tidak terdefinisi.

| mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro per kelas | Frame negatif dengan FP |
|---:|---:|---:|---:|---:|---:|
| 0.7526 | 0.4885 | 0.6836 | 0.5583 | 0.5121 | 21/60 |

Ini evaluasi retrospektif satu rangkaian; label awal dibantu prediksi KD murni sebelum ditinjau manusia. Hasil bukan bukti generalisasi lintas adegan. Angka pada tabel ini berbeda lingkupnya dari TEST dan metrik runtime live.

## Runtime OP3

Rata-rata ± SD tiga run; sumber T37. CPU adalah persentase satu CPU logis, RSS adalah RAM proses detektor.

| Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---:|---:|---:|---:|
| Diam | 64.70 ± 1.92 | 13.60 ± 0.35 | 1305.97 ± 4.91 | 358.87 ± 1.24 |
| Berjalan | 71.47 ± 2.98 | 12.54 ± 0.38 | 1303.77 ± 3.88 | 356.31 ± 2.09 |

Run dilakukan pada sesi berbeda dan digunakan sebagai analisis deskriptif. Rincian pengukuran serta batasnya ada pada [audit runtime](../../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

## Waktu training

| Seed | Durasi training (jam) |
|---:|---:|
| 42 | 1.344 |
| 1337 | 1.050 |
| 2025 | 1.033 |

Server dipakai bersama dan periode pengujian berbeda.

Sumber dan rincian pengukuran waktu: [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md).

## Grafik dan contoh kamera

[Ringkasan ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_hybrid1337_id.png) · [Overview EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_hybrid1337_en.png) · [Garis waktu ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_hybrid1337_id.png) · [Timeline EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_hybrid1337_en.png) · [Screenshot contoh](../../2026-11-09/visualisasi-tambahan-empat-model/media/hybrid_berjalan_u3_sesudah.png)

Screenshot berasal dari frame sesudah jendela pengukuran berjalan, bukan bukti gerak dari gambar tunggal. Video, bila ada, adalah sesi Supervised lain dengan kondisi fisik `unknown`. [Indeks empat model](../README.md).
