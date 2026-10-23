# Prompt uji ulang live OP3 dengan kondisi setara dan *teacher*

> **Ditunda (23 Oktober 2026).** Atas keputusan Bhre, prompt ini baru dijalankan setelah `prompt/PROMPT_PERBAIKAN_KD_JALUR_TENGAH.md` selesai sampai TH5. Bila perbaikan objektif menghasilkan model hasil KD baru, kunci `hybrid1337` pada tabel model diganti sesuai catatan "Pembaruan model" yang akan ditambahkan di sini. Tanpa catatan itu, model hasil KD tetap Hybrid full seed 1337.

> Versi 1, 23 Oktober 2026. Status: **belum dijalankan.** Prompt ini dibuat atas arahan Bhre bahwa pengujian akhir skripsi adalah uji live pada ROBOTIS OP3. Prompt ini menggantikan Sesi B pada `PROMPT_PERCOBAAN_KD_HYBRID_DI_ROBOT_OP3_V2.md` untuk keperluan pengujian akhir. Hasil percobaan 16 sampai 27 tetap disimpan sebagai uji pendahuluan dan tidak boleh dihapus, ditimpa, atau digabung dengan hasil sesi ini.

## Latar dan tujuan

Uji live sebelumnya (percobaan 25, 26, 27) tidak setara antarmodel. Tiap kondisi hanya satu *run*, adegan dan waktu pengambilan berbeda, dan pada KD murni `op3_manager` mati saat *idle* tetapi aktif saat berjalan. *Teacher* belum pernah diuji live, sehingga baris *teacher* pada T26 masih `[BELUM DIUKUR]`. Akibatnya rumusan masalah nomor 4 (latensi dan FPS model hasil KD dan *teacher* pada kondisi diam dan berjalan) dan nomor 5 (CPU dan RAM) belum terjawab.

Sesi ini mengukur empat model pada dua kondisi dengan tiga ulangan dan pengaturan yang sama:

| Kunci | Model | Peran | *Checkpoint* | SHA-256 |
|---|---|---|---|---|
| `teacher` | *Teacher* YOLO11n FP32 | Pembanding utama RQ4 dan RQ5 | `models_local/teacher_fp32_best.pt` (lokal, lewat override) | `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` |
| `hybrid1337` | KD Hybrid full seed 1337 | Model hasil KD utama | `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt` | `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363` |
| `sup1337` | *Supervised* seed 1337 | Kontrol arsitektur sama | `runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt` | `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041` |
| `kd42` | KD murni seed 42 (`op3_default`) | Ablasi KD tanpa label | `models/weights/kd_student_best.pt` | `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3` |

## Prompt siap pakai

Bertindak sebagai *engineer* ROS 2 dan pencatat eksperimen pada ROBOTIS OP3 di `/home/humanoid/bre_skripsi`. Tugasmu menjalankan uji live akhir empat model di atas pada kondisi *idle* dan berjalan dengan kondisi yang setara, lalu mendokumentasikan setiap pengujian. Baca lebih dahulu prompt ini, `OP3_PYTORCH_RUNTIME.md`, `docs/TRANSFER_TEACHER_KE_OP3.md`, README `ros2_packages/op3_servo_torque_control`, README `ros2_packages/op3_head_pose_hold`, serta dokumentasi percobaan 25, 26, dan 27 (termasuk berkas lokal perintah *gait* dan *telemetry* di folder `02-berjalan/`). Gunakan prosedur yang sama dengan percobaan tersebut kecuali bila prompt ini menyatakan lain.

### 0. Batas tindakan dan keselamatan

Yang boleh dilakukan agen:

- menjalankan detektor `scripts/op3_pytorch_detector.py`, penampil `scripts/view_op3_debug_image.py`, pembacaan *telemetry*, dan perekam *frame* referensi pada Fase 2;
- menjalankan `op3_servo_torque_control` dan `op3_head_pose_hold` sesuai README-nya, hanya setelah operator menyetujui di chat;
- mengirim perintah *start* dan *stop* *gait* standar yang **sama persis** dengan percobaan 25 sampai 27, hanya setelah operator mengonfirmasi blok berjalan di chat.

Yang dilarang:

- mengirim `ini_pose`, perintah kepala, `Goal_Position` ID 19/20, atau menjalankan `op3_head_ball_tracking`;
- menulis register servo apa pun setelah `op3_manager` berjalan (bus serial dipakai manager);
- mengubah *governor* CPU, parameter kamera, atau parameter *gait* di tengah sesi;
- melatih model, mengganti alias `op3_default`, mengubah package lama, menghapus atau menimpa *run* lama;
- `git commit` atau `git push` dari robot; menyalin bobot *teacher* ke repo.

Hentikan sesi dan laporkan bila: robot tidak stabil atau berisiko jatuh, servo melaporkan *hardware error*, tegangan di luar 10 sampai 15 V, suhu servo kepala 65 °C atau lebih (batas yang dipakai `op3_head_ball_tracking`), posisi kepala bergeser lebih dari 2 *count*, atau operator meminta berhenti. Pesan operator untuk berhenti selalu didahulukan.

### 1. Definisi kondisi setara

Semua *run* memakai nilai berikut. Bila salah satu tidak dapat dipenuhi, hentikan dan laporkan; jangan mengganti nilai diam-diam.

| Variabel | Nilai tetap |
|---|---|
| Komputer | NUC OP3 yang sama; *governor* hanya dibaca dan dicatat |
| Inferensi | CPU FP32, `imgsz:=640`, `confidence_threshold:=0.25`, `iou_threshold:=0.45` |
| *Tracking* | `enable_tracking:=true`, `tracker_config:=botsort.yaml` |
| *Thread* | `torch_num_threads:=4`, `torch_interop_threads:=2` (sama dengan percobaan 20 sampai 27) |
| *Warm-up* | `warmup_frames:=30`, dikecualikan dari analisis |
| Kamera | `/thesis/image_raw` 640×480, satu *publisher*, konfigurasi kamera dicatat dan tidak diubah |
| *Preview* | `publish_debug_image:=true`; satu penampil `view_op3_debug_image.py` pada terminal SSH -X dari laptop dan jaringan yang sama; jendela terbuka dan tidak di-*minimize* sepanjang *run* |
| Manager | `op3_manager` aktif dengan `auto_start_init_pose:=false` pada **kedua** kondisi |
| Servo kondisi *idle* | *Torque* ID 1 sampai 20 menyala, tanpa *gait* (`experiment_condition:=servo_idle`) |
| Servo kondisi berjalan | *Torque* ID 1 sampai 20 menyala, *gait* standar aktif (`experiment_condition:=walking`) |
| Kepala | ID 19/20 *torque on* dengan *goal* = posisi aktual saat persiapan; tidak ada perintah selama sesi; simpangan maksimal 2 *count* (≈ 0,00307 rad) dari sampel awal tiap *run* |
| Adegan | Bola, gawang, dan robot pada posisi bertanda lakban; posisi berdiri OP3 bertanda; pencahayaan sama; tidak ada orang di dalam pandangan kamera |
| Jendela ukur | 60 detik untuk kedua kondisi (lihat Fase 4) |
| Proses lain | Tidak ada *capture*, pra-label, *rosbag*, detektor kedua, atau proses berat lain selama *run* |
| Jeda | Minimal 120 detik antar-*run* |
| Daya | Sumber daya yang sama untuk seluruh sesi, sebaiknya adaptor; tegangan dicatat saat persiapan |

### 2. Persiapan (Titik henti TH1 dan TH2)

**2.1 Audit perangkat lunak.** Catat waktu WIB dan UTC, `git rev-parse HEAD`, `git status --short`, OS, Python, ROS, PyTorch, Ultralytics, OpenCV, `lscpu`, `free -h`, *governor*, suhu CPU (`sensors` atau `/sys/class/thermal/thermal_zone*/temp`), daftar node, dan informasi topic kamera (`ros2 topic info -v`, `ros2 topic hz`). Pastikan *checkout* robot memuat commit `d8b4af9` atau sesudahnya. Bila belum, lakukan `git pull --ff-only` hanya jika *working tree* bersih dari perubahan yang memengaruhi runtime; bila tidak bersih, laporkan dan tunggu.

**2.2 Verifikasi *checkpoint*.** Hitung `sha256sum` keempat berkas pada tabel di atas. *Teacher* harus sudah dipindahkan operator sesuai `docs/TRANSFER_TEACHER_KE_OP3.md`, dengan `configs/model_registry_local.yaml` berisi `teacher_fp32: models_local/teacher_fp32_best.pt`. Bila *teacher* belum ada atau hash tidak cocok, hentikan seluruh sesi: tanpa *teacher*, tujuan sesi tidak tercapai.

**TH1:** laporkan hasil audit dan hash kepada Bhre, lalu tunggu persetujuan.

**2.3 Servo dan kepala (sebelum manager).** Jalankan dengan `source /opt/ros/jazzy/setup.bash` lalu tambahkan path package tanpa menimpa `PYTHONPATH`:

1. `python3 -m op3_servo_torque_control.cli --preflight` untuk membaca daya bus, respons ID 1 sampai 20, mode, *hardware error*, dan tegangan.
2. Bila ID 1 sampai 18 belum menyala: `--enable-body --confirm-current-pose` setelah operator menyetujui.
3. Operator mengarahkan kepala secara manual ke adegan (*torque* kepala mati), lalu `python3 -m op3_head_pose_hold.cli --preflight`, `--dry-run`, dan `--hold-current-pose --confirm-current-camera-pose` setelah operator menyetujui arah kamera.
4. Bila seluruh 20 servo sudah menyala dari sesi sebelumnya dan *goal* kepala sama dengan posisi aktual, cukup catat hasil *preflight*; jangan menulis ulang.
5. Bila package menolak, berhenti dan laporkan. Jangan mencari jalan pintas.

Catat Goal/Present ID 19/20, suhu kepala, dan tegangan. Lalu jalankan `op3_manager` dengan `auto_start_init_pose:=false` memakai perintah yang sama dengan percobaan 25 sampai 27 dan catat perintahnya. Pastikan modul sendi untuk *walking* aktif dengan prosedur yang sama; percobaan 26 menunjukkan *run walking* tidak sah bila pemetaan modul sendi belum aktif.

**2.4 Adegan.** Susun bola, gawang, dan robot sehingga ketiganya terlihat pada pandangan *idle*. Catat jarak tiap objek dari kaki OP3, posisi lakban, sumber cahaya, dan simpan foto adegan dari luar serta satu *screenshot* *preview*. Bila *gait* standar membuat OP3 berpindah tempat, operator mengembalikan OP3 ke tanda lantai sebelum setiap *run* berjalan; catat hal ini di log penyimpangan.

**2.5 *Frame* referensi adegan.** Sebelum *run* pertama, saat detektor **tidak** berjalan, rekam 10 *frame* mentah:

```bash
python scripts/capture_op3_frames.py --session-id YYYYMMDD_eq_scene_ref_awal \
  --condition servo_idle --topic /thesis/image_raw \
  --max-frames 10 --interval-sec 1 --duration-sec 15
```

Ulangi dengan `--session-id YYYYMMDD_eq_scene_ref_akhir` setelah *run* terakhir. Kedua set dipakai untuk memeriksa bahwa adegan dan arah kamera tidak berubah, dan dapat dipakai pada Fase 8b. Jangan membuat pra-label dari model mana pun untuk set ini.

**2.6 Uji asap *teacher*.** Jalankan *teacher* 30 detik pada kondisi *idle* dengan *preview* aktif dan `run_id:=YYYYMMDD_eq_teacher_smoke_01`. Pastikan model termuat, tiga kelas `ball`, `gawang`, `robot` muncul pada *preview*, tidak ada *error frame*, dan JSON mencatat `checkpoint_local_override_used: true` serta hash registri *teacher*. *Run* ini tidak masuk analisis.

**TH2:** kirim ringkasan servo, kepala, adegan, *screenshot*, dan uji asap kepada Bhre. Tunggu persetujuan adegan dan arah kamera sebelum Fase 3.

### 3. Jadwal *run*

Jalankan tiga putaran. Tiap putaran terdiri atas blok *idle* (empat model) lalu blok berjalan (empat model). Urutan model digilir agar pengaruh waktu, suhu, dan kelelahan robot tersebar.

| Putaran | Blok | Urutan model |
|---|---|---|
| u1 | *idle* | `teacher`, `hybrid1337`, `sup1337`, `kd42` |
| u1 | berjalan | `kd42`, `sup1337`, `hybrid1337`, `teacher` |
| u2 | *idle* | `hybrid1337`, `kd42`, `teacher`, `sup1337` |
| u2 | berjalan | `sup1337`, `teacher`, `kd42`, `hybrid1337` |
| u3 | *idle* | `sup1337`, `teacher`, `kd42`, `hybrid1337` |
| u3 | berjalan | `hybrid1337`, `kd42`, `teacher`, `sup1337` |

Format `run_id`: `YYYYMMDD_eq_<kunci>_<idle|walk>_u<n>`, misalnya `20261024_eq_teacher_walk_u2`. Jangan memakai ulang `run_id` yang sudah ada.

Aturan tambahan:

- *Run* yang tidak sah (Fase 5) diulang di akhir blok yang sama dengan akhiran `_ulang1`. *Run* gagal tetap disimpan dan didokumentasikan dengan status `tidak sah` beserta alasannya.
- Bila sesi harus dihentikan, hentikan pada batas putaran. Putaran lengkap tetap sah; putaran yang terpotong dilaporkan sebagai parsial.
- Bila sesi terpaksa dibagi ke dua hari, pembagian dilakukan pada batas putaran, dan hari dicatat sebagai faktor di semua tabel.

### 4. Prosedur setiap *run*

**4.1 Sebelum *run*.** Pastikan jeda sejak *run* sebelumnya minimal 120 detik. Catat suhu CPU, `top -b -n 1 | head -n 25`, status manager, *publisher* kamera, dan proses penampil. Ambil sampel *telemetry* sendi awal dengan cara yang sama seperti percobaan 25 sampai 27 (`telemetry_pre_*.txt`).

**4.2 Jalankan detektor.** Satu node, `duration_s:=75` untuk kedua kondisi:

```bash
python scripts/op3_pytorch_detector.py --ros-args \
  -p input_topic:=/thesis/image_raw \
  <ARGUMEN_MODEL> \
  -p run_id:=<RUN_ID> \
  -p experiment_condition:=<servo_idle|walking> \
  -p imgsz:=640 -p confidence_threshold:=0.25 -p iou_threshold:=0.45 \
  -p enable_tracking:=true -p tracker_config:=botsort.yaml \
  -p publish_debug_image:=true \
  -p torch_num_threads:=4 -p torch_interop_threads:=2 \
  -p warmup_frames:=30 -p duration_s:=75
```

Isi `<ARGUMEN_MODEL>`:

- `teacher`: `-p model_variant:=teacher` dengan `model_path` dibiarkan kosong agar override lokal terpakai;
- `hybrid1337`: `-p model_variant:=hybrid`;
- `sup1337`: `-p model_variant:=supervised -p model_path:=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt` (varian `supervised` tanpa `model_path` akan memuat seed 42, jadi `model_path` wajib);
- `kd42`: `-p model_variant:=kd`.

Penampil SSH -X tetap terbuka pada `/vision/debug_image` sepanjang sesi dan tidak dimulai ulang antar-*run* kecuali mati; bila mati, catat sebagai penyimpangan.

**4.3 Jendela ukur.** Tentukan `t_w`, yaitu cap waktu kamera *frame* pertama dengan `is_warmup=false`.

- *Idle*: jendela ukur `[t_w + 5 s, t_w + 65 s]`. Tidak ada perintah gerak.
- Berjalan: kirim perintah *start* *gait* standar sekitar 3 detik setelah `t_w` dan catat waktu *ack*-nya (`t_g`). Jendela ukur `[t_g + 2 s, t_g + 62 s]`. Kirim *stop* *gait* pada `t_g + 63 s`. Bila `t_g` lebih dari `t_w + 10 s`, jendela tidak muat dalam `duration_s`; tandai *run* tidak sah dan ulangi.

Ambil dua sampel *telemetry* di tengah jendela (sekitar detik ke-20 dan ke-40) dan dua sampel sesudah *stop* atau sesudah jendela *idle* berakhir. Simpan perintah dan cap waktu *gait* (`gait_start_command.txt`, `gait_start_ack_utc.txt`, `gait_stop_command.txt`, `gait_stop_sent_utc.txt`).

**4.4 Sesudah jendela.** Ambil satu *screenshot* *overlay* setelah jendela ukur berakhir dan sebelum detektor selesai, dengan cara yang sama untuk semua *run*. Catat suhu CPU akhir. Biarkan detektor berhenti sendiri setelah 75 detik.

### 5. Kriteria *run* sah

Sebuah *run* sah bila seluruh syarat berikut terpenuhi:

1. Hash *checkpoint* di JSON cocok dengan tabel model.
2. Jendela ukur penuh 60 detik dan berada sepenuhnya setelah *warm-up*.
3. Tidak ada *error frame* di jendela; bila ada, catat jumlahnya dan anggap tidak sah bila lebih dari 1% *frame*.
4. Simpangan pan dan tilt ID 19/20 pada semua sampel maksimal 2 *count* dari sampel awal *run*.
5. Berjalan: sampel tengah menunjukkan perubahan sendi pinggul dan lutut, dan sampel sesudah *stop* menunjukkan sendi kaki stabil. *Idle*: sendi badan tidak berubah lebih dari 0,00307 rad.
6. *Preview* aktif sepanjang jendela (penampil hidup dan `/vision/debug_image` terbit).
7. Tidak ada proses berat lain yang tercatat di `top`.

### 6. Dokumentasi setiap pengujian

Ikuti format percobaan 26 dan 27. Gunakan nomor percobaan berikutnya yang belum terpakai (perkiraan 29) dengan folder `dokumentasi/<tanggal-mulai>/percobaan-29-uji-live-setara-empat-model/`:

```text
percobaan-29-uji-live-setara-empat-model/
  README_ID.md, README_EN.md          ringkasan sesi, protokol, hasil agregat, batas
  jadwal_run.csv                      urutan rencana dan aktual, status sah/tidak sah
  log_penyimpangan.md                 semua penyimpangan dan tindakannya
  00-persiapan/                       audit, hash, preflight servo/kepala, perintah manager,
                                      foto adegan, screenshot, frame referensi, uji asap teacher
  01-teacher/  02-kd-hybrid/  03-supervised/  04-kd-murni/
    README_ID.md, README_EN.md        ringkasan enam run model tersebut
    idle-u1/ idle-u2/ idle-u3/ berjalan-u1/ berjalan-u2/ berjalan-u3/
  05-ringkasan/                       tabel dan grafik gabungan
```

Setiap folder *run* memuat: `README_ID.md` dan `README_EN.md` (hasil, protokol, tabel performa, grafik, keluaran per kelas, kondisi robot, batas bukti, tautan artefak), `summary_metrics.json`, `tabel_performa.csv` dan `performance_table.csv`, `tabel_deteksi.csv` dan `detection_table.csv`, `jendela_runtime.csv`, `jendela_deteksi.csv`, `grafik_latensi_id.png` dan `latency_graph_en.png`, `grafik_cpu_ram_id.png` dan `cpu_ram_graph_en.png`, `grafik_keluaran_kelas_id.png` dan `class_outputs_graph_en.png`, metadata *screenshot* `live_overlay_<run_id>.json`, serta `status_kepala.csv` (Goal/Present atau *feedback* pan/tilt tiap sampel dan simpangannya). *Run* berjalan menambah berkas perintah dan cap waktu *gait*.

Tabel performa per *run* memuat **rata-rata**, median, dan P95 untuk pra-pemrosesan, inferensi, pasca-pemrosesan, dan *callback* total; FPS efektif `(jumlah frame − 1) / (t_terakhir − t_pertama)` dari cap waktu kamera dalam jendela; CPU proses (persen satu CPU logis dan persen kapasitas 16 CPU logis); RSS dalam MiB; jumlah *frame*; *error frame*; suhu CPU awal dan akhir. Rata-rata wajib ada karena rumusan masalah nomor 4 menanyakan rata-rata latensi. Jangan menghitung FPS dari `1000 / latensi`.

Keluaran per kelas (cakupan *frame*, median *confidence*, ID *tracker*) ditulis sebagai pengamatan, **bukan akurasi**, karena tidak ada *ground truth* per *frame*.

Log mentah tetap di `runs/op3_pytorch/` dan ditautkan sebagai `(lokal: ...)` seperti percobaan sebelumnya. *Screenshot* PNG, foto adegan, *frame* referensi, dan berkas *telemetry* mentah tetap lokal kecuali Bhre menyetujui publikasi.

### 7. Analisis dan tabel

Untuk setiap pasangan model dan kondisi, tampilkan ketiga ulangan lalu ringkasannya: rata-rata dan simpangan baku antarulangan untuk rata-rata latensi, FPS efektif, CPU, dan RSS, ditambah median dan P95 latensi gabungan jendela. Dengan n = 3, analisis bersifat deskriptif; jangan menulis klaim signifikansi statistik.

Hitung juga:

- selisih *idle* ke berjalan per model;
- rasio *teacher* terhadap `hybrid1337` untuk latensi, FPS, CPU, dan RSS (pembanding utama RQ4 dan RQ5);
- pembagian latensi menurut tahap (pra-pemrosesan, inferensi, pasca-pemrosesan) untuk menjelaskan apakah FPS dibatasi model atau bagian lain.

Buat tabel baru tanpa mengubah baris lama:

- **T36** `analisis_performa/tabel/T36_runtime_live_setara_per_run.{csv,md}`: satu baris per *run* sah dan tidak sah, lengkap dengan status.
- **T37** `analisis_performa/tabel/T37_runtime_live_setara_ringkasan.{csv,md}`: satu baris per model dan kondisi.
- Tambahkan baris protokol setara ke T19 dan kolom atau baris baru ke T26 dengan label `percobaan 29 (setara)`; nilai lama tetap ada dengan label protokol aslinya.

Grafik di `05-ringkasan/`: FPS per model per kondisi (titik tiap ulangan dan batang rata-rata), rata-rata dan P95 latensi, CPU, RSS, serta perbandingan *idle* dan berjalan. Perbarui `analisis_performa/INDEKS.md`, `analisis_performa/manifest.json`, dan `prompt/inventaris_tabel_dan_prompt.md`. Hapus pernyataan lama bahwa evaluasi live OP3 berada di luar hasil utama dan ganti dengan arahan baru. Bila tabel dihasilkan oleh `scripts/build_performance_tables.py`, tambahkan generator untuk T36 dan T37 tanpa mengubah keluaran tabel lama.

Bandingkan dengan percobaan 25 sampai 27 hanya secara deskriptif dan sebutkan perbedaan protokolnya.

### 8. Akurasi pada domain kamera OP3 (tanpa gerak robot)

**8a. Evaluasi *offline* empat model pada 260 *frame*.** Jalankan setelah seluruh *run* live selesai, saat robot tidak menjalankan detektor. Gunakan evaluator `op3_multi_session_eval` dengan sesi yang **identik** dengan `runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/input_manifest.json` (baca daftar sesi primer, negatif, dan parsial dari manifest itu), pengaturan yang sama, dan folder keluaran baru:

```bash
source .venv-op3-pytorch/bin/activate
PYTHONPATH="$PWD/ros2_packages/op3_camera_eval:$PWD/ros2_packages/op3_multi_session_eval" \
python -m op3_multi_session_eval \
  <--primary-session ... sesuai manifest> \
  <--negative-session ... sesuai manifest> \
  <--partial-session ... sesuai manifest> \
  --output-dir runs/op3_multi_session_eval/YYYYMMDD_empat_model_primary260_v1 \
  --models teacher=models_local/teacher_fp32_best.pt \
           hybrid=runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt \
           supervised=runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt \
           kd=models/weights/kd_student_best.pt
```

Pastikan checksum gambar dan label sama dengan manifest percobaan 28. Angka Hybrid dan *Supervised* harus sama persis dengan T34; bila berbeda, hentikan dan laporkan sebelum menulis tabel. Buat **T38** `T38_akurasi_op3_empat_model_260.{csv,md}` dan dokumentasi percobaan berikutnya (perkiraan 30). Tulis batasnya: satu rangkaian pengambilan, label awal dibantu KD murni seed 42 sehingga berpotensi menguntungkan `kd42`, dan set 50 *frame* gawang parsial tidak masuk angka utama.

**8b. Kesesuaian dengan adegan acuan (opsional, tunggu persetujuan Bhre).** Karena adegan dan arah kamera tetap, keluaran *run idle* dapat dibandingkan dengan kotak acuan yang dianotasi manual oleh Bhre dari set `YYYYMMDD_eq_scene_ref_awal` tanpa bantuan prediksi model. Laporkan proporsi *frame* yang kotaknya cocok dengan acuan pada IoU ≥ 0,5 per kelas serta jumlah kotak berlebih. Untuk *run* berjalan, laporkan hanya proporsi *frame* dengan tepat satu kotak per kelas. Sebut hasil ini "kesesuaian dengan adegan acuan", bukan mAP. Bila perlu kode baru, buat package atau skrip baru; jangan mengubah package lama. Jangan menulis kode sebelum Bhre menyetujui.

### 9. Putaran tambahan opsional: *preview* mati

Hanya bila Bhre memintanya setelah tiga putaran utama selesai: satu *run idle* per model dengan `publish_debug_image:=false` dan penampil ditutup, urutan `kd42`, `teacher`, `sup1337`, `hybrid1337`, `run_id` berakhiran `_nopreview_u1`. Tujuannya mengukur beban *preview* SSH -X. Hasilnya dilaporkan terpisah dan tidak menggantikan matriks utama.

### 10. Penutupan dan laporan

- Setelah *run* terakhir dan *frame* referensi akhir, hentikan *gait* bila masih aktif. Biarkan robot dalam kondisi yang diminta operator. Bila operator meminta *preview* pemantauan tetap menyala, jalankan dengan `run_id` terpisah dan jangan memasukkannya ke analisis.
- Tulis memory baru `memory/<tanggal>-uji-live-setara-op3.md` sesuai format folder `memory/`. Catat bahwa Bhre menetapkan uji live OP3 sebagai pengujian akhir pada 23 Oktober 2026, sehingga catatan memory 23 Oktober yang menyebut live OP3 di luar hasil utama tidak berlaku lagi.
- Laporkan kepada Bhre: daftar *run* sah dan tidak sah, tabel ringkas T37, rasio *teacher* terhadap Hybrid, penyimpangan, berkas yang dibuat, dan langkah berikutnya.
- Jangan commit atau push. Bhre yang memutuskan berkas mana yang dipublikasikan.

### Titik henti

| Kode | Kapan | Yang ditunggu |
|---|---|---|
| TH1 | Setelah audit dan hash | Persetujuan Bhre; *teacher* tersedia dan hash cocok |
| TH2 | Setelah servo, kepala, adegan, dan uji asap *teacher* | Persetujuan adegan dan arah kamera |
| TH3 | Sebelum setiap blok berjalan | Konfirmasi operator bahwa area aman, robot didampingi, dan robot di tanda lantai |
| TH4 | Setelah tiga putaran | Keputusan Bhre atas Fase 8b dan Fase 9 |
