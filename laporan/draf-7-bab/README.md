# Draf skripsi tujuh bab

Draf kerja berdasarkan struktur D17 dan bukti penelitian yang tersedia. Naskah lama tetap disimpan di [folder Bab IV–V](../draf-bab-iv-v/README.md) dan [proposal Bab I–III](../../DRAF_PROPOSAL_BAB_I-III.md). Draf ini belum merupakan naskah akhir atau persetujuan pembimbing atas teksnya.

| Bab | Dokumen | Isi |
|---|---|---|
| 1 | [Pendahuluan](BAB_1_PENDAHULUAN.md) | Latar belakang, lima rumusan, tujuan, batasan dan sistematika |
| 2 | [Landasan kepustakaan](BAB_2_LANDASAN_KEPUSTAKAAN.md) | Deteksi, KD, metrik, ROS 2, dan arahan penelitian terkait |
| 3 | [Metodologi](BAB_3_METODOLOGI.md) | Dataset, model, TEST, T38, T42 dan protokol runtime |
| 4 | [Rekayasa kebutuhan](BAB_4_REKAYASA_KEBUTUHAN.md) | Kebutuhan KF/KNF dan keterlacakan bukti |
| 5 | [Perancangan dan implementasi](BAB_5_PERANCANGAN_IMPLEMENTASI.md) | Alur sistem, model, keluaran dan logging |
| 6 | [Pengujian dan pembahasan](BAB_6_PENGUJIAN_DAN_PEMBAHASAN.md) | Tabel fungsional retrospektif, TEST, T38, T36/T37, T35, T42 |
| 7 | [Penutup](BAB_7_PENUTUP.md) | Jawaban rumusan dan saran berdasarkan bukti |

F1 utama D11 pada T38 dihitung dari precision dan recall makro tanpa menimpa F1 per kelas pada tabel sumber. Status uji pada Bab 6 secara eksplisit membedakan bukti yang ada dari hal yang tidak dapat dipastikan. Kemampuan tracking dicatat sebagai tambahan historis, bukan tujuan wajib penelitian.

Sebelum penyerahan: kembangkan pembahasan penelitian terkait dan verifikasi sitasi sumber primer, nomor gambar/tabel, format kampus, identitas dan tanggal persetujuan yang relevan, lalu konsultasikan naskah ke pembimbing. Bukti visual: [grafik akurasi hasil reproduksi](../../dokumentasi/2026-11-12/grafik-akurasi-terverifikasi/README.md) dan [grafik runtime per model](../../dokumentasi/model/README.md). T43 dan uji sensitivitasnya selesai pada 12 November (D21, D22) tetapi belum dimasukkan ke draf; statusnya eksploratif dan penempatannya di Bab 6 menunggu sesi jalur tunggal OP3. Verifikasi jalur TEST 13 November (D23) menunjukkan angka T05/T30 stabil terhadap pergantian jalur dan F1 Hybrid serta Supervised setara pada ambang runtime; kalimat Bab 6 dan 7 tentang F1 Hybrid yang sedikit lebih rendah perlu disesuaikan.
