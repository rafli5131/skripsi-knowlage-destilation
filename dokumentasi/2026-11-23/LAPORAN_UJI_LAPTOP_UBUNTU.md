# Laporan sesi pindah laptop ke Ubuntu dan uji ulang — 23 November 2026

Prompt: [`PROMPT_PINDAH_LAPTOP_UBUNTU_DAN_UJI_2026-11-23.md`](../../prompt/PROMPT_PINDAH_LAPTOP_UBUNTU_DAN_UJI_2026-11-23.md). Repositori: clone di laptop Ubuntu, branch `main`, commit `89bb780` (sesudah `037f445`, sejajar `origin/main`; tidak perlu pull). Tidak ada training, inferensi, atau perintah ke robot; tidak ada paket sistem yang dipasang.

## 1. Lingkungan

| Komponen | Versi |
|---|---|
| OS | Ubuntu 24.04.5 LTS, kernel 7.0.0-43-generic, x86_64 |
| Python | 3.12.3 |
| Git / OpenSSH | 2.43.0 / OpenSSH 9.6p1 |
| Venv | `~/.venvs/skripsi-uji` (di luar repositori) |

Paket di venv: pytest 9.2.0, numpy 1.26.4 (wheel tersedia untuk Python 3.12), PyYAML 6.0.3, matplotlib 3.11.2, serta dependensinya (pillow 13.0.0, contourpy 1.3.3, fonttools 4.68.0, kiwisolver 1.5.1, cycler 0.12.1, pyparsing 3.3.3, python-dateutil 4.0.0, packaging 26.3, pluggy 1.7.0, iniconfig 2.3.1, Pygments 2.21.0).

**Temuan lingkungan.** Shell laptop memuat `PYTHONPATH` ROS 2 Jazzy (`/opt/ros/jazzy/...` dan `~/robotis_ws/install/...`). Dengan `PYTHONPATH` itu, pytest memuat tujuh plugin ROS (`launch_testing`, `launch_ros`, `ament_*`), dan `launch_testing` gagal dimuat karena modul `lark` tidak ada. Akibatnya perintah langkah 5 yang persis seperti prompt berhenti sebelum satu tes pun berjalan (`ModuleNotFoundError: No module named 'lark'`). Ini masalah lingkungan shell, bukan masalah tes. Semua hasil di bawah dijalankan dengan `env -u PYTHONPATH`, sesuai kebiasaan repositori (`agent.md`), sehingga tidak ada plugin ROS yang dimuat.

## 2. Hasil tes (`--ignore=tests/test_kd_hybrid.py`)

- Tanpa `--continue-on-collection-errors`: **40 lulus** (1,33 s). Tidak ada galat pemuatan.
- Dengan `--continue-on-collection-errors -rA`: **40 lulus, 0 gagal, 0 galat** (0,87 s).

Jumlah 40 sesuai dengan Windows: 28 lulus + 2 gagal = 30 tes yang berjalan, ditambah 10 tes di dua berkas T42 (2 + 8) yang tidak termuat di Windows.

| Tes | Windows | Linux |
|---|---|---|
| `tests/test_continue_t42.py` (2 tes) | Galat pemuatan (`fcntl`) | Lulus 2/2 |
| `tests/test_continue_t42_attempt.py` (8 tes) | Galat pemuatan (`fcntl`) | Lulus 8/8 |
| `test_server_paths.py::ServerPathTests::test_evaluation_data_yaml_rebases_all_splits` | Gagal (path `\`) | Lulus |
| `test_server_paths.py::DriverTests::test_student_config_legacy_unchanged` | Gagal (path `\`) | Lulus |
| `test_build_jejak_waktu.py` (1 tes) | Lulus | Lulus |
| `test_build_bukti_kebutuhan.py` (2 tes) | Lulus | Lulus |
| 26 tes lain | Lulus | Lulus |

**Dugaan "keempat tes lulus di Linux": terbukti**, dengan syarat `PYTHONPATH` ROS tidak aktif saat pytest dijalankan. Tidak ada tes yang lulus di Windows tetapi gagal di Linux. Tidak ada tes yang diubah.

## 3. `tests/test_kd_hybrid.py`

Tidak dijalankan di laptop. Tes ini memeriksa kode loss KD (`train_kd.py`: `pure_v4` terhadap snapshot, Hybrid full dengan KD nol, kesamaan loss dan gradien KD, `hybrid_feature`, bentuk log validasi) pada CPU dengan satu gambar acak 64 x 64. Selain torch 2.4.1 dan ultralytics 8.4.130, tes membutuhkan bobot teacher pada `../rafli/advance_vision/artifacts/checkpoints/fp32/best.pt` (relatif terhadap repositori) atau `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`. Keduanya tidak ada di laptop, dan isi tes tidak boleh diubah, sehingga tes akan gagal karena berkas teacher, bukan karena kode. Bhre menyetujui untuk melewatinya; tes ini lebih tepat dijalankan di server lab.

## 4. Keluaran skrip build (langkah 8)

Dijalankan ke `/tmp/jejak_waktu_uji` dan `/tmp/bukti_kebutuhan_uji` (tanpa `--replace`). Ringkasan skrip: 64 kegiatan, 1.000 baris epoch, 24 run live; KF-04 lulus 24/24.

| Folder | Berkas berbeda | Penyebab |
|---|---|---|
| `jejak_waktu/` | `garis_waktu_kegiatan_id.png` | Versi matplotlib/pillow berbeda (diharapkan) |
| | `README.md` | Hanya baris "Dibangkitkan dari commit" (`a4bc9b2` → `89bb780`) |
| | `manifest_jejak_waktu_sha256.json` | `dibuat_utc`, `commit_repo`, dan hash kedua berkas di atas |
| `bukti_kebutuhan/` | `README.md` | Hanya baris "Dibangkitkan dari commit" |
| | `manifest_bukti_sha256.json` | `dibuat_utc`, `commit_repo`, dan hash `README.md` |

Semua CSV dan berkas lain identik byte demi byte. Folder yang di-commit tidak diubah.

## 5. Akses robot (langkah 10, hanya robot)

`ssh -o BatchMode=yes op3 'hostname; whoami'` → `humanoid-NUC12WSHi5` / `humanoid`. Akses ini memakai koneksi bersama (`ControlMaster`, alias `op3` di `~/.ssh/config`) dari login password Bhre; koneksi berakhir sekitar 4 jam setelah sesi terakhir ditutup. Laptop belum punya kunci SSH (`~/.ssh/id_*` tidak ada), dan alias `op3-robot` yang disebut prompt belum dibuat. Konfigurasi SSH tidak diubah pada sesi ini.

## 6. `git status --short` akhir

```
 M dokumentasi/2026-11-13/LOG_PROGRES_SKRIPSI.md
?? "Claude outputs/"
```

Perubahan pada log 13 November sudah ada sebelum sesi. Angkanya diperiksa terhadap `hasil_verifikasi_jalur_test.json` 13 November: TP gawang pada IoU 0,5 turun 3 sampai 13 dari varian `protokol_test` ke varian `robot`, sehingga koreksi itu benar dan ikut di-commit (koreksi "3 sampai 11" menjadi "3 sampai 13 dibanding jalur prediksi pada ambang TEST") dan bukan milik sesi ini. `.pytest_cache/`, `scripts/__pycache__/`, dan `tests/__pycache__/` ada sejak sebelum tes dijalankan dan sudah diabaikan Git. Tidak ada perubahan baru pada berkas terlacak dan tidak ada berkas baru di repositori.

## 7. Tindak lanjut: `test_kd_hybrid.py` di server lab

Dijalankan Bhre pada 23 November 2026 di server lab (`labkc-l40-debian`, akun `dindarosyidah`), commit repo `be6ba9f`, dengan `.venv-train` (Python 3.11.2, torch 2.4.1+cu121, ultralytics 8.4.130) dan `CUDA_VISIBLE_DEVICES=""` sehingga berjalan di CPU. Hasil: **5 dari 5 tes lulus** dalam 3,1 detik. Log lengkap: [`test_kd_hybrid_server_lab.log`](test_kd_hybrid_server_lab.log).

| Tes | Hasil |
|---|---|
| `test_pure_v4_matches_snapshot` | ok |
| `test_hybrid_full_zero_kd_equals_detection_loss` | ok |
| `test_hybrid_full_kd_equals_pure_v4_and_gradients` | ok |
| `test_hybrid_feature_uses_original_loss` | ok |
| `test_hybrid_full_validation_log_shape` | ok |

Catatan pelaksanaan:

- Path teacher utama di tes, `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`, tidak dapat diakses (`Permission denied`) karena akun `rafli5131` sudah dihapus. Path yang sama masih tercatat di `configs/model_registry.yaml`.
- Tes memakai path cadangan `../rafli/advance_vision/artifacts/checkpoints/fp32/best.pt` relatif terhadap repositori. Di server, path itu dibuat sebagai tautan simbolik di luar repositori ke `models_local/teacher_utama/best.pt`. SHA-256 sumber dan tautan sama: `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Bobot tidak disalin, dan isi tes tidak diubah.
- `.venv-train` tidak berisi pytest, dan venv itu tidak diubah. Tes dijalankan dengan `env -u PYTHONPATH CUDA_VISIBLE_DEVICES="" .venv-train/bin/python -m unittest discover -s tests -p test_kd_hybrid.py -v`. `-m unittest tests.test_kd_hybrid` gagal karena `tests/` tidak memiliki `__init__.py`.
- Peringatan `no model scale passed. Assuming scale='t'` sesuai dengan student skala `t` kustom. `Could not initialize NNPACK` hanya menandakan satu pustaka percepatan CPU tidak didukung; keduanya tidak memengaruhi hasil.

Dengan hasil ini, seluruh tes di `tests/` sudah dijalankan: 40 lulus di laptop Ubuntu dan 5 lulus di server lab.
