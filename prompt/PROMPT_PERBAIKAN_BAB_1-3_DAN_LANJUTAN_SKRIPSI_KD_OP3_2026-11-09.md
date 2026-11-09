# Prompt perbaikan Bab I–III dan penyelesaian draf skripsi KD–OP3

Gunakan prompt ini untuk memperbaiki naskah yang sudah ada, lalu menyelesaikan draf skripsi berdasarkan hasil penelitian yang terverifikasi. Baca seluruh instruksi sebelum mulai.

---

## Peran dan hasil yang diminta

Anda adalah asisten peneliti dan penulis akademik Bahasa Indonesia. Perbaiki **Bab I–III** dari proposal/naskah peneliti, lalu lanjutkan **seluruh bagian skripsi yang diperlukan sampai tersedia draf lengkap**: bagian awal, bab lanjutan sesuai pedoman, penutup, daftar referensi, dan lampiran. Gunakan materi yang sudah ada; jangan berhenti setelah membuat kerangka atau rencana.

Selesaikan seluruh pekerjaan yang dapat dilakukan dari bukti yang tersedia. Jika data, template, persetujuan atau sitasi belum tersedia, lanjutkan bagian lain dan tandai bagian yang bergantung pada sumber tersebut. Jangan mengaku skripsi disetujui atau siap diserahkan tanpa pemeriksaan peneliti/pembimbing. Jangan mengarang fakta, hasil, rujukan, persetujuan, kondisi eksperimen, data personal, atau nomor halaman.

## Lingkup dan keputusan yang harus dipatuhi

1. Penelitian memakai Knowledge Distillation untuk deteksi `ball`, `gawang`, `robot` dengan ROS 2 pada ROBOTIS OP3. Teacher utama YOLO11n FP32; student YOLO11 **skala t kustom**, bukan YOLO11n standar. Supervised memakai arsitektur student yang sama. Bedakan KD Murni teacher-only dan KD Hybrid full yang memakai loss deteksi berlabel plus distilasi.
2. Gunakan judul, rumusan masalah, tujuan, batasan, dan persetujuan yang dapat diverifikasi dari naskah/dokumen paling berwenang. Prompt proposal sebelumnya menyebut judul "Implementasi Knowledge Distillation untuk Deteksi Objek pada Robot Humanoid ROBOTIS OP3", sedangkan sebagian draf repo memakai judul kerja berbeda: **cek sumber naskah pengguna**, jangan memilih diam-diam. Bila tidak dapat dipastikan, gunakan `[PERLU KONFIRMASI: ...]` dan catat opsi sumbernya.
3. Objek target untuk lingkup deteksi skripsi **diposisikan statis**; pengujian robot diam dan berjalan tetap mengikuti rumusan masalah. Tracking yang pernah dicoba adalah percobaan opsional, bukan tujuan wajib atau syarat kelulusan uji. Jangan menambahkan keberhasilan kontrol kepala/servo sebagai klaim. Jika implementasi menggunakan tracker, jelaskan hanya apabila relevan dan terverifikasi.
4. Peneliti tidak meminta evaluasi online tambahan dalam laporan. Jangan menambahkan eksperimen tersebut; pengukuran latensi, FPS, CPU dan RAM **real-time OP3** pada kondisi robot diam dan berjalan tetap wajib dibahas karena menjawab rumusan masalah.
5. Jangan memasukkan percakapan atau keputusan pribadi yang peneliti tandai "jangan dimasukkan ke skripsi". Jangan mengubah asumsi menjadi fakta yang telah diverifikasi, mengarang validitas data, atau menyembunyikan hasil yang tidak mendukung hipotesis.

## Sumber yang wajib ditelusuri

- Naskah asli peneliti dan dokumen terbaru yang sah; `DRAF_PROPOSAL_BAB_I-III.md`, `DRAF_BAB_IV-V_HASIL_DAN_PEMBAHASAN.md`, `KERANGKA_BAB_SKRIPSI.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `AUDIT_DATASET_SKRIPSI.md`, `OP3_PYTORCH_RUNTIME.md`, `configs/analysis.yaml`, `configs/model_registry.yaml`, `docs/DECISIONS.md`, serta memory terbaru.
- `analisis_performa/tabel/T05`, `T06`, `T30`, `T31`, `T35`, `T36`, `T37`, `T38`, `T42` (CSV dan Markdown) serta JSON/manifest yang dapat diakses. Periksa [audit runtime](../dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md), [audit teacher T42](../audit_teacher_t42_LTOW7Xw5.json), [dokumentasi T38](../dokumentasi/2026-11-05/percobaan-37-evaluasi-t38-empat-model/README_ID.md), dan [grafik/media terkurasi](../dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/README.md).
- Bila tersedia, gunakan `dokumentasi/2026-11-09/AUDIT_INTEGRITAS_HASIL.md`, `MATRIKS_BUKTI_DAN_CELAH.md`, dan `DRAF_BAB_IV_V_TERPADU_T38_T42.md` sebagai bahan kerja. Ketiganya dapat hanya berada di robot, sehingga periksa keberadaannya; jangan menganggap file tersebut pasti ada pada GitHub atau menganggap eksperimen belum dilakukan bila file lokal tidak tersedia.
- Temukan dan baca naskah `.docx` peneliti, `PanduanSkripsiFilkom-v3.0.pdf`, `Template/Template-Skripsi-v3.0.docx`, `Template/Template-ProposalSkripsi-v3.0.docx`, folder `Paper/`, dan rujukan ejaan bila tersedia. Lokasi historis: `E:\Kuliah\Thesis` atau `/media/bhrew/DATA1/Kuliah/Thesis`; cari lokasi aktual dengan aman. Jangan menganggap template berada di mesin saat ini.
- Jika audit dari `PROMPT_AUDIT_CELAH_SKRIPSI_KD_OP3_2026-11-09.md` tersedia, baca hasilnya. Jika tidak, lakukan pemeriksaan sumber dan perhitungan pokok secara mandiri sebagai bagian dari tugas ini; jangan berhenti hanya karena prompt audit belum dijalankan.

## Metode kerja

1. Catat daftar sumber, lokasi, waktu/versi dan commit repo. Identifikasi bagian naskah yang sudah ditulis serta perubahan peneliti; pertahankan gagasan dan bukti yang sah. Jangan menimpa naskah asli, template, gambar, data atau hasil eksperimen. Simpan keluaran di folder baru yang unik.
2. Periksa pedoman resmi dan tipe penelitian sebelum menentukan struktur. Prompt proposal sebelumnya mencatat contoh implementatif-pengembangan **tujuh bab**: Pendahuluan; Landasan Kepustakaan; Metodologi; Rekayasa Kebutuhan; Perancangan dan Implementasi; Pengujian dan Evaluasi; Penutup. Verifikasi dari PDF/template aktual. Draf repo yang menggabungkan hasil pada Bab IV–V adalah sumber isi historis; petakan ulang ke Bab IV–VII bila pedoman memang mensyaratkannya. Jika pedoman tak tersedia, gunakan struktur sementara yang diberi tanda `[PERLU VERIFIKASI PANDUAN]`.
3. Revisi Bab I: latar belakang berbasis rujukan, rumusan masalah, tujuan, manfaat, batasan, dan sistematika. Pastikan setiap tujuan selaras dengan rumusan masalah dan bukti, tanpa menambah cakupan tracking.
4. Revisi Bab II: penelitian terdahulu, deteksi objek, YOLO11, teacher–student, KD murni dan hybrid, metrik, ROS 2, OP3, dan evaluasi runtime sesuai kebutuhan. Periksa sumber asli untuk setiap klaim. Tulis sumber loss dan perbedaan metode secara tepat; jangan mengklaim algoritma KD baru tanpa bukti.
5. Revisi Bab III: tahapan penelitian, dataset/split, model, pelatihan, seleksi di VAL, pengujian, protokol OP3, definisi metrik dan cara analisis. Letakkan hasil kebutuhan/rancangan terperinci di bab yang dipersyaratkan pedoman; jangan menyajikan hasil penelitian sebagai rencana yang belum dilakukan atau sebaliknya. Nyatakan bagaimana data eksperimen yang tersedia benar-benar dikumpulkan.
6. Tulis bab lanjutan sesuai struktur terverifikasi: kebutuhan fungsional/nonfungsional yang **didukung bukti**, rancangan alur kamera–ROS 2–model–keluaran, implementasi, metode pengujian, hasil, analisis dan pembahasan. Jangan mengada-adakan kebutuhan yang dianggap sudah diuji; bila belum ada bukti tandai `[BUTUH BUKTI UJI: ...]`.
7. Tulis kesimpulan yang menjawab setiap rumusan masalah, saran yang relevan, abstrak dan kata kunci sesuai bukti, daftar referensi dan lampiran. Jangan menambah klaim di abstrak yang tidak dibahas dalam hasil.

## Aturan numerik dan interpretasi

- Untuk TEST resmi, cek [T05](../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md). Teacher satu checkpoint; student dapat berupa rerata tiga seed. TEST pernah digunakan pada tahap sebelumnya. Sertakan perbedaan hasil yang sebenarnya: Hybrid lebih tinggi pada mAP50–95 dibanding supervised, sementara F1 sedikit lebih rendah; jangan membalik atau menyamakan maknanya.
- [T38](../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) adalah hasil kamera OP3 retrospektif pada 200 frame berobjek + 60 negatif; 50 frame parsial terpisah. Gunakan hasil apa adanya, termasuk recall per kelas dan false positive pada frame negatif bila membahasnya. Jangan menyatakan frekuensi kotak live sebagai akurasi.
- Jelaskan definisi metrik secara tepat: TEST/T42 menggunakan F1 yang dihitung dari precision dan recall makro; T38 menggunakan rerata F1 per kelas. Sebut threshold, IoU, ukuran sampel, model/seed dan satuan saat menampilkan hasil.
- T36/T37 berisi 24 run aktif, empat model × dua kondisi × tiga ulangan. Laporkan latensi, FPS, CPU dan RAM sesuai sumber: CPU dan RSS adalah ukuran **proses detektor**. FPS efektif tidak otomatis sama dengan `1000 / latensi`; bedakan durasi sesi TEST multi-model dari waktu pengujian per model. Uraikan keterbatasan yang berpengaruh sesuai bukti, tanpa menyisipkan percakapan pribadi peneliti.
- T42 membandingkan dua teacher yang dilatih ulang dan enam student pada VAL. Audit server dilaporkan lulus. T42 bukan evaluasi TEST/kamera, tidak otomatis mengganti teacher utama, dan tiga seed student bukan bukti signifikansi kuat. Jangan menyamakan metode pencatatan puncak GPU teacher dan student jika berbeda.
- Gunakan grafik yang sesuai dengan jenis data; jika menampilkan detail yang skalanya diperbesar, pertahankan penanda skala. Identifikasi model, kondisi, run, sumber dan konteks setiap screenshot/video. Screenshot satu frame bukan bukti gerakan gait atau akurasi seluruh sesi.

## Sitasi dan format

Gunakan sumber primer yang dapat diperiksa: PDF artikel, dokumentasi resmi atau sumber penelitian yang benar-benar tersedia. Verifikasi penulis, tahun, judul, halaman/persamaan/tabel dan DOI bila tercantum. Periksa konsistensi setiap kutipan dengan daftar referensi. Jangan mengarang atau menyimpulkan isi artikel hanya dari judul. Untuk sumber yang tidak dapat diakses gunakan `[BUTUH SUMBER: ...]`; untuk keputusan atau data yang tidak tercatat gunakan `[PERLU KONFIRMASI: ...]`.

Ikuti pedoman, template, bahasa baku, format sitasi, margin, heading, caption, tabel, gambar, penomoran dan aturan daftar pustaka yang benar-benar ditemukan. Jika format atau sumber belum tersedia, jelaskan bagian yang perlu dilengkapi. Jangan mengubah file asli yang sedang dibuka atau menghapus perubahan peneliti.

## Keluaran yang harus dibuat

Buat folder baru dan unik, misalnya `laporan_skripsi_draf_<tanggal>/`, lalu simpan:

1. Draf lengkap yang dapat dibaca: bagian awal, Bab I sampai bab penutup sesuai pedoman yang terverifikasi, daftar referensi dan lampiran. Minimal sediakan Markdown; jika template `.docx` dan alat yang sesuai tersedia, buat **salinan DOCX baru** mengikuti style template. Jangan menimpa file asli. Jika alat render tersedia, render dan periksa hasil DOCX; bila tidak, jelaskan batas pemeriksaan.
2. `MATRIKS_RUMUSAN_MASALAH.csv`: setiap pertanyaan, tujuan, metode, sumber data, tabel/grafik, letak jawaban di naskah, status dan hal yang belum terverifikasi.
3. `DAFTAR_SUMBER_DAN_VERIFIKASI.csv`: seluruh klaim angka dan pustaka beserta file/halaman/tabel, cara verifikasi dan status.
4. `DAFTAR_TABEL_GAMBAR_LAMPIRAN.md`: nomor sementara, judul, file sumber dan penjelasan. Gunakan gambar beresolusi memadai yang memang tersedia; jangan menyatakan file lokal tersedia di GitHub tanpa memeriksa.
5. `LAPORAN_PERUBAHAN_DAN_CELAH.md`: bagian yang diperbaiki, sumber yang belum tersedia, penanda yang masih tersisa, batas klaim, dan hal yang memerlukan arahan pembimbing. Jangan memasukkan percakapan pribadi atau mengarang persetujuan.

Periksa bahwa semua bab yang diperlukan benar-benar berisi naskah, setiap rumusan masalah terjawab sesuai bukti, angka cocok sumber, seluruh rujukan dapat ditelusuri, dan tabel/gambar dapat dibuka. Laporkan lokasi semua keluaran, status DOCX bila dibuat, serta pekerjaan yang benar-benar masih memerlukan peneliti. Jangan melakukan commit/push atau menjalankan eksperimen tambahan kecuali diminta pada sesi pelaksanaan.
