# Torque kepala tanpa menulis target

Package baru ini memakai `ServoBus` dari `op3_servo_torque_control` tanpa mengubah package lama. Hanya register Torque Enable alamat 64 ID 19/20 yang ditulis; Goal Position dan servo badan tidak ditulis. Ia memerlukan daya bus aktif, torque badan aktif, posisi aktual = goal, dan dua pembacaan stabil. Posisi, target dan torque dipantau sesaat setelah tiap aktivasi dan selama lima sampel lanjutan. Bila ada perubahan, operasi dihentikan dan keadaan serta perintah yang sudah terlanjur dikirim dicatat; tidak ada jaminan servo tak bergerak di antara sampel. Operator harus menopang robot dan area sendi harus kosong.

Log lokal disimpan di `runs/op3_head_torque_only/`. Jangan dijalankan saat manager memiliki bus. Saat menguji gunakan hanya setelah operator meminta torque dan mengonfirmasi kesiapan fisik.
