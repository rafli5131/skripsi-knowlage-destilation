# Log OP3 pelengkap (23 November 2026)

Folder ini melengkapi log yang sebelumnya hanya tersimpan di komputer OP3. Isinya diambil lewat SSH dari laptop dengan package [`op3_log_pelengkap`](../ros2_packages/op3_log_pelengkap/README.md) mengikuti [prompt 23 November](../prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md). Robot hanya dibaca: tidak ada kamera, ROS, servo, gait, training, inferensi, atau perekaman frame baru, dan repositori robot tidak diubah.

**Batas isi:** log jendela ukur 60 detik, metadata capture, dan berkas teks training teacher. Gambar, video, label, prediksi per frame, bobot model (`*.pt`), dan log mentah penuh di luar jendela ukur tidak disalin.

| Isi | Keterangan |
|---|---|
| [`live_24_run/`](live_24_run/) | `jendela_runtime.csv` dan `jendela_deteksi.csv` 15 run, serta [`status_ekstraksi.json`](live_24_run/status_ekstraksi.json) |
| [`t38_capture/`](t38_capture/) | Metadata 11 sesi capture T38 dan 4 sesi sumber kurasi |
| [`t43_capture/`](t43_capture/) | Metadata eksperimen T43 dan 8 sesi capture (`sesi/`) |
| [`teacher_training/`](teacher_training/) | `manifest.json`, `args.yaml`, dan `results.csv` training teacher |
| [`ringkasan_capture.csv`](ringkasan_capture.csv) | Satu baris per sesi capture |
| [`status_metadata.json`](status_metadata.json) | Daftar berkas disalin dan tidak disalin beserta SHA-256 |
| [`manifest_sha256.json`](manifest_sha256.json) | SHA-256 sumber dan keluaran, commit, hostname, dan waktu |
| [`LAPORAN_SESI.md`](LAPORAN_SESI.md) | Laporan sesi |

## Log jendela 24 run live

15 dari 15 run yang sebelumnya hanya ada di OP3 berhasil diekstrak. SHA-256 log mentah dan metadata setiap run sama dengan T36. Baris diambil bila `receive_time_utc` berada di jendela T36 (inklusif), dengan kolom dan urutan kolom log mentah dan akhir baris LF. Jumlah baris, jumlah error, rerata `end_to_end_ms`, dan FPS `(n - 1) × 1e9 / (capture_stamp_ns terakhir - pertama)` dicocokkan dengan T36 pada toleransi 1e-6. Sebagai kontrol, 9 run yang log jendelanya sudah ada di repositori diekstrak ulang dengan skrip yang sama; 9 dari 9 identik byte demi byte untuk `jendela_runtime.csv` dan `jendela_deteksi.csv`. Hasil ekstraksi ulang itu tidak disalin ke folder ini.

| run_id | Model | Kondisi | Ulangan | Status | Baris jendela (T36) | Pemeriksaan langkah 5 |
|---|---|---|---:|---|---:|---|
| `20261102_eq_teacher_idle_u1` | Teacher YOLO11n | diam | 1 | sudah ada di repositori; ekstraksi ulang identik | 584 (584) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_teacher_idle_u2` | Teacher YOLO11n | diam | 2 | sudah ada di repositori; ekstraksi ulang identik | 614 (614) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_teacher_idle_u3` | Teacher YOLO11n | diam | 3 | sudah ada di repositori; ekstraksi ulang identik | 581 (581) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_hybrid1337_idle_u1` | KD Hybrid seed 1337 | diam | 1 | sudah ada di repositori; ekstraksi ulang identik | 792 (792) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_hybrid1337_idle_u2` | KD Hybrid seed 1337 | diam | 2 | sudah ada di repositori; ekstraksi ulang identik | 825 (825) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_hybrid1337_idle_u3` | KD Hybrid seed 1337 | diam | 3 | sudah ada di repositori; ekstraksi ulang identik | 830 (830) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_sup1337_idle_u1_ulang2` | Supervised seed 1337 | diam | 1 | diekstrak | 719 (719) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_sup1337_idle_u2` | Supervised seed 1337 | diam | 2 | diekstrak | 749 (749) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_sup1337_idle_u3_ulang1` | Supervised seed 1337 | diam | 3 | diekstrak | 717 (717) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_kd42_idle_u1` | KD murni seed 42 | diam | 1 | diekstrak | 728 (728) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_kd42_idle_u2` | KD murni seed 42 | diam | 2 | diekstrak | 721 (721) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_kd42_idle_u3` | KD murni seed 42 | diam | 3 | diekstrak | 723 (723) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_teacher_walk_u3` | Teacher YOLO11n | berjalan | 1 | sudah ada di repositori; ekstraksi ulang identik | 589 (589) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_teacher_walk_retest_u2` | Teacher YOLO11n | berjalan | 2 | sudah ada di repositori; ekstraksi ulang identik | 585 (585) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261102_eq_teacher_walk_retest_u3` | Teacher YOLO11n | berjalan | 3 | sudah ada di repositori; ekstraksi ulang identik | 604 (604) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_hybrid1337_walk_u1` | KD Hybrid seed 1337 | berjalan | 1 | diekstrak | 772 (772) | hash cocok; baris dan error sama; Δ latensi -1,4e-14 ms; Δ FPS 0,0e+00 |
| `20261103_eq_hybrid1337_walk_u2` | KD Hybrid seed 1337 | berjalan | 2 | diekstrak | 758 (758) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_hybrid1337_walk_u3` | KD Hybrid seed 1337 | berjalan | 3 | diekstrak | 726 (726) | hash cocok; baris dan error sama; Δ latensi 1,4e-14 ms; Δ FPS 0,0e+00 |
| `20261103_eq_sup1337_walk_u1` | Supervised seed 1337 | berjalan | 1 | diekstrak | 742 (742) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_sup1337_walk_u2` | Supervised seed 1337 | berjalan | 2 | diekstrak | 794 (794) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_sup1337_walk_u3` | Supervised seed 1337 | berjalan | 3 | diekstrak | 739 (739) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_kd42_walk_u1` | KD murni seed 42 | berjalan | 1 | diekstrak | 725 (725) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_kd42_walk_u2` | KD murni seed 42 | berjalan | 2 | diekstrak | 731 (731) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |
| `20261103_eq_kd42_walk_u3_ulang1` | KD murni seed 42 | berjalan | 3 | diekstrak | 742 (742) | hash cocok; baris dan error sama; Δ latensi 0,0e+00 ms; Δ FPS 0,0e+00 |

## Sesi capture T38 dan T43

Waktu capture berasal dari `captured_at_utc` di `capture_frames.jsonl`. Dua sesi T38 (`20261021_ball_moving_candidate_01` dan `20261021_negative_candidate_01`) adalah set kurasi, bukan capture asli; waktunya ditelusuri lewat `curation_manifest.json` (`source_session`, `source_image`) ke jurnal sesi sumber, yang metadatanya ikut disalin. Untuk sesi yang dipakai, rentang waktu hanya mencakup frame yang dipakai T38/T43; untuk sesi sumber dan sesi yang dikecualikan, rentang mencakup semua frame sesi. Kondisi `unknown` pada T38 berasal dari manifest capture. Hash `capture_manifest.json` kelima sesi T43 cocok dengan `capture_260_manifest.json`.

| Set | Sesi | Peran | Kondisi | Frame dipakai | Frame capture | Capture pertama (UTC) | Capture terakhir (UTC) | Sumber timestamp |
|---|---|---|---|---:|---:|---|---|---|
| T38 | `20261021_robot_ball_01` | primary | unknown | 40 | 40 | 2026-10-21T07:24:49 | 2026-10-21T07:25:41 | capture_frames.jsonl |
| T38 | `20261021_robot_gawang_01` | primary | unknown | 40 | 40 | 2026-10-21T07:33:59 | 2026-10-21T07:34:53 | capture_frames.jsonl |
| T38 | `20261021_robot_ball_moving_01` | primary | unknown | 40 | 40 | 2026-10-21T10:31:04 | 2026-10-21T10:31:45 | capture_frames.jsonl |
| T38 | `20261021_ball_moving_candidate_01` | primary | unknown | 40 | 40 | 2026-10-21T10:36:52 | 2026-10-21T10:39:16 | curation_manifest.json -> capture_frames.jsonl sesi sumber |
| T38 | `20261021_all_three_position_01` | primary | unknown | 10 | 10 | 2026-10-21T10:45:26 | 2026-10-21T10:45:36 | capture_frames.jsonl |
| T38 | `20261021_all_three_position_02` | primary | unknown | 10 | 10 | 2026-10-21T10:46:46 | 2026-10-21T10:46:56 | capture_frames.jsonl |
| T38 | `20261021_all_three_position_03` | primary | unknown | 10 | 10 | 2026-10-21T10:48:10 | 2026-10-21T10:48:22 | capture_frames.jsonl |
| T38 | `20261021_all_three_position_04` | primary | unknown | 10 | 10 | 2026-10-21T10:49:19 | 2026-10-21T10:49:28 | capture_frames.jsonl |
| T38 | `20261021_negative_candidate_01` | negative | unknown | 60 | 60 | 2026-10-21T07:09:49 | 2026-10-21T07:14:38 | curation_manifest.json -> capture_frames.jsonl sesi sumber |
| T38 | `20261021_gawang_ball_01` | partial | unknown | 40 | 40 | 2026-10-21T07:38:51 | 2026-10-21T07:39:36 | capture_frames.jsonl |
| T38 | `20261021_all_three_position_05` | partial | unknown | 10 | 10 | 2026-10-21T10:53:52 | 2026-10-21T10:54:07 | capture_frames.jsonl |
| T38 | `20261021_ball_moving_01` | sumber_kurasi:20261021_ball_moving_candidate_01 | unknown | 0 | 40 | 2026-10-21T10:36:52 | 2026-10-21T10:37:48 | capture_frames.jsonl (semua frame sesi) |
| T38 | `20261021_ball_moving_replacement_01` | sumber_kurasi:20261021_ball_moving_candidate_01 | unknown | 0 | 12 | 2026-10-21T10:38:59 | 2026-10-21T10:39:16 | capture_frames.jsonl (semua frame sesi) |
| T38 | `20261021_empty_01` | sumber_kurasi:20261021_negative_candidate_01 | unknown | 0 | 60 | 2026-10-21T07:09:49 | 2026-10-21T07:12:08 | capture_frames.jsonl (semua frame sesi) |
| T38 | `20261021_empty_replacement_01` | sumber_kurasi:20261021_negative_candidate_01 | unknown | 0 | 12 | 2026-10-21T07:14:09 | 2026-10-21T07:14:38 | capture_frames.jsonl (semua frame sesi) |
| T43 | `20261112_t43_idle_objek_ulang_01` | diam_berobjek | servo_idle | 100 | 100 | 2026-11-12T05:16:17 | 2026-11-12T05:17:58 | capture_frames.jsonl |
| T43 | `20261112_t43_walk_objek_ulang_01` | jalan_berobjek_1 | walking | 50 | 50 | 2026-11-12T05:23:29 | 2026-11-12T05:24:19 | capture_frames.jsonl |
| T43 | `20261112_t43_walk_objek_ulang_02` | jalan_berobjek_2 | walking | 50 | 50 | 2026-11-12T05:26:35 | 2026-11-12T05:27:25 | capture_frames.jsonl |
| T43 | `20261112_t43_idle_negatif_01` | diam_kosong | servo_idle | 30 | 30 | 2026-11-12T05:28:36 | 2026-11-12T05:29:07 | capture_frames.jsonl |
| T43 | `20261112_t43_walk_negatif_01` | jalan_kosong | walking | 30 | 30 | 2026-11-12T05:30:11 | 2026-11-12T05:30:41 | capture_frames.jsonl |
| T43 | `20261112_t43_idle_berobjek_01` | dikecualikan_diarsipkan | servo_idle | 0 | 21 | 2026-11-12T04:51:07 | 2026-11-12T04:51:28 | capture_frames.jsonl (semua frame sesi) |
| T43 | `20261112_t43_idle_berobjek_02` | dikecualikan_diarsipkan | servo_idle | 0 | 79 | 2026-11-12T04:52:41 | 2026-11-12T04:54:03 | capture_frames.jsonl (semua frame sesi) |
| T43 | `20261112_t43_walk_objek_02` | dikecualikan_diarsipkan | walking | 0 | 50 | 2026-11-12T05:20:17 | 2026-11-12T05:21:07 | capture_frames.jsonl (semua frame sesi) |

## Catatan training teacher

Folder teacher di robot (`/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/`) memuat `manifest.json`, `args.yaml`, dan `results.csv`; tidak ada `SHA256SUMS.txt`. Ketiga berkas teks itu disalin dari robot. `best.pt` di folder tersebut dan di `.cache/hardware_models/fp32_pytorch/` tetap `e05b2b21…420b8c`. Salinan di laptop (`E:\Kuliah\SKRIPSI\Sourcecode\Progress 3\artifacts\checkpoints\fp32\`) cocok dengan hash pada prompt, tetapi memakai akhir baris CRLF; isinya identik dengan salinan robot setelah CRLF diubah menjadi LF.

| Berkas | Robot (bait, SHA-256) | Laptop (bait, SHA-256) | Sama setelah CRLF menjadi LF |
|---|---|---|---|
| `manifest.json` | 923 B, `197b14253bb7…` | 962 B, `24eed5d04ed8…` | ya |
| `args.yaml` | 1812 B, `472b96665585…` | 1928 B, `d2224eddf47a…` | ya |
| `results.csv` | 12687 B, `52fc98458a39…` | 12788 B, `1d36be98bf65…` | ya |

`timestamp` pada `manifest.json` (`2026-09-02T10:04:03.688292+00:00`) menurut skrip `scripts/step03_train_fp32.py` yang tersimpan (salinan robot dan laptop identik setelah normalisasi akhir baris) diisi sekali sebelum `model.train()` dengan `status: started`; saat training selesai hanya `status` yang diubah menjadi `completed`. Jadi nilai itu menandai awal training menurut skrip tersebut. Salinan skrip bertanggal 7 Oktober 2026, sesudah training, sehingga versi yang benar-benar dipakai pada 2 September tidak terverifikasi; kunci manifest sama persis dengan kunci yang ditulis skrip itu. `results.csv` memuat 100 epoch dengan `time` epoch terakhir 3385,53 detik.

## Berkas yang sengaja tidak disalin

| Set | Berkas | Jumlah | Alasan |
|---|---|---:|---|
| T38 | `audit_kotak_gawang_20261021.jpg` | 1 | bukan metadata teks (gambar atau lainnya) |
| T38 | `contact_sheet.jpg` | 6 | bukan metadata teks (gambar atau lainnya) |
| T38 | `contact_sheet_1.jpg` | 7 | bukan metadata teks (gambar atau lainnya) |
| T38 | `contact_sheet_2.jpg` | 7 | bukan metadata teks (gambar atau lainnya) |
| T38 | `labels_auto/predictions.jsonl` | 1 | berada di folder label; tidak disalin |
| T38 | `labels_auto/predictions.jsonl` | 10 | kunci koordinat 'xywhn'; kunci prediksi 'predictions' |
| T38 | `labels_auto/prelabel_manifest.json` | 11 | berada di folder label; tidak disalin |
| T38 | `labels_reviewed/review_log.jsonl` | 11 | berada di folder label; tidak disalin |
| T43 | `labels_auto/predictions.jsonl` | 2 | berada di folder label; tidak disalin |
| T43 | `labels_auto/predictions.jsonl` | 3 | kunci koordinat 'xyxy' |
| T43 | `labels_auto/prelabel_manifest.json` | 5 | berada di folder label; tidak disalin |
| T43 | `labels_reviewed/review_log.jsonl` | 5 | berada di folder label; tidak disalin |
| T43 eksperimen | `frozen_plan.json` | 1 | sudah ada di Git |
| T43 eksperimen | `walk_capture_guard_v1.py` | 1 | bukan metadata (kode atau berkas lain) |
| T38 dan T43 | label YOLO `labels_*/*.txt` | 1140 | label; tidak pernah disalin |
| T38 dan T43 | gambar `*.jpg`/`*.png` di folder sesi | 865 | gambar; tidak pernah disalin |
| T43 eksperimen | `blind_review_52/images/`, `labels_*` | - | gambar dan label tinjauan buta |
| Teacher | `best.pt`, `last.pt` | 2 | bobot model |

Berkas kandidat diperiksa isinya sebelum disalin. `predictions.jsonl` ditolak karena memuat koordinat dan prediksi; `prelabel_manifest.json` dan `review_log.jsonl` tidak disalin karena berada di folder label.
