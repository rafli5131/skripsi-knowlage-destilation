# Laporan runtime tracking OP3

Package baru ini membaca tiga log CSV/JSON dari sesi detektor OP3 yang **sudah berhenti** dan menghitung FPS, distribusi waktu proses, CPU/RAM proses, jumlah deteksi, cakupan ID, jeda deteksi, serta perubahan ID. Ia tidak membuka kamera, menjalankan model, atau menggerakkan robot; kode runtime lama tidak diubah.

Dari root repository:

```bash
source .venv-op3-pytorch/bin/activate
PYTHONPATH="$PWD/ros2_packages/op3_tracking_runtime_report" \
python -m op3_tracking_runtime_report \
  --run-dir runs/op3_pytorch \
  --run-id 20261021_tracking_live_01 \
  --output-dir runs/op3_tracking_runtime_report/NAMA_RUN_BARU
```

Output `summary.json`, `grafik_runtime.png`, dan `grafik_tracking.png` memakai log dari satu run yang sama dan menyimpan SHA-256 tiap sumber. `processed_fps` adalah frame sukses dibagi durasi proses menurut metadata; waktu callback mengukur pemrosesan node, sedangkan `camera_stamp_to_callback_start_ms` memakai selisih jam pada header kamera dan host. Persentase CPU berasal dari `psutil.Process.cpu_percent` dan dapat melebihi 100% pada proses multithread. ID tracker yang berubah setelah frame tanpa deteksi dicatat sebagai akuisisi ulang, bukan otomatis sebagai ID switch ground truth. Tidak ada MOTA/IDF1 tanpa anotasi identitas objek per frame.
