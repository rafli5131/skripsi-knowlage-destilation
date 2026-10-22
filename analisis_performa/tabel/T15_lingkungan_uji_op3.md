# T15. lingkungan uji OP3

**Status: lingkungan NUC tercatat.** Snapshot sistem dikumpulkan pada 22 Oktober 2026 dari host `humanoid-NUC12WSHi5`, yang juga tercatat memakai kernel dan runtime yang sama pada metadata benchmark 22 Oktober. Governor dan mode daya adalah snapshot host, bukan telemetry tersimpan per frame.

| Field | Nilai | Status / sumber |
|---|---|---|
| CPU | 12th Gen Intel Core i5-1240P | Catatan operator; memory 2026-10-19 |
| Core fisik / thread logis | 12 / 16 | Snapshot NUC; JSON benchmark mencatat 16 CPU logis |
| RAM terpasang | 7.33 GiB | Snapshot NUC |
| Arsitektur / OS / kernel | x86_64 / Ubuntu 24.04.5 LTS / 7.0.0-38-generic | Metadata run dan catatan host |
| Governor / mode daya | `powersave`; `intel_pstate active`, turbo diizinkan | Snapshot NUC 22-10-2026 |
| Python / PyTorch / Ultralytics / OpenCV | 3.12.3 / 2.4.1+cpu / 8.4.130 / 4.11.0 | Metadata benchmark |
| ROS 2 | Jazzy | Catatan operator |
| Kamera / resolusi / format | Logitech C920 / 640×480 / YUYV, ROS `rgb8` | Catatan konfigurasi sesi |
| Kamera diminta / topik | 30 FPS / `/thesis/image_raw` | Konfigurasi; 30 FPS bukan throughput detektor terukur |
| Inferensi | CPU FP32 | Metadata run |

Nilai detail dan sumber tiap field tersedia di [CSV](T15_lingkungan_uji_op3.csv). Snapshot NUC ini mendeskripsikan perangkat pengujian; ia tidak membuktikan governor/mode daya konstan sepanjang sesi historis.
