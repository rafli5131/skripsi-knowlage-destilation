# Prompt Implementasi Deteksi pada ROBOTIS OP3

> Salin prompt berikut ke coding assistant ketika mulai mengerjakan integrasi robot. Buka repository dan datasheet yang disebut di dalam prompt.

---

## Prompt

Bertindak sebagai engineer computer vision dan ROS 2 yang mengintegrasikan model PyTorch pada ROBOTIS OP3. Kerjakan implementasi pada repository ini, bukan sekadar memberi contoh umum. Sebelum mengubah kode, periksa struktur repository, datasheet OP3, checkpoint, konfigurasi model, serta antarmuka kamera dan ROS 2 yang benar-benar tersedia.

### Tujuan

Jalankan inferensi dari kamera ROBOTIS OP3 menggunakan checkpoint student KD:

```text
models/weights/kd_student_best.pt
```

Deteksi kelas sesuai indeks yang tercatat pada konfigurasi:

```text
0: ball
1: gawang
2: robot
```

Verifikasi urutan indeks dari konfigurasi sebelum membuat label tampilan; jangan mengubah mapping kelas.

### Konteks eksperimen

- Student adalah arsitektur YOLO11 custom yang lebih kecil, bukan otomatis model Ultralytics YOLO11n standar.
- Checkpoint adalah kandidat seed 42 dari pure teacher-only KD. Distilasi memakai fitur P3/P4/P5 dan output box/kelas teacher; objective KD tidak memakai ground-truth loss, pseudo-label loss, QAT, atau INT8.
- Benchmark akurasi memakai split resmi train/val/test dari dataset Roboflow `advance_vision_human` v1 (V1-Base). Protokol rinci ada di `PROTOKOL_EKSPERIMEN_SKRIPSI.md`.
- Checkpoint belum diuji pada kamera/runtime OP3. Benchmark NVIDIA L40 yang ada di repository bukan hasil OP3.
- Rencana runtime memakai PyTorch/Ultralytics `.pt` pada CPU. Jangan menambahkan OpenVINO, QAT, INT8, atau training ulang.
- Data terminal OP3 yang pernah dilaporkan: x86_64, Intel Core i5-1240P, Ubuntu 24.04.5, Python 3.12.3, ROS 2 Jazzy. Verifikasi ulang keadaan aktual sebelum menentukan dependensi atau sumber gambar.

### Ruang lingkup dan keselamatan

- Node deteksi hanya membaca frame dan menerbitkan hasil. Jangan mengirim perintah servo, mengubah gait, menyalakan motor, atau mengendalikan robot berjalan.
- Uji dilakukan operator dalam dua kondisi terpisah: `servo_idle` (robot menyala dan diam) dan `walking` (servo aktif/robot berjalan). Node mencatat kondisi yang dipilih, tetapi tidak mengubahnya.
- Jangan menginstal paket ke Python sistem atau mengubah konfigurasi ROS/servo secara otomatis. Jika diperlukan, jelaskan perubahan dan minta persetujuan operator.
- Jangan menyimpan atau mengunggah gambar/video secara otomatis. Penyimpanan rekaman harus menjadi pilihan eksplisit operator.
- Jangan mengklaim akurasi khusus kamera OP3 hanya dari tampilan kotak deteksi. Klaim akurasi memerlukan frame berlabel dan evaluasi terhadap ground truth.

### Pekerjaan

1. Temukan sumber gambar yang benar dengan memeriksa datasheet, paket, dan topik ROS 2 yang tersedia. Jangan menebak nama topik atau device kamera. Jika kamera tidak dapat diakses, buat sumber gambar yang dapat dikonfigurasi dan jelaskan prasyarat yang belum tersedia.
2. Buat node/entry point yang memuat checkpoint, mengambil frame, melakukan preprocessing, inferensi batch 1, dan postprocessing. Mulai dengan CPU, FP32, dan input 640 × 640. Pertahankan rasio gambar, gunakan letterbox bila pipeline model mendukungnya, dan catat konfigurasi aktual.
3. Jadikan sumber kamera, ukuran input, confidence threshold, IoU NMS, dan kondisi uji sebagai parameter. Jangan mengubah threshold evaluasi offline tanpa mencatatnya.
4. Tampilkan atau terbitkan gambar dengan bounding box, kelas, dan confidence. Sediakan opsi mematikan preview agar rendering tidak membebani pengukuran.
5. Catat waktu capture, preprocessing, inference, postprocessing, end-to-end per frame, FPS, utilisasi CPU, RAM proses, timestamp, resolusi, checkpoint, konfigurasi, dan kondisi `servo_idle`/`walking` ke CSV atau JSON.
6. Jalankan pengukuran terpisah dalam kondisi servo idle dan robot berjalan. Pertahankan model dan konfigurasi yang sama; jangan gabungkan hasil kedua kondisi menjadi satu angka tanpa melaporkan keduanya.
7. Hindari antrean frame yang terus menumpuk. Dokumentasikan kebijakan frame terbaru/frame yang terlewat. Tangani frame kosong, kamera terputus, checkpoint tidak ditemukan, dan shutdown dengan bersih.
8. Tambahkan dokumentasi setup, menjalankan/menghentikan node, memilih mode, dan membaca log. Jangan memulai pengujian fisik atau memberi perintah gerak sebagai bagian dari implementasi otomatis.

### Kriteria penerimaan

- Program memvalidasi checkpoint, mapping kelas, dependensi, dan sumber kamera sebelum inferensi.
- Hasil menggunakan kelas `ball`, `gawang`, `robot` dengan indeks yang tepat.
- Log membedakan servo idle dan berjalan dan menyediakan data untuk menghitung median/p95 latensi, FPS, CPU, dan RAM.
- Dokumentasi membedakan akurasi offline pada test Roboflow dari kinerja runtime kamera OP3.
- Jangan membuat angka hasil atau menyatakan robot telah diuji jika pengujian fisik belum dijalankan.
- Setelah implementasi, laporkan file yang diubah, cara menjalankan, pemeriksaan yang dilakukan, dan langkah manual operator yang masih diperlukan.

Mulai dengan membaca `README.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, `datasheet/README.md`, `environment/README.md`, dan `configs/data_train_val.yaml`. Pertahankan training scripts dan checkpoint; tugas ini adalah integrasi inferensi.
