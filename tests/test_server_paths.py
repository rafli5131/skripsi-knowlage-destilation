import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import server_paths  # noqa: E402


def load_driver():
    spec = importlib.util.spec_from_file_location("t42_driver_test", SCRIPTS / "run_t42_teacher_ablation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_env(**values):
    env = {key: value for key, value in os.environ.items()
           if key not in {"KD_TRAIN_PYTHON", "KD_DATA_ROOT", "T42_ATTEMPT"}}
    env.update(values)
    return patch.dict(os.environ, env, clear=True)


class ServerPathTests(unittest.TestCase):
    def test_legacy_layout_matches_original_paths(self):
        root = Path("/repo")
        with clean_env():
            layout = server_paths.t42_layout(root)
        self.assertEqual(layout.project, root / "runs/kd_teacher_ablation")
        self.assertEqual(layout.private, root / "models_local/teacher_ablation_t42/training")
        self.assertEqual(layout.pretrained, root / "models_local/teacher_ablation_t42/pretrained")
        self.assertEqual(layout.evaluation, root / "runs/val_ablation/teacher_yolo11s_t42_20261024")
        self.assertEqual(layout.status, root / "runs/kd_teacher_ablation/t42_status.jsonl")
        self.assertEqual(layout.teacher_run_name("n"), "teacher_yolo11n_seed42_retry1")
        self.assertEqual(layout.teacher_run_name("s"), "teacher_yolo11s_seed42")
        self.assertEqual(layout.student_config_path("x").name, "t42_x.yaml")

    def test_attempt_layout_is_separate(self):
        root = Path("/repo")
        with clean_env(T42_ATTEMPT="server2"):
            layout = server_paths.t42_layout(root)
        self.assertEqual(layout.project, root / "runs/kd_teacher_ablation/server2")
        self.assertEqual(layout.private, root / "models_local/teacher_ablation_t42/server2/training")
        self.assertEqual(layout.pretrained, root / "models_local/teacher_ablation_t42/pretrained")
        self.assertEqual(layout.evaluation, root / "runs/val_ablation/teacher_yolo11s_t42_server2")
        self.assertEqual(layout.teacher_run_name("n"), "teacher_yolo11n_seed42")
        self.assertEqual(layout.student_config_path("x").name, "t42_server2_x.yaml")

    def test_invalid_attempt_rejected(self):
        with clean_env(T42_ATTEMPT="../escape"):
            with self.assertRaises(ValueError):
                server_paths.t42_layout(Path("/repo"))

    def test_rebase_only_when_data_root_is_set(self):
        legacy = server_paths.LEGACY_DATA_ROOT + "/valid/images"
        with clean_env():
            self.assertEqual(server_paths.rebase_data_path(legacy), Path(legacy))
        with clean_env(KD_DATA_ROOT="/data/av"):
            self.assertEqual(server_paths.rebase_data_path(legacy), Path("/data/av/valid/images"))
            self.assertEqual(server_paths.rebase_data_path("/other/valid/images"), Path("/other/valid/images"))
            self.assertEqual(server_paths.data_root(), Path("/data/av"))

    def test_training_python(self):
        with clean_env(KD_TRAIN_PYTHON="/env/bin/python"):
            self.assertEqual(server_paths.training_python(), "/env/bin/python")
        with clean_env(), patch.object(server_paths, "LEGACY_PYTHON", "/does/not/exist"):
            self.assertEqual(server_paths.training_python(), sys.executable)

    def test_evaluation_data_yaml_legacy_returns_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.yaml"
            source.write_text("train: /x/train\nval: /x/val\n", encoding="utf-8")
            with clean_env():
                self.assertEqual(server_paths.evaluation_data_yaml(source, Path(directory) / "out"), source)
            self.assertFalse((Path(directory) / "out").exists())

    def test_evaluation_data_yaml_rebases_all_splits(self):
        legacy = server_paths.LEGACY_DATA_ROOT
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "data.yaml"
            source.write_text(yaml.safe_dump({
                "path": "/ignored", "train": f"{legacy}/train/images", "val": f"{legacy}/valid/images",
                "nc": 3, "names": {0: "ball", 1: "gawang", 2: "robot"}}), encoding="utf-8")
            with clean_env(KD_DATA_ROOT="/data/av"):
                target = server_paths.evaluation_data_yaml(source, Path(directory) / "out")
            resolved = yaml.safe_load(target.read_text(encoding="utf-8"))
            original = yaml.safe_load(source.read_text(encoding="utf-8"))
        self.assertEqual(target.name, ".resolved_data_eval.yaml")
        self.assertEqual(resolved["train"], "/data/av/train/images")
        self.assertEqual(resolved["val"], "/data/av/valid/images")
        self.assertNotIn("path", resolved)
        self.assertEqual(resolved["names"], {0: "ball", 1: "gawang", 2: "robot"})
        self.assertEqual(original["train"], f"{legacy}/train/images")  # YAML sumber tidak diubah


class DriverTests(unittest.TestCase):
    def prepare(self, root: Path, attempt: str):
        (root / "configs").mkdir(parents=True)
        (root / "configs/kd_hybrid_full.yaml").write_text(yaml.safe_dump({
            "teacher_checkpoint": "/old/teacher.pt",
            "run": {"project": "runs/kd_hybrid", "name": "x"},
            "training": {"seed": 42},
        }), encoding="utf-8")
        values = {"T42_ATTEMPT": attempt} if attempt else {}
        with clean_env(**values):
            driver = load_driver()
            layout = server_paths.t42_layout(root)
        driver.ROOT, driver.LAYOUT = root, layout
        driver.PROJECT, driver.PRIVATE = layout.project, layout.private
        driver.EVAL, driver.STATUS = layout.evaluation, layout.status
        return driver

    def test_student_config_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            driver = self.prepare(root, "server2")
            path = driver.student_config("n", 1337)
            config = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(path.name, "t42_server2_student_teacher_yolo11n_seed1337.yaml")
        self.assertEqual(config["run"], {"project": "runs/kd_teacher_ablation/server2",
                                         "name": "student_teacher_yolo11n_seed1337"})
        self.assertEqual(config["teacher_checkpoint"], str(
            root / "models_local/teacher_ablation_t42/server2/training/teacher_yolo11n_seed42/weights/best.pt"))
        self.assertEqual(config["training"]["seed"], 1337)

    def test_student_config_legacy_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            driver = self.prepare(root, "")
            path = driver.student_config("n", 42)
            config = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(path.name, "t42_student_teacher_yolo11n_seed42.yaml")
        self.assertEqual(config["run"]["project"], "runs/kd_teacher_ablation")
        self.assertTrue(config["teacher_checkpoint"].endswith(
            "models_local/teacher_ablation_t42/training/teacher_yolo11n_seed42_retry1/weights/best.pt"))

    def test_existing_attempt_status_is_not_resumed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            driver = self.prepare(root, "server2")
            driver.STATUS.parent.mkdir(parents=True)
            driver.STATUS.write_text('{"event": "t42_started"}\n', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "sudah ada"):
                driver.main()


if __name__ == "__main__":
    unittest.main()
