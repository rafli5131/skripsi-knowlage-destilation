"""Build the paired Hybrid TEST and lab benchmark tables from frozen JSON artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST = ROOT / "runs/final_test/hybrid_full_official_split_20261022/manifest.json"
HISTORICAL = ROOT / "runs/final_test/pure_kd_official_split_locked_retry1/manifest.json"
BENCHMARK = ROOT / "runs/benchmarks/hybrid_full_paired_20261022.json"
TABLES = ROOT / "analisis_performa/tabel"
REPORT = ROOT / "analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md"
CURATED_MANIFEST = ROOT / "analisis_performa/lab_server/manifest.json"
GENERATOR_MANIFEST = ROOT / "analisis_performa/manifest.json"
SEEDS = (42, 1337, 2025)
CLASSES = ("ball", "gawang", "robot")
METRICS = ("mAP50", "mAP50-95", "precision", "recall", "F1")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_sources(test: dict, historical: dict, benchmark: dict) -> None:
    expected = {f"hybrid_full_seed{seed}" for seed in SEEDS} | {
        f"supervised_seed{seed}" for seed in SEEDS
    }
    require(test.get("status") == "complete", "Hybrid TEST evaluation is incomplete.")
    require(set(test.get("models", {})) == expected, "Hybrid TEST model set is incomplete.")
    require(historical.get("status") == "complete", "Historical TEST evidence is incomplete.")
    require(test.get("historical_test_manifest_sha256") == sha256(HISTORICAL), "Historical TEST hash changed.")
    require(test.get("test_split_fingerprint_sha256") == historical.get("test_split_fingerprint_sha256"), "TEST splits differ.")
    require(test.get("data_yaml_sha256") == historical.get("data_yaml_sha256"), "Evaluation dataset YAML differs.")
    require(test.get("test_image_count") == historical.get("test_image_count") == 592, "TEST image count differs.")
    require(test.get("test_annotation_count") == historical.get("test_annotation_count") == 734, "TEST annotation count differs.")
    required_test_settings = {
        "split": "test", "precision": "FP32", "imgsz": 640, "batch": 16,
        "workers": 2, "device": "0", "augmentation": False, "rect": True,
        "conf_for_ap": 0.001, "nms_iou": 0.7,
        "operating_confidence": 0.25, "matching_iou": 0.5,
        "bootstrap_replicates": 1000, "bootstrap_seed": 20261009,
    }
    require(test.get("settings") == required_test_settings, "Hybrid TEST settings differ from the locked protocol.")
    for key, hash_key in (
        ("protocol", "protocol_sha256"),
        ("evaluator_script", "evaluator_script_sha256"),
        ("shared_metric_implementation", "shared_metric_implementation_sha256"),
        ("dataset_fingerprint", "dataset_fingerprint_sha256"),
    ):
        path = Path(test[key])
        require(path.is_file() and sha256(path) == test[hash_key], f"Frozen {key} hash differs.")
    require(benchmark.get("settings", {}).get("warmup_iterations") == 30, "Benchmark warmup changed.")
    require(benchmark.get("settings", {}).get("timed_iterations") == 200, "Benchmark iteration count changed.")
    require(benchmark.get("settings", {}).get("imgsz") == 640, "Benchmark image size changed.")
    require(benchmark.get("settings", {}).get("batch") == 1, "Benchmark batch changed.")
    require(benchmark.get("settings", {}).get("precision") == "FP32", "Benchmark precision changed.")
    require(benchmark.get("settings", {}).get("confidence") == 0.001, "Benchmark confidence changed.")
    require(benchmark.get("settings", {}).get("iou") == 0.7, "Benchmark NMS IoU changed.")
    require(benchmark.get("runtime", {}).get("device_name") == "NVIDIA L40", "Benchmark device changed.")
    require(test.get("runtime", {}).get("device_name") == "NVIDIA L40", "TEST device changed.")
    require(set(benchmark.get("models", {})) == expected, "Benchmark model set is incomplete.")
    benchmark_script = Path(benchmark["benchmark_script"])
    require(benchmark_script.is_file() and sha256(benchmark_script) == benchmark["benchmark_script_sha256"], "Benchmark script hash differs.")
    require(test.get("model_registry_sha256") == sha256(ROOT / "configs/model_registry.yaml"), "Frozen model registry hash differs.")
    for label in sorted(expected):
        result = test["models"][label]
        checkpoint = Path(result["checkpoint"])
        training_manifest = Path(result["training_manifest"])
        require(checkpoint.is_file() and sha256(checkpoint) == result["checkpoint_sha256"], f"Checkpoint hash differs: {label}")
        require(training_manifest.is_file() and sha256(training_manifest) == result["training_manifest_sha256"], f"Training manifest hash differs: {label}")
        require(benchmark["models"][label]["checkpoint_sha256"] == result["checkpoint_sha256"], f"TEST and benchmark checkpoints differ: {label}")
        require(len(benchmark["models"][label]["latency_ms"]["samples"]) == 200, f"Benchmark sample count differs: {label}")
        file_result = read_json(TEST.parent / f"{label}_metrics.json")
        require(file_result == result, f"TEST result file and manifest differ: {label}")
        if label.startswith("supervised_seed"):
            require(result["test_metrics"] == historical["models"][label]["test_metrics"], f"Control differs from historical TEST: {label}")


def summary_rows(test: dict, class_name: str | None = None) -> list[dict]:
    rows: list[dict] = []
    for seed in SEEDS:
        hybrid_result = test["models"][f"hybrid_full_seed{seed}"]
        control_result = test["models"][f"supervised_seed{seed}"]
        scope = "overall" if class_name is None else class_name
        hybrid_metrics = hybrid_result["test_metrics"]["overall" if class_name is None else "per_class"]
        control_metrics = control_result["test_metrics"]["overall" if class_name is None else "per_class"]
        if class_name is not None:
            hybrid_metrics, control_metrics = hybrid_metrics[class_name], control_metrics[class_name]
        hybrid_ci = hybrid_result["bootstrap_ci_95"]["overall" if class_name is None else "per_class"]
        control_ci = control_result["bootstrap_ci_95"]["overall" if class_name is None else "per_class"]
        if class_name is not None:
            hybrid_ci, control_ci = hybrid_ci[class_name], control_ci[class_name]
        for metric in METRICS:
            hybrid = float(hybrid_metrics[metric])
            control = float(control_metrics[metric])
            rows.append({
                "scope": scope, "row_type": "seed", "seed": seed, "metric": metric,
                "hybrid_full": hybrid, "supervised": control,
                "delta_hybrid_minus_supervised": hybrid - control,
                "hybrid_sd": "", "supervised_sd": "", "delta_sd": "",
                "hybrid_ci95_lower": hybrid_ci[metric]["lower"],
                "hybrid_ci95_upper": hybrid_ci[metric]["upper"],
                "supervised_ci95_lower": control_ci[metric]["lower"],
                "supervised_ci95_upper": control_ci[metric]["upper"],
            })
    for metric in METRICS:
        per_seed = [row for row in rows if row["metric"] == metric]
        hybrid = [float(row["hybrid_full"]) for row in per_seed]
        control = [float(row["supervised"]) for row in per_seed]
        delta = [float(row["delta_hybrid_minus_supervised"]) for row in per_seed]
        rows.append({
            "scope": "overall" if class_name is None else class_name,
            "row_type": "mean_sd", "seed": "mean_sd_n3", "metric": metric,
            "hybrid_full": statistics.mean(hybrid),
            "supervised": statistics.mean(control),
            "delta_hybrid_minus_supervised": statistics.mean(delta),
            "hybrid_sd": statistics.stdev(hybrid),
            "supervised_sd": statistics.stdev(control),
            "delta_sd": statistics.stdev(delta),
            "hybrid_ci95_lower": "", "hybrid_ci95_upper": "",
            "supervised_ci95_lower": "", "supervised_ci95_upper": "",
        })
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: f"{value:.10f}" if isinstance(value, float) else value for key, value in row.items()})


def displayed(value: float, sd: float | str = "", *, signed: bool = False) -> str:
    prefix = "+" if signed and value > 0 else ""
    result = f"{prefix}{value:.4f}".replace(".", ",")
    return result if sd == "" else result + " ± " + f"{float(sd):.4f}".replace(".", ",")


def markdown_summary(path: Path, rows: list[dict], title: str, note: str, per_class: bool = False) -> None:
    lines = [f"# {title}", "", note, ""]
    first = "| kelas | seed | metrik | Hybrid full | Supervised | Δ Hybrid − supervised |" if per_class else "| seed | metrik | Hybrid full | Supervised | Δ Hybrid − supervised |"
    lines.extend([first, "| --- | --- | --- | --- | --- | --- |" if per_class else "| --- | --- | --- | --- | --- |"])
    for row in rows:
        summary = row["row_type"] == "mean_sd"
        seed = "rerata ± SD (n=3)" if summary else str(row["seed"])
        cols = [seed, row["metric"], displayed(row["hybrid_full"], row["hybrid_sd"]), displayed(row["supervised"], row["supervised_sd"]), displayed(row["delta_hybrid_minus_supervised"], row["delta_sd"], signed=True)]
        if per_class:
            cols.insert(0, row["scope"])
        lines.append("| " + " | ".join(cols) + " |")
    lines.extend(["", "CSV menyimpan angka lebih presisi dan interval bootstrap 95% per checkpoint; SD pada baris ringkasan adalah variasi antar tiga seed, bukan interval bootstrap.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def benchmark_rows(benchmark: dict) -> list[dict]:
    rows = []
    for seed in SEEDS:
        for method in ("hybrid_full", "supervised"):
            label = f"{method}_seed{seed}"
            item = benchmark["models"][label]
            latency = item["latency_ms"]
            rows.append({
                "method": method, "seed": seed, "checkpoint_sha256": item["checkpoint_sha256"],
                "parameters_before_fusion": item["parameters"],
                "gflops_640": item["flops_gflops"],
                "checkpoint_size_bytes": item["checkpoint_size_bytes"],
                "mean_latency_ms": latency["mean"],
                "median_latency_ms": latency["median"],
                "p95_latency_ms": latency["p95"],
                "images_per_second": latency["images_per_second"],
            })
    return rows


def write_benchmark_markdown(path: Path, rows: list[dict]) -> None:
    lines = [
        "# T32. Benchmark inferensi KD Hybrid dan supervised di server",
        "",
        "NVIDIA L40, FP32, batch 1, imgsz 640, satu frame VAL tetap di memori; 30 iterasi pemanasan dan 200 iterasi ukur per checkpoint. Waktu meliputi preprocessing, forward, dan NMS. Images/s berasal dari 1000 dibagi mean latency; angka ini bukan FPS kamera OP3.",
        "",
        "| model | seed | mean ms | median ms | p95 ms | images/s | parameter | GFLOPs | ukuran best.pt (byte) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['method']} | {row['seed']} | {row['mean_latency_ms']:.3f} | "
            f"{row['median_latency_ms']:.3f} | {row['p95_latency_ms']:.3f} | "
            f"{row['images_per_second']:.1f} | {row['parameters_before_fusion']:,} | "
            f"{row['gflops_640']:.3f} | {row['checkpoint_size_bytes']:,} |"
        )
    lines.extend(["", "Seluruh model memakai arsitektur, parameter, dan GFLOPs yang sama. Perbedaan waktu dari satu urutan benchmark ini tidak membuktikan KD menyebabkan percepatan. CPU, RAM, latency end-to-end, dan FPS robot perlu pengukuran langsung pada OP3.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def training_rows() -> list[dict]:
    rows = []
    for seed in SEEDS:
        run = ROOT / f"runs/kd_hybrid/yolo11_tiny_hybrid_full_seed{seed}"
        manifest = read_json(run / "manifest.json")
        with (run / "results.csv").open("r", encoding="utf-8", newline="") as stream:
            epochs = list(csv.DictReader(stream))
        require(manifest.get("status") == "complete" and len(epochs) == 100, f"Hybrid training run is incomplete: {seed}")
        require(manifest.get("test_split_used") is False, f"Training used TEST: {seed}")
        best = max(epochs, key=lambda row: float(row["metrics/mAP50-95(B)"]))
        indexed = {int(float(epoch["epoch"])): epoch for epoch in epochs}
        require(all(epoch in indexed for epoch in (10, 25, 50, 75, 100)), f"Epoch samples are missing: {seed}")
        distillation = manifest["distillation"]
        row = {
            "seed": seed,
            "epochs_configured": manifest["training"]["epochs"],
            "epochs_completed": len(epochs),
            "batch": manifest["training"]["batch"],
            "imgsz": manifest["training"]["imgsz"],
            "optimizer": manifest["training"]["optimizer"],
            "amp": manifest["training"]["amp"],
            "train_labels_used_for_loss": manifest["train_labels_used_for_loss"],
            "feature_weight": distillation["feature_weight"],
            "box_weight": distillation["box_weight"],
            "class_weight": distillation["class_weight"],
            "temperature": distillation["class_temperature"],
            "training_time_seconds": float(epochs[-1]["time"]),
            "highest_logged_map_epoch": int(float(best["epoch"])),
            "highest_logged_val_map50_95": float(best["metrics/mAP50-95(B)"]),
            "manifest_best_checkpoint_val_map50_95": float(manifest["metrics"]["metrics/mAP50-95(B)"]),
            "best_checkpoint_sha256": manifest["student_best_sha256"],
        }
        for epoch in (10, 25, 50, 75, 100):
            row[f"val_map50_95_epoch_{epoch}"] = float(indexed[epoch]["metrics/mAP50-95(B)"])
        rows.append(row)
    return rows


def write_training_markdown(path: Path, rows: list[dict]) -> None:
    lines = [
        "# T33. Pelatihan dan konvergensi KD Hybrid full",
        "",
        "Tiga run memakai 100 epoch, batch 16, imgsz 640, AdamW, AMP mati, student YOLO11 skala `t` kustom, teacher FP32 beku, serta bobot distilasi fitur/kotak/kelas 1/1/1 pada temperatur kelas 2. Label TRAIN masuk loss deteksi student; TEST tidak masuk training. Kontrol supervised dengan resep bersama tercatat pada T02–T03.",
        "",
        "| seed | durasi training (s) | epoch mAP tertinggi di log | VAL mAP50–95 tertinggi di log | VAL mAP50–95 best.pt menurut manifest | epoch 10 | epoch 25 | epoch 50 | epoch 75 | epoch 100 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['seed']} | {row['training_time_seconds']:.2f} | {row['highest_logged_map_epoch']} | "
            f"{row['highest_logged_val_map50_95']:.4f} | {row['manifest_best_checkpoint_val_map50_95']:.4f} | "
            + " | ".join(f"{row[f'val_map50_95_epoch_{epoch}']:.4f}" for epoch in (10, 25, 50, 75, 100))
            + " |"
        )
    lines.extend([
        "",
        "Durasi diambil dari kolom `time` pada baris epoch terakhir `results.csv`. Epoch mAP tertinggi pada log bukan klaim tentang epoch checkpoint `best.pt`; angka checkpoint dari manifest dan evaluasi ulang `best.pt` pada T04/T28 dicatat terpisah. Perbedaan kecil di antara ketiganya tidak disamarkan. Perbedaan durasi antar-run pada server bersama tidak membuktikan perbedaan biaya komputasi kausal.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(test: dict, historical: dict, overall: list[dict], per_class: list[dict], bench: list[dict]) -> None:
    summary = {row["metric"]: row for row in overall if row["row_type"] == "mean_sd"}
    ap = summary["mAP50-95"]
    f1 = summary["F1"]
    p = summary["precision"]
    r = summary["recall"]
    pure_kd_map = statistics.mean(
        historical["models"][f"kd_seed{seed}"]["test_metrics"]["overall"]["mAP50-95"]
        for seed in SEEDS
    )
    teacher_map = historical["models"]["teacher_fp32"]["test_metrics"]["overall"]["mAP50-95"]
    gawang_f1_delta = next(
        row["delta_hybrid_minus_supervised"] for row in per_class
        if row["scope"] == "gawang" and row["row_type"] == "mean_sd" and row["metric"] == "F1"
    )
    gawang_precision_delta = next(
        row["delta_hybrid_minus_supervised"] for row in per_class
        if row["scope"] == "gawang" and row["row_type"] == "mean_sd" and row["metric"] == "precision"
    )
    lines = [
        "# Hasil TEST lanjutan KD Hybrid full — 22 Oktober 2026",
        "",
        "## Cakupan dan protokol",
        "",
        f"Enam checkpoint `best.pt` dievaluasi pada split TEST resmi yang sama: **{test['test_image_count']} gambar dan {test['test_annotation_count']} anotasi**, kelas ball, gawang, robot. Student adalah YOLO11 skala `t` kustom (810.649 parameter), dengan teacher YOLO11n FP32 saat training Hybrid. Semua tiga seed Hybrid full dibandingkan berpasangan dengan supervised. Inferensi FP32 pada NVIDIA L40; imgsz 640, batch 16, confidence floor AP 0,001, NMS IoU 0,7, P/R/F1 makro pada confidence >0,25 dan matching IoU 0,50. Interval bootstrap per checkpoint ada di JSON sumber. Protokol dikunci dan dipush sebelum evaluasi. Fingerprint TEST: `{test['test_split_fingerprint_sha256']}`.",
        "",
        "TEST ini pernah dievaluasi untuk teacher dan KD murni. Hasil Hybrid adalah eksperimen lanjutan pada split yang sama; interpretasinya dibatasi pada gambar dalam dataset resmi. Tiga seed memberi variasi deskriptif, bukan bukti signifikansi kuat.",
        "",
        "## Hasil akurasi",
        "",
        "| metrik | Hybrid full, rerata ± SD | Supervised, rerata ± SD | Δ berpasangan, rerata ± SD |",
        "| --- | --- | --- | --- |",
    ]
    for metric in METRICS:
        row = summary[metric]
        lines.append(f"| {metric} | {displayed(row['hybrid_full'], row['hybrid_sd'])} | {displayed(row['supervised'], row['supervised_sd'])} | {displayed(row['delta_hybrid_minus_supervised'], row['delta_sd'], signed=True)} |")
    lines.extend(["", "mAP50–95 TEST Hybrid full lebih tinggi pada ketiga pasangan seed:", "", "| seed | Hybrid full | Supervised | Δ |", "| --- | --- | --- | --- |"])
    for seed in SEEDS:
        row = next(row for row in overall if row["seed"] == seed and row["metric"] == "mAP50-95")
        lines.append(f"| {seed} | {displayed(row['hybrid_full'])} | {displayed(row['supervised'])} | {displayed(row['delta_hybrid_minus_supervised'], signed=True)} |")
    lines.extend(["", "Per kelas, selisih AP50–95 rerata berpasangan:", "", "| kelas | Δ AP50–95, rerata ± SD |", "| --- | --- |"])
    for name in CLASSES:
        row = next(row for row in per_class if row["scope"] == name and row["row_type"] == "mean_sd" and row["metric"] == "mAP50-95")
        lines.append(f"| {name} | {displayed(row['delta_hybrid_minus_supervised'], row['delta_sd'], signed=True)} |")
    lines.extend([
        "",
        f"Metrik utama mAP50–95 naik `{ap['delta_hybrid_minus_supervised']:+.4f}`. Pada confidence tetap 0,25, F1 turun `{f1['delta_hybrid_minus_supervised']:+.4f}` dan precision turun `{p['delta_hybrid_minus_supervised']:+.4f}`; selisih recall sekitar nol (`{r['delta_hybrid_minus_supervised']:+.6f}`). Keunggulan AP tidak menunjukkan peningkatan semua metrik deteksi.",
        "",
        f"Kelas gawang perlu perhatian saat uji OP3: meskipun AP50–95 naik, precision@0,25 turun `{gawang_precision_delta:+.4f}` dan F1@0,25 turun `{gawang_f1_delta:+.4f}` terhadap supervised. Frame kamera berlabel diperlukan untuk melihat apakah pola ini muncul pada robot.",
        "",
        "Ketiga hasil supervised yang diulang identik dengan metrik TEST historis pada checksum checkpoint dan manifest training yang sama. Kandidat tunggal untuk pengujian OP3 tetap Hybrid seed 1337 sesuai aturan VAL sebelum TEST; pemilihan ini tidak didasarkan pada hasil TEST.",
        "",
        f"Sebagai konteks eksperimen terdahulu pada split TEST yang sama, rerata mAP50–95 KD murni teacher-only `{pure_kd_map:.4f}` dan teacher FP32 `{teacher_map:.4f}`. Angka historis ini tidak dimasukkan ke perbandingan berpasangan Hybrid–supervised. Hybrid memakai loss deteksi berlabel tambahan, sehingga selisih dengan KD murni tidak mengisolasi satu komponen loss saja.",
        "",
        "## Benchmark diagnostik server",
        "",
        "Benchmark pada satu frame VAL tetap di memori memakai NVIDIA L40, FP32, batch 1, 30 pemanasan dan 200 iterasi ukur. Tabel lengkap ada di T32. Ringkasan berikut adalah median latency tiap checkpoint:",
        "",
        "| seed | Hybrid median ms | Supervised median ms |",
        "| --- | --- | --- |",
    ])
    for seed in SEEDS:
        a = next(row for row in bench if row["seed"] == seed and row["method"] == "hybrid_full")
        b = next(row for row in bench if row["seed"] == seed and row["method"] == "supervised")
        lines.append(f"| {seed} | {a['median_latency_ms']:.3f} | {b['median_latency_ms']:.3f} |")
    lines.extend([
        "",
        "Semua student memakai arsitektur, parameter, dan GFLOPs yang sama. Selisih waktu pada satu urutan benchmark host tidak dapat diatribusikan secara kausal ke KD. Benchmark ini tidak mengukur FPS kamera, latensi end-to-end, CPU, atau RAM OP3. Pengujian tersebut menunggu sesi robot idle dan berjalan dengan frame kamera berlabel yang diperiksa manual.",
        "",
        "## Artefak sumber",
        "",
        f"- Manifest TEST: [`runs/final_test/hybrid_full_official_split_20261022/manifest.json`](../../runs/final_test/hybrid_full_official_split_20261022/manifest.json), SHA-256 `{sha256(TEST)}`.",
        f"- Benchmark: [`runs/benchmarks/hybrid_full_paired_20261022.json`](../../runs/benchmarks/hybrid_full_paired_20261022.json), SHA-256 `{sha256(BENCHMARK)}`.",
        "- Tabel keseluruhan: [T30](../tabel/T30_kd_hybrid_test_berpasangan.md); per kelas: [T31](../tabel/T31_kd_hybrid_test_per_kelas.md); benchmark: [T32](../tabel/T32_kd_hybrid_benchmark_server.md); pelatihan: [T33](../tabel/T33_pelatihan_kd_hybrid_full.md).",
        "- Protokol praevaluasi: [`PROTOKOL_TEST_KD_HYBRID_2026-10-22.md`](../../docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md).",
        "- `best.pt` Hybrid seed 1337 dan 2025 tersimpan pada direktori run lab/server dan hash-nya dicatat di manifest serta registry. Payload bobot dua seed itu belum dipublikasikan ke repo GitHub publik; reproduksi inferensi di checkout lain memerlukan transfer artefak berizin.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def update_manifests() -> None:
    source_paths = [
        "docs/PROTOKOL_TEST_KD_HYBRID_2026-10-22.md",
        "docs/DECISIONS.md",
        "configs/model_registry.yaml",
        "artifacts/advance_vision_dataset_fingerprint.json",
        "scripts/evaluate_hybrid_locked_test.py",
        "scripts/evaluate_locked_test.py",
        "scripts/benchmark_inference.py",
        "scripts/build_kd_hybrid_test_tables.py",
        "runs/final_test/pure_kd_official_split_locked_retry1/manifest.json",
        "runs/final_test/hybrid_full_official_split_20261022/manifest.json",
        "runs/benchmarks/hybrid_full_paired_20261022.json",
    ]
    for seed in SEEDS:
        source_paths.append(f"runs/final_test/hybrid_full_official_split_20261022/hybrid_full_seed{seed}_metrics.json")
        source_paths.append(f"runs/final_test/hybrid_full_official_split_20261022/supervised_seed{seed}_metrics.json")
        run = f"runs/kd_hybrid/yolo11_tiny_hybrid_full_seed{seed}"
        source_paths.extend([f"{run}/manifest.json", f"{run}/results.csv", f"{run}/weights/best.pt"])
        snapshot = f"artifacts/training_source_snapshots/yolo11_tiny_hybrid_full_seed{seed}"
        source_paths.extend([f"{snapshot}/train_kd.py", f"{snapshot}/kd_losses.py", f"{snapshot}/distill_model.py"])
    output_paths = [
        "analisis_performa/INDEKS.md",
        "analisis_performa/lab_server/README.md",
        "analisis_performa/lab_server/HASIL_KD_HYBRID_TEST_2026-10-22.md",
        "analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.csv",
        "analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md",
        "analisis_performa/tabel/T31_kd_hybrid_test_per_kelas.csv",
        "analisis_performa/tabel/T31_kd_hybrid_test_per_kelas.md",
        "analisis_performa/tabel/T32_kd_hybrid_benchmark_server.csv",
        "analisis_performa/tabel/T32_kd_hybrid_benchmark_server.md",
        "analisis_performa/tabel/T33_pelatihan_kd_hybrid_full.csv",
        "analisis_performa/tabel/T33_pelatihan_kd_hybrid_full.md",
    ]
    sources = {path: sha256(ROOT / path) for path in source_paths}
    outputs = {path: sha256(ROOT / path) for path in output_paths}
    curated = read_json(CURATED_MANIFEST)
    curated["hybrid_test_added_on"] = "2026-10-22"
    curated["scope"] = "Curated lab/server tables plus KD Hybrid full three-seed training and VAL, follow-up TEST on the previously used official split, and L40 benchmark; OP3 metrics remain separate."
    notes = [item for item in curated.setdefault("notes", []) if not item.startswith("T30–T31 are a Hybrid full versus supervised")]
    curated["notes"] = notes
    note = "T30–T31 are a Hybrid full versus supervised follow-up TEST comparison on a split previously used for teacher and pure KD; T32 is a fixed-frame L40 benchmark, not OP3 FPS; T33 records three Hybrid training runs."
    if note not in notes:
        notes.append(note)
    availability_note = "Hybrid best.pt payloads for seeds 1337 and 2025 remain local to the lab/server pending explicit approval for public publication; their SHA-256 values are recorded."
    if availability_note not in notes:
        notes.append(availability_note)
    curated.setdefault("sources_sha256", {}).update(sources)
    curated.setdefault("outputs_sha256", {}).update(outputs)
    CURATED_MANIFEST.write_text(json.dumps(curated, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    generator = read_json(GENERATOR_MANIFEST)
    generator["kd_hybrid_test_2026_10_22"] = {
        "status": "complete",
        "scope": "Three Hybrid full training runs, three paired Hybrid and supervised seeds on official TEST, and a six-model L40 benchmark; TEST had historical use before this extension.",
        "pretest_protocol_commit": "084dfbaa4bd8c8ce7971f8d43aabc41fff1bdc45",
        "artifact_availability": "Hybrid best.pt seeds 1337 and 2025 are available in the lab workspace but are not included in the public repository pending explicit publication approval.",
        "sources_sha256": sources,
        "outputs_sha256": outputs,
    }
    GENERATOR_MANIFEST.write_text(json.dumps(generator, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    test, historical, benchmark = read_json(TEST), read_json(HISTORICAL), read_json(BENCHMARK)
    verify_sources(test, historical, benchmark)
    TABLES.mkdir(parents=True, exist_ok=True)
    overall = summary_rows(test)
    per_class = [row for name in CLASSES for row in summary_rows(test, name)]
    bench = benchmark_rows(benchmark)
    write_csv(TABLES / "T30_kd_hybrid_test_berpasangan.csv", overall)
    markdown_summary(TABLES / "T30_kd_hybrid_test_berpasangan.md", overall,
                     "T30. KD Hybrid full vs supervised pada TEST",
                     "Split TEST resmi 592 gambar. Semua tiga seed berpasangan; Δ = Hybrid full − supervised. Protokol dan checkpoint dikunci berdasarkan VAL sebelum evaluasi Hybrid.")
    write_csv(TABLES / "T31_kd_hybrid_test_per_kelas.csv", per_class)
    class_counts = {
        name: test["models"]["hybrid_full_seed42"]["test_metrics"]["per_class"][name]["ground_truth_count"]
        for name in CLASSES
    }
    markdown_summary(TABLES / "T31_kd_hybrid_test_per_kelas.md", per_class,
                     "T31. KD Hybrid full vs supervised pada TEST per kelas",
                     f"Split TEST resmi: ball {class_counts['ball']} anotasi, gawang {class_counts['gawang']}, robot {class_counts['robot']}. Metrik AP dan operating point mengikuti protokol TEST yang dikunci.", per_class=True)
    write_csv(TABLES / "T32_kd_hybrid_benchmark_server.csv", bench)
    write_benchmark_markdown(TABLES / "T32_kd_hybrid_benchmark_server.md", bench)
    training = training_rows()
    write_csv(TABLES / "T33_pelatihan_kd_hybrid_full.csv", training)
    write_training_markdown(TABLES / "T33_pelatihan_kd_hybrid_full.md", training)
    write_report(test, historical, overall, per_class, bench)
    update_manifests()
    print(f"Built T30–T33 and {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
