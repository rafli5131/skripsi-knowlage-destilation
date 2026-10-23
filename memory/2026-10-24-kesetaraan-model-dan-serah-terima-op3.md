# Memori: kesetaraan model dan serah terima uji OP3, 24 Oktober 2026

## Keputusan saat ini

- Model KD utama tetap **Hybrid full seed 1337**. Konfirmasi tiga seed pada [T41](../analisis_performa/tabel/T41_konfirmasi_hybrid_v2_val.md) menunjukkan kandidat `hybrid_v2` S2 gagal aturan penggantian yang telah dikunci: mAP50–95 VAL 0,7475 ± 0,0013 versus Hybrid full 0,7505 ± 0,0018; F1@0,25 0,9251 ± 0,0024 versus 0,9205 ± 0,0021. S2 menjadi ablasi, sesuai D16 di [keputusan](../docs/DECISIONS.md).
- Tiga metode student yang dibandingkan ialah supervised, Pure KD `pure_v4` teacher-only, dan KD Hybrid full. Student memakai arsitektur YOLO11 skala `t` kustom dengan 810.649 parameter; **bukan YOLO11n standar**. Teacher ialah YOLO11n FP32.
- Lab sudah menyetarakan arsitektur student, split Roboflow resmi (`TRAIN` 4.600, `VAL` 1.213, `TEST` 592), seed 42/1337/2025, anggaran 100 epoch, resep pelatihan dasar, dan setelan evaluasi. Perbedaan yang sengaja diuji adalah objective training. Ini mendukung perbandingan metode pada split gambar tersebut, bukan bukti bahwa performa ketiganya sudah setara pada kamera atau perangkat OP3.
- Hasil TEST Advance Vision yang sudah ada tetap berlaku dengan batasnya: TEST pernah dibuka sebelum rancangan Hybrid; provenance data latih teacher belum lengkap; nama sumber serupa lintas split belum membuktikan pemisahan sesi. Jangan menyebut TEST sebagai holdout yang sepenuhnya baru. Keunggulan runtime student terhadap teacher berasal dari ukuran/arsitektur model; KD dinilai sebagai cara meningkatkan mutu prediksi student.

## Checkpoint untuk sesi robot

| Peran | Path relatif repo pada OP3 | SHA-256 |
| --- | --- | --- |
| Teacher FP32 (privat) | `models_local/teacher_fp32_best.pt` | `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c` |
| KD Hybrid full seed 1337 (utama) | `runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337/weights/best.pt` | `cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363` |
| Supervised seed 1337 (kontrol) | `runs/supervised/yolo11_tiny_supervised_seed1337/weights/best.pt` | `d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041` |
| Pure KD seed 42 (ablasi) | `models/weights/kd_student_best.pt` | `2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3` |

Registry dan alias `op3_default` belum diubah: alias masih menunjuk Pure KD seed 42. Untuk model utama, pilih `model_variant:=hybrid` secara eksplisit. Transfer teacher mengikuti [panduan privat](../docs/TRANSFER_TEACHER_KE_OP3.md); bobot teacher tidak masuk repo publik.

## Pekerjaan OP3 berikutnya

1. Saat robot siap, jalankan [prompt serah terima OP3](../prompt/PROMPT_UJI_ROBOT_OP3_SETELAH_KONFIRMASI_KD_2026-10-24.md). Audit kamera, runtime, checkpoint, hash, kelas `0: ball`, `1: gawang`, `2: robot`, dan kondisi fisik dahulu. Belum ada hasil dari sesi baru ini.
2. Periksa fungsi live dan tracking tiga kelas dengan Hybrid full. Uji live setara empat model × dua kondisi (`servo_idle`, `walking`) × tiga ulangan menghasilkan T36/T37. Kondisi berjalan dan tindakan servo tetap dikendalikan operator; label kondisi tidak diambil dari detektor.
3. Setelah benchmark runtime selesai, kumpulkan **frame OP3 baru** untuk evaluasi akurasi eksternal. Pisahkan frame mentah, `labels_auto/`, dan `labels_reviewed/`. Bhre memeriksa setiap frame dan kotak, termasuk frame kosong, sebelum evaluasi keempat checkpoint pada gambar dan label identik. Perbandingan utama adalah Hybrid full terhadap Supervised; teacher dan Pure KD menjadi pembanding pendukung. Hasil 260 frame lama T34, serta T38 bila kelak dihitung pada frame yang sama, bersifat retrospektif dan tidak menggantikan set baru.
4. Simpan data gambar, label, video, teacher, dan log mentah robot secara lokal. Publikasikan hanya ringkasan/artefak yang secara eksplisit diminta pengguna. Jangan mengubah model atau threshold berdasarkan hasil OP3 final.

T42 ablasi teacher YOLO11s ialah eksperimen lab terpisah yang belum dikerjakan dan bukan prasyarat uji robot model final ini. T43 TEST tambahan tidak diperlukan karena Hybrid full tidak diganti. Status publikasi laporan dan artefak konfirmasi seed 1337/2025 harus diperiksa dari Git; bobot `last.pt`, log training, dan artefak privat tetap lokal. Tidak ada training atau uji robot yang dijalankan ketika memori ini dibuat.
