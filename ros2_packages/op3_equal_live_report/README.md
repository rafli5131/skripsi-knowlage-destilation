# Pelaporan uji live OP3

Package baru ini hanya membaca CSV detektor dan topic gambar overlay untuk dokumentasi. Ia tidak mengendalikan robot. `capture.py` menyimpan satu frame PNG dari `/vision/debug_image` tanpa detektor tambahan. `report.py` membuat tabel dan grafik per run serta grafik matriks 24 run dengan slot kosong tetap ditandai belum diukur.

Jalankan dari root repo dengan environment OP3 aktif:

```bash
export PYTHONPATH="$PWD/ros2_packages/op3_equal_live_report:$PYTHONPATH"
python -m op3_equal_live_report.report --session-dir dokumentasi/<tanggal>/<percobaan>
python -m op3_equal_live_report.capture dokumentasi/<tanggal>/<percobaan>/frame_deteksi.png
```

Grafik memakai PNG 180 DPI dengan tinggi 1800 piksel. Kriteria otomatis hanya meliputi CSV dan sampel telemetry; bukti preview dan suhu masih harus diaudit untuk menetapkan status protokol akhir.
