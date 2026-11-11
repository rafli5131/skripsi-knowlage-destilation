"""Grafik tunggal mAP50-95 VAL per epoch tiga metode student (rerata 3 seed, pita min-maks).

Keluaran: dokumentasi/model/gabungan/kurva_map50_95_val_per_epoch_{id,en}.png. Hapus keluaran lama sebelum menjalankan ulang.
"""
import csv, statistics as st, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1] / "runs"
runs = {
    "sup": [R/"supervised/yolo11_tiny_supervised_seed42_retry1", R/"supervised/yolo11_tiny_supervised_seed1337", R/"supervised/yolo11_tiny_supervised_seed2025"],
    "kd": [R/"kd/yolo11_tiny_pure_kd_v4_locked_seed42", R/"kd/yolo11_tiny_pure_kd_v4_seed1337", R/"kd/yolo11_tiny_pure_kd_v4_seed2025"],
    "hyb": [R/"kd_hybrid/yolo11_tiny_hybrid_full_seed42", R/"kd_hybrid/yolo11_tiny_hybrid_full_seed1337", R/"kd_hybrid/yolo11_tiny_hybrid_full_seed2025"],
}
color = {"sup": "#2a78d6", "kd": "#eb6834", "hyb": "#1baf7a"}
TXT = {
 "id": {"sup": "Supervised", "kd": "KD murni", "hyb": "KD Hybrid full",
        "title": "Kurva mAP50–95 VAL per epoch (rerata 3 seed, pita = min–maks)",
        "x": "Epoch", "y": "mAP50–95 VAL", "src": "Sumber: results.csv sembilan run student (seed 42, 1337, 2025); VAL 1.213 gambar. Dipakai untuk memilih best.pt, bukan hasil TEST.", "dec": ","},
 "en": {"sup": "Supervised", "kd": "Pure KD", "hyb": "Hybrid full KD",
        "title": "VAL mAP50–95 per epoch (mean of 3 seeds, band = min–max)",
        "x": "Epoch", "y": "VAL mAP50–95", "src": "Source: results.csv of nine student runs (seeds 42, 1337, 2025); VAL 1,213 images. Used to select best.pt, not TEST results.", "dec": "."},
}
def load(p, col="metrics/mAP50-95(B)"):
    rows = list(csv.DictReader(open(p/"results.csv")))
    return [int(r["epoch"]) for r in rows], [float(r[col]) for r in rows]

data = {}
for k, ps in runs.items():
    curves = [load(p) for p in ps]
    ep = curves[0][0]
    assert all(c[0] == ep for c in curves), k
    vals = list(zip(*[c[1] for c in curves]))
    data[k] = (ep, [st.mean(v) for v in vals], [min(v) for v in vals], [max(v) for v in vals])

for lang, t in TXT.items():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
    for k in ("sup", "kd", "hyb"):
        ep, m, lo, hi = data[k]
        ax.fill_between(ep, lo, hi, color=color[k], alpha=0.18, linewidth=0)
        ax.plot(ep, m, color=color[k], linewidth=2, label=t[k])
        val = f"{m[-1]:.3f}".replace(".", t["dec"])
        ax.annotate(f"{t[k]} {val}", (ep[-1], m[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=11, color="#0b0b0b")
    # keep labels apart: nudge if close
    ax.set_xlim(1, 100); ax.set_ylim(0, 0.8)
    ax.set_xlabel(t["x"], fontsize=12, color="#52514e"); ax.set_ylabel(t["y"], fontsize=12, color="#52514e")
    ax.set_title(t["title"], fontsize=14, color="#0b0b0b", loc="left", pad=12)
    ax.grid(axis="y", color="#e4e3de", linewidth=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color("#b8b7b0")
    ax.tick_params(colors="#52514e", labelsize=11)
    if t["dec"] == ",":
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
    ax.legend(loc="lower right", frameon=False, fontsize=11)
    fig.text(0.01, 0.01, t["src"], fontsize=9, color="#52514e")
    fig.subplots_adjust(right=0.80, bottom=0.12, top=0.90)
    out = str(Path(__file__).resolve().parents[1] / "dokumentasi/model/gabungan" / f"kurva_map50_95_val_per_epoch_{lang}.png")
    fig.savefig(out, facecolor=fig.get_facecolor()); plt.close(fig)
    print(out)
for k,(ep,m,lo,hi) in data.items(): print(k, "akhir", round(m[-1],4), "maks rerata", round(max(m),4), "epoch", ep[m.index(max(m))])
