# T13. sapuan imgsz

Status: Sebagian; titik dasar 640 tersedia, sapuan ukuran input dan metrik VAL per kelas belum tersedia.

| model | method | imgsz_px | split_metric | val_mAP50 | val_mAP50_95 | val_AP50_95_per_class | GFLOPs | latency_median_ms_server | throughput_images_s_server | benchmark_device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kd_seed42 | Pure KD | 640 | VAL | 0,9620 | 0,6825 | [BELUM DIUKUR] | 2,4291 | 25,28 | 39,30 | NVIDIA L40 |
| kd_seed1337 | Pure KD | 640 | VAL | 0,9509 | 0,6757 | [BELUM DIUKUR] | 2,4291 | 24,81 | 41,77 | NVIDIA L40 |
| kd_seed2025 | Pure KD | 640 | VAL | 0,9628 | 0,6789 | [BELUM DIUKUR] | 2,4291 | 24,92 | 41,37 | NVIDIA L40 |
| supervised_seed42 | Supervised student | 640 | VAL | 0,9733 | 0,7189 | [BELUM DIUKUR] | 2,4291 | 24,89 | 41,00 | NVIDIA L40 |
| supervised_seed1337 | Supervised student | 640 | VAL | 0,9674 | 0,7181 | [BELUM DIUKUR] | 2,4291 | 25,26 | 40,51 | NVIDIA L40 |
| supervised_seed2025 | Supervised student | 640 | VAL | 0,9705 | 0,7252 | [BELUM DIUKUR] | 2,4291 | 24,85 | 41,14 | NVIDIA L40 |
| teacher_fp32 | Teacher | 640 | VAL | 0,9738 | 0,7785 | [BELUM DIUKUR] | 6,5017 | 25,72 | 39,60 | NVIDIA L40 |

Sumber: [per_model.csv](../../artifacts/thesis_analysis_final_corrected/per_model.csv), [benchmark server](../../runs/benchmarks/pure_kd_final_inference.json), dan [protokol eksperimen](../../PROTOKOL_EKSPERIMEN_SKRIPSI.md).

Semua baris memakai imgsz 640 dan benchmark batch 1 pada NVIDIA L40; throughput_images_s_server adalah gambar per detik pada server, bukan FPS kamera OP3. Nilai VAL di sini berasal dari per_model.csv, sedangkan T03 memakai log training results.csv.
