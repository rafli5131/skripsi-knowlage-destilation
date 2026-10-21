# Peninjau gabungan beberapa sesi OP3 (SSH-X)

Package ini memakai `op3_label_reviewer` sebagai shared code tanpa mengubahnya. Ketiga sesi tetap memiliki `images/`, `labels_auto/`, dan `labels_reviewed/` sendiri. Nomor frame pada jendela berjalan terus dari 1 sampai 120; setelah frame 40 dan 80, tombol `N` maju ke sesi berikutnya. `S` menyimpan hanya frame yang sedang dilihat ke `labels_reviewed/` sesi asal dan mencatat peninjau pada `review_log.jsonl`.

Dari root repository:

```bash
source .venv-op3-pytorch/bin/activate
PYTHONPATH="$PWD/ros2_packages/op3_label_reviewer:$PWD/ros2_packages/op3_multi_session_reviewer" \
python -m op3_multi_session_reviewer \
  --session-dir data/op3_camera_eval/sessions/20261021_robot_ball_01 \
  --session-dir data/op3_camera_eval/sessions/20261021_robot_gawang_01 \
  --session-dir data/op3_camera_eval/sessions/20261021_gawang_ball_01 \
  --reviewer bhre
```

Tombol sama seperti peninjau lama: `N`/panah kanan maju, `P`/panah kiri mundur, klik kotak untuk memilih, `Delete` menghapus, tarik area kosong untuk menambah kotak, `0`/`1`/`2` memilih kelas `ball`/`gawang`/`robot`, `R` membatalkan edit yang belum disimpan, `S` menyimpan, dan `Q`/Esc keluar. Periksa **setiap** frame pada gambar resolusi penuh sebelum menekan `S`, termasuk frame tanpa kotak atau objek yang terpotong. Jika berhenti, jalankan ulang dengan `--start N` untuk memulai dari nomor frame global N. Gambar dan label otomatis tidak diubah; label otomatis tetap draf sampai disimpan oleh peninjau manusia.
