# Log progres - 25 November 2026

Naskah skripsi tujuh bab sudah sampai versi **v25** (25 November 2026, 116 halaman). Semua gambar sudah terisi. Yang tersisa adalah isian identitas dan tanggal dari penulis, satu penanda cek foto, dan persetujuan pembimbing. Pada 25 November, dokumentasi repositori disesuaikan dengan naskah tersebut: README, draf laporan, log, memory, dan catatan keputusan. Tidak ada eksperimen baru, dan tidak ada berkas yang dihapus.

## Lokasi naskah

| Berkas | Lokasi |
|---|---|
| Naskah DOCX dan PDF v1 sampai v25 | `E:\Kuliah\Thesis\Laporan\Skripsi\Skripsi_KD_OP3_vNN.docx` dan `.pdf` |
| Catatan sunting setiap versi | `E:\Kuliah\Thesis\Laporan\Skripsi\CATATAN_SUNTING_vNN.md` (v1 sampai v6, v9 sampai v16, v21 sampai v25) |
| Pemeriksaan istilah KBBI | `E:\Kuliah\Thesis\Laporan\Skripsi\CEK_KBBI.md` |
| Sumber pembangun naskah v25 | `E:\Kuliah\Thesis\Laporan\Skripsi\kerja\sumber_naskah_v25.zip` (skrip python-docx, proposal, templat, gambar, grafik) |
| Salinan Markdown naskah terbaru (v25) | [`laporan/draf-7-bab/`](../../laporan/draf-7-bab/README.md) |

## Riwayat naskah 13 sampai 25 November

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
| v21 | 25 Nov | Rumusan masalah disempurnakan (D25): rumusan 1 menyebut *student* KD hibrida, rumusan 3 dan 4 mencakup ketiga model (KD hibrida, *supervised*, *teacher*), dan kata "efisiensi" serta "secara penuh" dihapus. Batasan butir 3 mendefinisikan skala t sebagai skala kustom (810.649 parameter, bukan skala resmi YOLO11 n, s, m, l, x). Batasan butir 4 baru menegaskan KD hibrida sebagai model hasil KD dan KD murni sebagai pembanding tambahan. Ikut disesuaikan: tujuan, latar belakang, Subbab 3.2.5, Tabel 3.4, tujuan Subbab 6.2 sampai 6.5, Subbab 6.7, serta kesimpulan Bab 7 butir 3 dan 4 (angka *supervised* ditambahkan). |
| v22 | 25 Nov | Pemeriksaan menyeluruh format, struktur, dan kebahasaan. Bagian yang masih menyebut "model hasil KD" sebagai pembanding disesuaikan dengan rumusan v21 (KD hibrida, *supervised*, dan *teacher* sebagai pembanding utama). Daftar Istilah ditambah CNN, IDF1, INT8, MOTA, ONNX, PTQ, dan QAT (56 entri) dan tabelnya boleh berlanjut ke halaman berikutnya. Istilah asing yang belum miring dirapikan (*servo*, *loss*, *head*, *sigmoid*, *track*, *predict*, *log*), "VOC" menjadi "PASCAL VOC", TTL ditulis kepanjangannya, sitasi halaman memakai spasi ("p. 564"), spasi ganda dihapus, dan Gambar 5.16 diperkecil agar tidak menyisakan halaman kosong. |
| v23 | 25 Nov | Pengertian *seed* ditambahkan di Subbab 2.2.9 (nilai awal pembangkit bilangan acak semu, cara PyTorch dan Ultralytics menetapkannya, sumber variasi menurut Bouthillier, et al. dan Picard). Subbab 3.2.5 ditambah penjelasan perbedaan *seed* 42, 1337, dan 2025 (hanya nilai awal acak yang berbeda; bobot awal, urutan data, dan augmentasi ikut berbeda) serta peran setiap *seed*. Referensi baru Ultralytics, n.d.b (*Model training with Ultralytics YOLO*); sumber Ultralytics lama bergeser ke n.d.c dan n.d.d. Jumlah referensi 67, halaman 116. |
| v24 | 25 Nov | Alasan *supervised* *seed* 1337 ditulis: KD hibrida *seed* 1337 dan KD murni *seed* 42 dipilih dari mAP50-95 VAL tertinggi, sedangkan *supervised* memakai *seed* 1337 agar berpasangan dengan KD hibrida (mAP50-95 VAL *supervised*: 0,7189, 0,7179, 0,7255 untuk *seed* 42, 1337, 2025). Subbab 3.2.5, 5.1.2.2, dan langkah 2 Subbab 6.2.2 disesuaikan. |
| v25 | 25 Nov | Hasil cek KBBI VI Daring diterapkan: "port" menjadi "porta" (4 kali), "variansnya" menjadi "variansinya", "skala kustom" dan "berskala kustom" menjadi "skala khusus" dan "berskala khusus". Nama lembaga diseragamkan menjadi ROBOTIIK di manfaat penelitian dan tabel pemangku kepentingan Bab 4. Halaman tetap 116. |

## Isi pokok naskah v25

- **Rumusan masalah:** (1) mAP *student* KD hibrida dibandingkan *supervised* dan *teacher*, (2) *precision*, *recall*, dan F1, (3) latensi dan FPS saat robot diam dan berjalan, (4) penggunaan CPU dan RAM. Rumusan 2 sampai 4 berlaku untuk ketiga model yang sama. Pemetaan ke Subbab 6.2 sampai 6.5 ada di [README draf](../../laporan/draf-7-bab/README.md#rumusan-masalah-dan-letak-jawabannya).
- **Penamaan:** naskah menyebut T38 sebagai Set Kamera 1 dan T43 sebagai Set Kamera 2. Tabel padanan lengkap ada di [README draf](../../laporan/draf-7-bab/README.md#padanan-istilah-naskah-dan-kode-repositori).
- **Jalur evaluasi:** Bab 6 menyajikan kedua jalur evaluasi, yaitu validator dan prediksi, untuk TEST (Tabel 6.6 dan 6.13) dan kamera OP3 (Tabel 6.9). Bab 7 butir 1 dan 2 menyebut angka jalur prediksi untuk kamera OP3, karena jalur ini sama dengan *runtime* robot. Saran nomor 2 meminta jalur ini ditetapkan sebagai jalur utama sejak awal. Keputusan jalur angka utama bersama pembimbing (yang tercatat terbuka sejak 21 November) belum dikonfirmasi.
- **CPU (RM4):** disajikan sebagai CPU proses detektor dan RSS (Tabel 6.20), ditambah *replay offline* T45 (Tabel 6.21). Kesimpulannya, CPU dan RSS tidak membedakan efisiensi model secara jelas.
- **KF-03:** Tabel 6.1 menulis status "Lulus dengan catatan". Menurut laporan Bhre, pembimbing menyetujuinya secara lisan pada 25 November 2026, bersama keempat rumusan masalah (D25).
- **Catu daya:** spesifikasi bawaan OP3 adalah LiPo tiga sel 11,1 V 3.300 mAh (ROBOTIS, n.d.a). Unit penelitian memakai LiPo empat sel 14,8 V 2.200 mAh sesuai label baterai. Baterai tidak dipakai selama pengujian.
- **Gambar dokumentasi:** foto berasal dari `E:\Kuliah\Thesis\Dokumentasi\Dokumentasi\Dokumentasi\`. Gambar 5.16 dari `IMG_20261103_172715.jpg`. Gambar 4.3 dan 5.12 dari berkas PNG berlatar putih yang dikirim penulis. Ada perbedaan tulisan tali tatakan ("JAKARTA ROBOT" pada PNG, "JAKARTA HOBBY" pada foto kamera); atas keputusan penulis, PNG tetap dipakai karena yang dimaksud adalah stand robot.
- **Posisi objek uji:** foto 22 Oktober, 2 November, dan 3 November menunjukkan susunan objek yang berbeda. Penulis menyatakan foto-foto itu dipakai untuk mengecek deteksi. Naskah tetap menyebut objek ditempatkan statis pada posisi bertanda, dan denah Gambar 5.7 mengikuti susunan 3 November.

## Yang masih terbuka

1. Tanggal ujian dan dua tanggal tanda tangan.
2. Tujuh isian `[DIISI PENULIS]` di prakata.
3. `[PERLU DICEK]` di Subbab 5.2.1.2: kesamaan unit pada foto rangkaian elektronika (Brilliant, 2024) dengan unit penelitian.
4. Konfirmasi pembimbing atas jalur angka utama kamera OP3 (terbuka sejak 21 November).

Sudah selesai pada 25 November: persetujuan lisan pembimbing atas empat rumusan masalah dan KF-03, pemeriksaan `CEK_KBBI.md` (diperbarui dengan KBBI VI Daring), dan keseragaman nama ROBOTIIK. Folder `Paper\_to_delete\` dikosongkan sendiri oleh penulis; agen tidak menghapus berkas apa pun.

## Perapian repositori 25 November

- **[README utama](../../README.md):** status diperbarui ke naskah v20 (lalu v21 pada commit berikutnya) dan ditambah bagian naskah skripsi beserta tabel rumusan masalah dan hasil singkatnya. Riwayat progres 12 sampai 23 November tetap tersimpan di bagian yang dapat dibuka-tutup. Tabel langkah berikutnya disesuaikan dengan pekerjaan yang tersisa, dan struktur folder ditambah `laporan/alat/` serta arsip draf.
- **[`laporan/draf-7-bab/`](../../laporan/draf-7-bab/README.md):** draf ringkas 12 sampai 23 November disalin utuh ke [`laporan/arsip/draf-7-bab-2026-11-23/`](../../laporan/arsip/draf-7-bab-2026-11-23/README.md). Sesudahnya, isi folder diganti dengan salinan Markdown naskah v20 (Bab 1-7, halaman awal, daftar referensi, dan lampiran). Nama berkas bab tetap sama, jadi tautan lama tidak putus.
- **Data pribadi:** karena repositori ini publik, `HALAMAN_AWAL.md` tidak memuat nama, NIM, NIK, email, atau nama pihak di prakata. Lembar pengesahan, pernyataan orisinalitas, dan prakata hanya diringkas isinya, sedangkan abstrak, *abstract*, dan daftar istilah disalin utuh. Skrip konversi menerapkan aturan yang sama.
- **[`laporan/alat/konversi_naskah_ke_markdown.py`](../../laporan/alat/konversi_naskah_ke_markdown.py):** skrip baru untuk membuat ulang salinan Markdown dari DOCX.
- **[`laporan/draf-bab-iv-v/README.md`](../../laporan/draf-bab-iv-v/README.md):** diberi catatan arah ke naskah terbaru (v20, lalu v21).
- **[`docs/DECISIONS.md`](../../docs/DECISIONS.md):** ditambah D25 (empat rumusan masalah), D26 (format Daftar Referensi), dan D27 (spesifikasi baterai unit penelitian).
- **[Memory 25 November](../../memory/2026-11-25-naskah-skripsi-v20.md), [indeks dokumentasi](../INDEKS.md), dan [`agent.md`](../../agent.md):** diperbarui.
- **Tidak diubah:** folder `Claude outputs/` (belum dilacak Git) dan folder `Paper\_to_delete\` di luar repositori.
- **Git:** belum ada commit.

## Pembaruan v21 (25 November)

Rumusan masalah disempurnakan seperti baris v21 di atas. Salinan Markdown di `laporan/draf-7-bab/` dibuat ulang dari v21, dan README, D25, memory, serta `agent.md` disesuaikan. Ringkasan prakata di `HALAMAN_AWAL.md` kini dibuat oleh skrip konversi dengan rincian pihak menurut perannya, tetap tanpa nama.

## Pembaruan v22 (25 November)

Naskah diperiksa ulang dari halaman sampul sampai lampiran. Hasil pemeriksaan otomatis: tidak ada tanda pisah em atau en, nomor Tabel (46), Gambar (44), dan Kode Program (5) berurutan dan semuanya dirujuk, Persamaan 2.1 sampai 2.15 dirujuk, tidak ada rujukan subbab yang putus, dan 66 entri Daftar Referensi berurutan alfabet. Pemeriksaan PDF tidak menemukan judul subbab yang tertinggal di dasar halaman. Perbaikannya tercantum pada baris v22 di atas dan di `CATATAN_SUNTING_v22.md`. Salinan Markdown di `laporan/draf-7-bab/` dibuat ulang dari v22, tetap tanpa data pribadi.

## Pembaruan v23 (25 November)

Atas permintaan penulis, naskah kini menjelaskan apa itu *seed* dan apa beda ketiga *seed*. Rinciannya ada pada baris v23 di atas dan di `CATATAN_SUNTING_v23.md`. Isi penjelasan bersumber dari Bouthillier, et al. (2021), Picard (2021), dokumentasi PyTorch, dan dokumentasi pelatihan Ultralytics. Fakta dari repositori ikut menjadi dasar, yaitu `args.yaml` run KD hibrida *seed* 1337 (`seed: 1337`, `deterministic: true`, `pretrained: false`). Salinan Markdown dibuat ulang dari v23, tetap tanpa data pribadi.

## Pembaruan v24 (25 November)

Alasan *checkpoint* *supervised* *seed* 1337 dicek di repositori, lalu ditulis di naskah. Repositori tidak memuat kalimat "dipilih karena". Dasarnya adalah protokol pembandingan berpasangan per *seed* ([`docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md`](../../docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md)), rencana evaluasi OP3 untuk Hybrid *seed* 1337 dan *supervised* *seed* 1337 pada frame yang sama ([`docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md`](../../docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md)), dan nilai VAL per *seed* ([hasil multi-*seed* VAL](../../analisis_performa/lab_server/HASIL_KD_HYBRID_MULTI_SEED_VAL_2026-10-22.md)). Menurut nilai VAL tersebut, *supervised* *seed* 1337 bukan *seed* *supervised* terbaik. Rinciannya ada di `CATATAN_SUNTING_v24.md`.

## Pembaruan v25 (25 November)

- **Pemeriksaan KBBI.** Seluruh kata tegak di naskah (1.472 kata unik) dicocokkan dengan teks KBBI IV. Kata yang tidak ditemukan dicek di KBBI VI Daring. Ada empat perbaikan: port menjadi porta, variansnya menjadi variansinya, kustom menjadi khusus, dan Robotiik menjadi ROBOTIIK. "humanoid", "konvolusional", dan "hiperparameter" tidak ada di KBBI VI, tetapi atas keputusan penulis tetap dipakai. Rinciannya ada di `E:\Kuliah\Thesis\Laporan\Skripsi\CEK_KBBI.md`.
- **Persetujuan pembimbing.** Bhre melaporkan persetujuan lisan atas empat rumusan masalah dan KF-03 pada 25 November 2026 (D25).
