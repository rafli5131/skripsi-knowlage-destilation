# Teacher, idle ulangan 2 (pengganti)

Tanggal 2 November 2026. Run ID `20261102_eq_teacher_idle_u2`. Pengulangan pertama dengan ID ini diganti sesuai permintaan Bhre setelah deteksi gawang terlewat; berkas mentah ulangan baru ada di `runs/op3_pytorch/20261102_eq_teacher_idle_u2.{csv,json}` dan `20261102_eq_teacher_idle_u2_detections.csv`.

Model teacher FP32 SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Kamera `/thesis/image_raw` 640×480; BoT-SORT dan preview SSH-X aktif; confidence 0,25, NMS IoU 0,45; PyTorch 4 thread intra-op/2 inter-op. `op3_manager` aktif dengan `auto_start_init_pose=false`. Kepala tidak diberi perintah gerak.

| Metrik jendela 60 detik | Hasil |
| --- | ---: |
| Frame ukur | 614 |
| Error frame | 0 |
| Latensi total rata-rata | 92,15 ms |
| Latensi total P95 | 181,84 ms |
| FPS efektif dari timestamp kamera | 10,24 frame/detik |
| CPU proses rata-rata | 1349,11% dari satu CPU logis; 84,32% dari 16 CPU logis |
| RAM proses RSS rata-rata | 369,66 MiB |
| Frame tanpa deteksi bola/gawang/robot | 0/0/0 |
| Simpangan kepala terbesar pada sampel | 0 rad |
| Simpangan badan terbesar pada sampel | 0,001535 rad |

Data sumber dan status cek otomatis: [summary_metrics.json](summary_metrics.json). Grafik 2160×1800 piksel: [latensi, CPU, dan RAM](grafik_runtime_hd.png). Bukti adegan: [preview sebelum run](../../00-persiapan/preview_sebelum_u2_ulang.png) dan [preview sesudah run](preview_setelah_run.png). Telemetry tersedia pada `telemetry_pre.txt`, `telemetry_mid1.txt`, `telemetry_mid2.txt`, dan `telemetry_after.txt`.

Keluaran kelas di atas menunjukkan cakupan detektor, bukan akurasi terhadap label manual. `telemetry_mid1.txt` mencatat peringatan kehilangan beberapa pesan ROS sebelum sampel JointState berhasil diperoleh. Pemeriksaan otomatis CSV dan telemetry lulus; audit akhir kontinuitas preview dan suhu awal/akhir belum lengkap. Gambar overlay dari jendela ukur tidak tersimpan karena percobaan capture dimulai setelah detektor selesai; kedua gambar preview hanya menunjukkan adegan sebelum dan sesudah run.
