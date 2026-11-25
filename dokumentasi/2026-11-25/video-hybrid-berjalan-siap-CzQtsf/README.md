# Video deteksi KD Hybrid saat gait

Pada 25 November 2026 sekitar 21.10 WIB operator menyatakan robot siap dan mengonfirmasi mulai. Preview menampilkan KD Hybrid full seed 1337. Parameter gait dibaca dengan amplitudo maju/samping/putar nol (melangkah di tempat); perpindahan fisik aktual tidak diukur.

- `video/preview_deteksi_langsung.mp4`: video beranotasi 10 detik, 640×480, 100 frame pada 10 fps. Recorder melaporkan 10 frame mengulang hasil inferensi sebelumnya. Video ini adalah keluaran deteksi yang direkam langsung, bukan screen record X11 atau benchmark.
- `screenshot_awal.png`, `screenshot_tengah.png`, `screenshot_akhir.png`: cuplikan pada 2, 5 dan 8 detik. Pada ketiganya terlihat deteksi bola, gawang parsial, dan robot; seluruh frame tidak diaudit.
- `guard/gait_guard.json`, `guard/head_samples.csv`, `guard/pasca_stop.json`: respons start/stop, sampel telemetry dan pemeriksaan sesudah stop.
- `video/recording_stats.json`, `video/ffmpeg.log`, `manifest.json`: status recorder, log dan metadata/hash.

Pengendali memberikan ack start dan stop. Selama rekaman, 11 sampel telemetry berjarak sekitar satu detik menunjukkan variasi sudut lutut kiri 0,6108 rad dan kanan 0,5844 rad; ini mendukung adanya gerakan kaki, tanpa mengukur jarak berjalan. Kepala tidak diberi perintah gerak oleh guard; modul kepala `none` dan perubahan pembacaan maksimum dua count dari baseline. Pembacaan dua count tidak menjamin tidak ada gerakan sama sekali. Setelah stop, telemetry lima detik menunjukkan rentang sudut setiap kaki sekitar 0,00153–0,00307 rad dan pembacaan terakhir ID 19/20 2191/1793 count.

Persiapan sebelumnya sempat dihentikan oleh guard lama yang terpicu sekitar dua count; rincian pada `../persiapan-jalan-hybrid-terhenti-8MJIk8/`. Guard baru mempertahankan batas dua count memakai konversi encoder spesifik device dan telah diuji sintetis. Pencatatan ini hanya dokumentasi; confidence bukan akurasi, dan sesi tidak menghasilkan mAP atau metrik benchmark.
