# Prompt grafik garis kontinu runtime OP3 (latensi, FPS, CPU, RAM)

Tanggal: 11 November 2026. Dijalankan oleh agen di **komputer OP3** pada repo proyek ini. Pekerjaan ini hanya membaca log yang sudah ada dan membuat grafik; tidak ada pengukuran baru.

## Tujuan

Melengkapi grafik garis kontinu sebagai bukti rumusan masalah 4 (latensi dan FPS saat robot diam dan berjalan) dan 5 (CPU dan RAM proses detektor) untuk empat model: teacher YOLO11n, KD Hybrid full seed 1337, supervised seed 1337, dan KD murni seed 42. Grafik akurasi sudah dibuat pada 11 November 2026; bagian runtime tertunda karena 15 dari 24 berkas `jendela_runtime.csv` run aktif T36 (sesi 3 November) hanya ada di robot.

## Larangan

- Jangan mengirim perintah servo, gait, motor, atau torque, dan jangan menyalakan kamera atau detektor. Pekerjaan ini murni membaca berkas.
- Jangan menimpa, memindahkan, atau menghapus log percobaan maupun grafik yang sudah ada. Generator menolak menimpa berkas keluaran; bila keluaran sudah ada, berhenti dan laporkan.
- Jangan mengubah nilai log, T36, T37, atau manifest 9 November. Jangan merekonstruksi data yang hilang.
- Jangan *commit* atau push `jendela_runtime.csv` maupun log robot lain tanpa izin eksplisit Bhre. *Commit* dan push grafik juga hanya bila Bhre memintanya.

## Langkah

1. **Sinkronkan repo.** Jalankan `git status --short`. Bila ada perubahan lokal pada berkas yang dilacak Git, berhenti dan laporkan. Bila bersih, jalankan `git pull --ff-only origin main`. Pastikan `scripts/build_grafik_garis_model_20261111.py` dan `dokumentasi/model/manifest_grafik_garis_akurasi.json` ada.

2. **Periksa ke-24 log run aktif.** Daftar sumbernya adalah semua kunci berakhiran `jendela_runtime.csv` pada `dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/grafik-final/manifest_grafik.json` (pemetaan run aktif juga ada di `dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/active_run_sources.json`). Laporkan berkas yang tidak ada. Ke-15 berkas yang belum ada di GitHub adalah:
   - `dokumentasi/2026-11-03/percobaan-31-kd-hybrid-berjalan-3-ulangan/02-kd-hybrid/walk-u{1,2,3}/jendela_runtime.csv`
   - `dokumentasi/2026-11-03/percobaan-32-supervised-idle-3-ulangan/03-supervised/{idle-u1-ulang2,idle-u2,idle-u3-ulang1}/jendela_runtime.csv`
   - `dokumentasi/2026-11-03/percobaan-33-supervised-berjalan-3-ulangan/03-supervised/walk-u{1,2,3}/jendela_runtime.csv`
   - `dokumentasi/2026-11-03/percobaan-34-kd-murni-idle-3-ulangan/04-kd-murni/idle-u{1,2,3}/jendela_runtime.csv`
   - `dokumentasi/2026-11-03/percobaan-35-kd-murni-berjalan-3-ulangan/04-kd-murni/{walk-u1,walk-u2,walk-u3-ulang1}/jendela_runtime.csv`

   Bila berkas berada di lokasi lain di robot, jangan menyalin tanpa memastikan run ID di dalam CSV dan hash-nya cocok dengan manifest. Bila ada yang hilang atau hash berbeda, berhenti dan laporkan; jangan membuat grafik dari data sebagian.

3. **Buat grafik.** Dari akar repo, dengan Python yang memiliki `matplotlib` (skrip hanya memakai pustaka standar dan matplotlib):

   ```bash
   python3 scripts/build_grafik_garis_model_20261111.py --bagian runtime
   ```

   Generator mencocokkan hash tiap berkas dengan manifest 9 November (dengan toleransi perbedaan akhir baris CRLF/LF) serta jumlah frame dan rerata latensi tiap run dengan T36, lalu menulis:
   - `dokumentasi/model/<model>/garis_runtime_op3_<model>_{id,en}.png` untuk `teacher_yolo11n`, `kd_hybrid`, `supervised`, `kd_murni`: empat baris (latensi, FPS, CPU, RSS) × dua kolom (diam, berjalan), tiga ulangan per kondisi, bin 2 detik, garis batas KNF-01 8 FPS;
   - `dokumentasi/model/gabungan/garis_runtime_op3_empat_model_{id,en}.png`: rerata tiga ulangan per model dengan pita min–maks;
   - `dokumentasi/model/gabungan/data_garis_runtime_op3_empat_model.csv`;
   - `dokumentasi/model/manifest_grafik_garis_runtime.json`.

   Bila generator gagal pada pencocokan T36 atau hash, jangan mengubah skrip untuk melonggarkan pemeriksaan. Laporkan pesan galatnya.

4. **Periksa visual.** Buka setiap PNG. Pastikan judul, label sumbu, legenda, dan catatan kaki tidak bertumpuk, kurva lengkap 60 detik, dan garis 8 FPS terlihat. Catat masalah tata letak bila ada.

5. **Perbarui README.** Pada lima README di `dokumentasi/model/{teacher_yolo11n,kd_hybrid,supervised,kd_murni,gabungan}/README.md`, ganti butir "Runtime OP3 (latensi, FPS, CPU, RSS) per waktu: belum dibuat..." dengan tautan ke PNG Indonesia dan Inggris (dan CSV data untuk gabungan), serta rujukan ke `manifest_grafik_garis_runtime.json`. Jangan mengubah isi README lain.

6. **Laporkan.** Ringkas berkas yang dibuat, hasil pemeriksaan hash dan T36, temuan visual, dan `git status --short`. Tanyakan kepada Bhre apakah grafik boleh di-*commit* dan di-push, serta apakah ke-15 log `jendela_runtime.csv` boleh ikut diunggah.

## Cara membaca grafik

- Latensi adalah `end_to_end_ms` per frame yang dirata-ratakan per bin 2 detik. FPS adalah jumlah frame diterima dalam bin dibagi 2, dihitung dari timestamp kamera, bukan kebalikan latensi.
- CPU adalah nilai `psutil` untuk proses detektor dalam persen satu CPU logis, sehingga dapat melebihi 100%. RSS adalah memori resident proses detektor, bukan total RAM robot.
- Run tidak dijalankan bersamaan dan berbentuk blok lintas 2–3 November. Tiga student berarsitektur identik, sehingga selisih di antara mereka tidak ditafsirkan sebagai efek metode; perbandingan teacher dengan student lebih kuat. Analisis tetap deskriptif sesuai audit T36/T37.
