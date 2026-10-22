# T32. Benchmark inferensi KD Hybrid dan supervised di server

NVIDIA L40, FP32, batch 1, imgsz 640, satu frame VAL tetap di memori; 30 iterasi pemanasan dan 200 iterasi ukur per checkpoint. Waktu meliputi preprocessing, forward, dan NMS. Images/s berasal dari 1000 dibagi mean latency; angka ini bukan FPS kamera OP3.

| model | seed | mean ms | median ms | p95 ms | images/s | parameter | GFLOPs | ukuran best.pt (byte) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid_full | 42 | 9.760 | 8.887 | 12.631 | 102.5 | 810,649 | 2.429 | 1,910,803 |
| supervised | 42 | 12.693 | 11.681 | 15.927 | 78.8 | 810,649 | 2.429 | 1,909,459 |
| hybrid_full | 1337 | 8.649 | 8.483 | 9.562 | 115.6 | 810,649 | 2.429 | 1,910,803 |
| supervised | 1337 | 12.935 | 13.132 | 15.315 | 77.3 | 810,649 | 2.429 | 1,909,523 |
| hybrid_full | 2025 | 8.764 | 8.632 | 9.578 | 114.1 | 810,649 | 2.429 | 1,910,803 |
| supervised | 2025 | 11.523 | 12.323 | 13.932 | 86.8 | 810,649 | 2.429 | 1,909,459 |

Seluruh model memakai arsitektur, parameter, dan GFLOPs yang sama. Perbedaan waktu dari satu urutan benchmark ini tidak membuktikan KD menyebabkan percepatan. CPU, RAM, latency end-to-end, dan FPS robot perlu pengukuran langsung pada OP3.
