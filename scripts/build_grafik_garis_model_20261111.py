"""Grafik garis kontinu per model dan gabungan untuk bukti rumusan masalah 2 sampai 5.

Hanya membaca artefak yang sudah ada di repo; tidak melatih, mengevaluasi ulang, atau menjalankan robot.

- Akurasi VAL per epoch (mAP50, mAP50-95, precision, recall, F1) dari ``results.csv`` sembilan run student.
- Sapuan confidence VAL (precision, recall, F1) dari T11.
- Runtime OP3 (latensi, FPS, CPU, RSS) per bin 2 detik dari ``jendela_runtime.csv`` 24 run aktif T36.

Keluaran PNG (Indonesia dan Inggris), CSV data grafik, dan manifest hash ditulis ke ``dokumentasi/model/``.
Berkas yang sudah ada tidak ditimpa.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import statistics as st
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dokumentasi/model"
BIN_S = 2.0
WINDOW_S = 60.0
KNF_FPS = 8.0

SURFACE, INK, INK2, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3de", "#b8b7b0"
MODELS = {  # folder: properti
    "supervised": {"hue": "#2a78d6", "runtime": "sup1337", "t11": "supervised_seed1337", "robot_seed": 1337,
                   "runs": ["runs/supervised/yolo11_tiny_supervised_seed42_retry1", "runs/supervised/yolo11_tiny_supervised_seed1337",
                            "runs/supervised/yolo11_tiny_supervised_seed2025"],
                   "id": "Supervised seed 1337", "en": "Supervised seed 1337", "id_short": "Supervised", "en_short": "Supervised"},
    "kd_murni": {"hue": "#eb6834", "runtime": "kd42", "t11": "kd_seed42", "robot_seed": 42,
                 "runs": ["runs/kd/yolo11_tiny_pure_kd_v4_locked_seed42", "runs/kd/yolo11_tiny_pure_kd_v4_seed1337",
                          "runs/kd/yolo11_tiny_pure_kd_v4_seed2025"],
                 "id": "KD murni seed 42", "en": "Pure KD seed 42", "id_short": "KD murni", "en_short": "Pure KD"},
    "kd_hybrid": {"hue": "#1baf7a", "runtime": "hybrid1337", "t11": "hybrid_full_seed42", "robot_seed": 1337,
                  "runs": ["runs/kd_hybrid/yolo11_tiny_hybrid_full_seed42", "runs/kd_hybrid/yolo11_tiny_hybrid_full_seed1337",
                           "runs/kd_hybrid/yolo11_tiny_hybrid_full_seed2025"],
                  "id": "KD Hybrid full seed 1337", "en": "Hybrid full KD seed 1337", "id_short": "KD Hybrid full", "en_short": "Hybrid full KD"},
    "teacher_yolo11n": {"hue": "#eda100", "runtime": "teacher", "t11": "teacher_fp32", "robot_seed": None, "runs": [],
                        "id": "Teacher YOLO11n", "en": "Teacher YOLO11n", "id_short": "Teacher", "en_short": "Teacher"},
}
SEEDS = (42, 1337, 2025)
STYLES = ("-", "--", ":")
RUNTIME_DIR = {"01-teacher": "teacher", "02-kd-hybrid": "hybrid1337", "03-supervised": "sup1337", "04-kd-murni": "kd42"}
SOURCES: dict[str, str] = {}
OUTPUTS: list[str] = []

L = {
    "id": {"epoch": "Epoch", "map50": "mAP50 VAL", "map": "mAP50–95 VAL", "p": "Precision VAL", "r": "Recall VAL", "f1": "F1 VAL",
           "conf": "Ambang confidence", "t": "Waktu sejak frame pertama jendela ukur (detik)",
           "lat": "Latensi end-to-end (ms)", "fps": "FPS (frame/detik)", "cpu": "CPU proses (% satu CPU logis)", "rss": "RSS proses (MiB)",
           "idle": "Robot diam", "walk": "Robot berjalan", "u": "Ulangan", "seed": "seed", "robot": "dipakai di robot",
           "knf": "batas KNF-01: 8 FPS", "op": "confidence operasi 0,25", "dec": ","},
    "en": {"epoch": "Epoch", "map50": "VAL mAP50", "map": "VAL mAP50–95", "p": "VAL precision", "r": "VAL recall", "f1": "VAL F1",
           "conf": "Confidence threshold", "t": "Time since first frame of measurement window (s)",
           "lat": "End-to-end latency (ms)", "fps": "FPS (frames/s)", "cpu": "Process CPU (% of one logical CPU)", "rss": "Process RSS (MiB)",
           "idle": "Robot standing", "walk": "Robot walking", "u": "Repeat", "seed": "seed", "robot": "used on robot",
           "knf": "KNF-01 threshold: 8 FPS", "op": "operating confidence 0.25", "dec": "."},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path: Path) -> Path:
    SOURCES[path.relative_to(ROOT).as_posix()] = sha(path)
    return path


def fmt(lang: str, digits: int):
    return FuncFormatter(lambda v, _: f"{v:.{digits}f}".replace(".", L[lang]["dec"]))


def style(ax, lang: str, ydigits: int | None = None) -> None:
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=10)
    if ydigits is not None:
        ax.yaxis.set_major_formatter(fmt(lang, ydigits))


def save(fig, name: str, folder: str) -> None:
    path = OUT / folder / name
    if path.exists():
        raise FileExistsError(f"Tidak menimpa berkas yang sudah ada: {path}")
    fig.savefig(path, facecolor=SURFACE, dpi=200)
    plt.close(fig)
    OUTPUTS.append(path.relative_to(ROOT).as_posix())


def write_csv(rows: list[dict], name: str, folder: str) -> None:
    path = OUT / folder / name
    if path.exists():
        raise FileExistsError(f"Tidak menimpa berkas yang sudah ada: {path}")
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    OUTPUTS.append(path.relative_to(ROOT).as_posix())


def figure(title: str, subtitle: str, footer: str, nrows: int, ncols: int, size: tuple[float, float]):
    fig, axes = plt.subplots(nrows, ncols, figsize=size, squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    h = size[1]
    fig.text(0.04, 1 - 0.22 / h, title, fontsize=15, color=INK, weight="bold", va="top")
    fig.text(0.04, 1 - 0.55 / h, subtitle, fontsize=10.5, color=INK2, va="top")
    fig.text(0.04, 0.012, footer, fontsize=8.5, color=INK2, va="bottom", wrap=True)
    return fig, axes


def end_labels(ax, items, lang: str, digits: int = 3, min_gap_frac: float = 0.05) -> None:
    """Label nilai akhir di ujung kanan; geser vertikal agar tidak bertumpuk."""
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * min_gap_frac
    placed = []
    for x, y in sorted(items, key=lambda v: v[1]):
        yy = y if not placed or y - placed[-1][1] >= gap else placed[-1][1] + gap
        placed.append((x, yy, y))
    for x, yy, y in placed:
        ax.annotate(f"{y:.{digits}f}".replace(".", L[lang]["dec"]), xy=(x, y), xytext=(x + 1.5, yy),
                    textcoords="data", ha="left", va="center", fontsize=9, color=INK, annotation_clip=False)


# ---------------------------------------------------------------- data

def load_epochs(run: str) -> dict[str, list[float]]:
    rows = list(csv.DictReader(source(ROOT / run / "results.csv").open(encoding="utf-8")))
    p = [float(r["metrics/precision(B)"]) for r in rows]
    r_ = [float(r["metrics/recall(B)"]) for r in rows]
    return {"epoch": [int(r["epoch"]) for r in rows], "map50": [float(r["metrics/mAP50(B)"]) for r in rows],
            "map": [float(r["metrics/mAP50-95(B)"]) for r in rows], "p": p, "r": r_,
            "f1": [2 * a * b / (a + b) if a + b else 0.0 for a, b in zip(p, r_)]}


def load_t11() -> dict[str, list[dict]]:
    rows = list(csv.DictReader(source(ROOT / "analisis_performa/tabel/T11_sapuan_confidence.csv").open(encoding="utf-8")))
    out: dict[str, list[dict]] = {}
    for r in rows:
        if r["split"] != "val":
            continue
        out.setdefault(r["model"], []).append({"c": float(r["confidence_threshold"]), "p": float(r["precision"]),
                                               "r": float(r["recall"]), "f1": float(r["F1"])})
    for v in out.values():
        v.sort(key=lambda x: x["c"])
    return out


def load_runtime() -> dict[tuple[str, str], list[dict]]:
    manifest = json.loads((ROOT / "dokumentasi/2026-11-09/visualisasi-tambahan-empat-model/grafik-final/manifest_grafik.json").read_text(encoding="utf-8"))
    paths = sorted(k for k in manifest["sources_sha256"] if k.endswith("jendela_runtime.csv"))
    t36 = {(r["model"], r["condition"], r["ulangan"]): r for r in
           csv.DictReader(source(ROOT / "analisis_performa/tabel/T36_runtime_live_setara_per_run.csv").open(encoding="utf-8"))}
    runs: dict[tuple[str, str], list[dict]] = {}
    for rel in paths:
        if not (ROOT / rel).is_file():
            missing = [k for k in paths if not (ROOT / k).is_file()]
            raise FileNotFoundError(f"{len(missing)} dari {len(paths)} jendela_runtime.csv belum ada di repo, mis. {missing[0]}")
        path = source(ROOT / rel)
        # Manifest 9 November dihitung pada salinan berakhiran baris CRLF; repo menormalkan ke LF
        # (.gitattributes eol=lf). Isi dianggap sama bila salah satu bentuk cocok.
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        if manifest["sources_sha256"][rel] not in {hashlib.sha256(raw).hexdigest(),
                                                   hashlib.sha256(raw.replace(b"\n", b"\r\n")).hexdigest()}:
            raise RuntimeError(f"Hash sumber runtime berubah: {rel}")
        parts = Path(rel).parts
        model = RUNTIME_DIR[parts[-3]]
        cond = "idle" if parts[-2].startswith("idle") else "walk"
        rep = int(re.match(r"(?:idle|walk)-u(\d)", parts[-2]).group(1))
        rows = [r for r in csv.DictReader(path.open(encoding="utf-8")) if r["is_warmup"] == "False" and not r["error"]]
        t0 = int(rows[0]["capture_stamp_ns"])
        frames = [{"t": (int(r["capture_stamp_ns"]) - t0) / 1e9, "lat": float(r["end_to_end_ms"]),
                   "cpu": float(r["process_cpu_percent"]), "rss": int(r["process_rss_bytes"]) / 1048576} for r in rows]
        ref = t36[(model, cond, str(rep))]
        mean_lat = st.mean(f["lat"] for f in frames)
        if abs(mean_lat - float(ref["latency_mean_ms"])) > 0.01 or len(frames) != int(ref["frames"]):
            raise RuntimeError(f"Data {rel} tidak cocok dengan T36: {mean_lat} vs {ref['latency_mean_ms']}")
        nbin = int(WINDOW_S / BIN_S)
        bins = []
        for b in range(nbin):
            sel = [f for f in frames if b * BIN_S <= f["t"] < (b + 1) * BIN_S]
            bins.append({"t": (b + 0.5) * BIN_S, "lat": st.mean(f["lat"] for f in sel), "fps": len(sel) / BIN_S,
                         "cpu": st.mean(f["cpu"] for f in sel), "rss": st.mean(f["rss"] for f in sel)})
        runs.setdefault((model, cond), []).append({"rep": rep, "bins": bins, "source": rel})
    for v in runs.values():
        v.sort(key=lambda x: x["rep"])
        if [x["rep"] for x in v] != [1, 2, 3]:
            raise RuntimeError("Ulangan runtime tidak lengkap")
    return runs


# ---------------------------------------------------------------- grafik

ACC = ("map50", "map", "p", "r", "f1")


def accuracy_model(folder: str, lang: str, curves: dict[int, dict]) -> None:
    m, t = MODELS[folder], L[lang]
    fig, axes = figure(
        {"id": f"{m['id_short']}: akurasi VAL per epoch", "en": f"{m['en_short']}: VAL accuracy per epoch"}[lang],
        {"id": f"Tiga seed; garis tebal = seed {m['robot_seed']} yang {t['robot']}", "en": f"Three seeds; thick line = seed {m['robot_seed']} {t['robot']}"}[lang],
        {"id": "Sumber: results.csv per run (VAL 1.213 gambar). Precision/recall dari validator Ultralytics pada confidence yang memaksimalkan F1 rata-rata; F1 = rerata harmonik keduanya. Bukan hasil TEST dan bukan confidence 0,25.",
         "en": "Source: per-run results.csv (VAL, 1,213 images). Precision/recall from the Ultralytics validator at the confidence maximising mean F1; F1 = their harmonic mean. Not TEST results and not at confidence 0.25."}[lang],
        2, 3, (15, 8.6))
    for i, key in enumerate(ACC):
        ax = axes[i // 3][i % 3]
        style(ax, lang, 2)
        others = iter(("--", ":"))
        for seed in SEEDS:
            c = curves[seed]
            robot = seed == m["robot_seed"]
            ls = "-" if robot else next(others)
            ax.plot(c["epoch"], c[key], ls, color=m["hue"] if robot else INK2, linewidth=2.4 if robot else 1.2,
                    alpha=1 if robot else 0.75, label=f"{t['seed']} {seed}")
            if robot:
                ax.annotate(f"{c[key][-1]:.3f}".replace(".", t["dec"]), (c["epoch"][-1], c[key][-1]), xytext=(4, 0),
                            textcoords="offset points", va="center", fontsize=9, color=INK)
        ax.set_title(t[key], fontsize=11.5, color=INK, loc="left")
        ax.set_xlim(1, 100)
        ax.set_xlabel(t["epoch"], fontsize=10, color=INK2)
    axes[1][2].axis("off")
    h, lab = axes[0][0].get_legend_handles_labels()
    axes[1][2].legend(h, lab, loc="center", frameon=False, fontsize=11)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.88, bottom=0.10, hspace=0.38, wspace=0.22)
    save(fig, f"garis_akurasi_val_per_epoch_{folder}_{lang}.png", folder)


def sweep_model(folder: str, lang: str, rows: list[dict]) -> None:
    m, t = MODELS[folder], L[lang]
    name = {"teacher_yolo11n": "teacher_fp32", "kd_hybrid": "seed 42", "supervised": "seed 1337", "kd_murni": "seed 42"}[folder]
    note = {"id": " Untuk KD Hybrid, T11 hanya memuat seed 42; seed 1337 yang dipakai di robot tidak tersedia.",
            "en": " For Hybrid KD, T11 only covers seed 42; seed 1337 used on the robot is not available."}[lang] if folder == "kd_hybrid" else ""
    fig, axes = figure(
        {"id": f"{m['id_short']}: precision, recall, dan F1 terhadap ambang confidence", "en": f"{m['en_short']}: precision, recall and F1 versus confidence"}[lang],
        {"id": f"VAL 1.213 gambar, checkpoint {name}", "en": f"VAL, 1,213 images, checkpoint {name}"}[lang],
        {"id": "Sumber: T11 sapuan confidence (IoU pencocokan 0,5). Garis vertikal = confidence operasi 0,25 yang dipakai di robot." + note,
         "en": "Source: T11 confidence sweep (matching IoU 0.5). Vertical line = operating confidence 0.25 used on the robot." + note}[lang],
        1, 1, (11, 6.6))
    ax = axes[0][0]
    style(ax, lang, 2)
    c = [x["c"] for x in rows]
    for key, ls, lab in (("p", "-", "Precision"), ("r", "--", "Recall"), ("f1", ":", "F1")):
        y = [x[key] for x in rows]
        ax.plot(c, y, ls, color=m["hue"], linewidth=2.2, label=lab, marker="o", markersize=4)
        ax.annotate(lab, (c[-1], y[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=10, color=INK)
    ax.axvline(0.25, color=INK2, linewidth=1, linestyle="--")
    ax.text(0.255, 0.02, t["op"], transform=ax.get_xaxis_transform(), fontsize=9, color=INK2)
    ax.set_xlabel(t["conf"], fontsize=10.5, color=INK2)
    ax.xaxis.set_major_formatter(fmt(lang, 2))
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower left", frameon=False, fontsize=10)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.85, bottom=0.14)
    save(fig, f"garis_sapuan_confidence_val_{folder}_{lang}.png", folder)


RT = ("lat", "fps", "cpu", "rss")
RT_DIGITS = {"lat": 0, "fps": 0, "cpu": 0, "rss": 0}


def runtime_model(folder: str, lang: str, runtime: dict) -> None:
    m, t = MODELS[folder], L[lang]
    fig, axes = figure(
        {"id": f"{m['id']}: runtime OP3 selama jendela ukur 60 detik", "en": f"{m['en']}: OP3 runtime over the 60 s measurement window"}[lang],
        {"id": "Tiga ulangan per kondisi; titik = rerata per bin 2 detik", "en": "Three repeats per condition; points = mean per 2 s bin"}[lang],
        {"id": "Sumber: jendela_runtime.csv 24 run aktif T36 (rerata per run dicocokkan ulang dengan T36). FPS = frame diterima per 2 detik dibagi 2. CPU dari psutil untuk proses detektor; dapat melebihi 100% karena multithread. RSS = memori resident proses, bukan total RAM robot.",
         "en": "Source: jendela_runtime.csv of the 24 active T36 runs (per-run means re-checked against T36). FPS = frames received per 2 s divided by 2. CPU from psutil for the detector process; may exceed 100% due to multithreading. RSS = resident memory of the process, not total robot RAM."}[lang],
        4, 2, (14, 15))
    for j, cond in enumerate(("idle", "walk")):
        for i, key in enumerate(RT):
            ax = axes[i][j]
            style(ax, lang, RT_DIGITS[key])
            for run, ls in zip(runtime[(m["runtime"], cond)], STYLES):
                x = [b["t"] for b in run["bins"]]
                ax.plot(x, [b[key] for b in run["bins"]], ls, color=m["hue"], linewidth=1.8, label=f"{t['u']} {run['rep']}")
            if key == "fps":
                ax.axhline(KNF_FPS, color=INK2, linewidth=1, linestyle="--")
                ax.text(1, KNF_FPS, " " + t["knf"], fontsize=8.5, color=INK2, va="bottom")
                lo = min(b["fps"] for r in runtime[(m["runtime"], cond)] for b in r["bins"])
                ax.set_ylim(min(KNF_FPS - 1, lo - 1), None)
            ax.set_xlim(0, WINDOW_S)
            if i == 0:
                ax.set_title(t[cond], fontsize=12.5, color=INK, weight="bold")
            ax.set_ylabel(t[key], fontsize=10, color=INK2)
            if i == 3:
                ax.set_xlabel(t["t"], fontsize=10, color=INK2)
            if i == 0 and j == 1:
                ax.legend(loc="upper right", frameon=False, fontsize=9.5, ncol=3)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.07, hspace=0.32, wspace=0.18)
    save(fig, f"garis_runtime_op3_{folder}_{lang}.png", folder)


ORDER = ("teacher_yolo11n", "kd_hybrid", "supervised", "kd_murni")


def runtime_combined(lang: str, runtime: dict) -> list[dict]:
    t = L[lang]
    fig, axes = figure(
        {"id": "Empat model: runtime OP3 selama jendela ukur 60 detik", "en": "Four models: OP3 runtime over the 60 s measurement window"}[lang],
        {"id": "Setiap garis = rerata tiga ulangan per bin 2 detik; pita = rentang min–maks tiga ulangan", "en": "Each line = mean of three repeats per 2 s bin; band = min–max of the three repeats"}[lang],
        {"id": "Sumber: jendela_runtime.csv 24 run aktif T36. Run tidak dijalankan bersamaan; blok lintas 2–3 November. Tiga student berarsitektur identik, sehingga selisih di antaranya tidak ditafsirkan sebagai efek metode. CPU = % satu CPU logis proses detektor; RSS = memori resident proses.",
         "en": "Source: jendela_runtime.csv of the 24 active T36 runs. Runs were not simultaneous; blocks spanned 2–3 November. The three students share the same architecture, so differences among them are not read as method effects. CPU = % of one logical CPU for the detector process; RSS = process resident memory."}[lang],
        4, 2, (14, 15))
    rows = []
    for j, cond in enumerate(("idle", "walk")):
        for i, key in enumerate(RT):
            ax = axes[i][j]
            style(ax, lang, RT_DIGITS[key])
            for folder in ORDER:
                m = MODELS[folder]
                reps = runtime[(m["runtime"], cond)]
                x = [b["t"] for b in reps[0]["bins"]]
                vals = list(zip(*[[b[key] for b in r["bins"]] for r in reps]))
                mean = [st.mean(v) for v in vals]
                ax.fill_between(x, [min(v) for v in vals], [max(v) for v in vals], color=m["hue"], alpha=0.14, linewidth=0)
                ax.plot(x, mean, color=m["hue"], linewidth=2, label=m[f"{lang}_short"])
                if lang == "id":
                    for xx, v, mm in zip(x, vals, mean):
                        rows.append({"model": m["runtime"], "kondisi": cond, "metrik": key, "t_tengah_bin_s": xx,
                                     "rerata_3_ulangan": round(mm, 4), "min": round(min(v), 4), "maks": round(max(v), 4)})
            if key == "fps":
                ax.axhline(KNF_FPS, color=INK2, linewidth=1, linestyle="--")
                ax.text(1, KNF_FPS, " " + t["knf"], fontsize=8.5, color=INK2, va="bottom")
            ax.set_xlim(0, WINDOW_S)
            if i == 0:
                ax.set_title(t[cond], fontsize=12.5, color=INK, weight="bold")
            ax.set_ylabel(t[key], fontsize=10, color=INK2)
            if i == 3:
                ax.set_xlabel(t["t"], fontsize=10, color=INK2)
            if i == 0 and j == 1:
                ax.legend(loc="upper right", frameon=False, fontsize=9.5, ncol=2)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.92, bottom=0.07, hspace=0.32, wspace=0.18)
    save(fig, f"garis_runtime_op3_empat_model_{lang}.png", "gabungan")
    return rows


def accuracy_combined(lang: str, curves: dict[str, dict[int, dict]]) -> list[dict]:
    t = L[lang]
    fig, axes = figure(
        {"id": "Tiga metode student: akurasi VAL per epoch", "en": "Three student methods: VAL accuracy per epoch"}[lang],
        {"id": "Garis = rerata tiga seed (42, 1337, 2025); pita = rentang min–maks", "en": "Line = mean of three seeds (42, 1337, 2025); band = min–max"}[lang],
        {"id": "Sumber: results.csv sembilan run (VAL 1.213 gambar). Precision/recall dari validator Ultralytics pada confidence yang memaksimalkan F1 rata-rata; F1 = rerata harmonik keduanya. Kurva training teacher utama tidak tersedia di repo. Bukan hasil TEST.",
         "en": "Source: results.csv of nine runs (VAL, 1,213 images). Precision/recall from the Ultralytics validator at the confidence maximising mean F1; F1 = their harmonic mean. The main teacher's training curve is not in the repo. Not TEST results."}[lang],
        2, 3, (15, 8.6))
    rows = []
    for i, key in enumerate(ACC):
        ax = axes[i // 3][i % 3]
        style(ax, lang, 2)
        ends = []
        for folder in ("supervised", "kd_murni", "kd_hybrid"):
            m = MODELS[folder]
            ep = curves[folder][42]["epoch"]
            vals = list(zip(*[curves[folder][s][key] for s in SEEDS]))
            mean = [st.mean(v) for v in vals]
            ax.fill_between(ep, [min(v) for v in vals], [max(v) for v in vals], color=m["hue"], alpha=0.16, linewidth=0)
            ax.plot(ep, mean, color=m["hue"], linewidth=2, label=m[f"{lang}_short"])
            ends.append((ep[-1], mean[-1]))
            if lang == "id":
                for e, v, mm in zip(ep, vals, mean):
                    rows.append({"metode": folder, "metrik": key, "epoch": e, "rerata_3_seed": round(mm, 6),
                                 "min": round(min(v), 6), "maks": round(max(v), 6)})
        ax.set_title(t[key], fontsize=11.5, color=INK, loc="left")
        ax.set_xlim(1, 100)
        ax.set_xlabel(t["epoch"], fontsize=10, color=INK2)
        end_labels(ax, ends, lang)
    axes[1][2].axis("off")
    h, lab = axes[0][0].get_legend_handles_labels()
    axes[1][2].legend(h, lab, loc="center", frameon=False, fontsize=11)
    fig.subplots_adjust(left=0.05, right=0.96, top=0.88, bottom=0.10, hspace=0.38, wspace=0.24)
    save(fig, f"garis_akurasi_val_per_epoch_tiga_metode_{lang}.png", "gabungan")
    return rows


def sweep_combined(lang: str, t11: dict) -> None:
    t = L[lang]
    fig, axes = figure(
        {"id": "Empat model: precision, recall, dan F1 terhadap ambang confidence", "en": "Four models: precision, recall and F1 versus confidence"}[lang],
        {"id": "VAL 1.213 gambar; teacher_fp32, Hybrid seed 42, Supervised seed 1337, KD murni seed 42",
         "en": "VAL, 1,213 images; teacher_fp32, Hybrid seed 42, Supervised seed 1337, Pure KD seed 42"}[lang],
        {"id": "Sumber: T11 sapuan confidence (IoU pencocokan 0,5). T11 tidak memuat Hybrid seed 1337 yang dipakai di robot, sehingga Hybrid diwakili seed 42. Garis vertikal = confidence operasi 0,25.",
         "en": "Source: T11 confidence sweep (matching IoU 0.5). T11 does not include Hybrid seed 1337 used on the robot, so Hybrid is represented by seed 42. Vertical line = operating confidence 0.25."}[lang],
        1, 3, (16, 6.2))
    for i, (key, lab) in enumerate((("p", "Precision"), ("r", "Recall"), ("f1", "F1"))):
        ax = axes[0][i]
        style(ax, lang, 2)
        for folder in ORDER:
            m = MODELS[folder]
            rows = t11[m["t11"]]
            ax.plot([x["c"] for x in rows], [x[key] for x in rows], color=m["hue"], linewidth=2, label=m[f"{lang}_short"],
                    marker="o", markersize=3.5)
        ax.axvline(0.25, color=INK2, linewidth=1, linestyle="--")
        ax.set_title(f"{lab} VAL" if lang == "id" else f"VAL {lab.lower() if lab != 'F1' else 'F1'}", fontsize=11.5, color=INK, loc="left")
        ax.set_xlabel(t["conf"], fontsize=10, color=INK2)
        ax.xaxis.set_major_formatter(fmt(lang, 1))
        if i == 0:
            ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.82, bottom=0.17, wspace=0.2)
    save(fig, f"garis_sapuan_confidence_val_empat_model_{lang}.png", "gabungan")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bagian", choices=("akurasi", "runtime"), required=True,
                        help="akurasi: per epoch dan sapuan confidence; runtime: 24 run OP3 (butuh semua jendela_runtime.csv)")
    args = parser.parse_args()
    if args.bagian == "akurasi":
        curves = {f: {s: load_epochs(r) for s, r in zip(SEEDS, MODELS[f]["runs"])} for f in ("supervised", "kd_murni", "kd_hybrid")}
        t11 = load_t11()
        for lang in ("id", "en"):
            for folder in curves:
                accuracy_model(folder, lang, curves[folder])
            for folder in ORDER:
                sweep_model(folder, lang, t11[MODELS[folder]["t11"]])
            acc_rows = accuracy_combined(lang, curves)
            sweep_combined(lang, t11)
            if lang == "id":
                write_csv(acc_rows, "data_garis_akurasi_val_per_epoch_tiga_metode.csv", "gabungan")
    else:
        runtime = load_runtime()
        for lang in ("id", "en"):
            for folder in ORDER:
                runtime_model(folder, lang, runtime)
            rt_rows = runtime_combined(lang, runtime)
            if lang == "id":
                write_csv(rt_rows, "data_garis_runtime_op3_empat_model.csv", "gabungan")
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "part": args.bagian,
        "generator": "scripts/build_grafik_garis_model_20261111.py",
        "generator_sha256": sha(Path(__file__)),
        "bin_seconds": BIN_S,
        "notes": [
            "Akurasi per epoch berasal dari VAL saat training; bukan TEST dan bukan confidence 0,25.",
            "Precision/recall per epoch = keluaran validator Ultralytics 8.4.130 pada confidence yang memaksimalkan F1 rata-rata; F1 dihitung sebagai rerata harmonik keduanya.",
            "Kurva training teacher utama tidak tersedia di repo.",
            "T11 tidak memuat Hybrid seed 1337; grafik sapuan Hybrid memakai seed 42.",
            "Runtime: bin 2 detik dari jendela 60 detik; rerata latensi dan jumlah frame per run dicocokkan ulang dengan T36.",
        ],
        "sources_sha256": SOURCES,
        "outputs_sha256": {p: sha(ROOT / p) for p in OUTPUTS},
    }
    path = OUT / f"manifest_grafik_garis_{args.bagian}.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"part": args.bagian, "outputs": len(OUTPUTS), "sources": len(SOURCES)}))


if __name__ == "__main__":
    main()
