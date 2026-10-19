"""Load repository path and run-name configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_CONFIG = ROOT / "configs/run_registry.yaml"


def load_run_config(path: Path = DEFAULT_RUN_CONFIG) -> dict[str, Any]:
    """Read the shared run configuration."""
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Run registry must contain a YAML mapping: {path}")
    return value


def resolve_repo_path(value: str | Path) -> Path:
    """Resolve repository-relative or absolute configured paths."""
    path = Path(value).expanduser()
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
