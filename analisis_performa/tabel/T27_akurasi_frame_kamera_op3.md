# T27. akurasi frame kamera OP3

Status: **Sebagian.** Evaluasi **eksploratif** pada frame kamera OP3 berlabel manusia sudah tersedia. Evaluasi final lintas hari/adegan dan keputusan set D8 belum dikunci; angka di bawah tidak mewakili seluruh kondisi operasi robot.

## Set utama: 260 frame

Set utama terdiri dari **200 frame dengan target** dan **60 frame negatif**, dengan 400 kotak *ground truth* (`ball` 160, `gawang` 80, `robot` 160). KD dan kontrol supervised seed 42 diuji pada gambar dan label yang sama. Baris `macro` memakai rerata precision dan recall tiga kelas; F1 utama dihitung sebagai rerata harmonik kedua nilai itu, sama seperti T04/T05. `F1_mean_per_class` adalah rerata F1 tiga kelas dan hanya ditampilkan sebagai metrik sekunder. Hitungan TP/FP/FN pada baris `macro` adalah jumlah semua kelas. Frame negatif masuk evaluasi set utama, dan jumlah frame negatif dengan prediksi palsu ditampilkan terpisah di bawah.

| model | class | GT | TP | FP | FN | precision | recall | F1 | F1_mean_per_class | mAP50 | mAP50–95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| KD seed 42 | macro | 400 | 215 | 126 | 185 | 0,739 | 0,473 | 0,577 | 0,501 | 0,630 | 0,422 |
| KD seed 42 | ball | 160 | 159 | 10 | 1 | 0,941 | 0,994 | 0,967 | — | 0,995 | 0,923 |
| KD seed 42 | gawang | 80 | 12 | 0 | 68 | 1,000 | 0,150 | 0,261 | — | 0,328 | 0,116 |
| KD seed 42 | robot | 160 | 44 | 116 | 116 | 0,275 | 0,275 | 0,275 | — | 0,567 | 0,226 |
| Supervised seed 42 | macro | 400 | 247 | 184 | 153 | 0,748 | 0,556 | 0,638 | 0,572 | 0,672 | 0,419 |
| Supervised seed 42 | ball | 160 | 159 | 5 | 1 | 0,970 | 0,994 | 0,981 | — | 0,995 | 0,815 |
| Supervised seed 42 | gawang | 80 | 20 | 0 | 60 | 1,000 | 0,250 | 0,400 | — | 0,732 | 0,306 |
| Supervised seed 42 | robot | 160 | 68 | 179 | 92 | 0,275 | 0,425 | 0,334 | — | 0,288 | 0,137 |

## Catatan set gawang parsial: 50 frame terpisah

Set ini memuat 110 kotak GT: 50 `ball`, 50 `gawang`, dan 10 `robot`. Sebagian label `gawang` hanya mencakup satu tiang yang terlihat, berbeda dari definisi kotak rangka yang terlihat pada set utama. Label awal dibuat dari prediksi KD sebelum ditinjau manusia, sehingga ada risiko bias anotasi ke KD. Pada sesi `gawang_ball_01`, catatan mentah mencatat 40 TP `gawang` untuk KD; pada 10 frame posisi tambahan kedua model memiliki nol TP `gawang`. Angka lengkap tetap tersedia di CSV dan artefak sumber untuk audit, tetapi set ini **tidak digunakan untuk perbandingan KD dengan supervised, pemilihan model, atau penggabungan mAP dengan set utama**.

## Frame negatif pada set utama

| model | frame negatif | frame dengan prediksi palsu | jumlah kotak palsu | kelas kotak palsu |
| --- | ---: | ---: | ---: | --- |
| KD seed 42 | 60 | 0 | 0 | tidak ada |
| Supervised seed 42 | 60 | 12 | 12 | robot |

## Protokol, sumber, dan batas klaim

- **Sumber angka:** [`summary.csv`](../../runs/op3_multi_session_eval/20261021_primary260_partial50_v1/summary.csv) dan [`results.json`](../../runs/op3_multi_session_eval/20261021_primary260_partial50_v1/results.json). [`input_manifest.json`](../../runs/op3_multi_session_eval/20261021_primary260_partial50_v1/input_manifest.json) menyimpan SHA-256 checkpoint, gambar, label, dan log peninjau. Metode dan komposisi sesi dijelaskan pada [percobaan 13](../../dokumentasi/2026-10-21/percobaan-13-evaluasi-deteksi-multi-sesi/README.md).
- Evaluasi offline memakai FP32 CPU, input 640, tanpa augmentasi, NMS IoU 0,7. AP memakai confidence floor 0,001. Precision/recall/F1 memakai **confidence >0,25** dan IoU pencocokan ≥0,50. F1 utama dihitung ulang dari TP/FP/FN per kelas pada `results.json` sebagai rerata harmonik precision makro dan recall makro. Nilai F1 asli dari `summary.csv` disimpan di `F1_mean_per_class`; artefak sumber tidak diubah. Metrik pada frame negatif tidak didefinisikan tanpa GT positif; jumlah deteksi palsu dilaporkan tersendiri.
- Semua 310 pasangan gambar-label telah diperiksa kelengkapan/formatnya pada komputer OP3 dan ditinjau oleh `bhre`. Frame berasal dari satu lingkungan dan hari yang sama; sebagian frame berdekatan berkorelasi. **Set utama pun mempunyai risiko bias anotasi** karena label manusia berawal dari draf prediksi KD; peninjauan manusia tidak otomatis menghilangkan pengaruh draf itu. Set `ball_moving_candidate_01` memuat 32 frame asli dan 8 pengganti terkurasi; cocok untuk deteksi per frame, bukan tracking temporal.
- Set negatif terdiri dari 52 frame sesi awal dan 8 pengganti setelah pemeriksaan visual menemukan objek/ketidakpastian pada delapan frame awal. Detektor KD aktif selama penangkapan dan tidak mengeluarkan deteksi pada sesi itu, lalu dipakai lagi untuk draf label kosong. Karena pemilihan akhir dijelaskan sebagai kurasi visual tetapi log keputusan per frame tidak tersedia di checkout server, ketergantungan seleksi pada keluaran model **tidak dapat dipastikan dari artefak**; lihat [percobaan 02](../../dokumentasi/2026-10-21/percobaan-02-frame-negatif/README.md) dan [percobaan 12](../../dokumentasi/2026-10-21/percobaan-12-peninjauan-60-frame-negatif/README.md).
- Pada checkout lab/server ini, JPEG dan `labels_reviewed/` tidak ada karena folder sesi diabaikan Git. Tabel ini **menyalin hasil evaluasi yang tersimpan**, bukan menjalankan ulang inferensi atau memverifikasi ulang hash gambar/label. Untuk reproduksi penuh, pindahkan data sumber dari OP3 dan cocokkan hash pada manifest.
- Selisih mAP50–95 set utama KD–supervised sekitar **+0,0024** pada sampel ini; angka ini tidak membuktikan keunggulan umum KD. Recall `gawang` dan `robot` KD pada confidence 0,25 masing-masing 0,150 dan 0,275. Teacher tidak dievaluasi pada set ini karena checkpoint-nya tidak tersedia di komputer OP3. Hasil TEST Roboflow, evaluasi offline frame OP3, dan FPS live OP3 adalah tiga bukti dengan domain/protokol berbeda.
- Keputusan D8 tentang set evaluasi final kamera OP3 belum dikunci. Kondisi `walking`, hari/adegan independen, dan aturan label gawang final masih terbuka. Sesi idle awal 120 frame pada [percobaan 01](../../dokumentasi/2026-10-21/percobaan-01-monitor-rekam-servo-idle/README.md) dilaporkan terpisah karena adegan relatif tetap dan tidak digabung ke set utama.
