"""Build T42 from completed, checksum-verified VAL evaluation artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, stdev


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "runs/val_ablation/teacher_yolo11s_t42_20261024"
TABLE = ROOT / "analisis_performa/tabel"
PROJECT = ROOT / "runs/kd_teacher_ablation"
PRIVATE = ROOT / "models_local/teacher_ablation_t42/training"
SEEDS = (42, 1337, 2025)
SUPERVISED = {
    int(row["seed"]): float(row["map50_95"])
    for row in csv.DictReader((TABLE / "T41_konfirmasi_hybrid_v2_val.csv").open(newline="", encoding="utf-8"))
    if row["method"] == "supervised"
}


def read(label: str) -> dict:
    path = EVAL / f"{label}_val.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["images"] != 1213 or payload["model"] != label:
        raise RuntimeError(f"Invalid T42 VAL evidence: {path}")
    return payload


def map_value(payload: dict) -> float:
    return float(payload["validator_metrics"]["metrics/mAP50-95(B)"])


def main() -> None:
    csv_path = TABLE / "T42_ablasi_teacher_yolo11s_val.csv"
    md_path = TABLE / "T42_ablasi_teacher_yolo11s_val.md"
    if csv_path.exists() or md_path.exists():
        raise FileExistsError("T42 already exists; do not overwrite it")
    teacher = {variant: read(f"teacher_yolo11{variant}_seed42") for variant in ("n", "s")}
    students = {(variant, seed): read(f"student_teacher_yolo11{variant}_seed{seed}")
                for variant in ("n", "s") for seed in SEEDS}
    events = [json.loads(line) for line in (PROJECT / "t42_status.jsonl").read_text(encoding="utf-8").splitlines()]
    completed = {event["name"]: event for event in events if event["event"] == "step_finished"}
    rows = []
    for variant in ("n", "s"):
        teacher_map = map_value(teacher[variant])
        teacher_label = f"teacher_yolo11{variant}_seed42"
        teacher_run = "teacher_yolo11n_seed42_retry1" if variant == "n" else teacher_label
        teacher_manifest = json.loads((PRIVATE / teacher_run / "manifest.json").read_text(encoding="utf-8"))
        for seed in SEEDS:
            payload = students[variant, seed]
            student_map = map_value(payload)
            baseline = SUPERVISED[seed]
            denominator = teacher_map - baseline
            student_label = f"student_teacher_yolo11{variant}_seed{seed}"
            student_manifest = json.loads((PROJECT / student_label / "manifest.json").read_text(encoding="utf-8"))
            rows.append({
                "teacher_variant": f"yolo11{variant}", "student_seed": seed,
                "teacher_parameters": teacher_manifest["teacher_parameters"],
                "student_parameters": student_manifest["student_parameters"],
                "teacher_map50_95": teacher_map, "student_map50_95": student_map,
                "student_f1_conf025": payload["fixed_confidence_metrics"]["F1_macro"],
                "supervised_map50_95": baseline,
                "student_minus_supervised": student_map - baseline,
                "recovery_ratio": (student_map - baseline) / denominator if abs(denominator) >= .01 else "",
                "recovery_denominator_small": abs(denominator) < .01,
                "teacher_training_seconds": teacher_manifest["duration_seconds"],
                "teacher_gpu_peak_reserved_mib": teacher_manifest["gpu_peak_reserved_bytes"] / 1048576,
                "student_training_seconds": completed[f"train_{student_label}"]["elapsed_seconds"],
                "student_gpu_peak_sampled_mib": completed[f"train_{student_label}"]["gpu_process_peak_mib"],
                "teacher_checkpoint_sha256": teacher[variant]["checkpoint_sha256"],
                "student_checkpoint_sha256": payload["checkpoint_sha256"],
                "teacher_val_json": str((EVAL / f"teacher_yolo11{variant}_seed42_val.json").relative_to(ROOT)),
                "student_val_json": str((EVAL / f"student_teacher_yolo11{variant}_seed{seed}_val.json").relative_to(ROOT)),
            })
    TABLE.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    n_values = [map_value(students["n", seed]) for seed in SEEDS]
    s_values = [map_value(students["s", seed]) for seed in SEEDS]
    paired = [s - n for s, n in zip(s_values, n_values)]
    lines = [
        "# T42: ablasi kapasitas teacher YOLO11n vs YOLO11s pada VAL",
        "",
        "Kedua teacher dilatih dari bobot COCO resmi dengan data, resep, dan seed 42 yang sama. "
        "Student YOLO11 skala t dilatih dengan Hybrid full dan tiga seed berpasangan. "
        "Hasil ini hanya pada VAL; TEST dan kamera OP3 tidak dipakai.",
        "",
        "| Teacher | mAP50–95 teacher | mAP50–95 student, rerata ± SD |",
        "| --- | ---: | ---: |",
        f"| YOLO11n | {map_value(teacher['n']):.4f} | {mean(n_values):.4f} ± {stdev(n_values):.4f} |",
        f"| YOLO11s | {map_value(teacher['s']):.4f} | {mean(s_values):.4f} ± {stdev(s_values):.4f} |",
        "",
        f"Selisih student berpasangan (teacher s − n): {mean(paired):+.4f} ± {stdev(paired):.4f} "
        f"pada seed {', '.join(map(str, SEEDS))}. Rincian per seed, F1, kontrol supervised, "
        f"dan rasio pemulihan ada di [CSV]({csv_path.name}).",
        "",
        "Teacher YOLO11n pada ablasi ini dilatih ulang; teacher utama lama memiliki provenance resep berbeda. "
        "Hasil ablasi tidak mengganti checkpoint Hybrid full yang dipilih untuk OP3. "
        "Tiga seed memberikan analisis deskriptif, bukan bukti signifikansi statistik. "
        "Puncak GPU teacher berasal dari PyTorch; puncak GPU student disampel dari proses dengan interval 20 detik "
        "sehingga dapat lebih rendah dari puncak sebenarnya.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
