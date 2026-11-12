# Log progres skripsi, 11 November 2026

> **Pembaruan 12 November:** grafik runtime dan draf tujuh bab sudah tersedia; lihat [log terbaru](../2026-11-12/LOG_PROGRES_SKRIPSI.md). Status pekerjaan terbuka di bawah merupakan snapshot 11 November.

## Keputusan

- **D17:** naskah memakai struktur tujuh bab implementatif-pengembangan. Pemetaan materi ada di [folder draf](../../laporan/draf-bab-iv-v/README.md).
- **D18:** Bhre melaporkan persetujuan pembimbing atas protokol uji live dan hasil runtime deskriptif, daftar KF/KNF dengan pengujian retrospektif, Hybrid full seed 1337 sebagai model KD utama, serta nilai D3, D4, D6, D7, D8, dan D11. Nilai dikunci di [`configs/analysis.yaml`](../../configs/analysis.yaml). Tanggal dan bentuk persetujuan belum dicatat.
- **D19:** rencana evaluasi set frame OP3 baru (usulan T43) dengan pra-label dari model yang tidak dievaluasi, tinjauan semua frame, dan audit label buta 20%. Prosedur: [prompt evaluasi set frame baru](../../prompt/PROMPT_EVALUASI_SET_FRAME_BARU_OP3_2026-11-11.md).

Rincian ada di [`docs/DECISIONS.md`](../../docs/DECISIONS.md).

## Hasil yang ditambahkan

- **Grafik garis kontinu akurasi** di [`dokumentasi/model/`](../model/README.md): akurasi VAL per epoch (mAP50, mAP50–95, precision, recall, F1) untuk tiga metode student, kurva mAP50–95 VAL gabungan, dan sapuan confidence P/R/F1 empat model dari T11. Definisi dan batas tercantum di README tiap folder; manifest hash di [`manifest_grafik_garis_akurasi.json`](../model/manifest_grafik_garis_akurasi.json).
- **Uji fungsional RQ1** dapat diisi dari log yang ada: KF-01 (0 error frame pada 24 run, T36), KF-02 dan KF-03 (enam run Hybrid seed 1337: bola dan robot terdeteksi pada 100% frame, gawang 93,4 sampai 99,0%, satu ID per kelas termasuk saat berjalan; `tabel_deteksi.csv` percobaan 30 dan 31), KF-04 (CSV per frame), KF-05 (screenshot preview), dan KNF-01 (FPS ≥ 8 lulus untuk semua model; terendah teacher 9,87, T37). Terdeteksi tidak sama dengan benar; kebenaran kotak berasal dari T38.

## Pekerjaan terbuka

1. **Grafik garis runtime** (latensi, FPS, CPU, RSS): 15 dari 24 `jendela_runtime.csv` sesi 3 November hanya ada di robot. Prosedur: [prompt grafik runtime](../../prompt/PROMPT_GRAFIK_RUNTIME_OP3_GARIS_KONTINU_2026-11-11.md).
2. **Set frame OP3 baru** sesuai D19. Bobot teacher YOLO11s T42 untuk pra-label perlu disalin dari server lab ke robot di luar Git, dengan verifikasi hash.
3. **Penulisan naskah tujuh bab**, termasuk tabel uji kotak hitam di Bab 6 dan pembaruan proposal subbab 3.3.4 (T42) dan 3.3.5 (cara pelabelan sesuai praktik).
4. **Catatan persetujuan pembimbing:** isi tanggal dan bentuknya pada D18.
5. **Cadangan bobot:** teacher utama (hanya di OP3) dan teacher T42 (hanya di server lab) perlu salinan di luar perangkat tersebut.

Tidak ada pengukuran baru, pelatihan, aktivasi kamera, atau gerakan robot dalam pekerjaan ini.
