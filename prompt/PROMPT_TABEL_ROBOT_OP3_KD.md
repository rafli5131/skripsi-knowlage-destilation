# Prompt Tabel ROBOTIS OP3 — Runtime Realtime

## Tujuan

Gunakan prompt ini pada repository `~/bre_skripsi` untuk menganalisis pengukuran runtime/perangkat ROBOTIS OP3 dan memperbarui tabel T15–T27. Bentuk tabel harus mengikuti template di `~/bre_skripsi/analisis_performa/tabel/`.

## Prompt

Bertindak sebagai asisten analisis runtime computer vision dan ROS 2. Kerjakan hanya dari log/artefak OP3 yang sudah tersimpan. Jangan menjalankan perintah kamera, servo, gait, atau mengubah robot. Fokus pada model yang sudah dilatih di lab/server dan dideploy ke robot.

### Nomenklatur dan pemisahan kerja

Training dilakukan di komputer lab/server dengan **Knowledge Development (KD)** sesuai istilah penulis, bukan QAT. Pada robot hanya dilakukan inferensi realtime dan pencatatan runtime. Gunakan checkpoint student KD `.pt` dan runtime PyTorch/Ultralytics yang benar-benar tercatat. Jangan mengasumsikan OpenVINO, QAT, INT8, atau model lain. Jangan memasukkan metrik TEST offline sebagai akurasi kamera OP3.

### Ikuti format tabel yang sudah ada

1. Baca `analisis_performa/tabel/T15_*.md` sampai `T27_*.md`, `analisis_performa/DEFINISI.md`, `OP3_PYTORCH_RUNTIME.md` bila tersedia, dan `PROMPT_PERBAIKAN_KODE_DAN_ANALISIS_PERFORMA.md` bagian 6.
2. Pertahankan nomor/nama file T15–T27, judul `# Tnn. ...`, baris status, urutan, gaya Markdown, header `snake_case`, satuan dalam header, koma desimal Markdown, dan catatan sumber. Bila file template masih berupa placeholder `| status |`, gunakan schema rinci T15–T27 pada bagian 6.4 sebagai kolom target; jika datanya belum ada, jangan mengarang baris nilai.
3. Status `Lengkap`, `Sebagian`, atau `Belum diukur` harus mencerminkan bukti. Tulis `[BELUM DIUKUR]` untuk angka yang tidak punya sumber. Pertahankan CSV mentah dan log; jangan menimpa atau menghapusnya.

### Tabel robot yang harus diperiksa

- **T15 lingkungan uji OP3:** field, value, status, source. Cakup CPU/inti/thread, RAM, OS/kernel, Python/PyTorch/Ultralytics/OpenCV/ROS 2, governor/mode daya (dicatat saja), kamera, resolusi, format piksel, FPS diminta, topic, dan QoS. Jangan menyimpulkan parameter yang tidak direkam.
- **T16 latensi frame tetap:** varian × imgsz × thread; preprocess, inference, postprocess, total (mean/median/p95/p99/SD), FPS turunan, jumlah frame/blok. Isi hanya bila ada benchmark CPU OP3 pada frame tetap; jangan substitusi dengan sesi kamera live.
- **T17 sapuan thread:** thread × varian; median/p95 total, FPS turunan, CPU mentah/ternormalisasi, FPS per inti. Jika tidak pernah diukur, status tetap belum diukur.
- **T18 sesi live historis:** run_id, condition/catatan kondisi, processed frames, durasi capture, effective FPS, warmup, capture gap p50/p95/max, gap >1 s, end-to-end median/p95, CPU, RSS, jumlah deteksi, tracked IDs bila tersedia. Kondisi yang belum diverifikasi harus ditulis `unknown`, bukan servo_idle/walking.
- **T19 servo idle vs walking:** per varian, walking dikurangi servo_idle untuk metrik T18 dan CI antarsesi jika cukup sampel. Jangan mengisi hasil walking bila run walking belum ada.
- **T20 sumber daya startup:** waktu load model, latensi frame pertama, RSS median/puncak, CPU median/p95 jika ada.
- **T21 stabilitas termal:** suhu awal/maksimum, frekuensi, throttling, waktu pendinginan per blok/sesi sesuai data sensor. Jangan menamai suhu sebagai CPU package jika identitas sensor tidak ada.
- **T22 aliran kamera:** camera topic rate, processed frame rate/count, with_detector, camera_only_comparison. Bedakan probe kamera tanpa model dari log detektor; jangan menyebutnya perbandingan jika tidak ada dua kondisi terukur.
- **T23 kepatuhan tenggat:** proporsi frame pada batas 33,3 ms dan 66,7 ms untuk latency total/end-to-end, sesuai definisi; jangan menghitung bila sampel atau timestamp tidak cukup.
- **T24 pengaruh preview:** bandingkan preview off/on hanya bila ada sesi terkontrol dengan protokol sama.
- **T25 observasi deteksi live:** total/per-class detection, distribusi confidence, track IDs hanya jika CSV per deteksi/track tersedia. Tandai bukan akurasi.
- **T26 trade-off utama:** rangkum akurasi offline KD/supervised/teacher dari T05/T06 secara terpisah dari metrik runtime OP3 yang benar-benar terukur. Jangan menyimpulkan kinerja realtime OP3 dari benchmark server.
- **T27 akurasi frame kamera OP3:** memerlukan frame berlabel dan ground truth. Selama set berlabel belum tersedia, pertahankan status `[BELUM DIUKUR]`; jumlah deteksi/confidence kamera tidak boleh disebut precision, recall, F1, atau mAP.

### Sumber dan definisi

Gunakan `runs/op3_pytorch/`, log/manifest sesi robot, `OP3_PYTORCH_RUNTIME.md`, `analisis_performa/DEFINISI.md`, serta template T15–T27. Ikuti definisi repository: latensi per tahap preprocess/inference/postprocess; end-to-end dari callback sampai keluaran diterbitkan; effective FPS `(n - 1) / (t_n - t_1)` dari timestamp frame yang diproses setelah warm-up bila penandanya ada; FPS turunan `1000 / rerata latensi total` dilaporkan terpisah; CPU ternormalisasi hanya jika jumlah logical CPU tersedia; persentil memakai interpolasi linear NumPy.

### Batas interpretasi

- Uji kamera live tanpa ground truth hanya menghasilkan observasi runtime/deteksi, bukan akurasi.
- Jangan menyebut tiga sesi historis sebagai walking atau servo_idle jika kondisi tersebut tidak tercatat/terverifikasi.
- Jangan mengklaim sebab-akibat antara kondisi robot dan latency/FPS dari sesi yang tidak sebanding.
- Jangan menggabungkan sesi berbeda, model berbeda, atau versi protokol tanpa label.
- Jangan menjalankan training, tuning, TEST offline, instalasi paket, perubahan kode, atau perintah kontrol robot.

### Hasil yang diminta

Perbarui atau hasilkan T15–T27 dalam schema/gaya folder yang ada, dengan path dan status setiap tabel. Jelaskan mana yang terukur, sebagian, dan belum diukur. Jangan mengubah T01–T14 karena itu hasil lab/server.
