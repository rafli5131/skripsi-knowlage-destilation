"""Complete lab tables derivable from frozen VAL predictions and TEST summaries.

No model inference or training is performed. Area AP uses explicit one-to-one
IoU matching and ignores detections of same-class objects outside the area bin.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml
from ultralytics.utils.metrics import ap_per_class, compute_ap

try:
    from .analyze_val_detections import MODELS, NAMES, OUT, ROOT, TABLES, iou_matrix, source_paths, verify_val_bytes
except ImportError:
    from analyze_val_detections import MODELS, NAMES, OUT, ROOT, TABLES, iou_matrix, source_paths, verify_val_bytes


IOUS = np.arange(0.5, 1.0, 0.05)
SIZES = ("small", "medium", "large")
METHOD = {"teacher_fp32": "Teacher"}
METHOD.update({key: "Pure KD" if key.startswith("kd_") else "Supervised student" for key in MODELS if key != "teacher_fp32"})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def size_of_box(box: np.ndarray, shape: list[int]) -> str:
    # Rectangular validator padding can produce a tensor above 640 pixels.
    # Express areas at the protocol's 640-pixel reference scale.
    area = float(np.prod(np.maximum(box[2:] - box[:2], 0))) * (640 / max(shape)) ** 2
    return "small" if area < 1024 else "medium" if area <= 9216 else "large"


def area_metrics(records: list[dict], cls: int, size: str) -> tuple[int, float | None, float | None]:
    entries = [[] for _ in IOUS]
    gt_count = 0
    for record in records:
        gc = np.asarray(record["gt_cls"], dtype=int)
        gb = np.asarray(record["gt_xyxy"], dtype=float).reshape(-1, 4)
        pc = np.asarray(record["pred_cls"], dtype=int)
        pb = np.asarray(record["pred_xyxy"], dtype=float).reshape(-1, 4)
        confidence = np.asarray(record["pred_conf"], dtype=float)
        gt_indices = np.flatnonzero(gc == cls)
        pred_indices = np.flatnonzero(pc == cls)
        inside = np.array([size_of_box(gb[g], record["image_shape"]) == size for g in gt_indices], dtype=bool)
        gt_count += int(inside.sum())
        iou = iou_matrix(gb[gt_indices], pb[pred_indices])
        for index, threshold in enumerate(IOUS):
            eligible = np.argwhere(iou[inside] >= threshold)
            eligible_gt = np.flatnonzero(inside)
            candidates = sorted(((float(iou[eligible_gt[g], p]), int(eligible_gt[g]), int(p))
                                 for g, p in eligible), reverse=True)
            matched_gt, matched_pred = set(), set()
            for _, g, p in candidates:
                if g not in matched_gt and p not in matched_pred:
                    matched_gt.add(g)
                    matched_pred.add(p)
            for p, original_p in enumerate(pred_indices):
                if p in matched_pred:
                    entries[index].append((float(confidence[original_p]), 1, 0))
                elif np.any(iou[inside, p] >= threshold):
                    entries[index].append((float(confidence[original_p]), 0, 1))
                elif np.any(iou[~inside, p] >= threshold):
                    pass  # A correct detection of an out-of-bin GT is ignored.
                else:
                    entries[index].append((float(confidence[original_p]), 0, 1))
    if not gt_count:
        return 0, None, None
    selected = [row for row in entries[0] if row[0] > 0.25]
    recall = sum(row[1] for row in selected) / gt_count
    ap = []
    for observations in entries:
        observations.sort(key=lambda item: item[0], reverse=True)
        tp = np.cumsum([item[1] for item in observations])
        fp = np.cumsum([item[2] for item in observations])
        if len(tp):
            precision = tp / np.maximum(tp + fp, 1)
            recall_curve = tp / gt_count
            ap.append(float(compute_ap(recall_curve, precision)[0]))
        else:
            ap.append(0.0)
    return gt_count, float(recall), float(np.mean(ap))


def per_class_ap(records: list[dict]) -> dict[str, float]:
    tps, confs, pred_classes, gt_classes = [], [], [], []
    for record in records:
        gc = np.asarray(record["gt_cls"], dtype=int)
        pc = np.asarray(record["pred_cls"], dtype=int)
        gb = np.asarray(record["gt_xyxy"], dtype=float).reshape(-1, 4)
        pb = np.asarray(record["pred_xyxy"], dtype=float).reshape(-1, 4)
        iou = iou_matrix(gb, pb) * (gc[:, None] == pc[None, :])
        tp = np.zeros((len(pc), len(IOUS)), dtype=bool)
        for index, threshold in enumerate(IOUS):
            matches = np.array(np.nonzero(iou >= threshold)).T
            if len(matches):
                if len(matches) > 1:
                    matches = matches[iou[matches[:, 0], matches[:, 1]].argsort()[::-1]]
                    matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                    matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
                tp[matches[:, 1].astype(int), index] = True
        tps.append(tp)
        confs.extend(record["pred_conf"])
        pred_classes.extend(pc)
        gt_classes.extend(gc)
    result = ap_per_class(np.concatenate(tps), np.asarray(confs), np.asarray(pred_classes),
                          np.asarray(gt_classes), names=NAMES)
    ap, classes = result[5], result[6]
    return {NAMES[int(cls)]: float(ap[index].mean()) for index, cls in enumerate(classes)}


def table(path: Path, rows: list[dict], note: str) -> None:
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
            if value is None:
                values.append("[TIDAK ADA GT]")
            elif isinstance(value, float):
                values.append(f"{value:.4f}".replace(".", ","))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    _, expected, fingerprint = source_paths()
    verify_val_bytes(fingerprint)
    rows = []
    sources = {}
    baseline_ap = {}
    for model in MODELS:
        path = OUT / f"{model}_predictions.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = payload["images"]
        if (payload["checkpoint_sha256"] != yaml.safe_load((ROOT / "configs/model_registry.yaml").read_text())["models"][model]["sha256"]
                or payload["val_split_fingerprint_sha256"] != fingerprint["split_fingerprint_sha256"]
                or len(records) != len(expected) or {item["image"] for item in records} != expected):
            raise ValueError(f"Prediction source does not match locked VAL/model: {path}")
        source = path.relative_to(ROOT).as_posix()
        sources[source] = sha256(path)
        baseline_ap[model] = per_class_ap(records)
        for cls, name in NAMES.items():
            for size in SIZES:
                count, recall, ap = area_metrics(records, cls, size)
                rows.append({"model": model, "method": METHOD[model], "split": "val", "class": name,
                             "size_category": size, "ground_truth_objects_count": count,
                             "recall_iou50_conf025": recall, "AP50_95": ap, "source": source})
        print(f"T08 {model}: {len(records)} VAL images", flush=True)
    path = TABLES / "T08_akurasi_ukuran_objek.csv"
    table(path, rows, "Status: Lengkap untuk VAL pada tujuh checkpoint. Luas kotak dinormalisasi ke sisi referensi 640 piksel; kecil <1024 px², sedang 1024–9216 px², besar >9216 px². Recall memakai confidence >0,25 dan IoU 0,50. AP adalah rerata 10 ambang IoU 0,50–0,95, dengan pencocokan satu-ke-satu berdasarkan IoU; deteksi objek kelas sama di luar kelompok ukuran diabaikan. Definisi diagnostik ini tidak identik dengan evaluasi area COCO. Angka ini berasal dari VAL Advance Vision, bukan kamera OP3.")

    # Complete the seven historical L40 baseline rows with per-class VAL AP
    # from frozen predictions. Do not alter rows produced by a later sweep.
    path13 = TABLES / "T13_sapuan_imgsz.csv"
    rows13 = list(csv.DictReader(path13.open(encoding="utf-8")))
    for row in rows13:
        if row["benchmark_device"] == "NVIDIA L40":
            aps = baseline_ap[row["model"]]
            if abs(np.mean(list(aps.values())) - float(row["val_mAP50_95"])) > 0.005:
                raise ValueError(f"Reconstructed VAL AP differs from baseline: {row['model']}")
            row["val_AP50_95_per_class"] = json.dumps(aps, separators=(",", ":"))
    if not any(row["benchmark_device"].startswith("CPU ") for row in rows13):
        table(path13, rows13, "Status: Sebagian; tujuh titik dasar 640 pada NVIDIA L40 tersedia. AP VAL per kelas direkonstruksi dari prediksi VAL terkunci dengan aturan matching Ultralytics dan dapat berbeda kecil dari angka total pada manifest karena pembulatan atau pemrosesan validator. Sapuan ukuran input CPU server masih berjalan. FPS berasal dari benchmark frame tetap, bukan kamera OP3.")

    # Seed-level bootstrap of three already-locked TEST point estimates. This
    # represents variation over training seeds, not over TEST images.
    summary = list(csv.DictReader((ROOT / "artifacts/thesis_analysis_final_corrected/per_model.csv").open()))
    by_method = defaultdict(list)
    for item in summary:
        by_method[item["method"]].append(item)
    path5 = TABLES / "T05_akurasi_test_keseluruhan.csv"
    rows5 = list(csv.DictReader(path5.open()))
    rng = np.random.default_rng(20261020)
    for row in rows5:
        if int(row["n_models [model]"]) != 3:
            continue
        values = np.asarray([float(item[row["metric"]]) for item in by_method[row["method"]]], dtype=float)
        if len(values) != 3:
            raise ValueError(f"Expected three seeds: {row['method']}")
        resamples = values[rng.integers(0, 3, size=(10000, 3))].mean(axis=1)
        lo, hi = np.percentile(resamples, [2.5, 97.5])
        row["CI95 bootstrap of across-seed mean"] = f"[{lo:.6f}, {hi:.6f}]"
    table(path5, rows5, "Status: Lengkap untuk estimasi yang tersedia. Mean ± SD memakai tiga seed; IK 95% rerata antar-seed dihitung dengan bootstrap persentil 10.000 resampling seed (seed acak 20261020). Dengan hanya tiga seed, interval ini bersifat eksploratif dan tidak meresampling gambar TEST. Interval bootstrap per checkpoint yang meresampling gambar TEST tersedia terpisah di [lab_server/interval_bootstrap_per_model.md](../lab_server/interval_bootstrap_per_model.md). Teacher hanya satu checkpoint sehingga interval antar-seed tidak berlaku. P/R/F1 menggunakan confidence >0,25 dan IoU 0,50; AP memakai confidence floor 0,001 dan NMS 0,7.")

    # The existing pure KD runs provide the control setting for T04. A true
    # ablation still requires at least one alternate teacher-only objective.
    convergence = {item["model"]: item for item in csv.DictReader((TABLES / "T03_konvergensi.csv").open())}
    registry = yaml.safe_load((ROOT / "configs/model_registry.yaml").read_text())["models"]
    rows4 = []
    for model in MODELS:
        if not model.startswith("kd_"):
            continue
        manifest_path = Path(registry[model]["manifest"])
        manifest_path = manifest_path if manifest_path.is_absolute() else ROOT / manifest_path
        run = json.loads(manifest_path.read_text(encoding="utf-8"))
        distill, metrics = run["distillation"], run["metrics"]
        rows4.append({"model": model, "seed": run["seed"], "mode": "pure_v4 baseline",
                      "feature_weight": distill["feature_weight"], "box_weight": distill["box_weight"],
                      "class_weight": distill["class_weight"], "temperature": distill["class_temperature"],
                      "best_epoch": convergence[model]["best_epoch [epoch]"],
                      "val_mAP50": metrics["metrics/mAP50(B)"],
                      "val_mAP50_95": metrics["metrics/mAP50-95(B)"],
                      "val_precision": metrics["metrics/precision(B)"],
                      "val_recall": metrics["metrics/recall(B)"],
                      "source_run": manifest_path.relative_to(ROOT).as_posix()})
        sources[manifest_path.relative_to(ROOT).as_posix()] = sha256(manifest_path)
    path4 = TABLES / "T04_ablasi_kd_val.csv"
    table(path4, rows4, "Status: Sebagian. Tiga baris ini adalah kondisi kontrol pure_v4 teacher-only pada VAL, satu per seed. Epoch terbaik berasal dari log T03; mAP/P/R berasal dari manifest evaluasi checkpoint terbaik, sehingga nilai mAP dapat sedikit berbeda dari maksimum log per epoch. Tabel belum menjadi ablasi karena belum ada kondisi objective/bobot/temperatur alternatif yang dilatih dan dinilai. Tidak ada training baru saat tabel ini dibuat.")

    manifest_path = ROOT / "analisis_performa/lab_server/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources_sha256"].update(sources)
    script = Path(__file__).resolve()
    manifest["sources_sha256"][script.relative_to(ROOT).as_posix()] = sha256(script)
    for name in ("T04_ablasi_kd_val", "T05_akurasi_test_keseluruhan", "T08_akurasi_ukuran_objek", "T13_sapuan_imgsz"):
        for suffix in (".csv", ".md"):
            output = TABLES / f"{name}{suffix}"
            manifest["outputs_sha256"][output.relative_to(ROOT).as_posix()] = sha256(output)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
