# KF-01 Menerima citra kamera OP3

**Kebutuhan:** sistem menerima citra dari kamera OP3 melalui ROS 2 dan memproses setiap
frame yang masuk; kesalahan pemrosesan frame dicatat.

**Implementasi:** node `scripts/op3_pytorch_detector.py` berlangganan ke topik
`/thesis/image_raw` (parameter `input_topic`). Frame yang gagal diproses dicatat pada kolom
`error` dan dihitung sebagai `frame_errors`, sementara node tetap berjalan.

**Prosedur:** 24 run live (4 model x diam/berjalan x 3 ulangan), jendela ukur 60 detik setelah
30 frame pemanasan. Jumlah frame dan error frame dibaca dari
[T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) lalu dicocokkan dengan
`summary_metrics.json` setiap run.

**Kriteria lulus:** frame terproses lebih dari nol, error frame sama dengan nol, dan angka T36
sama dengan ringkasan run.

**Hasil:** 24/24 run lulus. Total 17.090 frame terproses
tanpa error. Rincian: [`bukti_frame_dan_error_24_run.csv`](bukti_frame_dan_error_24_run.csv).

**Batas:** bukti ini menunjukkan frame yang sampai ke node diproses tanpa kesalahan. Frame yang
mungkin hilang sebelum sampai ke node tidak dihitung; jeda penerimaan maksimum tercatat pada
kolom `max_receive_gap_s` T36.

**Log pendukung** di [`../log/`](../log/README.md): `run_live_24/<run_id>/summary_metrics.json` (jumlah frame dan error per run) dan `jendela_runtime.csv` (kolom `error` per frame).
