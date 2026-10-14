# Audit Dataset Skripsi: Advance Vision

## Ringkasan

Dataset Roboflow `humanoid-atom/advance_vision_human` memiliki tiga split yang benar-benar tersedia. Audit integritas label lulus; pemeriksaan tambahan menemukan risiko kesamaan sumber/adegan lintas split yang perlu dimasukkan ke protokol dan batasan skripsi.

## Sumber dan provenance

- Ringkasan datasheet di proyek sumber: [`docs/02_dataset.md`](/mnt/nas-hpg9/rafli5131/rafli/advance_vision/docs/02_dataset.md). Dokumen ringkasan itu masih mencatat versi sebagai `UNRESOLVED`; metadata README yang ikut diekspor lebih spesifik dan menyebut `v1 V1-Base`. Salinan README sumber/lisensi ada di [`datasheet/README.dataset.txt`](datasheet/README.dataset.txt) dan [`datasheet/README.roboflow.txt`](datasheet/README.roboflow.txt); hash dicatat di [`datasheet/README.md`](datasheet/README.md). Export bertanggal 31 Agustus 2026 mencatat 6.405 gambar, resize stretch 640×640, dan tanpa augmentasi.
- Normalisasi split: [`data.yaml`](/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/dataset/data.yaml).
- Pengunduh/normalizer: [`download_dataset.py`](/mnt/nas-hpg9/rafli5131/rafli/advance_vision/scripts/download_dataset.py). Script mengharuskan `ROBOFLOW_VERSION` dari environment dan memastikan train/valid/test tersedia.
- Metadata export secara eksplisit menyebut `advance_vision_human - v1 V1-Base`; salinan README tersebut cocok dengan SHA-256 yang dicatat di `datasheet/README.md`. Skrip unduh meminta `ROBOFLOW_VERSION` lalu memanggil `project.version(version_id)`, sehingga versi numerik untuk unduh ulang adalah `1`. Untuk eksperimen ini identitas byte yang otoritatif tetap fingerprint SHA-256 per gambar/label. YAML canonical memiliki `path` lama (`/mnt/nas-hpg9/rafli5131/rafli/skripsi/data/raw/...`), tetapi entri split absolut menunjuk direktori `advance_vision/data/raw/...` yang memang ada dan dipakai evaluator.
- Snapshot `args.yaml` milik run teacher FP32 lama menunjuk `/mnt/nas-hpg9/rafli5131/rafli/skripsi/data/dataset/data.yaml`, tetapi berkas tersebut tidak ada pada filesystem saat audit sekarang. Manifest teacher menyimpan nama project Roboflow dan parameter training, tetapi `dataset_version` bernilai `null`; karena itu kesamaan setiap byte TRAIN/VAL yang dipakai saat melatih teacher dengan fingerprint skripsi sekarang tidak dapat diverifikasi ulang. Checkpoint teacher sendiri terikat ke SHA-256 dan evaluasi TEST historisnya terikat ke path/hash checkpoint serta split yang ter-resolve. Catat ini sebagai keterbatasan provenance teacher. Jika pembimbing mensyaratkan bukti byte-level yang lengkap untuk teacher juga, retrain teacher dari snapshot terkunci dan ulangi semua student KD yang memakai teacher tersebut.

## Ukuran dan distribusi anotasi

| Split | Gambar | Anotasi objek | Ball | Gawang | Robot | Gambar background |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 4.600 | 6.143 | 881 | 3.662 | 1.600 | 4 |
| Val | 1.213 | 1.525 | 182 | 1.048 | 295 | 2 |
| Test | 592 | 734 | 83 | 532 | 119 | 1 |

`gawang` adalah kelas mayoritas di seluruh split (sekitar 59,6% objek train dan 72,5% objek test). Karena itu, skripsi perlu melaporkan metrik per kelas dan membahas jumlah objek test yang terbatas, khususnya `robot` (119 objek) dan `ball` (83 objek).

## Integritas label

Audit read-only diulang pada 8 Oktober 2026 dengan `scripts/audit_dataset.py --data /mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/dataset/data.yaml` dari repository sumber. Output kini mengunci distribusi kelas yang sebelumnya unresolved di datasheet: TRAIN 881/3.662/1.600 objek untuk ball/gawang/robot; VAL 182/1.048/295; TEST 83/532/119. Seluruh gambar memiliki berkas label pasangannya, tidak ada label orphan, tidak ada baris anotasi invalid, dan setiap split mempunyai gambar. Terdapat 4/2/1 label kosong yang dicatat sebagai background pada train/val/test. Script memeriksa irisan nama file lengkap antar-split; tidak ada peringatan overlap.

Dokumentasi sumber mencatat bahwa satu label TRAIN pernah diekspor sebagai polygon lalu dikonversi ke bounding box YOLO. Nama file dan kelas anomali tidak tersedia pada catatan, sehingga perubahan itu tidak dapat diaudit ulang hanya dari dokumentasi yang ada. Label saat ini lolos pemeriksaan sintaks/geometri.

## Pemeriksaan kebocoran atau kemiripan lintas split

Nama file Roboflow menyertakan suffix `.rf.<hash>`. Dengan membuang suffix itu, audit tambahan menemukan nama sumber bersama:

| Pasangan split | Nama sumber bersama |
| --- | ---: |
| Train–Val | 326 |
| Train–Test | 176 |
| Val–Test | 155 |

Jumlah ini adalah irisan nama dasar, bukan jumlah gambar yang pasti duplikat. Perbandingan piksel RGB pada pasangan yang punya nama dasar sama tidak menemukan pasangan identik. Pemeriksaan average-hash 8×8 adalah penyaring kasar, bukan bukti duplikasi; inspeksi visual sampel menunjukkan foto train/val yang sangat mirip dan frame train/test dengan arena serta gawang yang sama, tetapi posisi robot berubah. Contoh: `WIN_20240529_11_05_25_Pro_jpg` pada train/val dan `gawang00791_png` pada train/test.

Dengan demikian, split ini layak disebut **split resmi level-gambar** dan TEST historisnya tidak dipakai untuk training/tuning. Namun, belum ada bukti bahwa split memisahkan sesi, sumber video, atau adegan. Hindari klaim bahwa TEST mengukur generalisasi pada adegan baru. Jika klaim tersebut penting, bangun group-held-out split dari metadata sumber yang dapat diverifikasi dan latih ulang teacher serta semua student pada split itu.

## Riwayat penggunaan TEST

[`docs/08_final_test_evaluation.md`](/mnt/nas-hpg9/rafli5131/rafli/advance_vision/docs/08_final_test_evaluation.md) dan [`experiments/final_test/manifest.json`](/mnt/nas-hpg9/rafli5131/rafli/advance_vision/experiments/final_test/manifest.json) mencatat evaluasi akhir FP32 dan QAT pada 24 September 2026. Manifest menyatakan TEST tidak digunakan untuk training, range initialization, checkpoint selection, atau hyperparameter tuning. Jadi TEST sudah pernah dievaluasi untuk dua model lama; jangan lagi memperlakukannya sebagai split yang belum pernah dilihat. Untuk studi KD, kunci seluruh keputusan KD dan baseline pada VAL dahulu, lalu gunakan TEST hanya untuk evaluasi akhir yang tidak memicu perubahan model.

Preflight provenance teacher diulang 9 Oktober 2026: manifest training berstatus `completed`, class mapping cocok, args menunjukkan `val: true` dan `split: val`, serta SHA-256 checkpoint `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` cocok antara checkpoint yang dipakai dan artefak `weights/best.pt` pada run sumber. Manifest evaluasi historis berstatus `passed` dan menyatakan TEST hanya dipakai setelah seleksi model. Provenance versi dataset teacher tetap terbatas (`dataset_version: null`, YAML training lama menunjuk path yang kini tidak ada), sebagaimana dicatat di bagian provenance.

## Keputusan metodologis yang disarankan

Pada 9 Oktober 2026, peneliti memilih split Roboflow resmi sebagai protokol utama karena lebih hemat dan paling sebanding secara praktis dengan teacher dari proyek Advance Vision yang tersedia. Kesamaan byte TRAIN/VAL teacher dengan v1 tidak dapat diverifikasi karena manifest teacher tidak mencatat versi dataset (`dataset_version=null`) dan YAML training lamanya tidak tersedia. Kunci pure KD dan baseline supervised berdasarkan VAL, lalu evaluasi keduanya pada TEST tanpa tuning. Batasi kesimpulan pada generalisasi level-gambar dan laporkan kemiripan sumber/adegan serta keterbatasan provenance teacher; hasil ini tidak mendukung klaim generalisasi ke sesi atau adegan baru. Jika pembimbing meminta klaim tersebut, gunakan group-held-out split dan retrain teacher serta semua student agar tidak ada grup TEST yang pernah dilihat teacher.

Fingerprint SHA-256 per gambar dan label ada di [`artifacts/advance_vision_dataset_fingerprint.json`](artifacts/advance_vision_dataset_fingerprint.json), dibuat oleh [`scripts/fingerprint_yolo_dataset.py`](scripts/fingerprint_yolo_dataset.py). Fingerprint ini memudahkan verifikasi bahwa file data tidak berubah sepanjang eksperimen.
