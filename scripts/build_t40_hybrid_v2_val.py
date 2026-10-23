"""Summarize the locked S1-S3 VAL screen without modifying evaluation results."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "runs/val_ablation/hybrid_20261023_phase0_reproduction/hybrid_full_seed42_val.json"
SCREEN = ROOT / "runs/val_ablation/hybrid_v2_20261023"
OUT = ROOT / "analisis_performa/tabel"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def row(stage: str, value: dict, selected: bool, reason: str) -> dict[str, str | float]:
    fixed = value["fixed_confidence_metrics"]
    val = value["validator_metrics"]
    per_class = value["per_class"]
    return {
        "stage": stage, "seed": 42,
        "map50": val["metrics/mAP50(B)"], "map50_95": val["metrics/mAP50-95(B)"],
        "precision_conf025": fixed["precision_macro"],
        "recall_conf025": fixed["recall_macro"], "f1_conf025": fixed["F1_macro"],
        "f1_class_mean_conf025": sum(per_class[c]["F1_conf025"] for c in ("ball", "gawang", "robot")) / 3,
        "ball_ap50_95": per_class["ball"]["AP50_95"],
        "gawang_ap50_95": per_class["gawang"]["AP50_95"],
        "robot_ap50_95": per_class["robot"]["AP50_95"],
        "checkpoint_sha256": value["checkpoint_sha256"],
        "val_json": str((SCREEN / f"yolo11_tiny_hybrid_v2_{stage}_seed42_val.json") if stage != "baseline" else BASELINE),
        "selected_so_far": "yes" if selected else "no", "selection_reason": reason,
    }


def main() -> None:
    csv_path = OUT / "T40_penyaringan_hybrid_v2_val.csv"
    md_path = OUT / "T40_penyaringan_hybrid_v2_val.md"
    if csv_path.exists() or md_path.exists():
        raise FileExistsError("Refusing to overwrite T40")
    reference = load(BASELINE)
    if reference["images"] != 1213:
        raise RuntimeError("Baseline does not cover the locked 1213 VAL images")
    best = reference
    best_name = "baseline"
    rows = [row("baseline", reference, True, "acuan Hybrid full seed 42")]
    for stage in ("s1", "s2", "s3"):
        path = SCREEN / f"yolo11_tiny_hybrid_v2_{stage}_seed42_val.json"
        candidate = load(path)
        if candidate["images"] != reference["images"] or candidate["val_split_fingerprint_sha256"] != reference["val_split_fingerprint_sha256"]:
            raise RuntimeError(f"VAL inventory or fingerprint differs for {stage}")
        if candidate["settings"] != reference["settings"]:
            raise RuntimeError(f"VAL evaluation settings differ for {stage}")
        delta_map = candidate["validator_metrics"]["metrics/mAP50-95(B)"] - best["validator_metrics"]["metrics/mAP50-95(B)"]
        delta_f1 = candidate["fixed_confidence_metrics"]["F1_macro"] - best["fixed_confidence_metrics"]["F1_macro"]
        accept = delta_map >= 0.004 or (abs(delta_map) < 0.004 and delta_f1 >= 0.005)
        reason = f"vs {best_name}: delta mAP50-95={delta_map:+.6f}; delta F1@0,25={delta_f1:+.6f}"
        if accept:
            best, best_name = candidate, stage
        rows.append(row(stage, candidate, accept, reason))
    OUT.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# T40: penyaringan awal KD hibrida v2 pada VAL",
        "", "Hanya seed 42. Pemilihan bersifat eksploratif; TEST dan T34 OP3 tidak dipakai.",
        f"Aturan terkunci: [protokol](../../docs/PROTOKOL_HYBRID_V2_2026-10-23.md). Konfigurasi terbaik setelah S3: **{best_name}**.",
        "", "| Tahap | mAP50-95 | F1@0,25 | F1 rerata kelas | Terpilih saat tahap itu? |", "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in rows:
        lines.append(f"| {item['stage']} | {item['map50_95']:.4f} | {item['f1_conf025']:.4f} | {item['f1_class_mean_conf025']:.4f} | {item['selected_so_far']} |")
    lines += ["", "Nilai per kelas, precision, recall, SHA-256 checkpoint, dan path JSON sumber ada pada [CSV](T40_penyaringan_hybrid_v2_val.csv).", ""]
    with md_path.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    print(csv_path)
    print(md_path)


if __name__ == "__main__":
    main()
