# Preview gawang: confidence deteksi terakhir

Package ini memakai `op3_goal_continuity` sebagai shared tanpa mengubah package lama. Kotak deteksi asli menampilkan confidence pada frame terkini. Saat hanya template visual yang cocok, kotak oranye menampilkan `GAWANG ESTIMASI`, usia sejak deteksi, dan `CONF TERAKHIR ... (BUKAN SAAT INI)`. Nilai tersebut milik deteksi terakhir, bukan prediksi baru; kesamaan template bukan confidence detektor. Jumlah deteksi aktual dan metrik tidak ditambah, dan output tidak digunakan sebagai mAP, ground truth, atau benchmark.

```bash
cd /home/humanoid/bre_skripsi
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
export PYTHONPATH="$PWD/ros2_packages/op3_goal_last_confidence:$PWD/ros2_packages/op3_goal_continuity:$PWD/ros2_packages/op3_fullscreen_preview:$PYTHONPATH"
python -m op3_goal_last_confidence --model teacher --conf 0.25 --iou 0.45 --imgsz 640 --topic /thesis/image_raw --threads 4 --preview-fps 5
```

Model harus terlebih dahulu mendeteksi gawang; template hilang saat preview dimulai ulang. Estimasi tidak menjamin objek masih ada. Tidak ada perintah servo atau perekaman otomatis.
