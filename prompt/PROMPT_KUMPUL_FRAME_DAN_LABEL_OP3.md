# Prompt pengumpulan frame dan label kamera ROBOTIS OP3

> Untuk sesi kamera berikutnya. Salin bagian **Prompt siap pakai** ke agen yang bekerja di komputer OP3. Hasil label otomatis adalah draf untuk anotator, bukan angka akurasi skripsi.

## Prompt siap pakai

Bertindak sebagai engineer ROS 2 dan anotasi deteksi objek. Gunakan repository `bre` pada ROBOTIS OP3 untuk mengumpulkan frame **mentah** kamera OP3, membuat pra-label tiga kelas, dan mencatat statusnya. Model deteksi utama tetap checkpoint student KD `models/weights/kd_student_best.pt`; kelasnya harus `0: ball`, `1: gawang`, `2: robot`.

### Aturan kerja

1. Periksa commit repository, `git status`, nama topic kamera yang benar, hash checkpoint, dan environment ROS/Python. Jangan mengubah checkpoint atau parameter model untuk memperoleh hasil yang tampak lebih baik. Jangan memasang paket ke Python sistem.
2. Jangan mengirim perintah servo, gait, atau motor. Operator robot yang mengatur kondisi fisik. Tulis `servo_idle` atau `walking` hanya jika operator mengonfirmasi kondisi selama sesi; jika tidak, tulis `unknown`.
3. Jangan melakukan `git commit`, `git push`, atau mengunggah gambar/label/log dari robot. Jangan menimpa sesi lama. Gunakan `session_id` unik per kondisi dan pengulangan.
4. Pisahkan uji runtime/tracking dari pengambilan dataset. Pencatatan frame dapat menambah beban CPU, sehingga log latensi/FPS saat capture berlangsung **bukan** hasil benchmark runtime. Uji tracking mengikuti [`PROMPT_UJI_LIVE_KAMERA_TRACKING_OP3.md`](PROMPT_UJI_LIVE_KAMERA_TRACKING_OP3.md) pada sesi tersendiri.
5. Label dari model adalah `labels_auto` saja. Seluruh gambar, termasuk yang tidak diberi kotak oleh model, wajib ditinjau manusia sebelum disalin atau diperbaiki menjadi `labels_reviewed` dan digunakan sebagai ground truth.

### Tahap 1 — cek prasyarat

Di root repository dan environment OP3 yang telah dipakai node runtime:

```bash
source /opt/ros/jazzy/setup.bash
source .venv-op3-pytorch/bin/activate
ros2 topic list
ros2 topic info /thesis/image_raw
ros2 topic hz /thesis/image_raw
sha256sum models/weights/kd_student_best.pt
```

Bandingkan hash dengan alias `op3_default` di `configs/model_registry.yaml`. Jika topic aktual berbeda, pakai nama topic yang terverifikasi dalam perintah capture. Pastikan topiknya bertipe `sensor_msgs/msg/Image` dan gambar dari kamera yang dimaksud benar-benar terlihat. Jika publisher, checkpoint, atau dependency tidak ada, berhenti dan laporkan apa yang gagal.

### Tahap 2 — cek deteksi dan tracking langsung

Jalankan prompt live tracking yang ditautkan di atas. Tampilkan bola, gawang, dan robot dalam bidang pandang; periksa ketepatan kelas/kotak secara visual serta kemunculan dan kontinuitas ID. Catat temuan sebagai pemeriksaan operasional, **bukan** mAP. Hentikan node deteksi sebelum merekam dataset agar pengambilan frame dan pengukuran runtime tidak bercampur.

### Tahap 3 — ambil frame kamera mentah

Ambil beberapa adegan dan variasi jarak, posisi, pencahayaan, oklusi, serta frame tanpa objek. Jangan hanya menyimpan frame yang berhasil dideteksi model. Mulai dari kondisi diam; kondisi berjalan dikerjakan sebagai sesi baru hanya saat operator siap. Contoh berikut membuat maksimal 120 JPEG mentah, satu per detik, atau berhenti setelah 5 menit:

```bash
python scripts/capture_op3_frames.py \
  --session-id 20261022_idle_01 \
  --condition servo_idle \
  --topic /thesis/image_raw \
  --max-frames 120 \
  --interval-sec 1 \
  --duration-sec 300
```

Untuk kondisi berjalan, gunakan `--session-id 20261022_walking_01 --condition walking` hanya setelah operator memverifikasinya. Bila status tidak pasti, gunakan `--condition unknown`. Sesuaikan tanggal dan nomor pada `session_id` dengan sesi aktual; jangan pakai ulang nama sesi lama. Catat jumlah frame, topic, kondisi, dan apa saja objek yang benar-benar tampil. Hasil mentah dan metadata ada di `data/op3_camera_eval/sessions/<session_id>/images/` serta `capture_manifest.json`.

### Tahap 4 — buat label otomatis sebagai draf

Model teacher yang dipakai di lab/server tercatat di `configs/model_registry.yaml` dan mungkin tidak ada di komputer robot. Jika model teacher tersedia di komputer tempat gambar disalin, gunakan path teacher itu untuk pra-label dan catat hash. Jika besok hanya komputer OP3 yang tersedia, gunakan checkpoint student KD berikut; labelnya tetap **draf yang harus ditinjau manusia**:

```bash
python scripts/prelabel_op3_frames.py \
  --session-id 20261022_idle_01 \
  --model models/weights/kd_student_best.pt \
  --imgsz 640 --conf 0.25 --iou 0.45
```

Jalankan lagi untuk setiap `session_id`. Skrip menolak menimpa `labels_auto/` yang sudah ada. Setiap frame mendapat file `.txt` format YOLO, termasuk file kosong jika tidak ada prediksi. `predictions.jsonl` memuat confidence; `prelabel_manifest.json` memuat model/hash/parameter. **Folder hasil label otomatis: `data/op3_camera_eval/sessions/<session_id>/labels_auto/`.**

Jika menggunakan teacher di lab/server, salin **satu folder sesi lengkap** dengan cara transfer yang telah disetujui operator, pertahankan `session_id` dan struktur folder, lalu jalankan perintah pra-label di root repository pada komputer itu dengan `--model` mengarah ke checkpoint teacher. Jangan menjalankan dua model ke `labels_auto/` yang sama; gunakan sesi atau salinan terpisah untuk perbandingan pra-label. Jangan mengunggah data robot ke GitHub.

### Tahap 5 — tinjau label dan laporkan

Tinjau setiap frame secara manual di alat anotasi pilihan: perbaiki kelas, posisi kotak, objek yang terlewat, serta prediksi palsu. Simpan label final di `data/op3_camera_eval/sessions/<session_id>/labels_reviewed/` tanpa mengubah `labels_auto/` atau `images/`. Pastikan setiap gambar memiliki label final bernama sama (`frame_000001.jpg` → `frame_000001.txt`), termasuk file kosong untuk gambar tanpa tiga objek target. Catat siapa yang meninjau dan kapan. Bila peninjauan belum selesai, tandai `[BELUM GROUND TRUTH]` dan jangan hitung mAP, precision, recall, atau F1.

Laporkan: commit dan hash checkpoint; nama topic; kondisi fisik yang diverifikasi operator; jumlah frame per sesi; jumlah frame yang menampilkan masing-masing kelas setelah pemeriksaan manusia; path `images/`, `labels_auto/`, dan `labels_reviewed/`; status peninjauan; kegagalan kamera/dependency; serta temuan tracking dari sesi runtime terpisah. Nilai evaluasi OP3 baru dapat dihitung setelah label final dan protokol evaluasi dikunci. Jangan mengarang hasil atau menganggap prediksi model sebagai ground truth.
