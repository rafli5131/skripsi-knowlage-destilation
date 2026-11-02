# Memory — uji live setara OP3, 2 November 2026

## Keputusan dan status

- Tujuan sesi: empat model (teacher YOLO11n, KD Hybrid full seed 1337, supervised seed 1337, KD murni seed 42) × kondisi idle/berjalan × tiga ulangan, dengan preview SSH-X dan jendela ukur 60 detik sesudah warm-up 30 frame. [Prompt kerja](../prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md).
- Saat catatan ini dibuat, **9/24 slot telah diukur**: teacher idle 3, teacher berjalan 3, KD Hybrid idle 3. Semua sembilan slot berstatus `lulus_cek_otomatis` pada [tabel 24 run](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv). Status itu adalah cek CSV/telemetri, belum audit protokol dan kondisi fisik akhir.
- **15 slot tersisa**: KD Hybrid berjalan 3, supervised idle/berjalan 6, KD murni idle/berjalan 6. T36/T37 belum menjadi tabel final; T38 empat model pada 260 frame OP3 berlabel sama juga belum dikerjakan.
- Instruksi pengguna: kode baru ditempatkan dalam package ROS 2 baru; package lama hanya dipakai melalui antarmuka/shared tanpa mengubah kodenya. Selama pengujian kepala ID 19/20 boleh torque-on, tetapi posisi pandang tidak boleh diperintah berubah. Uji berjalan memerlukan pendamping, walk-ready, dan area gerak kosong.

## Bukti yang harus dipakai saat melanjutkan

| Pasangan | Latensi rata-rata antarrun (ms) | FPS antarrun | CPU proses (% satu CPU logis) | RSS (MiB) | Bukti |
|---|---:|---:|---:|---:|---|
| Teacher idle, 3 run | 96,24 ± 3,60 | 9,88 ± 0,31 | 1338,90 ± 9,65 | 370,58 ± 1,29 | [Ringkasan teacher](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/01-teacher/README_ID.md) |
| Teacher berjalan, 3 run aktif | 95,85 ± 1,27 | 9,87 ± 0,17 | 1333,54 ± 4,08 | 372,42 ± 5,11 | [Ringkasan teacher](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/01-teacher/README_ID.md) |
| KD Hybrid idle, 3 run | 64,70 ± 1,92 | 13,60 ± 0,35 | 1305,97 ± 4,91 | 358,87 ± 1,24 | [Ringkasan Hybrid](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/02-kd-hybrid/README_ID.md) |

Angka adalah rerata ± simpangan baku sampel **tiga rerata run**; sumber angka penuh ada di [CSV agregat](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_agregat_saat_ini.csv). Perbandingan antarblok model masih deskriptif karena urutan tidak digilir sesuai prompt dan kondisi adegan berubah. Preview KD Hybrid terlihat menyala setelah idle u3 pada pemeriksaan terakhir sesi; keberlangsungan proses harus dicek lagi saat melanjutkan.

## Asal data dan batas klaim

- Teacher berjalan **slot aktif u1** menunjuk raw `20261102_eq_teacher_walk_u3` lama; **u2/u3** menunjuk raw `20261102_eq_teacher_walk_retest_u2` dan `_u3`. Gunakan [pemetaan](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/active_run_sources.json), [arsip set lama](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/01-teacher/arsip-set-sebelumnya-20261102-1200/), dan [log penyimpangan](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/log_penyimpangan.md). Set dipilih ulang setelah melihat rendahnya cakupan gawang; jangan menyajikan set aktif sebagai sampel tanpa seleksi.
- Output gawang teacher berjalan aktif 1.676/1.778 frame (94,3%) dan KD Hybrid idle 2.421/2.447 (98,9%). Ini **cakupan keluaran**, bukan precision, recall, F1, atau mAP karena run live tidak memiliki kotak acuan per frame.
- Metrik akurasi berlabel tersedia pada TEST resmi: [T30](../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md) untuk Hybrid/supervised dan [T05](../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) untuk teacher. [T34](../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.md) hanya eksploratif untuk Hybrid dan supervised pada 260 frame OP3; teacher dan KD murni belum dievaluasi di set yang sama. Jangan menggabungkan definisi F1 TEST dengan F1 makro T34 tanpa penjelasan.
- [Dokumentasi sesi ID](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/README_ID.md) dan [EN](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/README_EN.md) menautkan tabel, grafik HD, bukti gambar, serta [peta lima rumusan masalah](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/PETA_RUMUSAN_MASALAH.md). Log mentah berada di `runs/op3_pytorch/` pada checkout robot.

## Langkah saat sesi robot berikutnya

1. Periksa status kamera, preview, manager, torque, posisi encoder kepala, dan keselamatan operator sebelum memulai run. Jangan menganggap proses yang aktif pada sesi ini tetap aktif.
2. Ukur KD Hybrid berjalan tiga kali, kemudian enam run supervised dan enam run KD murni sesuai slot tersisa; simpan bukti per run dan penyimpangan kondisi apa adanya. [Log progres](../dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/log_progres.md) harus diperbarui.
3. Setelah 24 slot lengkap dan audit protokol selesai, bangun T36/T37; lalu jalankan T38 retrospektif pada frame/label OP3 identik bila diperlukan untuk klaim akurasi domain OP3. Jangan isi tabel final dari run parsial.
