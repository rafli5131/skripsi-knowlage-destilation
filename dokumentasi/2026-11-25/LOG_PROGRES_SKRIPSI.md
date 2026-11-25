# Log progres - 25 November 2026

Naskah skripsi tujuh bab sudah sampai versi **v20** (24 November 2026, 115 halaman). Semua gambar sudah terisi. Yang tersisa adalah isian identitas dan tanggal dari penulis, satu penanda cek foto, dan persetujuan pembimbing. Pada 25 November, dokumentasi repositori disesuaikan dengan naskah tersebut: README, draf laporan, log, memory, dan catatan keputusan. Tidak ada eksperimen baru, dan tidak ada berkas yang dihapus.

## Lokasi naskah

| Berkas | Lokasi |
|---|---|
| Naskah DOCX dan PDF v1 sampai v20 | `E:\Kuliah\Thesis\Laporan\Skripsi\Skripsi_KD_OP3_vNN.docx` dan `.pdf` |
| Catatan sunting setiap versi | `E:\Kuliah\Thesis\Laporan\Skripsi\CATATAN_SUNTING_vNN.md` (v1 sampai v6, v9 sampai v16) |
| Pemeriksaan istilah KBBI | `E:\Kuliah\Thesis\Laporan\Skripsi\CEK_KBBI.md` |
| Sumber pembangun naskah v20 | `E:\Kuliah\Thesis\Laporan\Skripsi\kerja\sumber_naskah_v20.zip` (skrip python-docx, proposal, templat, gambar, grafik) |
| Salinan Markdown naskah v20 | [`laporan/draf-7-bab/`](../../laporan/draf-7-bab/README.md) |

## Riwayat naskah 13 sampai 24 November

| Versi | Tanggal | Perubahan utama |
|---|---|---|
| v1 sampai v3 | 13-14 Nov | Naskah tujuh bab pertama disusun dari proposal Bab 1-3 dan bukti repositori. Gelar Sarjana Teknik. Tatakan robot dicantumkan. KF-03 ditulis tetap seperti yang di-ACC. Halaman awal serta Bab 4 dan 6 disusun mengikuti pola skripsi kakak tingkat. |
| v4 sampai v8 | 18 Nov | Catu daya: OpenCR dicatu adaptor 12 V dan NUC adaptor 19 V. Tabel server memakai spesifikasi 16 November. Baris *teacher* jalur TEST (D24), T44, dan T45 masuk Bab 6. Perbandingan dengan penelitian lain dihapus. Gambar dari skripsi Brilliant (2024) diekstrak langsung dari PDF. Rujukan pengujian kotak hitam dan rekayasa kebutuhan, antara lain Khan dan Khan (2012) dan Glinz (2007), ditambahkan. |
| v9 | 24 Nov | Rumusan masalah menjadi empat; rumusan implementasi sistem dihapus. Subbab 6.1 memakai kasus uji dari `bukti_kebutuhan/` (commit `1c022d0`). |
| v10 | 24 Nov | 14 grafik Bab 6 dibuat ulang dengan gaya seragam dan tanpa kode percobaan internal. Batasan ukuran masukan dikoreksi. Lebar gambar dibatasi 14 cm. |
| v11 | 24 Nov | Bab 6 disusun ulang mengikuti urutan rumusan masalah. Susunannya: 6.1 fungsional, 6.2 mAP, 6.3 P/R/F1, 6.4 latensi dan FPS, 6.5 CPU dan RAM, 6.6 tambahan, dan 6.7 evaluasi keseluruhan. Bab 6 berisi 21 tabel dan 22 gambar. |
| v12 | 24 Nov | Tiga diagram baru: Gambar 3.1 alir penelitian, Gambar 5.8 blok satu langkah pelatihan KD hibrida, dan Gambar 5.9 alir pelatihan dan seleksi model. |
| v13 | 24 Nov | Tambahan: median dan P95 latensi (Tabel 6.18), Lampiran C (24 *run*), Lampiran D (akurasi setiap *seed*), F1 per kelas, penjelasan tidak adanya selang kepercayaan, abstrak sekitar 290 kata, serta Daftar Istilah dan Singkatan (49 entri). |
| v14 | 24 Nov | 14 paper versi terbit ditambahkan ke folder Paper dan diberi nama sesuai pola. Entri Daftar Referensi diganti ke versi terbit. Kutipan Chen, et al. (2017), Stanton, et al. (2021), dan Huang, et al. (2022) diberi nomor halaman. |
| v15 | 24 Nov | Daftar Referensi diseragamkan menurut Panduan Skripsi FILKOM v3.0 Subbab 3.6.6.3 (D26). Reddi, et al. (2020) dan Paszke, et al. (2019) diganti ke versi terbit. Email penulis diisi. |
| v16 | 24 Nov | Barry, et al. (2019) diganti ke IVCNZ 2019 dan Meneghetti, et al. (2021) ke *Journal of Intelligent & Robotic Systems*. Gholami, et al. (2021) tetap pracetak arXiv. |
| v17 | 24 Nov | Tanda tangan prakata memakai nama lengkap penulis. Blok tanda tangan dibuat muat di satu halaman. |
| v18 sampai v20 | 24 Nov | Gambar 5.7 berupa denah simulasi tampak atas yang diberi catatan "ilustrasi, tidak berskala". Gambar 5.16, 4.3, dan 5.12 memakai foto dokumentasi. Spesifikasi baterai unit penelitian dicatat sesuai label (D27). |

## Isi pokok naskah v20

- **Rumusan masalah:** (1) mAP, (2) *precision*, *recall*, dan F1, (3) latensi dan FPS saat robot diam dan berjalan, (4) penggunaan CPU dan RAM. Pemetaan ke Subbab 6.2 sampai 6.5 ada di [README draf](../../laporan/draf-7-bab/README.md#rumusan-masalah-dan-letak-jawabannya).
- **Penamaan:** naskah menyebut T38 sebagai Set Kamera 1 dan T43 sebagai Set Kamera 2. Tabel padanan lengkap ada di [README draf](../../laporan/draf-7-bab/README.md#padanan-istilah-naskah-dan-kode-repositori).
- **Jalur evaluasi:** Bab 6 menyajikan kedua jalur evaluasi, yaitu validator dan prediksi, untuk TEST (Tabel 6.6 dan 6.13) dan kamera OP3 (Tabel 6.9). Bab 7 butir 1 dan 2 menyebut angka jalur prediksi untuk kamera OP3, karena jalur ini sama dengan *runtime* robot. Saran nomor 2 meminta jalur ini ditetapkan sebagai jalur utama sejak awal. Keputusan jalur angka utama bersama pembimbing (yang tercatat terbuka sejak 21 November) belum dikonfirmasi.
- **CPU (RM4):** disajikan sebagai CPU proses detektor dan RSS (Tabel 6.20), ditambah *replay offline* T45 (Tabel 6.21). Kesimpulannya, CPU dan RSS tidak membedakan efisiensi model secara jelas.
- **KF-03:** Tabel 6.1 menulis status "Lulus dengan catatan". Konfirmasi penulis masih ditunggu.
- **Catu daya:** spesifikasi bawaan OP3 adalah LiPo tiga sel 11,1 V 3.300 mAh (ROBOTIS, n.d.a). Unit penelitian memakai LiPo empat sel 14,8 V 2.200 mAh sesuai label baterai. Baterai tidak dipakai selama pengujian.
- **Gambar dokumentasi:** foto berasal dari `E:\Kuliah\Thesis\Dokumentasi\Dokumentasi\Dokumentasi\`. Gambar 5.16 dari `IMG_20261103_172715.jpg`. Gambar 4.3 dan 5.12 dari berkas PNG berlatar putih yang dikirim penulis. Ada perbedaan tulisan tali tatakan ("JAKARTA ROBOT" pada PNG, "JAKARTA HOBBY" pada foto kamera); atas keputusan penulis, PNG tetap dipakai karena yang dimaksud adalah stand robot.
- **Posisi objek uji:** foto 22 Oktober, 2 November, dan 3 November menunjukkan susunan objek yang berbeda. Penulis menyatakan foto-foto itu dipakai untuk mengecek deteksi. Naskah tetap menyebut objek ditempatkan statis pada posisi bertanda, dan denah Gambar 5.7 mengikuti susunan 3 November.

## Yang masih terbuka

1. Tanggal ujian dan dua tanggal tanda tangan.
2. Tujuh isian `[DIISI PENULIS]` di prakata.
3. `[PERLU DICEK]` di Subbab 5.2.1.2: kesamaan unit pada foto rangkaian elektronika (Brilliant, 2024) dengan unit penelitian.
4. Persetujuan pembimbing atas empat rumusan masalah (D25) dan status KF-03.
5. Pemeriksaan istilah di `CEK_KBBI.md`.

## Perapian repositori 25 November

- **[README utama](../../README.md):** status diperbarui ke naskah v20 dan ditambah bagian naskah skripsi. Riwayat progres 12 sampai 23 November tetap tersimpan di bagian yang dapat dibuka-tutup. Tabel langkah berikutnya disesuaikan dengan pekerjaan yang tersisa, dan struktur folder ditambah `laporan/alat/` serta arsip draf.
- **[`laporan/draf-7-bab/`](../../laporan/draf-7-bab/README.md):** draf ringkas 12 sampai 23 November disalin utuh ke [`laporan/arsip/draf-7-bab-2026-11-23/`](../../laporan/arsip/draf-7-bab-2026-11-23/README.md). Sesudahnya, isi folder diganti dengan salinan Markdown naskah v20 (Bab 1-7, halaman awal, daftar referensi, dan lampiran). Nama berkas bab tetap sama, jadi tautan lama tidak putus.
- **[`laporan/alat/konversi_naskah_ke_markdown.py`](../../laporan/alat/konversi_naskah_ke_markdown.py):** skrip baru untuk membuat ulang salinan Markdown dari DOCX.
- **[`laporan/draf-bab-iv-v/README.md`](../../laporan/draf-bab-iv-v/README.md):** diberi catatan arah ke naskah v20.
- **[`docs/DECISIONS.md`](../../docs/DECISIONS.md):** ditambah D25 (empat rumusan masalah), D26 (format Daftar Referensi), dan D27 (spesifikasi baterai unit penelitian).
- **[Memory 25 November](../../memory/2026-11-25-naskah-skripsi-v20.md), [indeks dokumentasi](../INDEKS.md), dan [`agent.md`](../../agent.md):** diperbarui.
- **Tidak diubah:** folder `Claude outputs/` (belum dilacak Git) dan folder `Paper\_to_delete\` di luar repositori.
- **Git:** belum ada commit.
