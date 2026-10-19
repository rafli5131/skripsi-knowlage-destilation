"""Pemeriksaan runtime yang dikunci untuk eksperimen pelatihan."""

from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
from typing import Any

import ultralytics
import yaml


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    """Hitung SHA-256 berkas secara bertahap."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_training_runtime(config_path: Path | None = None) -> dict[str, Any]:
    """Tolak versi Ultralytics atau sumber DistillationModel yang berubah."""
    config_path = (config_path or ROOT / "configs/runtime_compatibility.yaml").resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    expected_version = str(config["ultralytics_version"])
    if str(ultralytics.__version__) != expected_version:
        raise RuntimeError(
            f"Ultralytics {ultralytics.__version__} terpasang, tetapi eksperimen dikunci ke {expected_version}."
        )

    module = importlib.import_module("ultralytics.nn.distill_model")
    source = Path(str(module.__file__)).resolve()
    actual_hash = sha256_file(source)
    expected_hash = str(config["distill_model_sha256"])
    if actual_hash != expected_hash:
        raise RuntimeError(
            "SHA-256 ultralytics/nn/distill_model.py berbeda dari konfigurasi: "
            f"expected={expected_hash}, actual={actual_hash}, path={source}"
        )
    return {
        "ultralytics_version": str(ultralytics.__version__),
        "distill_model_path": str(source),
        "distill_model_sha256": actual_hash,
        "compatibility_config": str(config_path),
        "compatibility_config_sha256": sha256_file(config_path),
    }
