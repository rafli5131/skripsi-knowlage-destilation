# Log progres - 13 November 2026

## Analisis menyeluruh folder skripsi

Seluruh folder `E:\Kuliah\Thesis` ditinjau: repo eksperimen, proposal KD (`Proposal_KD_OP3_v1.docx`), dua skripsi kakak tingkat, 64 PDF di folder Paper, template, dan acuan bahasa. Temuan utama yang memengaruhi naskah:

- Draf tujuh bab di `laporan/draf-7-bab/` masih kerangka; naskah akhir disusun dari Bab 1 sampai 3 proposal ditambah Bab 4 sampai 7 baru dengan pola skripsi Ivan Rafli Adipratama (2026).
- Model KD utama (Hybrid seed 1337) lebih tinggi mAP50-95 TEST, tetapi pada T38 menghasilkan FP pada 21/60 frame negatif dan hanya 2/80 gawang utuh; narasi Bab 6 berbentuk *trade-off*.
- Selisih latensi antar-student berarsitektur identik tidak dapat diatribusikan pada KD.
- Penyimpangan dari protokol proposal (urutan run blok lintas hari, set frame OP3) perlu ditulis terbuka.
- KF-03 tetap seperti yang sudah di-ACC; tidak diubah atau dipindah.

## Verifikasi jalur inferensi TEST (D23)

`scripts/verify_test_inference_path.py` (commit `f9647ae`) dijalankan di server `labkc-l40-debian` pada CPU untuk sembilan student; hasil di [`analisis_performa/lab_server/verifikasi_jalur_test_20261113/`](../../analisis_performa/lab_server/verifikasi_jalur_test_20261113/RINGKASAN.md) (commit `b097e40`). Sidik jari TEST cocok 592/592 gambar dan label; hash keempat berkas hasil cocok dengan manifest.

| Kelompok | mAP50-95 resmi / predict | F1 resmi / predict / runtime |
|---|---|---|
| KD Hybrid full | 0,7469 / 0,7434 | 0,9071 / 0,9090 / 0,9334 |
| Supervised | 0,7225 / 0,7248 | 0,9121 / 0,9098 / 0,9337 |
| KD murni | 0,6630 / 0,6647 | 0,8462 / 0,8467 / 0,9203 |

- Pada ambang yang sama, selisih per checkpoint maksimum 0,0076 (mAP50-95) dan 0,0101 (F1); urutan mAP50-95 tidak berubah.
- Jalur validator TEST memakai tensor 672 x 672 (`rect`, `pad=0.5`) dan NMS `multi_label=True`; jalur prediksi 640 x 640 tanpa multi-label. Perbedaan jalur ada, tetapi pengaruhnya kecil pada TEST. Bentuk 672 x 672 diperiksa pada Ultralytics 8.4.130 dengan dataset uji kecil, bukan dari log server.
- Pada pengaturan runtime (0,25 dan 0,45), F1 naik 0,02 sampai 0,07, terutama dari precision: prediksi gawang yang lolos turun dari sekitar 680 menjadi sekitar 560 per model dengan TP gawang hanya turun 3 sampai 11.
- Selisih F1 Hybrid dikurangi supervised: -0,0050 (resmi), -0,0008 (predict), -0,0003 (runtime). Untuk naskah, F1 keduanya lebih tepat disebut setara.
- Teacher belum dievaluasi karena bobot utama hanya tersimpan di OP3.

## Langkah berikutnya

1. Sesi OP3 offline dengan [prompt 13 November](../../prompt/PROMPT_SESI_OP3_OFFLINE_JALUR_TUNGGAL_DAN_RUNTIME_2026-11-13.md): salin teacher utama, jalur tunggal T38/T43 dengan pemisahan faktor padding dan NMS, rincian latensi per tahap 24 run, serta diagnosis CPU sekitar 1.300%.
2. Lengkapi baris teacher pada verifikasi TEST setelah bobot teacher tersalin ke server.
3. Konsultasi pembimbing: set frame OP3 utama dan narasi hasil.
4. Naskah: Bab 4 dan 5 dapat disusun sekarang; Bab 6 menunggu hasil langkah 1.
5. Referensi: entri Jacob dkk. diubah ke versi CVPR 2018, empat nama berkas "et al." dirapikan, dan lima paper baru diunduh.

Catatan infrastruktur: repo berada di akun GitHub `rafli5131`, dan dataset di server berada di NAS akun `dindarosyidah`. Keduanya bukan milik Bhre, sehingga salinan cadangan disarankan.
