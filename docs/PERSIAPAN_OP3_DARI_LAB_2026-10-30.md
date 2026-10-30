# Persiapan OP3 dari lab, 30 Oktober 2026

Audit server selesai; kesiapan fisik dan runtime robot belum diperiksa. Bukti terstruktur: [op3_preflight.json](../artifacts/lab_audit_20261030/op3_preflight.json).

Empat checkpoint teacher, Hybrid full seed 1337, supervised seed 1337, dan Pure KD seed 42 berhasil dimuat. SHA-256 cocok dengan registry dan kelas semuanya `0: ball`, `1: gawang`, `2: robot`. Parameter student 810.649 dan teacher 2.590.425. Alias `op3_default` tetap Pure KD seed 42; sesi Hybrid harus memilih `model_variant:=hybrid`, sedangkan supervised memakai path seed 1337 eksplisit.

Gunakan [prompt OP3 24 Oktober](../prompt/PROMPT_UJI_ROBOT_OP3_SETELAH_KONFIRMASI_KD_2026-10-24.md) sebagai prosedur utama. [Template manifest](../artifacts/lab_audit_20261030/op3_session_template.json) hanya persiapan; semua nilai kosong harus diisi dari pemeriksaan/sesi nyata. Hash model tersedia pada hasil audit, namun harus diverifikasi kembali pada robot.

Pada robot, pastikan runtime Python/ROS dan dependency CPU termasuk lap sesuai `requirements-op3-pytorch.txt`, topic kamera/QoS, teacher privat, operator, dan kondisi fisik. Matriks benchmark adalah empat model × dua kondisi × tiga ulangan, mengikuti urutan dan syarat sah dalam prompt. Capture frame dilakukan terpisah dari benchmark. Bekukan jumlah sampel, variasi sesi, aturan sampling, definisi kotak, dan ambang sebelum pengumpulan set baru; tinjau seluruh frame termasuk negatif.

Tidak ada angka runtime atau akurasi robot baru yang dihasilkan oleh audit server ini. Teacher dan data mentah tetap privat. Transfer teacher mengikuti `docs/TRANSFER_TEACHER_KE_OP3.md` ketika host robot tersedia.
