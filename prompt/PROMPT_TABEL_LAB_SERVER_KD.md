# Prompt Tabel Lab/Server — Knowledge Development (KD)

## Tujuan

Gunakan prompt ini di komputer lab/server untuk menyusun atau memperbarui tabel penelitian yang berasal dari dataset, training, evaluasi offline, dan benchmark server. Tabel mengikuti template yang sudah ada di `~/bre_skripsi/analisis_performa/tabel/`.

## Prompt

Bertindak sebagai asisten analisis eksperimen dan penulisan skripsi computer vision. Kerjakan dari repository `~/bre_skripsi` dan artefak yang sudah tersimpan. Fokus hanya pada pekerjaan lab/server. Jangan menjalankan training baru, membuka ulang TEST, atau melakukan pengujian fisik robot.

### Nomenklatur penelitian

Metode training penelitian ini adalah **Knowledge Development (KD)** sesuai istilah yang diminta penulis, bukan QAT (Quantization-Aware Training). Gunakan nama Knowledge Development (KD) di tabel dan narasi training. Repository mendokumentasikan objective teacher-only KD; jaga detail objective dan sumber yang benar. Jangan menyebut model KD sebagai QAT, PTQ, atau INT8. Bila ada artefak lama dari proyek lain yang menyebut QAT/OpenVINO, jangan menggabungkannya dengan hasil Knowledge Development ini.

### Ikuti format tabel yang sudah ada

1. Baca `analisis_performa/tabel/T01_*.md` sampai `T14_*.md`, `analisis_performa/DEFINISI.md`, `PROMPT_PERBAIKAN_KODE_DAN_ANALISIS_PERFORMA.md` bagian 6, dan draf hasil skripsi sebelum menyusun output.
2. Pertahankan nomor, nama file T01–T14, judul `# Tnn. ...`, baris `Status: ...`, urutan, gaya Markdown, nama kolom `snake_case`, satuan dalam header, koma desimal pada Markdown, dan catatan sumber di bawah tabel. Jika template hanya berisi kolom `status`, pakai definisi kolom rinci Tnn pada bagian 6.4 prompt perbaikan sebagai schema yang dimaksud.
3. Perbarui tabel yang sudah ada di `analisis_performa/tabel/`; jangan membuat sistem penomoran atau gaya tabel baru. Bila pasangan CSV tersedia, gunakan titik desimal di CSV seperti aturan repository.
4. Status tabel harus sesuai bukti: `Lengkap`, `Sebagian`, atau `Belum diukur`. Sel yang tidak punya data ditulis `[BELUM DIUKUR]`; jangan membuat angka agar tabel terlihat penuh.

### Tabel yang dikerjakan di komputer lab/server

- **T01 spesifikasi model:** `model`, `method`, `seed`, parameter sebelum/sesudah fusion, GFLOPs @640, ukuran checkpoint MiB, SHA-256, registry manifest.
- **T02 resep pelatihan:** `model`, `seed`, `objective`, epochs configured/completed, batch, optimizer, lr0, lrf, weight decay, warmup, AMP, augmentation, bobot KD feature/box/class, temperatur KD, durasi training, source run. Cantumkan Knowledge Development (KD), objective teacher-only, dan supervised sebagai kontrol terpisah bila sumber mendukung.
- **T03 konvergensi:** model, seed, sampel run, VAL mAP50-95 pada epoch 10/25/50/75/100, best epoch, best VAL mAP50-95.
- **T04 ablasi KD VAL:** mode, bobot, temperatur, metrik VAL. Isi hanya jika pilot kandidat benar-benar ada; jangan membuat hasil ablasi dari TEST.
- **T05 akurasi TEST keseluruhan:** method, metric, jumlah model, mean, sample SD, CI95 bootstrap lintas-seed dan per-model bila tersedia.
- **T06 akurasi per kelas:** method, class, jumlah objek ground truth, AP50/AP50-95, precision, recall, F1 (mean dan SD), jumlah model.
- **T07 selisih berpasangan:** seed, comparison, metric, KD minus supervised, retention versus teacher (%).
- **T08 akurasi ukuran objek:** ukuran, kelas, method/model, jumlah objek, recall/AP yang tersedia. Gunakan definisi ukuran dari protokol; bila prediksi/label yang diperlukan belum ada, biarkan belum diukur.
- **T09 analisis kesalahan:** model, FP per gambar dan kategori FP/FN sesuai schema T09. Gunakan evaluasi VAL yang diizinkan; jelaskan definisi kategori dan jangan menyimpulkan penyebab tanpa bukti.
- **T10 matriks kebingungan:** kelas aktual/prediksi termasuk latar, per model, dengan threshold/split sesuai protokol.
- **T11 sapuan confidence:** threshold dan model; precision, recall, F1, deteksi per gambar; tandai threshold F1 terbaik hanya jika dipilih di VAL.
- **T12 sapuan IoU NMS:** IoU dan model; mAP50, mAP50-95, precision, recall, duplikat, waktu postprocess jika tersedia.
- **T13 sapuan imgsz:** ukuran input dan model; metrik VAL, per kelas, GFLOPs dan latency/FPS server bila sumbernya ada.
- **T14 kalibrasi confidence:** model; ECE; bin confidence; rerata confidence; precision aktual; jumlah deteksi.

### Sumber yang harus diperiksa

Prioritaskan `runs/kd/`, `runs/supervised/`, `runs/final_test/`, `runs/benchmarks/`, `artifacts/thesis_analysis_final_corrected/`, manifest tiap run, `args.yaml`, `results.csv`, `AUDIT_DATASET_SKRIPSI.md`, `PROTOKOL_EKSPERIMEN_SKRIPSI.md`, serta file schema T01–T14. Cocokkan setiap angka dengan source run, seed, split, checkpoint, dan status penguncian TEST. Jangan memakai `thesis_analysis_final/` yang sudah ditandai sebagai keluaran lama jika versi corrected tersedia.

### Aturan analisis

- Pisahkan TRAIN, VAL, dan TEST. VAL digunakan untuk memilih checkpoint/parameter. TEST hanya untuk evaluasi final terkunci; jangan melakukan sweep atau pemilihan berdasarkan TEST.
- Sajikan hasil semua seed dan mean ± sample SD sesuai definisi repository. Bootstrap CI tidak menggantikan variasi antar-seed.
- Jangan menyebut benchmark NVIDIA L40 sebagai hasil ROBOTIS OP3. Tabel ini berisi hasil lab/server saja.
- Jangan mengklaim Knowledge Development mengungguli supervised: laporkan angka dan selisih sesuai sumber.
- Jangan mengubah raw artefacts, checkpoint, manifest historis, atau protokol. Buat hanya perubahan tabel yang diminta dan catat sumber/hash jika format analisis memang menyediakannya.
- Jika schema/angka bertentangan dengan sumber, berhenti pada baris tersebut, jelaskan konflik, dan jangan menebak.

### Hasil yang diminta

Perbarui atau hasilkan T01–T14 dalam format folder yang ada. Berikan ringkasan tabel mana yang lengkap, sebagian, atau belum diukur, beserta path sumber dan alasan keterbatasan. Jangan menyentuh T15–T27 karena itu kelompok pengujian robot.
