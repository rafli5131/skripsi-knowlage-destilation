# Memori proyek — 22 Oktober 2026: audit lab/server dan status menuju OP3

Catatan ini merekam pekerjaan setelah pengguna meminta pekerjaan yang bisa dilakukan di lab/server diselesaikan karena robot belum siap. Rincian audit dataset/provenance ada di [`docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md`](../docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md). Gunakan manifest/checkpoint/tabel sebagai sumber angka utama.

## Pekerjaan yang dilakukan

- Audit ulang dataset Advance Vision v1: train/val/test memiliki 4.600/1.213/592 gambar; 6.143/1.525/734 anotasi. Semua gambar berpasangan dengan label, tidak ada label orphan atau baris anotasi invalid.
- Normalisasi nama sumber menemukan 326 irisan train–val, 176 train–test, dan 155 val–test. Ini bukan hitungan duplikat piksel. Metadata belum cukup untuk menjamin pemisahan video/sesi/adegan; klaim harus dibatasi ke split resmi level-gambar.
- Teacher FP32 `best.pt` SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` berhasil ditelusuri ke manifest, konfigurasi, dan log. Teacher mencatat `dataset_version: null`; path YAML/data lama sudah tidak ada. Jumlah gambar pada log cocok dengan export v1 sekarang, tetapi itu tidak membuktikan identitas byte dataset.
- Semua sepuluh checkpoint pada `configs/model_registry.yaml` (teacher; tiga Pure KD; tiga supervised; tiga Hybrid full) ditemukan dan SHA-256 cocok dengan registry.
- Environment training dikonfirmasi lewat `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv`: Python 3.11.2, PyTorch 2.4.1+cu121, Ultralytics 8.4.130, NumPy 1.26.4, OpenCV 4.10.0. `scripts/train_kd.py --help` berhasil.
- Sandbox workspace tidak memiliki `/dev/nvidia*`; tetapi pemeriksaan host dengan akses yang disetujui menunjukkan driver NVIDIA 535.261.03, tiga L40, dan `torch.cuda.is_available() == True` pada environment terkunci. Pada snapshot 22 Oktober sekitar 20:09 WIB, GPU 0 memakai 4.749 MiB/39%, GPU 1 26.276 MiB/100%, GPU 2 8.102 MiB/99%; proses lain sedang aktif.
- Tidak ada training baru dijalankan. Eksperimen Pure KD, supervised, Hybrid full tiga seed, evaluasi, dan tabel server sudah tersedia. Tidak ada protokol baru yang mengharuskan run tambahan, dan TEST resmi sudah pernah dibuka.

## Hasil model dan batas metodologi

- Kandidat OP3 untuk uji berikutnya adalah Hybrid full seed 1337, dipilih berdasarkan VAL sebelum melihat TEST Hybrid. Checkpoint `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt`, hash `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363`.
- Alias `op3_default` masih menunjuk Pure KD seed 42. Checkpoint robot belum diganti otomatis.
- Hasil TEST lanjutan Hybrid: mAP50–95 Hybrid 0,7469 ± 0,0022 vs supervised 0,7225 ± 0,0035; F1 makro @0,25 0,9071 ± 0,0017 vs 0,9121 ± 0,0026. Laporkan kedua arah hasil. TEST bukan holdout bersih yang belum pernah dipakai; riwayat evaluasi teacher/Pure KD mendahului Hybrid.
- Split group-held-out yang sah belum bisa dibuat dari metadata saat ini. Bila dibuat split/teacher baru, hasil yang sekarang menjadi pembanding historis dan seluruh model pembanding harus dilatih ulang dengan split terkunci. Jangan gunakan TEST yang sudah dibuka untuk tuning.

## Kondisi OP3 dan langkah berikutnya

- Pengguna terakhir menyatakan robot belum siap untuk sesi uji berikutnya. Jangan memulai sesi perangkat atau mengasumsikan servo/kondisi robot aktif.
- Sudah ada artefak uji OP3 terdahulu: log live Pure KD, benchmark servo-idle, dan evaluasi kamera eksploratif T27 dengan 260 frame utama. Evaluasi T27 masih terbatas dan label berawal dari draf prediksi KD; jangan menyebut tidak pernah ada pengujian OP3, tetapi jangan anggap T27 sebagai evaluasi kamera final bebas bias.
- Hybrid seed 1337 belum diuji pada OP3. Setelah robot siap, ikuti `prompt/PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3_V2.md`: verifikasi checkout/hash/topic/runtime, lakukan sesi live/capture, ambil frame mentah, human-review semua label sebelum metrik akurasi, pisahkan servo-idle dan walking, serta lakukan benchmark runtime bersih tanpa preview/capture.
- Jangan mengirim perintah servo/gait/motor. Jangan unggah frame, video, label, atau log robot tanpa permintaan eksplisit.

## Keputusan pengguna: Jalur Pertama

- Pengguna memilih mempertahankan hasil eksperimen sekarang, menuliskan batas metodologi secara transparan, dan tidak melatih ulang pada split resmi yang TEST-nya sudah pernah digunakan.
- Setelah robot siap, lakukan evaluasi eksternal OP3 pada sesi/frame baru yang belum dipakai untuk seleksi model/threshold. Bekukan checkpoint/config sebelum capture, anotasi secara independen dari prediksi, lalu evaluasi Hybrid seed 1337 dan supervised seed 1337 pada frame serta label yang sama. Laporkan kedua model; jangan memilih ulang model dari metrik OP3 test.
- Uji OP3 baru memperluas bukti ke domain robot, tetapi tidak mengubah status TEST Advance Vision menjadi holdout bersih dan tidak memperbaiki provenance teacher yang tak tercatat. Keterbatasan itu tetap dijelaskan di Bab Metode/Hasil.

## Perubahan repo pada giliran ini

- Membuat audit lokal `docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md` dan memperjelas bahwa artefak OP3 lama ada, sedangkan uji Hybrid berikutnya menunggu robot.
- Membuat panduan proyek `agent.md` serta entrypoint standar `AGENTS.md` yang menunjuk ke panduan tersebut. Sebelum perubahan berikutnya, baca file agent dan memory terbaru.
- Mencatat pilihan Jalur Pertama di `docs/DECISIONS.md`, audit server, memory, dan panduan agent.
- File memory/audit belum di-commit atau di-push. Tidak ada dataset, label, atau checkpoint yang diubah.
