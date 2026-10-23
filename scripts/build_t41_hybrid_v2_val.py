"""Paired three-seed VAL confirmation and predeclared hybrid_v2 selection."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, stdev


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "runs/val_ablation/hybrid_20261022_multiseed"
NEW = ROOT / "runs/val_ablation/hybrid_v2_20261023"
OUT = ROOT / "analisis_performa/tabel"
SEEDS = (42, 1337, 2025)


def load(method: str, seed: int) -> tuple[Path, dict]:
    if method == "hybrid_v2_s2":
        path = NEW / f"yolo11_tiny_hybrid_v2_s2_seed{seed}_val.json"
    else:
        path = BASELINE / f"{method}_seed{seed}_val.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    csv_path = OUT / "T41_konfirmasi_hybrid_v2_val.csv"
    md_path = OUT / "T41_konfirmasi_hybrid_v2_val.md"
    if csv_path.exists() or md_path.exists():
        raise FileExistsError("Refusing to overwrite T41")
    methods = ("supervised", "hybrid_full", "hybrid_v2_s2")
    data = {method: {seed: load(method, seed) for seed in SEEDS} for method in methods}
    reference = data["hybrid_full"][42][1]
    rows: list[dict[str, object]] = []
    for method in methods:
        for seed in SEEDS:
            path, value = data[method][seed]
            if value["images"] != reference["images"] or value["settings"] != reference["settings"] or value["val_split_fingerprint_sha256"] != reference["val_split_fingerprint_sha256"]:
                raise RuntimeError(f"VAL inventory/settings/fingerprint mismatch: {method}, {seed}")
            metrics = value["validator_metrics"]
            fixed = value["fixed_confidence_metrics"]
            rows.append({
                "method": method, "seed": seed,
                "map50": metrics["metrics/mAP50(B)"], "map50_95": metrics["metrics/mAP50-95(B)"],
                "precision_conf025": fixed["precision_macro"],
                "recall_conf025": fixed["recall_macro"], "f1_conf025": fixed["F1_macro"],
                "f1_class_mean_conf025": mean(value["per_class"][c]["F1_conf025"] for c in ("ball", "gawang", "robot")),
                "ball_ap50_95": value["per_class"]["ball"]["AP50_95"],
                "gawang_ap50_95": value["per_class"]["gawang"]["AP50_95"],
                "robot_ap50_95": value["per_class"]["robot"]["AP50_95"],
                "checkpoint_sha256": value["checkpoint_sha256"], "val_json": str(path),
            })
    grouped = {method: [item for item in rows if item["method"] == method] for method in methods}
    summary = {}
    for method in methods:
        subset = grouped[method]
        summary[method] = {
            "map_mean": mean(item["map50_95"] for item in subset),
            "map_sd": stdev(item["map50_95"] for item in subset),
            "f1_mean": mean(item["f1_conf025"] for item in subset),
            "f1_sd": stdev(item["f1_conf025"] for item in subset),
        }
    hybrid = summary["hybrid_full"]
    candidate = summary["hybrid_v2_s2"]
    map_diffs = [grouped["hybrid_v2_s2"][i]["map50_95"] - grouped["hybrid_full"][i]["map50_95"] for i in range(3)]
    f1_diffs = [grouped["hybrid_v2_s2"][i]["f1_conf025"] - grouped["hybrid_full"][i]["f1_conf025"] for i in range(3)]
    criterion1 = candidate["map_mean"] >= hybrid["map_mean"] - 0.002
    f1_branch = candidate["f1_mean"] >= hybrid["f1_mean"] + 0.005
    map_branch = candidate["map_mean"] >= hybrid["map_mean"] + 0.004
    criterion2 = f1_branch or map_branch
    criterion3 = (sum(delta > 0 for delta in f1_diffs) >= 2 if f1_branch else False) or (sum(delta > 0 for delta in map_diffs) >= 2 if map_branch else False)
    criterion4 = all(grouped["hybrid_v2_s2"][i]["map50_95"] > grouped["supervised"][i]["map50_95"] for i in range(3))
    accepted = criterion1 and criterion2 and criterion3 and criterion4
    with csv_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# T41: konfirmasi KD hibrida v2 S2 pada VAL tiga seed", "",
        "Perbandingan berpasangan memakai seed 42, 1337, 2025 dan split VAL identik. Pemilihan ini belum merupakan uji pada data independen; TEST lama sudah diketahui saat v2 dirancang.", "",
        "| Metode | mAP50-95 rerata ± SD | F1@0,25 rerata ± SD |", "| --- | ---: | ---: |",
    ]
    for method in methods:
        value = summary[method]
        lines.append(f"| {method} | {value['map_mean']:.4f} ± {value['map_sd']:.4f} | {value['f1_mean']:.4f} ± {value['f1_sd']:.4f} |")
    lines += [
        "", f"Selisih S2 − Hybrid full per seed untuk mAP50-95: {', '.join(f'{x:+.4f}' for x in map_diffs)}.",
        f"Selisih S2 − Hybrid full per seed untuk F1@0,25: {', '.join(f'{x:+.4f}' for x in f1_diffs)}.", "",
        "## Aturan seleksi terkunci", "",
        f"1. mAP rerata S2 tidak turun lebih dari 0,002: **{'lulus' if criterion1 else 'gagal'}**.",
        f"2. F1 naik minimal 0,005 atau mAP naik minimal 0,004: **{'lulus' if criterion2 else 'gagal'}**.",
        f"3. Metrik yang memenuhi syarat 2 membaik pada minimal dua seed: **{'lulus' if criterion3 else 'gagal'}**.",
        f"4. mAP S2 melebihi Supervised pada ketiga seed: **{'lulus' if criterion4 else 'gagal'}**.",
        "", f"**Keputusan menurut aturan VAL: {'S2 layak menggantikan Hybrid full sebagai model KD' if accepted else 'Hybrid full tetap model KD utama; S2 dilaporkan sebagai ablasi'}**.",
        "Keputusan operasional dan model OP3 hanya berubah setelah dicatat di dokumen keputusan. Rincian per seed dan kelas ada di [CSV](T41_konfirmasi_hybrid_v2_val.csv).", "",
    ]
    with md_path.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    print(md_path)


if __name__ == "__main__":
    main()
