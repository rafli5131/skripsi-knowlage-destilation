"""Build T04 from completed pure_v4 and pure_weighted VAL evaluations."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

try:
    from .evaluate_val_ablation import BASELINES, OUT, PILOT, ROOT
except ImportError:
    from evaluate_val_ablation import BASELINES, OUT, PILOT, ROOT


TABLE = ROOT / "analisis_performa/tabel/T04_ablasi_kd_val.csv"
PER_CLASS = ROOT / "analisis_performa/tabel/T04_ablasi_kd_val_per_kelas.csv"
MANIFEST = ROOT / "analisis_performa/lab_server/manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def best_epoch(path: Path) -> int:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"Training history is empty: {path}")
    key = "metrics/mAP50-95(B)"
    return int(float(max(rows, key=lambda row: float(row[key]))["epoch"]))


def main() -> None:
    rows = []
    class_rows = []
    sources = {}
    fingerprint = None
    for label in (*BASELINES, PILOT):
        summary_path = OUT / f"{label}_val.json"
        result = json.loads(summary_path.read_text(encoding="utf-8"))
        manifest_path = Path(result["training_manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["status"] != "complete" or result["training_manifest_sha256"] != sha256(manifest_path):
            raise RuntimeError(f"Incomplete or changed training provenance: {label}")
        if fingerprint is None:
            fingerprint = result["val_split_fingerprint_sha256"]
        if result["val_split_fingerprint_sha256"] != fingerprint or result["images"] != 1213:
            raise RuntimeError(f"VAL split differs: {label}")
        training_dir = Path(manifest["output_dir"])
        history = training_dir / "results.csv"
        distill = manifest["distillation"]
        val = result["validator_metrics"]
        fixed = result["fixed_confidence_metrics"]
        by_class = result["per_class"]
        if set(by_class) != {"ball", "gawang", "robot"}:
            raise RuntimeError(f"Missing class metrics: {label}")
        source = summary_path.relative_to(ROOT).as_posix()
        for name in ("ball", "gawang", "robot"):
            item = by_class[name]
            class_rows.append({
                "model": label, "seed": manifest["seed"], "mode": result["training_mode"],
                "class": name, "ground_truth_count": item["ground_truth_count"],
                "val_AP50": item["AP50"], "val_AP50_95": item["AP50_95"],
                "val_precision_conf025": item["precision_conf025"],
                "val_recall_conf025": item["recall_conf025"],
                "val_F1_conf025": item["F1_conf025"], "source_run": source,
            })
        rows.append({
            "model": label, "seed": manifest["seed"],
            "mode": result["training_mode"],
            "feature_weight": distill["feature_weight"],
            "box_weight": distill["box_weight"],
            "class_weight": distill["class_weight"],
            "temperature": distill["class_temperature"],
            "best_epoch": best_epoch(history),
            "val_mAP50": val["metrics/mAP50(B)"],
            "val_mAP50_95": val["metrics/mAP50-95(B)"],
            "val_precision_conf025": fixed["precision_macro"],
            "val_recall_conf025": fixed["recall_macro"],
            "val_F1_conf025": fixed["F1_macro"],
            "gawang_recall_conf025": by_class["gawang"]["recall_conf025"],
            "source_run": source,
        })
        for path in (summary_path, manifest_path, history):
            sources[path.relative_to(ROOT).as_posix()] = sha256(path)
    fields = list(rows[0])
    with TABLE.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with PER_CLASS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(class_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(class_rows)
    lines = [
        "# T04. ablasi KD pada VAL", "",
        "Status: Lengkap untuk pilot satu seed; `pure_v4` tiga seed dan `pure_weighted` seed 42.", "",
        "Seluruh checkpoint terbaik dievaluasi ulang pada 1.213 gambar VAL resmi dengan FP32, imgsz 640,",
        "confidence floor 0,001, dan NMS IoU 0,7. AP memakai validator Ultralytics; P/R/F1 memakai",
        "confidence tetap >0,25 dan matching IoU 0,50, dirata-ratakan makro atas tiga kelas.",
        "F1 keseluruhan adalah harmonic mean dari precision makro dan recall makro,",
        "mengikuti evaluator TEST. Metrik tiap kelas ada pada",
        "[T04 per kelas](T04_ablasi_kd_val_per_kelas.md).",
        "Pemilihan kandidat hanya memakai VAL; TEST tidak dipakai dalam tabel ini.", "",
        "| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        values = [f"{value:.4f}".replace(".", ",") if isinstance(value, float) else str(value)
                  for value in row.values()]
        lines.append("| " + " | ".join(values) + " |")
    baseline = next(row for row in rows if row["model"] == "kd_seed42")
    candidate = next(row for row in rows if row["model"] == PILOT)
    delta_map = candidate["val_mAP50_95"] - baseline["val_mAP50_95"]
    delta_f1 = candidate["val_F1_conf025"] - baseline["val_F1_conf025"]
    delta_precision = candidate["val_precision_conf025"] - baseline["val_precision_conf025"]
    delta_gawang = candidate["gawang_recall_conf025"] - baseline["gawang_recall_conf025"]
    lines.extend([
        "", f"Perubahan pilot terhadap `pure_v4` seed 42: mAP50–95 {delta_map:+.4f}, "
        f"F1 pada confidence 0,25 {delta_f1:+.4f} (skala 0–1).",
        f"Recall `gawang` berubah {delta_gawang:+.4f}, tetapi precision makro berubah "
        f"{delta_precision:+.4f} pada confidence yang sama. Menurut kriteria mAP50–95 VAL "
        "yang ditetapkan sebelum pilot, `pure_v4` tetap model utama.",
        "Perbandingan satu seed ini bersifat eksploratif. Angka ini adalah akurasi VAL",
        "Advance Vision, bukan akurasi kamera OP3. Model utama tiga seed dan hasil",
        "TEST historis tidak diubah oleh pilot ini.", "",
    ])
    TABLE.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    class_lines = [
        "# T04. ablasi KD pada VAL per kelas", "",
        "Rincian tiga kelas untuk empat checkpoint pada T04. Precision, recall, dan F1",
        "memakai confidence >0,25 dan IoU 0,50; AP memakai confidence floor 0,001",
        "dan NMS IoU 0,7. Seluruh angka berasal dari 1.213 gambar VAL resmi.", "",
        "| " + " | ".join(class_rows[0]) + " |",
        "| " + " | ".join("---" for _ in class_rows[0]) + " |",
    ]
    for row in class_rows:
        values = [f"{value:.4f}".replace(".", ",") if isinstance(value, float) else str(value)
                  for value in row.values()]
        class_lines.append("| " + " | ".join(values) + " |")
    PER_CLASS.with_suffix(".md").write_text("\n".join(class_lines) + "\n", encoding="utf-8")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["sources_sha256"].update(sources)
    for script in (Path(__file__), ROOT / "scripts/evaluate_val_ablation.py", ROOT / "scripts/kd_losses.py"):
        manifest["sources_sha256"][script.relative_to(ROOT).as_posix()] = sha256(script)
    for path in (TABLE, TABLE.with_suffix(".md"), PER_CLASS, PER_CLASS.with_suffix(".md")):
        manifest["outputs_sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
    manifest["pure_weighted_pilot_added_on"] = "2026-10-20"
    manifest["scope"] = (
        "Curated lab/server T01-T14 from historical locked artifacts and VAL diagnosis, "
        "representative server sweeps, plus a new 100-epoch pure_weighted seed-42 "
        "training pilot and four-checkpoint VAL-only T04 ablation; no new TEST evaluation or robot operation"
    )
    manifest["notes"] = list(dict.fromkeys(manifest["notes"]))
    note = (
        "T04 was replaced with a four-checkpoint VAL-only ablation; pure_weighted has "
        "one pilot seed and is not the main three-seed model."
    )
    if note not in manifest["notes"]:
        manifest["notes"].append(note)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {TABLE}; delta VAL mAP50-95={delta_map:+.4f}, F1={delta_f1:+.4f}")


if __name__ == "__main__":
    main()
