# Video deteksi Supervised saat gait

Pada 25 November 2026 sekitar 21.31 WIB operator mengonfirmasi robot siap dan menyetujui gait serta rekaman. Preview menjalankan Supervised seed 1337 pada `/thesis/image_raw`. Parameter gait yang dibaca pada sesi sebelumnya menetapkan amplitudo maju, samping, dan putar nol (melangkah di tempat); perpindahan fisik aktual tidak diukur.

- `video/preview_deteksi_langsung.mp4`: keluaran deteksi beranotasi 10 detik, 640×480, 100 frame pada 10 fps, dengan 10 frame yang mengulang hasil inferensi sebelumnya. Ini bukan screen record desktop atau benchmark.
- `screenshot_awal.png`, `screenshot_tengah.png`, `screenshot_akhir.png`: cuplikan pada 2, 5, 8 detik. Bola, gawang parsial, dan robot terdeteksi pada ketiganya; seluruh frame tidak diaudit. Gawang dan robot sebagian terpotong, dan teks confidence bola kurang jelas karena melampaui latar label.
- `guard/gait_guard.json`, `guard/head_samples.csv`, `guard/pasca_stop.json`: laporan start/stop, telemetry, dan pemeriksaan setelah stop.
- `video/recording_stats.json`, `video/ffmpeg.log`, dan `manifest.json`: status dan metadata video.

Start dan stop menerima ack dari pengendali. 11 sampel telemetry menunjukkan rentang sudut lutut kiri 0.6461 rad dan kanan 0.6673 rad; ini mendukung adanya gerakan kaki, bukan pengukuran jarak. Modul kepala tetap `none` sebelum gait, guard tidak memerintahkan posisi kepala, dan perubahan pembacaan maksimum dua count dari baseline; ini tidak menjamin kepala sama sekali tidak bergerak. Pada pemeriksaan lima detik setelah stop, rentang tiap sendi kaki 0–0,00307 rad.

Confidence bukan akurasi, dan hasil sesi ini bukan pengukuran mAP atau benchmark. Video dan dokumentasi tersedia dalam repositori.
