# Status Audit Lab/Server — 22 Oktober 2026

## Tujuan

Mencatat pekerjaan yang bisa diselesaikan di lab/server sebelum robot OP3 siap, serta memisahkan fakta yang sudah diverifikasi dari pekerjaan yang masih memerlukan lingkungan atau perangkat tambahan. Audit ini bersifat read-only terhadap dataset, checkpoint, dan proyek sumber.

## Ringkasan status

| Area | Status | Temuan utama |
| --- | --- | --- |
| Integritas dataset Roboflow | Selesai diverifikasi | 4.600/1.213/592 gambar train/val/test; pasangan label lengkap; tidak ada label invalid atau orphan. |
| Pemisahan sumber/adegan | Ada risiko, belum dapat dibersihkan dengan metadata yang ada | Irisan nama dasar lintas split berjumlah 326 train–val, 176 train–test, dan 155 val–test. Ini bukan bukti duplikasi persis, tetapi split tidak membuktikan pemisahan sesi/adegan. |
| Asal teacher | Ditelusuri sebagian; belum terverifikasi byte-level | Checkpoint dan run tercatat, tetapi `dataset_version` teacher `null` dan YAML/path training lama sudah tidak tersedia. |
| Training yang sudah menjadi eksperimen utama | Selesai dan artefaknya tersedia | Pure KD, supervised, dan KD Hybrid full tiga seed telah dilatih; checkpoint terdaftar dan hash diperiksa. |
| Preflight training ulang | Berhasil melalui akses host | Environment eksperimen dapat mengimpor Ultralytics; PyTorch melihat tiga L40. GPU saat diperiksa sedang dipakai proses lain. |
| Evaluasi pada robot OP3 | Sudah ada hasil eksploratif; uji Hybrid lanjutan menunggu robot | Log live dan evaluasi 260 frame KD murni tersedia, tetapi belum menjadi evaluasi akhir yang bebas bias. Hybrid seed 1337 belum diuji pada OP3. |

## Audit dataset

Dataset yang diperiksa adalah export Roboflow `humanoid-atom/advance_vision_human`, versi yang metadata export-nya menyebut `v1 V1-Base`.

| Split | Gambar | Anotasi | Ball | Gawang | Robot | Background |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 4.600 | 6.143 | 881 | 3.662 | 1.600 | 4 |
| Val | 1.213 | 1.525 | 182 | 1.048 | 295 | 2 |
| Test | 592 | 734 | 83 | 532 | 119 | 1 |

Pemeriksaan label lulus: setiap gambar memiliki pasangan label, tidak ada label orphan, tidak ada baris anotasi invalid, dan ketiga split terisi. Kelas `gawang` mendominasi, sedangkan jumlah objek test `ball` (83) dan `robot` (119) relatif kecil.

Kesamaan nama dasar dihitung dengan menghapus suffix Roboflow `.rf.<hash>`. Hitungan tersebut menunjukkan nama sumber yang berulang, bukan jumlah duplikat persis. Pemeriksaan RGB atas pasangan nama dasar yang sama sebelumnya tidak menemukan berkas identik. Bukti yang tersedia tidak cukup untuk mengelompokkan seluruh gambar berdasarkan video/sesi/adegan. Karena itu hasil split saat ini hanya mendukung klaim evaluasi pada split resmi level-gambar; jangan klaim bahwa TEST berasal dari adegan baru.

Rincian, riwayat penggunaan TEST, dan rekomendasi protokol tercatat di [`AUDIT_DATASET_SKRIPSI.md`](../AUDIT_DATASET_SKRIPSI.md). Dataset fingerprint tersimpan di `artifacts/advance_vision_dataset_fingerprint.json`.

## Provenance teacher

Checkpoint teacher yang dipakai adalah:

`/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`

SHA-256 yang tercatat: `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`.

Manifest dan log run mencatat model awal `yolo11n.pt`, kelas `ball/gawang/robot`, 100 epoch, seed 42, ukuran 640, batch 16, optimizer AdamW, Ultralytics 8.4.130, PyTorch 2.4.1+cu121, dan GPU L40. Log menunjukkan 4.600 gambar train dan 1.213 gambar val, sesuai jumlah pada export v1 yang kini tersedia.

Namun, bukti ini belum membuktikan identitas byte dataset teacher:

- Manifest teacher menyimpan `dataset_version: null`.
- YAML dan direktori data yang ditunjuk saat training berada di path proyek `skripsi` yang kini tidak ada.
- Dataset v1 yang ada dan jumlah gambarnya konsisten dengan log teacher, tetapi konsistensi jumlah tidak membuktikan bahwa semua file sama.
- TEST pernah dibuka untuk evaluasi model lama, dan kemudian dipakai lagi untuk evaluasi KD Hybrid. TEST bukan holdout yang belum pernah dilihat sepanjang riwayat penelitian. Catatan keputusan ini sudah dijelaskan di `docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md`.

Kesimpulan: teacher dapat diidentifikasi dan checkpoint-nya terikat hash, tetapi provenance dataset training belum bersih. Untuk klaim provenance yang kuat atau split berbasis grup baru, perlu retraining teacher dan seluruh student dari snapshot dataset yang dikunci.

## Kesiapan komputasi training

Pemeriksaan ulang runtime pada 22 Oktober 2026:

- Pemeriksaan dalam sandbox workspace tidak melihat `/dev/nvidia*`, sehingga `nvidia-smi` gagal di konteks tersebut. Pemeriksaan host dengan akses yang disetujui berhasil: NVIDIA driver `535.261.03`, tiga NVIDIA L40, CUDA driver 12.2.
- Environment training yang dibekukan berhasil diverifikasi: Python 3.11.2, PyTorch `2.4.1+cu121`, Ultralytics `8.4.130`, NumPy `1.26.4`, dan OpenCV `4.10.0`. Dari environment itu `torch.cuda.is_available()` bernilai `True`, tiga L40 terdeteksi, dan `scripts/train_kd.py --help` berhasil.
- Interpreter system Python dengan PyTorch `2.13.0+cu130` memang melaporkan driver terlalu lama, tetapi itu bukan environment penelitian yang dikunci. Jangan gunakan interpreter itu untuk run skripsi.
- Saat diperiksa, GPU 0 memakai 4.749 MiB dan utilisasi 39%; GPU 1 memakai 26.276 MiB dan utilisasi 100%; GPU 2 memakai 8.102 MiB dan utilisasi 99%. Ada beberapa proses training/inferensi aktif di server.

Semua checkpoint model yang tercantum di `configs/model_registry.yaml` (teacher, tiga pure KD, tiga supervised, dan tiga Hybrid full) ditemukan dan SHA-256-nya cocok dengan registry. Eksperimen pure KD, supervised, dan Hybrid full yang telah tercatat sudah selesai; tabel VAL/TEST dan benchmark L40 juga telah tersedia. Karena itu training utama tidak perlu diulang hanya untuk melanjutkan pekerjaan OP3. Tidak ada run baru diluncurkan karena tidak ada protokol eksperimen baru yang perlu dijalankan dan GPU sedang dipakai proses lain.

Jika diperlukan retraining untuk protokol baru, admin perlu meneruskan device NVIDIA dan library driver yang sesuai ke sesi/container ini, lalu memastikan `nvidia-smi` dan `torch.cuda.is_available()` berhasil dari environment Python 3.11.2 yang dikunci. Jangan mengubah atau menimpa checkpoint lama; setiap run baru harus memiliki direktori, config, log, dan manifest tersendiri.

## Yang sudah dikerjakan dan yang masih terbuka

1. **Dataset dan split:** audit integritas selesai. Audit ini tidak menghapus gambar atau mengganti split. Split group-held-out belum bisa dibangun secara sah tanpa metadata sumber yang dapat mengidentifikasi grup video/sesi.
2. **Teacher:** checkpoint, hash, log training, konfigurasi, dan keterbatasan dataset version ditelusuri. Identitas byte dataset training belum dapat dipastikan.
3. **Eksperimen/model:** training utama pure KD, supervised, dan Hybrid full tiga seed sudah selesai; checkpoint dan hash lolos verifikasi. Training ulang hanya diperlukan jika protokol berubah. Jika dibuat split group-held-out baru, retrain teacher serta baseline/student yang dibandingkan dari snapshot baru; pemilihan model dilakukan di VAL. Karena TEST resmi sudah pernah digunakan, jelaskan riwayatnya dan jangan menyebutnya untouched holdout.
4. **OP3:** sudah ada log runtime dan evaluasi kamera eksploratif KD murni (T27, 260 frame utama), tetapi data/label dan kondisi uji memiliki keterbatasan yang didokumentasikan di indeks OP3. Sesuai status terbaru pengguna, robot belum siap untuk sesi berikutnya. Hybrid seed 1337 belum diuji pada OP3. Setelah robot siap, kumpulkan frame dengan label final independen dari prediksi, lalu catat kondisi servo idle/berjalan, konfigurasi perangkat keras, latensi, FPS, CPU, dan RAM. Pastikan kondisi berjalan dapat diverifikasi, bukan hanya input operator.

## Langkah lab/server berikutnya

1. Training utama dan tabel lab/server sudah tersedia; tidak perlu menjalankan training ulang untuk memakai kandidat Hybrid seed 1337 pada uji robot.
2. Keputusan pengguna: pilih Jalur Pertama. Pertahankan eksperimen sekarang, laporkan batas split/provenance dan riwayat TEST secara eksplisit, tanpa retraining pada split yang sama.
3. Siapkan evaluasi OP3 eksternal pada sesi/frame baru yang belum dipakai untuk pemilihan model/threshold. Bekukan checkpoint dan konfigurasi lebih dahulu; anotasi frame secara independen dari prediksi; evaluasi Hybrid seed 1337 dan supervised seed 1337 pada frame/label identik. Uji ini menambah bukti pada domain robot, tetapi tidak membuat TEST Advance Vision menjadi holdout baru dan tidak membuktikan ulang provenance teacher.
4. Metadata saat ini tetap belum cukup untuk membuat pemisahan adegan group-held-out yang bertanggung jawab. Jika pembimbing nanti mensyaratkan itu, perlu dataset/protokol baru dan retraining; jangan menggunakan TEST yang sudah dibuka untuk tuning. Uji OP3 menunggu robot siap.

Tidak ada file dataset, label, maupun checkpoint model yang diubah dalam audit ini.
