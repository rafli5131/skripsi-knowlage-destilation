# Teacher, idle ulangan 3

Run ID `20261102_eq_teacher_idle_u3`, 2 November 2026. Teacher FP32 SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` pada kamera OP3 640×480; BoT-SORT dan preview SSH-X aktif, manager tanpa init pose otomatis. Input 640, confidence 0,25, NMS IoU 0,45, PyTorch 4/2 thread. Jendela ukur 60 detik sesudah warm-up 30 frame.

| Metrik | Hasil |
| --- | ---: |
| Frame ukur / error | 581 / 0 |
| Latensi callback rata-rata / P95 | 97,67 / 181,73 ms |
| FPS efektif timestamp kamera | 9,69 frame/detik |
| CPU proses rata-rata | 1337,67% dari satu CPU logis; 83,60% dari 16 CPU logis |
| RAM proses RSS rata-rata | 372,06 MiB |
| Frame tanpa deteksi bola/gawang/robot | 0/0/0 |
| Simpangan kepala/badan terbesar pada sampel | 0,001534 / 0,001535 rad |

Bukti: [summary_metrics.json](summary_metrics.json), [grafik runtime 2160×1800](grafik_runtime_hd.png), [gambar deteksi saat run](frame_deteksi_saat_run.png), [gambar sesudah jendela ukur](frame_deteksi_sesudah_jendela.png), dan empat berkas `telemetry_*.txt`. CSV/JSON mentah: `runs/op3_pytorch/20261102_eq_teacher_idle_u3.*`. Tiga objek terdeteksi pada seluruh frame jendela, tetapi angka ini bukan akurasi berlabel. Cek otomatis CSV/telemetry lulus; audit akhir suhu dan kontinuitas preview belum lengkap.
