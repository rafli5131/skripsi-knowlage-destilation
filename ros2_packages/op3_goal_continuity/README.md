# Preview dengan estimasi kontinuitas gawang

Package baru ini menggunakan preview dan inferensi bersama `op3_fullscreen_preview`/`op3_live_monitor`, tanpa mengubah package lama dan tanpa menjalankan model kedua. Saat model mendeteksi gawang, kotak asli ditampilkan. Jika deteksi menghilang setelah pernah muncul, pencocokan template lokal mempertahankan kotak **oranye bertuliskan `GAWANG ESTIMASI`** selama pola gambar cocok; angka pada label adalah waktu sejak deteksi terakhir, bukan confidence. Jika template tidak cocok atau area kurang bertekstur, estimasi hilang dan sistem menunggu deteksi baru. Ini bukan bukti bahwa gawang tetap ada dan bisa keliru pada pola yang mirip.

Secara bawaan, estimasi bertahan selama template cocok. Untuk membatasi durasi tambahkan `--goal-max-age <detik>`; ambang kesamaan template dapat ditentukan dengan `--goal-match` (default 0,90). Nilai kesamaan ini bukan confidence deteksi. Confidence detektor diatur terpisah, default 0,25, dengan IoU NMS 0,45 dan `imgsz` 640 seperti preview standar. Jika model kembali mendeteksi gawang, kotak asli dan confidence deteksinya tampil seperti biasa. Perubahan ini hanya visualisasi preview: jumlah deteksi dan metrik model tidak menambahkan kotak estimasi, dan hasilnya tidak digunakan sebagai ground truth, mAP, atau benchmark. Tidak ada perintah servo atau perekaman otomatis.

```bash
cd /home/humanoid/bre_skripsi
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
export PYTHONPATH="$PWD/ros2_packages/op3_goal_continuity:$PWD/ros2_packages/op3_fullscreen_preview:$PYTHONPATH"
python -m op3_goal_continuity --model teacher --conf 0.25 --iou 0.45 --imgsz 640 --topic /thesis/image_raw --threads 4 --preview-fps 5
```

Kontrol preview: `1` kamera, `2` dashboard, `F` fullscreen, `Q`/Esc keluar. Model harus mendeteksi gawang setidaknya sekali sebelum estimasi dapat dimulai; template di memori dihapus saat preview dimulai ulang.
