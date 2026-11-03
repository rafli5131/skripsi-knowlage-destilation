# Supervised idle slot 1 — pengganti pertama

Run `20261103_eq_sup1337_idle_u1_ulang1` dibuat karena [ulangan awal](../idle-u1/README_ID.md) perlu audit. Protokol inferensi dan preview sama; jendela ukur 06:10:45–06:11:45 UTC. Tidak ada perintah gerak robot.

| Parameter | Hasil |
|---|---:|
| Frame ukur / error | 744 / 0 |
| Latensi rata-rata / P95 | 72,13 / 162,88 ms |
| FPS efektif | 12,41 frame/detik |
| CPU proses | 1301,13% dari satu CPU logis |
| RAM RSS | 353,32 MiB |
| Simpangan kepala / badan maksimum | 1 / 3 count |

Status otomatis **`perlu_audit`**: `r_sho_pitch` bergeser tiga count pada sampel tengah pertama dan sesudah jendela pertama. Karena pengganti ini juga melewati batas idle dua count, data tidak dipakai untuk menggantikan slot 1 pada tabel utama. Ketiga kelas muncul pada 744/744 frame sebagai keluaran model; ini **bukan akurasi berlabel**.

Bukti: [overlay](frame_deteksi_sesudah_jendela.png), [ringkasan](summary_metrics.json), [tabel performa](tabel_performa.csv), [tabel deteksi](tabel_deteksi.csv), [grafik runtime](grafik_runtime_hd.png), [grafik CPU/RAM](grafik_cpu_ram_id.png), dan telemetry [pra](telemetry_pre.txt), [tengah 1](telemetry_mid1.txt), [tengah 2](telemetry_mid2.txt), [sesudah 1](telemetry_after.txt), [sesudah 2](telemetry_after2.txt). Log mentah lokal: `runs/op3_pytorch/20261103_eq_sup1337_idle_u1_ulang1.*`.
