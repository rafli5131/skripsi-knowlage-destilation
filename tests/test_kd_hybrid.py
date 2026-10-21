"""Pemeriksaan loss KD hibrida pada CPU dan batch kecil."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import torch
from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG, get_cfg
from ultralytics.nn.distill_model import DistillationModel


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import train_kd  # noqa: E402


def make_wrapper(seed: int = 42) -> DistillationModel:
    """Bangun pasangan model yang sama dengan ukuran input 64 pada CPU."""
    torch.manual_seed(seed)
    student = YOLO(str(ROOT / "models/yolo11_tiny_kd.yaml"), task="detect").model
    student.args = get_cfg(DEFAULT_CFG, {"imgsz": 64, "dis": 1.0})
    teacher = ROOT.parent / "rafli/advance_vision/artifacts/checkpoints/fp32/best.pt"
    if not teacher.is_file():
        teacher = Path("/mnt/nas-hpg9/rafli5131/rafli/advance_vision/artifacts/checkpoints/fp32/best.pt")
    return DistillationModel(str(teacher), student).train()


def make_batch() -> dict[str, torch.Tensor]:
    """Buat satu gambar dan satu label kotak tetap."""
    generator = torch.Generator().manual_seed(20261021)
    return {"img": torch.rand((1, 3, 64, 64), generator=generator),
            "batch_idx": torch.tensor([0.0]), "cls": torch.tensor([[0.0]]),
            "bboxes": torch.tensor([[0.5, 0.5, 0.25, 0.25]])}


PURE_CONFIG = {"feature_weight": 1.0, "box_weight": 1.0, "class_weight": 1.0,
               "temperature": 2.0, "mode": "pure_v4"}


class HybridLossTests(unittest.TestCase):
    """Bandingkan loss hibrida dengan baseline historis."""

    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def setUp(self) -> None:
        DistillationModel.loss = train_kd.ORIGINAL_DISTILLATION_LOSS

    def tearDown(self) -> None:
        DistillationModel.loss = train_kd.ORIGINAL_DISTILLATION_LOSS

    def test_pure_v4_matches_snapshot(self) -> None:
        """Pastikan loss pure_v4 identik dengan skrip run lama."""
        snapshot_path = ROOT / "artifacts/training_source_snapshots/yolo11_tiny_pure_kd_v4_seed1337/train_kd.py"
        spec = importlib.util.spec_from_file_location("historical_train_kd", snapshot_path)
        assert spec and spec.loader
        snapshot = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(snapshot)
        current = make_wrapper()
        train_kd.install_teacher_only_kd_loss(PURE_CONFIG)
        current_loss, _ = current.loss(make_batch())
        historical = make_wrapper()
        snapshot.install_teacher_only_kd_loss(PURE_CONFIG)
        historical_loss, _ = historical.loss(make_batch())
        self.assertTrue(torch.equal(current_loss, historical_loss))

    def test_hybrid_full_zero_kd_equals_detection_loss(self) -> None:
        """KD berbobot nol mempertahankan loss deteksi berlabel."""
        wrapper = make_wrapper()
        config = dict(PURE_CONFIG, feature_weight=0.0, box_weight=0.0, class_weight=0.0)
        train_kd.install_hybrid_full_kd_loss(config)
        captured: list[torch.Tensor] = []
        original_student_loss = wrapper.student_model.loss

        def capture(batch, preds=None):
            loss, items = original_student_loss(batch, preds)
            captured.append(loss.detach().clone())
            return loss, items

        wrapper.student_model.loss = capture
        values, items = wrapper.loss(make_batch())
        self.assertEqual(len(captured), 1)
        self.assertTrue(torch.equal(values[:-1].detach(), captured[0]))
        self.assertEqual(float(values[-1]), 0.0)
        self.assertIn("dis_loss", items)
        self.assertEqual(tuple(items["dis_loss"].shape), (1,))

    def test_hybrid_full_kd_equals_pure_v4_and_gradients(self) -> None:
        """Komponen KD sama dengan pure_v4, dan teacher tetap beku."""
        hybrid = make_wrapper()
        train_kd.install_hybrid_full_kd_loss(PURE_CONFIG)
        hybrid_values, _ = hybrid.loss(make_batch())
        pure = make_wrapper()
        train_kd.install_teacher_only_kd_loss(PURE_CONFIG)
        pure_value, _ = pure.loss(make_batch())
        self.assertTrue(torch.equal(hybrid_values[-1], pure_value))
        hybrid_values.sum().backward()
        self.assertTrue(all(parameter.grad is None for parameter in hybrid.teacher_model.parameters()))
        self.assertTrue(any(parameter.grad is not None and parameter.grad.abs().sum() > 0
                            for parameter in hybrid.student_model.parameters()))
        self.assertTrue(any(parameter.grad is not None and parameter.grad.abs().sum() > 0
                            for parameter in hybrid.projector.parameters()))

    def test_hybrid_feature_uses_original_loss(self) -> None:
        """Mode fitur tidak memasang penimpaan pada DistillationModel."""
        self.assertIs(DistillationModel.loss, train_kd.ORIGINAL_DISTILLATION_LOSS)

    def test_hybrid_full_validation_log_shape(self) -> None:
        """Nilai dis_loss pada validasi tetap berbentuk satu elemen."""
        wrapper = make_wrapper()
        train_kd.install_hybrid_full_kd_loss(PURE_CONFIG)
        wrapper.eval()
        values, items = wrapper.loss(make_batch())
        self.assertEqual(tuple(items["dis_loss"].shape), (1,))
        self.assertEqual(values.numel(), len(items))


if __name__ == "__main__":
    unittest.main()
