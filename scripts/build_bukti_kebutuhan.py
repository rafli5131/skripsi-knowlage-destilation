#!/usr/bin/env python3
"""Kumpulkan bukti uji kebutuhan fungsional (KF) dan nonfungsional (KNF).

Skrip ini hanya membaca berkas yang sudah ada di repositori, lalu menulis folder
``bukti_kebutuhan/``: tabel bukti per kebutuhan, salinan gambar pendukung,
README per kebutuhan, tabel kasus uji, dan manifest SHA-256. Tidak ada
eksperimen baru, tidak ada akses robot, dan berkas sumber tidak diubah.

Kriteria kelulusan ditulis retrospektif (D18) dari indikator Bab 4; README
menyatakan hal ini secara terbuka.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "bukti_kebutuhan"

T36 = ROOT / "analisis_performa/tabel/T36_runtime_live_setara_per_run.csv"
T45_MANIFEST = ROOT / "runs/op3_single_path_eval/20261116_runtime_01/runtime_stages_manifest.json"
P27 = ROOT / "dokumentasi/2026-10-23/percobaan-27-uji-ulang-kd-hybrid/03-tracking"
DETECTOR = ROOT / "scripts/op3_pytorch_detector.py"
RUN_ROOTS = [ROOT / "dokumentasi/2026-11-02", ROOT / "dokumentasi/2026-11-03"]

MODEL_LABEL = {
    "teacher": "Teacher YOLO11n",
    "hybrid1337": "KD Hybrid seed 1337",
    "sup1337": "Supervised seed 1337",
    "kd42": "KD murni seed 42",
}
KONDISI = {"idle": "diam", "walk": "berjalan"}
CLASSES = ("ball", "gawang", "robot")
RUNTIME_COLUMNS = [
    "run_id", "condition", "frame_index", "capture_stamp_ns", "receive_time_utc",
    "width", "height", "preprocess_ms", "inference_ms", "postprocess_ms",
    "end_to_end_ms", "fps_running", "process_cpu_percent", "process_rss_bytes",
    "detection_count", "tracked_count", "n_ball", "n_gawang", "n_robot", "error",
    "is_warmup", "effective_fps_after_warmup",
]
# Kolom yang wajib terisi pada baris tanpa error menurut indikator KF-04.
KF04_REQUIRED = [
    "capture_stamp_ns", "receive_time_utc", "preprocess_ms", "inference_ms",
    "postprocess_ms", "end_to_end_ms", "process_cpu_percent", "process_rss_bytes",
]
KNF01_MIN_FPS = 8.0

COPIES = {
    "KF-02_deteksi_tiga_kelas": [
        ("dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/02-kd-hybrid/idle-u1/frame_deteksi_sesudah_jendela.png",
         "contoh_keluaran_hybrid_diam_u1.png"),
        ("dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/02-kd-hybrid/idle-u1/grafik_keluaran_kelas_id.png",
         "grafik_keluaran_kelas_hybrid_diam_u1.png"),
    ],
    "KF-03_id_pelacakan": [
        ("dokumentasi/2026-10-23/percobaan-27-uji-ulang-kd-hybrid/03-tracking/grafik_lintasan_bola_id.png",
         "grafik_lintasan_bola_id2.png"),
        ("dokumentasi/2026-10-23/percobaan-27-uji-ulang-kd-hybrid/03-tracking/grafik_id_track_bola_id.png",
         "grafik_id_track_bola.png"),
    ],
    "KF-05_preview": [
        ("dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/02-kd-hybrid/idle-u1/preview_sebelum_run.png",
         "preview_hybrid_diam_u1_sebelum_run.png"),
        ("dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/teacher_berjalan_u1_sesudah.png",
         "preview_teacher_berjalan.png"),
        ("dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/hybrid_berjalan_u3_sesudah.png",
         "preview_hybrid_berjalan.png"),
        ("dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/supervised_berjalan_u1_sesudah.png",
         "preview_supervised_berjalan.png"),
        ("dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/kd_murni_berjalan_u3_sesudah.png",
         "preview_kd_murni_berjalan.png"),
    ],
    "KNF-01_laju_pemrosesan": [
        ("dokumentasi/model/gabungan/garis_runtime_op3_empat_model_id.png",
         "garis_runtime_op3_empat_model_id.png"),
    ],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def ribuan(value: int) -> str:
    return f"{value:,}".replace(",", ".")


class Writer:
    """Menulis berkas LF dan mencatat hash keluaran serta sumber."""

    def __init__(self, out: Path):
        self.out = out
        self.outputs: dict[str, dict] = {}
        self.sources: dict[str, str] = {}

    def source(self, path: Path) -> Path:
        self.sources[rel(path)] = sha256_file(path)
        return path

    def text(self, name: str, content: str) -> None:
        path = self.out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode("utf-8")
        path.write_bytes(data)
        self.outputs[name] = {"sha256": sha256_bytes(data), "jenis": "dibangkitkan"}

    def table(self, name: str, header: list[str], rows: list[list]) -> None:
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
        self.text(name, buffer.getvalue())

    def copy(self, source: str, name: str) -> None:
        src = ROOT / source
        dst = self.out / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        digest = sha256_file(dst)
        if digest != sha256_file(src):
            raise RuntimeError(f"salinan tidak identik: {source}")
        self.outputs[name] = {"sha256": digest, "jenis": "salinan", "sumber": source}


def load_runs(w: Writer) -> list[dict]:
    runs = list(csv.DictReader(w.source(T36).open(encoding="utf-8")))
    folders: dict[str, Path] = {}
    for base in RUN_ROOTS:
        for summary in sorted(base.rglob("summary_metrics.json")):
            if "arsip" in summary.as_posix():
                continue
            run_id = json.loads(summary.read_text(encoding="utf-8")).get("run_id")
            folders.setdefault(run_id, summary.parent)
    for run in runs:
        folder = folders.get(run["run_id"])
        if folder is None:
            raise FileNotFoundError(f"folder dokumentasi untuk {run['run_id']} tidak ditemukan")
        run["folder"] = folder
        run["summary"] = json.loads(w.source(folder / "summary_metrics.json").read_text(encoding="utf-8"))
        table = list(csv.reader(w.source(folder / "tabel_deteksi.csv").open(encoding="utf-8")))
        run["kelas"] = {row[0]: row for row in table[1:]}
    if len(runs) != 24:
        raise ValueError(f"T36 seharusnya memuat 24 run, ditemukan {len(runs)}")
    return runs


def run_label(run: dict) -> list[str]:
    return [MODEL_LABEL[run["model"]], KONDISI[run["condition"]], run["ulangan"], run["run_id"]]


def build_kf01(w: Writer, runs: list[dict]) -> dict:
    rows, ok = [], 0
    for run in runs:
        frames_t36, err_t36 = int(run["frames"]), int(run["error_frames"])
        frames_sum, err_sum = int(run["summary"]["frames_window"]), int(run["summary"]["error_frames"])
        lulus = frames_t36 > 0 and err_t36 == 0 and frames_t36 == frames_sum and err_t36 == err_sum
        ok += lulus
        rows.append(run_label(run) + [frames_t36, err_t36, frames_sum, err_sum,
                                      rel(run["folder"] / "summary_metrics.json"),
                                      "lulus" if lulus else "tidak lulus"])
    w.table("KF-01_menerima_citra/bukti_frame_dan_error_24_run.csv",
            ["model", "kondisi", "ulangan", "run_id", "frame_T36", "error_frame_T36",
             "frame_ringkasan_run", "error_frame_ringkasan_run", "sumber_ringkasan_run", "status"], rows)
    total = sum(int(r["frames"]) for r in runs)
    return {"lulus": ok, "n": len(runs), "frame_total": total}


def build_kf02(w: Writer, runs: list[dict]) -> dict:
    rows, ok = [], 0
    min_cov = {c: 100.0 for c in CLASSES}
    for run in runs:
        present = all(c in run["kelas"] and int(run["kelas"][c][1]) > 0 for c in CLASSES)
        ok += present
        cells = []
        for c in CLASSES:
            row = run["kelas"].get(c)
            cov = float(row[3]) if row else 0.0
            min_cov[c] = min(min_cov[c], cov)
            cells += [row[1] if row else 0, round(cov, 2), round(float(row[4]), 4) if row else ""]
        rows.append(run_label(run) + [run["frames"]] + cells
                    + [rel(run["folder"] / "tabel_deteksi.csv"), "lulus" if present else "tidak lulus"])
    header = ["model", "kondisi", "ulangan", "run_id", "frame_jendela"]
    for c in CLASSES:
        header += [f"frame_ada_{c}", f"cakupan_persen_{c}", f"confidence_median_{c}"]
    header += ["sumber", "status"]
    w.table("KF-02_deteksi_tiga_kelas/bukti_cakupan_kelas_24_run.csv", header, rows)
    return {"lulus": ok, "n": len(runs), "min_cov": min_cov}


def build_kf03(w: Writer) -> dict:
    detections = list(csv.DictReader(w.source(P27 / "jendela_deteksi.csv").open(encoding="utf-8")))
    runtime = list(csv.DictReader(w.source(P27 / "jendela_runtime.csv").open(encoding="utf-8")))
    summary = json.loads(w.source(P27 / "summary_metrics.json").read_text(encoding="utf-8"))
    frames = [r["frame_index"] for r in runtime]
    by_frame: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for det in detections:
        by_frame[det["frame_index"]][det["class_name"]].append(det)
    ball_ids = Counter(d["track_id"] for d in detections if d["class_name"] == "ball")
    main_id = ball_ids.most_common(1)[0][0]
    rows = []
    centers = []
    for frame in frames:
        balls = by_frame[frame]["ball"]
        ids = sorted({b["track_id"] for b in balls}, key=lambda x: int(x) if x.isdigit() else -1)
        main = [b for b in balls if b["track_id"] == main_id]
        if main:
            b = main[0]
            cx = (float(b["x1_px"]) + float(b["x2_px"])) / 2
            cy = (float(b["y1_px"]) + float(b["y2_px"])) / 2
            centers.append((cx, cy))
            rows.append([frame, len(balls), " ".join(ids), 1, round(cx, 2), round(cy, 2)])
        else:
            rows.append([frame, len(balls), " ".join(ids), 0, "", ""])
    w.table("KF-03_id_pelacakan/bukti_id_bola_per_frame.csv",
            ["frame_index", "jumlah_kotak_bola", "id_bola_pada_frame", f"id_utama_{main_id}_ada",
             "pusat_x_id_utama_px", "pusat_y_id_utama_px"], rows)
    present = sum(r[3] for r in rows)
    extra = sum(1 for r in rows if r[1] > 1)
    xs, ys = [c[0] for c in centers], [c[1] for c in centers]
    result = {
        "run_id": summary["run_id"], "frames": len(frames), "main_id": main_id, "present": present,
        "extra_frames": extra, "ids": dict(ball_ids), "x_span": max(xs) - min(xs),
        "y_span": max(ys) - min(ys), "errors": sum(1 for r in runtime if r.get("error")),
        "checkpoint": summary["checkpoint_sha256"], "condition": summary["condition"],
        "fps": summary["effective_fps"],
        "robot_ids": summary["class_outputs"]["robot"]["track_id_counts"],
    }
    if abs(result["x_span"] - summary["ball_tracking"]["track_2_x_span_px"]) > 1e-6:
        raise ValueError("rentang X ID utama tidak cocok dengan summary_metrics.json percobaan 27")
    return result


def build_kf04(w: Writer, runs: list[dict]) -> dict:
    rows, ok_files = [], 0
    for run in runs:
        path = run["folder"] / "jendela_runtime.csv"
        if not path.exists():
            continue
        data = list(csv.DictReader(w.source(path).open(encoding="utf-8")))
        header = list(data[0].keys()) if data else []
        missing_cols = [c for c in RUNTIME_COLUMNS if c not in header]
        clean = [r for r in data if not r["error"]]
        empty = sum(1 for r in clean for c in KF04_REQUIRED if r.get(c, "") == "")
        lulus = not missing_cols and empty == 0 and len(data) == int(run["frames"])
        ok_files += lulus
        rows.append(run_label(run) + [len(data), run["frames"], len(header),
                                      " ".join(missing_cols) or "-", empty, rel(path),
                                      "lulus" if lulus else "tidak lulus"])
    w.table("KF-04_log_runtime/bukti_kolom_log_jendela_repo.csv",
            ["model", "kondisi", "ulangan", "run_id", "baris_jendela", "frame_T36", "jumlah_kolom",
             "kolom_hilang", "sel_wajib_kosong", "sumber", "status"], rows)
    manifest = json.loads(w.source(T45_MANIFEST).read_text(encoding="utf-8"))
    raw_rows, ok_raw = [], 0
    by_id = {r["run_id"]: r for r in runs}
    for run_id, info in sorted(manifest["sources"].items()):
        run = by_id[run_id]
        same_hash = info["raw_csv_sha256"] == run["raw_csv_sha256"]
        match = bool(info["e2e_mean_match_t36"]) and same_hash and int(info["frames"]) == int(run["frames"])
        ok_raw += match
        raw_rows.append(run_label(run) + [info["frames"], info["raw_csv_sha256"], same_hash,
                                          info["e2e_mean_match_t36"], "lulus" if match else "tidak lulus"])
    w.table("KF-04_log_runtime/bukti_log_mentah_24_run_T45.csv",
            ["model", "kondisi", "ulangan", "run_id", "frame", "sha256_csv_mentah",
             "hash_sama_dengan_T36", "rerata_end_to_end_cocok_T36", "status"], raw_rows)
    return {"files": len(rows), "ok_files": ok_files, "raw": len(raw_rows), "ok_raw": ok_raw}


def build_knf01(w: Writer, runs: list[dict]) -> dict:
    rows, ok = [], 0
    for run in runs:
        fps = float(run["fps"])
        lulus = fps >= KNF01_MIN_FPS
        ok += lulus
        rows.append(run_label(run) + [run["frames"], round(fps, 4), round(float(run["latency_mean_ms"]), 2),
                                      KNF01_MIN_FPS, "lulus" if lulus else "tidak lulus"])
    w.table("KNF-01_laju_pemrosesan/bukti_fps_24_run.csv",
            ["model", "kondisi", "ulangan", "run_id", "frame", "fps_efektif", "latensi_rerata_ms",
             "batas_minimum_fps", "status"], rows)
    lowest = min(runs, key=lambda r: float(r["fps"]))
    by_model = defaultdict(list)
    for run in runs:
        by_model[run["model"]].append(float(run["fps"]))
    return {"lulus": ok, "n": len(runs), "min": float(lowest["fps"]), "min_run": lowest,
            "by_model": {k: (min(v), max(v)) for k, v in by_model.items()}}


def readmes(w: Writer, kf01, kf02, kf03, kf04, knf01, commit: str) -> list[list]:
    cases = [
        ["UJ-KF-01", "KF-01", "Menerima citra kamera OP3",
         "Node detektor dijalankan pada topik kamera /thesis/image_raw selama jendela ukur 60 detik per run, 24 run (4 model x 2 kondisi x 3 ulangan).",
         "Citra kamera 640 x 480 dari ROS 2",
         "Setiap run memproses frame (>0) dan error frame = 0; jumlah frame dan error pada T36 sama dengan ringkasan run.",
         f"{kf01['lulus']}/{kf01['n']} run memenuhi; {ribuan(kf01['frame_total'])} frame terproses tanpa error.",
         "Lulus" if kf01["lulus"] == kf01["n"] else "Tidak lulus", "KF-01_menerima_citra/"],
        ["UJ-KF-02", "KF-02", "Mendeteksi bola, gawang, dan robot",
         "Bola, gawang, dan robot ditata di depan kamera; keluaran deteksi dicatat per frame pada 24 run.",
         "Adegan berisi tiga kelas objek",
         "Ketiga kelas muncul sebagai kotak berlabel kelas pada setiap run.",
         f"{kf02['lulus']}/{kf02['n']} run memuat ketiga kelas; cakupan frame terendah bola {fmt(kf02['min_cov']['ball'], 1)}%, gawang {fmt(kf02['min_cov']['gawang'], 1)}%, robot {fmt(kf02['min_cov']['robot'], 1)}%.",
         "Lulus" if kf02["lulus"] == kf02["n"] else "Tidak lulus", "KF-02_deteksi_tiga_kelas/"],
        ["UJ-KF-03", "KF-03", "Menyediakan ID pelacakan pada mode tambahan",
         "Mode pelacakan BoT-SORT aktif; bola dipindahkan di depan kamera selama sekitar 30 detik (percobaan 27, KD Hybrid seed 1337).",
         "Bola bergerak, gawang dan robot diam",
         "Bola utama memiliki ID dan ID yang sama tetap muncul pada setiap frame jendela selama bola bergerak.",
         f"ID {kf03['main_id']} muncul pada {kf03['present']}/{kf03['frames']} frame; pusat bergeser {fmt(kf03['x_span'], 1)} px (X) dan {fmt(kf03['y_span'], 1)} px (Y). Kotak bola tambahan dengan ID lain muncul pada {kf03['extra_frames']} frame.",
         "Lulus dengan catatan", "KF-03_id_pelacakan/"],
        ["UJ-KF-04", "KF-04", "Mencatat runtime per frame",
         "Log CSV per frame dibuat node selama 24 run lalu diperiksa kolom dan kecocokannya dengan T36.",
         "Frame kamera yang diproses",
         "Setiap baris memuat timestamp, durasi tahap, CPU, RSS, dan kolom error; log mentah cocok dengan T36.",
         f"{kf04['ok_files']}/{kf04['files']} log jendela di repositori lengkap; {kf04['ok_raw']}/{kf04['raw']} log mentah di OP3 cocok dengan T36 (pemeriksaan T45).",
         "Lulus" if kf04["ok_files"] == kf04["files"] and kf04["ok_raw"] == kf04["raw"] else "Tidak lulus",
         "KF-04_log_runtime/"],
        ["UJ-KF-05", "KF-05", "Menampilkan preview deteksi",
         "Preview beranotasi diterbitkan pada /vision/debug_image dan ditampilkan melalui SSH-X; tangkapan layar diambil sebelum dan sesudah run.",
         "Hasil deteksi pada frame kamera",
         "Kotak, nama kelas, confidence, dan ID tampak pada preview.",
         "Enam tangkapan dari empat model menampilkan kotak, kelas, confidence, dan ID.",
         "Lulus untuk contoh yang tersedia", "KF-05_preview/"],
        ["UJ-KNF-01", "KNF-01", "Laju pemrosesan",
         "FPS efektif dihitung dari timestamp kamera pada jendela 60 detik tiap run.",
         "24 run live",
         f"FPS efektif rata-rata tiap run >= {fmt(KNF01_MIN_FPS, 0)} FPS pada kondisi diam dan berjalan.",
         f"{knf01['lulus']}/{knf01['n']} run memenuhi; terendah {fmt(knf01['min'], 2)} FPS ({MODEL_LABEL[knf01['min_run']['model']]}, {KONDISI[knf01['min_run']['condition']]}, ulangan {knf01['min_run']['ulangan']}).",
         "Lulus" if knf01["lulus"] == knf01["n"] else "Tidak lulus", "KNF-01_laju_pemrosesan/"],
    ]
    header = ["id_uji", "kebutuhan", "nama", "prosedur", "masukan", "hasil_diharapkan",
              "hasil_aktual", "status", "folder_bukti"]
    w.table("kasus_uji_kf_knf.csv", header, cases)

    table = "\n".join(
        f"| {c[0]} | {c[1]} {c[2]} | {c[5]} | {c[6]} | {c[7]} | [{c[8]}]({c[8]}README.md) |" for c in cases)
    w.text("README.md", f"""# Bukti uji kebutuhan fungsional dan nonfungsional

Folder ini mengumpulkan bukti untuk kebutuhan KF-01 sampai KF-05 dan KNF-01 pada
[Bab 4](../laporan/draf-7-bab/BAB_4_REKAYASA_KEBUTUHAN.md) serta hasil uji pada
[Bab 6](../laporan/draf-7-bab/BAB_6_PENGUJIAN_DAN_PEMBAHASAN.md). Pengujian memakai
pendekatan kotak hitam: sistem dinilai dari masukan dan keluarannya, bukan dari struktur
kode di dalamnya (Khan dan Khan, 2012; Nidhra dan Dondeti, 2012). KNF-01 dirumuskan
sebagai kebutuhan kinerja, yaitu salah satu jenis kebutuhan nonfungsional (Glinz, 2007).

Semua bukti berasal dari pengukuran yang sudah dilakukan. Tidak ada uji baru untuk folder
ini. Daftar kebutuhan dan pengujian retrospektif dari log disetujui pembimbing secara lisan
pada 12 November 2026 (D18 di [`docs/DECISIONS.md`](../docs/DECISIONS.md)). Kriteria lulus
pada tabel di bawah dirumuskan dari indikator Bab 4 sesudah data tersedia, sehingga
penilaiannya bersifat retrospektif.

## Ringkasan kasus uji

| ID uji | Kebutuhan | Hasil yang diharapkan | Hasil aktual | Status | Bukti |
|---|---|---|---|---|---|
{table}

Tabel lengkap dengan kolom prosedur dan masukan: [`kasus_uji_kf_knf.csv`](kasus_uji_kf_knf.csv).

## Isi folder

| Folder | Isi |
|---|---|
| `KF-01_menerima_citra/` | Jumlah frame dan error frame 24 run dari T36, dicocokkan dengan ringkasan tiap run |
| `KF-02_deteksi_tiga_kelas/` | Cakupan frame dan confidence median tiap kelas untuk 24 run, contoh keluaran |
| `KF-03_id_pelacakan/` | ID bola per frame pada sesi bola bergerak, grafik lintasan dan ID |
| `KF-04_log_runtime/` | Pemeriksaan kolom log jendela di repositori dan kecocokan 24 log mentah dengan T36 |
| `KF-05_preview/` | Tangkapan preview beranotasi dari empat model |
| `KNF-01_laju_pemrosesan/` | FPS efektif 24 run terhadap batas 8 FPS, grafik runtime |

Setiap folder memuat README dengan prosedur, hasil, sumber, dan batas tafsir.
[`manifest_bukti_sha256.json`](manifest_bukti_sha256.json) mencatat SHA-256 setiap berkas
di folder ini dan setiap berkas sumber yang dibaca. Gambar adalah salinan identik dari
dokumentasi percobaan; sumber aslinya tidak diubah.

## Batas bukti

- Lulus berarti kebutuhan terpenuhi pada run dan contoh yang diperiksa, bukan jaminan pada
  semua kondisi.
- KF-02 hanya menilai bahwa keluaran berisi kelas dan kotak. Ketepatan deteksi terhadap label
  acuan dinilai pada RM2 dan RM3 (TEST, T38, T43, T44).
- KF-03 diuji pada satu sesi bola bergerak berdurasi sekitar 30 detik. Pelacakan bukan tujuan
  wajib penelitian.
- Log mentah 24 run, frame, dan label tetap tersimpan lokal di OP3. Folder ini hanya memuat
  ringkasan dan hash.

## Membangkitkan ulang

```bash
python3 scripts/build_bukti_kebutuhan.py --replace
```

Dibangkitkan dari commit `{commit[:12]}`.
""")

    w.text("KF-01_menerima_citra/README.md", f"""# KF-01 Menerima citra kamera OP3

**Kebutuhan:** sistem menerima citra dari kamera OP3 melalui ROS 2 dan memproses setiap
frame yang masuk; kesalahan pemrosesan frame dicatat.

**Implementasi:** node `scripts/op3_pytorch_detector.py` berlangganan ke topik
`/thesis/image_raw` (parameter `input_topic`). Frame yang gagal diproses dicatat pada kolom
`error` dan dihitung sebagai `frame_errors`, sementara node tetap berjalan.

**Prosedur:** 24 run live (4 model x diam/berjalan x 3 ulangan), jendela ukur 60 detik setelah
30 frame pemanasan. Jumlah frame dan error frame dibaca dari
[T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md) lalu dicocokkan dengan
`summary_metrics.json` setiap run.

**Kriteria lulus:** frame terproses lebih dari nol, error frame sama dengan nol, dan angka T36
sama dengan ringkasan run.

**Hasil:** {kf01['lulus']}/{kf01['n']} run lulus. Total {ribuan(kf01['frame_total'])} frame terproses
tanpa error. Rincian: [`bukti_frame_dan_error_24_run.csv`](bukti_frame_dan_error_24_run.csv).

**Batas:** bukti ini menunjukkan frame yang sampai ke node diproses tanpa kesalahan. Frame yang
mungkin hilang sebelum sampai ke node tidak dihitung; jeda penerimaan maksimum tercatat pada
kolom `max_receive_gap_s` T36.
""")

    w.text("KF-02_deteksi_tiga_kelas/README.md", f"""# KF-02 Mendeteksi bola, gawang, dan robot

**Kebutuhan:** keluaran sistem memuat kelas `ball`, `gawang`, dan `robot` beserta kotak
pembatasnya.

**Implementasi:** hasil deteksi diterbitkan sebagai `vision_msgs/Detection2DArray` pada
`/vision/detections` dan dicatat per kotak pada log deteksi.

**Prosedur:** ketiga objek ditata di depan robot. Untuk setiap run dihitung jumlah frame yang
memuat tiap kelas pada confidence > 0,25 dan NMS IoU 0,45 (sumber: `tabel_deteksi.csv`
setiap run).

**Kriteria lulus:** ketiga kelas muncul sebagai kotak berlabel pada setiap run.

**Hasil:** {kf02['lulus']}/{kf02['n']} run lulus. Cakupan frame terendah: bola
{fmt(kf02['min_cov']['ball'], 1)}%, gawang {fmt(kf02['min_cov']['gawang'], 1)}%, robot
{fmt(kf02['min_cov']['robot'], 1)}%. Rincian:
[`bukti_cakupan_kelas_24_run.csv`](bukti_cakupan_kelas_24_run.csv).

![Contoh keluaran KD Hybrid saat diam](contoh_keluaran_hybrid_diam_u1.png)

**Batas:** kemunculan kotak tidak sama dengan deteksi yang benar. Ketepatan terhadap label acuan
dinilai pada TEST (T05/T30), T38, T43, dan T44. Adegan ini sama untuk semua run, sehingga cakupan
tinggi di sini tidak menggambarkan kinerja pada adegan lain.
""")

    ids_text = ", ".join(f"ID {k}: {v} kotak" for k, v in sorted(kf03["ids"].items(), key=lambda x: int(x[0])))
    robot_ids = ", ".join(f"ID {k}" for k in kf03["robot_ids"])
    w.text("KF-03_id_pelacakan/README.md", f"""# KF-03 Menyediakan ID pelacakan pada mode tambahan

**Kebutuhan:** pada mode pelacakan, setiap objek memperoleh ID dan ID tersebut dipertahankan
ketika objek bergerak. Kebutuhan ini merupakan kemampuan tambahan, bukan tujuan wajib penelitian.

**Implementasi:** bila `enable_tracking` aktif, node memanggil `model.track` dengan konfigurasi
BoT-SORT (`botsort.yaml`, `persist=True`). ID dicatat pada kolom `track_id` log deteksi.

**Prosedur:** sesi `{kf03['run_id']}` (percobaan 27) dengan KD Hybrid seed 1337
(SHA-256 `{kf03['checkpoint'][:12]}...`). Bola dipindahkan di depan kamera selama jendela
{kf03['frames']} frame ({fmt(kf03['fps'], 2)} FPS), sedangkan gawang dan robot diam. Kondisi
fisik robot tercatat `{kf03['condition']}`. Sumber:
[dokumentasi percobaan 27](../../dokumentasi/2026-10-23/percobaan-27-uji-ulang-kd-hybrid/03-tracking/README_ID.md).

**Kriteria lulus:** bola utama memiliki ID, dan ID yang sama muncul pada setiap frame jendela
selama bola bergerak.

**Hasil:** ID {kf03['main_id']} muncul pada {kf03['present']}/{kf03['frames']} frame. Pusat kotak
ID tersebut bergeser {fmt(kf03['x_span'], 1)} px pada sumbu X dan {fmt(kf03['y_span'], 1)} px pada
sumbu Y, sehingga bola memang berpindah dan ID tidak berganti. Robot memakai {robot_ids} pada
seluruh frame. Error frame: {kf03['errors']}. Rincian per frame:
[`bukti_id_bola_per_frame.csv`](bukti_id_bola_per_frame.csv).

**Catatan:** pada {kf03['extra_frames']} frame muncul kotak bola kedua dengan ID lain
({ids_text}). Kotak tambahan ini tidak menggantikan ID utama, tetapi menunjukkan adanya kotak
ganda atau deteksi palsu sesaat. Gawang memakai dua ID selama sesi (lihat dokumentasi sumber).

![Lintasan pusat bola ID utama](grafik_lintasan_bola_id2.png)

![ID utama dan kotak tambahan](grafik_id_track_bola.png)

**Batas:** satu sesi sekitar 30 detik dengan satu model dan satu objek bergerak. Tidak ada label
acuan identitas, sehingga hasil ini tidak mengukur metrik pelacakan seperti MOTA atau IDF1.
""")

    w.text("KF-04_log_runtime/README.md", f"""# KF-04 Mencatat runtime per frame

**Kebutuhan:** setiap frame yang diproses dicatat beserta timestamp, durasi tahap pemrosesan,
penggunaan CPU, RSS, dan status error.

**Implementasi:** node menulis CSV per frame dengan {len(RUNTIME_COLUMNS)} kolom, antara lain
`capture_stamp_ns`, `receive_time_utc`, `preprocess_ms`, `inference_ms`, `postprocess_ms`,
`end_to_end_ms`, `process_cpu_percent`, `process_rss_bytes`, dan `error`.

**Prosedur:**

1. Memeriksa {kf04['files']} log jendela (`jendela_runtime.csv`) yang tersimpan di repositori:
   kelengkapan kolom, sel wajib yang kosong pada baris tanpa error, dan kecocokan jumlah baris
   dengan T36.
2. Untuk 24 run, log mentah di OP3 dibaca ulang pada percobaan 41 (T45); rerata `end_to_end_ms`
   tiap run cocok dengan T36 pada toleransi 1e-6 dan hash CSV mentahnya sama dengan yang tercatat
   di T36.

**Kriteria lulus:** semua kolom tersedia, sel wajib terisi, dan log mentah cocok dengan T36.

**Hasil:** {kf04['ok_files']}/{kf04['files']} log jendela lengkap
([`bukti_kolom_log_jendela_repo.csv`](bukti_kolom_log_jendela_repo.csv)).
{kf04['ok_raw']}/{kf04['raw']} log mentah cocok dengan T36
([`bukti_log_mentah_24_run_T45.csv`](bukti_log_mentah_24_run_T45.csv),
[T45](../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md)).

**Batas:** log jendela {24 - kf04['files']} run lain (supervised, KD murni, dan Hybrid berjalan) tidak
disimpan di repositori. Untuk run tersebut, bukti berupa hash dan kecocokan rerata yang dihitung dari log
mentah di OP3.
""")

    w.text("KF-05_preview/README.md", """# KF-05 Menampilkan preview deteksi

**Kebutuhan:** sistem menampilkan citra beranotasi berisi kotak dan kelas hasil deteksi.

**Implementasi:** bila `publish_debug_image` aktif, node menggambar hasil dengan
`result.plot()` dan menerbitkannya pada `/vision/debug_image`. Preview ditampilkan melalui SSH-X.

**Prosedur:** tangkapan preview diambil sebelum run dan sesudah jendela ukur pada beberapa run
dari keempat model. Pemeriksaan dilakukan secara visual.

**Kriteria lulus:** kotak, nama kelas, confidence, dan ID tampak pada preview.

**Hasil:** keenam tangkapan menampilkan kotak, nama kelas, confidence, dan ID untuk bola,
gawang, dan robot.

| Berkas | Model dan kondisi |
|---|---|
| `preview_hybrid_diam_u1_sebelum_run.png` | KD Hybrid seed 1337, diam, sebelum run |
| `preview_teacher_berjalan.png` | Teacher, berjalan, sesudah jendela |
| `preview_hybrid_berjalan.png` | KD Hybrid seed 1337, berjalan, sesudah jendela |
| `preview_supervised_berjalan.png` | Supervised seed 1337, berjalan, sesudah jendela |
| `preview_kd_murni_berjalan.png` | KD murni seed 42, berjalan, sesudah jendela |
| `../KF-02_deteksi_tiga_kelas/contoh_keluaran_hybrid_diam_u1.png` | KD Hybrid seed 1337, diam, sesudah jendela |

![Preview KD Hybrid saat berjalan](preview_hybrid_berjalan.png)

Cuplikan video 10 detik (supervised, percobaan 22) tersedia di
[`dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/`](../../dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/media/manifest_media.json).

**Batas:** tangkapan tunggal tidak membuktikan preview bebas macet sepanjang setiap run.
Tangkapan sesudah jendela pada kondisi berjalan juga tidak membuktikan robot sedang melangkah
pada gambar tersebut.
""")

    lines = "\n".join(
        f"| {MODEL_LABEL[k]} | {fmt(v[0], 2)} | {fmt(v[1], 2)} |" for k, v in knf01["by_model"].items())
    low = knf01["min_run"]
    w.text("KNF-01_laju_pemrosesan/README.md", f"""# KNF-01 Laju pemrosesan

**Kebutuhan:** FPS efektif rata-rata setiap run minimal {fmt(KNF01_MIN_FPS, 0)} FPS pada kondisi
diam dan berjalan. KNF-01 adalah kebutuhan kinerja (Glinz, 2007).

**Prosedur:** FPS efektif dihitung sebagai (jumlah frame - 1) dibagi selang timestamp kamera
antara frame pertama dan terakhir pada jendela 60 detik. Nilai per run diambil dari
[T36](../../analisis_performa/tabel/T36_runtime_live_setara_per_run.md).

**Kriteria lulus:** FPS efektif setiap run >= {fmt(KNF01_MIN_FPS, 0)}.

**Hasil:** {knf01['lulus']}/{knf01['n']} run lulus. Nilai terendah {fmt(knf01['min'], 2)} FPS pada
{MODEL_LABEL[low['model']]}, kondisi {KONDISI[low['condition']]}, ulangan {low['ulangan']}
(`{low['run_id']}`). Rincian: [`bukti_fps_24_run.csv`](bukti_fps_24_run.csv).

| Model | FPS run terendah | FPS run tertinggi |
|---|---:|---:|
{lines}

![Runtime OP3 empat model](garis_runtime_op3_empat_model_id.png)

**Batas:** kriteria berlaku untuk rerata per run. Pada grafik dengan bin 2 detik, FPS sesaat
dapat turun di bawah {fmt(KNF01_MIN_FPS, 0)} tanpa membatalkan kriteria. Rerata per model pada
T37 (terendah teacher 9,87 FPS saat berjalan) adalah besaran lain dan tidak dipakai sebagai
penilaian KNF-01. Run dikumpulkan lintas hari, sehingga selisih antarmodel tidak ditafsirkan
sebagai efek metode.
""")
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--replace", action="store_true",
                        help="Ganti folder keluaran yang seluruhnya dibangkitkan skrip ini")
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        manifest = out / "manifest_bukti_sha256.json"
        if not args.replace or not manifest.exists():
            raise SystemExit(f"Folder sudah ada: {out}. Pakai --replace hanya untuk folder hasil skrip ini.")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    w = Writer(out)
    w.source(DETECTOR)
    runs = load_runs(w)
    kf01 = build_kf01(w, runs)
    kf02 = build_kf02(w, runs)
    kf03 = build_kf03(w)
    kf04 = build_kf04(w, runs)
    knf01 = build_knf01(w, runs)
    for folder, items in COPIES.items():
        for source, name in items:
            w.source(ROOT / source)
            w.copy(source, f"{folder}/{name}")
    commit = git_commit()
    cases = readmes(w, kf01, kf02, kf03, kf04, knf01, commit)
    manifest = {
        "dibuat_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "skrip": rel(Path(__file__)),
        "skrip_sha256": sha256_file(Path(__file__)),
        "commit_repo": commit,
        "kriteria": "retrospektif dari indikator Bab 4; daftar KF/KNF disetujui pembimbing (D18)",
        "status": {c[1]: c[7] for c in cases},
        "sumber": dict(sorted(w.sources.items())),
        "keluaran": dict(sorted(w.outputs.items())),
    }
    data = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (out / "manifest_bukti_sha256.json").write_bytes(data)
    for c in cases:
        print(f"{c[1]}: {c[7]} | {c[6]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
