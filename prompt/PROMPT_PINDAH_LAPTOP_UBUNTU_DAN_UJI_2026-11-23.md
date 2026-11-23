# Prompt pindah laptop ke Ubuntu dan menjalankan ulang tes

Tanggal: 23 November 2026. Dijalankan oleh agen (Claude Code) di **laptop Bhre yang sudah memakai Ubuntu**, di folder hasil `git clone` repositori ini. Tujuannya dua: menyiapkan lingkungan kerja yang sama dengan laptop Windows sebelumnya, lalu memastikan apakah empat tes yang gagal di Windows lulus di Linux.

Pekerjaan ini **offline terhadap robot**: tanpa kamera, ROS live, servo, torque, gait, training, atau inferensi. Tidak ada perintah ke robot atau server lab kecuali Bhre memintanya di langkah 7.

## Latar

- Pada 23 November 2026 di laptop Windows, `python -m pytest -q tests --ignore=tests/test_kd_hybrid.py --continue-on-collection-errors` menghasilkan **28 lulus, 2 gagal, 2 galat**. Tidak ada yang terkait pekerjaan hari itu.
  - Galat: `tests/test_continue_t42.py` dan `tests/test_continue_t42_attempt.py`, karena skrip T42 mengimpor `fcntl` (khusus Unix).
  - Gagal: `tests/test_server_paths.py::ServerPathTests::test_evaluation_data_yaml_rebases_all_splits` dan `tests/test_server_paths.py::DriverTests::test_student_config_legacy_unchanged`, karena path Windows memakai `\`.
  - Tes `test_build_jejak_waktu.py` dan `test_build_bukti_kebutuhan.py` lulus.
- Dugaan: keempatnya lulus di Linux. Dugaan ini **belum terbukti**; tugas sesi ini adalah mengujinya.
- `tests/test_kd_hybrid.py` kemungkinan butuh `torch` dan `ultralytics`. Tes itu dilewati di Windows.
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
   ```
   Repositori harus berada di commit `037f445` atau yang lebih baru di `main`. Bila belum, jalankan `git pull --ff-only origin main`. Bila gagal, berhenti dan laporkan.
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
5. Jalankan tes yang sama persis dengan perintah di Windows, tanpa opsi `--continue-on-collection-errors` lebih dulu:
   ```bash
   ~/.venvs/skripsi-uji/bin/python -m pytest -q tests --ignore=tests/test_kd_hybrid.py
   ```
   Lalu jalankan versi yang melanjutkan setelah galat pemuatan, dengan rincian per tes, supaya bisa dibandingkan dengan Windows:
   ```bash
   ~/.venvs/skripsi-uji/bin/python -m pytest -q tests --ignore=tests/test_kd_hybrid.py --continue-on-collection-errors -rA
   ```
6. Bandingkan hasilnya dengan Windows. Untuk setiap dari empat tes yang gagal di Windows, catat: lulus atau gagal di Linux, dan bila gagal, pesan galat lengkapnya. Tes lain yang lulus di Windows tetapi gagal di Linux juga dicatat.

## Tes yang butuh torch dan ultralytics (opsional, tanya dulu)

7. `tests/test_kd_hybrid.py` butuh `torch` dan `ultralytics` (lihat `requirements-op3-pytorch.txt`). Pemasangannya besar (beberapa ratus MB sampai lebih dari 1 GB) dan memakai CPU saja. **Tanyakan Bhre** apakah tes ini mau dijalankan. Bila ya:
   ```bash
   ~/.venvs/skripsi-uji/bin/python -m pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cpu
   ~/.venvs/skripsi-uji/bin/python -m pip install ultralytics==8.4.130
   ~/.venvs/skripsi-uji/bin/python -m pytest -q tests/test_kd_hybrid.py
   ```
   Catat versi Python Ubuntu; torch 2.4.1 mungkin tidak punya wheel untuk Python terbaru. Bila pemasangan gagal, laporkan dan jangan memaksa.

## Pemeriksaan tambahan

8. Pastikan skrip build menghasilkan keluaran yang sama dengan yang di-commit. Tes `test_build_jejak_waktu.py` dan `test_build_bukti_kebutuhan.py` sudah memeriksanya, tetapi PNG di `jejak_waktu/` dibuat dengan versi matplotlib laptop Windows. Jalankan:
   ```bash
   git status --short
   ~/.venvs/skripsi-uji/bin/python scripts/build_jejak_waktu.py --output /tmp/jejak_waktu_uji
   ~/.venvs/skripsi-uji/bin/python scripts/build_bukti_kebutuhan.py --output /tmp/bukti_kebutuhan_uji
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
    - tabel hasil tes: nama tes, hasil di Windows, hasil di Linux;
    - apakah dugaan "keempat tes lulus di Linux" terbukti, sebagian, atau tidak, beserta pesan galat bila gagal;
    - hasil `test_kd_hybrid.py` atau alasan tidak dijalankan;
    - hasil perbandingan keluaran skrip build (langkah 8);
    - `git status --short` akhir.

    Setelah itu tanyakan kepada Bhre apakah ada hal yang perlu dicatat di repositori. Jangan commit sebelum ada jawaban.
