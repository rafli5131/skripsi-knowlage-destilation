# Tabel lab/server T01–T14

Pembaruan: 20 Oktober 2026. Folder ini adalah pintu masuk untuk tabel dataset, pelatihan, evaluasi gambar, dan benchmark server. Metode penelitian adalah **Knowledge Distillation (KD) murni dengan objective teacher-only**; student supervised adalah kontrol. Angka TEST berasal dari evaluasi terkunci pada split resmi Roboflow Advance Vision v1. Hasilnya berlaku pada level gambar dan belum menjadi ukuran akurasi kamera ROBOTIS OP3.

## Lokasi berkas

Nomor dan nama berkas T01–T14 tetap berada di [`analisis_performa/tabel/`](../tabel/). Setiap tabel memiliki CSV untuk pengolahan data dan Markdown untuk dibaca. CSV memakai titik desimal; Markdown memakai koma desimal dengan pembulatan tampilan. Nilai sumber yang lebih presisi tetap ada di CSV dan artefak asal.

| Tabel | Isi | Status | Buka |
| --- | --- | --- | --- |
| T01 | Spesifikasi teacher dan enam student | Lengkap | [Markdown](../tabel/T01_spesifikasi_model.md) · [CSV](../tabel/T01_spesifikasi_model.csv) |
| T02 | Resep dan durasi enam run pelatihan | Lengkap | [Markdown](../tabel/T02_resep_pelatihan.md) · [CSV](../tabel/T02_resep_pelatihan.csv) |
| T03 | Konvergensi VAL pada epoch terpilih | Lengkap | [Markdown](../tabel/T03_konvergensi.md) · [CSV](../tabel/T03_konvergensi.csv) |
| T04 | Ablasi objective KD pada VAL | Belum diukur | [Markdown](../tabel/T04_ablasi_kd_val.md) · [CSV](../tabel/T04_ablasi_kd_val.csv) |
| T05 | Metrik TEST keseluruhan | Sebagian | [Markdown](../tabel/T05_akurasi_test_keseluruhan.md) · [CSV](../tabel/T05_akurasi_test_keseluruhan.csv) |
| T06 | Metrik TEST per kelas | Lengkap | [Markdown](../tabel/T06_akurasi_per_kelas.md) · [CSV](../tabel/T06_akurasi_per_kelas.csv) |
| T07 | Selisih KD–supervised berpasangan | Lengkap | [Markdown](../tabel/T07_selisih_berpasangan.md) · [CSV](../tabel/T07_selisih_berpasangan.csv) |
| T08 | Akurasi menurut ukuran objek | Belum diukur | [Markdown](../tabel/T08_akurasi_ukuran_objek.md) · [CSV](../tabel/T08_akurasi_ukuran_objek.csv) |
| T09 | Kategori kesalahan deteksi pada VAL | Belum diukur | [Markdown](../tabel/T09_analisis_kesalahan.md) · [CSV](../tabel/T09_analisis_kesalahan.csv) |
| T10 | Matriks kebingungan | Belum diukur | [Markdown](../tabel/T10_matriks_kebingungan.md) · [CSV](../tabel/T10_matriks_kebingungan.csv) |
| T11 | Sapuan ambang confidence pada VAL | Belum diukur | [Markdown](../tabel/T11_sapuan_confidence.md) · [CSV](../tabel/T11_sapuan_confidence.csv) |
| T12 | Sapuan IoU NMS pada VAL | Belum diukur | [Markdown](../tabel/T12_sapuan_iou_nms.md) · [CSV](../tabel/T12_sapuan_iou_nms.csv) |
| T13 | Sapuan ukuran input; titik dasar 640 tersedia | Sebagian | [Markdown](../tabel/T13_sapuan_imgsz.md) · [CSV](../tabel/T13_sapuan_imgsz.csv) |
| T14 | Kalibrasi confidence | Belum diukur | [Markdown](../tabel/T14_kalibrasi_confidence.md) · [CSV](../tabel/T14_kalibrasi_confidence.csv) |

Pelengkap T05: [interval bootstrap per model](interval_bootstrap_per_model.md) ([CSV](interval_bootstrap_per_model.csv)). Berkas itu memuat lima metrik untuk masing-masing tujuh checkpoint sehingga interval per checkpoint dapat ditelusuri tanpa mencampurnya dengan simpangan baku antar-seed.

## Sumber utama dan cara baca

| Kebutuhan | Artefak sumber | Pemakaian |
| --- | --- | --- |
| Spesifikasi, metrik VAL/TEST, biaya model | [`per_model.csv`](../../artifacts/thesis_analysis_final_corrected/per_model.csv), [`model_registry.yaml`](../../configs/model_registry.yaml) | T01, T05–T07, titik dasar T13 |
| Rerata dan SD sampel | [`summary_mean_sd.csv`](../../artifacts/thesis_analysis_final_corrected/summary_mean_sd.csv) | T05; tiga seed untuk KD dan supervised, satu teacher |
| Perbandingan seed berpasangan | [`paired_seed_deltas.csv`](../../artifacts/thesis_analysis_final_corrected/paired_seed_deltas.csv), [`paired_summary.csv`](../../artifacts/thesis_analysis_final_corrected/paired_summary.csv) | T07; delta = KD dikurangi supervised pada seed yang sama |
| Resep dan riwayat training | Manifest, `args.yaml`, dan `results.csv` pada [run yang terdaftar](../../configs/model_registry.yaml) | T02–T03; durasi dari `results.csv`, kecuali supervised seed 1337 dari jumlah dua segmen resume |
| Evaluasi TEST terkunci | [`manifest.json`](../../runs/final_test/pure_kd_official_split_locked_retry1/manifest.json) dan tujuh berkas `*_metrics.json` pada folder yang sama | T05–T06 dan interval per checkpoint |
| Benchmark server | [`pure_kd_final_inference.json`](../../runs/benchmarks/pure_kd_final_inference.json) | T01 dan titik dasar T13, FP32 batch 1 pada NVIDIA L40 |
| Definisi dan batas eksperimen | [`DEFINISI.md`](../DEFINISI.md), [`PROTOKOL_EKSPERIMEN_SKRIPSI.md`](../../PROTOKOL_EKSPERIMEN_SKRIPSI.md), [`AUDIT_DATASET_SKRIPSI.md`](../../AUDIT_DATASET_SKRIPSI.md) | Split, operating point, ukuran objek, dan batas klaim |

Pada TEST, precision/recall/F1 memakai confidence tetap `>0,25` dan IoU pencocokan 0,50. AP memakai confidence floor 0,001 dan NMS IoU 0,7. Bootstrap 95% meresampling **gambar TEST** untuk satu checkpoint; SD sampel menghitung variasi hasil **antar tiga seed**. Interval bootstrap untuk rerata antar-seed belum tersedia, sehingga T05 berstatus Sebagian.

T03 membaca maksimum metrik VAL per epoch dari `results.csv`. Nilai VAL pada T13 berasal dari evaluasi checkpoint yang dicatat `per_model.csv`. Kedua jalur sumber ini harus disebut saat angka VAL dibandingkan. T13 baru memiliki ukuran 640; latensi dan throughput yang ditampilkan berasal dari server NVIDIA L40, bukan FPS stream OP3.

## Ringkasan yang sudah dapat dikutip

Mean TEST mAP50–95 pure KD adalah **0,6630 ± 0,0108** dari tiga seed; supervised student **0,7225 ± 0,0035** dari tiga seed; teacher **0,7800** dari satu checkpoint. Delta berpasangan KD dikurangi supervised adalah **−0,0595 ± 0,0138**. Sumbernya adalah [T05](../tabel/T05_akurasi_test_keseluruhan.md) dan [T07](../tabel/T07_selisih_berpasangan.md). Angka tersebut mendeskripsikan split resmi pada level gambar; ia tidak mengukur akurasi kamera OP3.

## Data yang masih dibutuhkan

- T04 memerlukan run pilot objective KD yang dinilai pada VAL. Belum ada run pilot kandidat yang dapat dipakai.
- T08–T10 memerlukan prediksi per gambar dan kecocokan dengan label, beserta definisi kategori kesalahan yang tidak saling tumpang tindih. Metrik agregat TEST tidak cukup untuk menyusunnya.
- T11–T12 memerlukan hasil sapuan confidence dan IoU NMS pada VAL dengan protokol tetap.
- T13 memerlukan pengukuran beberapa ukuran input dengan kondisi benchmark yang sebanding; satu titik 640 belum membentuk sapuan.
- T14 memerlukan prediksi per deteksi beserta label benar/salah untuk menghitung bin reliabilitas dan ECE.

Kolom untuk tabel yang belum diukur sudah disiapkan; CSV-nya berisi header tanpa baris observasi. Penanda `[BELUM DIUKUR]` dan alasannya terdapat pada Markdown masing-masing.

## Jejak perubahan tabel

[`manifest.json`](manifest.json) mencatat SHA-256 sumber dan keluaran T01–T14 yang dikurasi pada 20 Oktober 2026. [`analisis_performa/manifest.json`](../manifest.json) berawal dari snapshot generator tanggal 19 Oktober 2026 dan telah diperbarui untuk sumber serta keluaran tabel OP3 T15–T27. Untuk hash tabel lab/server T01–T14, gunakan manifest kurasi di folder ini. Menjalankan ulang [`scripts/build_performance_tables.py`](../../scripts/build_performance_tables.py) akan menulis ulang tabel dan dapat mengganti kurasi ini; periksa perbedaan terhadap manifest kurasi sebelum menerima hasil regenerasi.

Tabel robot T15–T27 berada di [indeks umum](../INDEKS.md) dan memiliki [prompt tersendiri](../../prompt/PROMPT_TABEL_ROBOT_OP3_KD.md). Log OP3 tersimpan telah diintegrasikan ke T15, T18, T20, T22, T23, T25, dan T26 pada pembaruan terpisah.
