# Visualisasi tambahan empat model — 9 November 2026

Kumpulan ini menjelaskan hasil pengujian Teacher YOLO11n, KD Hybrid, Supervised, dan KD Murni. Grafik tersedia dalam bahasa Indonesia (`id`) dan Inggris (`en`), dengan ukuran minimal **2.400 × 1.500 piksel**. Angka bersumber dari tabel dan data run yang sudah ada; visualisasi ini tidak menjalankan robot atau pengujian baru.

## Perbandingan seluruh model

| Grafik | Bahasa Indonesia | English | Kegunaan |
|---|---|---|---|
| Akurasi TEST | [Lihat](grafik-final/01_test_empat_model_id.png) | [View](grafik-final/01_test_empat_model_en.png) | Membandingkan mAP, precision, recall, dan F1 empat model. |
| Perbedaan kecil Hybrid vs Supervised | [Lihat](grafik-final/02_selisih_test_hybrid_supervised_id.png) | [View](grafik-final/02_selisih_test_hybrid_supervised_en.png) | Memperbesar **selisih** mAP50–95 dan F1 untuk setiap seed. |
| Akurasi frame OP3 | [Lihat](grafik-final/03_akurasi_kamera_op3_id.png) | [View](grafik-final/03_akurasi_kamera_op3_en.png) | Perbandingan pada 260 frame OP3 yang sama. |
| Deteksi per objek dan alarm palsu | [Lihat](grafik-final/04_kelas_dan_alarm_palsu_id.png) | [View](grafik-final/04_kelas_dan_alarm_palsu_en.png) | Recall bola, gawang, robot dan jumlah frame negatif yang menghasilkan deteksi salah. |
| Runtime pada OP3 | [Lihat](grafik-final/05_runtime_empat_model_idle_berjalan_id.png) | [View](grafik-final/05_runtime_empat_model_idle_berjalan_en.png) | Latensi, FPS, CPU dan RAM untuk kondisi diam dan berjalan; titik menunjukkan tiga ulangan. |
| Ablasi teacher T42 | [Lihat](grafik-final/06_ablasi_teacher_T42_id.png) | [View](grafik-final/06_ablasi_teacher_T42_en.png) | Membaca selisih kecil antarstudent untuk tiga seed di VAL. |
| Waktu training student | [Lihat](grafik-final/07_waktu_training_student_id.png) | [View](grafik-final/07_waktu_training_student_en.png) | Membandingkan durasi sembilan run training. |

## Rincian tiap model

Ringkasan per model memperlihatkan precision/recall per kelas pada T38 dan nilai latensi/FPS dari setiap ulangan. Grafik garis waktu menunjukkan latensi dan jumlah frame per detik selama tiga run, dipisahkan menurut kondisi diam dan berjalan.

| Model | Ringkasan ID / EN | Garis waktu ID / EN |
|---|---|---|
| Teacher YOLO11n | [ID](grafik-final/08_ringkasan_teacher_id.png) · [EN](grafik-final/08_ringkasan_teacher_en.png) | [ID](grafik-final/09_garis_waktu_teacher_id.png) · [EN](grafik-final/09_garis_waktu_teacher_en.png) |
| KD Hybrid | [ID](grafik-final/08_ringkasan_hybrid1337_id.png) · [EN](grafik-final/08_ringkasan_hybrid1337_en.png) | [ID](grafik-final/09_garis_waktu_hybrid1337_id.png) · [EN](grafik-final/09_garis_waktu_hybrid1337_en.png) |
| Supervised | [ID](grafik-final/08_ringkasan_sup1337_id.png) · [EN](grafik-final/08_ringkasan_sup1337_en.png) | [ID](grafik-final/09_garis_waktu_sup1337_id.png) · [EN](grafik-final/09_garis_waktu_sup1337_en.png) |
| KD Murni | [ID](grafik-final/08_ringkasan_kd42_id.png) · [EN](grafik-final/08_ringkasan_kd42_en.png) | [ID](grafik-final/09_garis_waktu_kd42_id.png) · [EN](grafik-final/09_garis_waktu_kd42_en.png) |

### Cara membaca dengan mudah

- **mAP:** ukuran ketepatan deteksi pada berbagai ambang; lebih tinggi lebih baik. `mAP50–95` memakai kriteria lokasi kotak yang lebih beragam daripada `mAP50`.
- **Precision:** dari deteksi yang dibuat, berapa bagian yang benar. **Recall:** dari target acuan, berapa bagian yang berhasil ditemukan. **F1:** ringkasan precision dan recall; cara agregasinya berbeda antara TEST dan T38.
- **Latensi:** waktu pemrosesan dalam milidetik; lebih kecil lebih cepat. **FPS:** jumlah frame per detik; lebih tinggi berarti lebih banyak frame yang diproses/diterima per detik.
- Pada grafik runtime gabungan, warna pekat adalah kondisi diam, warna bergaris kondisi berjalan; tiga titik menunjukkan hasil masing-masing ulangan. Pada grafik garis, warna menunjukkan ulangan 1, 2, atau 3 yang berlangsung pada waktu berbeda.
- Pada grafik garis waktu, setiap titik merangkum interval **2 detik**: latensi adalah rata-rata per frame dan FPS adalah jumlah frame yang diterima dibagi dua detik. Ini merupakan visualisasi temporal, bukan angka FPS keseluruhan run pada T36/T37.
- Grafik yang memakai **skala diperbesar/terpotong** memberi keterangan pada gambar. Angka dan satuan tetap ditampilkan agar perbedaan yang kecil tidak disalahartikan sebagai perbedaan besar atau signifikan secara statistik.

## Contoh hasil deteksi

Screenshot berikut adalah salinan asli 640 × 480 piksel dari frame **setelah jendela analisis** run berjalan. Gambar tunggal memperlihatkan keluaran detektor, bukan bukti gerakan gait atau akurasi keseluruhan.

- [Teacher — berjalan ulangan 1](media/teacher_berjalan_u1_sesudah.png), run sumber `20261102_eq_teacher_walk_u3` yang dipakai sebagai slot ulangan 1.
- [KD Hybrid — berjalan ulangan 3](media/hybrid_berjalan_u3_sesudah.png).
- [Supervised — berjalan ulangan 1](media/supervised_berjalan_u1_sesudah.png).
- [KD Murni — berjalan ulangan 3 pengganti](media/kd_murni_berjalan_u3_sesudah.png).

[Cuplikan deteksi dan ID tracking supervised — 10 detik](media/supervised_deteksi_tracking_10detik.mp4) berasal dari sesi pemeriksaan fungsi 22 Oktober. Kondisi fisik robot pada sesi itu **unknown**. Video merupakan rekaman keluaran gambar beranotasi dari topik ROS, bukan rekaman layar desktop; objek pada cuplikan relatif statis dan video tidak membuktikan tracking gerak atau kualitas seluruh frame. Sumber dan hash terdapat di [manifest media](media/manifest_media.json).

## Sumber dan batas penggunaan

Grafik TEST berasal dari [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md); teacher satu checkpoint, student rerata tiga seed. TEST sudah pernah digunakan sebelumnya. Grafik kamera berasal dari [T38](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md): 200 frame dengan target dan 60 tanpa target; 50 frame gawang parsial dipisahkan. T38 bersifat retrospektif dari satu rangkaian kamera dan label awal dibantu model sebelum ditinjau.

Grafik runtime menggunakan [T36](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md), serta sumber frame aktif yang dipetakan oleh audit. CPU dinormalisasi terhadap 16 CPU logis dan RAM adalah RSS **proses detektor**, bukan seluruh sistem. Pengukuran lintas sesi diterima untuk pembahasan deskriptif; rincian tersedia di [audit](../../2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md). [T42](../../../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md) adalah ablasi di VAL, bukan hasil kamera atau TEST. Waktu training menggunakan [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md); beban server dapat berbeda.

[Manifest grafik](grafik-final/manifest_grafik.json) mencatat SHA-256 setiap sumber dan keluaran. [Skrip pembuat](../../../scripts/build_visualisasi_publik_20261109.py) membutuhkan tabel serta CSV runtime per frame; sebagian CSV runtime dan media sumber hanya tersedia pada checkout robot, bukan semua ikut dipublikasikan. Kumpulan awal `grafik/` dan `grafik-v2/` adalah keluaran lokal sebelum perapian label; **gunakan `grafik-final/`** sebagai versi final.
