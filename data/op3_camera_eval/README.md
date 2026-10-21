# Dataset evaluasi kamera OP3

Folder ini untuk **frame asli dari kamera OP3** dan anotasi tiga kelas. Data sesi berada di `sessions/<session_id>/` dan tidak otomatis masuk Git.

```text
data/op3_camera_eval/
└── sessions/<session_id>/
    ├── images/                  # frame kamera mentah, tanpa overlay deteksi
    ├── capture_frames.jsonl     # waktu dan ukuran setiap frame
    ├── capture_manifest.json    # kondisi dan topic sesi
    ├── labels_auto/             # hasil prediksi model; DRAF, bukan ground truth
    │   ├── frame_000001.txt     # format YOLO: class x_center y_center width height
    │   ├── predictions.jsonl    # confidence dan koordinat prediksi
    │   └── prelabel_manifest.json
    └── labels_reviewed/         # label setelah diperiksa/dikoreksi manusia
```

Urutan kelas tetap `0: ball`, `1: gawang`, `2: robot`. Setiap gambar harus diperiksa, termasuk yang file label otomatisnya kosong. Koreksi kelas, kotak, objek yang terlewat, dan deteksi palsu; simpan hasil di `labels_reviewed/` dengan nama dasar yang sama dengan gambar. File kosong berarti tidak ada objek target setelah pemeriksaan. Jangan menghitung mAP, precision, recall, atau F1 dari `labels_auto/` sebagai kebenaran acuan.

Contoh `session_id`: `20261022_idle_01` dan `20261022_walking_01`. Jangan campurkan kondisi idle dan berjalan dalam satu sesi. Frame yang terlalu mirip dari video berurutan tetap berkorelasi; catat lokasi, pencahayaan, jarak, dan adegan agar batas generalisasi hasil bisa dijelaskan. Evaluasi ini berlaku untuk frame OP3 yang dikumpulkan dan ditinjau, bukan otomatis untuk semua keadaan pertandingan.

Gunakan [prompt monitoring dan capture bersamaan](../../prompt/PROMPT_MONITOR_DAN_REKAM_KAMERA_OP3_BERSAMAAN.md) bila ingin melihat deteksi saat frame disimpan. [Prompt pengumpulan dan label OP3](../../prompt/PROMPT_KUMPUL_FRAME_DAN_LABEL_OP3.md) memberi alur capture tersendiri. [Prompt live tracking](../../prompt/PROMPT_UJI_LIVE_KAMERA_TRACKING_OP3.md) dipakai terpisah untuk menilai alur dan ID tracking tanpa proses capture tambahan.
