# Memori 23 Oktober 2026: diagnosis lab KD dan revisi prompt OP3

Sumber angka primer: [T39](../analisis_performa/tabel/T39_diagnosis_objektif_kd.md), [laporan lab](../analisis_performa/lab_server/HASIL_DIAGNOSIS_KD_JALUR_TENGAH_2026-10-23.md), dan JSON mentah di `runs/val_ablation/hybrid_20261023_phase0_reproduction/`, `runs/val_diagnostics/hybrid_objective_20261023/`, serta `runs/kd_diagnosis/`.

## Yang selesai

- Fase 0 prompt perbaikan KD: audit teacher dan runtime, reproduksi VAL Hybrid full/Supervised seed 42. Angka mAP50–95 serta F1@0,25 identik dengan hasil sebelumnya.
- Fase 1 yang tersedia: sapuan ambang tiga seed tiap metode, histogram TP/FP per kelas, ECE diagnostik, bentuk head dan proporsi anchor teacher pada satu batch VAL, serta komponen loss label dan head yang dapat dipulihkan. T39 dibuat tanpa data TEST.
- Kode menunjukkan kotak head adalah 4 × 16 kanal DFL; checkpoint saat ini hanya mempunyai `one2many`. Proyektor fitur terlatih tidak tersimpan bersama student, sehingga feature loss historis belum terukur.
- Prompt lab dikoreksi untuk klaim TEST yang telah terbuka, loss klasifikasi BCE yang tidak nol saat student sama dengan teacher, kondisi cabang head, kontrol ukuran teacher, dan anggaran epoch. Prompt live OP3 dikoreksi untuk preflight servo yang berbeda saat kepala torque on/off, pembacaan tegangan/suhu sebelum manager, domain waktu pengukuran, peran operator, batas evaluasi 260 frame lama, dan rencana set OP3 baru untuk akurasi eksternal. Keputusan D13/D14 ditambahkan tanpa menghapus D12 historis.

## Yang belum selesai

- `hybrid_v2` belum diimplementasi/dilatih. GPU tidak terlihat dari sandbox saat ini, tetapi pemeriksaan baca-saja host melihat tiga L40 yang sedang dipakai. Grid penyaringan dan aturan seleksi perlu dikunci berdasarkan T39 sebelum training baru; eksperimen baru tetap eksploratif karena TEST resmi sudah diketahui.
- Teacher YOLO11s dan kontrol teacher YOLO11n resep sama belum dilatih. T40–T43 belum ada.
- Robot belum diakses. Data mentah 260 frame OP3 tidak ada pada server ini, sehingga T36–T38 dan uji live setara empat model belum dikerjakan. Untuk akurasi independen model baru, ambil sesi OP3 baru dan tinjau label final tanpa bergantung pada prediksi kandidat.

Jangan menyimpulkan driver NVIDIA host rusak dari kegagalan `nvidia-smi` dalam sandbox. Jangan menghapus atau menimpa artefak lama. Perubahan lokal yang sudah ada sebelum sesi ini pada `docs/DECISIONS.md`, `AGENTS.md`, `agent.md`, dan berkas audit 22 Oktober dipertahankan.
