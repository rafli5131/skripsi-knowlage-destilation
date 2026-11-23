#!/usr/bin/env python3
"""Rangkum jejak waktu training, evaluasi, dan pengujian live menjadi satu folder.

Skrip membaca manifest, results.csv, tabel T36, dan log jendela yang sudah ada di
repositori, lalu menulis ``jejak_waktu/``: kronologi kegiatan, waktu per epoch,
ringkasan timestamp frame live, garis waktu bergambar, README, dan manifest
SHA-256. Tidak ada eksperimen baru dan berkas sumber tidak diubah.
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
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "jejak_waktu"
REGISTRY = ROOT / "configs/model_registry.yaml"
T36 = ROOT / "analisis_performa/tabel/T36_runtime_live_setara_per_run.csv"
RUN_ROOTS = [ROOT / "dokumentasi/2026-11-02", ROOT / "dokumentasi/2026-11-03"]
# Log jendela pelengkap yang diekstrak dari OP3 (prompt 23 November 2026).
PELENGKAP = ROOT / "log_op3_pelengkap/live_24_run"
TEACHER_TRAINING = ROOT / "log_op3_pelengkap/teacher_training"

METODE = {"kd": "KD murni", "supervised": "Supervised", "hybrid_full": "KD Hybrid full"}
MODEL_LIVE = {"teacher": "Teacher YOLO11n", "hybrid1337": "KD Hybrid seed 1337",
              "sup1337": "Supervised seed 1337", "kd42": "KD murni seed 42"}
KONDISI = {"idle": "diam", "walk": "berjalan"}
# Palet tetap yang dipakai grafik lain di repositori (supervised, KD murni, Hybrid).
WARNA = {"Supervised": "#2a78d6", "KD murni": "#eb6834", "KD Hybrid full": "#1baf7a"}
ABU = "#6b7280"

TRAINING_LAIN = [
    ("runs/kd_hybrid_v2", "Ablasi Hybrid v2 (S1 sampai S8)"),
    ("runs/kd_teacher_ablation/server2", "Ablasi teacher T42 (student)"),
    ("runs/kd_hybrid/yolo11_tiny_hybrid_feature_seed42", "Hybrid feature (pendahuluan)"),
    ("runs/kd/yolo11_tiny_pure_weighted_pilot_seed42", "KD murni berbobot (pilot)"),
    ("runs/kd/yolo11_tiny_pure_kd_v4", "KD murni v4 (run awal)"),
]
EVALUASI_OFFLINE = [
    ("runs/op3_camera_eval/20261021_idle_01_exploratory_retry1/input_manifest.json", "Evaluasi kamera eksploratif T27"),
    ("runs/op3_multi_session_eval/20261021_primary260_partial50_v1/input_manifest.json", "Evaluasi multi-sesi 260 frame (awal)"),
    ("runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/input_manifest.json", "Evaluasi 260 frame Hybrid vs supervised"),
    ("runs/op3_t43_evaluation/20261112_reviewed_260/input_manifest.json", "Evaluasi T43 260 frame"),
    ("runs/op3_t43_sensitivity/20261112_confidence_01/run_manifest.json", "Uji sensitivitas T43"),
    ("runs/op3_single_path_eval/20261116_runtime_01/runtime_stages_manifest.json", "Rincian runtime T45"),
]
VERIFIKASI = [
    ("analisis_performa/lab_server/verifikasi_jalur_test_20261113/hasil_verifikasi_jalur_test.json", "Verifikasi jalur TEST sembilan student (D23)"),
    ("analisis_performa/lab_server/verifikasi_jalur_test_20261116_teacher/hasil_verifikasi_jalur_test.json", "Verifikasi jalur TEST teacher (D24)"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def parse(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def iso(value: dt.datetime | None) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds") if value else ""


def wib(value: dt.datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(dt.timezone(dt.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


class Writer:
    def __init__(self, out: Path):
        self.out = out
        self.outputs: dict[str, str] = {}
        self.sources: dict[str, str] = {}

    def source(self, path: Path) -> Path:
        self.sources[rel(path)] = sha256(path)
        return path

    def write(self, name: str, data: bytes) -> None:
        path = self.out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.outputs[name] = hashlib.sha256(data).hexdigest()

    def table(self, name: str, header: list[str], rows: list[list]) -> None:
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
        self.write(name, buffer.getvalue().encode("utf-8"))


def device(manifest: dict) -> str:
    runtime = manifest.get("runtime")
    if isinstance(runtime, dict):
        return runtime.get("device_name") or runtime.get("device_type") or ""
    return "tidak tercatat di manifest"


def results_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [{k.strip(): v.strip() for k, v in row.items()} for row in csv.DictReader(stream)]


def training_main(w: Writer):
    registry = yaml.safe_load(w.source(REGISTRY).read_text(encoding="utf-8"))["models"]
    activities, epochs, main_dirs = [], [], set()
    for key, info in registry.items():
        if key == "teacher_fp32" and (TEACHER_TRAINING / "manifest.json").exists():
            manifest = json.loads(w.source(TEACHER_TRAINING / "manifest.json").read_text(encoding="utf-8"))
            rows = results_rows(w.source(TEACHER_TRAINING / "results.csv"))
            stamp = parse(manifest.get("timestamp"))
            activities.append(["training_utama", "teacher_fp32", "Teacher YOLO11n", "42", "", iso(stamp), "",
                               manifest.get("gpu_name", ""), len(rows), round(float(rows[-1]["time"]), 1),
                               rel(TEACHER_TRAINING / "manifest.json"),
                               "Manifest teacher hanya memuat satu kolom timestamp; ditempatkan sebagai waktu selesai "
                               "karena belum dipastikan apakah menandai awal atau akhir training."])
            previous = 0.0
            for row in rows:
                t = float(row["time"])
                epochs.append(["teacher_fp32", "Teacher YOLO11n", "42", int(row["epoch"]), t,
                               round(t - previous, 2) if t >= previous else "",
                               row.get("metrics/precision(B)", ""), row.get("metrics/recall(B)", ""),
                               row.get("metrics/mAP50(B)", ""), row.get("metrics/mAP50-95(B)", "")])
                previous = t
            continue
        if key == "teacher_fp32":
            activities.append(["training_utama", "teacher_fp32", "Teacher YOLO11n", "", "", "", "",
                               "NVIDIA L40 (menurut audit 22 Oktober)", "100", "",
                               "docs/STATUS_AUDIT_LAB_SERVER_2026-10-22.md",
                               "Dilatih di server lab pada proyek Advance Vision; manifest dan log ada di akun lama yang kini tidak dapat diakses, sehingga waktu training tidak tersedia di repositori."])
            continue
        method = key.rsplit("_seed", 1)[0]
        seed = key.rsplit("_seed", 1)[1]
        run_dir = ROOT / Path(info["manifest"]).parent
        main_dirs.add(run_dir.resolve())
        manifest = json.loads(w.source(run_dir / "manifest.json").read_text(encoding="utf-8"))
        rows = results_rows(w.source(run_dir / "results.csv"))
        start, finish = parse(manifest.get("started_at_utc")), parse(manifest.get("finished_at_utc"))
        resume = manifest.get("resume_history") or []
        if resume:
            segments = sum(float(r.get("pre_resume_results_csv_time_seconds", 0)) +
                           float(r.get("post_resume_results_csv_time_seconds", 0)) for r in resume)
            train_s = segments
            note = "Dilanjutkan dari checkpoint setelah interupsi; durasi training adalah jumlah dua segmen, selisih mulai-selesai memuat jeda interupsi."
        else:
            train_s = float(rows[-1]["time"])
            note = ""
        activities.append(["training_utama", key, METODE[method], seed, iso(start), iso(finish),
                           round((finish - start).total_seconds(), 1), device(manifest), len(rows),
                           round(train_s, 1), rel(run_dir / "manifest.json"), note])
        previous = 0.0
        for row in rows:
            t = float(row["time"])
            epochs.append([key, METODE[method], seed, int(row["epoch"]), t,
                           round(t - previous, 2) if t >= previous else "",
                           row.get("metrics/precision(B)", ""), row.get("metrics/recall(B)", ""),
                           row.get("metrics/mAP50(B)", ""), row.get("metrics/mAP50-95(B)", "")])
            previous = t
    return activities, epochs, main_dirs


def training_other(w: Writer, main_dirs: set) -> list[list]:
    rows = []
    for base, label in TRAINING_LAIN:
        path = ROOT / base
        manifests = [path / "manifest.json"] if (path / "manifest.json").exists() else sorted(path.glob("*/manifest.json"))
        for mf in manifests:
            if mf.parent.resolve() in main_dirs:
                continue
            manifest = json.loads(w.source(mf).read_text(encoding="utf-8"))
            start, finish = parse(manifest.get("started_at_utc")), parse(manifest.get("finished_at_utc"))
            results = mf.parent / "results.csv"
            n = len(results_rows(results)) if results.exists() else ""
            rows.append(["training_pendukung", mf.parent.name, label, manifest.get("seed", ""), iso(start),
                         iso(finish), round((finish - start).total_seconds(), 1) if start and finish else "",
                         device(manifest), n, "", rel(mf), ""])
    return rows


def evaluations(w: Writer) -> list[list]:
    rows = []
    for mf in sorted((ROOT / "runs/final_test").glob("*/manifest.json")):
        manifest = json.loads(w.source(mf).read_text(encoding="utf-8"))
        start, finish = parse(manifest.get("started_at_utc")), parse(manifest.get("finished_at_utc"))
        models = manifest.get("models") or manifest.get("locked_models") or []
        count = len(models) if isinstance(models, (list, dict)) else ""
        status = manifest.get("status", "")
        name = f"Sesi TEST {count} checkpoint" if status == "complete" else "Sesi TEST gagal (diulang sebagai retry1)"
        rows.append(["evaluasi_test", mf.parent.name, name, "", iso(start),
                     iso(finish), round((finish - start).total_seconds(), 1), device(manifest), "", "", rel(mf),
                     f"status {manifest.get('status', '')}"])
    for source, label in VERIFIKASI:
        path = ROOT / source
        data = json.loads(w.source(path).read_text(encoding="utf-8"))
        start, finish = parse(data.get("started_at_utc")), parse(data.get("finished_at_utc"))
        host = (data.get("environment") or {}).get("hostname", "")
        rows.append(["verifikasi_test", path.parent.name, label, "", iso(start), iso(finish),
                     round((finish - start).total_seconds(), 1), f"CPU {host}".strip(), "", "", source, ""])
    for source, label in EVALUASI_OFFLINE:
        path = ROOT / source
        data = json.loads(w.source(path).read_text(encoding="utf-8"))
        created = parse(data.get("created_at_utc") or data.get("created_utc"))
        rows.append(["evaluasi_offline_op3", path.parent.name, label, "", iso(created), "", "", "", "", "",
                     source, "Hanya waktu pembuatan manifest yang tercatat."])
    return rows


def live_runs(w: Writer) -> tuple[list[list], list[list]]:
    runs = list(csv.DictReader(w.source(T36).open(encoding="utf-8")))
    folders = {}
    for base in RUN_ROOTS:
        for summary in sorted(base.rglob("summary_metrics.json")):
            if "arsip" in summary.as_posix():
                continue
            run_id = json.loads(summary.read_text(encoding="utf-8")).get("run_id")
            folders.setdefault(run_id, summary.parent)
    activities, frames = [], []
    for run in runs:
        start, finish = parse(run["window_start_utc"]), parse(run["window_end_utc"])
        folder = folders[run["run_id"]]
        window = folder / "jendela_runtime.csv"
        if not window.exists() and (PELENGKAP / run["run_id"] / "jendela_runtime.csv").exists():
            window = PELENGKAP / run["run_id"] / "jendela_runtime.csv"
        status = "ada di repositori" if window.exists() else "hanya di OP3"
        activities.append(["run_live", run["run_id"], MODEL_LIVE[run["model"]], "", iso(start), iso(finish),
                           round((finish - start).total_seconds(), 1), "OP3 i5-1240P CPU", "", "",
                           rel(T36), f"kondisi {KONDISI[run['condition']]}, ulangan {run['ulangan']}, "
                                     f"{run['frames']} frame, {round(float(run['fps']), 2)} FPS; log per frame {status}"])
        if window.exists():
            rows = list(csv.DictReader(w.source(window).open(encoding="utf-8")))
            stamps = [int(r["capture_stamp_ns"]) for r in rows]
            received = [parse(r["receive_time_utc"]) for r in rows]
            gaps = [(b - a) / 1e9 for a, b in zip(stamps, stamps[1:])]
            frames.append([run["run_id"], MODEL_LIVE[run["model"]], KONDISI[run["condition"]], run["ulangan"],
                           len(rows), iso(min(received)), iso(max(received)),
                           round((max(stamps) - min(stamps)) / 1e9, 3), round(max(gaps), 3),
                           round(sum(gaps) / len(gaps), 4), sum(1 for r in rows if r["error"]),
                           rel(window), sha256(window)])
        else:
            frames.append([run["run_id"], MODEL_LIVE[run["model"]], KONDISI[run["condition"]], run["ulangan"],
                           run["frames"], iso(start), iso(finish), "", run["max_receive_gap_s"], "", run["error_frames"],
                           f"OP3: runs/op3_pytorch/{run['run_id']}.csv", run["raw_csv_sha256"]])
    return activities, frames


def chart(w: Writer, activities: list[list]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.ticker
    import matplotlib.pyplot as plt

    groups = [
        ("Training utama", [a for a in activities if a[0] == "training_utama" and a[4]]),
        ("Training pendukung", [a for a in activities if a[0] == "training_pendukung" and a[4]]),
        ("Evaluasi TEST dan verifikasi", [a for a in activities if a[0] in ("evaluasi_test", "verifikasi_test")]),
        ("Evaluasi offline OP3", [a for a in activities if a[0] == "evaluasi_offline_op3"]),
        ("Run live OP3 (24)", [a for a in activities if a[0] == "run_live"]),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=200)
    labels = []
    for y, (name, items) in enumerate(groups):
        labels.append(name)
        for item in items:
            start = parse(item[4])
            finish = parse(item[5]) or start + dt.timedelta(hours=2)
            color = WARNA.get(item[2], ABU) if item[0] == "training_utama" else ABU
            width = max((finish - start).total_seconds() / 86400, 0.12)
            ax.barh(len(groups) - 1 - y, width, left=mdates.date2num(start), height=0.5, color=color,
                    edgecolor="white", linewidth=0.6)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels(list(reversed(labels)), fontsize=9, color="#1f2937")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda x, _: f"{mdates.num2date(x).day:02d} {bulan[mdates.num2date(x).month - 1]}"))
    ax.tick_params(axis="x", labelsize=8, colors="#4b5563")
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#9ca3af")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in WARNA.values()] + [plt.Rectangle((0, 0), 1, 1, color=ABU)]
    ax.legend(handles, list(WARNA) + ["Kegiatan lain"], loc="upper left", bbox_to_anchor=(0, -0.12), ncol=4,
              frameon=False, fontsize=8)
    ax.set_title("Garis waktu training, evaluasi, dan pengujian (UTC, Oktober sampai November 2026)",
                 loc="left", fontsize=10.5, color="#111827")
    fig.text(0.01, 0.005, "Sumber: manifest run, T36, dan verifikasi jalur TEST di repositori. Teacher utama tidak memiliki catatan waktu training.",
             fontsize=7, color="#6b7280")
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", metadata={"Software": None})
    plt.close(fig)
    w.write("garis_waktu_kegiatan_id.png", buffer.getvalue())


def readme(w: Writer, activities, epochs, frames, commit: str) -> None:
    main = [a for a in activities if a[0] == "training_utama"]
    main_rows = "\n".join(
        f"| {a[2]} | {a[3] or '-'} | {wib(parse(a[4])) or 'tidak tersedia'} | {wib(parse(a[5])) or 'tidak tersedia'} | "
        f"{(str(round(float(a[9]) / 3600, 2)).replace('.', ',') + ' jam') if a[9] != '' else '-'} | {a[7]} |"
        for a in main)
    tests = [a for a in activities if a[0] in ("evaluasi_test", "verifikasi_test")]
    test_rows = "\n".join(f"| {a[2]} | {wib(parse(a[4]))} | {str(a[6]).replace('.', ',')} detik | {a[7]} |" for a in tests)
    live = [a for a in activities if a[0] == "run_live"]
    first, last = min(parse(a[4]) for a in live), max(parse(a[5]) for a in live)
    in_repo = sum(1 for f in frames if not f[11].startswith("OP3:"))
    teacher = next(a for a in activities if a[1] == "teacher_fp32")
    if teacher[5]:
        teacher_text = (
            "**Teacher utama** dilatih di server lab pada proyek Advance Vision, bukan di robot. Robot hanya menyimpan\n"
            "salinan bobotnya (SHA-256 `e05b2b21...420b8c`). Salinan manifest dan `results.csv` training teacher ada di\n"
            f"[`log_op3_pelengkap/teacher_training/`](../log_op3_pelengkap/teacher_training/). Manifest hanya memuat satu\n"
            f"timestamp ({wib(parse(teacher[5]))} WIB) yang belum dipastikan menandai awal atau akhir training; durasi\n"
            "training diambil dari kolom `time` epoch terakhir. `dataset_version` teacher tetap kosong, sehingga\n"
            "keterbatasan provenance dataset teacher masih berlaku.")
    else:
        teacher_text = (
            "**Teacher utama** dilatih di server lab pada proyek Advance Vision, bukan di robot. Robot hanya menyimpan\n"
            "salinan bobotnya (SHA-256 `e05b2b21...420b8c`). Audit 22 Oktober mencatat bahwa manifest dan log teacher\n"
            "menyebut 100 epoch, seed 42, dan GPU L40, tetapi berkas tersebut berada di akun server lama yang kini tidak\n"
            "dapat diakses, sehingga waktu mulai dan selesai training teacher tidak tersedia di repositori.")
    w.write("README.md", f"""# Jejak waktu training, evaluasi, dan pengujian

Folder ini merangkum kapan setiap model dilatih, dievaluasi, dan diuji di robot. Semua angka dibaca dari
berkas yang sudah ada di repositori: manifest run (`started_at_utc`, `finished_at_utc`), kolom `time`
pada `results.csv`, tabel T36, log jendela runtime, dan hasil verifikasi jalur TEST. Waktu asli tercatat
dalam UTC; tabel di halaman ini juga menampilkannya dalam WIB (UTC+7).

![Garis waktu kegiatan](garis_waktu_kegiatan_id.png)

## Isi folder

| Berkas | Isi |
|---|---|
| [`kronologi_kegiatan.csv`](kronologi_kegiatan.csv) | {len(activities)} kegiatan berurutan waktu: training utama dan pendukung, sesi TEST, verifikasi jalur, evaluasi offline OP3, dan 24 run live, lengkap dengan perangkat dan berkas sumber |
| [`training_per_epoch.csv`](training_per_epoch.csv) | {len(epochs)} baris: waktu kumulatif dan durasi tiap epoch, serta precision, recall, mAP50, dan mAP50-95 VAL untuk sembilan student utama |
| [`timestamp_frame_live_24_run.csv`](timestamp_frame_live_24_run.csv) | Untuk tiap run live: jumlah frame, timestamp frame pertama dan terakhir, rentang timestamp kamera, jeda terbesar, dan jumlah error |
| `garis_waktu_kegiatan_id.png` | Grafik garis waktu di atas |
| [`manifest_jejak_waktu_sha256.json`](manifest_jejak_waktu_sha256.json) | SHA-256 berkas keluaran dan setiap berkas sumber |

## Training utama

| Metode | Seed | Mulai (WIB) | Selesai (WIB) | Durasi training | Perangkat |
|---|---|---|---|---:|---|
{main_rows}

Durasi training diambil dari kolom `time` epoch terakhir, sama dengan
[T35](../analisis_performa/tabel/T35_waktu_training_dan_pengujian.md). Supervised seed 1337 sempat terhenti
dan dilanjutkan dari checkpoint, sehingga durasinya adalah jumlah dua segmen dan selisih mulai-selesai
memuat jeda interupsi.

{teacher_text}

## Evaluasi TEST dan verifikasi jalur

| Kegiatan | Mulai (WIB) | Durasi | Perangkat |
|---|---|---:|---|
{test_rows}

Durasi sesi TEST mencakup seluruh checkpoint dalam sesi dan overhead penyiapan, bukan waktu per model.

## Pengujian live di OP3

24 run live berlangsung dari {wib(first)} sampai {wib(last)} WIB, masing-masing dengan jendela ukur 60
detik. Log per frame (`capture_stamp_ns`, `receive_time_utc`, durasi tiap tahap, CPU, RSS, error) untuk
{in_repo} run tersimpan di repositori. Untuk {len(frames) - in_repo} run lainnya, log mentah hanya ada di OP3;
repositori menyimpan hash-nya pada kolom `raw_csv_sha256` T36 dan kolom `sha256` tabel frame.

## Yang masih dicari di robot

| Yang dicari | Lokasi yang diduga di OP3 | Cara memeriksa |
|---|---|---|
| Log per frame {len(frames) - in_repo} run live | `runs/op3_pytorch/<run_id>.csv` pada repo robot | `sha256sum` harus sama dengan kolom `sha256` pada `timestamp_frame_live_24_run.csv` |
| Manifest capture frame T38 dan T43 | `data/op3_camera_eval/sessions/` dan `data/op3_camera_eval/experiments/t43_20261112/` | Cocokkan dengan manifest beku T38 dan `review_260_audit_and_frozen_hashes.json` |
| Manifest atau log training teacher | `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/` (folder yang sama dengan bobot teacher) | Cari `manifest.json`, `args.yaml`, atau `results.csv`; bila tidak ada, catat sebagai tidak tersedia |

Frame, label, dan log mentah dari robot tetap tidak masuk Git kecuali Bhre memintanya. Bila log mentah
disalin ke repositori, jalankan ulang skrip agar tabel frame terisi lengkap.

## Membangkitkan ulang

```bash
python3 scripts/build_jejak_waktu.py --replace
```

Dibangkitkan dari commit `{commit[:12]}`.
""".encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        if not args.replace or not (out / "manifest_jejak_waktu_sha256.json").exists():
            raise SystemExit(f"Folder sudah ada: {out}. Pakai --replace hanya untuk folder hasil skrip ini.")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    w = Writer(out)
    activities, epochs, main_dirs = training_main(w)
    activities += training_other(w, main_dirs)
    activities += evaluations(w)
    live, frames = live_runs(w)
    activities += live
    activities.sort(key=lambda a: (a[4] == "", a[4], a[1]))
    w.table("kronologi_kegiatan.csv",
            ["kategori", "id", "nama", "seed", "mulai_utc", "selesai_utc", "durasi_mulai_selesai_detik",
             "perangkat", "epoch", "durasi_training_detik", "sumber", "catatan"], activities)
    w.table("training_per_epoch.csv",
            ["model", "metode", "seed", "epoch", "waktu_kumulatif_detik", "durasi_epoch_detik",
             "precision_val", "recall_val", "map50_val", "map50_95_val"], epochs)
    w.table("timestamp_frame_live_24_run.csv",
            ["run_id", "model", "kondisi", "ulangan", "frame", "frame_pertama_utc", "frame_terakhir_utc",
             "rentang_timestamp_kamera_detik", "jeda_terbesar_detik", "jeda_rerata_detik", "error_frame",
             "sumber", "sha256"], frames)
    chart(w, activities)
    commit = git_commit()
    readme(w, activities, epochs, frames, commit)
    manifest = {
        "dibuat_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "skrip": rel(Path(__file__)), "skrip_sha256": sha256(Path(__file__)), "commit_repo": commit,
        "sumber": dict(sorted(w.sources.items())), "keluaran": dict(sorted(w.outputs.items())),
    }
    (out / "manifest_jejak_waktu_sha256.json").write_bytes(
        (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"{len(activities)} kegiatan, {len(epochs)} baris epoch, {len(frames)} run live")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
