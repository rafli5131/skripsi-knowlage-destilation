# Prompt pelengkap log OP3 melalui SSH dari laptop

Tanggal: 23 November 2026. Dijalankan oleh agen di **laptop Bhre** (Claude Code di VS Code, folder `E:\Kuliah\Thesis\Kode program\skripsi-knowlage-destilation`) yang sudah dapat masuk ke komputer OP3 melalui SSH. Semua perintah di robot dikirim lewat SSH dari laptop. Pekerjaan ini **offline**: tanpa kamera, detektor live, servo, torque, modul, action, atau gait. Tidak ada pelatihan, inferensi, atau perekaman frame baru.

Hasil akhir disimpan di laptop, di folder repositori **`log_op3_pelengkap/`**, beserta laporan `log_op3_pelengkap/LAPORAN_SESI.md` yang akan dibaca dan ditinjau di percakapan Claude terpisah.

## Latar

- [`jejak_waktu/`](../jejak_waktu/README.md) dan [`bukti_kebutuhan/`](../bukti_kebutuhan/README.md) sudah merangkum waktu training, evaluasi, dan 24 run live. Log per frame (`jendela_runtime.csv`, `jendela_deteksi.csv`) baru tersedia di repositori untuk 9 run. Untuk 15 run lainnya, repositori hanya menyimpan hash log mentah pada kolom `raw_csv_sha256` dan `metadata_sha256` di [T36](../analisis_performa/tabel/T36_runtime_live_setara_per_run.csv).
- Manifest capture frame T38 dan T43 hanya ada di OP3.
- Teacher utama dilatih di server lab, bukan di robot. Robot menyimpan salinan bobotnya di `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt` (SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`). Folder yang sama mungkin juga berisi `manifest.json`, `args.yaml`, dan `results.csv` training teacher.
- Salinan catatan training teacher sudah ditemukan di laptop: `E:\Kuliah\SKRIPSI\Sourcecode\Progress 3\artifacts\checkpoints\fp32\`.
- `scripts/build_jejak_waktu.py` dan `scripts/build_bukti_kebutuhan.py` otomatis membaca `log_op3_pelengkap/live_24_run/<run_id>/jendela_runtime.csv` dan `log_op3_pelengkap/teacher_training/` bila folder itu ada.

## Izin dan larangan

- Bhre meminta log jendela run live, manifest capture (metadata saja), dan berkas teks training teacher disimpan ke `log_op3_pelengkap/` di repositori laptop. Izin ini **tidak** mencakup gambar, video, label, prediksi per frame T38/T43, bobot model (`*.pt`), atau log mentah penuh di luar jendela ukur.
- Di robot, perintah SSH hanya boleh membaca berkas, menghitung hash, dan menulis ke satu direktori kerja sementara baru, misalnya `/tmp/op3_log_pelengkap_<YYYYmmddTHHMMSSZ>/`. Jangan menulis, memindahkan, atau menghapus apa pun di repositori robot (`/home/humanoid/bre_skripsi`), `runs/`, `data/`, atau folder teacher. Jangan menjalankan `git` yang mengubah repositori robot.
- Tidak ada perintah gerak, kamera, ROS launch, atau detektor live melalui SSH. Bila suatu langkah tampak membutuhkannya, berhenti dan laporkan.
- Jangan mengubah hasil beku T36, T37, T38, T43, T44, dan T45 di repositori laptop. Bila `log_op3_pelengkap/` sudah ada di laptop, berhenti dan laporkan.
- Kode baru dibuat di repositori laptop sebagai package baru `ros2_packages/op3_log_pelengkap/`, lalu disalin ke direktori kerja sementara di robot untuk dijalankan. Package lama hanya dipakai sebagai acuan atau fungsi bersama tanpa diubah.
- Jangan memasang paket baru di robot maupun di laptop tanpa izin Bhre. Skrip ekstraksi di robot cukup memakai pustaka standar Python.
- Jangan menyimpan kata sandi, kunci, atau alamat IP robot di berkas yang masuk Git. Gunakan alias SSH yang sudah dikonfigurasi Bhre.
- Bila hash tidak cocok atau berkas tidak ditemukan, catat apa adanya. Jangan mengganti dengan berkas lain, jangan merekonstruksi data, dan jangan menebak.
- *Commit* dan *push* dari laptop hanya setelah Bhre menyetujui daftar berkas.

## Persiapan di laptop

1. Di repositori laptop: `git status --short`, lalu `git pull --ff-only origin main` bila tidak ada konflik. Perubahan lama yang bukan milik sesi ini (misalnya `dokumentasi/2026-11-13/LOG_PROGRES_SKRIPSI.md`) dibiarkan.
2. Baca `agent.md`, [`jejak_waktu/README.md`](../jejak_waktu/README.md), `jejak_waktu/timestamp_frame_live_24_run.csv`, [`bukti_kebutuhan/KF-04_log_runtime/README.md`](../bukti_kebutuhan/KF-04_log_runtime/README.md), `analisis_performa/tabel/T36_runtime_live_setara_per_run.csv`, serta fungsi `summarize` dan `write_run_details` di `ros2_packages/op3_equal_live_report/op3_equal_live_report/report.py`.
3. Tanyakan kepada Bhre alias SSH robot bila belum jelas, lalu uji dengan `ssh <alias> 'hostname; whoami; ls -d /home/humanoid/bre_skripsi'`. Hostname yang diharapkan `humanoid-NUC12WSHi5`. Bila gagal, berhenti dan laporkan.
4. Daftar run sasaran adalah baris `jejak_waktu/timestamp_frame_live_24_run.csv` yang kolom `sumber`-nya diawali `OP3:` (seharusnya 15 run). Buat juga daftar 9 run lain untuk pemeriksaan konsistensi.

## Bagian A. Log jendela 15 run live

5. Tulis skrip `ros2_packages/op3_log_pelengkap/ekstrak_jendela.py` (pustaka standar Python saja). Masukannya: daftar `run_id` beserta `window_start_utc`, `window_end_utc`, `frames`, `error_frames`, `latency_mean_ms`, `fps`, `raw_csv_sha256`, dan `metadata_sha256` dari T36; keluarannya ditulis ke direktori kerja sementara. Untuk setiap run, skrip:
   - mencari `runs/op3_pytorch/<run_id>.csv`, `<run_id>_detections.csv`, dan `<run_id>.json` di repositori robot; bila tidak ada, mencatat lokasi hasil `find /home/humanoid -name '<run_id>*'` tanpa memakainya sebelum hash dicek;
   - menghitung SHA-256 log mentah dan metadata; nilainya **wajib** sama dengan T36, bila tidak, run dilewati dan statusnya dicatat;
   - mengambil baris dengan `receive_time_utc` di antara `window_start_utc` dan `window_end_utc` T36 (inklusif) ke `live_24_run/<run_id>/jendela_runtime.csv`, dengan kolom dan urutan kolom yang sama seperti log mentah, akhir baris LF;
   - mengambil baris log deteksi yang `frame_index`-nya ada di jendela ke `jendela_deteksi.csv`, sama dengan `write_run_details`;
   - memeriksa: jumlah baris jendela sama dengan `frames` T36; jumlah baris dengan kolom `error` terisi sama dengan `error_frames`; rerata `end_to_end_ms` pada baris tanpa error sama dengan `latency_mean_ms` pada toleransi 1e-6; FPS `(n - 1) × 1e9 / (capture_stamp_ns terakhir - capture_stamp_ns pertama)` pada baris tanpa error sama dengan `fps` pada toleransi 1e-6. Bila ada yang gagal, berkas jendela run itu tidak dipakai dan selisihnya dicatat;
   - menulis `status_ekstraksi.json` berisi status, hasil pemeriksaan, path sumber, dan SHA-256 setiap berkas sumber dan keluaran.
6. Salin skrip ke robot (`scp` ke direktori kerja sementara), jalankan dengan `ssh <alias> 'cd /home/humanoid/bre_skripsi && python3 <dir_sementara>/ekstrak_jendela.py ...'`, lalu salin keluaran kembali ke laptop dengan `scp -r` ke `log_op3_pelengkap/live_24_run/`.
7. Di laptop, hitung ulang SHA-256 berkas yang diterima dan cocokkan dengan `status_ekstraksi.json`. Bila berbeda, ulangi penyalinan sekali; bila masih berbeda, berhenti dan laporkan.
8. Pemeriksaan konsistensi: jalankan ekstraksi yang sama untuk 9 run yang log jendelanya sudah ada di `dokumentasi/2026-11-02/`, tetapi simpan hasilnya hanya di direktori kerja sementara. Bandingkan hash atau isinya dengan berkas di repositori laptop dan laporkan apakah identik. Jangan menyalin 9 run ini ke `log_op3_pelengkap/`.

## Bagian B. Manifest capture T38 dan T43 (metadata saja)

9. **T38.** Melalui SSH, baca manifest di `runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/` untuk menentukan sesi capture yang menyusun 260 frame T38 dan 50 frame parsial. Untuk setiap sesi di `data/op3_camera_eval/sessions/<session_id>/`, daftar berkasnya, lalu salin ke laptop hanya berkas metadata (`*.json`, `*.csv`, `*.txt` yang berisi manifest, daftar frame, waktu capture, atau kurasi) ke `log_op3_pelengkap/t38_capture/<session_id>/`. Jangan menyalin gambar, contact sheet, atau label.
10. **T43.** Dari `data/op3_camera_eval/experiments/t43_20261112/`, salin hanya metadata, misalnya `capture_260_manifest.json`, `review_260_audit_and_frozen_hashes.json`, dan `blind_review_52/selection_manifest.json`, beserta manifest sesi capture yang dirujuknya, ke `log_op3_pelengkap/t43_capture/`. `frozen_plan.json` sudah ada di Git dan tidak perlu disalin.
11. Sebelum menyalin, periksa isi setiap berkas melalui SSH (`head`, `python3 -c` dengan `json`). Bila berkas memuat koordinat kotak label, prediksi per frame, atau data gambar tersandi, jangan disalin; catat namanya sebagai "tidak disalin karena memuat label atau prediksi".
12. Buat `log_op3_pelengkap/ringkasan_capture.csv` di laptop dengan satu baris per sesi: set (T38 atau T43), `session_id`, kondisi bila tercatat, jumlah frame, timestamp capture pertama dan terakhir (UTC) bila tercatat, berkas sumber, dan SHA-256. Bila timestamp tidak tercatat di manifest, isi `tidak tercatat`; jangan menurunkannya dari nama berkas atau waktu modifikasi tanpa menandainya.

## Bagian C. Catatan training teacher

13. Melalui SSH, jalankan `ls -la` dan `sha256sum` pada `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/` dan `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/.cache/hardware_models/fp32_pytorch/`. Pastikan `best.pt` tetap `e05b2b21...420b8c`.
14. Bila di robot ada `manifest.json`, `args.yaml`, `results.csv`, atau `SHA256SUMS.txt`, salin hanya berkas teks tersebut ke `log_op3_pelengkap/teacher_training/`. Jangan menyalin berkas `.pt`.
15. Bandingkan dengan salinan di laptop (`E:\Kuliah\SKRIPSI\Sourcecode\Progress 3\artifacts\checkpoints\fp32\`), yang SHA-256-nya:
    - `manifest.json`: `24eed5d04ed889ab77ff8358d8ed68231a9579a4a9e5d955057c7917f26d6ff7` (962 bait)
    - `args.yaml`: `d2224eddf47a8688901cb62018dffe539d47045d737d7cdcfbb795ca30a5c6af` (1.928 bait)
    - `results.csv`: `1d36be98bf65273f6d9f6e3b7295c72190dda4f218eefd4a671b5b80dff284bf` (12.788 bait)

    Bila berkas di robot tidak ada, salin ketiga berkas dari folder laptop tersebut ke `log_op3_pelengkap/teacher_training/` dan catat bahwa sumbernya laptop. Bila hash robot dan laptop berbeda, periksa apakah perbedaannya hanya akhir baris (CRLF atau LF) dan laporkan; pakai salinan robot bila isinya sama.
16. Catat apakah `timestamp` pada `manifest.json` teacher menandai awal atau akhir training. Periksa skrip training lama bila ada di robot atau di `E:\Kuliah\SKRIPSI\Sourcecode\Progress 3\` (cari `"timestamp"`). Bila tidak dapat dipastikan, tulis "tidak dapat dipastikan".

## Bagian D. README, manifest, dan pembaruan rangkuman (di laptop)

17. Tulis `log_op3_pelengkap/README.md` dalam Bahasa Indonesia:
    - tujuan folder dan batas isinya (tanpa gambar, label, prediksi, atau bobot);
    - tabel 24 run: `run_id`, model, kondisi, ulangan, status (sudah ada di repositori, diekstrak, hash tidak cocok, tidak ditemukan), jumlah baris, dan hasil pemeriksaan langkah 5;
    - tabel sesi capture T38 dan T43 dari `ringkasan_capture.csv`;
    - status catatan training teacher dan hasil langkah 15 dan 16;
    - daftar berkas yang sengaja tidak disalin beserta alasannya.
18. Tulis `log_op3_pelengkap/manifest_sha256.json`: path sumber di robot atau laptop beserta SHA-256-nya, SHA-256 setiap berkas keluaran, commit repositori laptop, hostname robot, waktu UTC, dan SHA-256 skrip package baru.
19. Di laptop, jalankan:

    ```bash
    python scripts/build_jejak_waktu.py --replace
    python scripts/build_bukti_kebutuhan.py --replace
    python -m pytest -q tests --ignore=tests/test_kd_hybrid.py
    ```

    Bila Python laptop belum memiliki `matplotlib`, `PyYAML`, `numpy`, atau `pytest`, berhenti dan tanyakan kepada Bhre; jangan memasang tanpa izin. Periksa bahwa `jejak_waktu/README.md` menyebut log per frame untuk run yang berhasil diekstrak dan baris teacher terisi, serta bahwa KF-04 di `bukti_kebutuhan/` menghitung log jendela tambahan. Bila tes gagal, laporkan tanpa mengubah tes.

    Catatan: PNG yang dibangkitkan di laptop boleh berbeda hash dari versi sebelumnya karena versi pustaka berbeda; manifest yang baru akan mencatat hash terbarunya.
20. Tambahkan:
    - `dokumentasi/<tanggal>/LOG_PROGRES_SKRIPSI.md` (tanggal sesi) berisi ringkasan hasil dan berkas yang tidak ditemukan;
    - `memory/<tanggal>-log-op3-pelengkap.md` dengan ringkasan singkat dan rujukan ke folder;
    - satu baris di bagian "Mulai dari sini" README utama yang menautkan `log_op3_pelengkap/README.md`, serta pembaruan baris robot pada tabel langkah berikutnya;
    - tautan di `dokumentasi/INDEKS.md`.
21. Hapus direktori kerja sementara di robot yang dibuat sesi ini saja (`rm -r /tmp/op3_log_pelengkap_<...>`), setelah semua hash di laptop terverifikasi. Jangan menghapus berkas lain.

## Laporan

22. Tulis `log_op3_pelengkap/LAPORAN_SESI.md` dalam Bahasa Indonesia, lalu tampilkan isinya kepada Bhre:
    - jumlah run yang berhasil diekstrak dari 15, serta run yang gagal beserta alasannya;
    - hasil pemeriksaan konsistensi 9 run lama;
    - sesi capture T38 dan T43 yang ditemukan, serta apakah timestamp capture tercatat;
    - status catatan training teacher, sumbernya (robot atau laptop), dan kecocokan hash;
    - hasil tes dan ringkasan perubahan `jejak_waktu/` serta `bukti_kebutuhan/`;
    - ukuran total `log_op3_pelengkap/`;
    - keluaran `git status --short`.

    Setelah itu tanyakan kepada Bhre berkas mana yang boleh di-*commit* dan di-*push*. Jangan *commit* sebelum ada jawaban.
