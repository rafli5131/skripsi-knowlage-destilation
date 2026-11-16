# Log progres — 12 November 2026

## Audit grafik akurasi

Sepuluh sumber cocok dengan manifest dan 1.500 baris data agregat cocok saat dihitung ulang. Sebanyak 18 PNG historis cocok dengan commit asal tetapi berbeda dari hash pada manifest lama; penyebab historis belum diketahui. [Audit lengkap dan hash aktual](AUDIT_GRAFIK_AKURASI.md) mempertahankan catatan awal. Sebanyak [18 grafik hasil reproduksi terpisah](grafik-akurasi-terverifikasi/README.md) dibuat dari sumber yang sama dengan manifest baru; reproduksi kedua pada environment sama cocok 18/18 hash; keduanya tidak menggantikan file historis. Dua kurva mAP tambahan pada manifest lama cocok hash-nya.

## Grafik runtime OP3

Ke-24 sumber jendela runtime tersedia dan cocok dengan manifest; generator juga memeriksa jumlah frame dan rerata latensi terhadap T36. Dibuat 10 PNG (empat model dan gabungan, ID/EN), satu CSV dan [manifest](../model/manifest_grafik_garis_runtime.json). Grafik berukuran 2.800 × 3.000 piksel, nilai per bin 2 detik. Pemeriksaan visual lembar pratinjau lima panel untuk setiap bahasa menemukan judul, sumbu, legenda dan garis 8 FPS terlihat; teks catatan kaki relatif kecil pada tampilan diperkecil dan perlu diperiksa pada skala akhir cetak. Garis 8 FPS bukan bukti setiap bin memenuhi kriteria rata-rata per run.

Grafik: [teacher](../model/teacher_yolo11n/README.md), [Hybrid](../model/kd_hybrid/README.md), [supervised](../model/supervised/README.md), [KD murni](../model/kd_murni/README.md), dan [gabungan](../model/gabungan/README.md). CPU dan RSS adalah proses detektor; perbandingan bersifat deskriptif. Data mentah tidak diubah atau dipublikasikan.

## Naskah dan tindak lanjut

[Draf tujuh bab](../../laporan/draf-7-bab/README.md) memetakan hasil ke D17 dan menyertakan tabel fungsional retrospektif. [F1 utama T38](T38_F1_D11_turunan.csv) dihitung dari precision dan recall makro sumber; nilai historis rerata F1 kelas tetap ditampilkan terpisah. KF-03 hanya didukung keberadaan ID, belum merupakan bukti lulus kestabilan ID pada objek bergerak; tracking bukan tujuan wajib. Kriteria KNF-01 dipakai pada FPS rerata per run: minimum T36 9,6869 FPS.

Draf masih memerlukan pengembangan pembahasan pustaka, verifikasi sitasi, penyesuaian format kampus dan tinjauan pembimbing. T43 masih rencana dan tidak dijalankan. Tidak ada kamera, servo, robot, training, atau evaluasi baru yang dijalankan untuk pekerjaan ini.

## Evaluasi T43 — pembaruan setelah pengambilan

T43 dilaksanakan setelah catatan sebelumnya: 260 frame (100 berobjek + 30 kosong untuk masing-masing kondisi diam dan berjalan di tempat), ditinjau `bhre`; 52 frame sampel dilabeli tanpa kotak prediksi sebelum pra-label. Seluruh 260 label dan log penyimpanannya lengkap. Pra-label merupakan gabungan empat model, operator telah melihat preview Hybrid, dan konvensi diklarifikasi setelah sampel awal. Batas atas kotak bagian bawah gawang belum ditentukan dengan landmark tetap.

[Hasil empat model dan grafik](percobaan-39-evaluasi-t43/README_ID.md) serta [T43](../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md) bersifat eksploratif; semua frame bergawang parsial, dengan kotak bagian bawah gawang dan badan robot, berbeda dari T38. Evaluasi offline menggunakan confidence >0,25 untuk precision/recall/F1 dan floor 0,001 untuk AP. Pada ambang tetap teacher dan KD Murni memiliki 0/200 TP gawang; perlu audit sebaran confidence dan kotak. Tinjauan 52 frame oleh orang yang sama bukan bukti kesepakatan antarpeninjau. Data mentah dan log robot tetap lokal.

## Catatan tambahan

- **D18:** persetujuan pembimbing diberikan secara lisan pada 12 November 2026 (dilaporkan Bhre).
- **D20:** kondisi berjalan pada T36 dan T43 dibangkitkan oleh skrip pengujian atas arahan peneliti; rincian ada di [`docs/DECISIONS.md`](../../docs/DECISIONS.md).
- **Interpretasi T43 (D21):** AP50 gawang teacher, Hybrid, dan supervised sama-sama 0,995, sedangkan pada confidence > 0,25 gawang yang lolos 0/200, 196/200, dan 99/200 (KD murni 0/200, AP50 0,608). Selisih F1 terutama berasal dari confidence pada gawang parsial, bukan kemampuan menemukan objek. Selisih mAP50–95 gawang (Hybrid 0,884, teacher 0,656) bergantung pada konvensi kotak bagian bawah. Uji sensitivitas direncanakan di [prompt T43 sensitivitas](../../prompt/PROMPT_T43_UJI_SENSITIVITAS_2026-11-12.md). Sumber angka: `runs/op3_t43_evaluation/20261112_reviewed_260/results.json`.

## Sensitivitas T43 — bagian A dan B selesai

Sapuan confidence pada 260 frame mereproduksi AP dan hitungan baseline >0,25 untuk keempat model. Pemeriksaan teacher menemukan jalur validasi AP memakai tensor 512×672 dan NMS multi-label, sedangkan jalur prediksi operasi 480×640 dengan NMS default. Efek masing-masing belum diisolasi; jangan menjelaskan selisih AP–F1 hanya sebagai kalibrasi.

Dipo meninjau 52 frame mengikuti aturan yang diperjelas dan kemudian 52 frame dengan konvensi alternatif. Frame alternatif 29 diperiksa dan disimpan ulang oleh Dipo setelah satu kelas salah ditemukan. Pada IoU ≥0,5 kesepakatan dengan Bhre adalah 40/40 per kelas; rata-rata IoU bola/gawang/robot 0,6811/0,6389/0,8882. Urutan mAP50–95 berubah antartiga label; efek peninjau, klarifikasi aturan dan urutan anotasi tidak terpisah. Lihat [tabel tiga set](../../analisis_performa/tabel/T43_sensitivitas_label_52.md) dan [dokumentasi](percobaan-40-sensitivitas-t43/README_ID.md). Hasil eksploratif, model utama dan ambang operasi tidak diganti.
- **Koreksi interpretasi T43 (D22):** setelah uji sensitivitas, penjelasan "selisih F1 karena confidence" hanya berlaku untuk supervised. Pada jalur prediksi yang dipakai robot, teacher praktis tidak mendeteksi gawang parsial (recall 0 pada > 0,05). F1 stabil antarpeninjau, mAP50–95 tidak; dengan konvensi seluruh rangka gawang, supervised tertinggi dan Hybrid turun. Keunggulan Hybrid bergantung pada konvensi kotak bagian bawah. AP (`model.val`) dan P/R/F1 (`model.predict`) dihitung lewat jalur berbeda. Rincian di [`docs/DECISIONS.md`](../../docs/DECISIONS.md).
