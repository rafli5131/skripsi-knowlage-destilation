# op3_log_pelengkap

Package baca-saja untuk melengkapi log OP3 sesuai [`prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md`](../../prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md). Kedua skrip hanya memakai pustaka standar Python dan dijalankan di komputer OP3 dari root repositori robot. Keduanya menulis ke direktori keluaran baru di luar repositori, misalnya `/tmp/op3_log_pelengkap_<YYYYmmddTHHMMSSZ>/`, dan menolak berjalan bila direktori itu sudah ada. Tidak ada perintah kamera, ROS, servo, atau gait.

| Skrip | Isi |
|---|---|
| `ekstrak_jendela.py` | Mencocokkan SHA-256 log mentah dan metadata run live dengan T36, mengambil baris jendela ukur ke `jendela_runtime.csv` dan `jendela_deteksi.csv`, lalu memeriksa jumlah baris, error, rerata `end_to_end_ms`, dan FPS terhadap T36 (toleransi 1e-6). Hasil ditulis ke `status_ekstraksi.json`. |
| `salin_metadata.py` | Menyalin metadata sesi capture T38 dan T43 serta berkas teks training teacher. Gambar, folder `images/` dan `labels_*`, prediksi, berkas `.pt`, dan kode tidak disalin. Setiap berkas kandidat diperiksa isinya; berkas yang memuat koordinat kotak, prediksi, atau data gambar tersandi dicatat dan tidak disalin. Hasil ditulis ke `status_metadata.json`. |

Contoh pemakaian dari laptop:

```bash
ssh <alias> 'mkdir /tmp/op3_log_pelengkap_<stamp>'
scp ros2_packages/op3_log_pelengkap/*.py runs_15.json <alias>:/tmp/op3_log_pelengkap_<stamp>/
ssh <alias> 'cd /home/humanoid/bre_skripsi && python3 /tmp/op3_log_pelengkap_<stamp>/ekstrak_jendela.py \
  --runs /tmp/op3_log_pelengkap_<stamp>/runs_15.json --out /tmp/op3_log_pelengkap_<stamp>/live_24_run'
```

Hasil sesi 23 November 2026 ada di [`log_op3_pelengkap/`](../../log_op3_pelengkap/README.md).
