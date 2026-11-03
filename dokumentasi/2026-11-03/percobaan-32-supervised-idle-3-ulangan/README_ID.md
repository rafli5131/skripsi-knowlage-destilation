# Percobaan 32 — Supervised idle, tiga ulangan aktif

Pada 3 November 2026 dilakukan uji idle Supervised seed 1337 dengan preview SSH-X, tanpa perintah gerak robot. Tiga run aktif lulus pemeriksaan otomatis CSV dan telemetry. Pemilihan pengganti didasarkan pada batas simpangan sendi, bukan performa. Ulangan awal 1 dan 3 serta pengganti pertama 1 tetap tersedia untuk audit.

| Slot | Run aktif | Frame | Latensi rata-rata | FPS | CPU proses | RSS |
|---|---|---:|---:|---:|---:|---:|
| 1 | [Pengganti kedua](03-supervised/idle-u1-ulang2/README_ID.md) | 719 | 74,48 ms | 12,00 | 1300,69% | 354,96 MiB |
| 2 | [Ulangan 2](03-supervised/idle-u2/README_ID.md) | 749 | 69,39 ms | 12,47 | 1295,37% | 359,63 MiB |
| 3 | [Pengganti pertama](03-supervised/idle-u3-ulang1/README_ID.md) | 717 | 75,48 ms | 11,94 | 1301,47% | 353,19 MiB |

Rerata ± simpangan baku sampel tiga run: latensi **73,12 ± 3,27 ms**, FPS **12,14 ± 0,29**, CPU proses **1299,18 ± 3,32% dari satu CPU logis**, dan RSS **355,93 ± 3,32 MiB**. Total 2.185 frame ukur, tanpa error frame. Ketiga kelas menghasilkan keluaran pada seluruh frame tersebut; cakupan keluaran bukan akurasi berlabel.

[Grafik tiga ulangan HD](03-supervised/grafik_sup1337_idle_ulangan_1_2_3_hd.png), [English graph](03-supervised/graph_sup1337_idle_repetitions_1_2_3_hd.png), [tabel tiga run](05-ringkasan/tabel_3_run.csv), [agregat](05-ringkasan/tabel_agregat_saat_ini.csv), screenshot dan telemetry per run tersedia. [Log penyimpangan](log_penyimpangan.md) menjelaskan perubahan bahu kanan, pemilihan run, dan batas bukti. Audit akhir protokol masih terbuka: torque tidak dibaca langsung saat manager menguasai bus, dan foto luar, jarak, serta frame referensi mentah pra/pasca tidak tersedia.

Kampanye sekarang memiliki **15/24 slot terukur dan lulus cek otomatis**: teacher dan Hybrid idle/berjalan, serta Supervised idle. Tersisa sembilan slot Supervised berjalan dan KD murni idle/berjalan. [Matriks lintas hari](../../2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv) dan grafiknya telah diperbarui; T36/T37 belum final.
