# Prompt KD Hibrida di Lab/Server

> Salin seluruh isi bagian **Prompt** ke agen koding yang membuka *repository* ini di server lab (`/mnt/nas-hpg9/rafli5131/bre`). Versi 21 Oktober 2026. Pembimbing telah menyetujui penambahan **KD hibrida** (*loss* label ditambah distilasi) sebagai varian baru. Prompt ini menggantikan Fase 2 dan Fase 3 (pilot `pure_box_weighted`) di `prompt/PROMPT_LAB_SERVER_TANPA_ROBOT.md`. Fase lain di prompt itu tetap berlaku dan boleh berjalan sejajar.

---

## Prompt

### 0. Peran dan prinsip kerja

Anda adalah agen koding dan analisis yang membantu Bhre (Teknik Komputer FILKOM Universitas Brawijaya) melatih dan mengevaluasi varian *knowledge distillation* (KD) hibrida untuk deteksi `ball`, `gawang`, dan `robot`. Semua angka akan dipertanggungjawabkan di sidang.

1. Keabsahan eksperimen lebih penting daripada kecepatan. Perbedaan antarvarian selain *loss* adalah cacat rancangan.
2. Verifikasi dari kode sumber Ultralytics 8.4.130 yang terpasang sebelum memakai API apa pun, lalu sebutkan berkas dan barisnya di laporan.
3. Berhenti di setiap titik henti (TH) dan tunggu persetujuan tertulis Bhre.
4. Tulis kode sederhana dan eksplisit agar Bhre dapat menjelaskannya baris per baris.
5. Tidak ada jalan pintas diam-diam. Bila gagal, berhenti dan laporkan; jangan mengubah resep, *batch*, atau metode agar alur tetap berjalan.
6. Jangan mengarang angka atau rujukan. Sel tanpa data diisi `[BELUM DIUKUR]`.
7. Bila Anda tidak yakin pada suatu fakta teknis, nyatakan tidak yakin dan tunjukkan cara memverifikasinya.

### 1. Tujuan

- Melatih *student* YOLO11 skala `t` dengan KD hibrida: L = L_det + L_KD. L_det adalah *loss* deteksi Ultralytics berlabel TRAIN; L_KD adalah distilasi dari *teacher* YOLO11n FP32 yang dibekukan.
- **Pertanyaan utama:** bagaimana perbandingan KD hibrida dengan *student supervised* yang berarsitektur, berdata, berresep, dan ber-*seed* sama. Perbandingan ini menguji apakah distilasi memberi manfaat di atas label.
- **Pembanding sekunder:** *pure KD* (`pure_v4`) dan *teacher*.
- **Dasar pustaka:** KD yang menggabungkan *loss* label dengan target lunak *teacher*, misalnya Hinton, Vinyals, dan Dean (2015) serta Chen et al. (2017). Verifikasi dari naskah asli sebelum dikutip di dokumen.

### 2. Aturan model baru, tanpa menimpa yang lama

- **Dilarang** mengubah, menimpa, memindahkan, atau menghapus:
  - `runs/kd/`, `runs/supervised/`, `runs/final_test/`, `runs/benchmarks/`, dan `runs/val_ablation/` yang sudah ada;
  - `artifacts/thesis_analysis_final/`, `artifacts/thesis_analysis_final_corrected/`, dan *snapshot* di `artifacts/training_source_snapshots/` yang sudah ada;
  - `models/weights/kd_student_best.pt`, serta entri yang sudah ada di `configs/model_registry.yaml`, termasuk alias `op3_default`.
- Semua keluaran baru masuk ke direktori baru:
  - `runs/kd_hybrid/<nama_run>/` untuk pelatihan;
  - `runs/val_ablation/hybrid_<tanggal>/` untuk evaluasi VAL;
  - `runs/final_test/hybrid_kd_official_split_<tanggal>/` untuk evaluasi TEST;
  - `artifacts/thesis_analysis_hybrid_<tanggal>/` untuk tabel analisis.
- Sebelum menulis, pastikan path tujuan belum ada. Skrip harus menolak menimpa direktori yang sudah ada.
- Tabel hanya boleh **ditambah** baris atau bagian. Periksa dengan `git diff` bahwa baris lama tidak berubah, kecuali baris status dan catatan.
- *Checkpoint deploy* tidak diganti. Bila kelak Bhre memilih model hibrida untuk OP3, salin ke berkas baru `models/weights/kd_hybrid_student_best.pt` dengan alias baru, hanya setelah ada keputusan tertulis.
- Jangan menjalankan `git clean` atau `git reset --hard`. Jangan `push` tanpa izin.
- Tanpa robot, kamera, OpenVINO, ONNX untuk penerapan, INT8, PTQ, QAT, atau argumen `quantize`.
- TEST tidak boleh dipakai untuk memilih apa pun.

### 3. Dua varian hibrida

| Mode | Rumus | Implementasi | Alasan |
| --- | --- | --- | --- |
| `hybrid_feature` | L_det + `dis` · L_fitur | `DistillationModel.loss` bawaan Ultralytics 8.4.130 tanpa penimpaan. Nilai `dis` memakai bawaan versi terpasang; panduan Ultralytics menyebut 6,0, cek di `ultralytics/cfg/default.yaml`. | Resep KD standar dari Ultralytics. |
| `hybrid_full` | L_det + 1,0 · L_fitur + 1,0 · L_kotak + 1,0 · L_kelas, T = 2 | L_KD sama persis dengan `pure_v4` (rerata seragam atas semua *anchor*; *loss* kelas tidak dibobot), ditambah L_det. | Mengisolasi efek menambahkan label pada KD yang sudah dipakai. |

Resep keduanya identik dengan semua run lama:

- 100 *epoch*, *batch* 16, AdamW `lr0` 0,001, `lrf` 0,01, *warmup* 3, *weight decay* 0,0005, `close_mosaic` 10, AMP mati, `patience` 30, `pretrained=False`, `imgsz` 640;
- *teacher* `/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt` dengan SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`;
- *student* `models/yolo11_tiny_kd.yaml`;
- data `configs/data_train_val.yaml`, tanpa TEST.

Anggaran 100 *epoch* dipertahankan agar sebanding dengan semua run lama. Catat hal ini sebagai usulan penguncian D3.

### 4. Alur kerja dan titik henti

```
Fase 0  Persiapan dan pencatatan keputusan
Fase 1  Kode, tes, uji asap, pra-registrasi                  -> TH-1 (izin training)
Fase 2  Dua pilot seed 42 dan evaluasi VAL                    -> TH-2 (pilih varian)
Fase 3  Dua seed tambahan untuk varian terpilih
Fase 4  Evaluasi TEST terkunci baru dan analisis              -> TH-3
Fase 5  Registri, tabel, dan dokumentasi                      -> TH-akhir
```

Satu run di L40 memerlukan sekitar 5,5 jam (run KD *seed* 42 lama selesai dalam 5 jam 23 menit). Total empat run sekitar 22 jam bila dijalankan berurutan.

### 5. Fase 0: persiapan

1. Jalankan `git status` dan `git pull --ff-only`. Catat *commit* awal.
2. Pakai interpreter `env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python`. Catat versi Python, PyTorch, dan Ultralytics.
3. Jalankan `nvidia-smi`. Bila gagal, jangan lanjut ke pelatihan.
4. Tambahkan baris baru di `docs/DECISIONS.md`: "21 Oktober 2026: KD hibrida (label ditambah distilasi) disetujui pembimbing, sebagaimana dilaporkan Bhre, sebagai varian tambahan. `pure_v4` dan seluruh hasil lama tetap dipertahankan." Di `configs/analysis.yaml`, tambahkan kunci baru di bawah D2 (misalnya `hybrid_approved`, `hybrid_approved_at`, `hybrid_modes`). Baris dan kunci lama tidak dihapus.

### 6. Fase 1: kode, tes, dan pra-registrasi

1. Verifikasi dari kode sumber terpasang, lalu laporkan berkas dan barisnya:
   - `DistillationModel.loss` bawaan menghitung `regular_loss` berlabel ditambah `dis` × *loss* fitur;
   - cara *trainer* deteksi memberi nama dan mencatat komponen *loss* saat `distill_model` diisi;
   - nilai bawaan `dis`.
2. Perluas `scripts/train_kd.py`:
   - mode `pure_v4` dan `pure_weighted` tidak berubah; `install_teacher_only_kd_loss` hanya dipasang untuk mode murni;
   - `hybrid_feature`: tidak memasang penimpaan apa pun, meneruskan `dis` dari konfigurasi, dan mencatat objektif "KD hibrida: *loss* deteksi berlabel ditambah distilasi fitur bawaan Ultralytics";
   - `hybrid_full`: memakai satu *forward student* untuk *hook* fitur dan untuk `regular_loss = student_model.loss(batch, preds)`, lalu menambahkan L_KD yang dihitung dengan rumus `pure_v4`. Struktur keluaran harus sama dengan `loss()` bawaan: `torch.cat([regular_loss, kd_loss_terskala])` dan `loss_items` berisi `dis_loss`. Pada mode validasi, perilakunya sama dengan bawaan;
   - *manifest* mencatat mode, semua bobot, `dis`, temperatur, `train_labels_used_for_loss: true`, serta *snapshot* `train_kd.py`, `kd_losses.py`, dan `distill_model.py`.
3. Buat `configs/kd_hybrid_feature.yaml` dan `configs/kd_hybrid_full.yaml` dengan `run.project: runs/kd_hybrid` dan nama run `yolo11_tiny_hybrid_feature_seed42` serta `yolo11_tiny_hybrid_full_seed42`.
4. Tulis `tests/test_kd_hybrid.py`. Jalankan di CPU dengan model dari YAML yang sama dan `imgsz` kecil, misalnya 64:
   - nilai *loss* `pure_v4` pada *batch* tetap sama persis dengan implementasi di `artifacts/training_source_snapshots/yolo11_tiny_pure_kd_v4_seed1337/train_kd.py`;
   - `hybrid_full` dengan semua bobot KD nol sama dengan *loss* deteksi biasa pada *batch* yang sama;
   - bagian L_KD dari `hybrid_full` sama dengan *loss* `pure_v4` pada *batch* yang sama;
   - *teacher* tidak menerima gradien, sedangkan *student* dan proyektor menerimanya;
   - pada mode `hybrid_feature`, `DistillationModel.loss` tetap fungsi aslinya di proses yang baru.
   Bila tes terlalu lambat di CPU, laporkan dan usulkan penggantinya.
5. Uji asap 1 *epoch* untuk masing-masing mode memakai konfigurasi terpisah di `runs/kd_smoke/`. Periksa bahwa *loss* berhingga, kolom `results.csv` benar, dan *manifest* lengkap. Hasil uji asap tidak masuk tabel.
6. Tulis `docs/PILOT_KD_HIBRIDA_<tanggal>.md` **sebelum** pilot dijalankan:
   - evaluasi ulang *supervised seed* 42 pada VAL dengan `scripts/evaluate_val_ablation.py` dan pengaturan yang sama dengan T04, sebagai acuan. Hasil `pure_v4 seed` 42 yang sudah ada boleh dipakai ulang;
   - **aturan pemilihan:** varian dengan mAP50-95 VAL lebih tinggi dibawa ke tiga *seed*. Bila selisih kedua varian kurang dari 0,005, pilih `hybrid_feature` karena lebih sederhana dan merupakan resep bawaan. Varian terpilih tetap dilanjutkan walaupun nilainya di bawah *supervised*, karena pertanyaan penelitiannya adalah perbandingan;
   - **metrik pendamping:** P, R, dan F1 pada ambang 0,25, FP per gambar, dan duplikasi.

**TH-1:** tampilkan *diff*, hasil tes, hasil uji asap, nilai `dis` yang terverifikasi, dan dokumen pra-registrasi. Tunggu izin pelatihan.

### 7. Fase 2: dua pilot *seed* 42

1. Jalankan kedua pilot di `tmux`, berurutan:

   ```bash
   env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_kd.py --config configs/kd_hybrid_feature.yaml
   env -u PYTHONPATH /mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python scripts/train_kd.py --config configs/kd_hybrid_full.yaml
   ```

   Menjalankan sejajar di dua GPU hanya boleh dengan izin Bhre dan bila `nvidia-smi` menunjukkan GPU kosong. Catat perangkat yang dipakai setiap run.
2. Evaluasi kedua *checkpoint* pada VAL dengan `scripts/evaluate_val_ablation.py` (1.213 gambar, FP32, `imgsz` 640, NMS 0,7, *confidence floor* 0,001) ke `runs/val_ablation/hybrid_<tanggal>/`. Jalankan juga `scripts/analyze_val_detections.py` untuk kategori FP.
3. Tambahkan baris pilot ke T04 dan T04 per kelas tanpa mengubah baris lama.
4. Terapkan aturan pemilihan dan tulis hasilnya di dokumen pilot.

**TH-2:** laporkan hasil dan varian terpilih. Tunggu konfirmasi untuk dua *seed* tambahan.

### 8. Fase 3: dua *seed* tambahan

1. Latih varian terpilih dengan `--seed 1337` dan `--seed 2025`, nama run `yolo11_tiny_hybrid_<mode>_seed1337` dan `yolo11_tiny_hybrid_<mode>_seed2025`, di `runs/kd_hybrid/`.
2. Pilot *seed* 42 dipakai sebagai anggota ketiga, karena konfigurasinya identik. Buktikan dengan membandingkan isi konfigurasi dan *manifest* yang hanya berbeda pada *seed* dan nama run.
3. Setiap run harus berakhir dengan status `complete`. Bila gagal, jangan mengulang diam-diam; arsipkan sebagai gagal mengikuti pola repo, lalu laporkan.

### 9. Fase 4: evaluasi TEST dan analisis

1. Jangan mengubah `scripts/evaluate_locked_test.py`. Buat skrip baru, misalnya `scripts/evaluate_locked_test_hybrid.py`, yang mengimpor fungsinya dan memakai pengaturan identik: `imgsz` 640, *batch* 16, *confidence floor* dan NMS yang sama, P/R/F1 pada ambang 0,25 dan IoU 0,5, *bootstrap* 1.000 replikasi dengan *seed* 20261009, serta verifikasi hash TEST terhadap *fingerprint*.
2. **Cek reproduksi lebih dulu:** evaluasi ulang `supervised_seed42` dengan skrip baru di direktori baru. Hasilnya harus sama dengan `artifacts/thesis_analysis_final_corrected/per_model.csv`. Bila berbeda, berhenti dan laporkan.
3. Evaluasi tiga *checkpoint* hibrida pada TEST, masing-masing **sekali**. Catat bahwa TEST sudah pernah dilihat (*teacher* pada 24 September 2026, enam *student* pada 9 Oktober 2026), sehingga hasilnya adalah evaluasi lanjutan atas tolok ukur yang sudah diketahui.
4. Susun analisis di `artifacts/thesis_analysis_hybrid_<tanggal>/`: metrik per model, rerata ± SD tiga *seed*, selisih berpasangan per *seed* (hibrida dikurangi *supervised* sebagai perbandingan utama, hibrida dikurangi *pure KD*), retensi terhadap *teacher*, dan interval *bootstrap* per *checkpoint*. Pakai definisi F1 dari D11 bila sudah dikunci; bila belum, ikuti evaluator TEST.
5. Dengan n = 3, jangan menyatakan signifikansi. Laporkan konsistensi tanda selisih antar-*seed*.

**TH-3:** laporkan hasil TEST, cek reproduksi, dan tabel analisis.

### 10. Fase 5: registri, tabel, dan dokumentasi

1. Tambahkan tiga entri baru di `configs/model_registry.yaml` (alias `kd_hybrid_<mode>_seed42`, `_seed1337`, `_seed2025`) berisi path, SHA-256, parameter, GFLOPs, dan *manifest* sumber. Entri lama dan `op3_default` tidak diubah.
2. Tambahkan baris atau bagian baru pada tabel:
   - T01, T02, T03: spesifikasi, resep, dan konvergensi tiga run hibrida;
   - T05, T06, T07: metode "KD hibrida" dan perbandingan berpasangan;
   - T08 sampai T14: diagnosis VAL untuk *checkpoint* hibrida (minimal *seed* 42, ketiganya bila skrip pembangun mendukung);
   - T26: baris hibrida dengan kolom runtime `[BELUM DIUKUR]`;
   - T27: hanya bila data kamera OP3 sudah ada di server dan hash-nya cocok dengan `runs/op3_multi_session_eval/20261021_primary260_partial50_v1/input_manifest.json`. Evaluasi KD hibrida *seed* 42 pada set yang sama di direktori run baru. Bila data belum ada, tuliskan perintahnya.
3. Bila skrip pembangun tabel menulis ulang seluruh berkas, pastikan lewat `git diff` bahwa baris lama tetap sama persis.
4. Perbarui `analisis_performa/INDEKS.md`, `analisis_performa/lab_server/README.md`, bagian varian model di `README.md`, dan `prompt/inventaris_tabel_dan_prompt.md`. Tulis catatan memory baru `memory/<tanggal>.md` dengan format yang sama seperti catatan sebelumnya.
5. Pengukuran runtime OP3 untuk model hibrida dikerjakan nanti dengan paket `op3_runtime_benchmark` dari prompt lab yang lain, hanya bila Bhre memintanya.

**TH-akhir:** laporkan semua berkas baru, hasil utama, dan keputusan yang dibutuhkan, misalnya apakah model hibrida menjadi kandidat *deploy*.

### 11. Standar kode dan dokumen

- Python bertipe dengan *docstring* Bahasa Indonesia singkat, modul `logging`, dan `pathlib`.
- Jalankan tes sebelum setiap *commit*. Buat *commit* kecil per tugas.
- Dokumen ditulis dalam Bahasa Indonesia ragam baku akademis:
  - tanpa tanda pisah *em dash*;
  - memakai "algoritme" (bukan "algoritma") dan "analisis" (bukan "analisa"), serta tidak memakai "rancang bangun";
  - istilah asing dicetak miring kecuali nama produk;
  - setiap klaim faktual bersitasi atau diberi penanda `[BUTUH SITASI: ...]`;
  - dilarang mengarang nama penulis, tahun, judul, atau DOI.

### 12. Format laporan di setiap titik henti

1. Yang dikerjakan, ringkas.
2. Berkas yang dibuat atau diubah, beserta *commit*-nya.
3. Perintah yang dijalankan dan hasilnya; setiap angka disertai path berkas sumber.
4. Penyimpangan dari prompt ini beserta alasannya.
5. Keputusan atau informasi yang dibutuhkan dari Bhre.

### 13. Mulai dari sini

Baca `docs/DECISIONS.md`, `configs/analysis.yaml`, `configs/kd.yaml`, `configs/supervised_baseline.yaml`, `scripts/train_kd.py`, `scripts/kd_losses.py`, `artifacts/training_source_snapshots/kd_seed42/distill_model.py`, `analisis_performa/tabel/T04_ablasi_kd_val.md`, dan `docs/PILOT_PURE_WEIGHTED_2026-10-20.md`. Kerjakan Fase 0 dan Fase 1, lalu berhenti di TH-1.
