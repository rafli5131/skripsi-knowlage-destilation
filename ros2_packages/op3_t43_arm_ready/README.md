# Penyesuaian bahu T43

Package baru menggunakan monitor bersama `op3_t43_walk_ready` dan memetakan hanya `l_sho_pitch` serta `r_sho_pitch` ke walking module; kepala harus tetap `none`. Bahu/kaki dapat bergerak saat modul bersiap. Penghentian gait tidak dijamin menghentikan transisi pose yang sedang berlangsung. Operator harus menopang robot dan memeriksa pose sebelum gait.
