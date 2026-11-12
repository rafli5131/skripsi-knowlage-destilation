# BAB 5 — PERANCANGAN DAN IMPLEMENTASI

## 5.1 Arsitektur sistem

```text
Kamera OP3 → topik citra ROS 2 → node deteksi PyTorch → topik deteksi
                                               ├── preview beranotasi
                                               └── log frame dan performa
```

Citra diterima sebagai `sensor_msgs/Image`, diproses dengan input 640 dan checkpoint yang dipilih, lalu hasil diterbitkan sebagai `vision_msgs/Detection2DArray`. Preview adalah keluaran beranotasi yang dapat ditampilkan melalui SSH-X; proses ini terpisah dari pengendalian motor. Rincian topik, parameter, pemeriksaan kelas, dan registry berada pada [dokumentasi runtime](../../OP3_PYTORCH_RUNTIME.md).

## 5.2 Implementasi model

Teacher adalah YOLO11n FP32. Student memakai arsitektur YOLO11 t kustom dan inisialisasi yang dicatat pada manifest. Kelompok supervised memakai label TRAIN; KD murni memakai objective teacher-only; Hybrid full menggabungkan label TRAIN dengan distilasi fitur, kotak dan kelas. Checkpoint Hybrid full seed 1337 dipilih berdasarkan VAL. Registry tetap memuat alias `op3_default` KD murni seed 42; pemakaian Hybrid dilakukan melalui varian atau konfigurasi yang eksplisit.

## 5.3 Penyajian dan pencatatan

Node mencatat konfigurasi, hash checkpoint, timestamp, waktu tahap pemrosesan, CPU, RSS, jumlah deteksi dan error. Mode preview menerbitkan citra beranotasi. Hasil deteksi dapat diperiksa pada [dokumentasi per model](../../dokumentasi/model/README.md). Angka confidence pada tampilan menunjukkan skor prediksi model dan tidak langsung menunjukkan ketepatan terhadap ground truth.

Kondisi fisik robot tidak disimpulkan oleh node deteksi; status diam atau berjalan dicatat berdasarkan prosedur dan bukti operasi yang tersedia. Mode asosiasi ID merupakan kemampuan tambahan dan tidak digunakan sebagai bukti bahwa servo kepala mengikuti objek.
