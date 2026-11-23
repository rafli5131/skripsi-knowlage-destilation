# Log lab server pelengkap (23 November 2026)

Salinan log mentah dari server lab (`labkc-l40-debian`) yang sebelumnya hanya ada di server dan tidak masuk Git. Diambil lewat `scp` dari laptop, hanya dibaca dari server, dan SHA-256 22 berkas dicocokkan dengan hasil `sha256sum` di server ([`manifest_sha256.json`](manifest_sha256.json)). Isi log diperiksa: tidak ada kata `wandb`, `token`, `password`, `secret`, atau kunci SSH. Satu-satunya jejak identitas adalah path `/mnt/nas-hpg9/dindarosyidah` dan satu rujukan `/mnt/nas-hpg9/rafli5131`.

| Folder | Isi |
|---|---|
| [`verifikasi_teacher_20261116/`](verifikasi_teacher_20261116/) | Log mentah verifikasi jalur TEST baris teacher (D24), 16 November 13:41-14:02 WIB, berakhir `EXIT=0`, beserta skrip pemicunya. Hasilnya ada di [`analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher/`](../analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher/RINGKASAN.md). |
| [`t42_server2/`](t42_server2/) | 18 log di `server2/logs/` (8 training mentah: 2 teacher dan 6 student; 10 evaluasi; `build_t42.log`) dan 2 log peluncur `run_server2_*.log`, dari ablasi teacher T42 pada 5-6 November. Hasilnya ada di [T42](../analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md). |

**Yang tidak ada.** Log mentah verifikasi jalur TEST 13 November (`/tmp/verif/verifikasi_jalur_test.log`) hilang karena server di-reboot pada 15 November 12:18 WIB. Isinya hanya baris progres per checkpoint dan cetakan `RINGKASAN.md`; hasilnya tetap lengkap di [`verifikasi_jalur_test_20261113/`](../analisis_performa/lab_server/verifikasi_jalur_test_20261113/RINGKASAN.md).

**Catatan `.gitignore`.** Pola `/runs/kd_teacher_ablation/*/logs/` dan `/runs/kd_teacher_ablation/run_*.log` mengabaikan log T42 di lokasi aslinya. Salinan di folder ini berada di luar `runs/`, sehingga ikut terlacak tanpa mengubah `.gitignore`.
