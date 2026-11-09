# Audit 24 run dan bahan hasil skripsi

> Pembaruan 5 November 2026: [T38 empat model pada 260 frame OP3](../../../analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md) telah selesai; status T38 dalam audit 3 November ini adalah catatan historis.

Audit baca-saja menemukan **24 dari 24 run aktif lolos pemeriksaan log dan sampel telemetry**. Hash checkpoint, parameter inferensi, label kondisi, warm-up, jendela 60 detik, urutan waktu, frame error, timestamp kamera, FPS dan rerata latensi cocok dengan sumber yang diperiksa. Dua belas run berjalan memiliki guard dan ack mulai/berhenti; pemeriksaan ulang telemetry menggunakan fungsi laporan yang sudah ada. Ini adalah hasil pemeriksaan bukti yang tersedia, **bukan pengesahan penuh kesetaraan protokol**.

## Hasil dan berkas

- [T36 per run](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) · [CSV lengkap dengan hash sumber](../../../analisis_performa/tabel/T36_runtime_live_setara_per_run.csv) · [enam run tidak aktif/diganti](T36_lampiran_run_tidak_aktif.csv).
- [T37 ringkasan delapan pasangan](../../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.md) · [CSV lengkap](../../../analisis_performa/tabel/T37_runtime_live_setara_ringkasan.csv) · [tahapan per run](rincian_tahapan_per_run.csv).
- [Grafik runtime Indonesia](grafik_runtime_24_run_id_hd.png) · [English](grafik_runtime_24_run_en_hd.png), masing-masing 2880×1800 piksel. Titik adalah rerata tiga run, batang adalah SD sampel, tanda silang adalah tiap run.
- [Hasil audit log/hash](audit.json) · [audit telemetry](audit_telemetry.csv) · [audit log peninjauan label](audit_review_labels.json) · [draf pembahasan](DRAF_PEMBAHASAN.md).
- [Ringkasan akurasi TEST empat metode](TABEL_AKURASI_TEST.md) · [waktu training dan pengujian T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md).

Rerata latency teacher/Hybrid masing-masing **96,24/64,70 ms saat idle** dan **95,85/71,47 ms saat berjalan**. Rasio latency teacher terhadap Hybrid adalah **1,49× idle** dan **1,34× berjalan**; FPS Hybrid terhadap teacher adalah **1,38× idle** dan **1,27× berjalan**. Rasio adalah perbandingan rerata deskriptif, bukan bukti sebab-akibat atau signifikansi dari tiga ulangan. CPU dilaporkan sebagai persen satu CPU logis dan dalam CSV juga sebagai persen dari 16 CPU logis; RSS adalah memori resident proses detector.

## Temuan yang membatasi interpretasi

1. Urutan aktual berbentuk blok lintas 2–3 November, bukan rotasi model sesuai rencana. Suhu, waktu, kondisi adegan, dan urutan berpotensi memengaruhi perbandingan. Jarak objek dan pencahayaan tidak diukur secara kuantitatif.
2. Set teacher berjalan aktif dipilih ulang setelah cakupan gawang set awal terlihat dan objek ditata kembali. Run lama tetap ada dalam [arsip teacher](../../2026-11-02/percobaan-30-uji-live-setara-empat-model/01-teacher/arsip-set-sebelumnya-20261102-1200/) dan [lampiran run tidak aktif](T36_lampiran_run_tidak_aktif.csv); pemilihan tersebut harus dilaporkan.
3. Screenshot overlay khusus tepat setelah jendela tidak ditemukan pada teacher idle u1/u2; u2 memiliki `preview_setelah_run.png` tetapi bukan bukti screenshot sesuai waktu protokol. Hybrid berjalan u1 memakai baseline telemetry enam sendi dengan provenance, bukan snapshot 20 sendi. Semua ack gait dan sampel yang digunakan pemeriksaan tetap tersedia.
4. Status torque saat beberapa sesi 3 November tidak dibaca langsung saat manager menguasai bus. Preview diaktifkan menurut metadata, tetapi video layar tidak tersedia untuk membuktikan tampilan tidak freeze pada setiap frame. Foto adegan luar, jarak dan 10 frame referensi pra/pasca tidak lengkap; suhu akhir beberapa run tidak tersimpan. Jangan menyatakan semua syarat protokol terbukti terpenuhi.
5. Beberapa run diganti setelah kegagalan kriteria telemetry atau atas permintaan pengguna. Gunakan pemetaan `active_run_sources.json` dan lampiran; jangan membuang run yang tidak aktif. Ulangan awal KD murni berjalan u3 memiliki gerak sendi dalam sampel guard tetapi gagal cek dua sampel tengah; penggantinya menjadi run aktif dan lulus cek otomatis.

## Label dan akurasi

Manifest kamera lama mencakup **200 frame utama berobjek, 60 negatif, dan 50 parsial**. Seluruh hash gambar/label cocok; semua frame dalam manifest tercakup dalam log peninjauan `bhre` dan hash log cocok. Ada beberapa entri log berulang, tetapi tidak ada frame manifest tanpa entri review. Ini mendukung bahwa peninjauan telah dilakukan; **tidak perlu mengulang audit manual seluruh frame hanya untuk memverifikasi kelengkapan ini**.

Label awal dibantu prediksi KD murni sebelum ditinjau, berasal dari satu rangkaian pengambilan, dan 50 frame gawang parsial dikeluarkan dari angka utama. [T34](../../../analisis_performa/tabel/T34_akurasi_op3_hybrid_supervised_seed1337.md) adalah perbandingan eksploratif Hybrid dan Supervised pada 260 frame, bukan evaluasi independen lintas adegan. T38 empat model pada set 260 frame belum dijalankan pada audit ini. [T05](../../../analisis_performa/tabel/T05_akurasi_test_keseluruhan.md) dan [T30](../../../analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md) menyimpan evaluasi TEST resmi; TEST telah pernah digunakan sebelumnya dan bukan holdout yang belum tersentuh. [T35](../../../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md) memisahkan waktu training, sesi TEST, dan latensi.

**Status:** pengguna telah [menerima hasil untuk analisis deskriptif](KEPUTUSAN_PENGGUNA.md) dengan keterbatasan di atas. Persetujuan pembimbing belum dicatat, dan kesetaraan kondisi fisik tidak dinyatakan terbukti. Jika ingatan operator tidak dapat memastikan kondisi yang tidak direkam, tuliskan `tidak terdokumentasi`; jangan merekonstruksi nilai.
