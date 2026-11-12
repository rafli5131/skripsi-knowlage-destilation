# Indeks dokumentasi percobaan OP3

> **12 November 2026:** [Log progres](2026-11-12/LOG_PROGRES_SKRIPSI.md) · [audit hash](2026-11-12/AUDIT_GRAFIK_AKURASI.md) · [grafik akurasi reproduksi](2026-11-12/grafik-akurasi-terverifikasi/README.md) · [grafik runtime](model/README.md) · [draf tujuh bab](../laporan/draf-7-bab/README.md).

> **11 November 2026:** [Log progres](2026-11-11/LOG_PROGRES_SKRIPSI.md) · [grafik garis kontinu akurasi per model](model/README.md) · keputusan D17 (tujuh bab), D18 (persetujuan pembimbing), dan D19 (rencana set frame baru) di [`DECISIONS.md`](../docs/DECISIONS.md).

> **9 November 2026:** [Draf Bab IV–V dan arsip](../laporan/draf-bab-iv-v/README.md) · [Log progres skripsi](2026-11-09/LOG_PROGRES_SKRIPSI.md) · [Matriks bukti dan celah](2026-11-09/MATRIKS_BUKTI_DAN_CELAH.md).

> [Dokumentasi per model dan confusion matrix](model/README.md): Teacher, KD Hybrid, Supervised, KD Murni, serta perbandingan gabungan.

> **9 November 2026:** [Grafik tambahan empat model, screenshot, dan cuplikan video](2026-11-09/visualisasi-tambahan-empat-model/README.md) sudah tersedia di repositori.

> [Audit integritas hasil](2026-11-09/AUDIT_INTEGRITAS_HASIL.md) merangkum pemeriksaan dan batas sumber yang tersedia.

> **5 November 2026:** [Percobaan 37 — T38 empat model pada 260 frame OP3](2026-11-05/percobaan-37-evaluasi-t38-empat-model/README_ID.md) selesai secara offline; hasil bersifat eksploratif dan retrospektif.

> Pembaruan terbaru: [audit 24 run, T36/T37 dan batas protokol](2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md); seluruh cek log/telemetry lulus, pengesahan kesetaraan fisik masih terbuka. Status terdahulu di bawah merupakan snapshot historis.

> Arsip progres: [pengganti KD murni berjalan ulangan 3](2026-11-03/percobaan-35-kd-murni-berjalan-3-ulangan/04-kd-murni/walk-u3-ulang1/README_ID.md) lulus cek otomatis; 24/24 slot aktif lulus cek otomatis. Audit protokol akhir masih terbuka; status di bawah adalah snapshot sebelumnya.

> Arsip progres: [KD murni berjalan tiga ulangan](2026-11-03/percobaan-35-kd-murni-berjalan-3-ulangan/README_ID.md) selesai; 24/24 slot terukur, 23 lulus cek otomatis dan satu perlu audit. Status sebelumnya di bawah merupakan snapshot historis.

> Arsip progres: [KD murni idle tiga ulangan](2026-11-03/percobaan-34-kd-murni-idle-3-ulangan/README_ID.md) selesai; kampanye 21/24 slot. Status sebelumnya di bawah adalah snapshot historis.

> Arsip progres: [Supervised berjalan tiga ulangan](2026-11-03/percobaan-33-supervised-berjalan-3-ulangan/README_ID.md) selesai; kampanye 18/24 slot. Status di bawah merupakan snapshot sebelumnya.

> Arsip progres: [Supervised idle tiga ulangan](2026-11-03/percobaan-32-supervised-idle-3-ulangan/README_ID.md) selesai; kampanye 15/24 slot. Pernyataan 12/24 di bawah adalah snapshot sebelumnya.

Laporan per percobaan ditautkan di bawah. Isi folder berbeda-beda: ringkasan metode dan hasil, grafik, contoh gambar/audit visual, serta tautan ke CSV dan metadata JSON jika artefaknya tersedia. Data mentah berada di `runs/`; tabel evaluasi model dan analisis performa berada di [`../analisis_performa/INDEKS.md`](../analisis_performa/INDEKS.md).

Versi GitHub memuat laporan, tabel, grafik analisis, dan metadata hasil yang dikurasi. Rujukan bertanda **lokal** menunjuk log mentah, snapshot kamera, atau video yang disimpan pada checkout robot; berkas tersebut tidak ikut commit publik. Salinan lengkap perubahan sebelum kurasi dipertahankan pada cabang lokal `archive/op3-progress-full-local-20261023`.

**Catatan interpretasi:** frekuensi kotak dan confidence pada log live adalah keluaran model, bukan akurasi. Akurasi memerlukan anotasi ground truth yang sesuai dengan frame uji. Status kondisi idle/berjalan juga harus dibaca sesuai sumber verifikasi yang dijelaskan pada masing-masing laporan.

## 2026-10-19

- [Hasil inferensi kamera OP3](2026-10-19/percobaan-01-kondisi-tidak-terverifikasi/README.md)
- [Hasil inferensi kamera OP3](2026-10-19/percobaan-02-kamera-unknown/README.md)
- [Hasil inferensi kamera OP3](2026-10-19/percobaan-03-servo-idle/README.md)
- [Percobaan 04 — tracking kamera, servo idle](2026-10-19/percobaan-04-live-tracking-servo-idle/README.md)
- [Percobaan 05 — tracking bola dengan target servo kepala 19/20](2026-10-19/percobaan-05-head-ball-tracking/README.md)

## 2026-10-21

- [Percobaan 01 — monitor deteksi dan rekam kamera, servo idle](2026-10-21/percobaan-01-monitor-rekam-servo-idle/README.md)
- [Percobaan 02 — kandidat 60 frame tanpa objek target](2026-10-21/percobaan-02-frame-negatif/README.md)
- [Percobaan 03 — 40 frame robot dan bola](2026-10-21/percobaan-03-robot-bola-40-frame/README.md)
- [Percobaan 04 — 40 frame robot dan gawang](2026-10-21/percobaan-04-robot-gawang-40-frame/README.md)
- [Percobaan 05 — 40 frame gawang dan bola](2026-10-21/percobaan-05-gawang-bola-40-frame/README.md)
- [Peninjauan manual 120 frame dari tiga kelompok](2026-10-21/percobaan-06-peninjauan-manual-120-frame/README.md)
- [Percobaan 07 — 40 frame robot dan bola berpindah](2026-10-21/percobaan-07-robot-bola-berpindah-40-frame/README.md)
- [Percobaan 08 — 40 frame bola bergerak](2026-10-21/percobaan-08-bola-bergerak-40-frame/README.md)
- [Percobaan 09 — tiga objek pada empat posisi](2026-10-21/percobaan-09-tiga-objek-empat-posisi/README.md)
- [Percobaan 10 — 10 frame posisi tambahan](2026-10-21/percobaan-10-posisi-tambahan-10-frame/README.md)
- [Peninjauan manual 120 + 10 frame](2026-10-21/percobaan-11-peninjauan-manual-130-frame/README.md)
- [Peninjauan manual 60 frame tanpa target](2026-10-21/percobaan-12-peninjauan-60-frame-negatif/README.md)
- [Percobaan 13 — evaluasi deteksi offline multi-sesi OP3](2026-10-21/percobaan-13-evaluasi-deteksi-multi-sesi/README.md)
- [Percobaan 14 — audit kesalahan 80 frame prioritas](2026-10-21/percobaan-14-audit-kesalahan-80-frame/README.md)
- [Percobaan 15 — tracking dan deteksi live kamera OP3](2026-10-21/percobaan-15-tracking-live-runtime/README.md)

## 2026-10-22

- [Percobaan 16 — Benchmark KD Murni, kondisi servo idle](2026-10-22/percobaan-16-benchmark-kd-murni-servo-idle/README_ID.md) · [English](2026-10-22/percobaan-16-benchmark-kd-murni-servo-idle/README_EN.md)
- [Percobaan 17 — Benchmark KD murni saat robot berjalan](2026-10-22/percobaan-17-benchmark-kd-murni-walking/README_ID.md) · [English](2026-10-22/percobaan-17-benchmark-kd-murni-walking/README_EN.md)
- [Percobaan 18 — Perbandingan KD murni setara dengan preview aktif](2026-10-22/percobaan-18-benchmark-kd-murni-setara-preview/README_ID.md) · [English](2026-10-22/percobaan-18-benchmark-kd-murni-setara-preview/README_EN.md)
- [Percobaan 19 — Benchmark KD Hybrid idle dan terbeban](2026-10-22/percobaan-19-benchmark-kd-hybrid-setara-preview/README_ID.md) · [English](2026-10-22/percobaan-19-benchmark-kd-hybrid-setara-preview/README_EN.md)
- [Percobaan 20 — Diagnostik live KD Hybrid dan keluaran gawang](2026-10-22/percobaan-20-diagnostik-kd-hybrid-gawang-opencr/README_ID.md) · [English](2026-10-22/percobaan-20-diagnostik-kd-hybrid-gawang-opencr/README_EN.md)
- [Percobaan 21 — KD Hybrid pada kondisi servo-idle setelah OpenCR pulih](2026-10-22/percobaan-21-kd-hybrid-servo-idle-opencr-pulih/README_ID.md) · [English](2026-10-22/percobaan-21-kd-hybrid-servo-idle-opencr-pulih/README_EN.md)
- [Percobaan 22 — pemeriksaan fungsi live supervised dan tracking](2026-10-22/percobaan-22-supervised-live-function/README_ID.md) · [English](2026-10-22/percobaan-22-supervised-live-function/README_EN.md)
- [Percobaan 23 — supervised servo idle dengan preview SSH-X](2026-10-22/percobaan-23-supervised-servo-idle/README_ID.md) · [English](2026-10-22/percobaan-23-supervised-servo-idle/README_EN.md)
- [Percobaan 24 — uji ulang supervised: idle, tracking statis, dan status uji berjalan](2026-10-22/percobaan-24-supervised-retest/README_ID.md) · [hasil tracking](2026-10-22/percobaan-24-supervised-retest/03-tracking/README_ID.md)
- [Percobaan 25 — uji ulang Supervised idle, berjalan, dan tracking dengan posisi kepala dipertahankan](2026-10-22/percobaan-25-supervised-retest-head-locked/README_ID.md)

## 2026-10-23

- [Percobaan 26 — uji ulang KD murni: Idle, berjalan, dan tracking selesai](2026-10-23/percobaan-26-uji-ulang-kd-murni/README_ID.md)

- [Percobaan 27 — uji ulang KD Hybrid: idle, berjalan, dan tracking](2026-10-23/percobaan-27-uji-ulang-kd-hybrid/README_ID.md) · [English](2026-10-23/percobaan-27-uji-ulang-kd-hybrid/README_EN.md)
- [Percobaan 28 — evaluasi offline berpasangan KD Hybrid vs Supervised pada 260 frame OP3](2026-10-23/percobaan-28-evaluasi-offline-hybrid-supervised-260/README_ID.md) · [English](2026-10-23/percobaan-28-evaluasi-offline-hybrid-supervised-260/README_EN.md)

## 2026-11-02

- [Percobaan 30 — awal uji live setara empat model OP3, kini 12/24 slot lintas hari](2026-11-02/percobaan-30-uji-live-setara-empat-model/README_ID.md) · [English](2026-11-02/percobaan-30-uji-live-setara-empat-model/README_EN.md) · [Log awal](2026-11-02/percobaan-30-uji-live-setara-empat-model/log_progres.md) · [Tabel 24 slot terbaru](2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv)

## 2026-11-03

- [Percobaan 31 — KD Hybrid berjalan tiga ulangan](2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/README_ID.md) · [English](2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/README_EN.md) · [Grafik tiga ulangan HD](2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/grafik_hybrid1337_walk_ulangan_1_2_3_hd.png) · [Tabel tiga run](2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/05-ringkasan/tabel_3_run.csv)

## Materi skripsi dan audit

- [Audit kelengkapan dokumentasi skripsi](AUDIT_KELENGKAPAN_SKRIPSI_2026-10-22.md)
- [Indeks seluruh tabel analisis performa](../analisis_performa/INDEKS.md)
- [Draf Proposal Bab I–III](../DRAF_PROPOSAL_BAB_I-III.md)
- [Draf Bab IV–V hasil dan pembahasan](../DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md)
- [Draf abstrak](../DRAF_ABSTRAK_SKRIPSI.md)
