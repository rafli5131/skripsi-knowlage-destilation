#!/usr/bin/env python3
"""Susun README.md dan manifest_sha256.json untuk ``log_op3_pelengkap/`` (di laptop).

Masukan: ``status_ekstraksi.json`` (15 run), ``status_metadata.json``,
``ringkasan_capture.csv``, status ekstraksi ulang 9 run pembanding beserta hasil
perbandingannya, dan tabel run ``jejak_waktu/timestamp_frame_live_24_run.csv``.
Hanya pustaka standar.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "log_op3_pelengkap"
PACKAGE = ROOT / "ros2_packages/op3_log_pelengkap"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt_e(value: float) -> str:
    return f"{value:.1e}".replace(".", ",")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def tabel_run(ekstrak: dict, konsistensi: dict, banding: dict) -> list[str]:
    runs = list(csv.DictReader((ROOT / "jejak_waktu/timestamp_frame_live_24_run.csv").open(encoding="utf-8")))
    hasil15 = {r["run_id"]: r for r in ekstrak["runs"]}
    hasil9 = {r["run_id"]: r for r in konsistensi["runs"]}
    sama9 = {r["run_id"]: r for r in banding["runs"]}
    lines = ["| run_id | Model | Kondisi | Ulangan | Status | Baris jendela (T36) | Pemeriksaan langkah 5 |",
             "|---|---|---|---:|---|---:|---|"]
    for run in runs:
        rid = run["run_id"]
        if rid in hasil15:
            r = hasil15[rid]
            status = {"diekstrak": "diekstrak", "hash_tidak_cocok": "hash tidak cocok",
                      "tidak_ditemukan": "tidak ditemukan", "pemeriksaan_gagal": "pemeriksaan gagal"}[r["status"]]
        else:
            r = hasil9[rid]
            ident = sama9[rid]
            identik = ident["jendela_runtime"]["identik"] and ident["jendela_deteksi"]["identik"]
            status = "sudah ada di repositori" + ("; ekstraksi ulang identik" if identik else "; ekstraksi ulang BERBEDA")
        c = r["pemeriksaan"]
        if r["status"] == "diekstrak":
            cek = (f"hash cocok; baris dan error sama; Δ latensi {fmt_e(c['rerata_end_to_end_ms']['selisih'])} ms; "
                   f"Δ FPS {fmt_e(c['fps']['selisih'])}")
            n = f"{c['jumlah_baris']['jendela']} ({c['jumlah_baris']['t36']})"
        else:
            cek = json.dumps(c, ensure_ascii=False)
            n = "-"
        lines.append(f"| `{rid}` | {run['model']} | {run['kondisi']} | {run['ulangan']} | {status} | {n} | {cek} |")
    return lines


def tabel_capture() -> list[str]:
    rows = list(csv.DictReader((FOLDER / "ringkasan_capture.csv").open(encoding="utf-8")))
    lines = ["| Set | Sesi | Peran | Kondisi | Frame dipakai | Frame capture | Capture pertama (UTC) | Capture terakhir (UTC) | Sumber timestamp |",
             "|---|---|---|---|---:|---:|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['set']} | `{r['session_id']}` | {r['peran']} | {r['kondisi']} | {r['jumlah_frame_dipakai']} | "
                     f"{r['jumlah_frame_capture']} | {r['capture_pertama_utc'][:19]} | {r['capture_terakhir_utc'][:19]} | "
                     f"{r['sumber_timestamp']} |")
    return lines


def tidak_disalin(meta: dict) -> list[str]:
    counts: dict[tuple[str, str, str], int] = {}
    for setname, key in (("T38", "t38"), ("T43", "t43")):
        for s in meta[key]["sesi"].values():
            for item in s["tidak_disalin"]:
                alasan = item["alasan"] if isinstance(item["alasan"], str) else "; ".join(item["alasan"])
                rel = Path(item["berkas"])
                name = rel.name if len(rel.parts) == 1 else f"{rel.parts[0]}/{rel.name}"
                counts[(setname, name, alasan)] = counts.get((setname, name, alasan), 0) + 1
    for item in meta["t43"]["berkas_eksperimen"]["tidak_disalin"]:
        counts[("T43 eksperimen", item["berkas"], "; ".join(item["alasan"]))] = 1
    lines = ["| Set | Berkas | Jumlah | Alasan |", "|---|---|---:|---|"]
    for (setname, name, alasan), n in sorted(counts.items()):
        lines.append(f"| {setname} | `{name}` | {n} | {alasan} |")
    n_label = sum(s["jumlah_label_txt_tidak_disalin"] for k in ("t38", "t43") for s in meta[k]["sesi"].values())
    n_img = sum(s["jumlah_gambar_tidak_disalin"] for k in ("t38", "t43") for s in meta[k]["sesi"].values())
    lines.append(f"| T38 dan T43 | label YOLO `labels_*/*.txt` | {n_label} | label; tidak pernah disalin |")
    lines.append(f"| T38 dan T43 | gambar `*.jpg`/`*.png` di folder sesi | {n_img} | gambar; tidak pernah disalin |")
    lines.append("| T43 eksperimen | `blind_review_52/images/`, `labels_*` | - | gambar dan label tinjauan buta |")
    lines.append("| Teacher | `best.pt`, `last.pt` | 2 | bobot model |")
    return lines


def tulis_readme(ekstrak: dict, konsistensi: dict, banding: dict, meta: dict, teacher_cmp: dict) -> None:
    n_ok = sum(r["status"] == "diekstrak" for r in ekstrak["runs"])
    n_same = sum(r["jendela_runtime"]["identik"] and r["jendela_deteksi"]["identik"] for r in banding["runs"])
    tf = meta["teacher"]["folder"]
    best = {f: next((b["sha256"] for b in v["berkas"] if b["nama"] == "best.pt"), None) for f, v in tf.items()}
    teacher_rows = ["| Berkas | Robot (bait, SHA-256) | Laptop (bait, SHA-256) | Sama setelah CRLF menjadi LF |",
                    "|---|---|---|---|"]
    for name, item in teacher_cmp.items():
        teacher_rows.append(f"| `{name}` | {item['robot_bytes']} B, `{item['robot_sha256'][:12]}…` | "
                            f"{item['laptop_bytes']} B, `{item['laptop_sha256'][:12]}…` | "
                            f"{'ya' if item['sama_setelah_normalisasi'] else 'tidak'} |")
    text = [
        "# Log OP3 pelengkap (23 November 2026)",
        "",
        "Folder ini melengkapi log yang sebelumnya hanya tersimpan di komputer OP3. Isinya diambil lewat SSH dari laptop "
        "dengan package [`op3_log_pelengkap`](../ros2_packages/op3_log_pelengkap/README.md) mengikuti "
        "[prompt 23 November](../prompt/PROMPT_PELENGKAP_LOG_OP3_2026-11-23.md). Robot hanya dibaca: tidak ada kamera, "
        "ROS, servo, gait, training, inferensi, atau perekaman frame baru, dan repositori robot tidak diubah.",
        "",
        "**Batas isi:** log jendela ukur 60 detik, metadata capture, dan berkas teks training teacher. Gambar, video, label, "
        "prediksi per frame, bobot model (`*.pt`), dan log mentah penuh di luar jendela ukur tidak disalin.",
        "",
        "| Isi | Keterangan |",
        "|---|---|",
        "| [`live_24_run/`](live_24_run/) | `jendela_runtime.csv` dan `jendela_deteksi.csv` 15 run, serta "
        "[`status_ekstraksi.json`](live_24_run/status_ekstraksi.json) |",
        "| [`t38_capture/`](t38_capture/) | Metadata 11 sesi capture T38 dan 4 sesi sumber kurasi |",
        "| [`t43_capture/`](t43_capture/) | Metadata eksperimen T43 dan 8 sesi capture (`sesi/`) |",
        "| [`teacher_training/`](teacher_training/) | `manifest.json`, `args.yaml`, dan `results.csv` training teacher |",
        "| [`ringkasan_capture.csv`](ringkasan_capture.csv) | Satu baris per sesi capture |",
        "| [`status_metadata.json`](status_metadata.json) | Daftar berkas disalin dan tidak disalin beserta SHA-256 |",
        "| [`manifest_sha256.json`](manifest_sha256.json) | SHA-256 sumber dan keluaran, commit, hostname, dan waktu |",
        "| [`LAPORAN_SESI.md`](LAPORAN_SESI.md) | Laporan sesi |",
        "",
        "## Log jendela 24 run live",
        "",
        f"{n_ok} dari 15 run yang sebelumnya hanya ada di OP3 berhasil diekstrak. SHA-256 log mentah dan metadata setiap run "
        "sama dengan T36. Baris diambil bila `receive_time_utc` berada di jendela T36 (inklusif), dengan kolom dan urutan "
        "kolom log mentah dan akhir baris LF. Jumlah baris, jumlah error, rerata `end_to_end_ms`, dan FPS "
        "`(n - 1) × 1e9 / (capture_stamp_ns terakhir - pertama)` dicocokkan dengan T36 pada toleransi 1e-6. "
        f"Sebagai kontrol, 9 run yang log jendelanya sudah ada di repositori diekstrak ulang dengan skrip yang sama; "
        f"{n_same} dari 9 identik byte demi byte untuk `jendela_runtime.csv` dan `jendela_deteksi.csv`. Hasil "
        "ekstraksi ulang itu tidak disalin ke folder ini.",
        "",
        *tabel_run(ekstrak, konsistensi, banding),
        "",
        "## Sesi capture T38 dan T43",
        "",
        "Waktu capture berasal dari `captured_at_utc` di `capture_frames.jsonl`. Dua sesi T38 "
        "(`20261021_ball_moving_candidate_01` dan `20261021_negative_candidate_01`) adalah set kurasi, bukan capture asli; "
        "waktunya ditelusuri lewat `curation_manifest.json` (`source_session`, `source_image`) ke jurnal sesi sumber, yang "
        "metadatanya ikut disalin. Untuk sesi yang dipakai, rentang waktu hanya mencakup frame yang dipakai T38/T43; untuk "
        "sesi sumber dan sesi yang dikecualikan, rentang mencakup semua frame sesi. Kondisi `unknown` pada T38 berasal dari "
        "manifest capture. Hash `capture_manifest.json` kelima sesi T43 cocok dengan `capture_260_manifest.json`.",
        "",
        *tabel_capture(),
        "",
        "## Catatan training teacher",
        "",
        "Folder teacher di robot (`/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/`) memuat "
        "`manifest.json`, `args.yaml`, dan `results.csv`; tidak ada `SHA256SUMS.txt`. Ketiga berkas teks itu disalin dari "
        "robot. `best.pt` di folder tersebut dan di `.cache/hardware_models/fp32_pytorch/` tetap "
        f"`{(best[next(iter(best))] or '')[:8]}…{(best[next(iter(best))] or '')[-6:]}`. Salinan di laptop "
        "(`E:\\Kuliah\\SKRIPSI\\Sourcecode\\Progress 3\\artifacts\\checkpoints\\fp32\\`) cocok dengan hash pada prompt, "
        "tetapi memakai akhir baris CRLF; isinya identik dengan salinan robot setelah CRLF diubah menjadi LF.",
        "",
        *teacher_rows,
        "",
        "`timestamp` pada `manifest.json` (`2026-09-02T10:04:03.688292+00:00`) menurut skrip `scripts/step03_train_fp32.py` "
        "yang tersimpan (salinan robot dan laptop identik setelah normalisasi akhir baris) diisi sekali sebelum "
        "`model.train()` dengan `status: started`; saat training selesai hanya `status` yang diubah menjadi `completed`. "
        "Jadi nilai itu menandai awal training menurut skrip tersebut. Salinan skrip bertanggal 7 Oktober 2026, sesudah "
        "training, sehingga versi yang benar-benar dipakai pada 2 September tidak terverifikasi; kunci manifest sama persis "
        "dengan kunci yang ditulis skrip itu. `results.csv` memuat 100 epoch dengan `time` epoch terakhir 3385,53 detik.",
        "",
        "## Berkas yang sengaja tidak disalin",
        "",
        *tidak_disalin(meta),
        "",
        "Berkas kandidat diperiksa isinya sebelum disalin. `predictions.jsonl` ditolak karena memuat koordinat dan prediksi; "
        "`prelabel_manifest.json` dan `review_log.jsonl` tidak disalin karena berada di folder label.",
        "",
    ]
    (FOLDER / "README.md").write_text("\n".join(text), encoding="utf-8")


def tulis_manifest(ekstrak: dict, konsistensi: dict, banding: dict, meta: dict, teacher_cmp: dict,
                   robot_tmp: str) -> None:
    sumber = {}
    for r in ekstrak["runs"]:
        for key, item in r["sumber"].items():
            sumber[f"OP3:{item['path']}"] = item["sha256"]
    for key in ("t38", "t43"):
        for s in meta[key]["sesi"].values():
            for f in s["disalin"]:
                sumber[f"OP3:{f['sumber']}"] = f["sha256"]
    for f in meta["t43"]["berkas_eksperimen"]["disalin"] + meta["teacher"]["disalin"]:
        sumber[f"OP3:{f['sumber']}"] = f["sha256"]
    sumber[f"OP3:{meta['t38']['input_manifest']['path']}"] = meta["t38"]["input_manifest"]["sha256"]
    for folder, entry in meta["teacher"]["folder"].items():
        for b in entry["berkas"]:
            sumber[f"OP3:{folder}/{b['nama']}"] = b["sha256"]
    for name, item in teacher_cmp.items():
        sumber[f"laptop:{item['laptop_path']}"] = item["laptop_sha256"]
    keluaran = {str(p.relative_to(FOLDER)).replace("\\", "/"): sha256(p)
                for p in sorted(FOLDER.rglob("*")) if p.is_file() and p.name not in ("manifest_sha256.json", "LAPORAN_SESI.md")}
    manifest = {
        "dibuat_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "commit_repositori_laptop": git("rev-parse", "HEAD"),
        "hostname_robot": ekstrak["hostname"],
        "direktori_kerja_sementara_robot": robot_tmp,
        "waktu_ekstraksi_robot_utc": ekstrak["dibuat_utc"],
        "waktu_metadata_robot_utc": meta["dibuat_utc"],
        "skrip_package_sha256": {p.name: sha256(p) for p in sorted(PACKAGE.glob("*.py"))},
        "skrip_dijalankan_di_robot_sha256": {"ekstrak_jendela.py": ekstrak["skrip_sha256"],
                                            "salin_metadata.py": meta["skrip_sha256"]},
        "konsistensi_9_run": {"skrip_sha256": konsistensi["skrip_sha256"],
                              "hasil": [{"run_id": r["run_id"],
                                         "jendela_runtime": r["jendela_runtime"], "jendela_deteksi": r["jendela_deteksi"]}
                                        for r in banding["runs"]]},
        "sumber_sha256": dict(sorted(sumber.items())),
        "keluaran_sha256": keluaran,
        "catatan": "LAPORAN_SESI.md dan berkas ini tidak dicantumkan di keluaran_sha256 karena ditulis paling akhir.",
    }
    (FOLDER / "manifest_sha256.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--konsistensi-status", type=Path, required=True)
    parser.add_argument("--konsistensi-banding", type=Path, required=True)
    parser.add_argument("--teacher-laptop", type=Path, required=True)
    parser.add_argument("--robot-tmp", required=True)
    args = parser.parse_args()
    ekstrak = json.loads((FOLDER / "live_24_run/status_ekstraksi.json").read_text(encoding="utf-8"))
    meta = json.loads((FOLDER / "status_metadata.json").read_text(encoding="utf-8"))
    konsistensi = json.loads(args.konsistensi_status.read_text(encoding="utf-8"))
    banding = json.loads(args.konsistensi_banding.read_text(encoding="utf-8"))
    teacher_cmp = {}
    for name in ("manifest.json", "args.yaml", "results.csv"):
        robot = (FOLDER / "teacher_training" / name).read_bytes()
        laptop_path = args.teacher_laptop / name
        laptop = laptop_path.read_bytes()
        teacher_cmp[name] = {"robot_bytes": len(robot), "robot_sha256": hashlib.sha256(robot).hexdigest(),
                             "laptop_path": str(laptop_path), "laptop_bytes": len(laptop),
                             "laptop_sha256": hashlib.sha256(laptop).hexdigest(),
                             "sama_setelah_normalisasi": laptop.replace(b"\r\n", b"\n") == robot}
    tulis_readme(ekstrak, konsistensi, banding, meta, teacher_cmp)
    tulis_manifest(ekstrak, konsistensi, banding, meta, teacher_cmp, args.robot_tmp)
    print("README.md dan manifest_sha256.json ditulis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
