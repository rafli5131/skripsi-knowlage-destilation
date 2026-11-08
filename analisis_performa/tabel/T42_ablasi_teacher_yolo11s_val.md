# T42: ablasi kapasitas teacher YOLO11n vs YOLO11s pada VAL

Kedua teacher dilatih dari bobot COCO resmi dengan data, resep, dan seed 42 yang sama. Student YOLO11 skala t dilatih dengan Hybrid full dan tiga seed berpasangan. Hasil ini hanya pada VAL; TEST dan kamera OP3 tidak dipakai. Percobaan: `server2` (status `runs/kd_teacher_ablation/server2/t42_status.jsonl`).

| Teacher | mAP50–95 teacher | mAP50–95 student, rerata ± SD |
| --- | ---: | ---: |
| YOLO11n | 0.7760 | 0.7482 ± 0.0003 |
| YOLO11s | 0.7843 | 0.7473 ± 0.0003 |

Selisih student berpasangan (teacher s − n): -0.0009 ± 0.0006 pada seed 42, 1337, 2025. Rincian per seed, F1, kontrol supervised, dan rasio pemulihan ada di [CSV](T42_ablasi_teacher_yolo11s_val.csv).

Teacher YOLO11n pada ablasi ini dilatih ulang; teacher utama lama memiliki provenance resep berbeda. Hasil ablasi tidak mengganti checkpoint Hybrid full yang dipilih untuk OP3. Tiga seed memberikan analisis deskriptif, bukan bukti signifikansi statistik. Puncak GPU teacher berasal dari PyTorch; puncak GPU student disampel dari proses dengan interval 20 detik sehingga dapat lebih rendah dari puncak sebenarnya.
