# Tabel lab/server T01–T14, T28–T33, dan T39–T41

Pembaruan: 24 Oktober 2026. Folder ini adalah pintu masuk untuk tabel dataset, pelatihan, evaluasi gambar, dan benchmark server. Analisis ini memuat eksperimen utama **KD murni teacher-only**, **KD Hybrid full**, serta ablasi **Hybrid v2 S2** yang dibandingkan pada VAL. Split TEST sudah pernah dipakai dalam eksperimen teacher dan KD murni; hasil Hybrid adalah perbandingan lanjutan pada split yang sama. Semua hasil akurasi ini berlaku pada level gambar dan bukan ukuran akurasi kamera ROBOTIS OP3.

## Lokasi berkas

Nomor dan nama berkas T01–T14 tetap berada di [`analisis_performa/tabel/`](../tabel/). Setiap tabel memiliki CSV untuk pengolahan data dan Markdown untuk dibaca. CSV memakai titik desimal; Markdown memakai koma desimal dengan pembulatan tampilan. Nilai sumber yang lebih presisi tetap ada di CSV dan artefak asal.

| Tabel | Isi | Status | Buka |
| --- | --- | --- | --- |
| T01 | Spesifikasi teacher dan enam student | Lengkap | [Markdown](../tabel/T01_spesifikasi_model.md) · [CSV](../tabel/T01_spesifikasi_model.csv) |
| T02 | Resep dan durasi enam run pelatihan | Lengkap | [Markdown](../tabel/T02_resep_pelatihan.md) · [CSV](../tabel/T02_resep_pelatihan.csv) |
| T03 | Konvergensi VAL pada epoch terpilih | Lengkap | [Markdown](../tabel/T03_konvergensi.md) · [CSV](../tabel/T03_konvergensi.csv) |
| T04 | Ablasi objective KD pada VAL | Lengkap untuk KD pure tiga seed, pilot pure_weighted seed 42, hybrid_feature seed 42, dan hybrid_full tiga seed | [Markdown](../tabel/T04_ablasi_kd_val.md) · [CSV](../tabel/T04_ablasi_kd_val.csv) · [Per kelas](../tabel/T04_ablasi_kd_val_per_kelas.md) |
| T05 | Metrik TEST keseluruhan | Lengkap untuk ringkasan dan bootstrap seed yang tersedia | [Markdown](../tabel/T05_akurasi_test_keseluruhan.md) · [CSV](../tabel/T05_akurasi_test_keseluruhan.csv) |
| T06 | Metrik TEST per kelas | Lengkap | [Markdown](../tabel/T06_akurasi_per_kelas.md) · [CSV](../tabel/T06_akurasi_per_kelas.csv) |
| T07 | Selisih KD–supervised berpasangan | Lengkap | [Markdown](../tabel/T07_selisih_berpasangan.md) · [CSV](../tabel/T07_selisih_berpasangan.csv) |
| T08 | Akurasi menurut ukuran objek | Lengkap untuk tujuh checkpoint pada VAL | [Markdown](../tabel/T08_akurasi_ukuran_objek.md) · [CSV](../tabel/T08_akurasi_ukuran_objek.csv) |
| T09 | Kategori kesalahan deteksi pada VAL | Lengkap | [Markdown](../tabel/T09_analisis_kesalahan.md) · [CSV](../tabel/T09_analisis_kesalahan.csv) |
| T10 | Matriks kebingungan | Lengkap | [Markdown](../tabel/T10_matriks_kebingungan.md) · [CSV](../tabel/T10_matriks_kebingungan.csv) |
| T11 | Sapuan ambang confidence pada VAL | Lengkap | [Markdown](../tabel/T11_sapuan_confidence.md) · [CSV](../tabel/T11_sapuan_confidence.csv) |
| T12 | Sapuan IoU NMS pada VAL | Lengkap untuk tiga model perwakilan | [Markdown](../tabel/T12_sapuan_iou_nms.md) · [CSV](../tabel/T12_sapuan_iou_nms.csv) |
| T13 | Sapuan ukuran input dan titik dasar L40 | Lengkap untuk tiga model perwakilan pada CPU server | [Markdown](../tabel/T13_sapuan_imgsz.md) · [CSV](../tabel/T13_sapuan_imgsz.csv) |
| T14 | Kalibrasi confidence | Lengkap | [Markdown](../tabel/T14_kalibrasi_confidence.md) · [CSV](../tabel/T14_kalibrasi_confidence.csv) |

### Tabel eksperimen KD Hybrid

| Tabel | Isi | Status | Buka |
| --- | --- | --- | --- |
| T28 | Selisih Hybrid–supervised pada VAL | Lengkap, tiga seed berpasangan | [Markdown](../tabel/T28_selisih_kd_hybrid_val.md) · [CSV](../tabel/T28_selisih_kd_hybrid_val.csv) |
| T29 | Hasil VAL per kelas | Lengkap, tiga seed berpasangan | [Markdown](../tabel/T29_kd_hybrid_val_per_kelas.md) · [CSV](../tabel/T29_kd_hybrid_val_per_kelas.csv) |
| T30 | Selisih Hybrid–supervised pada TEST | Lengkap, tiga seed, interval bootstrap per checkpoint di CSV | [Markdown](../tabel/T30_kd_hybrid_test_berpasangan.md) · [CSV](../tabel/T30_kd_hybrid_test_berpasangan.csv) |
| T31 | Hasil TEST per kelas | Lengkap, tiga seed berpasangan | [Markdown](../tabel/T31_kd_hybrid_test_per_kelas.md) · [CSV](../tabel/T31_kd_hybrid_test_per_kelas.csv) |
| T32 | Benchmark enam checkpoint pada L40 | Lengkap untuk satu frame VAL tetap, batch 1 | [Markdown](../tabel/T32_kd_hybrid_benchmark_server.md) · [CSV](../tabel/T32_kd_hybrid_benchmark_server.csv) |
| T33 | Resep, durasi, dan konvergensi training Hybrid full | Lengkap untuk tiga seed | [Markdown](../tabel/T33_pelatihan_kd_hybrid_full.md) · [CSV](../tabel/T33_pelatihan_kd_hybrid_full.csv) |

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
| Evaluasi TEST KD Hybrid | [`manifest.json`](../../runs/final_test/hybrid_full_official_split_20261022/manifest.json) dan enam `*_metrics.json` pada folder yang sama | T30–T31; checkpoint dan protokol dicatat sebelum TEST Hybrid |
| Benchmark KD Hybrid | [`hybrid_full_paired_20261022.json`](../../runs/benchmarks/hybrid_full_paired_20261022.json) | T32; enam checkpoint pada frame VAL tetap dan NVIDIA L40 |
| Run training KD Hybrid full | Manifest dan `results.csv` pada tiga direktori `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed*/` | T33; durasi dan deret mAP VAL per epoch |
| Diagnosis VAL tujuh checkpoint | [`DIAGNOSIS_VAL_2026-10-20.md`](DIAGNOSIS_VAL_2026-10-20.md), [`summary.json`](../../runs/val_diagnostics/official_split_20261020/summary.json), tujuh prediksi JSON per gambar | T09–T11 dan T14; FP32 CPU pada VAL, tanpa training atau membuka TEST |
| Pelengkapan tabel dari prediksi dan run lama | [`complete_existing_lab_tables.py`](../../scripts/complete_existing_lab_tables.py), prediksi VAL dan manifest run KD | T04 kondisi dasar sebelum pilot, T05 bootstrap antar-seed, T08 ukuran objek, dan AP per kelas titik dasar T13 |
| Pilot `pure_weighted` dan evaluasi ulang VAL | [`PILOT_PURE_WEIGHTED_2026-10-20.md`](../../docs/PILOT_PURE_WEIGHTED_2026-10-20.md), [`evaluate_val_ablation.py`](../../scripts/evaluate_val_ablation.py), [`build_kd_ablation_table.py`](../../scripts/build_kd_ablation_table.py) | T04 final: tiga baseline dan satu kandidat seed 42, termasuk rincian per kelas |
| Sapuan VAL dan benchmark CPU server | [`sweep_val_lab.py`](../../scripts/sweep_val_lab.py), [`runs/val_sweeps/official_split_20261020/`](../../runs/val_sweeps/official_split_20261020/) | T12 IoU NMS dan T13 ukuran 320/416/512/640 pada tiga model perwakilan |
| Definisi dan batas eksperimen | [`DEFINISI.md`](../DEFINISI.md), [`PROTOKOL_EKSPERIMEN_SKRIPSI.md`](../../PROTOKOL_EKSPERIMEN_SKRIPSI.md), [`AUDIT_DATASET_SKRIPSI.md`](../../AUDIT_DATASET_SKRIPSI.md) | Split, operating point, ukuran objek, dan batas klaim |

Pada TEST, precision/recall/F1 memakai confidence tetap `>0,25` dan IoU pencocokan 0,50. AP memakai confidence floor 0,001 dan NMS IoU 0,7. Interval bootstrap per checkpoint meresampling **gambar TEST**. T05 kini juga memuat interval bootstrap atas **rerata tiga seed** dengan resampling seed 10.000 kali; interval kedua ini eksploratif karena hanya ada tiga seed dan tidak meresampling gambar. SD sampel menghitung variasi hasil antar-seed.

T03 membaca maksimum metrik VAL per epoch dari `results.csv`. T13 memuat titik dasar 640 dari `per_model.csv` dan sapuan VAL yang dievaluasi ulang; kedua jalur sumber ini dapat berbeda sedikit. Titik dasar benchmark memakai NVIDIA L40, sedangkan sapuan baru memakai CPU server AMD EPYC 7413. Bandingkan ukuran input hanya dalam satu perangkat; angka tersebut bukan FPS stream OP3.
T12/T13 memakai grid sementara D5 untuk diagnosis VAL; keputusan konfigurasi runtime dan grid skripsi akhir belum dikunci. GFLOPs T13 dihitung sebelum fusi Conv–BN agar metode sama dengan titik dasar historis.

## Ringkasan yang sudah dapat dikutip

Mean TEST mAP50–95 pure KD adalah **0,6630 ± 0,0108** dari tiga seed; supervised student **0,7225 ± 0,0035** dari tiga seed; teacher **0,7800** dari satu checkpoint. Delta berpasangan KD dikurangi supervised adalah **−0,0595 ± 0,0138**. Sumbernya adalah [T05](../tabel/T05_akurasi_test_keseluruhan.md) dan [T07](../tabel/T07_selisih_berpasangan.md). Angka tersebut mendeskripsikan split resmi pada level gambar; ia tidak mengukur akurasi kamera OP3.

[Diagnosis VAL 20 Oktober](DIAGNOSIS_VAL_2026-10-20.md) menjelaskan T09–T11/T14, termasuk FP duplikasi yang lebih sering pada KD dan trade-off threshold gawang sebelum keputusan objective baru.

Pilot `pure_weighted` selesai 100 epoch pada seed 42. Pada VAL, mAP50–95 turun dari **0,6826** (`pure_v4` seed 42) menjadi **0,5907**; F1 pada confidence 0,25 turun dari **0,8676** menjadi **0,0903** karena precision sangat rendah. Recall `gawang` meningkat, tetapi AP50–95 `gawang` turun. Sesuai kriteria pilot, `pure_v4` tetap model utama. Rincian ada pada [T04](../tabel/T04_ablasi_kd_val.md) dan [catatan pilot](../../docs/PILOT_PURE_WEIGHTED_2026-10-20.md).

## KD Hybrid full: hasil VAL tiga seed

KD Hybrid full dan kontrol supervised dievaluasi ulang pada VAL dengan prosedur yang sama. Rerata mAP50–95 Hybrid full **0,7505 ± 0,0018**, supervised **0,7208 ± 0,0041**, dan delta berpasangan **+0,0297 ± 0,0047** pada tiga seed. Selisih mAP50–95 positif pada setiap pasangan. F1 makro pada confidence 0,25 hampir sama dan sedikit lebih rendah untuk Hybrid full; precision turun sementara recall naik. Lihat [laporan evaluasi](HASIL_KD_HYBRID_MULTI_SEED_VAL_2026-10-22.md), [T28](../tabel/T28_selisih_kd_hybrid_val.md), dan [T29](../tabel/T29_kd_hybrid_val_per_kelas.md).

Hasil VAL mendasari pilihan Hybrid full sebagai kandidat evaluasi lanjutan. Checkpoint OP3 belum diganti.

## KD Hybrid full: hasil TEST dan benchmark server

Pada TEST resmi 592 gambar, rerata mAP50–95 Hybrid full **0,7469 ± 0,0022**, supervised **0,7225 ± 0,0035**, dan delta berpasangan **+0,0244 ± 0,0040** pada tiga seed. F1 makro pada confidence 0,25 adalah **0,9071 ± 0,0017** vs **0,9121 ± 0,0026** (delta **−0,0051 ± 0,0011**). Kelas gawang paling perlu ditinjau pada OP3: F1@0,25 per kelas turun sekitar **0,0193** walau AP50–95 naik. Hasil supervised yang diulang identik dengan evaluasi historis. Detail per kelas, interval bootstrap per checkpoint, benchmark L40, dan pelatihan Hybrid ada di [laporan TEST Hybrid](HASIL_KD_HYBRID_TEST_2026-10-22.md), T30–T33. Angka benchmark bukan FPS kamera OP3.

Checkpoint Hybrid [`best.pt` seed 1337](../../runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt) dan [`best.pt` seed 2025](../../runs/kd_hybrid/yolo11_tiny_hybrid_full_seed2025/weights/best.pt) sudah tersedia di repo GitHub publik. Hash keduanya tercatat di [registry model](../../configs/model_registry.yaml) dan manifest. `last.pt` serta cache training tetap lokal.

## Data yang masih dibutuhkan

Diagnosis pada [T39](../tabel/T39_diagnosis_objektif_kd.md) dan [laporan 23 Oktober](HASIL_DIAGNOSIS_KD_JALUR_TENGAH_2026-10-23.md) memakai VAL saja untuk menilai ambang, TP/FP, bentuk DFL, dan komponen loss yang tersedia. Penyaringan `hybrid_v2` S1–S8 selesai pada [T40](../tabel/T40_penyaringan_hybrid_v2_val_s1_s8.md), dan konfirmasi S2 tiga seed selesai pada [T41](../tabel/T41_konfirmasi_hybrid_v2_val.md). S2 tidak lolos aturan penggantian; Hybrid full tetap model KD utama. Feature loss historis tidak dapat dihitung dari checkpoint student lama yang tidak menyimpan proyektor terlatih. T42–T43 belum ada.

- T04/T28–T29 memuat VAL; T30–T31 memuat TEST lanjutan; T32 memuat benchmark L40; T33 memuat pelatihan Hybrid tiga seed. Split TEST sudah pernah dipakai sebelumnya, sehingga klaim dibatasi pada evaluasi gambar dataset resmi.
- T12/T13 menyapu satu checkpoint per varian agar biaya diagnosis terukur. Sapuan seluruh seed memerlukan inferensi dan benchmark tambahan; hasil perwakilan tidak menunjukkan variasi antar-seed pada setiap titik grid.
- T15–T27 adalah pengukuran OP3 terpisah. Akurasi kamera OP3 tidak dapat dihitung dari tabel lab/server ini tanpa frame kamera berlabel.

## Menghasilkan ulang tabel baru

Jalankan dengan lingkungan Python yang mempunyai versi Ultralytics dan PyTorch eksperimen. `complete_existing_lab_tables.py` membaca prediksi VAL terkunci, ringkasan TEST lama, dan manifest run; **menjalankan ulang skrip ini akan menimpa T04 pilot**, sehingga setelahnya jalankan `build_kd_ablation_table.py`. `sweep_val_lab.py` memverifikasi hash dataset/checkpoint, membuat JSON hasil per kombinasi, lalu menggabungkannya ke T12/T13. Run yang sudah mempunyai JSON dilewati agar sapuan bisa dilanjutkan.

T30–T33 dan laporan TEST Hybrid dapat dibangun ulang dari manifest evaluasi, benchmark, dan training yang sudah ada dengan `python3 scripts/build_kd_hybrid_test_tables.py`. Skrip memeriksa checksum checkpoint, protokol, evaluator, dan kecocokan metrik supervised dengan hasil historis sebelum menulis tabel.

```bash
python scripts/complete_existing_lab_tables.py
python scripts/sweep_val_lab.py --phase nms
python scripts/sweep_val_lab.py --phase imgsz
python scripts/sweep_val_lab.py --phase rebenchmark
python scripts/build_kd_ablation_table.py
```

Jalankan `rebenchmark` setelah inferensi lain selesai agar angka latensi frame tetap tidak dipengaruhi beban sapuan. Perintah itu mengulang benchmark CPU, memperbarui JSON sumber, dan menulis T12/T13 serta hash keluarannya. `build_kd_ablation_table.py` memakai empat JSON VAL yang sudah ada untuk membuat T04; pelatihan pilot yang menghasilkan checkpoint baru telah selesai secara terpisah.

## Jejak perubahan tabel

[`manifest.json`](manifest.json) mencatat SHA-256 sumber dan keluaran T01–T14 yang dikurasi pada 20 Oktober 2026, termasuk prediksi VAL dan sapuan baru. [`analisis_performa/manifest.json`](../manifest.json) berawal dari snapshot generator tanggal 19 Oktober 2026 dan telah diperbarui untuk sumber serta keluaran tabel OP3 T15–T27. Untuk hash tabel lab/server T01–T14, gunakan manifest kurasi di folder ini. Menjalankan ulang [`scripts/build_performance_tables.py`](../../scripts/build_performance_tables.py) akan menulis ulang tabel dan dapat mengganti kurasi ini; periksa perbedaan terhadap manifest kurasi sebelum menerima hasil regenerasi.

Tabel robot T15–T27 berada di [indeks umum](../INDEKS.md) dan memiliki [prompt tersendiri](../../prompt/PROMPT_TABEL_ROBOT_OP3_KD.md). Log OP3 tersimpan telah diintegrasikan ke T15, T18, T20, T22, T23, T25, dan T26 pada pembaruan terpisah.
