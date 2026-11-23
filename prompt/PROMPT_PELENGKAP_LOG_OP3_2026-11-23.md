# Prompt sesi OP3 offline: pelengkap log live, manifest capture T38/T43, dan catatan training teacher

Tanggal: 23 November 2026. Dijalankan oleh agen di **komputer OP3** (`/home/humanoid/bre_skripsi`), karena log mentah run live, manifest capture, dan salinan bobot teacher tersimpan lokal di sana. Pekerjaan ini **offline**: tanpa kamera, detektor live, servo, torque, modul, action, atau gait. Tidak ada pelatihan, inferensi, atau perekaman frame baru.

Semua hasil disimpan di satu folder baru di repositori: **`log_op3_pelengkap/`**.

## Latar

- [`jejak_waktu/`](../jejak_waktu/README.md) dan [`bukti_kebutuhan/`](../bukti_kebutuhan/README.md) sudah merangkum waktu training, evaluasi, dan 24 run live. Log per frame (`jendela_runtime.csv`, `jendela_deteksi.csv`) baru tersedia di repositori untuk 9 run. Untuk 15 run lainnya, repositori hanya menyimpan hash log mentah pada kolom `raw_csv_sha256` dan `metadata_sha256` di [T36](../analisis_performa/tabel/T36_runtime_live_setara_per_run.csv).
- Manifest capture frame T38 dan T43 hanya ada di OP3.
- Teacher utama dilatih di server lab, bukan di robot. Robot menyimpan salinan bobotnya di `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt` (SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`). Folder yang sama mungkin juga berisi `manifest.json`, `args.yaml`, dan `results.csv` training teacher.
- `scripts/build_jejak_waktu.py` dan `scripts/build_bukti_kebutuhan.py` sudah otomatis membaca `log_op3_pelengkap/live_24_run/<run_id>/jendela_runtime.csv` dan `log_op3_pelengkap/teacher_training/` bila folder itu ada.

## Izin dan larangan

- Bhre meminta log jendela run live, manifest capture (metadata saja), dan berkas teks training teacher disimpan ke `log_op3_pelengkap/`. Izin ini **tidak** mencakup gambar, video, label, prediksi per frame T38/T43, bobot model (`*.pt`), atau log mentah penuh di luar jendela ukur.
- Tidak ada perintah gerak, kamera, atau detektor live. Bila suatu langkah tampak membutuhkannya, berhenti dan laporkan.
- Jangan mengubah, memindahkan, atau menimpa log mentah, manifest, frame, label, atau hasil beku T36, T37, T38, T43, T44, dan T45. Semua keluaran baru ditulis ke `log_op3_pelengkap/`. Bila folder itu sudah ada, berhenti dan laporkan.
- Kode baru dibuat sebagai package baru `ros2_packages/op3_log_pelengkap/`. Package lama, misalnya `op3_equal_live_report`, hanya dipakai sebagai fungsi bersama tanpa diubah.
- Jangan memasang paket baru tanpa izin Bhre.
- Bila hash tidak cocok atau berkas tidak ditemukan, catat apa adanya. Jangan mengganti dengan berkas lain, jangan merekonstruksi data, dan jangan menebak.
- *Commit* dan *push* hanya setelah Bhre menyetujui daftar berkas yang akan masuk Git.

## Persiapan

1. `git status --short`; bila bersih, `git pull --ff-only origin main`. Bila ada perubahan lokal, berhenti dan laporkan.
2. Baca `agent.md`, [`jejak_waktu/README.md`](../jejak_waktu/README.md), `jejak_waktu/timestamp_frame_live_24_run.csv`, [`bukti_kebutuhan/KF-04_log_runtime/README.md`](../bukti_kebutuhan/KF-04_log_runtime/README.md), `analisis_performa/tabel/T36_runtime_live_setara_per_run.csv`, dan fungsi `summarize` serta `write_run_details` di `ros2_packages/op3_equal_live_report/op3_equal_live_report/report.py`.
3. Daftar run sasaran adalah baris `timestamp_frame_live_24_run.csv` yang kolom `sumber`-nya diawali `OP3:` (seharusnya 15 run: supervised dan KD murni pada kedua kondisi, serta Hybrid berjalan).

## Bagian A. Log jendela 15 run live

Untuk setiap run sasaran:

4. Cari log mentah `runs/op3_pytorch/<run_id>.csv`, log deteksi `runs/op3_pytorch/<run_id>_detections.csv`, dan metadata `runs/op3_pytorch/<run_id>.json`. Bila tidak ada di lokasi itu, cari dengan `find /home/humanoid -name '<run_id>*' 2>/dev/null` dan catat lokasi yang ditemukan.
5. Hitung SHA-256 log mentah dan metadata. Nilainya **wajib** sama dengan `raw_csv_sha256` dan `metadata_sha256` pada T36. Bila berbeda atau tidak ada, catat statusnya dan lewati run tersebut.
6. Ambil baris log mentah dengan `receive_time_utc` di antara `window_start_utc` dan `window_end_utc` T36 (inklusif). Tulis ke `log_op3_pelengkap/live_24_run/<run_id>/jendela_runtime.csv` dengan kolom dan urutan kolom yang sama seperti log mentah, akhir baris LF.
7. Ambil baris log deteksi yang `frame_index`-nya ada di jendela tersebut, sama dengan `write_run_details`. Tulis ke `jendela_deteksi.csv` di folder yang sama.
8. Pemeriksaan wajib per run:
   - jumlah baris jendela sama dengan `frames` T36;
   - jumlah baris dengan kolom `error` terisi sama dengan `error_frames` T36;
   - rerata `end_to_end_ms` pada baris tanpa error sama dengan `latency_mean_ms` T36 pada toleransi 1e-6;
   - FPS efektif `(n - 1) × 1e9 / (capture_stamp_ns terakhir - capture_stamp_ns pertama)` pada baris tanpa error sama dengan `fps` T36 pada toleransi 1e-6 (rumus yang sama dengan `summarize`).

   Bila salah satu gagal, hapus hanya berkas jendela run itu yang baru dibuat di `log_op3_pelengkap/`, catat selisihnya, dan lanjutkan ke run berikutnya.
9. Sebagai pemeriksaan konsistensi, lakukan langkah 6 sampai 8 juga untuk 9 run yang log jendelanya sudah ada di `dokumentasi/2026-11-02/` dan bandingkan hasilnya dengan berkas di repositori. Jangan menyalin ulang 9 run tersebut; cukup laporkan apakah identik.

## Bagian B. Manifest capture T38 dan T43 (metadata saja)

10. **T38.** Dari `runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/` (manifest input, `results.json`, dan berkas pendukungnya), tentukan sesi capture yang menyusun 260 frame T38 dan 50 frame parsial. Untuk setiap sesi di `data/op3_camera_eval/sessions/<session_id>/`, salin hanya berkas metadata (`*.json`, `*.csv`, `*.txt` yang berisi manifest, daftar frame, waktu capture, atau kurasi) ke `log_op3_pelengkap/t38_capture/<session_id>/`. Jangan menyalin gambar, contact sheet, atau label.
11. **T43.** Dari `data/op3_camera_eval/experiments/t43_20261112/`, salin hanya metadata, misalnya `capture_260_manifest.json`, `review_260_audit_and_frozen_hashes.json`, dan `blind_review_52/selection_manifest.json`, beserta manifest sesi capture yang dirujuknya, ke `log_op3_pelengkap/t43_capture/`. `frozen_plan.json` sudah ada di Git dan tidak perlu disalin.
12. Sebelum menyalin, periksa isi setiap berkas. Bila sebuah berkas memuat koordinat kotak label, prediksi per frame, atau data gambar tersandi, jangan disalin; catat namanya di README sebagai "tidak disalin karena memuat label atau prediksi".
13. Buat `log_op3_pelengkap/ringkasan_capture.csv` dengan satu baris per sesi: set (T38 atau T43), `session_id`, kondisi bila tercatat, jumlah frame, timestamp capture pertama dan terakhir (UTC) bila tercatat, berkas sumber, dan SHA-256. Bila timestamp tidak tercatat di manifest, isi `tidak tercatat`; jangan menurunkannya dari nama berkas atau waktu modifikasi tanpa menandainya.

## Bagian C. Catatan training teacher di OP3

14. Daftar isi `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/` dan `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/.cache/hardware_models/fp32_pytorch/` (`ls -la`), lalu hitung SHA-256 semua berkas di dalamnya. Pastikan `best.pt` tetap `e05b2b21...420b8c`.
15. Bila ada `manifest.json`, `args.yaml`, `results.csv`, atau `SHA256SUMS.txt`, salin **hanya berkas teks tersebut** ke `log_op3_pelengkap/teacher_training/`. Jangan menyalin berkas `.pt`.
16. Bandingkan dengan salinan yang ditemukan di laptop Bhre (`E:\Kuliah\SKRIPSI\Sourcecode\Progress 3\artifacts\checkpoints\fp32\`). SHA-256 di laptop:
    - `manifest.json`: `24eed5d04ed889ab77ff8358d8ed68231a9579a4a9e5d955057c7917f26d6ff7` (962 bait)
    - `args.yaml`: `d2224eddf47a8688901cb62018dffe539d47045d737d7cdcfbb795ca30a5c6af` (1.928 bait)
    - `results.csv`: `1d36be98bf65273f6d9f6e3b7295c72190dda4f218eefd4a671b5b80dff284bf` (12.788 bait)

    Bila hash berbeda, periksa apakah perbedaannya hanya akhir baris (CRLF atau LF) dengan membandingkan isi setelah normalisasi, lalu laporkan. Bila berkas tidak ada di OP3, tulis "tidak ditemukan di OP3" di README; Bhre dapat menyalinnya dari laptop pada sesi terpisah.
17. Catat apakah `timestamp` pada `manifest.json` teacher menandai awal atau akhir training. Periksa skrip training lama bila tersedia di OP3 (misalnya cari `"timestamp"` di folder proyek `skripsi-yolo11-op3`). Bila tidak dapat dipastikan, tulis "tidak dapat dipastikan".

## Bagian D. README, manifest, dan pembaruan rangkuman

18. Tulis `log_op3_pelengkap/README.md` dalam Bahasa Indonesia:
    - tujuan folder dan batas isinya (tanpa gambar, label, prediksi, atau bobot);
    - tabel 24 run: `run_id`, model, kondisi, ulangan, status (sudah ada di repositori, diekstrak, hash tidak cocok, tidak ditemukan), jumlah baris, dan hasil pemeriksaan langkah 8;
    - tabel sesi capture T38 dan T43 dari `ringkasan_capture.csv`;
    - status catatan training teacher dan hasil langkah 16 dan 17;
    - daftar berkas yang sengaja tidak disalin beserta alasannya.
19. Tulis `log_op3_pelengkap/manifest_sha256.json`: path sumber di OP3 beserta SHA-256-nya, SHA-256 setiap berkas keluaran, commit repositori, waktu UTC, dan SHA-256 skrip package baru.
20. Jalankan:

    ```bash
    python3 scripts/build_jejak_waktu.py --replace
    python3 scripts/build_bukti_kebutuhan.py --replace
    python3 -m pytest -q tests
    ```

    Periksa bahwa `jejak_waktu/README.md` menyebut log per frame untuk run yang berhasil diekstrak, dan bahwa KF-04 di `bukti_kebutuhan/` menghitung log jendela tambahan. Bila tes gagal, laporkan tanpa mengubah tes.
21. Tambahkan:
    - `dokumentasi/<tanggal>/LOG_PROGRES_SKRIPSI.md` (tanggal sesi) berisi ringkasan hasil dan berkas yang tidak ditemukan;
    - `memory/<tanggal>-log-op3-pelengkap.md` dengan ringkasan singkat dan rujukan ke folder;
    - satu baris di bagian "Mulai dari sini" README utama yang menautkan `log_op3_pelengkap/README.md`, serta pembaruan baris robot pada tabel langkah berikutnya;
    - tautan di `dokumentasi/INDEKS.md`.

## Laporan kepada Bhre

22. Laporkan dalam Bahasa Indonesia:
    - jumlah run yang berhasil diekstrak dari 15, serta run yang gagal beserta alasannya;
    - hasil pemeriksaan konsistensi 9 run lama;
    - sesi capture T38 dan T43 yang ditemukan, serta apakah timestamp capture tercatat;
    - status catatan training teacher dan kecocokannya dengan salinan laptop;
    - ukuran total `log_op3_pelengkap/`;
    - `git status --short`, lalu tanyakan berkas mana yang boleh di-*commit* dan di-*push*.
