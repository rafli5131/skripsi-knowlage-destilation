"""Muat registry model dan validasi hash checkpoint sebelum inferensi."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "configs/model_registry.yaml"


def sha256_file(path: Path) -> str:
    """Hitung SHA-256 berkas secara bertahap."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    """Baca registry model dari YAML."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data.get("models"), dict) or not isinstance(data.get("aliases", {}), dict):
        raise ValueError(f"Format registry model tidak valid: {path}")
    return data


def resolve_registered_path(value: str | Path) -> Path:
    """Resolve path relatif terhadap akar repository."""
    path = Path(value).expanduser()
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def checkpoint_for_variant(variant: str, registry_path: Path = DEFAULT_REGISTRY) -> tuple[str, Path]:
    """Pilih checkpoint default yang terdaftar untuk varian runtime."""
    registry = load_registry(registry_path)
    entry_names = {
        "kd": "op3_default",
        "hybrid": "hybrid_full_seed1337",
        "supervised": "supervised_seed42",
        "teacher": "teacher_fp32",
    }
    if variant not in entry_names:
        raise ValueError(f"Varian model tidak dikenal: {variant!r}")
    entry_name = entry_names[variant]
    entry = registry.get("aliases", {}).get(entry_name) or registry["models"].get(entry_name)
    if entry is None:
        raise ValueError(f"Checkpoint default {entry_name!r} tidak tercatat di {registry_path}.")
    return entry_name, resolve_registered_path(entry["checkpoint"])


def validate_checkpoint(
    checkpoint: str | Path,
    *,
    label: str | None = None,
    registry_path: Path = DEFAULT_REGISTRY,
) -> tuple[str, dict[str, Any]]:
    """Pastikan path dan hash cocok dengan entri model atau alias yang terdaftar."""
    registry = load_registry(registry_path)
    candidate = Path(checkpoint).expanduser().resolve()
    entries: dict[str, tuple[str, dict[str, Any]]] = {
        **{name: (name, value) for name, value in registry["models"].items()},
        **{
            name: (str(value.get("model", name)), value)
            for name, value in registry.get("aliases", {}).items()
        },
    }
    if label is not None:
        if label not in entries:
            raise ValueError(f"Model {label!r} tidak tercatat di {registry_path}.")
        selected = {label: entries[label]}
    else:
        selected = entries

    for entry_name, (model_name, entry) in selected.items():
        registered_path = resolve_registered_path(entry["checkpoint"])
        if registered_path != candidate:
            continue
        if not candidate.is_file():
            raise FileNotFoundError(f"Checkpoint registry tidak ditemukan: {candidate}")
        actual_hash = sha256_file(candidate)
        expected_hash = str(entry["sha256"])
        if actual_hash != expected_hash:
            raise ValueError(
                f"Hash checkpoint {entry_name!r} tidak cocok: expected={expected_hash}, actual={actual_hash}"
            )
        return model_name, entry
    raise ValueError(f"Checkpoint tidak terdaftar: {candidate}")
