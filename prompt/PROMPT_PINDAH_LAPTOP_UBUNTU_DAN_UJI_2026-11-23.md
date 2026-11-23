# Prompt pindah laptop ke Ubuntu dan menjalankan ulang tes

Tanggal: 23 November 2026. Dijalankan oleh agen (Claude Code) di **laptop Bhre yang sudah memakai Ubuntu**, di folder hasil `git clone` repositori ini. Tujuannya dua: menyiapkan lingkungan kerja yang sama dengan laptop Windows sebelumnya, lalu memastikan apakah empat tes yang gagal di Windows lulus di Linux.

Pekerjaan ini **offline terhadap robot**: tanpa kamera, ROS live, servo, torque, gait, training, atau inferensi. Tidak ada perintah ke robot atau server lab kecuali Bhre memintanya di langkah 7.

## Latar

- Pada 23 November 2026 di laptop Windows, `python -m pytest -q tests --ignore=tests/test_kd_hybrid.py --continue-on-collection-errors` menghasilkan **28 lulus, 2 gagal, 2 galat**. Tidak ada yang terkait pekerjaan hari itu.
  - Galat: `tests/test_continue_t42.py` dan `tests/test_continue_t42_attempt.py`, karena skrip T42 mengimpor `fcntl` (khusus Unix).
  - Gagal: `tests/test_server_paths.py::ServerPathTests::test_evaluation_data_yaml_rebases_all_splits` dan `tests/test_server_paths.py::DriverTests::test_student_config_legacy_unchanged`, karena path Windows memakai `\`.
  - Tes `test_build_jejak_waktu.py` dan `test_build_bukti_kebutuhan.py` lulus.
- Dugaan awal: keempatnya lulus di Linux. Dugaan ini **sudah diuji sekali** pada hari yang sama (lihat butir berikut); tugas sesi ini adalah mengulanginya di laptop Linux lain atau lingkungan baru dan membandingkan hasilnya.
- **Hasil sesi sebelumnya di laptop Ubuntu 24.04.5 (Python 3.12.3)**, dari [`dokumentasi/2026-11-23/LAPORAN_UJI_LAPTOP_UBUNTU.md`](../dokumentasi/2026-11-23/LAPORAN_UJI_LAPTOP_UBUNTU.md): `pytest -q tests --ignore=tests/test_kd_hybrid.py` menghasilkan **40 lulus, 0 gagal, 0 galat**, termasuk keempat tes yang gagal di Windows. Angka 40 berasal dari 30 tes yang berjalan di Windows ditambah 10 tes di dua berkas T42 yang tidak termuat di Windows. Hasil ini hanya berlaku bila `PYTHONPATH` ROS tidak aktif saat pytest dijalankan (lihat butir berikut). Tidak ada tes yang diubah.
- **Syarat lingkungan: `PYTHONPATH` ROS 2.** Shell laptop itu memuat `PYTHONPATH` ROS 2 Jazzy (`/opt/ros/jazzy/...` dan `~/robotis_ws/install/...`). Dengan `PYTHONPATH` itu, pytest memuat plugin ROS (`launch_testing`, `launch_ros`, `ament_*`), dan `launch_testing` gagal dimuat karena modul `lark` tidak ada. Akibatnya pytest berhenti dengan `ModuleNotFoundError: No module named 'lark'` **sebelum satu tes pun berjalan**. Itu masalah lingkungan shell, bukan masalah tes. Karena itu **semua perintah `pytest` dan skrip Python di prompt ini dijalankan dengan `env -u PYTHONPATH`**, sesuai kebiasaan repositori (`agent.md`). Di laptop tanpa ROS, awalan itu tidak berpengaruh dan tetap aman dipakai.
- `tests/test_kd_hybrid.py` **tidak dijalankan** di sesi sebelumnya. Tes itu butuh `torch` 2.4.1, `ultralytics` 8.4.130, dan bobot teacher pada `../rafli/advance_vision/artifacts/checkpoints/fp32/best.pt` (relatif terhadap repositori) atau `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt`. Tanpa bobot itu tes gagal karena berkas teacher, bukan karena kode, dan isi tes tidak boleh diubah. Tes ini lebih tepat dijalankan di server lab. Tes itu dilewati di Windows juga.
- Aturan proyek ada di `agent.md` dan `AGENTS.md`. Bacalah sebelum mengubah apa pun.

## Larangan

- Jangan mengubah isi tes untuk membuatnya lulus. Bila ada tes gagal, laporkan apa adanya beserta penyebabnya.
- Jangan mengubah hasil beku T05, T30, T36, T37, T38, T43, T44, dan T45, `docs/DECISIONS.md`, atau berkas di `runs/`, `artifacts/`, `log_op3_pelengkap/`.
- Jangan menjalankan training, inferensi, atau perintah ke robot. Jangan mengunduh dataset.
- Jangan memasang paket sistem (`apt install`) atau mengubah konfigurasi SSH tanpa menanyakan Bhre lebih dulu. Paket Python hanya boleh dipasang ke virtual environment baru di luar repositori (`~/.venvs/skripsi-uji`), supaya tidak muncul di `git status`; jangan memasangnya ke Python sistem dan jangan mengubah `.gitignore`.
- Jangan menyimpan kata sandi, token, kunci privat, atau alamat IP robot di berkas yang masuk Git.
- Jangan commit atau push tanpa persetujuan Bhre atas daftar berkasnya. Folder `Claude outputs/` tidak boleh ikut.

## Persiapan

1. Periksa lingkungan dan laporkan hasilnya sebelum memasang apa pun:
   ```bash
   uname -a; lsb_release -ds; python3 --version; git --version; ssh -V
   git status --short; git log -1 --oneline; git remote -v
   echo "PYTHONPATH=${PYTHONPATH:-<kosong>}"; echo "ROS_DISTRO=${ROS_DISTRO:-<kosong>}"
   ```
   Repositori harus berada di commit `f319785` atau yang lebih baru di `main`. Bila belum, jalankan `git pull --ff-only origin main`. Bila gagal, berhenti dan laporkan. Catat apakah `PYTHONPATH` berisi path ROS; bila ya, `env -u PYTHONPATH` wajib dipakai pada langkah 5, 7, dan 8.
2. Baca `agent.md`, `AGENTS.md`, `README.md` (bagian "Progres dan langkah berikutnya"), dan `log_op3_pelengkap/LAPORAN_SESI.md`.
3. Buat virtual environment baru. Bila `python3 -m venv` gagal karena paket `python3-venv` tidak ada, **berhenti dan tanyakan Bhre** apakah boleh menjalankan `sudo apt install python3-venv`.
   ```bash
   mkdir -p ~/.venvs && python3 -m venv ~/.venvs/skripsi-uji
   ~/.venvs/skripsi-uji/bin/python -m pip install --upgrade pip
   ```

## Tes tanpa paket berat

4. Pasang hanya yang dibutuhkan skrip build dan tes ringan:
   ```bash
   ~/.venvs/skripsi-uji/bin/python -m pip install pytest "numpy==1.26.4" "PyYAML==6.0.3" matplotlib
   ```
   Bila `numpy==1.26.4` tidak punya wheel untuk versi Python Ubuntu, catat versi yang terpasang dan lanjutkan; jangan mengompilasi dari sumber tanpa bertanya.
5. Jalankan tes yang sama dengan perintah di Windows, tetapi dengan `env -u PYTHONPATH` di depannya, tanpa opsi `--continue-on-collection-errors` lebih dulu:
   ```bash
   env -u PYTHONPATH ~/.venvs/skripsi-uji/bin/python -m pytest -q tests --ignore=tests/test_kd_hybrid.py
   ```
   Lalu jalankan versi yang melanjutkan setelah galat pemuatan, dengan rincian per tes, supaya bisa dibandingkan dengan Windows:
   ```bash
   env -u PYTHONPATH ~/.venvs/skripsi-uji/bin/python -m pytest -q tests --ignore=tests/test_kd_hybrid.py --continue-on-collection-errors -rA
   ```
   Bila `PYTHONPATH` tadi tampak berisi path ROS, **jalankan juga sekali tanpa `env -u PYTHONPATH`** untuk membuktikan bahwa kegagalannya (`No module named 'lark'`, tidak ada tes yang berjalan) memang berasal dari plugin ROS. Catat hasilnya sebagai temuan lingkungan; jangan memasang `lark` atau paket ROS untuk menghindarinya.
6. Bandingkan hasilnya dengan Windows dan dengan hasil sesi Ubuntu sebelumnya (40 lulus). Untuk setiap dari empat tes yang gagal di Windows, catat: lulus atau gagal di Linux, dan bila gagal, pesan galat lengkapnya. Tes lain yang lulus di Windows tetapi gagal di Linux juga dicatat, begitu pula selisih jumlah tes dibanding 40.

## Tes yang butuh torch dan ultralytics (opsional, tanya dulu)

7. `tests/test_kd_hybrid.py` butuh `torch`, `ultralytics` (lihat `requirements-op3-pytorch.txt`), **dan bobot teacher** pada salah satu path di bagian Latar. Pemasangannya besar (beberapa ratus MB sampai lebih dari 1 GB) dan memakai CPU saja. Pada sesi sebelumnya tes ini dilewati dengan persetujuan Bhre karena bobot teacher tidak ada di laptop.

   **Periksa dulu** apakah salah satu path bobot teacher ada. Bila tidak ada, **jangan memasang torch dan ultralytics**; laporkan bahwa tes ini lebih tepat dijalankan di server lab dan lanjut ke langkah 8. Bila ada, **tanyakan Bhre** apakah tes ini mau dijalankan. Bila ya:
   ```bash
   ~/.venvs/skripsi-uji/bin/python -m pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cpu
   ~/.venvs/skripsi-uji/bin/python -m pip install ultralytics==8.4.130
   env -u PYTHONPATH ~/.venvs/skripsi-uji/bin/python -m pytest -q tests/test_kd_hybrid.py
   ```
   Catat versi Python Ubuntu; torch 2.4.1 mungkin tidak punya wheel untuk Python terbaru. Bila pemasangan gagal, laporkan dan jangan memaksa. Jangan menyalin bobot teacher dari robot atau server tanpa persetujuan Bhre.

## Pemeriksaan tambahan

8. Pastikan skrip build menghasilkan keluaran yang sama dengan yang di-commit. Tes `test_build_jejak_waktu.py` dan `test_build_bukti_kebutuhan.py` sudah memeriksanya, tetapi PNG di `jejak_waktu/` dibuat dengan versi matplotlib laptop Windows. Jalankan:
   ```bash
   git status --short
   env -u PYTHONPATH ~/.venvs/skripsi-uji/bin/python scripts/build_jejak_waktu.py --output /tmp/jejak_waktu_uji
   env -u PYTHONPATH ~/.venvs/skripsi-uji/bin/python scripts/build_bukti_kebutuhan.py --output /tmp/bukti_kebutuhan_uji
   diff -rq jejak_waktu /tmp/jejak_waktu_uji; diff -rq bukti_kebutuhan /tmp/bukti_kebutuhan_uji
   ```
   Bila skrip tidak menerima `--output`, lihat `--help` dan sesuaikan; jangan memakai `--replace` pada folder yang di-commit. Laporkan berkas yang berbeda. Perbedaan hash pada PNG akibat versi matplotlib diharapkan dan tidak perlu diperbaiki.
9. Pastikan `git status --short` setelah semua langkah hanya berisi `Claude outputs/` (dan, bila memang ada sejak awal, perubahan lama yang bukan milik sesi ini). Tidak boleh ada perubahan baru pada berkas terlacak dan tidak ada berkas baru di repositori. Bila `pytest` meninggalkan `.pytest_cache/` atau `__pycache__/` yang tidak diabaikan Git, laporkan namanya; jangan menghapusnya tanpa bertanya.

## Akses ke robot dan server lab dari laptop baru (hanya bila diminta Bhre)

10. Bhre mungkin ingin menyambung lagi ke robot dan server dari laptop Ubuntu. Jangan menyalin `~/.ssh` dari laptop Windows lewat chat atau repositori. Bila Bhre memintanya, ikuti urutan ini dan berhenti di setiap langkah yang butuh kata sandi:
    - buat kunci baru: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -C "ubuntu-laptop"` (tanpa passphrase hanya bila Bhre setuju);
    - Bhre sendiri yang mengirim kunci publiknya ke robot dan server (`ssh-copy-id`), karena itu butuh kata sandi mereka;
    - alias SSH ditulis di `~/.ssh/config` dengan nama `op3-robot` dan `gpu-labkc`; alamat, pengguna, dan port diminta dari Bhre atau dibaca dari `~/.ssh/config` laptop lama, jangan ditebak;
    - uji dengan `ssh -o BatchMode=yes <alias> 'hostname; whoami'` dan laporkan hasilnya.

## Laporan

11. Tulis `LAPORAN_SESI_UBUNTU.md` di folder kerja sementara di luar repositori (misalnya `/tmp/laporan_ubuntu/`), lalu tampilkan isinya kepada Bhre dalam Bahasa Indonesia:
    - versi Ubuntu, Python, dan paket yang terpasang di `~/.venvs/skripsi-uji`;
    - tabel hasil tes: nama tes, hasil di Windows, hasil di Linux, dan jumlah lulus dibanding 40 pada sesi Ubuntu sebelumnya;
    - nilai `PYTHONPATH` dan `ROS_DISTRO` di shell, serta hasil pytest tanpa dan dengan `env -u PYTHONPATH` bila ROS aktif;
    - apakah hasil "keempat tes lulus di Linux" terulang, sebagian, atau tidak, beserta pesan galat bila gagal;
    - hasil `test_kd_hybrid.py` atau alasan tidak dijalankan;
    - hasil perbandingan keluaran skrip build (langkah 8);
    - `git status --short` akhir.

    Setelah itu tanyakan kepada Bhre apakah ada hal yang perlu dicatat di repositori. Jangan commit sebelum ada jawaban.
