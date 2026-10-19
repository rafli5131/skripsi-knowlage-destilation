#!/usr/bin/env python3
"""Buat tabel awal analisis performa dengan pemeriksaan hash sumber."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analisis_performa"
ANALYSIS = ROOT / "artifacts/thesis_analysis_final_corrected"
ANALYSIS_MANIFEST = ANALYSIS / "analysis_manifest.json"
TEST_MANIFEST = ROOT / "runs/final_test/pure_kd_official_split_locked_retry1/manifest.json"
BENCHMARK = ROOT / "runs/benchmarks/pure_kd_final_inference.json"
MODEL_REGISTRY = ROOT / "configs/model_registry.yaml"
OP3_DIR = ROOT / "runs/op3_pytorch"
CLASS_NAMES = {"ball": 0, "gawang": 1, "robot": 2}

STATUSES = {
    1: "Lengkap dari artefak historis; bukan validasi kamera OP3.",
    2: "Lengkap dari manifest dan args.yaml run yang sudah ada.",
    3: "Lengkap dari results.csv run yang sudah ada.",
    4: "Belum diukur; belum ada pilot kandidat KD baru di VAL.",
    5: "Sebagian; CI bootstrap tersedia per model, belum untuk rerata lintas seed.",
    6: "Lengkap dari hasil TEST terkunci yang sudah ada.",
    7: "Lengkap untuk selisih KD-supervised; perbandingan teacher diturunkan dari tabel sumber.",
    8: "Belum diukur.", 9: "Belum diukur.", 10: "Belum diukur.", 11: "Belum diukur.",
    12: "Belum diukur.", 13: "Belum diukur.", 14: "Belum diukur.",
    15: "Sebagian; spesifikasi perangkat berasal dari catatan historis dan input operator.",
    16: "Belum diukur pada CPU OP3 dengan frame tetap.",
    17: "Belum diukur.",
    18: "Sebagian; tiga sesi historis, belum ada run tracking dan belum semua kondisi terverifikasi.",
    19: "Belum diukur; sesi walking belum tersedia.", 20: "Belum diukur.", 21: "Belum diukur.",
    22: "Sebagian; log detektor lama bukan probe laju topic kamera.",
    23: "Belum diukur sesuai protokol frame tetap.", 24: "Belum diukur.",
    25: "Belum lengkap; log historis tidak menyimpan per kelas atau ID tracking.",
    26: "Belum diukur; menunggu hasil runtime OP3 dengan protokol terkunci.",
    27: "Belum diukur; belum ada set frame kamera OP3 berlabel.",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def verify_source_hashes() -> dict[str, str]:
    """Cocokkan tabel, benchmark, dan manifest evaluasi dengan hash sumbernya."""
    analysis_manifest = read_json(ANALYSIS_MANIFEST)
    source_paths: dict[Path, str] = {}
    for item in analysis_manifest["outputs"].values():
        path = Path(item["path"]).resolve()
        source_paths[path] = str(item["sha256"])
    for key, path in (("test_manifest_sha256", TEST_MANIFEST), ("benchmark_sha256", BENCHMARK)):
        source_paths[path.resolve()] = str(analysis_manifest[key])

    for path, expected in source_paths.items():
        if not path.is_file():
            raise FileNotFoundError(f"Sumber analisis tidak ditemukan: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(f"Hash sumber berubah: {path}; expected={expected}, actual={actual}")

    manifest_path = OUTPUT / "manifest.json"
    if manifest_path.is_file():
        previous = read_json(manifest_path).get("sources", {})
        for source_text, expected in previous.items():
            source = Path(source_text).resolve()
            if not source.is_file() or sha256_file(source) != expected:
                actual = sha256_file(source) if source.is_file() else "missing"
                raise ValueError(f"Sumber berbeda dari manifest tabel sebelumnya: {source}; expected={expected}, actual={actual}")

    source_paths.update({ANALYSIS_MANIFEST.resolve(): sha256_file(ANALYSIS_MANIFEST), TEST_MANIFEST.resolve(): sha256_file(TEST_MANIFEST), BENCHMARK.resolve(): sha256_file(BENCHMARK), MODEL_REGISTRY.resolve(): sha256_file(MODEL_REGISTRY)})
    for model_path in TEST_MANIFEST.parent.glob("*_metrics.json"):
        source_paths[model_path.resolve()] = sha256_file(model_path)
    import yaml
    registry_document = yaml.safe_load(MODEL_REGISTRY.read_text(encoding="utf-8"))
    registry_models = {**registry_document["models"], **registry_document.get("aliases", {})}
    for name, item in registry_models.items():
        checkpoint = Path(item["checkpoint"]).expanduser()
        checkpoint = checkpoint if checkpoint.is_absolute() else ROOT / checkpoint
        checkpoint = checkpoint.resolve()
        if not checkpoint.is_file():
            raise FileNotFoundError(f"Checkpoint registry {name!r} is missing: {checkpoint}")
        actual = sha256_file(checkpoint)
        if actual != item["sha256"]:
            raise ValueError(f"Checkpoint registry hash mismatch for {name}: expected={item['sha256']}, actual={actual}")
        source_paths[checkpoint] = actual
    for path in sorted(OP3_DIR.glob("20261019T*")):
        if path.is_file():
            source_paths[path.resolve()] = sha256_file(path)

    for group in ("kd", "supervised"):
        for manifest_path in sorted((ROOT / "runs" / group).glob("*/manifest.json")):
            if manifest_path.is_file():
                source_paths[manifest_path.resolve()] = sha256_file(manifest_path)
            results_path = manifest_path.parent / "results.csv"
            if results_path.is_file():
                source_paths[results_path.resolve()] = sha256_file(results_path)
            args_path = manifest_path.parent / "args.yaml"
            if args_path.is_file():
                source_paths[args_path.resolve()] = sha256_file(args_path)
    return {str(path): digest for path, digest in sorted(source_paths.items(), key=lambda item: str(item[0]))}


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def number(value: Any, digits: int = 6) -> str:
    if value is None or value == "":
        return "[BELUM DIUKUR]"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(numeric):
        return "[BELUM DIUKUR]"
    return f"{numeric:.{digits}f}".rstrip("0").rstrip(".")


def mean_sd(values: list[float]) -> tuple[float | None, float | None]:
    return (mean(values), stdev(values) if len(values) > 1 else None) if values else (None, None)


def write_table(code: int, name: str, rows: list[dict[str, Any]], source_note: str) -> dict[str, str]:
    folder = OUTPUT / "tabel"
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"T{code:02d}_{name}"
    if not rows:
        rows = [{"status": "[BELUM DIUKUR]"}]
    fields = list(rows[0])
    csv_path = folder / f"{stem}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    md_path = folder / f"{stem}.md"
    rendered = [[number(row.get(field)) for field in fields] for row in rows]
    lines = [f"# T{code:02d}. {name.replace('_', ' ')}", "", f"Status: {STATUSES[code]}", "", "| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rendered)
    lines.extend(["", f"Sumber: {source_note}", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {str(path.relative_to(ROOT)): sha256_file(path) for path in (csv_path, md_path)}


def build_measured_tables() -> dict[int, dict[str, str]]:
    per_model = read_csv(ANALYSIS / "per_model.csv")
    paired = read_csv(ANALYSIS / "paired_seed_deltas.csv")
    paired_summary = read_csv(ANALYSIS / "paired_summary.csv")
    summary = read_csv(ANALYSIS / "summary_mean_sd.csv")
    test_manifest = read_json(TEST_MANIFEST)
    test_seed42 = read_json(TEST_MANIFEST.parent / "kd_seed42_metrics.json")
    test_metrics = test_seed42["test_metrics"]["per_class"]
    by_name = {row["model"]: row for row in per_model}
    import yaml
    registry = yaml.safe_load(MODEL_REGISTRY.read_text(encoding="utf-8"))["models"]
    outputs: dict[int, dict[str, str]] = {}

    t01 = []
    for row in per_model:
        entry = registry[row["model"]]
        t01.append({"model": row["model"], "method": row["method"], "seed": row["seed"] or "teacher", "parameters_before_fusion [count]": row["parameters"], "parameters_after_fusion [count]": row["parameters_after_validator_fusion"], "GFLOPs @640 [GFLOPs]": row["GFLOPs"], "checkpoint_size [MiB]": row["checkpoint_size_MiB"], "checkpoint_SHA256": row["checkpoint_sha256"], "registry_manifest": entry["manifest"]})
    outputs[1] = write_table(1, "spesifikasi_model", t01, "per_model.csv dan configs/model_registry.yaml")

    t02 = []
    for row in per_model:
        if row["model"] == "teacher_fp32":
            continue
        is_kd = row["model"].startswith("kd_")
        prefix = "kd" if is_kd else "supervised"
        run_dir = ROOT / "runs" / prefix / ("yolo11_tiny_pure_kd_v4_locked_seed42" if row["model"] == "kd_seed42" else f"yolo11_tiny_pure_kd_v4_seed{row['seed']}" if is_kd else f"yolo11_tiny_supervised_seed{row['seed']}" if row["seed"] != "42" else "yolo11_tiny_supervised_seed42_retry1")
        manifest = read_json(run_dir / "manifest.json")
        args = yaml.safe_load((run_dir / "args.yaml").read_text(encoding="utf-8"))
        train = manifest.get("training", {})
        distill = manifest.get("distillation") or {}
        t02.append({"model": row["model"], "seed": row["seed"], "objective": manifest.get("objective", ""), "epochs_configured [epoch]": train.get("epochs"), "epochs_completed [epoch]": len(read_csv(run_dir / "results.csv")), "batch [image/batch]": train.get("batch"), "optimizer": train.get("optimizer"), "lr0": train.get("lr0"), "lrf": train.get("lrf"), "weight_decay": train.get("weight_decay"), "warmup_epochs [epoch]": train.get("warmup_epochs"), "AMP": train.get("amp"), "augmentation": f"mosaic={args.get('mosaic')}; mixup={args.get('mixup')}; copy_paste={args.get('copy_paste')}; close_mosaic={args.get('close_mosaic')}", "KD feature/box/class weight": f"{distill.get('feature_weight')}/{distill.get('box_weight')}/{distill.get('class_weight')}" if is_kd else "not applicable", "KD temperature": distill.get("class_temperature", "not applicable"), "training duration [s]": train.get("duration_seconds", "[BELUM DIUKUR]"), "source run": str(run_dir.relative_to(ROOT))})
    outputs[2] = write_table(2, "resep_pelatihan", t02, "run manifest, args.yaml, dan results.csv")

    t03 = []
    checkpoints = {10, 25, 50, 75, 100}
    for row in per_model:
        if row["model"] == "teacher_fp32":
            continue
        is_kd = row["model"].startswith("kd_")
        run_dir = ROOT / "runs" / ("kd" if is_kd else "supervised") / ("yolo11_tiny_pure_kd_v4_locked_seed42" if row["model"] == "kd_seed42" else f"yolo11_tiny_pure_kd_v4_seed{row['seed']}" if is_kd else f"yolo11_tiny_supervised_seed{row['seed']}" if row["seed"] != "42" else "yolo11_tiny_supervised_seed42_retry1")
        epochs = read_csv(run_dir / "results.csv")
        metric_rows = [(int(float(item["epoch"])), float(item["metrics/mAP50-95(B)" ])) for item in epochs]
        best_epoch, best_map = max(metric_rows, key=lambda pair: (pair[1], -pair[0]))
        record: dict[str, Any] = {"model": row["model"], "seed": row["seed"], "run_sample [run]": 1}
        for epoch in sorted(checkpoints):
            match = next((value for current, value in metric_rows if current == epoch), None)
            record[f"VAL mAP50-95 @ epoch {epoch} [0-1]"] = match
        record.update({"best_epoch [epoch]": best_epoch, "best_VAL_mAP50-95 [0-1]": best_map})
        t03.append(record)
    outputs[3] = write_table(3, "konvergensi", t03, "results.csv pada setiap run final")
    outputs[4] = write_table(4, "ablasi_kd_val", [{"mode": "[BELUM DIUKUR]", "weight": "[BELUM DIUKUR]", "temperature": "[BELUM DIUKUR]", "VAL metrics": "[BELUM DIUKUR]"}], "Pilot Fase D belum dijalankan")

    metric_names = ("test_precision", "test_recall", "test_F1", "test_mAP50", "test_mAP50_95")
    t05 = []
    for method in ("Pure KD", "Supervised student", "Teacher"):
        for metric in metric_names:
            stat = next(item for item in summary if item["method"] == method and item["metric"] == metric)
            representative = by_name["kd_seed42" if method == "Pure KD" else "supervised_seed42" if method == "Supervised student" else "teacher_fp32"]
            ci_label = "teacher" if method == "Teacher" else "seed-42"
            t05.append({"method": method, "metric": metric, "n_models [model]": stat["n"], "mean": stat["mean"], "sample_SD": stat["sample_sd"] or "[not defined for n=1]", "CI95 bootstrap of across-seed mean": "[BELUM DIUKUR]", "CI95 bootstrap per model": f"available in source per_model.csv; {ci_label} range={representative[f'{metric}_ci95_lower']}..{representative[f'{metric}_ci95_upper']}"})
    outputs[5] = write_table(5, "akurasi_test_keseluruhan", t05, "summary_mean_sd.csv, per_model.csv, dan evaluasi TEST terkunci; P/R/F1 pada confidence 0,25 dan IoU 0,5")

    t06 = []
    for method, prefix in (("Pure KD", "kd"), ("Supervised student", "supervised"), ("Teacher", "teacher")):
        selected = [row for row in per_model if row["method"] == method]
        for class_name in CLASS_NAMES:
            metrics = {metric: [float(row[f"test_{class_name}_{metric}"]) for row in selected] for metric in ("mAP50", "mAP50_95", "precision", "recall", "F1")}
            ap95_mean, ap95_sd = mean_sd(metrics["mAP50_95"])
            ap50_mean, ap50_sd = mean_sd(metrics["mAP50"])
            p_mean, p_sd = mean_sd(metrics["precision"])
            r_mean, r_sd = mean_sd(metrics["recall"])
            f_mean, f_sd = mean_sd(metrics["F1"])
            t06.append({"method": method, "class": class_name, "ground_truth_objects [object]": test_metrics[class_name]["ground_truth_count"], "AP50 mean": ap50_mean, "AP50 SD": ap50_sd, "AP50-95 mean": ap95_mean, "AP50-95 SD": ap95_sd, "precision mean": p_mean, "precision SD": p_sd, "recall mean": r_mean, "recall SD": r_sd, "F1 mean": f_mean, "F1 SD": f_sd, "n_models [model]": len(selected)})
    outputs[6] = write_table(6, "akurasi_per_kelas", t06, "per_model.csv dan metrik per kelas dari TEST terkunci; jumlah objek diperiksa pada hasil seed 42")

    t07 = []
    for row in paired:
        t07.append({"seed": row["seed"], "comparison": "KD - supervised", "metric": "mAP50-95", "KD minus supervised [0-1]": row["kd_minus_supervised_test_mAP50_95"], "retention versus teacher [%]": "[BELUM DIUKUR per seed]"})
    for row in paired_summary:
        if row["metric"] in ("test_mAP50_95", "test_precision", "test_recall", "test_F1"):
            t07.append({"seed": "mean ± SD", "comparison": row["comparison"], "metric": row["metric"], "KD minus supervised [0-1]": f"{row['mean_paired_delta']} ± {row['sample_sd']}", "retention versus teacher [%]": "[BELUM DIUKUR]"})
    for row in per_model:
        if row["model"].startswith("kd_"):
            t07.append({"seed": row["seed"], "comparison": "KD - teacher", "metric": "mAP50-95", "KD minus supervised [0-1]": row["test_mAP50_95_delta_vs_teacher"], "retention versus teacher [%]": row["mAP50_95_retention_vs_teacher_percent"]})
    outputs[7] = write_table(7, "selisih_berpasangan", t07, "paired_seed_deltas.csv, paired_summary.csv, dan per_model.csv")

    for code, name in ((8, "akurasi_ukuran_objek"), (9, "analisis_kesalahan"), (10, "matriks_kebingungan"), (11, "sapuan_confidence"), (12, "sapuan_iou_nms"), (13, "sapuan_imgsz"), (14, "kalibrasi_confidence"), (16, "latensi_frame_tetap"), (17, "sapuan_thread"), (19, "servo_idle_vs_walking"), (20, "sumber_daya_startup"), (21, "stabilitas_termal"), (23, "kepatuhan_tenggat"), (24, "pengaruh_preview"), (26, "tradeoff_utama"), (27, "akurasi_frame_kamera_op3")):
        outputs[code] = write_table(code, name, [{"status": "[BELUM DIUKUR]"}], "Belum tersedia pada artefak yang diaudit")

    t15 = [
        {"field": "CPU", "value": "12th Gen Intel Core i5-1240P", "status": "catatan terminal OP3", "source": "informasi terminal operator"},
        {"field": "architecture", "value": "x86_64", "status": "catatan terminal OP3", "source": "informasi terminal operator"},
        {"field": "OS", "value": "Ubuntu 24.04.5 LTS", "status": "catatan terminal OP3", "source": "informasi terminal operator"},
        {"field": "Python", "value": "3.12.3", "status": "catatan terminal OP3", "source": "informasi terminal operator"},
        {"field": "ROS 2", "value": "Jazzy", "status": "catatan terminal OP3", "source": "informasi terminal operator"},
        {"field": "PyTorch / Ultralytics / OpenCV", "value": "2.4.1+cpu / 8.4.130 / 4.11.0", "status": "terekam di sesi kamera lama", "source": "runs/op3_pytorch/*.json"},
        {"field": "camera/topic", "value": "Logitech C920 / /thesis/image_raw", "status": "konfigurasi sesi lama", "source": "runs/op3_pytorch/*.json dan dokumentasi/README.md"},
        {"field": "capture", "value": "640x480 YUYV; 30 FPS diminta", "status": "terekam di dokumentasi sesi", "source": "dokumentasi sesi lama"},
        {"field": "RAM, kernel, governor, mode daya, QoS", "value": "[BELUM DIUKUR]", "status": "tidak tercatat lengkap", "source": "[BELUM DIUKUR]"},
    ]
    outputs[15] = write_table(15, "lingkungan_uji_op3", t15, "JSON tiga sesi lama dan output terminal OP3 yang disampaikan operator")

    t18 = []
    for meta_path in sorted(OP3_DIR.glob("20261019T*.json")):
        metadata = read_json(meta_path)
        run_id = metadata["run_id"]
        csv_path = OP3_DIR / f"{run_id}.csv"
        rows = read_csv(csv_path)
        stamp = [int(row["capture_stamp_ns"]) for row in rows if row.get("capture_stamp_ns", "").isdigit()]
        gaps = [(right - left) / 1e9 for left, right in zip(stamp, stamp[1:])]
        end_to_end = [float(row["end_to_end_ms"]) for row in rows if row.get("end_to_end_ms")]
        cpu = [float(row["process_cpu_percent"]) for row in rows if row.get("process_cpu_percent")]
        rss_mib = [int(row["process_rss_bytes"]) / 1024**2 for row in rows if row.get("process_rss_bytes")]
        detections = [int(row["detection_count"]) for row in rows if row.get("detection_count", "").isdigit()]
        duration = (max(stamp) - min(stamp)) / 1e9 if stamp else None
        fps = (len(stamp) - 1) / duration if duration and len(stamp) > 1 else None
        condition = metadata.get("condition", "unknown")
        condition_note = "label tidak terverifikasi" if run_id == "20261019T080757Z" else "label operator; bukan telemetry"
        t18.append({"run_id": run_id, "condition": condition, "condition_note": condition_note, "processed_frames [frame]": len(rows), "duration_capture [s]": duration, "effective_FPS_all_frames [frame/s]": fps, "warmup_removed": "no; not identifiable in legacy logs", "capture_gap_p50 [ms]": (percentile(gaps, .5) or 0) * 1000 if gaps else None, "capture_gap_p95 [ms]": (percentile(gaps, .95) or 0) * 1000 if gaps else None, "capture_gap_max [s]": max(gaps) if gaps else None, "gaps_over_1s [count]": sum(gap > 1 for gap in gaps), "end_to_end_median [ms]": percentile(end_to_end, .5), "end_to_end_p95 [ms]": percentile(end_to_end, .95), "CPU_median [percent]": percentile(cpu, .5), "RSS_median [MiB]": percentile(rss_mib, .5), "detection_instances [count]": sum(detections), "tracked_IDs": "not logged in this run"})
    outputs[18] = write_table(18, "sesi_live_historis", t18, "runs/op3_pytorch/*.csv dan *.json; tidak termasuk bukti akurasi atau tracking")

    t22 = [{"run_id": row["run_id"], "condition": row["condition"], "camera_topic_rate [Hz]": "[BELUM DIUKUR oleh camera_stream_probe]", "processed_frame_rate [frame/s]": row["effective_FPS_all_frames [frame/s]"], "processed_frames [frame]": row["processed_frames [frame]"], "with_detector": "KD seed 42", "camera_only_comparison": "[BELUM DIUKUR]"} for row in t18]
    outputs[22] = write_table(22, "aliran_kamera", t22, "timestamp frame yang diterima node pada log detektor lama; bukan laju ROS topic")

    outputs[25] = write_table(25, "observasi_deteksi_live", [{"run_id": row["run_id"], "condition": row["condition"], "total_detections [count]": row["detection_instances [count]"], "per_class_counts": "[BELUM DIUKUR]", "confidence_distribution": "[BELUM DIUKUR]", "track_IDs": "not logged in this run"} for row in t18], "CSV lama hanya menyimpan jumlah deteksi total; versi node terbaru menambahkan CSV per kotak")
    return outputs


def write_definitions() -> None:
    definitions = """# Definisi metrik dan batas interpretasi\n\n- **Latensi per tahap**: preprocess, inference, dan postprocess/NMS; total = jumlah ketiga tahap. End-to-end = awal callback gambar sampai keluaran deteksi diterbitkan.\n- **Capture-to-publish** = waktu terbit dikurangi timestamp header kamera hanya jika keduanya memakai clock yang sama. Nilai itu belum tersedia pada log lama.\n- **FPS efektif** = (n - 1) / (t_n - t_1), berdasarkan timestamp frame yang diproses. Tabel sesi lama memakai semua frame karena penanda warm-up belum direkam.\n- **FPS turunan** = 1000 / rerata latensi total (ms); tidak sama dengan FPS stream kamera.\n- **CPU ternormalisasi** = CPU% proses / jumlah logical CPU. Jumlah logical CPU OP3 belum tercatat dalam sesi lama.\n- **Persentil**: interpolasi linear NumPy, sama dengan posisi (n - 1)q.\n- **Kepatuhan tenggat** = proporsi frame dengan latensi <= 33,3 ms dan <= 66,7 ms. Belum ada tabel terukur.\n- **P, R, F1**: dihitung pada IoU 0,5 dan confidence 0,25 untuk evaluasi historis; mAP50-95 dirata-ratakan pada IoU 0,50 sampai 0,95.\n- **mAP/akurasi Advance Vision**: valid untuk evaluasi gambar pada dataset Advance Vision. Angka tidak mengukur akurasi kamera OP3.\n- **Sesi kamera**: jumlah deteksi dan runtime tidak sama dengan precision/recall karena tidak ada anotasi ground truth pada frame kamera.\n- **Tracking**: ID BoT-SORT menghubungkan deteksi lintas frame dan hanya berlaku selama satu proses node. ID tidak menunjukkan kebenaran kelas, dan kestabilan ID belum diukur pada OP3.\n- **Ukuran objek**: kecil < 32^2 piksel; sedang 32^2 sampai 96^2; besar > 96^2 pada citra 640. Tabel per ukuran belum dihasilkan.\n\nPersentase metrik ditampilkan sebagai fraksi 0 sampai 1 pada tabel mesin; format Markdown menggunakan koma desimal. Sel yang belum punya sumber diberi `[BELUM DIUKUR]`.\n"""
    (OUTPUT / "DEFINISI.md").write_text(definitions, encoding="utf-8")


def main() -> int:
    sources = verify_source_hashes()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = build_measured_tables()
    write_definitions()
    statuses = [{"table": f"T{code:02d}", "status": description, "source": "analisis_performa/tabel/Txx_*.csv", "updated": datetime.now(timezone.utc).date().isoformat()} for code, description in sorted(STATUSES.items())]
    lines = ["# Indeks tabel analisis performa", "", "Pembaruan: 2026-10-19. Semua hasil TEST di bawah adalah evaluasi historis dataset Advance Vision dan tidak mengukur akurasi kamera OP3.", "", "| Tabel | Status | Berkas |", "| --- | --- | --- |"]
    for row in statuses:
        code = int(row["table"][1:])
        csv_path = next((OUTPUT / "tabel").glob(f"T{code:02d}_*.csv"))
        md_path = csv_path.with_suffix(".md")
        links = f"[CSV](tabel/{csv_path.name}) · [Markdown](tabel/{md_path.name})"
        lines.append(f"| {row['table']} | {row['status']} | {links} |")
    lines.append("")
    (OUTPUT / "INDEKS.md").write_text("\n".join(lines), encoding="utf-8")
    table_hashes = {**outputs, "analisis_performa/INDEKS.md": sha256_file(OUTPUT / "INDEKS.md"), "analisis_performa/DEFINISI.md": sha256_file(OUTPUT / "DEFINISI.md")}
    payload = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "generator": "scripts/build_performance_tables.py", "generator_sha256": sha256_file(Path(__file__)), "sources": sources, "tables": table_hashes, "notes": ["Historical webcam runs predate tracking IDs.", "Advance Vision TEST metrics are image-level dataset results, not OP3 camera accuracy."]}
    (OUTPUT / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {sum(len(value) for value in outputs.values())} table files in {OUTPUT}")
    print(f"Verified {len(sources)} source file hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
