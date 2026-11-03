# Supervised idle slot 1 — pengganti kedua, run aktif

Run `20261103_eq_sup1337_idle_u1_ulang2` dibuat setelah [ulangan awal](../idle-u1/README_ID.md) dan [pengganti pertama](../idle-u1-ulang1/README_ID.md) melewati batas deviasi badan. Checkpoint, kamera, BoT-SORT, threshold, thread, warm-up, dan preview sama. Jendela ukur 06:17:51–06:18:51 UTC; tidak ada perintah gerak robot.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 719 / 0 |
| Latensi rata-rata / P95 | 74,48 / 161,82 ms |
| FPS efektif | 12,00 frame/detik |
| CPU proses | 1300,69% dari satu CPU logis |
| RAM RSS | 354,96 MiB |
| Simpangan kepala / badan maksimum | 0 / 1 count |

Status otomatis **`lulus_cek_otomatis`**. Run ini dipakai sebagai slot 1 aktif berdasarkan batas telemetry, bukan nilai performa. Dua run sebelumnya tetap tersimpan. Bola, gawang, dan robot masing-masing muncul pada 719/719 frame menurut keluaran model; **cakupan bukan akurasi berlabel**. Audit protokol akhir masih diperlukan.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), serta telemetry [pra](telemetry_pre.txt), [tengah 1](telemetry_mid1.txt), [tengah 2](telemetry_mid2.txt), [sesudah 1](telemetry_after.txt), [sesudah 2](telemetry_after2.txt). Log mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_idle_u1_ulang2.*`.
