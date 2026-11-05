# Tutorial mengulang T42 secara mandiri di server lab baru

Versi 5 November 2026. Akun server lama `rafli5131` sudah tidak tersedia, sehingga T42 (ablasi kapasitas *teacher*) harus diulang dari awal di server lain. Tutorial ini untuk Bhre, dijalankan sendiri lewat SSH tanpa agen.

## 0. Situasinya

**Yang aman, karena ada di GitHub:**

- kode, konfigurasi, protokol, memory, dan dokumentasi;
- tabel T01 sampai T41 serta T36/T37 (uji live OP3);
- `best.pt` *student* utama: *supervised* tiga *seed*, KD murni tiga *seed*, Hybrid full tiga *seed*, `hybrid_feature`, serta Hybrid v2 S1 sampai S8 dan S2 *seed* 1337/2025.

**Yang hilang bersama server lama:**

- salinan dataset dan *venv* di server;
- *teacher* T42 (YOLO11n `retry1`), *log* mentah, dan sebagian `last.pt`;
- salinan *teacher* utama YOLO11n FP32 di server. Salinan yang tersisa ada di OP3 (`models_local/teacher_fp32_best.pt`).

**Cara mengulang T42.** T42 dijalankan sebagai percobaan baru dengan nama sendiri lewat variabel `T42_ATTEMPT` (contoh di tutorial ini: `server2`). Semua keluarannya masuk folder terpisah, jadi riwayat T42 lama (VAL *teacher* YOLO11n 0,7760) tetap utuh sebagai riwayat. Skrip T42 sudah disesuaikan supaya path server, dataset, dan Python bisa diatur lewat variabel lingkungan. Tanpa variabel itu, perilaku skrip sama dengan sebelumnya.

## 1. Amankan dulu teacher utama dari OP3

Ini tidak dibutuhkan T42, tetapi dibutuhkan bila nanti ada evaluasi ulang dengan *teacher* utama, misalnya T38. Saat ini OP3 menyimpan satu-satunya salinan yang tersisa.

Di OP3:

```bash
cd /home/humanoid/bre_skripsi
sha256sum models_local/teacher_fp32_best.pt
# harus: e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c
```

Dari laptop (ganti `<alamat-op3>`):

```bash
scp humanoid@<alamat-op3>:/home/humanoid/bre_skripsi/models_local/teacher_fp32_best.pt ./teacher_fp32_best.pt
sha256sum teacher_fp32_best.pt
```

Simpan salinannya di tempat privat, misalnya Google Drive pribadi. Jangan dimasukkan ke repo publik.

## 2. Siapkan repo di server baru

```bash
ssh <user>@<server-baru>
mkdir -p ~/skripsi && cd ~/skripsi
git clone https://github.com/rafli5131/skripsi-knowlage-destilation.git
cd skripsi-knowlage-destilation
ls scripts/server_paths.py    # harus ada; bila tidak, perubahan skrip untuk server baru belum di-push

export REPO=$PWD
export DATA=$HOME/skripsi/data/advance_vision_human   # lokasi dataset, di luar repo
```

## 3. Buat environment training

```bash
nvidia-smi                    # catat jenis GPU; kolom "CUDA Version" sebaiknya 12.1 atau lebih baru
cd "$REPO"
python3.11 -m venv .venv-train        # versi server lama 3.11.2; pakai python3 bila 3.11 tidak ada
source .venv-train/bin/activate
pip install --upgrade pip
pip install --extra-index-url https://download.pytorch.org/whl/cu121 -r requirements/train-gpu.txt
export PY=$REPO/.venv-train/bin/python
```

Cek versi dan sumber KD Ultralytics. Skrip *training* menolak berjalan bila keduanya berbeda dari yang dikunci:

```bash
$PY -c "import torch, ultralytics; print(torch.__version__, ultralytics.__version__, torch.cuda.is_available())"
#   harus: 2.4.1+cu121 8.4.130 True
$PY -c "import sys; sys.path.insert(0, 'scripts'); from training_runtime import verify_training_runtime; print(verify_training_runtime())"
#   distill_model_sha256 harus fe77f5d519c948614a0060e525a9c5537ae7f826a7fe5baee7274a15e9eaa75c
```

Folder `.venv-train/` sudah masuk `.gitignore`.

## 4. Siapkan dataset Advance Vision v1

Dataset aslinya adalah ekspor Roboflow `humanoid-atom/advance_vision_human` versi v1 (V1-Base, 31 Agustus 2026, CC BY 4.0): <https://universe.roboflow.com/humanoid-atom/advance_vision_human>.

1. Bila kamu masih punya *zip* ekspor asli, salin ke server lalu ekstrak ke `$DATA`.
2. Bila tidak, unduh versi **v1** langsung di server dengan Roboflow Python SDK. Kamu perlu akun Roboflow dan *API key* yang ada di pengaturan *workspace* Roboflow-mu. Folder `$DATA` sebaiknya belum ada sebelum mengunduh. Pasang paket `roboflow` di *venv* terpisah agar *venv* training tidak ikut berubah, karena paket itu bisa membawa versi dependensi lain:

   ```bash
   python3 -m venv ~/rf-venv
   ~/rf-venv/bin/pip install roboflow
   export ROBOFLOW_API_KEY='isi-api-key-kamu'      # jangan ditulis ke repo
   mkdir -p "$(dirname "$DATA")"
   ~/rf-venv/bin/python - <<'EOF'
   import os
   from roboflow import Roboflow
   rf = Roboflow(api_key=os.environ["ROBOFLOW_API_KEY"])
   version = rf.workspace("humanoid-atom").project("advance_vision_human").version(1)
   dataset = version.download(model_format="yolov8", location=os.environ["DATA"], overwrite=False)
   print(dataset.location)
   EOF
   ```

   Alternatifnya lewat CLI Roboflow: `roboflow download -f yolov8 -l "$DATA" humanoid-atom/advance_vision_human/1`. Format `yolov11` juga tersedia; struktur folder dan label teksnya sama dengan `yolov8`.
3. Pastikan strukturnya `train/images`, `train/labels`, `valid/images`, `valid/labels`, `test/images`, `test/labels`:

   ```bash
   ls "$DATA"; for s in train valid test; do echo "$s: $(ls "$DATA/$s/images" | wc -l) gambar, $(ls "$DATA/$s/labels" | wc -l) label"; done
   #   harus 4600, 1213, dan 592 gambar
   ```

Lalu cocokkan isinya dengan sidik jari yang dikunci di repo:

```bash
cd "$REPO"
$PY - <<'EOF'
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, "scripts")
from experiment_paths import resolve_training_data
_, _, meta = resolve_training_data(
    Path("configs/data_train_val.yaml"), Path(tempfile.mkdtemp()),
    Path("artifacts/advance_vision_dataset_fingerprint.json"), os.environ["DATA"])
print("COCOK" if meta["dataset_split_fingerprints_verified"] else "TIDAK COCOK", meta["dataset_split_fingerprints"])
EOF
```

Perintah ini membandingkan nama dan hash setiap gambar dan label TRAIN serta VAL. Bila hasilnya "COCOK", lanjutkan. **Bila muncul *error* hash atau inventaris berbeda, berhenti.** Artinya ekspor ulang tidak identik byte demi byte dengan data lama. Saya tidak yakin ekspor ulang Roboflow selalu menghasilkan berkas yang identik. Dalam kasus itu, T42 tidak lagi sebanding dengan kontrol *supervised* T41 dan perlu keputusan dulu, jadi kirim pesan *error*-nya ke agen atau ke Claude.

**Kasus yang sudah diketahui: satu label TRAIN berupa poligon.** Pada ekspor ulang format `yolov8` pada 5 November 2026, hanya satu label TRAIN (`KakaoTalk_20250203_160516031_mp4-0049_jpg.rf.71283140d6e7ec0db99bc112144a3695.txt`) yang berbeda: berkas itu berisi satu baris poligon, sedangkan data lama berisi kotak. `AUDIT_DATASET_SKRIPSI.md` mencatat bahwa satu label TRAIN memang pernah diekspor sebagai poligon lalu dikonversi ke kotak YOLO. Mengganti baris poligon dengan kotak pembatas sumbunya (x pusat, y pusat, lebar, tinggi, 12 desimal, baris baru di akhir berkas) menghasilkan SHA-256 yang sama persis dengan hash terkunci, sehingga berkas hasil konversi identik byte demi byte dengan berkas lama. `scripts/restore_polygon_label.py` melakukan pemulihan itu. Skrip ini hanya memeriksa kecuali diberi `--apply`, hanya menulis bila semua selisih di TRAIN dan VAL bisa dipulihkan dengan hash yang cocok persis, menyalin label asli ke `<DATA>_backup_label_polygon/`, dan memverifikasi hasil tulisannya:

```bash
cd "$REPO"
$PY scripts/restore_polygon_label.py "$DATA" 2>&1 | tee ~/restore_dry.log            # periksa dulu
$PY scripts/restore_polygon_label.py "$DATA" --apply 2>&1 | tee ~/restore_apply.log  # hanya bila hasil periksa sesuai
```

Setelah itu ulangi cek sidik jari di atas. Bila ada selisih yang tidak bisa dipulihkan dengan cara ini, berhenti dan jangan memakai `--apply`. Catat pemulihan ini di laporan T42.

## 5. Unduh bobot pralatih resmi

```bash
mkdir -p "$REPO/models_local/teacher_ablation_t42/pretrained"
cd "$REPO/models_local/teacher_ablation_t42/pretrained"
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s.pt
sha256sum yolo11n.pt   # harus 0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1
sha256sum yolo11s.pt   # harus 85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5
```

URL dan hash ini berasal dari `docs/PROTOKOL_T42_ABLASI_TEACHER_2026-10-24.md`. `models_local/` diabaikan Git.

## 6. Jalankan T42

Ketiga variabel di bawah wajib diisi di *shell* yang sama dengan perintah *training*:

```bash
tmux new -s t42                     # bila tmux tidak ada, lihat catatan di bawah
cd "$REPO"
export KD_TRAIN_PYTHON=$REPO/.venv-train/bin/python
export KD_DATA_ROOT=$HOME/skripsi/data/advance_vision_human
export T42_ATTEMPT=server2
$KD_TRAIN_PYTHON scripts/run_t42_teacher_ablation.py 2>&1 \
  | tee "runs/kd_teacher_ablation/run_${T42_ATTEMPT}_$(date -u +%Y%m%dT%H%M%SZ).log"
# lepas dari tmux tanpa menghentikan proses: Ctrl-b, lalu d
```

Tanpa `tmux`:

```bash
nohup env KD_TRAIN_PYTHON=$REPO/.venv-train/bin/python KD_DATA_ROOT=$HOME/skripsi/data/advance_vision_human \
  T42_ATTEMPT=server2 $REPO/.venv-train/bin/python scripts/run_t42_teacher_ablation.py \
  > "runs/kd_teacher_ablation/run_server2_$(date -u +%Y%m%dT%H%M%SZ).log" 2>&1 &
```

Urutan yang dijalankan *driver*:

1. *teacher* YOLO11n dan evaluasi VAL-nya;
2. *teacher* YOLO11s dan evaluasi VAL-nya;
3. enam *student* Hybrid full (*teacher* n dan s × *seed* 42, 1337, 2025), masing-masing diikuti evaluasi VAL;
4. pembuatan tabel T42.

Keluaran percobaan `server2`:

| Isi | Lokasi |
|---|---|
| Status | `runs/kd_teacher_ablation/server2/t42_status.jsonl` |
| *Log* tiap tahap | `runs/kd_teacher_ablation/server2/logs/` |
| *Teacher* (privat) | `models_local/teacher_ablation_t42/server2/training/` |
| *Student* | `runs/kd_teacher_ablation/server2/student_teacher_yolo11{n,s}_seed{42,1337,2025}/` |
| Konfigurasi *student* | `configs/t42_server2_student_teacher_*.yaml` |
| Hasil VAL | `runs/val_ablation/teacher_yolo11s_t42_server2/` |
| Tabel | `analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.{csv,md}` |

Perkiraan waktu: di L40 server lama, *teacher* YOLO11n butuh sekitar 2,3 jam dan satu *student* Hybrid full sekitar 1 sampai 1,4 jam (T33). YOLO11s lebih berat. Totalnya kira-kira 12 sampai 16 jam bila GPU kosong. Di GPU lain waktunya bisa jauh berbeda. Ini perkiraan, bukan angka terukur.

*Driver* menunggu GPU yang memori terpakainya paling banyak 8 GiB dan utilisasinya paling banyak 25% pada dua pengecekan berjarak 60 detik. Kalau GPU sedang dipakai orang lain, *driver* bisa terlihat diam lama. Itu bukan *hang*.

## 7. Memantau

```bash
cd "$REPO"
tail -f runs/kd_teacher_ablation/server2/t42_status.jsonl            # keluar: Ctrl-c
LOG=$(ls -t runs/kd_teacher_ablation/server2/logs/* | head -1); tail -n 5 "$LOG"
wc -l models_local/teacher_ablation_t42/server2/training/*/results.csv   # baris - 1 = epoch selesai
nvidia-smi
tmux attach -t t42                                                     # lepas lagi: Ctrl-b, d
```

Event yang perlu diperhatikan: `step_started` dan `step_finished` per tahap, `t42_failed` (berhenti), dan `t42_complete` (selesai).

## 8. Bila ada tahap yang gagal

- Baca *log* tahap yang gagal: `ls -t runs/kd_teacher_ablation/server2/logs/ | head -1`.
- **Jangan menghapus folder apa pun.** *Driver* sengaja menolak dijalankan ulang dengan `T42_ATTEMPT` yang sama.
- Bila gagal di awal (misalnya di *teacher* YOLO11n), perbaiki penyebabnya, lalu jalankan ulang dengan nama percobaan baru, misalnya `T42_ATTEMPT=server2b`.
- Bila gagal setelah beberapa tahap selesai, jangan memulai dari nol. Kirim `tail -n 20` berkas status beserta 50 baris terakhir *log* yang gagal ke agen, supaya dibuatkan lanjutan yang terdokumentasi seperti `continue_t42_after_teacher_n.py`.
- Bila evaluasi VAL gagal dengan `PermissionError` pada path `/mnt/nas-hpg9/rafli5131/...`, penyebabnya `configs/data_train_val.yaml` yang masih berisi path server lama. Pastikan `KD_DATA_ROOT` terisi dan repo sudah di-`git pull`. Lanjutannya untuk percobaan `server2` adalah `scripts/continue_t42_attempt_after_eval_fix.py`: jalankan dulu tanpa argumen untuk audit, lalu dengan `--execute`.

## 9. Setelah selesai: commit dan push

Pastikan baris terakhir status berisi `t42_complete`, lalu:

```bash
cd "$REPO"
git pull --ff-only
git add analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.csv \
        analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md \
        runs/val_ablation/teacher_yolo11s_t42_server2 \
        runs/kd_teacher_ablation/server2/t42_status.jsonl \
        configs/t42_server2_student_teacher_*.yaml
for d in runs/kd_teacher_ablation/server2/student_teacher_yolo11*; do
  git add "$d"/manifest.json "$d"/args.yaml "$d"/results.csv 2>/dev/null
done
git status --short    # pastikan tidak ada models_local/, logs/, last.pt, atau .venv-train/
git -c user.name=BhreW -c user.email=BhreW@users.noreply.github.com \
    commit -m "Add T42 teacher capacity ablation rerun on new server (VAL only)"
git push origin main  # perlu login GitHub akun BhreW (personal access token)
```

`best.pt` *student* T42 hanya ditambahkan bila kamu memang ingin mempublikasikannya. Sesudah itu, minta agen atau Claude memperbarui `analisis_performa/INDEKS.md`, `docs/DECISIONS.md`, dan memory. Catat bahwa server lama tidak lagi tersedia, T42 diulang sebagai percobaan `server2`, dan hasil *teacher* YOLO11n lama hanya menjadi riwayat.

## 10. Cara membaca hasilnya

- **Perbandingan utama T42 adalah *student* dengan *teacher* YOLO11s terhadap *student* dengan *teacher* YOLO11n**, keduanya dari percobaan `server2`. Perbandingan ini adil karena kedua *teacher* dilatih di server, data, dan resep yang sama.
- Kolom selisih terhadap *supervised* dan rasio pemulihan di CSV T42 memakai kontrol *supervised* T41 yang dilatih di server lama. Jadi kolom itu mencampur dua server dan hanya boleh dibaca sebagai indikasi.
- Hasil di GPU atau server berbeda tidak dijamin sama persis dengan hasil lama, walaupun *seed*-nya sama.
- T42 tetap ablasi VAL. Hasilnya tidak mengganti model OP3 (Hybrid full seed 1337) maupun keputusan D16.

## 11. Larangan singkat

- Jangan menjalankan `git clean`, `git reset --hard`, atau `rm` pada folder run.
- Jangan mengubah `configs/kd_hybrid_full.yaml` atau `artifacts/advance_vision_dataset_fingerprint.json`.
- Jangan memakai `continue_t42_after_teacher_n.py`. Skrip itu hanya untuk percobaan lama dan sekarang menolak berjalan bila `T42_ATTEMPT` diisi.
- Jangan mengunggah `models_local/`, bobot *teacher*, dataset, atau *log* mentah ke GitHub.
