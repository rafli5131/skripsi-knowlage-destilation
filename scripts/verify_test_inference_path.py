#!/usr/bin/env python3
"""Verifikasi jalur inferensi pada split TEST Advance Vision v1.

Skrip ini membandingkan metrik TEST resmi (T05/T30), yang dihitung lewat jalur
``DetectionValidator`` (``model.val``), dengan metrik yang dihitung ulang lewat
jalur ``model.predict``, yaitu jalur yang dipakai node deteksi di robot OP3.

Dua varian prediksi dijalankan untuk setiap checkpoint:

* ``protokol_test``: confidence floor 0,001 dan NMS IoU 0,7, sama dengan
  evaluator TEST resmi. Selisih terhadap angka resmi berasal dari jalur
  (letterbox per gambar vs batch rect, implementasi NMS, perangkat), bukan dari
  ambang. Varian ini menghasilkan mAP50, mAP50-95, serta P/R/F1 pada
  confidence > 0,25 dan IoU 0,5.
* ``robot``: confidence 0,25 dan NMS IoU 0,45, sama dengan runtime OP3 (D4).
  Varian ini hanya menghasilkan P/R/F1 pada IoU 0,5 karena prediksi di bawah
  0,25 sudah dibuang sebelum NMS.

Batas: tidak ada training, tidak ada pemilihan ulang model atau ambang, dan
hasil lama tidak disentuh. TEST sudah pernah dibuka, sehingga hasil ini hanya
pemeriksaan konsistensi metodologi, bukan dasar untuk mengganti model.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import inspect
import json
import math
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
CLASS_NAMES = {0: "ball", 1: "gawang", 2: "robot"}
IOU_THRESHOLDS = np.linspace(0.5, 0.95, 10)
OPERATING_CONFIDENCE = 0.25
MATCH_IOU = 0.5
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VARIANTS = {
    "protokol_test": {"conf": 0.001, "iou": 0.7, "keterangan": "ambang sama dengan evaluator TEST resmi"},
    "robot": {"conf": 0.25, "iou": 0.45, "keterangan": "ambang sama dengan runtime OP3 (D4)"},
}
STUDENT_KEYS = [
    "hybrid_full_seed42", "hybrid_full_seed1337", "hybrid_full_seed2025",
    "supervised_seed42", "supervised_seed1337", "supervised_seed2025",
    "kd_seed42", "kd_seed1337", "kd_seed2025",
]
OFFICIAL_SOURCES = {
    "teacher_fp32": "runs/final_test/pure_kd_official_split_locked_retry1/teacher_fp32_metrics.json",
    "kd_seed42": "runs/final_test/pure_kd_official_split_locked_retry1/kd_seed42_metrics.json",
    "kd_seed1337": "runs/final_test/pure_kd_official_split_locked_retry1/kd_seed1337_metrics.json",
    "kd_seed2025": "runs/final_test/pure_kd_official_split_locked_retry1/kd_seed2025_metrics.json",
    "supervised_seed42": "runs/final_test/hybrid_full_official_split_20261022/supervised_seed42_metrics.json",
    "supervised_seed1337": "runs/final_test/hybrid_full_official_split_20261022/supervised_seed1337_metrics.json",
    "supervised_seed2025": "runs/final_test/hybrid_full_official_split_20261022/supervised_seed2025_metrics.json",
    "hybrid_full_seed42": "runs/final_test/hybrid_full_official_split_20261022/hybrid_full_seed42_metrics.json",
    "hybrid_full_seed1337": "runs/final_test/hybrid_full_official_split_20261022/hybrid_full_seed1337_metrics.json",
    "hybrid_full_seed2025": "runs/final_test/hybrid_full_official_split_20261022/hybrid_full_seed2025_metrics.json",
}
GROUPS = {
    "teacher_fp32": "Teacher YOLO11n",
    "hybrid_full": "KD Hybrid full",
    "supervised": "Supervised",
    "kd": "KD murni",
}
METRICS = ("mAP50", "mAP50-95", "precision", "recall", "F1")


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def parse_args() -> argparse.Namespace:
    stamp = dt.datetime.now().strftime("%Y%m%d")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, help="data.yaml Advance Vision v1 di server")
    parser.add_argument("--test-images", type=Path, help="Folder gambar TEST bila tidak ingin dibaca dari data.yaml")
    parser.add_argument("--teacher", type=Path, help="Checkpoint teacher utama; SHA-256 wajib sama dengan registry")
    parser.add_argument("--models", nargs="+", default=None, help="Kunci registry yang dievaluasi (bawaan: semua)")
    parser.add_argument("--device", default="cpu", help="Perangkat inferensi; bawaan cpu agar mendekati robot")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--registry", type=Path, default=ROOT / "configs/model_registry.yaml")
    parser.add_argument("--fingerprint", type=Path, default=ROOT / "artifacts/advance_vision_dataset_fingerprint.json")
    parser.add_argument("--output", type=Path, default=ROOT / f"analisis_performa/lab_server/verifikasi_jalur_test_{stamp}")
    parser.add_argument("--allow-fingerprint-mismatch", action="store_true",
                        help="Lanjut walau hash TEST berbeda; hasil ditandai tidak sebanding")
    return parser.parse_args()


# ---------------------------------------------------------------- dataset

def resolve_test_dir(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    if args.test_images:
        return args.test_images.expanduser().resolve(), {"source": "--test-images"}
    if not args.data:
        raise VerificationError("Berikan --data atau --test-images")
    from ultralytics.data.utils import check_det_dataset

    try:
        data = check_det_dataset(str(args.data.expanduser().resolve()), autodownload=False)
    except Exception as exc:  # noqa: BLE001
        raise VerificationError(f"data.yaml gagal dibaca Ultralytics ({type(exc).__name__}: {exc}); "
                                "berikan folder gambar TEST lewat --test-images") from exc
    test = data.get("test")
    if not test:
        raise VerificationError("data.yaml tidak memuat entri test")
    if isinstance(test, (list, tuple)):
        if len(test) != 1:
            raise VerificationError("Entri test berisi lebih dari satu sumber; berikan --test-images")
        test = test[0]
    test_dir = Path(test)
    if not test_dir.is_dir():
        raise VerificationError(f"Folder TEST tidak ditemukan: {test_dir}")
    names = data.get("names")
    if isinstance(names, dict):
        names = {int(k): v for k, v in names.items()}
    elif isinstance(names, (list, tuple)):
        names = dict(enumerate(names))
    if names != CLASS_NAMES:
        raise VerificationError(f"Nama kelas data.yaml {names} berbeda dari {CLASS_NAMES}")
    return test_dir, {"source": "data.yaml", "names": names}


def label_path_for(image: Path) -> Path:
    from ultralytics.data.utils import img2label_paths

    return Path(img2label_paths([str(image)])[0])


def verify_fingerprint(images: list[Path], fingerprint_path: Path, allow_mismatch: bool) -> dict[str, Any]:
    fingerprint = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    expected = {item["image"]: item for item in fingerprint["splits"]["test"]["files"]}
    actual_names = {image.name for image in images}
    report: dict[str, Any] = {
        "fingerprint_file": str(fingerprint_path.relative_to(ROOT)) if fingerprint_path.is_relative_to(ROOT) else str(fingerprint_path),
        "fingerprint_file_sha256": sha256(fingerprint_path),
        "expected_images": len(expected),
        "found_images": len(images),
        "missing_images": sorted(set(expected) - actual_names),
        "unexpected_images": sorted(actual_names - set(expected)),
        "image_hash_mismatch": [],
        "label_hash_mismatch": [],
        "missing_labels": [],
    }
    for image in images:
        record = expected.get(image.name)
        if record is None:
            continue
        if sha256(image) != record["image_sha256"]:
            report["image_hash_mismatch"].append(image.name)
        label = label_path_for(image)
        if not label.exists():
            report["missing_labels"].append(label.name)
        elif sha256(label) != record["label_sha256"]:
            report["label_hash_mismatch"].append(label.name)
    problems = sum(len(report[key]) for key in (
        "missing_images", "unexpected_images", "image_hash_mismatch", "label_hash_mismatch", "missing_labels"))
    report["all_match"] = problems == 0
    if problems and not allow_mismatch:
        preview = {key: report[key][:10] for key in (
            "missing_images", "unexpected_images", "image_hash_mismatch", "label_hash_mismatch", "missing_labels")}
        raise VerificationError(
            "TEST di server berbeda dari sidik jari terkunci. Tidak ada berkas hasil yang ditulis.\n"
            + json.dumps(preview, indent=2, ensure_ascii=False))
    return report


def read_labels(label: Path, width: int, height: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Baca label YOLO menjadi kotak xyxy piksel; poligon diubah menjadi kotak pembungkus."""
    classes, boxes, polygons = [], [], 0
    if label.exists():
        for line in label.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if not parts:
                continue
            cls = int(float(parts[0]))
            values = [float(value) for value in parts[1:]]
            if len(values) == 4:
                cx, cy, w, h = values
                x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
            elif len(values) >= 6 and len(values) % 2 == 0:
                polygons += 1
                xs, ys = values[0::2], values[1::2]
                x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            else:
                raise VerificationError(f"Format label tidak dikenal: {label}: {line!r}")
            classes.append(cls)
            boxes.append([x1 * width, y1 * height, x2 * width, y2 * height])
    return (np.asarray(classes, dtype=np.int64),
            np.asarray(boxes, dtype=np.float64).reshape(-1, 4), polygons)


# ---------------------------------------------------------------- metrics

def box_iou(gt: np.ndarray, pred: np.ndarray) -> np.ndarray:
    if gt.size == 0 or pred.size == 0:
        return np.zeros((len(gt), len(pred)))
    lt = np.maximum(gt[:, None, :2], pred[None, :, :2])
    rb = np.minimum(gt[:, None, 2:], pred[None, :, 2:])
    inter = np.clip(rb - lt, 0, None).prod(2)
    area_gt = (gt[:, 2] - gt[:, 0]) * (gt[:, 3] - gt[:, 1])
    area_pred = (pred[:, 2] - pred[:, 0]) * (pred[:, 3] - pred[:, 1])
    return inter / (area_gt[:, None] + area_pred[None, :] - inter + 1e-7)


def match_predictions(pred_cls: np.ndarray, gt_cls: np.ndarray, iou: np.ndarray) -> np.ndarray:
    """Pencocokan sekelas dan serakah berdasarkan IoU, mengikuti aturan validator Ultralytics."""
    correct = np.zeros((len(pred_cls), len(IOU_THRESHOLDS)), dtype=bool)
    if len(pred_cls) == 0 or len(gt_cls) == 0:
        return correct
    iou = iou * (gt_cls[:, None] == pred_cls[None, :])
    for index, threshold in enumerate(IOU_THRESHOLDS):
        matches = np.array(np.nonzero(iou >= threshold)).T
        if matches.shape[0]:
            if matches.shape[0] > 1:
                matches = matches[iou[matches[:, 0], matches[:, 1]].argsort()[::-1]]
                matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
            correct[matches[:, 1].astype(int), index] = True
    return correct


def operating_point(tp: np.ndarray, conf: np.ndarray, pred_cls: np.ndarray, gt_cls: np.ndarray) -> dict[str, Any]:
    match_index = int(np.argmin(np.abs(IOU_THRESHOLDS - MATCH_IOU)))
    per_class = {}
    for class_id, name in CLASS_NAMES.items():
        selected = (pred_cls == class_id) & (conf > OPERATING_CONFIDENCE)
        predictions = int(selected.sum())
        targets = int((gt_cls == class_id).sum())
        true_positive = int(tp[selected, match_index].sum()) if predictions else 0
        precision = true_positive / predictions if predictions else 0.0
        recall = true_positive / targets if targets else 0.0
        f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
        per_class[name] = {"precision": precision, "recall": recall, "F1": f1, "ground_truth_count": targets,
                           "predictions_above_confidence": predictions, "true_positives_at_iou50": true_positive}
    precision = float(np.mean([item["precision"] for item in per_class.values()]))
    recall = float(np.mean([item["recall"] for item in per_class.values()]))
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    overall = {"precision": precision, "recall": recall, "F1": f1,
               "F1_rerata_per_kelas": float(np.mean([item["F1"] for item in per_class.values()]))}
    return {"overall": overall, "per_class": per_class}


def average_precision(tp: np.ndarray, conf: np.ndarray, pred_cls: np.ndarray, gt_cls: np.ndarray) -> dict[str, Any]:
    from ultralytics.utils.metrics import ap_per_class

    result = ap_per_class(tp, conf, pred_cls, gt_cls, plot=False, names=CLASS_NAMES)
    ap, unique_classes = result[5], result[6]
    if ap.ndim != 2 or ap.shape[1] != len(IOU_THRESHOLDS):
        raise VerificationError(f"Bentuk keluaran ap_per_class tidak terduga: {ap.shape}")
    per_class = {CLASS_NAMES[int(c)]: {"mAP50": float(ap[i, 0]), "mAP50-95": float(ap[i].mean())}
                 for i, c in enumerate(unique_classes)}
    return {"overall": {"mAP50": float(ap[:, 0].mean()), "mAP50-95": float(ap.mean())}, "per_class": per_class}


def evaluate_variant(model: Any, images: list[Path], ground_truth: dict[str, tuple], variant: dict[str, Any],
                     args: argparse.Namespace) -> dict[str, Any]:
    tps, confs, classes, targets = [], [], [], []
    letterbox_shapes: dict[str, int] = {}
    for result in model.predict(source=[str(p) for p in images], stream=True, imgsz=args.imgsz,
                                conf=variant["conf"], iou=variant["iou"], device=args.device,
                                max_det=300, agnostic_nms=False, verbose=False, save=False):
        name = Path(result.path).name
        height, width = result.orig_shape
        gt_cls, gt_boxes = ground_truth[name](width, height)
        boxes = result.boxes
        pred_boxes = boxes.xyxy.cpu().numpy().astype(np.float64)
        pred_conf = boxes.conf.cpu().numpy().astype(np.float64)
        pred_cls = boxes.cls.cpu().numpy().astype(np.int64)
        tps.append(match_predictions(pred_cls, gt_cls, box_iou(gt_boxes, pred_boxes)))
        confs.append(pred_conf)
        classes.append(pred_cls)
        targets.append(gt_cls)
        shape = getattr(getattr(model, "predictor", None), "batch", None)
        if shape is not None:
            try:
                tensor_shape = model.predictor.preprocess(model.predictor.batch[1]).shape  # type: ignore[attr-defined]
                key = f"{tensor_shape[2]}x{tensor_shape[3]}"
                letterbox_shapes[key] = letterbox_shapes.get(key, 0) + 1
            except Exception:  # noqa: BLE001 - informasi tambahan saja
                pass
    tp = np.concatenate(tps, axis=0) if tps else np.zeros((0, len(IOU_THRESHOLDS)), dtype=bool)
    conf = np.concatenate(confs) if confs else np.zeros(0)
    pred_cls = np.concatenate(classes) if classes else np.zeros(0, dtype=np.int64)
    gt_cls = np.concatenate(targets) if targets else np.zeros(0, dtype=np.int64)
    output = {"settings": {"conf": variant["conf"], "iou": variant["iou"], "imgsz": args.imgsz, "precision": "FP32",
                           "device": args.device, "batch": 1, "max_det": 300, "agnostic_nms": False},
              "keterangan": variant["keterangan"],
              "prediction_count": int(len(conf)),
              "letterbox_tensor_shapes": letterbox_shapes,
              "operating_point": operating_point(tp, conf, pred_cls, gt_cls)}
    if variant["conf"] <= 0.001:
        output["average_precision"] = average_precision(tp, conf, pred_cls, gt_cls)
    return output


# ---------------------------------------------------------------- reporting

def flat_metrics(official: dict[str, Any], variants: dict[str, Any]) -> dict[str, float | None]:
    proto, robot = variants["protokol_test"], variants["robot"]
    return {
        "resmi_mAP50": official["mAP50"], "resmi_mAP50-95": official["mAP50-95"],
        "resmi_precision": official["precision"], "resmi_recall": official["recall"], "resmi_F1": official["F1"],
        "predict_mAP50": proto["average_precision"]["overall"]["mAP50"],
        "predict_mAP50-95": proto["average_precision"]["overall"]["mAP50-95"],
        "predict_precision": proto["operating_point"]["overall"]["precision"],
        "predict_recall": proto["operating_point"]["overall"]["recall"],
        "predict_F1": proto["operating_point"]["overall"]["F1"],
        "robot_precision": robot["operating_point"]["overall"]["precision"],
        "robot_recall": robot["operating_point"]["overall"]["recall"],
        "robot_F1": robot["operating_point"]["overall"]["F1"],
    }


def group_of(key: str) -> str:
    if key == "teacher_fp32":
        return "teacher_fp32"
    return key.rsplit("_seed", 1)[0]


def mean_sd(values: list[float]) -> tuple[float, float | None]:
    return statistics.fmean(values), (statistics.stdev(values) if len(values) > 1 else None)


def fmt(value: float | None, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:.{digits}f}".replace(".", ",")


def fmt_delta(value: float) -> str:
    return ("+" if value >= 0 else "") + fmt(value)


def write_outputs(output: Path, payload: dict[str, Any], rows: list[dict[str, Any]], groups: list[dict[str, Any]]) -> list[Path]:
    written = []
    results_path = output / "hasil_verifikasi_jalur_test.json"
    results_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(results_path)

    per_model = output / "ringkasan_per_model.csv"
    with per_model.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    written.append(per_model)

    per_group = output / "ringkasan_per_kelompok.csv"
    with per_group.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(groups[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(groups)
    written.append(per_group)

    lines = [
        "# Verifikasi jalur inferensi pada TEST",
        "",
        f"Dijalankan {payload['started_at_utc']} UTC pada `{payload['environment']['hostname']}`, perangkat "
        f"`{payload['arguments']['device']}`, Ultralytics {payload['environment']['ultralytics']}, "
        f"torch {payload['environment']['torch']}. Commit repo: `{payload['environment']['git_commit']}`.",
        "",
        "Angka **resmi** berasal dari evaluator TEST terkunci (`model.val`, batch 16, rect, GPU). Angka **predict** "
        "memakai `model.predict` per gambar dengan ambang yang sama (floor 0,001, NMS IoU 0,7). Angka **robot** memakai "
        "`model.predict` dengan confidence 0,25 dan NMS IoU 0,45 seperti runtime OP3. P/R/F1 memakai confidence > 0,25, "
        "pencocokan sekelas IoU ≥ 0,5, dan rerata makro; F1 = 2PR/(P+R).",
        "",
        "## Rerata per kelompok",
        "",
        "| Kelompok | n | mAP50-95 resmi | mAP50-95 predict | Δ | F1 resmi | F1 predict | Δ | F1 robot | Δ robot - resmi |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group in groups:
        lines.append(
            f"| {group['kelompok']} | {group['n']} | {fmt(group['resmi_mAP50-95_mean'])} | "
            f"{fmt(group['predict_mAP50-95_mean'])} | {fmt_delta(group['predict_mAP50-95_mean'] - group['resmi_mAP50-95_mean'])} | "
            f"{fmt(group['resmi_F1_mean'])} | {fmt(group['predict_F1_mean'])} | "
            f"{fmt_delta(group['predict_F1_mean'] - group['resmi_F1_mean'])} | {fmt(group['robot_F1_mean'])} | "
            f"{fmt_delta(group['robot_F1_mean'] - group['resmi_F1_mean'])} |")
    lines += [
        "",
        "## Per checkpoint",
        "",
        "| Model | mAP50-95 resmi | predict | F1 resmi | predict | robot | P robot | R robot |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {fmt(row['resmi_mAP50-95'])} | {fmt(row['predict_mAP50-95'])} | {fmt(row['resmi_F1'])} | "
            f"{fmt(row['predict_F1'])} | {fmt(row['robot_F1'])} | {fmt(row['robot_precision'])} | {fmt(row['robot_recall'])} |")
    nms = payload["environment"]["validator_nms_call"]
    lines += [
        "",
        "## Catatan pembacaan",
        "",
        f"- Pemanggilan NMS di `DetectionValidator.postprocess` pada versi terpasang: `{nms}`.",
        f"- Bentuk tensor letterbox jalur predict (varian protokol_test, gabungan semua model): "
        f"{payload['letterbox_shapes_summary'] or 'tidak tercatat'}.",
        f"- Sidik jari TEST cocok seluruhnya: {'ya' if payload['fingerprint']['all_match'] else 'TIDAK, hasil tidak sebanding'}.",
        "- Selisih resmi vs predict pada ambang yang sama menunjukkan pengaruh jalur (letterbox, NMS, batch, perangkat). "
        "Selisih robot vs resmi menambahkan pengaruh ambang runtime 0,25/0,45.",
        "- TEST sudah dibuka pada tahap sebelumnya. Hasil ini hanya pemeriksaan konsistensi dan tidak dipakai memilih "
        "ulang model atau ambang.",
        "",
    ]
    summary = output / "RINGKASAN.md"
    summary.write_text("\n".join(lines), encoding="utf-8")
    written.append(summary)
    return written


def validator_nms_call() -> str:
    try:
        from ultralytics.models.yolo.detect.val import DetectionValidator

        source = inspect.getsource(DetectionValidator.postprocess)
        start = source.find("non_max_suppression")
        if start < 0:
            return "non_max_suppression tidak ditemukan pada postprocess"
        end = source.find(")", source.find("(", start))
        depth, index = 0, source.find("(", start)
        for index in range(source.find("(", start), len(source)):
            depth += source[index] == "("
            depth -= source[index] == ")"
            if depth == 0:
                end = index
                break
        return " ".join(source[start:end + 1].split())
    except Exception as exc:  # noqa: BLE001
        return f"gagal dibaca: {type(exc).__name__}: {exc}"


def main() -> int:
    args = parse_args()
    started = dt.datetime.now(dt.timezone.utc)
    output = args.output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Folder hasil sudah ada dan tidak akan ditimpa: {output}")

    import torch
    import ultralytics
    from ultralytics import YOLO

    registry = yaml.safe_load(args.registry.read_text(encoding="utf-8"))["models"]
    keys = args.models or STUDENT_KEYS + (["teacher_fp32"] if args.teacher else [])
    if "teacher_fp32" in keys and not args.teacher:
        raise VerificationError("teacher_fp32 diminta tetapi --teacher tidak diberikan")
    checkpoints: dict[str, dict[str, Any]] = {}
    for key in keys:
        if key not in registry or key not in OFFICIAL_SOURCES:
            raise VerificationError(f"Model {key} tidak ada di registry atau tidak punya hasil TEST resmi")
        path = args.teacher if key == "teacher_fp32" else ROOT / registry[key]["checkpoint"]
        path = Path(path).expanduser().resolve()
        if not path.exists():
            raise VerificationError(f"Checkpoint {key} tidak ditemukan: {path}")
        digest = sha256(path)
        if digest != registry[key]["sha256"]:
            raise VerificationError(f"SHA-256 {key} berbeda dari registry: {digest}")
        checkpoints[key] = {"path": str(path), "sha256": digest}

    test_dir, data_info = resolve_test_dir(args)
    images = sorted(p for p in test_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    fingerprint = verify_fingerprint(images, args.fingerprint.expanduser().resolve(), args.allow_fingerprint_mismatch)

    polygon_total = 0
    label_cache: dict[str, tuple[np.ndarray, np.ndarray, int]] = {}

    def make_reader(image: Path):
        def reader(width: int, height: int):
            cls, boxes, polygons = read_labels(label_path_for(image), width, height)
            label_cache[image.name] = (cls, boxes, polygons)
            return cls, boxes
        return reader

    ground_truth = {image.name: make_reader(image) for image in images}

    output.mkdir(parents=True)
    results: dict[str, Any] = {}
    shapes_summary: dict[str, int] = {}
    for key, checkpoint in checkpoints.items():
        print(f"[{dt.datetime.now():%H:%M:%S}] {key}", flush=True)
        model = YOLO(checkpoint["path"])
        variants = {}
        for name, variant in VARIANTS.items():
            variants[name] = evaluate_variant(model, images, ground_truth, variant, args)
            if name == "protokol_test":
                for shape, count in variants[name]["letterbox_tensor_shapes"].items():
                    shapes_summary[shape] = shapes_summary.get(shape, 0) + count
        official_path = ROOT / OFFICIAL_SOURCES[key]
        official = json.loads(official_path.read_text(encoding="utf-8"))
        if official.get("checkpoint_sha256") not in (None, checkpoint["sha256"]):
            raise VerificationError(f"Hash checkpoint pada hasil resmi {key} berbeda dari checkpoint yang dievaluasi")
        results[key] = {"checkpoint": checkpoint, "official_source": OFFICIAL_SOURCES[key],
                        "official_source_sha256": sha256(official_path),
                        "official_test_metrics": official["test_metrics"], "predict": variants}
    polygon_total = sum(item[2] for item in label_cache.values())
    target_total = sum(len(item[0]) for item in label_cache.values())

    rows = []
    for key, record in results.items():
        flat = flat_metrics(record["official_test_metrics"]["overall"], record["predict"])
        rows.append({"model": key, "kelompok": group_of(key), **flat})
    groups = []
    for group_key, label in GROUPS.items():
        members = [row for row in rows if row["kelompok"] == group_key]
        if not members:
            continue
        entry: dict[str, Any] = {"kelompok": label, "n": len(members)}
        for column in [c for c in members[0] if c not in ("model", "kelompok")]:
            mean, sd = mean_sd([row[column] for row in members])
            entry[f"{column}_mean"] = mean
            entry[f"{column}_sd"] = sd
        groups.append(entry)

    payload = {
        "purpose": "Verifikasi jalur model.val vs model.predict pada TEST; bukan seleksi model",
        "started_at_utc": started.isoformat(timespec="seconds"),
        "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "arguments": {"data": str(args.data), "test_images": str(test_dir), "device": args.device,
                      "imgsz": args.imgsz, "models": keys, "command": " ".join(sys.argv)},
        "data": {**data_info,
                 "data_yaml_sha256": sha256(args.data.expanduser().resolve()) if args.data and args.data.exists() else None,
                 "image_count": len(images), "annotation_count": target_total,
                 "polygon_labels_converted_to_box": polygon_total},
        "fingerprint": fingerprint,
        "variants": VARIANTS,
        "matching": {"iou_thresholds": IOU_THRESHOLDS.round(2).tolist(), "operating_confidence": OPERATING_CONFIDENCE,
                     "operating_match_iou": MATCH_IOU, "rule": "sekelas, serakah menurut IoU, satu prediksi per label"},
        "letterbox_shapes_summary": shapes_summary,
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "hostname": platform.node(), "torch": torch.__version__,
                        "ultralytics": ultralytics.__version__, "numpy": np.__version__,
                        "git_commit": git_value("rev-parse", "HEAD"),
                        "git_dirty": bool(git_value("status", "--porcelain")),
                        "script": str(Path(__file__).resolve().relative_to(ROOT)),
                        "script_sha256": sha256(Path(__file__).resolve()),
                        "validator_nms_call": validator_nms_call()},
        "results": results,
    }
    written = write_outputs(output, payload, rows, groups)
    manifest = {"created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "files": {path.name: sha256(path) for path in written},
                "script_sha256": payload["environment"]["script_sha256"],
                "git_commit": payload["environment"]["git_commit"]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Selesai. Hasil: {output}")
    print((output / "RINGKASAN.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (VerificationError, FileExistsError) as error:
        print(f"GAGAL: {error}", file=sys.stderr)
        sys.exit(2)
