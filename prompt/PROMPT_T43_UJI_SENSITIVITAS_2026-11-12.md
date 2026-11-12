# Prompt uji sensitivitas T43: sapuan confidence, peninjau kedua, dan konvensi kotak alternatif

Tanggal: 12 November 2026. Dijalankan oleh agen di **komputer OP3**, karena frame, label, dan prediksi T43 tersimpan lokal di sana. Pekerjaan ini **offline**: tanpa kamera, detektor live, servo, torque, modul, action, atau gait. Tidak ada pelatihan dan tidak ada perekaman frame baru.

## Tujuan

Menguji dua kelemahan T43 tanpa membuat set baru:

1. **Bagian A, sapuan confidence.** Apakah selisih F1 antarmodel pada T43 berasal dari confidence pada gawang parsial, bukan dari kemampuan menemukan objek. Dasar dugaan: AP50 gawang teacher, Hybrid, dan supervised sama-sama 0,995, tetapi gawang yang lolos confidence > 0,25 hanya 0/200, 196/200, dan 99/200 (KD murni 0/200, AP50 0,608).
2. **Bagian B, sensitivitas label pada 52 frame sampel.** Seberapa besar kesepakatan dengan peninjau kedua, dan apakah urutan model berubah bila gawang dan robot diberi kotak dengan konvensi lain.

## Larangan

- Tidak ada perintah gerak, kamera, atau detektor live. Bila suatu langkah tampak membutuhkannya, berhenti dan laporkan.
- Jangan mengubah label, prediksi, manifest, atau hasil T43 yang sudah dibekukan (`data/op3_camera_eval/experiments/t43_20261112/`, `runs/op3_t43_evaluation/20261112_reviewed_260/`). Semua keluaran baru ditulis ke direktori baru.
- Jangan mengubah checkpoint, ambang, atau parameter evaluasi T43, dan jangan memilih ulang model dari hasil ini.
- Kode baru dibuat sebagai package baru (`ros2_packages/op3_t43_sensitivity/`); package lama hanya dipakai sebagai fungsi bersama tanpa diubah.
- Frame, label, dan prediksi per frame tetap lokal. *Commit* dan push tabel atau dokumentasi hanya bila Bhre memintanya.
- Bila tidak yakin pada fakta teknis, katakan tidak yakin. Jangan merekonstruksi data yang tidak ada.

## Persiapan

1. `git status --short`; bila bersih, `git pull --ff-only origin main`. Baca `agent.md`, `docs/DECISIONS.md` (D19 dan seterusnya), `analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md`, `dokumentasi/2026-11-12/percobaan-38-t43-persiapan/README_ID.md`, `dokumentasi/2026-11-12/percobaan-38-t43-persiapan/AUDIT_REVIEW_52_SEMENTARA.md`, dan `ros2_packages/op3_t43_evaluation/`.
2. Verifikasi hash: keempat checkpoint, `review_260_audit_and_frozen_hashes.json`, `capture_260_manifest.json`, `blind_review_52/selection_manifest.json`, dan `runs/op3_t43_evaluation/20261112_reviewed_260/results.json`. Bila ada yang berbeda, berhenti dan laporkan.

## Bagian A. Sapuan confidence pada 260 frame (tanpa orang tambahan)

3. Gunakan prediksi per frame T43 yang sudah tersimpan (confidence floor 0,001, NMS IoU 0,7). Bila prediksi per frame tidak tersimpan, hitung ulang dengan fungsi `op3_t43_evaluation` dan `op3_multi_session_eval` yang sama, lalu pastikan AP dan angka pada confidence 0,25 identik dengan `results.json`. Bila tidak identik, berhenti dan laporkan.
4. Untuk setiap model, kelas, dan kondisi (diam, berjalan, gabungan), hitung precision, recall, F1, TP, FP, FN pada ambang confidence 0,05 sampai 0,90 dengan langkah 0,05 (grid sama dengan T11), pencocokan IoU ≥ 0,5 dengan aturan yang sama seperti T43. Catat juga sebaran confidence prediksi gawang yang cocok dengan label (median, kuartil, minimum, maksimum) per model.
5. Laporkan untuk gawang: ambang tertinggi di mana recall gawang ≥ 0,9 per model, dan apakah teacher serta supervised mencapai recall gawang setara Hybrid pada ambang yang lebih rendah. Tandai bahwa ambang operasi tetap 0,25 (D4); sapuan ini analisis, bukan pemilihan ambang baru.

## Bagian B. Sensitivitas label pada 52 frame sampel

Bagian ini membutuhkan dua sesi pelabelan oleh manusia. Tunjukkan instruksi kepada Bhre dan tunggu konfirmasi sebelum tiap sesi.

6. **Aturan tertulis dibekukan dulu.** Sebelum peninjau kedua mulai, minta Bhre menulis aturan kotak dalam satu sampai tiga kalimat per kelas, sesuai konvensi T43 (bola utuh; gawang bagian bawah dengan batas atas yang jelas, misalnya landmark tertentu pada rangka; robot hanya badan). Simpan sebagai `rules_konvensi_t43.json` beserta hash dan waktu UTC, sebelum peninjau kedua melihat gambar.
7. **Peninjau kedua.** Satu orang selain Bhre melabeli 52 frame dari `blind_review_52/selection_manifest.json` dengan `op3_blind_label_reviewer`, identitas peninjau terpisah (misalnya `peninjau2`), tanpa kotak prediksi dan tanpa melihat label Bhre, mengikuti aturan langkah 6. Simpan di direktori baru, misalnya `data/op3_camera_eval/experiments/t43_sensitivity_<tanggal>/reviewer2/`.
8. **Konvensi alternatif.** Pada 52 frame yang sama, buat label kedua untuk konvensi alternatif: gawang = satu kotak yang melingkupi seluruh rangka yang terlihat (dibatasi tepi gambar), robot = seluruh tubuh robot yang terlihat, bola tetap. Tulis aturan ini lebih dulu seperti langkah 6. Pelabel boleh Bhre atau peninjau kedua; catat siapa. Simpan di `.../alternative_convention/`.
9. **Kesepakatan antarpeninjau.** Bandingkan label Bhre (versi final T43 untuk 52 frame tersebut) dengan label `peninjau2`: per kelas, proporsi kotak yang berpasangan pada IoU ≥ 0,5, IoU rata-rata dan median pasangan, serta jumlah kotak tanpa pasangan. Laporkan apa adanya.
10. **Evaluasi ulang keempat model pada 52 frame** dengan tiga set label: (a) label final Bhre, (b) label `peninjau2`, (c) konvensi alternatif. Parameter sama dengan T43. Laporkan mAP50, mAP50–95, precision, recall, F1 utama (D11), dan TP gawang pada confidence > 0,25 per model, serta urutan model untuk tiap set label. Tegaskan bahwa 52 frame berurutan dari satu adegan, sehingga hasilnya deskriptif.

## Keluaran dan laporan

11. Tulis tabel `analisis_performa/tabel/T43_sensitivitas_confidence.{csv,md}` dan `analisis_performa/tabel/T43_sensitivitas_label_52.{csv,md}`, grafik garis sapuan confidence per kelas untuk keempat model (versi Indonesia dan Inggris), serta dokumentasi `dokumentasi/<tanggal>/percobaan-<nomor berikutnya>-sensitivitas-t43/README_ID.md` dan `README_EN.md` yang memuat metode, aturan tertulis, identitas pelabel, hasil, dan keterbatasan. Simpan manifest hash sumber dan keluaran.
12. Tambahkan bagian singkat pada `analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md` yang menautkan kedua tabel sensitivitas, tanpa mengubah angka T43.
13. Laporkan kepada Bhre: ringkasan Bagian A dan B, apakah urutan model berubah antarset label, `git status --short`, dan tanyakan apa yang boleh di-*commit* dan di-push.

## Cara membaca hasil

- Bila teacher dan supervised mencapai recall gawang mendekati Hybrid pada ambang lebih rendah, selisih F1 T43 terutama soal kalibrasi confidence pada gawang parsial.
- Bila urutan model sama pada label Bhre, `peninjau2`, dan konvensi alternatif, pengaruh konvensi dan peninjau terhadap kesimpulan kecil. Bila urutan berubah, klaim T43 dibatasi pada konvensi yang dipakai dan perubahan itu dilaporkan.
