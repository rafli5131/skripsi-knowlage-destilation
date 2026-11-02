# Teacher, idle ulangan 1

Run ID `20261102_eq_teacher_idle_u1`, 2 November 2026. Teacher FP32 dijalankan pada kamera OP3 640×480 dengan BoT-SORT dan preview SSH-X aktif; manager berjalan tanpa init pose otomatis. Jendela ukur 60 detik sesudah warm-up 30 frame.

Pada 584 frame ukur, tidak ada error atau frame tanpa deteksi bola, gawang, maupun robot. Latensi callback rata-rata 98,91 ms, P95 180,21 ms, FPS efektif kamera 9,72, CPU proses rata-rata 1329,91% dari satu CPU logis, dan RSS 370,03 MiB. Simpangan kepala pada empat sampel telemetry 0 rad; simpangan badan terbesar 0,001535 rad.

Bukti: [summary_metrics.json](summary_metrics.json), [grafik runtime 2160×1800](grafik_runtime_hd.png), empat berkas `telemetry_*.txt`, dan CSV/JSON mentah `runs/op3_pytorch/20261102_eq_teacher_idle_u1.*`. Screenshot overlay khusus run ini tidak tersimpan. Pemeriksaan otomatis CSV/telemetry lulus; kontinuitas preview dan suhu perlu audit akhir. Cakupan deteksi bukan akurasi berlabel.
