# KD Murni seed 42

Dokumentasi terindeks untuk checkpoint `kd_seed42`. SHA-256 checkpoint: `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`. Sumber tabel dan run: [T38](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) dan T36/T37. Tidak ada pengujian baru dalam pembuatan folder ini.

## Akurasi dataset TEST

Evaluasi pada 592 gambar dataset TEST, berbeda dari frame kamera OP3. Nilai teacher memakai satu checkpoint; tiga model student memakai **rerata tiga seed** (42, 1337, 2025), bukan hanya checkpoint OP3 yang menjadi judul halaman ini. F1 dihitung dari precision dan recall makro. Sumber: [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md).

| mAP50 | mAP50–95 | Precision | Recall | F1 dari P/R makro |
|---:|---:|---:|---:|---:|
| 0.9446 | 0.6630 | 0.7547 | 0.9631 | 0.8462 |

TEST sudah pernah digunakan sebelumnya, dan hasilnya tidak sama dengan hasil kamera OP3 di bawah. Tiga seed memberikan ringkasan deskriptif, sementara teacher hanya satu checkpoint.

## Confusion matrix kamera OP3

- [Jumlah kotak — Indonesia](confusion_matrix_kd_murni_jumlah_id.png) · [English](confusion_matrix_kd_murni_jumlah_en.png)
- [Persen per kelas acuan — Indonesia](confusion_matrix_kd_murni_persen_id.png) · [English](confusion_matrix_kd_murni_persen_en.png)
- [Data jumlah CSV](confusion_matrix_kd_murni.csv) · [Data persen CSV](confusion_matrix_kd_murni_persen.csv) · [Metadata JSON](confusion_matrix_kd_murni.json)

Data T38: 260 frame (200 berobjek + 60 negatif), 400 kotak acuan, confidence >0,25, IoU ≥0,5. Baris adalah label acuan; kolom adalah prediksi. Baris latar menunjukkan prediksi tanpa pasangan, termasuk duplikasi atau kotak yang lokasinya tidak mencapai IoU 0,5; tidak berarti semuanya berasal dari frame kosong. Kolom terlewat menunjukkan label tanpa pasangan. Pasangan sekelas ditetapkan sesuai T38, lalu sisa prediksi dan label berbeda kelas dipasangkan berdasarkan IoU. **FP suatu kelas adalah isi kolom kelas selain diagonal; FN adalah isi baris kelas selain diagonal**, sehingga salah kelas turut dihitung sebagai FP dan FN. Persentase hanya dinormalisasi pada tiga baris label, bukan baris latar. Sel latar–latar kosong karena true negative tidak terdefinisi.

| mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro per kelas | Frame negatif dengan FP |
|---:|---:|---:|---:|---:|---:|
| 0.6301 | 0.4218 | 0.7386 | 0.4729 | 0.5008 | 0/60 |

Ini evaluasi retrospektif satu rangkaian; label awal dibantu prediksi KD murni sebelum ditinjau manusia. Hasil bukan bukti generalisasi lintas adegan. Angka pada tabel ini berbeda lingkupnya dari TEST dan metrik runtime live.

## Runtime OP3

Rata-rata ± SD tiga run; sumber T37. CPU adalah persentase satu CPU logis, RSS adalah RAM proses detektor.

| Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---:|---:|---:|---:|
| Diam | 74.09 ± 1.04 | 12.07 ± 0.05 | 1300.21 ± 2.44 | 356.97 ± 5.92 |
| Berjalan | 72.65 ± 2.55 | 12.21 ± 0.15 | 1295.65 ± 1.35 | 360.18 ± 4.69 |

Run dilakukan pada sesi berbeda dan digunakan sebagai analisis deskriptif. Rincian pengukuran serta batasnya ada pada [audit runtime](../../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md).

## Waktu training

| Seed | Durasi training (jam) |
|---:|---:|
| 42 | 5.341 |
| 1337 | 2.934 |
| 2025 | 2.974 |

Server dipakai bersama dan periode pengujian berbeda.

Sumber dan rincian pengukuran waktu: [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md).

## Grafik dan contoh kamera

[Ringkasan ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_kd42_id.png) · [Overview EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/08_ringkasan_kd42_en.png) · [Garis waktu ID](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_kd42_id.png) · [Timeline EN](../../2026-11-09/visualisasi-tambahan-empat-model/grafik-final/09_garis_waktu_kd42_en.png) · [Screenshot contoh](../../2026-11-09/visualisasi-tambahan-empat-model/media/kd_murni_berjalan_u3_sesudah.png)

Screenshot berasal dari frame sesudah jendela pengukuran berjalan, bukan bukti gerak dari gambar tunggal. Video, bila ada, adalah sesi Supervised lain dengan kondisi fisik `unknown`. [Indeks empat model](../README.md).

## Grafik garis kontinu (11 November 2026)

- **Akurasi VAL per epoch** (mAP50, mAP50–95, precision, recall, F1; tiga seed, seed 42 yang dipakai di robot ditebalkan): [Indonesia](garis_akurasi_val_per_epoch_kd_murni_id.png) · [English](garis_akurasi_val_per_epoch_kd_murni_en.png). Bukti pendukung rumusan masalah 2 dan 3 dari sisi pelatihan.
- **Precision, recall, dan F1 terhadap ambang confidence (VAL):** [Indonesia](garis_sapuan_confidence_val_kd_murni_id.png) · [English](garis_sapuan_confidence_val_kd_murni_en.png).
- **Runtime OP3 (latensi, FPS, CPU, RSS) per waktu:** belum dibuat. Dari 24 berkas `jendela_runtime.csv` run aktif T36, 15 berkas sesi 3 November belum ada di repo dan masih di robot. Grafik dibuat dengan `--bagian runtime` setelah berkas itu tersedia.

Definisi: kurva per epoch memakai VAL (1.213 gambar) yang tercatat saat training, bukan TEST dan bukan confidence 0,25. Precision dan recall per epoch adalah keluaran validator Ultralytics 8.4.130 pada confidence yang memaksimalkan F1 rata-rata; F1 dihitung sebagai rerata harmonik keduanya. Sapuan confidence berasal dari T11 (VAL, IoU pencocokan 0,5). Hash sumber dan keluaran ada di [manifest](../manifest_grafik_garis_akurasi.json); generator `scripts/build_grafik_garis_model_20261111.py`.
