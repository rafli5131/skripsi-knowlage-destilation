# Percobaan 33 — Supervised berjalan

Ulangan [1](03-supervised/walk-u1/README_ID.md), [2](03-supervised/walk-u2/README_ID.md), dan [3](03-supervised/walk-u3/README_ID.md) selesai setelah konfirmasi operator per run dan lulus pemeriksaan otomatis CSV/telemetry. Ketiganya mendapat ack mulai/berhenti, dengan deviasi kepala maksimum satu count dari baseline guard. Preview Supervised dinyalakan kembali setelah gait berhenti.

Rerata ± simpangan baku sampel tiga run: latensi **70,80 ± 2,71 ms**, FPS **12,64 ± 0,52**, CPU proses **1301,13 ± 6,04% satu CPU logis**, dan RSS **359,16 ± 4,76 MiB**. Total 2.275 frame ukur tanpa error frame. [Tabel tiga run](05-ringkasan/tabel_3_run.csv), [agregat](05-ringkasan/tabel_agregat_saat_ini.csv), [grafik HD bahasa Indonesia](03-supervised/grafik_sup1337_walk_ulangan_1_2_3_hd.png), dan [grafik bahasa Inggris](03-supervised/graph_sup1337_walk_repetitions_1_2_3_hd.png) tersedia. Keluaran deteksi live bukan akurasi berlabel.

Kampanye kini **18/24 slot** lulus cek otomatis; enam slot KD murni idle/berjalan tersisa. Data ini belum menggantikan audit akhir protokol, termasuk kesetaraan adegan dan kondisi torque yang tidak dibaca langsung saat manager menguasai bus.

Bola dan robot muncul pada seluruh 2.275 frame ukur; gawang muncul pada 2.258/2.275 frame (99,25%) menurut keluaran model. Jumlah ini bukan precision atau akurasi. Preview tidak direkam sebagai video layar, sehingga kontinuitas tampilan tidak dapat diaudit per frame; data CSV dan screenshot disimpan. Suhu CPU akhir ulangan 3 tidak tersimpan tepat setelah run dan tidak dapat direkonstruksi sebagai pengukuran akhir.

Pada persiapan ulangan 1, proses guard pertama gagal import `robotis_controller_msgs` karena overlay ROS workspace belum dimuat. Proses itu gagal sebelum membuat artefak guard dan sebelum mengirim perintah gait. Guard dijalankan ulang setelah overlay dimuat, lalu menerima ack mulai dan berhenti. Tidak ada kode package yang diubah. Audit protokol akhir masih diperlukan.
