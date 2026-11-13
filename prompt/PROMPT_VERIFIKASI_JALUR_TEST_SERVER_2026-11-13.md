# Verifikasi jalur inferensi TEST di server lab (13 November 2026)

## Tujuan

Memeriksa apakah metrik TEST resmi (T05/T30), yang dihitung lewat `model.val`, berubah bila dihitung lewat `model.predict`, yaitu jalur yang dipakai node robot. Pemeriksaan ini menindaklanjuti catatan D22: "apakah evaluasi TEST memakai dua jalur yang sama belum diperiksa".

Hasil pembacaan kode `scripts/evaluate_locked_test.py` sebelum eksekusi: mAP dan P/R/F1 TEST berasal dari satu jalur (`DetectionValidator`, `rect=True`, batch 16, floor 0,001, NMS IoU 0,7). Pada Ultralytics 8.4.130, `DetectionValidator.postprocess` memanggil NMS dengan `multi_label=True`, sedangkan `DetectionPredictor.postprocess` tidak memakai argumen itu. Robot memakai confidence 0,25 dan NMS IoU 0,45.

## Yang dijalankan skrip

`scripts/verify_test_inference_path.py` menjalankan `model.predict` per gambar (batch 1, FP32, bawaan CPU) pada 592 gambar TEST untuk setiap checkpoint, dengan dua varian:

| Varian | Confidence | NMS IoU | Metrik |
|---|---:|---:|---|
| `protokol_test` | 0,001 | 0,7 | mAP50, mAP50-95, serta P/R/F1 pada confidence > 0,25 dan IoU 0,5 |
| `robot` | 0,25 | 0,45 | P/R/F1 pada IoU 0,5 |

Pencocokan prediksi dan label mengikuti aturan validator Ultralytics (sekelas, serakah menurut IoU); kesamaannya sudah diuji pada 500 kasus acak dengan hasil identik. AP dihitung dengan `ultralytics.utils.metrics.ap_per_class`.

Pengaman:

- SHA-256 setiap checkpoint dicocokkan dengan `configs/model_registry.yaml`.
- Seluruh gambar dan label TEST dicocokkan dengan `artifacts/advance_vision_dataset_fingerprint.json`. Bila ada yang berbeda, skrip berhenti tanpa menulis hasil.
- Folder hasil tidak boleh sudah ada; hasil lama tidak disentuh.
- Tidak ada training, tidak ada pemilihan ulang model atau ambang. TEST sudah pernah dibuka, jadi hasil ini hanya pemeriksaan konsistensi metodologi.

## Langkah di server

```bash
cd <FOLDER_REPO_DI_SERVER>
git pull

# 1. Cari data.yaml dan versi pustaka yang dipakai T42 server2
grep -h '"data_yaml"' models_local/teacher_ablation_t42/server2/training/*/manifest.json
grep -h -A4 '"versions"' models_local/teacher_ablation_t42/server2/training/teacher_yolo11n_seed42/manifest.json

# 2. Pakai Python venv yang sama dengan T42; Ultralytics harus 8.4.130
PY=<PATH_PYTHON_VENV_T42>
env -u PYTHONPATH "$PY" -c "import ultralytics, torch; print(ultralytics.__version__, torch.__version__)"

# 3. (Opsional) Teacher utama. Ukurannya 5.481.875 bait, SHA-256 harus
#    e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c
#    Bila salinannya ada di robot, cari di robot dengan:
#      find ~ -name '*.pt' -size 5481875c -exec sha256sum {} \;
#    lalu salin ke server (models_local/ tidak masuk Git):
mkdir -p models_local/teacher_utama
# scp <user>@<ip_robot>:<path_teacher>/best.pt models_local/teacher_utama/best.pt
sha256sum models_local/teacher_utama/best.pt

# 4. Jalankan di tmux karena memakan waktu (perkiraan 10 sampai 30 menit di CPU)
tmux new -s verifikasi_test
env -u PYTHONPATH "$PY" scripts/verify_test_inference_path.py \
  --data <PATH_DATA_YAML> \
  --teacher models_local/teacher_utama/best.pt \
  --device cpu 2>&1 | tee /tmp/verifikasi_jalur_test.log
```

Bila teacher utama tidak tersedia, hapus baris `--teacher`; sembilan checkpoint student tetap dievaluasi. Bila `data.yaml` gagal dibaca, ganti `--data <PATH_DATA_YAML>` dengan `--test-images <FOLDER>/test/images`.

Bila skrip berhenti dengan `GAGAL: TEST di server berbeda dari sidik jari terkunci`, jangan memakai `--allow-fingerprint-mismatch`. Simpan pesan galatnya untuk ditinjau. Untuk label poligon, pola perbaikan T42 ada di `scripts/restore_polygon_label.py`.

## Hasil dan push

Hasil tertulis di `analisis_performa/lab_server/verifikasi_jalur_test_<YYYYMMDD>/`:

| Berkas | Isi |
|---|---|
| `RINGKASAN.md` | Tabel resmi vs predict vs robot per kelompok dan per checkpoint |
| `ringkasan_per_model.csv` | Angka per checkpoint |
| `ringkasan_per_kelompok.csv` | Rerata dan simpangan baku per kelompok |
| `hasil_verifikasi_jalur_test.json` | Rincian per kelas, pengaturan, sidik jari, lingkungan, dan pemanggilan NMS validator |
| `manifest.json` | SHA-256 berkas hasil, skrip, dan commit |

```bash
git add analisis_performa/lab_server/verifikasi_jalur_test_*/
git commit -m "Record TEST inference-path verification"
git push
```

Bila server tidak punya akses push, salin folder hasil ke laptop lalu commit dari laptop:

```bash
scp -r <user>@<server>:<FOLDER_REPO_DI_SERVER>/analisis_performa/lab_server/verifikasi_jalur_test_<YYYYMMDD> \
  "analisis_performa/lab_server/"
```

## Cara membaca

- Selisih **resmi vs predict** (ambang sama) menunjukkan pengaruh jalur: letterbox per gambar vs batch rect, NMS multi-label vs biasa, batch, dan perangkat.
- Selisih **robot vs resmi** menambahkan pengaruh ambang runtime 0,25 dan 0,45.
- Bila selisih F1 kecil (misalnya di bawah 0,01) dan urutan model tidak berubah, angka TEST resmi dapat dipakai dengan catatan jalur. Bila besar atau urutan berubah, naskah perlu menyajikan kedua jalur dan keputusan dicatat sebagai D23.
