# Laporan sesi pelengkap log OP3 — 23 November 2026

Sesi menjalankan [`prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md`](../prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md) dari laptop melalui SSH ke OP3 (`humanoid-NUC12WSHi5`, alias SSH lokal Bhre). Robot hanya dibaca. Tidak ada kamera, ROS, servo, torque, gait, training, inferensi, atau perekaman frame. Satu-satunya tulisan di robot adalah direktori kerja sementara `/tmp/op3_log_pelengkap_20261123T021748Z/`, yang dihapus setelah semua hash di laptop terverifikasi. `git status --short` repositori robot berisi 709 baris sebelum dan sesudah setiap langkah. Repositori laptop berada di commit `a4bc9b2` (mutakhir dengan `origin/main`).

**Status: semua langkah 1–22 selesai. Belum ada commit.** Pada langkah 19 sesi sempat berhenti karena `pytest` tidak ada di laptop. Bhre lalu mengizinkan pemasangan `pytest` dan menyetujui rekomendasi untuk menempatkan `timestamp` teacher sebagai waktu mulai.

## 1. Log jendela 15 run

**15 dari 15 run berhasil diekstrak; tidak ada run yang gagal.** Untuk setiap run:

- SHA-256 log mentah dan metadata sama dengan T36.
- Jumlah baris jendela sama dengan `frames` T36, dan jumlah error 0 sesuai `error_frames`.
- Rerata `end_to_end_ms` dan FPS cocok dengan T36. Selisih terbesar 1,4e-14 ms pada latensi dan 0 pada FPS, di bawah toleransi 1e-6.

Penyalinan ke laptop dilakukan sekali. Ke-30 berkas (`jendela_runtime.csv` dan `jendela_deteksi.csv`) memiliki SHA-256 yang sama dengan `status_ekstraksi.json`. Rincian per run ada di [README](README.md#log-jendela-24-run-live).

## 2. Konsistensi 9 run lama

Kesembilan run yang log jendelanya sudah ada di `dokumentasi/2026-11-02/` diekstrak ulang dengan skrip yang sama ke direktori sementara di robot. Hasilnya **identik byte demi byte untuk 9 dari 9 run**, baik `jendela_runtime.csv` maupun `jendela_deteksi.csv`, dengan berkas di repositori laptop. Hasil ekstraksi ulang tidak disalin ke `log_op3_pelengkap/`; hanya hash perbandingannya yang dicatat di `manifest_sha256.json`.

## 3. Sesi capture T38 dan T43

**T38.** `input_manifest.json` T38 merujuk 11 sesi:

- 200 frame primary dan 60 frame negatif (260 frame utama), serta 50 frame parsial.
- Dua sesi, `20261021_ball_moving_candidate_01` dan `20261021_negative_candidate_01`, adalah set kurasi, bukan capture asli.
- Frame kedua sesi kurasi ditelusuri lewat `curation_manifest.json` ke empat sesi sumber. Metadata keempat sesi sumber itu ikut disalin.
- Kondisi di manifest capture T38 tercatat `unknown`.

**T43.** `capture_260_manifest.json` merujuk 5 sesi yang dipakai (260 frame) dan 3 sesi yang dikecualikan. Hash `capture_manifest.json` kelima sesi yang dipakai cocok dengan manifest T43. Dari folder eksperimen, 14 berkas metadata disalin.

**Timestamp capture tercatat untuk semua 23 baris** [`ringkasan_capture.csv`](ringkasan_capture.csv). Sumbernya `captured_at_utc` di `capture_frames.jsonl`, dan tidak ada frame tanpa timestamp. Tidak ada timestamp yang diturunkan dari nama berkas atau waktu modifikasi. Rentangnya:

| Set | Rentang capture pertama dan terakhir (UTC) |
|---|---|
| T38 | 2026-10-21 07:09:49 sampai 10:54:07 |
| T43 (sesi yang dipakai) | 2026-11-12 05:16:17 sampai 05:30:41 |

**Yang tidak disalin:**

- Gambar (865) dan label YOLO (1.140).
- Contact sheet.
- `predictions.jsonl`, ditolak karena memuat koordinat `xywhn`/`xyxy` dan prediksi.
- `prelabel_manifest.json` dan `review_log.jsonl`, karena berada di folder label.
- `frozen_plan.json` (sudah ada di Git) dan `walk_capture_guard_v1.py` (kode).

## 4. Catatan training teacher

- **Sumber: robot.** `manifest.json`, `args.yaml`, dan `results.csv` ada di folder teacher robot, sedangkan `SHA256SUMS.txt` tidak ada. `best.pt` di `artifacts/checkpoints/fp32/` dan `.cache/hardware_models/fp32_pytorch/` tetap `e05b2b21…420b8c`.
- **Kecocokan hash.** Salinan laptop (`Progress 3`) cocok dengan hash dan ukuran pada prompt, tetapi berbeda dari salinan robot hanya karena akhir baris (CRLF di laptop, LF di robot). Setelah normalisasi, ketiga berkas identik. Sesuai prompt, salinan robot yang dipakai.
- **Arti `timestamp`** (`2026-09-02T10:04:03Z`, 17:04 WIB):
  - Menurut `scripts/step03_train_fp32.py` yang tersimpan, nilai ini diisi sebelum `model.train()` (`status: started`) dan tidak diperbarui saat status menjadi `completed`. Artinya awal training.
  - Salinan skrip bertanggal 7 Oktober 2026, sesudah training, sehingga versi yang benar-benar dipakai tidak terverifikasi.
  - Atas persetujuan Bhre, `build_jejak_waktu.py` kini menempatkannya sebagai waktu mulai. Waktu selesai dibiarkan tidak tercatat dan tidak diturunkan dari durasi.

## 5. Tes dan perubahan `jejak_waktu/` serta `bukti_kebutuhan/`

`pytest` 9.2.0 dipasang dengan `python -m pip install --user pytest` (Python 3.13) atas izin Bhre. Kedua skrip build berjalan tanpa galat.

Perintah `python -m pytest -q tests --ignore=tests/test_kd_hybrid.py` berhenti di tahap *collection* dengan 2 galat, sehingga tidak ada tes yang berjalan. Dengan `--continue-on-collection-errors`, hasilnya **28 lulus, 2 gagal, dan 2 galat**:

- **Galat:** `tests/test_continue_t42.py` dan `tests/test_continue_t42_attempt.py`. Skrip T42 untuk server mengimpor `fcntl`, modul khusus Unix.
- **Gagal:** `test_server_paths.py::test_evaluation_data_yaml_rebases_all_splits` (mendapat path `\data\av\...`, bukan `/data/av/...`) dan `test_server_paths.py::test_student_config_legacy_unchanged` (pemeriksaan akhiran path). Keduanya kemungkinan besar karena pemisah path Windows.
- **Tes yang relevan dengan sesi ini lulus:** `test_build_jejak_waktu.py` dan `test_build_bukti_kebutuhan.py` (3 tes).

Tes tidak diubah. Keempat masalah itu terkait platform laptop dan perlu dicek ulang di Linux bila diperlukan.

**Perubahan `jejak_waktu/`:**

- `timestamp_frame_live_24_run.csv`: 15 run kini bersumber dari `log_op3_pelengkap/live_24_run/`, dengan rentang timestamp kamera dan jeda rerata terisi.
- `README.md`: menyebut 24 run berlog per frame, 15 di antaranya hasil ekstraksi 23 November. Bagian "Yang masih dicari di robot" diganti "Log pelengkap dari robot". Baris teacher terisi (mulai 2026-09-02 17:04 WIB, durasi 0,94 jam, NVIDIA L40).
- `training_per_epoch.csv`: bertambah 100 baris epoch teacher, menjadi 1.000 baris.
- `kronologi_kegiatan.csv`: diperbarui, tetap 64 kegiatan.
- `garis_waktu_kegiatan_id.png` dan manifestnya dibangkitkan ulang. Hash PNG berubah karena versi pustaka laptop, dan teacher tidak digambar.

**Perubahan `bukti_kebutuhan/`:** KF-04 kini menyatakan 24/24 log jendela lengkap (sebelumnya 9/9), dan `bukti_kolom_log_jendela_repo.csv` bertambah 15 baris. `README.md`, `kasus_uji_kf_knf.csv`, dan manifest ikut diperbarui. Status KF lain tidak berubah.

**Perubahan `scripts/build_jejak_waktu.py`:**

- Penempatan `timestamp` teacher sebagai waktu mulai.
- Baris teacher tidak digambar pada grafik.
- Teks README yang bersyarat pada log yang tersedia.
- Deskripsi tabel epoch menyebut teacher bila ada.

## 6. Ukuran dan berkas baru

Ukuran `log_op3_pelengkap/`: sekitar 8,5 MB (8,1 MiB) dalam 100 berkas. Hampir seluruhnya berupa log jendela run live. Isinya:

- `live_24_run/`: 15 run dan `status_ekstraksi.json`.
- `t38_capture/`: 15 sesi.
- `t43_capture/`: 14 berkas eksperimen dan 8 sesi.
- `teacher_training/`: 3 berkas.
- `ringkasan_capture.csv`, `status_metadata.json`, `README.md`, `manifest_sha256.json`, dan laporan ini.

Berkas baru lain:

- Package `ros2_packages/op3_log_pelengkap/`, berisi README dan empat skrip pustaka standar:
  - `ekstrak_jendela.py` dan `salin_metadata.py`, yang dijalankan di robot.
  - `susun_ringkasan.py` dan `susun_dokumen.py`, yang dijalankan di laptop.
- `dokumentasi/2026-11-23/LOG_PROGRES_SKRIPSI.md` dan `memory/2026-11-23-log-op3-pelengkap.md`.
- Baris baru di README utama ("Mulai dari sini" dan baris robot pada tabel langkah) dan di `dokumentasi/INDEKS.md`.

`salin_metadata.py` dijalankan dua kali. Pada versi kedua, penelusuran sesi sumber kurasi ditambahkan, dan keluarannya identik dengan versi pertama kecuali empat sesi sumber tambahan. Tidak ada alamat IP, kata sandi, atau kunci di berkas baru.

## 7. `git status --short`

```
 M README.md
 M bukti_kebutuhan/KF-04_log_runtime/README.md
 M bukti_kebutuhan/KF-04_log_runtime/bukti_kolom_log_jendela_repo.csv
 M bukti_kebutuhan/README.md
 M bukti_kebutuhan/kasus_uji_kf_knf.csv
 M bukti_kebutuhan/manifest_bukti_sha256.json
 M dokumentasi/2026-11-13/LOG_PROGRES_SKRIPSI.md
 M dokumentasi/INDEKS.md
 M jejak_waktu/README.md
 M jejak_waktu/garis_waktu_kegiatan_id.png
 M jejak_waktu/kronologi_kegiatan.csv
 M jejak_waktu/manifest_jejak_waktu_sha256.json
 M jejak_waktu/timestamp_frame_live_24_run.csv
 M jejak_waktu/training_per_epoch.csv
 M scripts/build_jejak_waktu.py
?? "Claude outputs/"
?? dokumentasi/2026-11-23/
?? log_op3_pelengkap/
?? memory/2026-11-23-log-op3-pelengkap.md
?? ros2_packages/op3_log_pelengkap/
```

Perubahan `dokumentasi/2026-11-13/LOG_PROGRES_SKRIPSI.md` bukan milik sesi ini dan dibiarkan.

## Usulan daftar commit (menunggu persetujuan Bhre)

Semua berkas di atas, **kecuali** `"Claude outputs/"` dan `dokumentasi/2026-11-13/LOG_PROGRES_SKRIPSI.md`. Pesan commit yang diusulkan: "Add OP3 log supplement and rebuild time trace and requirement evidence".
