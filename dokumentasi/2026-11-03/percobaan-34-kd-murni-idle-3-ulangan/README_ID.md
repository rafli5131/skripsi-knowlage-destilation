# Percobaan 34 — KD murni idle

Tiga ulangan idle KD murni seed 42 selesai sesuai permintaan operator, tanpa konfirmasi antarulangan. Preview SSH-X dipakai selama pengukuran; tidak ada perintah gerak robot. Tiap folder menyimpan screenshot, telemetry, metrik dan grafik.

Ulangan [1](04-kd-murni/idle-u1/README_ID.md), [2](04-kd-murni/idle-u2/README_ID.md), dan [3](04-kd-murni/idle-u3/README_ID.md) lulus cek otomatis CSV/telemetry. Rerata ± simpangan baku sampel tiga run: latensi **74,09 ± 1,04 ms**, FPS **12,07 ± 0,05**, CPU **1300,21 ± 2,44% satu CPU logis**, dan RSS **356,97 ± 5,92 MiB**. Total 2.172 frame ukur tanpa error; ketiga kelas memiliki keluaran pada seluruh frame. Ini cakupan prediksi, bukan akurasi berlabel.

[Tabel tiga run](05-ringkasan/tabel_3_run.csv), [agregat](05-ringkasan/tabel_agregat_saat_ini.csv), [grafik HD bahasa Indonesia](04-kd-murni/grafik_kd42_idle_ulangan_1_2_3_hd.png), dan [grafik bahasa Inggris](04-kd-murni/graph_kd42_idle_repetitions_1_2_3_hd.png) tersedia. Kondisi torque tidak dibaca langsung saat manager menguasai bus; foto luar, pengukuran jarak, serta frame mentah referensi sebelum/sesudah tidak dikumpulkan pada sesi ini. Suhu CPU akhir tiap run tidak tersimpan tepat setelah jendela. Audit akhir kesetaraan protokol masih diperlukan.

Matriks kampanye sekarang **21/24 slot** lulus cek otomatis; tiga slot KD murni berjalan tersisa. Preview KD murni kembali aktif setelah ulangan 3.
