# Indeks dokumentasi percobaan OP3

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

## Materi skripsi dan audit

- [Audit kelengkapan dokumentasi skripsi](AUDIT_KELENGKAPAN_SKRIPSI_2026-10-22.md)
- [Indeks seluruh tabel analisis performa](../analisis_performa/INDEKS.md)
- [Draf Proposal Bab I–III](../DRAF_PROPOSAL_BAB_I-III.md)
- [Draf Bab IV–V hasil dan pembahasan](../DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md)
- [Draf abstrak](../DRAF_ABSTRAK_SKRIPSI.md)
