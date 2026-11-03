# Supervised idle slot 3 — pengganti pertama

Run `20261103_eq_sup1337_idle_u3_ulang1` dibuat karena [ulangan awal slot 3](../idle-u3/README_ID.md) melewati batas deviasi badan. Pengaturan checkpoint, kamera, BoT-SORT, threshold, thread, warm-up, dan preview sama. Jendela ukur 06:14:19–06:15:19 UTC; tidak ada perintah gerak robot.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 717 / 0 |
| Latensi rata-rata / P95 | 75,48 / 161,49 ms |
| FPS efektif | 11,94 frame/detik |
| CPU proses | 1301,47% dari satu CPU logis |
| RAM RSS | 353,19 MiB |
| Simpangan kepala / badan maksimum | 1 / 2 count |

Status otomatis **`lulus_cek_otomatis`**. Run ini menggantikan ulangan 3 pada matriks aktif; run awal tetap disimpan untuk audit. Bola, gawang, dan robot masing-masing muncul pada 717/717 frame menurut model. **Cakupan keluaran bukan akurasi berlabel.** Audit protokol akhir masih diperlukan.

Bukti: [overlay sebelum](preview_sebelum_run.png), [overlay sesudah jendela](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik runtime](grafik_runtime_hd.png), [grafik latensi](grafik_latensi_id.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), [grafik kelas](grafik_keluaran_kelas_id.png), serta telemetry [pra](telemetry_pre.txt), [tengah 1](telemetry_mid1.txt), [tengah 2](telemetry_mid2.txt), [sesudah 1](telemetry_after.txt), [sesudah 2](telemetry_after2.txt). Log mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_idle_u3_ulang1.*`.
