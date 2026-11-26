# Guard persiapan bahu berbasis count

Wrapper package baru ini menggunakan prosedur `op3_t43_arm_ready` sebagai shared, tanpa mengubah package lama. Telemetry kepala dikonversi ke count XM430 dengan `op3_walk_video_guard`; pengaman menghentikan persiapan jika pembacaan melewati dua count dari acuan sebelum startup. Tidak mengirim perintah target kepala atau start gait. Operator harus menopang badan dan kepala, area harus kosong, dan stop tidak menjamin transisi pose seketika berhenti.
