"""Muat registry model dan validasi hash checkpoint sebelum inferensi."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "configs/model_registry.yaml"
DEFAULT_LOCAL_REGISTRY = ROOT / "configs/model_registry_local.yaml"


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


def load_local_overrides(
    registry: dict[str, Any], local_registry_path: Path | None = None
) -> dict[str, Path]:
    """Baca path checkpoint lokal opsional tanpa mengubah hash acuan."""
    path = local_registry_path or DEFAULT_LOCAL_REGISTRY
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Format registry lokal harus berupa pemetaan nama ke path: {path}")
    model_names = registry["models"]
    overrides: dict[str, Path] = {}
    for name, value in data.items():
        if name not in model_names:
            raise ValueError(f"Model override lokal {name!r} tidak ada di registry utama.")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Path override lokal untuk {name!r} harus berupa string non-kosong.")
        overrides[name] = resolve_registered_path(value)
    return overrides


def checkpoint_for_variant(
    variant: str,
    registry_path: Path = DEFAULT_REGISTRY,
    *,
    local_registry_path: Path | None = None,
) -> tuple[str, Path]:
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
    model_name = str(entry.get("model", entry_name))
    overrides = load_local_overrides(registry, local_registry_path)
    path = overrides.get(model_name) or overrides.get(entry_name) or resolve_registered_path(entry["checkpoint"])
    return entry_name, path


def validate_checkpoint(
    checkpoint: str | Path,
    *,
    label: str | None = None,
    registry_path: Path = DEFAULT_REGISTRY,
    local_registry_path: Path | None = None,
) -> tuple[str, dict[str, Any]]:
    """Pastikan path dan hash cocok dengan entri model atau alias yang terdaftar."""
    registry = load_registry(registry_path)
    candidate = Path(checkpoint).expanduser().resolve()
    overrides = load_local_overrides(registry, local_registry_path)
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
        local_path = overrides.get(model_name) or overrides.get(entry_name)
        using_local_override = local_path == candidate and local_path != registered_path
        if registered_path != candidate and not using_local_override:
            continue
        if not candidate.is_file():
            raise FileNotFoundError(f"Checkpoint terdaftar tidak ditemukan: {candidate}")
        actual_hash = sha256_file(candidate)
        expected_hash = str(entry["sha256"])
        if actual_hash != expected_hash:
            raise ValueError(
                f"Hash checkpoint {entry_name!r} tidak cocok: expected={expected_hash}, actual={actual_hash}"
            )
        resolved_entry = dict(entry)
        resolved_entry["local_override_used"] = using_local_override
        resolved_entry["local_override_path"] = str(candidate) if using_local_override else None
        return model_name, resolved_entry
    raise ValueError(f"Checkpoint tidak terdaftar: {candidate}")
