# Catatan Historis Pemeriksaan OpenVINO untuk Student KD di OP3

## Status keputusan

Keputusan terbaru: **OpenVINO tidak digunakan**. Deployment direncanakan memakai checkpoint `.pt` melalui PyTorch/Ultralytics pada CPU OP3. Catatan ini disimpan sebagai rekam pemeriksaan sebelumnya dan bukan rencana runtime skripsi saat ini.

## Pemeriksaan yang selesai

- Checkpoint yang dipakai: student pure KD seed 2025, `runs/kd/yolo11_tiny_pure_kd_v4_seed2025/weights/best.pt`.
- Environment proyek: Ultralytics 8.4.130, PyTorch 2.4.1+cu121, ONNX 1.17.0, OpenVINO 2024.4.0.
- Ekspor FP32, ukuran input 640, batch 1 ke OpenVINO berhasil. Model hasil ekspor berada di `/tmp/op3_kd_openvino_precheck/student_best_openvino_model/` dan bersifat sementara.
- Smoke inference pada satu gambar VAL berhasil. PyTorch dan OpenVINO menghasilkan tiga deteksi dengan kelas yang sama (`ball`, `robot`, `robot`); selisih maksimum koordinat kotak sekitar `0,000061` piksel.
- Host pemeriksaan memakai CPU AMD EPYC, bukan NUC OP3. Hasil satu gambar ini tidak mengukur mAP, latensi OP3, FPS live, utilisasi CPU, atau RAM sistem robot.

## Implikasi

Saat pemeriksaan dilakukan, spesifikasi yang dikirim cocok dengan prasyarat utama OpenVINO CPU: Intel Core generasi ke-12, AVX2, Ubuntu 24.04, dan Python 3.12. Versi kernel OP3 belum dikirim. ROS 2 Jazzy menargetkan Ubuntu 24.04 sebagai platform Tier 1.

Pemeriksaan ekspor di host hanya menunjukkan model bisa diekspor dan dijalankan di host tersebut; itu bukan hasil benchmark OP3.

Student yang diperiksa tetap model pure KD FP32. Tidak ada QAT/INT8.

## Data perangkat yang diterima

Hasil terminal yang diterima:

```bash
Architecture: x86_64
Model name: 12th Gen Intel(R) Core(TM) i5-1240P
CPU flags include: avx2
OS: Ubuntu 24.04.5 LTS (Noble)
Python: 3.12.3
ROS_DISTRO: jazzy
```

Langkah deployment yang dipilih sekarang adalah memuat `models/weights/kd_student_best.pt` dengan PyTorch/Ultralytics di CPU, lalu menguji frame kamera dan integrasi ROS 2. Ukur inference model serta alur kamera-ke-hasil deteksi secara terpisah.

## Referensi perangkat

- [ROBOTIS OP3 — spesifikasi dan revisi hardware](https://emanual.robotis.com/docs/en/platform/op3/introduction/)
- [OpenVINO 2026 — system requirements](https://docs.openvino.ai/2026/about-openvino/release-notes-openvino/system-requirements.html)
- [OpenVINO 2025 — release notes, persyaratan AVX2 mulai 2026.0](https://docs.openvino.ai/2025/about-openvino/release-notes-openvino.html)
- [ROS 2 Jazzy — Ubuntu target platforms](https://docs.ros.org/en/jazzy/Installation/Alternatives/Ubuntu-Development-Setup.html)
