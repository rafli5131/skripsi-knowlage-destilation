"""Continue the predeclared hybrid_v2 VAL screen, preserving every old run."""

from __future__ import annotations

import csv
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    from .train_kd import sha256_file
except ImportError:
    from train_kd import sha256_file


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "runs/kd_hybrid_v2"
EVAL = ROOT / "runs/val_ablation/hybrid_v2_20261023"
OUT = ROOT / "analisis_performa/tabel"
PYTHON = "/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python"
STATUS = PROJECT / "screen_s4_s8_status.jsonl"
BASELINE = ROOT / "runs/val_ablation/hybrid_20261023_phase0_reproduction/hybrid_full_seed42_val.json"


def record(event: str, **details: object) -> None:
    with STATUS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": event, "time_utc": datetime.now(timezone.utc).isoformat(), **details}, sort_keys=True) + "\n")


def val_path(stage: str) -> Path:
    return EVAL / f"yolo11_tiny_hybrid_v2_{stage}_seed42_val.json"


def load_val(stage: str) -> dict:
    return json.loads((BASELINE if stage == "baseline" else val_path(stage)).read_text(encoding="utf-8"))


def selected(candidate: dict, best: dict) -> tuple[bool, float, float]:
    delta_map = candidate["validator_metrics"]["metrics/mAP50-95(B)"] - best["validator_metrics"]["metrics/mAP50-95(B)"]
    delta_f1 = candidate["fixed_confidence_metrics"]["F1_macro"] - best["fixed_confidence_metrics"]["F1_macro"]
    return delta_map >= 0.004 or (abs(delta_map) < 0.004 and delta_f1 >= 0.005), delta_map, delta_f1


def config_path(stage: str) -> Path:
    return ROOT / f"configs/kd_hybrid_v2_{stage}.yaml"


def new_config(stage: str, parent: str) -> Path:
    source = config_path(parent)
    config = yaml.safe_load(source.read_text(encoding="utf-8"))
    config["run"]["name"] = f"yolo11_tiny_hybrid_v2_{stage}_seed42"
    if stage == "s5":
        config["distillation"]["temperature"] = 1.0
    elif stage == "s6":
        config["distillation"]["temperature"] = 4.0
    elif stage == "s7":
        config["distillation"]["box_weight"] = 0.5
        config["distillation"]["class_weight"] = 0.5
    elif stage == "s8":
        config["distillation"]["box_weight"] = 2.0
        config["distillation"]["class_weight"] = 2.0
    else:
        raise ValueError(f"Unexpected adaptive stage: {stage}")
    path = config_path(stage)
    with path.open("x", encoding="utf-8") as stream:
        yaml.safe_dump(config, stream, sort_keys=False)
    return path


def run_stage(stage: str, env: dict[str, str]) -> dict:
    run = PROJECT / f"yolo11_tiny_hybrid_v2_{stage}_seed42"
    if run.exists() or (PROJECT / f".{run.name}.manifest.json").exists():
        raise FileExistsError(f"Refusing to overwrite {stage} run")
    path = config_path(stage)
    record("training_started", stage=stage, config=str(path), config_sha256=sha256_file(path))
    log = PROJECT / f"{stage}_train.log"
    with log.open("x", encoding="utf-8") as stream:
        subprocess.run([PYTHON, str(ROOT / "scripts/train_kd.py"), "--config", str(path)], cwd=ROOT, env=env,
                       stdout=stream, stderr=subprocess.STDOUT, check=True)
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or manifest["training_script_sha256"] != source_hash:
        raise RuntimeError(f"{stage}: training manifest failed or source changed")
    record("training_complete", stage=stage, checkpoint=manifest["student_best_checkpoint"])
    record("evaluation_started", stage=stage)
    log = EVAL / f"{stage}_eval.log"
    with log.open("x", encoding="utf-8") as stream:
        subprocess.run([PYTHON, str(ROOT / "scripts/evaluate_hybrid_v2_val.py"), "--run-dir", str(run),
                        "--output-dir", str(EVAL)], cwd=ROOT, env=env,
                       stdout=stream, stderr=subprocess.STDOUT, check=True)
    result = load_val(stage)
    record("evaluation_complete", stage=stage, result=str(val_path(stage)))
    return result


def write_full_table(rows: list[dict[str, object]], best_stage: str) -> None:
    csv_path = OUT / "T40_penyaringan_hybrid_v2_val_s1_s8.csv"
    md_path = OUT / "T40_penyaringan_hybrid_v2_val_s1_s8.md"
    if csv_path.exists() or md_path.exists():
        raise FileExistsError("Refusing to overwrite S1-S8 table")
    with csv_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# T40: penyaringan KD hibrida v2 pada VAL, S1–S8", "",
             "Satu seed (42), bersifat eksploratif. TEST dan T34 OP3 tidak dipakai untuk pemilihan.",
             f"Aturan: [protokol](../../docs/PROTOKOL_HYBRID_V2_2026-10-23.md). Kandidat terbaik: **{best_stage}**.", "",
             "| Tahap | mAP50-95 | F1@0,25 | Terpilih saat tahap itu? |",
             "| --- | ---: | ---: | --- |"]
    for item in rows:
        lines.append(f"| {item['stage']} | {item['map50_95']:.4f} | {item['f1_conf025']:.4f} | {item['selected_so_far']} |")
    lines += ["", "Rincian per kelas dan hash checkpoint tersedia di [CSV](T40_penyaringan_hybrid_v2_val_s1_s8.csv).", ""]
    with md_path.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines))
    record("full_table_complete", csv=str(csv_path), markdown=str(md_path), best_stage=best_stage)


def make_row(stage: str, result: dict, accepted: bool, reference: str, delta_map: float, delta_f1: float) -> dict[str, object]:
    return {
        "stage": stage, "seed": 42,
        "map50": result["validator_metrics"]["metrics/mAP50(B)"],
        "map50_95": result["validator_metrics"]["metrics/mAP50-95(B)"],
        "precision_conf025": result["fixed_confidence_metrics"]["precision_macro"],
        "recall_conf025": result["fixed_confidence_metrics"]["recall_macro"],
        "f1_conf025": result["fixed_confidence_metrics"]["F1_macro"],
        "f1_class_mean_conf025": sum(result["per_class"][c]["F1_conf025"] for c in ("ball", "gawang", "robot")) / 3,
        "ball_ap50_95": result["per_class"]["ball"]["AP50_95"],
        "gawang_ap50_95": result["per_class"]["gawang"]["AP50_95"],
        "robot_ap50_95": result["per_class"]["robot"]["AP50_95"],
        "checkpoint_sha256": result["checkpoint_sha256"],
        "val_json": str(BASELINE if stage == "baseline" else val_path(stage)),
        "selected_so_far": "yes" if accepted else "no",
        "compared_to": reference, "delta_map50_95": delta_map, "delta_f1_conf025": delta_f1,
    }


def main() -> None:
    global source_hash
    if STATUS.exists():
        raise FileExistsError("S4-S8 driver already started")
    if not (PROJECT / "t40_finalizer_status.json").is_file():
        raise RuntimeError("S1-S3 and T40 must finish first")
    source_hash = sha256_file(ROOT / "scripts/train_kd.py")
    first = json.loads((PROJECT / "yolo11_tiny_hybrid_v2_s1_seed42/manifest.json").read_text(encoding="utf-8"))
    if first["training_script_sha256"] != source_hash:
        raise RuntimeError("Training source changed since S1; audit before continuing")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    record("driver_started", stages=["s4", "s5", "s6", "s7", "s8"], training_script_sha256=source_hash)
    try:
        baseline = load_val("baseline")
        best_stage, best_result = "baseline", baseline
        rows = [make_row("baseline", baseline, True, "", 0.0, 0.0)]
        for stage in ("s1", "s2", "s3"):
            result = load_val(stage)
            accepted, delta_map, delta_f1 = selected(result, best_result)
            rows.append(make_row(stage, result, accepted, best_stage, delta_map, delta_f1))
            if accepted:
                best_stage, best_result = stage, result
        if best_stage != "s2":
            raise RuntimeError(f"Frozen S4 configuration expects S2 as parent, found {best_stage}")
        expected_s4 = yaml.safe_load(config_path("s2").read_text(encoding="utf-8"))
        expected_s4["run"]["name"] = "yolo11_tiny_hybrid_v2_s4_seed42"
        expected_s4["distillation"]["class_kd_weighting"] = "floor"
        if yaml.safe_load(config_path("s4").read_text(encoding="utf-8")) != expected_s4:
            raise RuntimeError("S4 configuration differs from the frozen grid")
        for stage in ("s4", "s5", "s6", "s7", "s8"):
            if stage != "s4":
                new_config(stage, best_stage)
            result = run_stage(stage, env)
            if result["images"] != baseline["images"] or result["settings"] != baseline["settings"] or result["val_split_fingerprint_sha256"] != baseline["val_split_fingerprint_sha256"]:
                raise RuntimeError(f"{stage}: VAL inventory, settings, or fingerprint changed")
            accepted, delta_map, delta_f1 = selected(result, best_result)
            record("selection", stage=stage, compared_to=best_stage, accepted=accepted,
                   delta_map50_95=delta_map, delta_f1_conf025=delta_f1)
            rows.append(make_row(stage, result, accepted, best_stage, delta_map, delta_f1))
            if accepted:
                best_stage, best_result = stage, result
        write_full_table(rows, best_stage)
        record("screen_s1_s8_complete", best_stage=best_stage)
    except BaseException as error:
        record("driver_failed", error=f"{type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    main()
