"""VAL NMS/input-size sweeps for representative teacher, KD, and supervised models.

Writes resumable raw JSON per run and curated T12/T13 tables. Uses the locked
VAL inventory, no TEST images, and never trains a model.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import platform
import statistics
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import MethodType

import cv2
import torch
import ultralytics
import yaml
from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG, get_cfg
from ultralytics.data.build import build_dataloader
from ultralytics.models.yolo.detect.val import DetectionValidator
from ultralytics.utils.torch_utils import get_flops

try:
    from .analyze_val_detections import DATA_YAML, ROOT, TABLES, image_matches, registry_models, source_paths, verify_val_bytes
    from .evaluate_locked_test import ReadOnlyTestDataset
    from .model_registry import validate_checkpoint
except ImportError:
    from analyze_val_detections import DATA_YAML, ROOT, TABLES, image_matches, registry_models, source_paths, verify_val_bytes
    from evaluate_locked_test import ReadOnlyTestDataset
    from model_registry import validate_checkpoint


MODELS = ("teacher_fp32", "kd_seed42", "supervised_seed42")
NMSES = (0.30, 0.45, 0.50, 0.60, 0.70)
SIZES = (320, 416, 512, 640)
OUT = ROOT / "runs/val_sweeps/official_split_20261020"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def method(model: str) -> str:
    return "Teacher" if model == "teacher_fp32" else "Pure KD" if model.startswith("kd_") else "Supervised student"


def cpu_name() -> str:
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
        if line.startswith("model name"):
            return line.partition(":")[2].strip()
    return platform.processor() or platform.machine()


def checkpoint(model: str) -> Path:
    path = Path(registry_models()[model]["checkpoint"])
    path = (path if path.is_absolute() else ROOT / path).resolve()
    validate_checkpoint(path, label=model)
    return path


def run_val(model_name: str, imgsz: int, nms_iou: float, expected: set[str], images: Path,
            fingerprint: dict, threads: int) -> dict:
    cp = checkpoint(model_name)
    torch.set_num_threads(threads)
    model = YOLO(str(cp), task="detect").model
    model.to(torch.device("cpu")).float().eval()
    gflops_before_validator_fusion = float(get_flops(model, imgsz=imgsz))
    cfg = get_cfg(DEFAULT_CFG, {
        "task": "detect", "mode": "val", "split": "val", "data": str(DATA_YAML),
        "imgsz": imgsz, "batch": 16, "workers": 0, "device": "cpu", "cache": False,
        "fraction": 1.0, "rect": True, "augment": False, "amp": False,
        "plots": False, "save_json": False, "save_txt": False, "conf": 0.001,
        "iou": nms_iou, "verbose": False, "compile": False,
    })
    dataset = ReadOnlyTestDataset(
        img_path=str(images), imgsz=cfg.imgsz, batch_size=cfg.batch, augment=False,
        hyp=copy.copy(cfg), rect=True, cache=False, single_cls=False,
        stride=max(int(model.stride.max()), 32), pad=0.5, prefix="val: ",
        task="detect", classes=None, data=yaml.safe_load(DATA_YAML.read_text(encoding="utf-8")),
        fraction=1.0, external_cache_path=OUT / f".val_labels_{imgsz}.cache",
    )
    loader = build_dataloader(dataset, batch=cfg.batch, workers=0, shuffle=False,
                              rank=-1, drop_last=False, device=torch.device("cpu"))
    validator = DetectionValidator(loader, save_dir=OUT / model_name, args=copy.copy(cfg))
    seen = set()
    duplicates = Counter()
    original = validator._process_batch

    def capture(self: DetectionValidator, preds: dict, batch: dict) -> dict:
        stats = original(preds, batch)
        name = Path(batch["im_file"]).name
        if name in seen:
            raise RuntimeError(f"Duplicate VAL image: {name}")
        seen.add(name)
        record = {
            "gt_cls": batch["cls"].cpu().numpy().astype(int).tolist(),
            "gt_xyxy": batch["bboxes"].cpu().numpy().tolist(),
            "pred_cls": preds["cls"].cpu().numpy().astype(int).tolist(),
            "pred_conf": preds["conf"].cpu().numpy().tolist(),
            "pred_xyxy": preds["bboxes"].cpu().numpy().tolist(),
        }
        duplicates.update(image_matches(record)[0])
        return stats

    validator._process_batch = MethodType(capture, validator)
    try:
        validator(model=model)
    finally:
        if hasattr(loader, "close"):
            loader.close()
    if seen != expected:
        raise RuntimeError(f"VAL inventory mismatch: {model_name} {imgsz} IoU {nms_iou}: {len(seen)} images")
    metrics = validator.metrics.results_dict
    cls_maps = validator.metrics.box.maps
    row = {
        "model": model_name, "checkpoint": str(cp), "checkpoint_sha256": sha256(cp),
        "val_split_fingerprint_sha256": fingerprint["split_fingerprint_sha256"],
        "settings": {"imgsz": imgsz, "nms_iou": nms_iou, "conf_floor": 0.001,
                     "batch": 16, "threads": threads, "device": "cpu", "rect": True},
        "n_images": len(seen), "metrics": metrics,
        "per_class_map50_95": {name: float(cls_maps[cls]) for cls, name in enumerate(("ball", "gawang", "robot"))},
        "duplicate_count_conf025": duplicates["fp_duplicate_count"],
        "speed_ms_per_image": validator.speed,
        "gflops": gflops_before_validator_fusion,
        "versions": {"python": platform.python_version(), "torch": str(torch.__version__),
                     "ultralytics": ultralytics.__version__},
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return row


def fixed_frame_benchmark(cp: Path, imgsz: int, image: Path, threads: int) -> dict:
    torch.set_num_threads(threads)
    frame = cv2.imread(str(image))
    if frame is None:
        raise RuntimeError(f"Failed to decode VAL image: {image}")
    model = YOLO(str(cp), task="detect")
    def infer() -> None:
        model.predict(source=frame, imgsz=imgsz, batch=1, device="cpu", half=False,
                      conf=0.001, iou=0.7, verbose=False, save=False, plots=False)
    for _ in range(30):
        infer()
    times = []
    for _ in range(100):
        start = time.perf_counter()
        infer()
        times.append((time.perf_counter() - start) * 1000)
    return {"fixed_val_image": str(image), "fixed_val_image_sha256": sha256(image),
            "warmup": 30, "iterations": 100, "latency_median_ms": statistics.median(times),
            "latency_mean_ms": statistics.mean(times), "fps_from_mean": 1000 / statistics.mean(times),
            "timing_scope": "YOLO.predict preprocess + inference + NMS, excludes checkpoint loading and camera"}


def write_csv_and_md(path: Path, rows: list[dict], note: str) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path}")
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = [f"# {path.stem.replace('_', ' ')}", "", note, "", "| " + " | ".join(fields) + " |",
             "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        values = []
        for value in row.values():
            values.append(f"{value:.4f}".replace(".", ",") if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def aggregate() -> None:
    nms_rows = []
    size_rows = []
    sources = {}
    path13 = TABLES / "T13_sapuan_imgsz.csv"
    historical = []
    if path13.exists():
        for old in csv.DictReader(path13.open(encoding="utf-8")):
            if old["benchmark_device"] == "NVIDIA L40":
                historical.append({**old, "source": (
                    "artifacts/thesis_analysis_final_corrected/per_model.csv;"
                    "runs/benchmarks/pure_kd_final_inference.json;"
                    f"runs/val_diagnostics/official_split_20261020/{old['model']}_predictions.json")})
    for name in MODELS:
        for iou in NMSES:
            path = OUT / f"nms_{name}_{iou:.2f}.json"
            row = json.loads(path.read_text(encoding="utf-8"))
            source = path.relative_to(ROOT).as_posix()
            sources[source] = sha256(path)
            metrics = row["metrics"]
            nms_rows.append({"model": name, "split": "val", "nms_iou_threshold": iou,
                             "mAP50": metrics["metrics/mAP50(B)"],
                             "mAP50_95": metrics["metrics/mAP50-95(B)"],
                             "precision": metrics["metrics/precision(B)"],
                             "recall": metrics["metrics/recall(B)"],
                             "duplicate_count": row["duplicate_count_conf025"],
                             "postprocess_ms": row["speed_ms_per_image"]["postprocess"], "source": source})
        for imgsz in SIZES:
            path = OUT / f"imgsz_{name}_{imgsz}.json"
            row = json.loads(path.read_text(encoding="utf-8"))
            source = path.relative_to(ROOT).as_posix()
            sources[source] = sha256(path)
            metrics = row["metrics"]
            fixed = row["fixed_frame_benchmark"]
            size_rows.append({"model": name, "method": method(name), "imgsz_px": imgsz,
                              "split_metric": "VAL", "val_mAP50": metrics["metrics/mAP50(B)"],
                              "val_mAP50_95": metrics["metrics/mAP50-95(B)"],
                              "val_AP50_95_per_class": json.dumps(row["per_class_map50_95"], separators=(",", ":")),
                              "GFLOPs": row["gflops"],
                              "latency_median_ms_server": fixed["latency_median_ms"],
                              "throughput_images_s_server": fixed["fps_from_mean"],
                              "benchmark_device": f"CPU {cpu_name()} 8 threads",
                              "source": source})
    path12 = TABLES / "T12_sapuan_iou_nms.csv"
    write_csv_and_md(path12, nms_rows, "Status: Lengkap untuk tiga model representatif (teacher, KD seed 42, supervised seed 42) pada VAL. Confidence floor 0,001 untuk AP; precision dan recall adalah keluaran validator Ultralytics pada titik F1 internalnya, bukan operating point confidence 0,25. Jumlah duplikat memakai confidence >0,25 dan IoU pencocokan 0,50. Waktu postprocess adalah rerata per gambar dari validator CPU server, bukan latensi OP3. Grid ini bersifat diagnosis VAL; seed 1337/2025 tidak disapu.")
    write_csv_and_md(path13, historical + size_rows, "Status: Lengkap untuk sapuan CPU server pada tiga model representatif (teacher, KD seed 42, supervised seed 42). Tujuh titik dasar 640 pada NVIDIA L40 dipertahankan sebagai hasil historis yang tidak langsung sebanding dengan CPU; AP VAL per kelasnya direkonstruksi dari prediksi VAL terkunci. Semua nilai metrik berasal dari VAL; benchmark CPU memakai satu gambar VAL yang sama, batch 1, FP32, 8 thread, 30 warmup + 100 iterasi. FPS = 1000/rerata latensi; latensi median dilaporkan terpisah. CPU server ini bukan CPU OP3, dan FPS turunan bukan FPS kamera.")
    manifest_path = ROOT / "analisis_performa/lab_server/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources_sha256"].update(sources)
    script = Path(__file__).resolve()
    manifest["sources_sha256"][script.relative_to(ROOT).as_posix()] = sha256(script)
    for path in (path12, path12.with_suffix(".md"), path13, path13.with_suffix(".md")):
        manifest["outputs_sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
    manifest["lab_sweeps_added_on"] = "2026-10-20"
    manifest["scope"] = ("Curated lab/server T01-T14 from locked historical artifacts, seven-checkpoint VAL "
                         "diagnosis, and representative VAL NMS/input-size sweeps on CPU server; "
                         "no new training, TEST rerun, or robot operation")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("all", "nms", "imgsz", "rebenchmark", "aggregate"), default="all")
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    if args.threads < 1:
        raise ValueError("threads must be positive")
    images, expected, fingerprint = source_paths()
    verify_val_bytes(fingerprint)
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    if args.phase in ("all", "nms"):
        jobs += [("nms", name, 640, iou) for name in MODELS for iou in NMSES]
    if args.phase in ("all", "imgsz"):
        jobs += [("imgsz", name, size, 0.7) for name in MODELS for size in SIZES]
    fixed_image = sorted(images.glob("*.jpg"))[0]
    if args.phase == "rebenchmark":
        for name in MODELS:
            for imgsz in SIZES:
                path = OUT / f"imgsz_{name}_{imgsz}.json"
                row = json.loads(path.read_text(encoding="utf-8"))
                if (row["checkpoint_sha256"] != sha256(checkpoint(name))
                        or row["val_split_fingerprint_sha256"] != fingerprint["split_fingerprint_sha256"]):
                    raise RuntimeError(f"Source mismatch: {path}")
                print(f"Quiet CPU benchmark {name} imgsz={imgsz}", flush=True)
                row["gflops"] = float(get_flops(YOLO(str(checkpoint(name)), task="detect").model, imgsz=imgsz))
                row["gflops_method"] = "Ultralytics get_flops before validator Conv-BN fusion, batch 1"
                row["fixed_frame_benchmark"] = fixed_frame_benchmark(checkpoint(name), imgsz, fixed_image, args.threads)
                row["fixed_frame_benchmark"]["measured_after_accuracy_sweeps"] = True
                path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        aggregate()
        return
    for kind, name, imgsz, iou in jobs:
        path = OUT / (f"nms_{name}_{iou:.2f}.json" if kind == "nms" else f"imgsz_{name}_{imgsz}.json")
        if path.exists():
            print(f"Existing {path.name}", flush=True)
            continue
        print(f"Running {kind} {name} imgsz={imgsz} NMS={iou:.2f}", flush=True)
        row = run_val(name, imgsz, iou, expected, images, fingerprint, args.threads)
        if kind == "imgsz":
            row["fixed_frame_benchmark"] = fixed_frame_benchmark(checkpoint(name), imgsz, fixed_image, args.threads)
        path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Saved {path.name}: mAP50-95={row['metrics']['metrics/mAP50-95(B)']:.4f}", flush=True)
    if args.phase in ("all", "aggregate"):
        aggregate()


if __name__ == "__main__":
    main()
