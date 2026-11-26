# Video Teacher YOLO11n kondisi diam

Pada 26 November 2026 sekitar 20.48 WIB operator secara eksplisit meminta perekaman Teacher, setelah sebelumnya memilih melewatinya. Operator mengonfirmasi badan/kepala ditopang serta area kosong, dan setelah persiapan menyatakan pose stabil serta arah kamera sesuai. Tidak ada perintah start gait. Manager mengirim torque-on saat inisialisasi; status torque per servo tidak dibaca ulang secara langsung saat manager menguasai bus. [Persiapan servo dan guard bahu terhenti](../persiapan-teacher-siap-jalan-drtwiaor/README.md) dicatat terpisah.

- `preview_deteksi_langsung.mp4`: keluaran preview beranotasi 10 detik, 640×480, 100 frame pada 10 fps. Recorder melaporkan 12 frame mengulang hasil inferensi sebelumnya. Ini bukan screen record desktop atau benchmark.
- `screenshot_awal.png`, `screenshot_tengah.png`, `screenshot_akhir.png`: cuplikan 2, 5, dan 8 detik. Pada ketiganya bola, gawang parsial, dan robot ditandai dengan kotak deteksi aktual; seluruh frame video belum diaudit.
- `recording_stats.json`, `pasca_rekaman.json`, `ffmpeg.log`, dan `manifest.json`: status recorder, telemetry pascarekaman, log, metadata, dan hash.

Preview menggunakan confidence 0,25, IoU 0,45, dan input 640. Ia juga dapat menggambar `GAWANG ESTIMASI` bila deteksi tidak ada; label `CONF TERAKHIR` mengacu pada deteksi sebelumnya, bukan frame saat ini. Estimasi tidak ditambahkan ke jumlah deteksi aktual atau dipakai sebagai ground truth. Pemeriksaan pascarekaman lima detik menunjukkan kepala terakhir 2021/1886 count dan rentang masing-masing satu count; ini tidak membuktikan sama sekali tidak ada gerak. Confidence bukan akurasi; video bukan evaluasi mAP. Video dan data tersimpan lokal.
