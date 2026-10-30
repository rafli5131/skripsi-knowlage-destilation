# Prompt tes ROBOTIS OP3 setelah audit server — 30 Oktober 2026

Status: prompt siap salin, belum menjadi bukti uji robot. Dibuat dari prompt serah terima 24 Oktober, protokol live setara, dan audit checkpoint server 30 Oktober. Pastikan checkout robot memuat file prompt ini; jangan menganggap checkout robot otomatis mengikuti GitHub. Salin isi bagian berikut ke agen di robot, atau berikan file ini secara lokal.

---

Kamu bekerja sebagai engineer ROS 2 dan pencatat eksperimen pada ROBOTIS OP3. Gunakan Bahasa Indonesia. Kerjakan pengujian yang dapat dilakukan pada robot bersama operator, simpan bukti, lalu perbarui memory dan log. Gunakan skrip yang sudah tersedia; jangan membuat framework baru atau memperluas eksperimen.

## 1. Konteks dan sumber

Checkout robot yang pernah digunakan ialah `/home/humanoid/bre_skripsi`; periksa lokasi aktual sebelum bekerja. Baca `agent.md`, memory terbaru, `docs/DECISIONS.md` terutama D14/D16, `OP3_PYTORCH_RUNTIME.md`, dan `configs/model_registry.yaml`.

Acuan detail:

- `prompt/PROMPT_UJI_ULANG_LIVE_SETARA_OP3_DENGAN_TEACHER.md`: kondisi fisik, urutan run, jendela waktu, dan kriteria sah.
- `prompt/PROMPT_UJI_ROBOT_OP3_SETELAH_KONFIRMASI_KD_2026-10-24.md`: serah terima model final.
- `prompt/PROMPT_EVALUASI_EKSTERNAL_OP3_JALUR_1.md`: sampling dan label set baru.
- `docs/TRANSFER_TEACHER_KE_OP3.md`: teacher privat dan override lokal.
- Bila sudah tersedia: `docs/PERSIAPAN_OP3_DARI_LAB_2026-10-30.md`, `artifacts/lab_audit_20261030/op3_preflight.json`, dan `op3_session_template.json` di direktori yang sama.

Hasil audit server: empat checkpoint dapat dimuat, SHA-256 cocok dengan registry, dan kelas `0: ball`, `1: gawang`, `2: robot`. Audit ini belum membuktikan kesiapan environment, kamera, atau kondisi fisik OP3. Training utama dan konfirmasi S2 selesai; Hybrid full seed 1337 tetap model utama. T42 merupakan ablasi server terpisah dan tidak perlu ditunggu. Jangan memakai teacher atau student T42 sebagai pengganti checkpoint di bawah.

Uji Hybrid historis sudah ada pada percobaan 27 dan T34. T34 memakai 260 frame eksploratif dengan draf label berbantuan Pure KD; sesi baru harus dicatat terpisah. Jangan mengasumsikan robot saat ini dalam keadaan yang sama dengan sesi lama.

## 2. Checkpoint yang dipakai

Semua path berikut relatif terhadap root repo robot.

| Kunci | Checkpoint | SHA-256 |
| --- | --- | --- |
| `teacher` | `models_local/teacher_fp32_best.pt` | `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` |
| `hybrid1337` | `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt` | `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363` |
| `sup1337` | `runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt` | `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041` |
| `kd42` | `models/weights/kd_student_best.pt` | `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3` |

Teacher utama memiliki 2.590.425 parameter; student memakai YOLO11 skala t kustom, 810.649 parameter. `op3_default` masih menunjuk Pure KD seed 42. Pilih Hybrid secara eksplisit. Jangan mengganti alias atau memilih model/threshold dari hasil pengujian ini.

## 3. Audit robot dan perbaikan environment

Mulai dari pemeriksaan baca saja: tanggal UTC/WIB, commit, perubahan lokal, OS, CPU/RAM, ROS, Python, PyTorch, Ultralytics, NumPy, OpenCV, lap, suhu/governor CPU, node, topic kamera, tipe pesan, QoS, resolusi, dan laju kamera. Batasi durasi perintah pengamatan topic; hentikan proses pengamat sebelum benchmark.

Gunakan environment OP3 yang sudah ada sesuai `OP3_PYTORCH_RUNTIME.md`; periksa bahwa satu interpreter bisa mengimpor `rclpy`, `cv_bridge`, `sensor_msgs`, `vision_msgs`, PyTorch, Ultralytics, OpenCV, PyYAML, psutil, dan `lap==0.5.12`. Jika dependency kurang, pasang sesuai `requirements-op3-pytorch.txt` ke venv OP3, dengan indeks CPU PyTorch yang didokumentasikan, lalu periksa ulang versi/import. Pertahankan modul ROS yang berasal dari environment robot. Jangan memasang paket ke Python sistem atau menyalin environment CUDA server.

Verifikasi hash keempat checkpoint dan mapping kelas pada robot. Teacher memakai override lokal:

```yaml
# configs/model_registry_local.yaml
teacher_fp32: models_local/teacher_fp32_best.pt
```

Gabungkan entri itu dengan konfigurasi lokal yang ada; jangan menimpa override lain. Jika teacher belum tersedia, laporkan path yang diperlukan dan gunakan prosedur transfer privat dengan operator. Jangan mengganti teacher dengan checkpoint lain. Jika hash tidak cocok, hentikan tahap yang memakai model tersebut.

Jangan otomatis menarik perubahan Git atau mereset checkout robot. Audit kemampuan runtime aktual: dukungan empat varian, override teacher, thread, warm-up, durasi, `receive_time_utc`, `capture_stamp_ns`, dan `is_warmup`. Jika berkas baru belum ada, gunakan salinan prompt ini; jika kemampuan runtime wajib belum ada, laporkan kekurangannya sebelum benchmark.

Laporkan ringkasan kesiapan. Lanjutkan pekerjaan perangkat lunak yang sudah diizinkan; hentikan hanya tahap yang memerlukan dependency, artefak, atau konfirmasi fisik yang belum tersedia.

## 4. Persiapan operator dan pemeriksaan fungsi

Operator mengendalikan servo, kepala, manager, dan gait. Agen hanya menjalankan detektor, penampil, pencatatan, serta pembacaan telemetry yang diizinkan. Jangan mengirim perintah motor, `ini_pose`, atau head-following. Tracking BoT-SORT di sini hanya asosiasi ID pada gambar.

Ikuti Fase 2 protokol live untuk pemeriksaan badan dan kepala. Setelah manager aktif, jangan membuka bus serial lagi. Gunakan telemetry yang tersedia melalui jalur yang sudah dipakai pada sesi sebelumnya. Kondisi benchmark yang harus diverifikasi operator:

- `op3_manager` aktif dengan `auto_start_init_pose:=false` pada idle maupun walking.
- Torque ID 1–20 aktif; kepala 19/20 mempertahankan posisi awal, tanpa perintah gerak selama run.
- Kamera, posisi objek, sumber daya, dan pencahayaan konsisten; OP3 kembali ke tanda lantai sebelum setiap run berjalan.
- Operator hadir, area aman, dan kondisi berjalan dikonfirmasi kembali sebelum tiap blok walking.

Jika kondisi tidak terverifikasi, pakai `unknown` pada pemeriksaan fungsi dan jangan memasukkannya sebagai benchmark idle/walking. Hentikan sesi jika operator meminta, robot tidak stabil, ada hardware error servo, tegangan terukur di luar 10–15 V, suhu kepala terukur ≥65 °C, atau sampel posisi kepala bergeser >2 count. Catat batas pemantauan bila suhu/tegangan hanya dapat dibaca saat persiapan.

Jalankan pemeriksaan fungsi Hybrid dengan preview dan BoT-SORT. Tampilkan ball, gawang, dan robot satu per satu; catat objek terdeteksi, objek terlewat, salah kelas, kotak berlebih, dan perubahan ID. Jalankan smoke test teacher sekitar 30 detik; pastikan override dan hash tercatat benar, model termuat, dan keluaran terbit. Ketiadaan suatu kelas pada adegan bukan otomatis kegagalan perangkat lunak. Kedua smoke test tidak masuk T36/T37.

Tunggu operator menyetujui adegan dan arah kamera sebelum matriks utama. Rekam 10 frame referensi mentah sebelum run pertama dan sesudah run terakhir saat detektor berhenti, sesuai protokol lama. Simpan lokal dengan session_id unik.

## 5. Benchmark utama: 24 run

Pertahankan konfigurasi berikut untuk semua model:

| Pengaturan | Nilai |
| --- | --- |
| Perangkat dan presisi | CPU OP3, FP32 |
| Kamera | `/thesis/image_raw`, 640×480; verifikasi publisher dan QoS |
| Input model | 640 |
| Confidence / NMS IoU live | 0,25 / 0,45 |
| Tracking | BoT-SORT aktif |
| Thread intra-op / inter-op | 4 / 2 |
| Warm-up | 30 frame |
| Durasi node setelah warm-up | **75 detik** (`duration_s:=75`) |
| Jendela analisis | **60 detik**, dipilih dari CSV sesuai aturan di bawah |
| Preview | Aktif melalui SSH-X, satu penampil yang sama, jendela terlihat |
| Jeda antarrun | Minimal 120 detik |
| Proses tambahan | Tidak ada capture, rosbag, labeler, detektor kedua, atau proses berat |

Jika topic/resolusi atau konfigurasi wajib berbeda, dokumentasikan dan selesaikan keputusan protokol sebelum benchmark; jangan menggantinya diam-diam.

| Putaran | Idle | Walking |
| --- | --- | --- |
| u1 | teacher → hybrid1337 → sup1337 → kd42 | kd42 → sup1337 → hybrid1337 → teacher |
| u2 | hybrid1337 → kd42 → teacher → sup1337 | sup1337 → teacher → kd42 → hybrid1337 |
| u3 | sup1337 → teacher → kd42 → hybrid1337 | hybrid1337 → kd42 → teacher → sup1337 |

Buat run_id unik dari tanggal aktual, model, kondisi, dan ulangan. Pakai akhiran `_ulang1` bila mengulang run tidak sah, dan pertahankan semua hasil gagal. Pilih nomor dokumentasi berikutnya yang belum dipakai; nomor percobaan 29 sudah dipakai diagnosis lab.

Argumen model pada `scripts/op3_pytorch_detector.py`:

- teacher: `-p model_variant:=teacher`, tanpa `model_path` agar override lokal dipakai.
- hybrid1337: `-p model_variant:=hybrid`.
- sup1337: `-p model_variant:=supervised -p model_path:=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt`. Tanpa path eksplisit, varian ini dapat memuat seed 42.
- kd42: `-p model_variant:=kd`.

Argumen bersama: `input_topic:=/thesis/image_raw`, `imgsz:=640`, `confidence_threshold:=0.25`, `iou_threshold:=0.45`, `enable_tracking:=true`, `tracker_config:=botsort.yaml`, `publish_debug_image:=true`, `torch_num_threads:=4`, `torch_interop_threads:=2`, `warmup_frames:=30`, `duration_s:=75`, serta run_id dan kondisi yang telah diverifikasi. Susun perintah dari parameter aktual skrip; jangan menjalankan placeholder literal.

Tentukan `t_w` dari `receive_time_utc` frame pertama `is_warmup=false`. Idle memakai `[t_w+5 s, t_w+65 s]`. Untuk walking, operator memulai gait sekitar `t_w+3 s`; catat ack UTC pada jam NUC sebagai `t_g`, ukur `[t_g+2 s, t_g+62 s]`, dan operator menghentikan gait pada `t_g+63 s`. Bila ack lebih dari `t_w+10 s`, run tidak sah. Jangan mengurangkan timestamp kamera dari UTC ack gait karena domain jamnya belum terbukti sama.

Catat telemetry awal, dua sampel tengah, dan dua sampel akhir sesuai protokol. Operator menjalankan seluruh perintah gerak. Run sah memerlukan hash cocok, jendela 60 detik lengkap, error frame ≤1%, preview aktif, tidak ada loncatan jam, simpangan kepala pada sampel ≤2 count, serta telemetry kondisi yang sesuai: idle berubah ≤0,00307 rad pada badan; walking menunjukkan perubahan pinggul/lutut dan stabil setelah stop. Run tidak sah disimpan dengan alasan dan diulang di akhir blok.

## 6. Analisis runtime

Gunakan hanya frame dalam jendela sah. Laporkan rata-rata, median, P95 latensi per tahap dan callback total; FPS efektif; CPU proses; RSS MiB; jumlah/error frame; suhu awal/akhir; kondisi dan penyimpangan. FPS dihitung `(N−1)/(timestamp_akhir−timestamp_awal)` dari capture timestamp positif, unik, dan meningkat. Jika timestamp kamera tidak valid, tandai FPS kamera tidak sah dan laporkan FPS waktu penerimaan hanya sebagai diagnostik. Jangan memakai `1000/latensi` sebagai FPS terukur.

CPU persen satu CPU logis dan persen kapasitas seluruh CPU harus dibedakan; gunakan jumlah CPU logis aktual. Tampilkan tiga ulangan dan rerata ± SD antarulangan untuk setiap model/kondisi. Perbandingan utama runtime ialah teacher versus Hybrid; mutu KD dibandingkan dengan supervised berarsitektur sama. Jangan mengklaim signifikansi kuat dari tiga ulangan.

Buat T36 per-run dan T37 ringkasan dengan nama yang sudah ditetapkan protokol, serta grafik ringkas. Semua run gagal/parsial tetap tercatat. Gunakan nomor percobaan aktual saat menautkan T19/T26; jangan menyalin label historis `percobaan 29` dari contoh lama. Jangan menimpa tabel lama atau menjalankan generator yang akan meregenerasi seluruh arsip tanpa pemeriksaan.

## 7. Set akurasi OP3 baru

Kerjakan setelah benchmark selesai, pada sesi terpisah. Sebelum capture, bekukan jumlah frame, sesi/kondisi, variasi jarak/objek, frame negatif, interval sampling, aturan frame, definisi kotak gawang utuh/parsial, dan konfigurasi evaluator. Jika keputusan ini belum tersedia atau masih `temporary`, siapkan rancangan konkret dan minta Bhre menetapkannya sebelum pengambilan final. Jangan memilih frame berdasarkan keberhasilan detektor.

Simpan frame mentah, `labels_auto`, dan `labels_reviewed` terpisah. Utamakan peninjauan dari gambar mentah tanpa prediksi kandidat; bila pra-label dipakai, catat asalnya dan bias yang mungkin terjadi. Bhre wajib memeriksa setiap frame, termasuk frame kosong. Tanpa tinjauan lengkap, laporkan jumlah frame yang menunggu label dan hentikan perhitungan akurasi final.

Bekukan hash frame/label, lalu evaluasi empat checkpoint pada gambar dan label identik. Gunakan pengaturan evaluasi yang dibekukan, bukan otomatis menyalin NMS live. Acuan evaluasi sebelumnya: AP confidence floor 0,001, input 640, NMS IoU 0,7, P/R/F1 confidence >0,25 dan IoU matching ≥0,5. Catat versi evaluator serta definisi F1 makro sebagai rerata F1 per kelas; jangan mencampurnya dengan F1 dari P/R makro.

Laporkan mAP50–95, AP tiap kelas, precision, recall, F1, serta FP pada frame negatif per kondisi. T34 lama tetap eksploratif. T38 retrospektif pada 260 frame lama hanya dikerjakan bila diminta; set baru memakai nomor tabel kosong setelah T43. Hasil set baru tidak dipakai memilih ulang checkpoint atau ambang.

## 8. Penutupan, memory, dan laporan

Simpan artefak minimum yang dapat diaudit: manifest/checkpoint/hash, konfigurasi dan versi aktual, jadwal run rencana/aktual, JSON/CSV mentah, bukti kondisi/telemetry, jendela analisis, status sah/tidak sah dan alasannya, tabel/grafik ringkas, serta README sesi. Gunakan generator yang sudah tersedia. Hindari membuat banyak salinan atau alat baru untuk dokumentasi yang sama.

Perbarui memory bertanggal aktual, indeks hasil, dan manifest sumber/keluaran untuk tabel baru. Laporkan kepada Bhre: kesiapan perangkat, hasil fungsi tiap kelas, jumlah run sah/gagal/parsial, ringkasan T37 bila tersedia, status capture dan tinjauan label, lokasi artefak, serta pekerjaan yang terhambat. Laporkan hanya pengujian yang benar-benar terjadi.

Robot tetap didampingi operator; operator menghentikan gait dan menetapkan kondisi akhir. Seluruh teacher privat, gambar, video, label, screenshot, dan log mentah tetap lokal. Jangan commit, push, atau unggah tanpa instruksi khusus. Tugas dianggap selesai untuk sesi ini setelah semua tahap yang memungkinkan selesai dan tahap yang menunggu operator/label dicatat secara konkret.

Mulai sekarang dari audit perangkat lunak, kamera, dan hash checkpoint. Jangan menjalankan benchmark fisik sebelum kondisi operator dan adegan terkonfirmasi.
