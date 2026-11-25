# Prompt: preview deteksi objek OP3 dan rekaman layar SSH-X

Jalankan instruksi berikut pada komputer onboard ROBOTIS OP3. Tujuannya membuka preview deteksi objek, memberi kesempatan operator menata objek, lalu membuat **rekaman layar jendela preview** sebagai dokumentasi. Ini bukan pengujian performa atau pengambilan ground truth baru.

## Ketentuan

- Gunakan jendela desktop melalui SSH-X, tanpa aplikasi web. Tampilkan kelas `ball`, `gawang`, dan `robot`, kotak deteksi, serta confidence apabila tersedia. ID tracking boleh ditampilkan jika jalur yang digunakan mendukungnya; jangan menyatakan tracking telah diuji hanya karena ID tampil.
- Gunakan model yang diminta operator. Jika belum ditentukan, gunakan **KD Hybrid full seed 1337** (`model_variant:=hybrid`), bukan alias `op3_default` yang menunjuk KD murni. Pilihan lain: teacher, supervised seed 1337, dan KD murni seed 42. Untuk supervised seed 1337 berikan `model_path:=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt`; varian supervised tanpa path menunjuk seed lain. Periksa `configs/model_registry.yaml`, path sebenarnya, dan SHA-256 checkpoint sebelum mulai, termasuk override lokal teacher. Laporkan nama model dan hash; jangan diam-diam mengganti model jika checkpoint tidak tersedia atau hash berbeda.
- Jangan mengirim perintah servo, torque, gait, pose, modul gerak, atau motor, termasuk ID 19 dan 20. Jangan mengubah arah kamera. Catat kondisi robot sesuai konfirmasi operator; jika tidak diketahui tulis `unknown`. Jangan menjalankan robot.
- Ikuti `AGENTS.md`, `agent.md`, dan memory terbaru. Untuk kode baru terkait robot, buat package baru dan gunakan fungsi package lama sebagai shared; jangan mengubah package yang sudah ada. Utamakan komponen yang tersedia agar tidak perlu membuat kode baru.
- Jangan menghapus atau menimpa data/artefak sebelumnya. Jangan commit, push, atau unggah video, gambar, dan log tanpa instruksi khusus operator.

## 1. Pemeriksaan awal dan preview

1. Periksa status proses serta publisher/subscriber kamera dan detektor yang sedang aktif. Gunakan hanya stream yang benar-benar tersedia, periksa topik, QoS, dan frame yang terus bertambah. Hindari menjalankan detektor duplikat atau menghentikan proses milik pengguna lain. Jika kamera/publisher belum tersedia, diagnosis dan gunakan prosedur kamera yang ada tanpa perintah motor; jika tidak dapat dipulihkan, laporkan hambatannya.
2. Periksa ketersediaan checkpoint, environment ROS dan PyTorch, ruang penyimpanan, `ffmpeg`, `ffprobe`, `xwininfo`, serta dukungan `ffmpeg -h demuxer=x11grab`. Pastikan sesi SSH-X memiliki `DISPLAY`, otorisasi X11 yang berfungsi, dan jendela dapat dibuka. Jangan menampilkan isi cookie otorisasi. Jika X11 belum tersambung, jelaskan cara menyambung ulang dengan `ssh -X`; jangan diam-diam beralih ke web.
3. Utamakan [`ros2_packages/op3_fullscreen_preview/README.md`](../ros2_packages/op3_fullscreen_preview/README.md): penampil menjalankan satu model terpilih, dengan tombol `1` untuk kamera dan kotak deteksi, `2` untuk dashboard grafik FPS, latensi inferensi, CPU dan RAM, serta `F` untuk fullscreen. Jika operator meminta kedua versi rekaman, rekam setiap tampilan secara terpisah setelah konfirmasi; jangan jalankan inferensi kedua. Jika detektor lain sudah aktif, hindari inferensi duplikat: gunakan satu penampil [`scripts/view_op3_debug_image.py`](../scripts/view_op3_debug_image.py) untuk topik debug aktual, atau hentikan hanya proses sendiri setelah tidak diperlukan lalu gunakan penampil fullscreen. Jalur alternatif detektor dijelaskan pada [`docs/OP3_PYTORCH_RUNTIME.md`](../docs/OP3_PYTORCH_RUNTIME.md). Monitor lama [`op3_live_monitor`](../ros2_packages/op3_live_monitor/README.md) khusus KD seed 42; jangan gunakan untuk model lain.
4. Periksa gambar bergerak dengan cap waktu atau nomor frame yang meningkat dan laporkan model, kelas yang benar-benar terdeteksi, serta status preview. Kegagalan mendeteksi suatu kelas adalah observasi yang harus dilaporkan, bukan alasan mengganti model atau mengarang hasil. Pertahankan preview aktif agar operator dapat mengatur objek. Gawang parsial boleh tetap terlihat sesuai pengaturan operator.
5. Beritahu operator bahwa preview sudah aktif, model yang digunakan, dan bahwa **rekaman belum dimulai**. Minta operator menata objek dan mengonfirmasi kesiapan sebelum merekam. Tunggu jawaban; jangan memulai perekaman berdasarkan asumsi. Jika durasi belum ditentukan, tawarkan 60 detik sebagai durasi dokumentasi, dengan opsi lain dari operator.

## 2. Rekam layar setelah konfirmasi

Jika operator secara khusus memilih rekaman langsung keluaran deteksi, gunakan opsi `--record-dir`, `--record-duration`, dan `--record-fps` pada penampil fullscreen; lihat README package. Verifikasi durasi, frame berulang, dan isi hasilnya. Catat sebagai **rekaman keluaran preview beranotasi**, bukan rekaman layar desktop. Tetap minta konfirmasi sebelum memulai, gunakan satu aliran inferensi, lalu lanjutkan ke dokumentasi pada bagian 3. Untuk pilihan rekaman layar X11, jalankan langkah-langkah berikut:

1. Setelah konfirmasi, tentukan jendela preview yang benar dengan `xwininfo`/identitas proses dan verifikasi bahwa jendela tersebut benar-benar menampilkan deteksi terkini. Rekam **jendela itu**, bukan seluruh desktop atau aplikasi lain. Jangan minimalkan atau menutup jendela selama rekaman. Beritahu operator tepat saat perekaman dimulai dan durasinya.
2. Gunakan `ffmpeg` dengan perangkat `x11grab` dan opsi `-window_id` bila dapat mengakses jendela melalui display sesi SSH-X. Tentukan frame rate dan encoder yang tersedia sesuai kemampuan perangkat, utamakan preview tetap responsif, dan simpan berkas video pada direktori sesi unik. Jika akses X11/forwarding tidak memungkinkan perekaman jendela yang benar, jelaskan hambatannya dan minta operator merekam jendela pada laptop dengan alat lokal. Jangan menyebut rekaman topic kamera atau video anotasi ROS sebagai screen recording; bila operator memilihnya secara terpisah, beri label yang sesuai.
3. Pantau detektor, frame preview, proses perekam, dan ruang penyimpanan. Jika preview macet atau perekaman gagal, catat rentang kejadian dan statusnya; jangan menampilkan hasil seolah berhasil. Hentikan perekam secara normal pada akhir durasi agar video selesai ditulis. Jangan menghentikan proses pengguna lain; biarkan preview menyala kecuali operator meminta sebaliknya.
4. Verifikasi video menggunakan `ffprobe`: ada stream video yang dapat dibaca, dimensi, frame rate, dan durasi sesuai hasil sebenarnya. Periksa beberapa frame awal, tengah, dan akhir untuk memastikan isi adalah jendela deteksi yang dimaksud; bedakan adegan statis dari preview yang benar-benar macet. Buat satu screenshot representatif dari video, dan catat jika kualitas, durasi, atau kesinambungannya kurang baik.
5. Simpan rekaman penuh secara lokal. Jika diminta klip ringkas atau suatu saat perlu dibagikan dengan izin khusus, buat salinan maksimal 10 detik tanpa menimpa rekaman asli; periksa klip dengan `ffprobe`. Jangan mengunggah rekaman atau klip tanpa izin eksplisit untuk artefak tersebut.

## 3. Dokumentasi dan laporan

Buat direktori baru yang unik seperti `dokumentasi/YYYY-MM-DD/percobaan-HHMMSS-preview-rekam-layar-<model>/`, berisi:

```text
README.md                 Tujuan, kondisi, langkah, hasil dan keterbatasan
manifest.json             Waktu dan zona waktu, model, checkpoint dan SHA-256,
                          topik, konfigurasi, durasi, kondisi operator,
                          jalur rekaman, status verifikasi, dan gangguan
rekaman_preview.mp4        Rekaman layar jendela, bukan hanya topic ROS
screenshot_preview.png    Contoh frame yang diambil dari rekaman
klip_10_detik.mp4         Opsional, bila diminta atau disiapkan untuk berbagi
```

Gunakan ekstensi dan nama sesuai format aktual; jangan membuat entri yang menyatakan file tersedia jika perekaman gagal. Catat jam mulai/selesai, perangkat yang merekam (robot atau laptop), resolusi, fps dan durasi aktual, serta apakah preview tetap berjalan. Metrik yang terlihat pada preview bersifat pengamatan sesi dan dapat terpengaruh overhead encoding/SSH-X; confidence bukan akurasi, dan mAP/precision/recall/F1 tidak dapat dihitung dari rekaman tanpa ground truth. Jangan gabungkan rekaman ini ke benchmark sebelumnya.

Sampaikan lokasi file yang benar-benar dibuat, model/hash, durasi, hasil pemeriksaan, dan kendala apa pun. Jangan mengklaim video telah dipush jika tidak ada instruksi dan hasil push yang terverifikasi.
