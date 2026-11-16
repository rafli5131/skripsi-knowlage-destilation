# T45 — rincian latensi dan diagnosis CPU OP3

Sebanyak 24 run dibaca dari log mentah dengan jendela dan filter yang sama seperti `op3_runtime_audit_24`. Rata-rata end-to-end setiap run cocok T36 pada toleransi 1e-6. Angka tabel berikut adalah **rerata seluruh frame yang digabung** dari tiga run; karena jumlah frame berbeda, nilai dapat sedikit berbeda dari rerata tiga rerata run T37. Median dan P95 per run serta per kelompok tersedia di [CSV](T45_rincian_latensi_dan_cpu_op3.csv).

| Model | Kondisi | Preprocess ms | Inference ms | Postprocess ms | Sisa ms | End-to-end ms | CPU % satu CPU logis | CPU % dari 16 CPU logis |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| teacher | idle | 5.43 | 76.55 | 0.83 | 13.37 | 96.17 | 1338.9 | 83.7 |
| teacher | walk | 5.69 | 76.79 | 0.84 | 12.51 | 95.84 | 1333.5 | 83.3 |
| hybrid1337 | idle | 4.13 | 45.28 | 0.85 | 14.42 | 64.67 | 1306.0 | 81.6 |
| hybrid1337 | walk | 4.98 | 51.06 | 0.95 | 14.42 | 71.41 | 1303.8 | 81.5 |
| sup1337 | idle | 5.57 | 53.14 | 0.95 | 13.40 | 73.06 | 1299.2 | 81.2 |
| sup1337 | walk | 5.05 | 50.13 | 0.96 | 14.59 | 70.73 | 1301.1 | 81.3 |
| kd42 | idle | 5.35 | 53.02 | 0.97 | 14.75 | 74.09 | 1300.2 | 81.3 |
| kd42 | walk | 5.28 | 52.57 | 0.96 | 13.83 | 72.63 | 1295.6 | 81.0 |

Sisa dihitung **per frame** sebagai end-to-end dikurangi tiga tahap Ultralytics. Di `scripts/op3_pytorch_detector.py`, timer end-to-end mencakup konversi pesan kamera, pemanggilan model/tracker, pembentukan dan penerbitan deteksi, `result.plot()`, konversi dan penerbitan gambar preview, serta penulisan/flush CSV deteksi sebelum timer berhenti. Pencatatan baris runtime terjadi sesudah timer. Di predictor Ultralytics terpasang, callback tracker `on_predict_postprocess_end` dipanggil **di luar** timer `postprocess`; gambar preview dan penerbitan ROS juga berada di luar tiga tahap `result.speed`. Karena itu sisa bukan waktu tracker murni.

## Replay CPU offline — 4/2 thread Torch diverifikasi

Replay memberi 300 frame sebagai array yang dimuat sebelumnya; set T43 berisi 260 gambar, sehingga frame diulang secara deterministik dan 30 frame awal digunakan untuk warm-up. Delapan varian utama diikuti dua kontrol tambahan OpenBLAS 1 thread. Semua varian membuat preview `result.plot()`, tetapi tidak mencakup konversi atau publikasi ROS, kamera, maupun log deteksi. Laju input adalah throughput replay tanpa jeda terjadwal; bukan FPS live T36/T37. CPU per frame dan persentase CPU dihitung dari waktu CPU proses/waktu dinding. Satu pengulangan per varian, urutan serial; pengambilan sampel thread menambah sedikit overhead.

| Model | Varian | CPU ms/frame | CPU % satu CPU logis | CPU % dari 16 | Laju replay frame/detik | Thread OpenCV | Maksimum thread teramati |
|---|---|---:|---:|---:|---:|---:|---:|
| Teacher | Tracking + preview | 599.4 | 977.1 | 61.1 | 16.30 | 1 | 22 |
| Teacher | Tanpa tracking | 147.3 | 399.7 | 25.0 | 27.13 | 1 | 22 |
| Teacher | Tracking + OpenCV 1 thread | 599.8 | 970.4 | 60.6 | 16.18 | 1 | 22 |
| Teacher | Tracking tanpa GMC | 556.8 | 1013.8 | 63.4 | 18.21 | 1 | 22 |
| Teacher | Tracking + OpenBLAS 1 thread | 186.7 | 399.5 | 25.0 | 21.40 | 1 | 7 |
| KD Hybrid | Tracking + preview | 392.4 | 965.7 | 60.4 | 24.61 | 1 | 22 |
| KD Hybrid | Tanpa tracking | 71.3 | 400.0 | 25.0 | 56.10 | 1 | 22 |
| KD Hybrid | Tracking + OpenCV 1 thread | 348.9 | 958.1 | 59.9 | 27.46 | 1 | 22 |
| KD Hybrid | Tracking tanpa GMC | 303.6 | 1012.3 | 63.3 | 33.34 | 1 | 22 |
| KD Hybrid | Tracking + OpenBLAS 1 thread | 113.3 | 399.3 | 25.0 | 35.24 | 1 | 7 |

Rincian waktu CPU dan nama masing-masing thread ada pada [CSV thread](T45_cpu_thread_replay.csv). Pembacaan thread dilakukan sekali per frame; thread sangat singkat dapat terlewat sehingga jumlah waktu per thread adalah batas bawah. Hanya satu percobaan per varian: perbedaan menunjukkan asosiasi dalam replay, bukan estimasi kausal pasti untuk seluruh 24 run.

## Pengaturan thread dan percobaan awal

Seluruh metadata T36 mencatat Torch 4 intra-op, 2 inter-op, BoT-SORT `botsort.yaml`, tracking dan preview aktif; file terpasang menggunakan `gmc_method: sparseOptFlow`. Isi lengkap [salinan konfigurasi tracker](../../dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3/botsort_terpasang.yaml) disertakan untuk audit. Metadata node dicatat saat inisialisasi sebelum inferensi pertama. Pada replay awal, pemanggilan CPU pertama melalui `ultralytics.utils.torch_utils.select_device` mengubah intra-op menjadi 8 (`NUM_THREADS`); karena tidak memenuhi syarat replay 4/2, data berikut dipertahankan sebagai **percobaan awal**, bukan varian 4/2 di atas:

| Model | Varian awal | Torch intra-op setelah inisialisasi | CPU % satu CPU logis | CPU ms/frame |
|---|---|---:|---:|---:|
| KD Hybrid | Tracking + OpenCV 1 thread | 8 | 1259.6 | 679.0 |
| KD Hybrid | Tanpa tracking | 8 | 799.7 | 224.8 |
| KD Hybrid | Tracking + preview | 8 | 1261.6 | 744.0 |
| Teacher | Tracking + OpenCV 1 thread | 8 | 1280.7 | 956.7 |
| Teacher | Tracking tanpa GMC | 8 | 1362.0 | 781.8 |
| Teacher | Tanpa tracking | 8 | 800.0 | 370.7 |
| Teacher | Tracking + preview | 8 | 1216.1 | 1077.8 |

Replay utama mengembalikan intra-op menjadi 4 setelah inisialisasi backend dan memverifikasinya selama setiap frame. Ini menjelaskan mengapa metadata pra-inferensi saja belum membuktikan jumlah thread saat 24 run asli; tidak ada pengukuran langsung jumlah thread aktual pasca-inferensi pada run historis, sehingga penyebab pasti CPU historis tetap belum pasti. Konfigurasi OpenCV terukur sesudah impor Ultralytics adalah 1 thread, dan varian satu thread harus dibaca dengan fakta ini. Pada proses uji terpisah dengan urutan import seperti node, NumPy OpenBLAS default terukur 16 thread; kontrol tambahan membatasi OpenBLAS ke satu thread melalui environment sebelum impor dan mencatat nilai aktual satu. CPU replay tracking turun dibanding kontrol awal, menunjukkan OpenBLAS sebagai faktor besar dalam replay ini. Jumlah OpenBLAS aktual pada 24 run historis tidak direkam; hasil tidak membuktikan penyebab tunggal pada run historis.

Perbandingan latensi teacher dengan angka skripsi Ivan belum dapat disimpulkan: definisi waktu, perangkat, model, dan prosedur pada sumber Ivan belum diverifikasi. Tidak ada pengaturan robot atau hasil T36/T37 yang diubah.
