"""Benchmark full Ultralytics inference on one fixed validation image."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import ultralytics
import yaml
from ultralytics import YOLO
from ultralytics.utils.torch_utils import get_flops


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RUNTIME_VERSIONS = {
    "python": "3.11.2",
    "numpy": "1.26.4",
    "torch": "2.4.1+cu121",
    "ultralytics": "8.4.130",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        metavar="LABEL=CHECKPOINT",
        help="Named checkpoint paths to compare under identical inference settings.",
    )
    parser.add_argument("--data", type=Path, default=ROOT / "configs/data_train_val.yaml")
    parser.add_argument("--image", type=Path, help="Optional fixed image; must be inside the VAL images directory.")
    parser.add_argument("--device", default="0", help="Ultralytics device, e.g. 0 or cpu.")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "runs/benchmarks/inference_speed.json",
        help="Output JSON path; existing files are preserved.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def synchronize(device: str) -> None:
    if device != "cpu":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable in this process.")
        index = int(device.split(":")[-1]) if device.replace("cuda:", "").isdigit() else 0
        torch.cuda.synchronize(index)


def runtime_device_metadata(device: str) -> dict[str, Any]:
    requested = str(device)
    metadata: dict[str, Any] = {
        "requested_device": requested,
        "platform": platform.platform(),
        "cuda_available": torch.cuda.is_available(),
        "cuda_runtime_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "visible_cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
    if requested.lower() == "cpu":
        metadata.update(
            {
                "device_type": "cpu",
                "device_name": platform.processor() or platform.machine(),
            }
        )
        return metadata
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable in this process.")

    token = requested.split(",", maxsplit=1)[0].strip().lower()
    if token in {"", "cuda"}:
        index = torch.cuda.current_device()
    elif token.startswith("cuda:"):
        index = int(token.split(":", maxsplit=1)[1])
    else:
        index = int(token)
    properties = torch.cuda.get_device_properties(index)
    metadata.update(
        {
            "device_type": "cuda",
            "logical_device_index": index,
            "device_name": torch.cuda.get_device_name(index),
            "total_memory_bytes": int(properties.total_memory),
            "compute_capability": f"{properties.major}.{properties.minor}",
        }
    )
    return metadata


def resolve_validation_image(data_yaml: Path, image_arg: Path | None) -> Path:
    payload = yaml.safe_load(data_yaml.read_text(encoding="utf-8")) or {}
    if "test" in payload:
        raise ValueError("Benchmark data YAML must not expose TEST; this script uses VAL images only.")
    val_value = payload.get("val")
    if not isinstance(val_value, str) or not val_value:
        raise ValueError(f"Data YAML has no validation image path: {data_yaml}")
    val_dir = Path(val_value).expanduser()
    if not val_dir.is_absolute():
        dataset_root = Path(payload.get("path") or data_yaml.parent).expanduser()
        if not dataset_root.is_absolute():
            dataset_root = (data_yaml.parent / dataset_root).resolve()
        val_dir = dataset_root / val_dir
    val_dir = val_dir.resolve()
    if not val_dir.is_dir():
        raise ValueError(f"Validation image directory does not exist: {val_dir}")

    if image_arg is not None:
        image = image_arg.expanduser().resolve()
        if not image.is_file() or image.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError(f"Benchmark input is not a supported image file: {image}")
        if not image.is_relative_to(val_dir):
            raise ValueError(f"Benchmark image must be inside VAL images: {image}")
        return image

    images = sorted(path for path in val_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise ValueError(f"Validation directory has no images: {val_dir}")
    return images[0]


def parse_models(specifications: list[str]) -> list[tuple[str, Path]]:
    models = []
    labels = set()
    for specification in specifications:
        label, separator, path_value = specification.partition("=")
        if not separator or not label or not path_value:
            raise ValueError(f"Model must be specified as LABEL=CHECKPOINT: {specification!r}")
        if label in labels:
            raise ValueError(f"Model labels must be unique: {label!r}")
        labels.add(label)
        checkpoint = Path(path_value).expanduser().resolve()
        if not checkpoint.is_file():
            raise FileNotFoundError(f"Checkpoint does not exist: {checkpoint}")
        models.append((label, checkpoint))
    return models


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def benchmark_one(label: str, checkpoint: Path, image: Path, frame: Any, args: argparse.Namespace) -> dict[str, Any]:
    model = YOLO(str(checkpoint), task="detect")
    parameters = sum(parameter.numel() for parameter in model.model.parameters())
    flops_gflops = float(get_flops(model.model, imgsz=args.imgsz))

    def infer():
        return model.predict(
            source=frame,
            imgsz=args.imgsz,
            batch=1,
            device=args.device,
            half=False,
            conf=0.001,
            iou=0.7,
            verbose=False,
            save=False,
            plots=False,
        )

    for _ in range(args.warmup):
        infer()
    synchronize(args.device)
    times_ms = []
    last_result = None
    for _ in range(args.iterations):
        synchronize(args.device)
        started = time.perf_counter()
        result = infer()
        synchronize(args.device)
        times_ms.append((time.perf_counter() - started) * 1000)
        last_result = result[0]

    mean_ms = statistics.mean(times_ms)
    record = {
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256_file(checkpoint),
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "parameters": parameters,
        "flops_gflops": flops_gflops if flops_gflops > 0 else None,
        "flops_method": "Ultralytics get_flops using THOP at batch 1 and the requested image size",
        "latency_ms": {
            "mean": mean_ms,
            "median": statistics.median(times_ms),
            "p95": percentile(times_ms, 0.95),
            "images_per_second": 1000.0 / mean_ms,
            "samples": times_ms,
        },
        "last_iteration_detection_count": int(len(last_result.boxes)) if last_result is not None else 0,
    }
    del model
    if args.device != "cpu":
        torch.cuda.empty_cache()
    return record


def main() -> int:
    args = parse_args()
    runtime_versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": str(torch.__version__),
        "ultralytics": ultralytics.__version__,
    }
    if runtime_versions != EXPECTED_RUNTIME_VERSIONS:
        raise RuntimeError(f"Benchmark runtime differs from the frozen environment: {runtime_versions!r}")
    if args.warmup < 0 or args.iterations < 2:
        raise ValueError("warmup must be nonnegative and iterations must be at least 2.")
    if (args.device, args.imgsz, args.warmup, args.iterations) != ("0", 640, 30, 200):
        raise ValueError("Inference benchmark settings differ from the locked protocol.")
    data_yaml = args.data.expanduser().resolve()
    if not data_yaml.is_file():
        raise FileNotFoundError(f"Data YAML does not exist: {data_yaml}")
    image = resolve_validation_image(data_yaml, args.image)
    frame = cv2.imread(str(image))
    if frame is None:
        raise ValueError(f"OpenCV could not decode the validation image: {image}")
    models = parse_models(args.models)
    output = args.output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing benchmark results: {output}")

    runtime = runtime_device_metadata(args.device)
    if runtime.get("device_name") != "NVIDIA L40":
        raise RuntimeError("Locked inference benchmark must run on the recorded NVIDIA L40 device.")
    if args.device != "cpu":
        synchronize(args.device)

    results = {}
    for label, checkpoint in models:
        print(f"Benchmarking {label}: {checkpoint}", flush=True)
        results[label] = benchmark_one(label, checkpoint, image, frame, args)
        print(f"  mean={results[label]['latency_ms']['mean']:.3f} ms, p95={results[label]['latency_ms']['p95']:.3f} ms", flush=True)

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "diagnostic fixed-image inference benchmark; not a deployment-platform claim",
        "benchmark_script": str(Path(__file__).resolve()),
        "benchmark_script_sha256": sha256_file(Path(__file__).resolve()),
        "data_yaml": str(data_yaml),
        "data_yaml_sha256": sha256_file(data_yaml),
        "validation_image": str(image),
        "validation_image_sha256": sha256_file(image),
        "settings": {
            "device": args.device,
            "device_name": runtime["device_name"],
            "batch": 1,
            "imgsz": args.imgsz,
            "precision": "FP32",
            "confidence": 0.001,
            "iou": 0.7,
            "warmup_iterations": args.warmup,
            "timed_iterations": args.iterations,
            "input": "same validation frame decoded once to in-memory OpenCV BGR; disk read excluded",
            "timing_scope": "YOLO.predict including preprocessing, inference, and NMS; checkpoint loading excluded",
        },
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "opencv": cv2.__version__,
            "torch": torch.__version__,
            "ultralytics": ultralytics.__version__,
        },
        "runtime": runtime,
        "models": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Benchmark manifest: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
