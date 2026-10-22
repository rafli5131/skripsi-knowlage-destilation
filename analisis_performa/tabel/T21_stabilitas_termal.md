# T21. catatan suhu servo dan status stabilitas termal

**Status: data suhu sesaat tersedia; stabilitas termal belum diuji.** Dua sesi tracking kepala menyimpan suhu servo saat preflight. Ini bukan suhu CPU/NUC dan bukan pengukuran kenaikan suhu selama beban berkelanjutan.

| Waktu / sesi | Sensor | Suhu | Konteks |
|---|---|---:|---|
| 2026-10-19T13:02:01.149133+00:00 / 20261019T130201Z_7ba2ef | Dynamixel ID 19 (head_pan) | 22 °C | single servo preflight snapshot before short head-tracking session; torque was off |
| 2026-10-19T13:02:01.149133+00:00 / 20261019T130201Z_7ba2ef | Dynamixel ID 20 (head_tilt) | 22 °C | single servo preflight snapshot before short head-tracking session; torque was off |
| 2026-10-19T13:04:00.306260+00:00 / 20261019T130400Z_74c464 | Dynamixel ID 19 (head_pan) | 25 °C | single servo preflight snapshot before short head-tracking session; torque was off |
| 2026-10-19T13:04:00.306260+00:00 / 20261019T130400Z_74c464 | Dynamixel ID 20 (head_tilt) | 25 °C | single servo preflight snapshot before short head-tracking session; torque was off |

Nilai sumber tersedia di [CSV](T21_stabilitas_termal.csv). Tidak ada time-series suhu CPU/NUC atau suhu servo sepanjang benchmark KD idle/walking. Karena log termal tidak diambil selama sesi 22 Oktober, kestabilan termal dan throttling tidak dapat disimpulkan.
