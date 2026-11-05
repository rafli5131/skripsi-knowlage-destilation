"""Path server training yang dapat diganti lewat variabel lingkungan.

Nilai bawaan sama dengan server lama (`/mnt/nas-hpg9/rafli5131`), sehingga perilaku
skrip lama tidak berubah bila variabel lingkungan tidak diisi. Untuk server baru:

- ``KD_TRAIN_PYTHON``: interpreter Python environment training.
- ``KD_DATA_ROOT``: akar dataset Advance Vision (berisi ``train/``, ``valid/``, ``test/``).
- ``T42_ATTEMPT``: nama percobaan T42 baru, misalnya ``server2``. Kosong berarti
  percobaan T42 lama dengan path dan nama run aslinya.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LEGACY_PYTHON = "/mnt/nas-hpg9/rafli5131/rafli/advance_vision/.venv/bin/python"
LEGACY_DATA_ROOT = "/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human"
_ATTEMPT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def training_python() -> str:
    """Interpreter untuk subproses training: variabel lingkungan, server lama, lalu interpreter aktif."""
    configured = os.environ.get("KD_TRAIN_PYTHON", "").strip()
    if configured:
        return configured
    return LEGACY_PYTHON if Path(LEGACY_PYTHON).exists() else sys.executable


def data_root() -> Path:
    """Akar dataset Advance Vision; bawaan path server lama."""
    configured = os.environ.get("KD_DATA_ROOT", "").strip()
    return Path(configured or LEGACY_DATA_ROOT)


def rebase_data_path(path: str | Path) -> Path:
    """Pindahkan path di bawah akar dataset lama ke ``KD_DATA_ROOT`` bila variabel itu diisi."""
    path = Path(path)
    configured = os.environ.get("KD_DATA_ROOT", "").strip()
    if not configured:
        return path
    legacy = Path(LEGACY_DATA_ROOT)
    try:
        relative = path.relative_to(legacy)
    except ValueError:
        return path
    return Path(configured) / relative


def t42_attempt() -> str:
    """Nama percobaan T42 dari ``T42_ATTEMPT``; string kosong berarti percobaan lama."""
    value = os.environ.get("T42_ATTEMPT", "").strip()
    if value and not _ATTEMPT_PATTERN.fullmatch(value):
        raise ValueError("T42_ATTEMPT hanya boleh berisi huruf, angka, '_' atau '-', maksimal 64 karakter")
    return value


@dataclass(frozen=True)
class T42Layout:
    """Lokasi keluaran satu percobaan T42."""

    attempt: str
    project: Path
    private: Path
    pretrained: Path
    evaluation: Path
    configs: Path

    @property
    def status(self) -> Path:
        return self.project / "t42_status.jsonl"

    def teacher_run_name(self, variant: str) -> str:
        if variant not in {"n", "s"}:
            raise ValueError(f"Varian teacher tidak dikenal: {variant!r}")
        # Percobaan lama: upaya pertama YOLO11n berhenti sebelum epoch 1 dan disimpan untuk audit.
        if not self.attempt and variant == "n":
            return "teacher_yolo11n_seed42_retry1"
        return f"teacher_yolo11{variant}_seed42"

    def student_config_path(self, run_name: str) -> Path:
        prefix = f"t42_{self.attempt}_" if self.attempt else "t42_"
        return self.configs / f"{prefix}{run_name}.yaml"


def t42_layout(root: Path) -> T42Layout:
    """Susun path T42; tanpa ``T42_ATTEMPT`` hasilnya identik dengan path lama."""
    attempt = t42_attempt()
    base_private = root / "models_local/teacher_ablation_t42"
    if not attempt:
        return T42Layout(
            attempt="",
            project=root / "runs/kd_teacher_ablation",
            private=base_private / "training",
            pretrained=base_private / "pretrained",
            evaluation=root / "runs/val_ablation/teacher_yolo11s_t42_20261024",
            configs=root / "configs",
        )
    return T42Layout(
        attempt=attempt,
        project=root / "runs/kd_teacher_ablation" / attempt,
        private=base_private / attempt / "training",
        pretrained=base_private / "pretrained",
        evaluation=root / "runs/val_ablation" / f"teacher_yolo11s_t42_{attempt}",
        configs=root / "configs",
    )
