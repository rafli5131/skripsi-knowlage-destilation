# Jejak waktu training, evaluasi, dan pengujian

Folder ini merangkum kapan setiap model dilatih, dievaluasi, dan diuji di robot. Semua angka dibaca dari
berkas yang sudah ada di repositori: manifest run (`started_at_utc`, `finished_at_utc`), kolom `time`
pada `results.csv`, tabel T36, log jendela runtime, dan hasil verifikasi jalur TEST. Waktu asli tercatat
dalam UTC; tabel di halaman ini juga menampilkannya dalam WIB (UTC+7).

![Garis waktu kegiatan](garis_waktu_kegiatan_id.png)

## Isi folder

| Berkas | Isi |
|---|---|
| [`kronologi_kegiatan.csv`](kronologi_kegiatan.csv) | 64 kegiatan berurutan waktu: training utama dan pendukung, sesi TEST, verifikasi jalur, evaluasi offline OP3, dan 24 run live, lengkap dengan perangkat dan berkas sumber |
| [`training_per_epoch.csv`](training_per_epoch.csv) | 900 baris: waktu kumulatif dan durasi tiap epoch, serta precision, recall, mAP50, dan mAP50-95 VAL untuk sembilan student utama |
| [`timestamp_frame_live_24_run.csv`](timestamp_frame_live_24_run.csv) | Untuk tiap run live: jumlah frame, timestamp frame pertama dan terakhir, rentang timestamp kamera, jeda terbesar, dan jumlah error |
| `garis_waktu_kegiatan_id.png` | Grafik garis waktu di atas |
| [`manifest_jejak_waktu_sha256.json`](manifest_jejak_waktu_sha256.json) | SHA-256 berkas keluaran dan setiap berkas sumber |

## Training utama

| Metode | Seed | Mulai (WIB) | Selesai (WIB) | Durasi training | Perangkat |
|---|---|---|---|---:|---|
| Supervised | 42 | 2026-10-09 02:59 | 2026-10-09 08:37 | 5,6 jam | tidak tercatat di manifest |
| KD murni | 42 | 2026-10-09 08:59 | 2026-10-09 14:22 | 5,34 jam | NVIDIA L40 |
| Supervised | 1337 | 2026-10-09 14:22 | 2026-10-09 19:31 | 3,73 jam | NVIDIA L40 |
| KD murni | 1337 | 2026-10-09 19:31 | 2026-10-09 22:28 | 2,93 jam | NVIDIA L40 |
| Supervised | 2025 | 2026-10-09 22:28 | 2026-10-10 01:43 | 3,23 jam | NVIDIA L40 |
| KD murni | 2025 | 2026-10-10 01:44 | 2026-10-10 04:44 | 2,97 jam | NVIDIA L40 |
| KD Hybrid full | 42 | 2026-10-22 00:00 | 2026-10-22 01:21 | 1,34 jam | NVIDIA L40 |
| KD Hybrid full | 1337 | 2026-10-22 05:10 | 2026-10-22 06:14 | 1,05 jam | NVIDIA L40 |
| KD Hybrid full | 2025 | 2026-10-22 06:14 | 2026-10-22 07:17 | 1,03 jam | NVIDIA L40 |
| Teacher YOLO11n | - | tidak tersedia | tidak tersedia | - | NVIDIA L40 (menurut audit 22 Oktober) |

Durasi training diambil dari kolom `time` epoch terakhir, sama dengan
[T35](../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md). Supervised seed 1337 sempat terhenti
dan dilanjutkan dari checkpoint, sehingga durasinya adalah jumlah dua segmen dan selisih mulai-selesai
memuat jeda interupsi.

**Teacher utama** dilatih di server lab pada proyek Advance Vision, bukan di robot. Robot hanya menyimpan
salinan bobotnya (SHA-256 `e05b2b21...420b8c`). Audit 22 Oktober mencatat bahwa manifest dan log teacher
menyebut 100 epoch, seed 42, dan GPU L40, tetapi berkas tersebut berada di akun server lama yang kini tidak
dapat diakses, sehingga waktu mulai dan selesai training teacher tidak tersedia di repositori.

## Evaluasi TEST dan verifikasi jalur

| Kegiatan | Mulai (WIB) | Durasi | Perangkat |
|---|---|---:|---|
| Sesi TEST gagal (diulang sebagai retry1) | 2026-10-10 10:49 | 5,7 detik | NVIDIA L40 |
| Sesi TEST 7 checkpoint | 2026-10-10 11:00 | 167,2 detik | NVIDIA L40 |
| Sesi TEST 6 checkpoint | 2026-10-22 08:12 | 52,8 detik | NVIDIA L40 |
| Verifikasi jalur TEST sembilan student (D23) | 2026-11-13 17:01 | 10927,0 detik | CPU labkc-l40-debian |
| Verifikasi jalur TEST teacher (D24) | 2026-11-16 13:41 | 1267,0 detik | CPU labkc-l40-debian |

Durasi sesi TEST mencakup seluruh checkpoint dalam sesi dan overhead penyiapan, bukan waktu per model.

## Pengujian live di OP3

24 run live berlangsung dari 2026-11-02 17:56 sampai 2026-11-03 17:32 WIB, masing-masing dengan jendela ukur 60
detik. Log per frame (`capture_stamp_ns`, `receive_time_utc`, durasi tiap tahap, CPU, RSS, error) untuk
9 run tersimpan di repositori. Untuk 15 run lainnya, log mentah hanya ada di OP3;
repositori menyimpan hash-nya pada kolom `raw_csv_sha256` T36 dan kolom `sha256` tabel frame.

## Yang masih dicari di robot

| Yang dicari | Lokasi yang diduga di OP3 | Cara memeriksa |
|---|---|---|
| Log per frame 15 run live | `runs/op3_pytorch/<run_id>.csv` pada repo robot | `sha256sum` harus sama dengan kolom `sha256` pada `timestamp_frame_live_24_run.csv` |
| Manifest capture frame T38 dan T43 | `data/op3_camera_eval/sessions/` dan `data/op3_camera_eval/experiments/t43_20261112/` | Cocokkan dengan manifest beku T38 dan `review_260_audit_and_frozen_hashes.json` |
| Manifest atau log training teacher | `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/` (folder yang sama dengan bobot teacher) | Cari `manifest.json`, `args.yaml`, atau `results.csv`; bila tidak ada, catat sebagai tidak tersedia |

Frame, label, dan log mentah dari robot tetap tidak masuk Git kecuali Bhre memintanya. Bila log mentah
disalin ke repositori, jalankan ulang skrip agar tabel frame terisi lengkap.

## Membangkitkan ulang

```bash
python3 scripts/build_jejak_waktu.py --replace
```

Dibangkitkan dari commit `4a9f34453bee`.
