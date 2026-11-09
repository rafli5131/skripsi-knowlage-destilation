# Prompt audit celah skripsi Knowledge Distillation dan ROBOTIS OP3

Gunakan prompt ini untuk memeriksa kelengkapan penelitian dan kesiapan naskah secara teliti. Hasil audit adalah dokumen kerja peneliti, bukan isi skripsi secara otomatis.

---

## Peran dan tugas

Anda adalah auditor penelitian dan penulisan akademik. Audit secara menyeluruh skripsi tentang penerapan **Knowledge Distillation (KD)** pada deteksi objek YOLO11 skala t kustom berbasis ROS 2 di ROBOTIS OP3. Temukan kekurangan teknis, kesalahan angka, ketidaksesuaian naskah dengan bukti, celah penjelasan, ketidaksesuaian format, referensi yang tidak dapat diverifikasi, dan berkas yang belum tersinkron.

Kerjakan secara mandiri sampai audit lengkap dalam lingkup sumber yang tersedia. Jangan mengarang informasi, mengasumsikan cek lulus, atau menyatakan penelitian bebas dari seluruh kesalahan. Bedakan fakta yang diperiksa, informasi yang hanya dilaporkan sumber lain, asumsi yang belum dibuktikan, serta data yang tidak tersedia. Jangan menyalakan kamera, robot, servo atau gait; jangan menjalankan ulang training atau mengubah checkpoint hanya untuk melakukan audit.

## Batasan penelitian

- Kelas target adalah `ball`, `gawang`, dan `robot`. Student adalah YOLO11 skala **t kustom**, bukan YOLO11n standar; teacher utama adalah YOLO11n. Supervised memiliki arsitektur student yang sama.
- Pure KD dan KD Hybrid full adalah objective yang berbeda. Hybrid full menggabungkan loss deteksi berlabel dengan distilasi; jangan menyebutnya pure teacher-only. Hybrid full seed 1337 merupakan kandidat utama OP3 yang tercatat; perubahan model hanya berdasarkan keputusan baru yang terverifikasi.
- Objek target dalam cakupan skripsi ditempatkan **statis** sesuai klarifikasi peneliti; robot tetap dapat diuji dalam kondisi diam dan berjalan sebagaimana rumusan masalah. Uji tracking terdahulu adalah percobaan tambahan, bukan rumusan masalah, syarat utama, atau klaim keberhasilan kontrol kepala. Jangan meminta uji tracking tambahan hanya untuk melengkapi skripsi.
- Evaluasi online di luar lingkup yang diminta peneliti tidak perlu dimasukkan. Ini **tidak menghapus** pengukuran real-time OP3: latensi, FPS, CPU, dan RAM saat robot diam dan berjalan tetap menjawab rumusan masalah.
- Keputusan atau percakapan pribadi peneliti yang ditandai agar tidak dimasukkan ke skripsi tidak boleh disalin ke naskah. Jangan mengubah ketidakpastian menjadi fakta; jika kondisi identik tidak terbukti, jangan menyatakannya sebagai hasil pengukuran.

## Sumber dan aturan prioritas

1. Temukan versi naskah asli/terkini, judul, rumusan masalah, batasan masalah, pedoman serta template kampus di mesin tempat prompt dijalankan. Dokumen yang paling baru belum tentu disetujui: cek identitasnya dan catat versi/hash. Jangan menimpa berkas milik peneliti.
2. Baca `AGENTS.md`, `agent.md`, `configs/model_registry.yaml`, `configs/analysis.yaml`, `docs/DECISIONS.md`, `AUDIT_DATASET_SKRIPSI.md`, serta memory terbaru. Status lama yang bertentangan dengan manifest atau sumber hasil terbaru harus ditandai sebagai historis, bukan dianggap fakta terkini.
3. Baca tabel berikut beserta CSV/manifest/JSON sumber bila tersedia: `T05`, `T06`, `T30`, `T31`, `T35`, `T36`, `T37`, `T38`, dan `T42` di `analisis_performa/tabel/`. Baca juga `audit_teacher_t42_LTOW7Xw5.json` dan `dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md`.
4. Periksa `dokumentasi/2026-11-05/percobaan-37-evaluasi-t38-empat-model/`, `dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/`, serta dokumentasi tracking lama **hanya jika** diperlukan menjelaskan lingkup atau status data. Tinjau sumber visual, label, sumbu dan keterangannya.
5. Bila ada, baca `dokumentasi/2026-11-09/AUDIT_INTEGRITAS_HASIL.md`, `MATRIKS_BUKTI_DAN_CELAH.md`, `DRAF_BAB_IV_V_TERPADU_T38_T42.md`, dan memory terbaru. Ketiga dokumen 9 November tersebut dapat hanya berada di mesin OP3 dan belum tentu tersedia di checkout GitHub. Jangan menganggap tidak adanya salinan lokal sebagai bukti eksperimen tidak pernah dilakukan; catat batas verifikasi.
6. Bila tersedia, periksa `PanduanSkripsiFilkom-v3.0.pdf`, `Template/Template-Skripsi-v3.0.docx`, `Template/Template-ProposalSkripsi-v3.0.docx`, naskah proposal/skripsi asli, folder `Paper/`, dan folder ejaan. Lokasi historis antara lain `E:\Kuliah\Thesis` atau `/media/bhrew/DATA1/Kuliah/Thesis`; cari lokasi aktual secara aman. Struktur implementatif-pengembangan tujuh bab tercatat pada prompt lama, tetapi verifikasi langsung pada pedoman yang benar sebelum menjadikannya aturan final.

## Pemeriksaan wajib

### A. Keterlacakan rumusan masalah

Bangun matriks yang memasangkan setiap rumusan masalah dengan metode, data, metrik, tabel/grafik, kesimpulan, dan sumber. Setidaknya periksa kebutuhan/perancangan/implementasi/uji ROS 2; perbandingan mAP model KD, supervised, dan teacher; precision/recall/F1; latensi dan FPS real-time pada kondisi diam/berjalan; serta CPU/RAM onboard. Cocokkan redaksi dan jumlah pertanyaan dengan naskah peneliti yang paling berwenang. Jika redaksinya berbeda, tampilkan perbedaan tanpa diam-diam mengubahnya.

### B. Akurasi dan model

- Verifikasi identitas checkpoint dan seed, cakupan split, kelas, confidence, NMS, IoU, perangkat, rumus F1, per kelas dan per model. Bedakan hasil TEST dataset, T38 kamera OP3 retrospektif, dan T42 ablasi VAL; jangan mencampurkan angka atau mengklaim semuanya pengujian yang sama.
- Periksa perbedaan F1 pada TEST/T42 (dari precision dan recall makro) dengan T38 (rerata F1 per kelas). Bandingkan hasil T38 dengan hasil mentah jika tersedia; jelaskan bahwa jumlah kotak live atau confidence bukan akurasi.
- Periksa bahwa hasil pada 260 frame T38 meliputi 200 frame berobjek dan 60 negatif; 50 frame parsial terpisah. Tinjau hasil per kelas dan false positive untuk memastikan angka yang kurang baik tidak disembunyikan. Label telah ditinjau manusia setelah pra-label; periksa bukti log jika tersedia.
- Periksa kronologi pemakaian TEST dan provenance teacher utama lama. Teacher n dan s yang dilatih ulang untuk T42 bukan teacher utama OP3. Jangan mengklaim T42 sebagai TEST, hasil kamera OP3, atau otomatis mengganti model utama.

### C. Runtime dan biaya

- Verifikasi 24 run aktif: empat model × dua kondisi × tiga ulangan; rujuk T36, T37, peta run aktif, log dan audit telemetry. Cocokkan setiap agregat, timestamp, warm-up, durasi, metadata, hash dan run yang diganti sejauh datanya tersedia.
- Bedakan latensi, FPS efektif, waktu training, waktu seluruh sesi TEST, dan benchmark server. CPU dalam T36/T37 adalah penggunaan proses; jelaskan normalisasi CPU dan bahwa RSS bukan total RAM sistem. Jangan menyatakan nilai sistem keseluruhan jika tidak diukur.
- Verifikasi apa yang didukung log/telemetry tentang gait, arah kepala dan kondisi robot. Jangan mengonversi asumsi menjadi kepastian atau menjadikan tangkapan gambar setelah jendela sebagai bukti gerakan kontinu.

### D. Reproduksibilitas, naskah, dan media

- Periksa fingerprint, hash file sumber, model, versi environment, script, konfigurasi, seed, dan ketersediaan data; bedakan pemeriksaan byte TRAIN/VAL yang dicatat saat preflight dari audit teacher terbaru yang tidak menghitung ulang seluruh byte dataset.
- Audit grafik: apakah setiap angka cocok sumber, skala terpotong ditandai, satuan jelas, resolusi memadai, label tidak tertutup, dan definisi metrik tepat. Periksa screenshot dan video: model, waktu, kondisi, durasi, apakah berasal dari preview/rekaman dan apakah mewakili klaim yang dibuat.
- Telusuri seluruh sitasi sampai sumber primer yang benar-benar tersedia; cocokkan penulis/tahun/DOI/halaman, nomor persamaan dan daftar pustaka. Jangan mengarang referensi, fakta bibliografi, hasil literatur atau persetujuan pembimbing.
- Audit kesesuaian judul, lima rumusan masalah, tujuan, metode, desain, hasil, kesimpulan, abstrak, daftar tabel/gambar, nomor halaman, lampiran, terminologi, dan format kampus. Deteksi struktur Bab IV–V historis versus kemungkinan format skripsi tujuh bab, lalu selaraskan dengan pedoman yang benar.
- Periksa status Git: mana yang ada pada commit/remote, mana yang hanya lokal atau diabaikan, apakah dokumen terbaru dan sumber mentah dapat diakses, dan apakah cadangan terpisah terverifikasi. Jangan push data, video, label, log, atau checkpoint privat tanpa instruksi yang sesuai.

## Bentuk keluaran

Buat folder baru `dokumentasi/<tanggal>/audit-celah-skripsi/` atau nama unik bila sudah ada. Simpan:

1. `LAPORAN_AUDIT.md`: temuan berprioritas **kritis / penting / editorial**, dampak terhadap klaim, bukti spesifik dengan path/tabel/halaman dan status `terverifikasi`, `hanya dilaporkan`, `tidak tersedia`, atau `belum diperiksa`.
2. `MATRIKS_RUMUSAN_MASALAH.csv`: rumusan masalah → metode → data → metrik → sumber → hasil → status → tindakan.
3. `DAFTAR_TINDAKAN.md`: tindakan yang dapat dikerjakan segera, yang memerlukan sumber/akses, dan yang memerlukan keputusan pembimbing; bedakan pengujian tambahan opsional dari kebutuhan yang benar-benar belum terjawab.
4. `AUDIT_SITASI_DAN_GAMBAR.csv`: klaim/elemen, sumber, lokasi, hasil pemeriksaan dan status.

Cantumkan tanggal, commit, file lokal/tidak terlacak yang digunakan dan keterbatasan audit. Jangan menambahkan percakapan pribadi ke naskah. Laporkan hasil audit, celah yang masih nyata, tindakan yang telah dilakukan, dan langkah berikutnya tanpa menyebut `sudah bebas celah` bila belum ada buktinya.
