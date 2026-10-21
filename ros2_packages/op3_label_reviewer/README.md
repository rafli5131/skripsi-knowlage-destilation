# Peninjau label kamera OP3 (SSH-X)

Package baru ini menampilkan satu jendela berisi JPEG dan kotak dari `labels_auto/`. Paket runtime/ROS lama tidak diubah. Tidak membuka kamera atau mengendalikan robot.

Dari root repository:

```bash
source .venv-op3-pytorch/bin/activate
PYTHONPATH="$PWD/ros2_packages/op3_label_reviewer" python -m op3_label_reviewer \
  --session-dir data/op3_camera_eval/sessions/20261021_idle_01 \
  --reviewer NAMA_ATAU_INISIAL
```

SSH dengan `-X` memerlukan `$DISPLAY` yang berfungsi. `--reviewer` boleh dihilangkan: saat pertama kali menekan `S`, ketik nama/inisial langsung di jendela lalu tekan Enter. Tindakan itu menyimpan hanya frame yang sedang diperiksa. Esc membatalkan pengisian nama tanpa menyimpan.

Tombol `N`/`D` atau panah kanan maju; `P`/`A` atau panah kiri mundur. Klik kotak untuk memilih, lalu `Delete` menghapusnya. Untuk memperbaiki posisi, hapus kotak dan tarik kotak baru pada gambar. Tombol `0`, `1`, `2` memilih kelas `ball`, `gawang`, `robot` dan mengubah kelas kotak yang sedang dipilih. `R` membatalkan perubahan yang belum disimpan. **Tekan `S` setelah benar-benar memeriksa setiap gambar**, termasuk jika labelnya kosong; hanya frame itu yang disimpan ke `labels_reviewed/`. `Q`/Esc menutup jendela. Navigasi atau keluar akan ditahan jika ada perubahan belum disimpan.

Jumlah frame yang sudah ditinjau terlihat di panel kanan. `labels_auto/` dan JPEG tidak diubah. `labels_reviewed/review_log.jsonl` mencatat nama peninjau dan waktu setiap penyimpanan. Jika gambar belum diperiksa manusia, jangan tekan `S`; keberadaan kotak otomatis saja bukan ground truth. Jangan hitung mAP/precision/recall/F1 sebelum semua frame selesai dan label final diverifikasi.

Jika sesi GUI terhenti sebelum menyimpan edit pada frame pertama percobaan 21 Oktober, draf pemulihan tersedia di `data/op3_camera_eval/sessions/20261021_idle_01/review_recovery/frame_000001.txt`, bersama screenshot jendela lama dan catatan asal. Buka kembali dengan `--recover-draft` menunjuk file itu. Periksa lagi kotak `gawang` sebelum menyimpan; draf pemulihan ini **belum** berstatus label final.
