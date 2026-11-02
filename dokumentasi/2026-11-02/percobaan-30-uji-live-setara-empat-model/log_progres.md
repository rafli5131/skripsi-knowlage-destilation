# Log progres percobaan 30 — 2 November 2026

Cap waktu di bawah adalah awal **jendela ukur UTC**, bukan waktu mulai node. Status `lulus_cek_otomatis` berasal dari CSV/telemetri dan belum menyatakan audit protokol akhir selesai. [Jadwal dan ID run lengkap](jadwal_run.csv) · [pemetaan slot aktif teacher berjalan](active_run_sources.json) · [log penyimpangan dan batas seleksi](log_penyimpangan.md).

| Urutan waktu | Model/kondisi | Slot | Awal jendela UTC | Run mentah | Status |
|---:|---|---:|---|---|---|
| 1 | Teacher idle | 1 | 10:56:52 | `20261102_eq_teacher_idle_u1` | Lulus cek otomatis |
| 2 | Teacher idle | 2 | 11:13:51 | `20261102_eq_teacher_idle_u2` | Lulus cek otomatis |
| 3 | Teacher idle | 3 | 11:23:11 | `20261102_eq_teacher_idle_u3` | Lulus cek otomatis |
| 4 | Teacher berjalan | 1 aktif | 11:49:38 | `20261102_eq_teacher_walk_u3` | Lulus cek otomatis; raw u3 set lama dipilih sebagai slot u1 aktif |
| 5 | Teacher berjalan | 2 aktif | 12:04:11 | `20261102_eq_teacher_walk_retest_u2` | Lulus cek otomatis |
| 6 | Teacher berjalan | 3 aktif | 12:10:06 | `20261102_eq_teacher_walk_retest_u3` | Lulus cek otomatis |
| 7 | KD Hybrid idle | 1 | 12:44:04 | `20261102_eq_hybrid1337_idle_u1` | Lulus cek otomatis |
| 8 | KD Hybrid idle | 2 | 12:47:50 | `20261102_eq_hybrid1337_idle_u2` | Lulus cek otomatis |
| 9 | KD Hybrid idle | 3 | 12:51:40 | `20261102_eq_hybrid1337_idle_u3` | Lulus cek otomatis |

Enam run teacher dan tiga run Hybrid idle mengisi **9/24 slot**. Masih ada **15 slot**. Set teacher berjalan lama di luar pemetaan aktif tetap tersimpan di [arsip](01-teacher/arsip-set-sebelumnya-20261102-1200/); semua raw ID serta cap waktunya dipertahankan. Urutan blok model menyimpang dari rotasi pada prompt; perbandingan antarmodel bersifat deskriptif.

Hasil dan visual: [tabel 24 slot](05-ringkasan/tabel_24_run.csv), [agregat sementara](05-ringkasan/tabel_agregat_saat_ini.csv), [grafik matriks 2880×1800](05-ringkasan/grafik_24_run_ulangan_1_2_3_hd.png), [teacher ID](01-teacher/README_ID.md) / [EN](01-teacher/README_EN.md), dan [KD Hybrid ID](02-kd-hybrid/README_ID.md) / [EN](02-kd-hybrid/README_EN.md). Screenshot overlay dan telemetry berada dalam folder masing-masing run. **T36/T37/T38 belum final.** Frekuensi deteksi serta confidence live bukan akurasi berlabel.
