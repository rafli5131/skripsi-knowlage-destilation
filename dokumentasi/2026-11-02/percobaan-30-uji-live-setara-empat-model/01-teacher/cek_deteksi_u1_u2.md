# Pemeriksaan keluaran deteksi teacher pada dua run idle

Sumber: CSV frame mentah `runs/op3_pytorch/20261102_eq_teacher_idle_u1.csv` dan `20261102_eq_teacher_idle_u2.csv`. Yang dihitung hanya jendela 60 detik setelah 30 frame warm-up dan jeda awal 5 detik. Nilai `n_ball`, `n_gawang`, `n_robot` bernilai nol berarti kelas tersebut tidak dikeluarkan detektor pada frame itu. Ini bukan ukuran akurasi karena frame run belum diberi label ground truth.

| Run | Frame ukur | Bola tidak terdeteksi | Gawang tidak terdeteksi | Robot tidak terdeteksi | Error frame |
| --- | ---: | ---: | ---: | ---: | ---: |
| Teacher idle u1 | 584 | 0 | 0 | 0 | 0 |
| Teacher idle u2 (pengganti) | 614 | 0 | 0 | 0 | 0 |

Ulangan u2 sebelumnya dibatalkan setelah gawang sering tidak terdeteksi. Sesuai instruksi Bhre, berkas CSV, JSON, log deteksi, dan telemetry u2 lama diganti oleh u2 baru dengan `run_id` yang sama. Hasil baru mendeteksi ketiga kelas pada semua 614 frame dalam jendela ukur. Berkas [preview sebelum pengulangan](../00-persiapan/preview_sebelum_u2_ulang.png) memperlihatkan tiga kotak; gambar ini diambil sebelum run, bukan dari jendela ukur. Pemeriksaan CSV dan empat sampel telemetry tidak menemukan error atau pergeseran kepala; status akhir masih memerlukan audit bukti preview sepanjang run dan suhu.
