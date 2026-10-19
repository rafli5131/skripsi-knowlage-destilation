# Hasil inferensi kamera OP3

## Status terbaru kode deteksi dan tracking

Pada 19 Oktober 2026, jalur node ROS diperbarui untuk menjalankan deteksi kelas `ball`, `gawang`, dan `robot`, lalu meneruskan ID BoT-SORT per objek ke pesan ROS dan CSV. Uji offline memakai satu citra VAL per kelas berhasil mendeteksi kelas yang sesuai dan mempertahankan ID pada frame statis berulang setelah track terkonfirmasi. Rincian dan hash input tersedia di [`../artifacts/op3_tracking_offline_smoke_20261019.json`](../artifacts/op3_tracking_offline_smoke_20261019.json). Ini belum merupakan uji kamera OP3. Ketiga log kamera di bawah dibuat sebelum tracking ditambahkan; log tersebut tidak memiliki ID lintas frame, dan kondisi berjalan belum diuji secara terkendali.

Lihat [indeks percobaan berdasarkan tanggal](INDEKS.md) untuk laporan per run dan grafiknya.

Dokumentasi ini merangkum satu sesi inferensi kamera yang benar-benar dijalankan. Grafik menunjukkan performa dan aliran frame. Satu frame beranotasi disertakan sebagai contoh visual; video dan frame mentah tidak disimpan.

## Ringkasan sesi

| Item | Nilai |
| --- | --- |
| Run ID | `20261019T083428Z` |
| Kondisi tercatat | `unknown` (label operator; tidak diukur otomatis) |
| Sumber label kondisi | Input operator; bukan telemetry gerak |
| Waktu mulai (UTC) | `2026-10-19T08:34:28.413982+00:00` |
| Waktu berhenti (UTC) | `2026-10-19T08:35:05.674559+00:00` |
| Durasi | 37.3 detik |
| Kamera/sumber | Logitech HD Pro Webcam C920, `/dev/video0`, ROS topic `/thesis/image_raw` |
| Mode capture | 640×480, YUYV dikonversi `yuyv2rgb`, 30 FPS diminta |
| Frame diproses | 512 |
| FPS rata-rata sesi | 13.74 |
| Error pemrosesan frame | 0 |
| Checkpoint | `kd_student_best.pt` (SHA-256 `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3`) |
| Runtime | Python 3.12.3, PyTorch 2.4.1+cpu, Ultralytics 8.4.130, CPU FP32 |
| Input model | 640×640, batch 1 |
| Threshold runtime | confidence 0.25, IoU NMS 0.45 |
| Preview | Mati; tidak menyimpan gambar/video |
| Topic output | `/vision/detections` (`vision_msgs/Detection2DArray`) |
| Mapping kelas | 0: ball, 1: gawang, 2: robot |

Log frame menunjukkan total **0 instance deteksi** yang dikeluarkan selama 512 frame. CSV hanya merekam jumlah deteksi per frame. Gambar beranotasi di bawah adalah contoh kamera terpisah dari sesi sebelumnya; timestamp, kelas, confidence, dan koordinatnya tercatat di JSON pendamping. Contoh tunggal ini dan jumlah deteksi bukan ukuran akurasi, precision, atau recall karena tidak ada frame berlabel dan ground truth.

![Contoh hasil deteksi pada satu frame kamera](figures/contoh_deteksi_kamera.png)

Detail bbox dan confidence untuk contoh frame: [`contoh_deteksi_kamera.json`](contoh_deteksi_kamera.json).

## Performa

Latensi dihitung per frame dari CSV. P95 memakai persentil linear NumPy. End-to-end mencakup callback deteksi dan publish ROS; preview mati.

| Tahap | Median (ms) | P95 (ms) | Rata-rata (ms) | Unit |
| --- | ---: | ---: | ---: | --- |
| Preprocess | 1.18 | 1.53 | 1.18 | ms |
| Inference | 25.21 | 27.66 | 24.76 | ms |
| Postprocess/NMS | 0.51 | 0.56 | 0.45 | ms |
| End-to-end | 27.89 | 30.27 | 28.24 | ms |

![Median dan p95 latensi per tahap](figures/latensi_tahap.png)

![Latensi end-to-end sepanjang sesi](figures/latensi_per_frame.png)

CPU proses: median 761.7% dan p95 818.5%. psutil menghitung 100% sebagai satu logical CPU, sehingga nilai dapat melampaui 100% ketika beberapa thread bekerja bersamaan. RSS proses: median 354.9 MiB dan p95 359.5 MiB.

![Penggunaan CPU dan RAM proses](figures/cpu_ram_proses.png)

## Aliran frame dan batas hasil

Di antara timestamp capture berurutan, terdapat 3 jeda lebih dari 1 detik dan 0 jeda lebih dari 5 detik; jeda maksimum 2.00 detik. Pengamatan ini sejalan dengan peringatan kamera terputus sementara pada log node. FPS sesi karenanya menggambarkan stream yang benar-benar diterima selama sesi ini, bukan kemampuan maksimum model atau kamera dalam kondisi lain.

![Selang timestamp capture antar-frame](figures/jeda_frame.png)

Node ini adalah detektor objek (`ball`, `gawang`, `robot`), bukan pengenal aksi/gerakan; ia tidak menentukan apakah robot sedang berjalan. Label `experiment_condition` diisi operator dan bukan hasil telemetry gerak. Label `servo_idle` pada sesi lama tidak cocok dengan kondisi yang dilaporkan operator, sehingga kondisi fisik sesi tersebut tidak dapat dipastikan. Run ulang ini memakai `unknown`, menghasilkan 0 deteksi objek dalam 512 frame, dan tidak mengirim perintah servo/gait. Sesi walking terkontrol belum dilakukan.

Contoh PNG di atas dibuat untuk dokumentasi atas permintaan. Grafik performa dibuat dari CSV sesi benchmark yang preview-nya mati. CSV benchmark tidak menyimpan bounding box per kelas atau frame; detail bbox di JSON hanya berlaku untuk contoh tunggal. Evaluasi akurasi memerlukan frame berlabel dan ground truth.

## Artefak sumber

- Data mentah per frame: [`../runs/op3_pytorch/20261019T083428Z.csv`](../runs/op3_pytorch/20261019T083428Z.csv)
- Metadata konfigurasi dan status: [`../runs/op3_pytorch/20261019T083428Z.json`](../runs/op3_pytorch/20261019T083428Z.json)
- Script pembuat laporan dan grafik: [`../scripts/build_op3_session_documentation.py`](../scripts/build_op3_session_documentation.py)
