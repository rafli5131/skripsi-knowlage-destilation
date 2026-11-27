# Naskah skripsi tujuh bab

Folder ini berisi salinan Markdown naskah skripsi **Skripsi_KD_OP3_v33** (27 November 2026, 116 halaman). Berkas yang diserahkan tetap DOCX dan PDF di `E:\Kuliah\Thesis\Laporan\Skripsi\`. Salinan ini dipakai untuk membaca, mencari teks, dan mencocokkan isi naskah dengan bukti di repositori. Gambar tidak ikut disalin, tetapi setiap keterangan gambar tetap dicantumkan beserta nomornya.

**Judul:** Implementasi *Knowledge Distillation* untuk Deteksi Objek pada Robot Humanoid ROBOTIS OP3
**Struktur:** tujuh bab implementatif-pengembangan (D17), mengikuti Panduan Skripsi FILKOM v3.0.

| Berkas | Isi |
|---|---|
| [Halaman awal](HALAMAN_AWAL.md) | Abstrak dan *abstract*; pengesahan, pernyataan, dan prakata hanya diringkas tanpa data pribadi |
| [Bab 1 Pendahuluan](BAB_1_PENDAHULUAN.md) | Latar belakang, empat rumusan masalah, tujuan, manfaat, batasan, dan sistematika |
| [Bab 2 Landasan Kepustakaan](BAB_2_LANDASAN_KEPUSTAKAAN.md) | Kajian pustaka KD pada detektor dan deteksi pada robot humanoid, lalu dasar teori OP3, YOLO11, KD, ROS 2, BoT-SORT, metrik akurasi, metrik *runtime*, serta variasi antar-*seed* |
| [Bab 3 Metodologi Penelitian](BAB_3_METODOLOGI.md) | Tipe penelitian, rancangan, teknik pengumpulan dan analisis data, peralatan, dan metode setiap tahap |
| [Bab 4 Rekayasa Kebutuhan](BAB_4_REKAYASA_KEBUTUHAN.md) | Kajian masalah, pemangku kepentingan, KF-01 sampai KF-05, KNF-01, serta kebutuhan perangkat keras dan lunak |
| [Bab 5 Perancangan dan Implementasi](BAB_5_PERANCANGAN_IMPLEMENTASI.md) | Rancangan dan implementasi perangkat keras, model *student*, pelatihan KD, *node* deteksi ROS 2, dan *logging* |
| [Bab 6 Pengujian](BAB_6_PENGUJIAN_DAN_PEMBAHASAN.md) | Pengujian fungsional, lalu satu subbab per rumusan masalah, pengujian tambahan, dan evaluasi keseluruhan |
| [Bab 7 Penutup](BAB_7_PENUTUP.md) | Empat butir kesimpulan yang menjawab rumusan masalah dan lima saran |
| [Daftar Referensi](DAFTAR_REFERENSI.md) | 67 entri, format seragam Harvard-Anglia adaptasi FILKOM |
| [Lampiran](LAMPIRAN.md) | A konfigurasi pelatihan, B rincian himpunan data, C hasil *runtime* 24 *run*, D akurasi TEST setiap *seed*, E daftar istilah dan singkatan |

## Rumusan masalah dan letak jawabannya

| No | Rumusan masalah | Pengujian | Kesimpulan |
|---|---|---|---|
| 1 | Akurasi berdasarkan mAP *student* KD hibrida dibandingkan *student* *supervised* berarsitektur sama dan *teacher* YOLO11n | Subbab 6.2 | Bab 7 butir 1 |
| 2 | *Precision*, *recall*, dan *F1-score* ketiga model | Subbab 6.3 | Bab 7 butir 2 |
| 3 | Rata-rata latensi dan FPS ketiga model pada komputer *onboard* OP3 saat robot diam dan berjalan | Subbab 6.4 | Bab 7 butir 3 |
| 4 | Penggunaan CPU dan RAM ketiga model pada komputer *onboard* OP3 | Subbab 6.5 | Bab 7 butir 4 |

"Ketiga model" adalah KD hibrida penuh, *supervised*, dan *teacher* YOLO11n; KD murni disertakan sebagai pembanding tambahan (Batasan Masalah butir 4). Istilah "skala t" didefinisikan pada Batasan Masalah butir 3 sebagai skala khusus (kedalaman 0,50, lebar 0,125, 810.649 parameter), bukan skala resmi YOLO11.

Rumusan masalah implementasi sistem (rumusan nomor 1 pada draf 12 November) dihapus pada naskah v9. Status implementasi kini dibahas di Subbab 6.1 dan di paragraf pembuka kesimpulan. Rumusan disempurnakan pada naskah v21 (menyebut KD hibrida dan ketiga model). Persetujuan pembimbing atas empat rumusan ini belum tercatat; lihat D25 di [`docs/DECISIONS.md`](../../docs/DECISIONS.md).

## Padanan istilah naskah dan kode repositori

Naskah tidak memakai kode percobaan internal. Tabel berikut menghubungkan istilah naskah dengan sumber datanya di repositori.

| Di naskah | Di repositori |
|---|---|
| Set Kamera 1 (260 *frame* retrospektif) | [T38](../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) |
| Set Kamera 2 (260 *frame*, 12 November) | [T43](../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md) dan uji sensitivitasnya |
| Tabel 6.1 kasus uji KF/KNF | [`bukti_kebutuhan/`](../../bukti_kebutuhan/README.md) |
| Tabel 6.2 penyaringan varian pada VAL | [T04](../../analisis_performa/tabel/T04_ablasi_kd_val.md) dan [T28](../../analisis_performa/tabel/T28_selisih_kd_hybrid_val.md) |
| Tabel 6.3, 6.4, 6.10, 6.11 akurasi TEST dan selisih berpasangan | [T05](../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md) |
| Tabel 6.5 dan 6.12 per kelas | [T06](../../analisis_performa/tabel/T06_akurasi_per_kelas.md) dan [T31](../../analisis_performa/tabel/T31_kd_hybrid_test_per_kelas.md) |
| Tabel 6.6 dan 6.13 jalur evaluasi TEST | [Verifikasi jalur student](../../analisis_performa/lab_server/verifikasi_jalur_test_20261113/RINGKASAN.md) dan [teacher](../../analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher/RINGKASAN.md) (D23, D24) |
| Tabel 6.9 jalur evaluasi kamera OP3 | [T44](../../analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.md) |
| Tabel 6.8 dan 6.16 kepekaan label | [T43 sensitivitas label](../../analisis_performa/tabel/T43_sensitivitas_label_52.md) |
| Gambar 6.12 sapuan *confidence* | [T11](../../analisis_performa/tabel/T11_sapuan_confidence.md) |
| Tabel 6.17, 6.18, 6.20, Lampiran C *runtime* | [T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) dan [T37](../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md) |
| Tabel 6.19 dan 6.21 rincian tahap dan *replay* | [T45](../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md) |
| Tabel 6.22 ablasi ukuran *teacher* | [T42](../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md) |
| Lampiran D akurasi setiap *seed* | T30 dan [`interval_bootstrap_per_model.csv`](../../analisis_performa/lab_server/interval_bootstrap_per_model.csv) |
| Label penulis dan label peninjau kedua | Label Bhre dan label peninjau kedua pada T43 |

## Yang masih diisi penulis

- Tanggal ujian dan tanggal tanda tangan (tiga tempat).
- Tujuh isian `[DIISI PENULIS]` di prakata.
- Penanda `[PERLU DICEK]` di Subbab 5.2.1.2: kesamaan unit OP3 pada foto rangkaian elektronika (Gambar 5.13 sampai 5.15, dari Brilliant, 2024) dengan unit penelitian.

## Cara memperbarui salinan ini

Salinan dibuat dari DOCX dengan pandoc, lalu dipecah per bab dengan [`laporan/alat/konversi_naskah_ke_markdown.py`](../alat/konversi_naskah_ke_markdown.py):

```bash
pandoc Skripsi_KD_OP3_vNN.docx -t gfm --wrap=none -o naskah.md
python3 laporan/alat/konversi_naskah_ke_markdown.py naskah.md laporan/draf-7-bab "Skripsi_KD_OP3_vNN (tanggal)"
```

Skrip menimpa berkas bab di folder ini. Salin dulu versi lama ke `laporan/arsip/` bila masih diperlukan.

## Versi sebelumnya

- Draf ringkas 12 sampai 23 November: [`laporan/arsip/draf-7-bab-2026-11-23/`](../arsip/draf-7-bab-2026-11-23/README.md).
- Draf Bab IV-V dan proposal Bab I-III: [`laporan/draf-bab-iv-v/`](../draf-bab-iv-v/README.md) dan [`laporan/DRAF_PROPOSAL_BAB_I-III.md`](../DRAF_PROPOSAL_BAB_I-III.md).
- Riwayat suntingan naskah v1 sampai v33: [log 25 November](../../dokumentasi/2026-11-25/LOG_PROGRES_SKRIPSI.md).
