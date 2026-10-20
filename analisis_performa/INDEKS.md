# Indeks tabel analisis performa

Pembaruan tabel lab/server T01–T14: 2026-10-20. [Indeks lab/server](lab_server/README.md) memuat sumber, status, dan data yang masih diperlukan. Tabel robot T15–T27 masih mengikuti kurasi 2026-10-19 dan belum mengintegrasikan log OP3 terbaru. Semua hasil TEST di bawah adalah evaluasi gambar dataset Advance Vision dan tidak mengukur akurasi kamera OP3.

| Tabel | Status | Berkas |
| --- | --- | --- |
| T01 | Lengkap dari artefak historis; bukan validasi kamera OP3. | [CSV](tabel/T01_spesifikasi_model.csv) · [Markdown](tabel/T01_spesifikasi_model.md) |
| T02 | Lengkap; durasi enam run ditelusuri ke results.csv atau manifest resume. | [CSV](tabel/T02_resep_pelatihan.csv) · [Markdown](tabel/T02_resep_pelatihan.md) |
| T03 | Lengkap dari results.csv run yang sudah ada. | [CSV](tabel/T03_konvergensi.csv) · [Markdown](tabel/T03_konvergensi.md) |
| T04 | Belum diukur; belum ada pilot kandidat KD baru di VAL. | [CSV](tabel/T04_ablasi_kd_val.csv) · [Markdown](tabel/T04_ablasi_kd_val.md) |
| T05 | Sebagian; CI bootstrap tersedia untuk setiap checkpoint pada [rincian per model](lab_server/interval_bootstrap_per_model.md), belum untuk rerata lintas seed. | [CSV](tabel/T05_akurasi_test_keseluruhan.csv) · [Markdown](tabel/T05_akurasi_test_keseluruhan.md) |
| T06 | Lengkap dari hasil TEST terkunci yang sudah ada. | [CSV](tabel/T06_akurasi_per_kelas.csv) · [Markdown](tabel/T06_akurasi_per_kelas.md) |
| T07 | Lengkap untuk lima metrik keseluruhan pada tiga pasangan seed dan retensi mAP50–95 terhadap teacher. | [CSV](tabel/T07_selisih_berpasangan.csv) · [Markdown](tabel/T07_selisih_berpasangan.md) |
| T08 | Belum diukur. | [CSV](tabel/T08_akurasi_ukuran_objek.csv) · [Markdown](tabel/T08_akurasi_ukuran_objek.md) |
| T09 | Belum diukur. | [CSV](tabel/T09_analisis_kesalahan.csv) · [Markdown](tabel/T09_analisis_kesalahan.md) |
| T10 | Belum diukur. | [CSV](tabel/T10_matriks_kebingungan.csv) · [Markdown](tabel/T10_matriks_kebingungan.md) |
| T11 | Belum diukur. | [CSV](tabel/T11_sapuan_confidence.csv) · [Markdown](tabel/T11_sapuan_confidence.md) |
| T12 | Belum diukur. | [CSV](tabel/T12_sapuan_iou_nms.csv) · [Markdown](tabel/T12_sapuan_iou_nms.md) |
| T13 | Sebagian; data dasar ukuran 640 tersedia, sapuan ukuran input belum diukur. | [CSV](tabel/T13_sapuan_imgsz.csv) · [Markdown](tabel/T13_sapuan_imgsz.md) |
| T14 | Belum diukur. | [CSV](tabel/T14_kalibrasi_confidence.csv) · [Markdown](tabel/T14_kalibrasi_confidence.md) |
| T15 | Sebagian; spesifikasi perangkat berasal dari catatan historis dan input operator. | [CSV](tabel/T15_lingkungan_uji_op3.csv) · [Markdown](tabel/T15_lingkungan_uji_op3.md) |
| T16 | Belum diukur pada CPU OP3 dengan frame tetap. | [CSV](tabel/T16_latensi_frame_tetap.csv) · [Markdown](tabel/T16_latensi_frame_tetap.md) |
| T17 | Belum diukur. | [CSV](tabel/T17_sapuan_thread.csv) · [Markdown](tabel/T17_sapuan_thread.md) |
| T18 | Sebagian; tabel ini baru memuat tiga sesi historis dan belum mengintegrasikan run tracking yang masuk kemudian. | [CSV](tabel/T18_sesi_live_historis.csv) · [Markdown](tabel/T18_sesi_live_historis.md) |
| T19 | Belum diukur; sesi walking belum tersedia. | [CSV](tabel/T19_servo_idle_vs_walking.csv) · [Markdown](tabel/T19_servo_idle_vs_walking.md) |
| T20 | Belum diukur. | [CSV](tabel/T20_sumber_daya_startup.csv) · [Markdown](tabel/T20_sumber_daya_startup.md) |
| T21 | Belum diukur. | [CSV](tabel/T21_stabilitas_termal.csv) · [Markdown](tabel/T21_stabilitas_termal.md) |
| T22 | Sebagian; log detektor lama bukan probe laju topic kamera. | [CSV](tabel/T22_aliran_kamera.csv) · [Markdown](tabel/T22_aliran_kamera.md) |
| T23 | Belum diukur sesuai protokol frame tetap. | [CSV](tabel/T23_kepatuhan_tenggat.csv) · [Markdown](tabel/T23_kepatuhan_tenggat.md) |
| T24 | Belum diukur. | [CSV](tabel/T24_pengaruh_preview.csv) · [Markdown](tabel/T24_pengaruh_preview.md) |
| T25 | Sebagian; tabel historis belum memuat log per kelas atau ID tracking dari sesi yang masuk kemudian. | [CSV](tabel/T25_observasi_deteksi_live.csv) · [Markdown](tabel/T25_observasi_deteksi_live.md) |
| T26 | Belum diukur; menunggu hasil runtime OP3 dengan protokol terkunci. | [CSV](tabel/T26_tradeoff_utama.csv) · [Markdown](tabel/T26_tradeoff_utama.md) |
| T27 | Belum diukur; belum ada set frame kamera OP3 berlabel. | [CSV](tabel/T27_akurasi_frame_kamera_op3.csv) · [Markdown](tabel/T27_akurasi_frame_kamera_op3.md) |
