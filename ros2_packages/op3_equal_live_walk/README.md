# OP3 equal live walking guard

Paket baru ini memulai gait melalui topic standar hanya setelah detektor melewati 30 frame warm-up. Ia menunggu ack `Start walking` dari `/robotis/status`, mencatat waktu NUC, menghentikan gait setelah 63 detik, dan menghentikan lebih awal jika posisi kepala bergeser lebih dari dua count atau telemetry sendi terputus. Kepala tidak menerima perintah posisi atau modul gerak. Penggunaan memerlukan operator yang mendampingi dan robot walk-ready.
