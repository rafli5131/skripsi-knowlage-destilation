import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("continuation_attempt", SCRIPTS / "continue_t42_attempt_after_eval_fix.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class StageOrderTests(unittest.TestCase):
    def run_main(self, fail=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run").mkdir()
            driver = Mock(ROOT=root, PROJECT=root / "run", PRIVATE=root, PYTHON="python", DATA_ROOT="data",
                          LAYOUT=Mock(attempt="server2"))
            driver.student_config.return_value = root / "config.yaml"
            driver.teacher_run_name.side_effect = lambda variant: f"teacher_yolo11{variant}_seed42"
            if fail:
                driver.evaluate.side_effect = RuntimeError("eval failed")
            with patch.object(module, "prepare", return_value=(driver, "verified")), \
                    patch("sys.argv", ["continue", "--execute"]):
                if fail:
                    with self.assertRaisesRegex(RuntimeError, "eval failed"):
                        module.main()
                else:
                    module.main()
            return driver

    def test_retry_eval_first_then_remaining_stages(self):
        driver = self.run_main()
        first = driver.evaluate.call_args_list[0]
        self.assertEqual(first.args[0], "teacher_yolo11n_seed42")
        self.assertEqual(first.kwargs["step_name"], "eval_teacher_yolo11n_seed42_retry1")
        names = [call.args[0] for call in driver.run_step.call_args_list]
        self.assertEqual(names, ["train_teacher_yolo11s_seed42"]
                         + [f"train_student_teacher_yolo11{v}_seed{s}" for v in ("n", "s") for s in (42, 1337, 2025)]
                         + ["build_t42"])
        self.assertEqual(driver.evaluate.call_count, 8)
        self.assertEqual(driver.record.call_args_list[0].args[0], "t42_continued")
        self.assertEqual(driver.record.call_args.args[0], "t42_complete")

    def test_failure_is_recorded(self):
        driver = self.run_main(fail=True)
        driver.run_step.assert_not_called()
        self.assertEqual(driver.record.call_args.args[0], "t42_failed")


class PreflightTests(unittest.TestCase):
    """Susun root tiruan yang meniru kondisi percobaan server2 setelah evaluasi gagal."""

    def build(self, directory, mutate=None):
        root = Path(directory)
        shutil.copytree(SCRIPTS, root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        (root / "configs").mkdir()
        recipe = b"teacher_checkpoint: /old\nrun: {project: x, name: y}\ntraining: {seed: 42}\n"
        (root / "configs/kd_hybrid_full.yaml").write_bytes(recipe)
        (root / "scripts/evaluate_val_ablation.py").write_text("evaluation_data_yaml\n", encoding="utf-8")
        project = root / "runs/kd_teacher_ablation/server2"
        (project / "logs").mkdir(parents=True)
        run = root / "models_local/teacher_ablation_t42/server2/training/teacher_yolo11n_seed42"
        (run / "weights").mkdir(parents=True)
        best = b"fake-best"
        (run / "weights/best.pt").write_bytes(best)
        (run / "manifest.json").write_text(json.dumps({"status": "complete", "teacher_best_sha256": sha(best)}), encoding="utf-8")
        pre = root / "models_local/teacher_ablation_t42/pretrained"
        pre.mkdir(parents=True)
        (pre / "yolo11s.pt").write_bytes(b"fake-s")
        legacy = "/mnt/nas-hpg9/rafli5131/rafli/advance_vision/data/raw/advance_vision_human"
        (project / "logs/eval_teacher_yolo11n_seed42.log").write_text(
            f"PermissionError: [Errno 13] Permission denied: '{legacy}/train/images'\n", encoding="utf-8")
        train, ev = "train_teacher_yolo11n_seed42", "eval_teacher_yolo11n_seed42"
        events = [
            {"event": "t42_started", "recipe_sha256": sha(recipe)},
            {"event": "gpu_available", "physical_index": 1},
            {"event": "step_started", "name": train},
            {"event": "step_finished", "name": train, "exit_code": 0},
            {"event": "step_started", "name": ev},
            {"event": "step_failed", "name": ev, "exit_code": 1},
            {"event": "t42_failed", "error": "RuntimeError"},
        ]
        if mutate:
            mutate(root, events)
        (project / "t42_status.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        return root

    def prepare(self, root):
        env = {key: value for key, value in os.environ.items() if key not in {"KD_TRAIN_PYTHON", "KD_DATA_ROOT", "T42_ATTEMPT"}}
        env["T42_ATTEMPT"] = "server2"
        with patch.dict(os.environ, env, clear=True), patch.object(module, "EXPECTED_S_SHA256", sha(b"fake-s")):
            return module.prepare(root)

    def test_supported_state_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            _, teacher_sha = self.prepare(self.build(directory))
        self.assertEqual(teacher_sha, sha(b"fake-best"))

    def test_other_failure_cause_is_refused(self):
        def mutate(root, events):
            (root / "runs/kd_teacher_ablation/server2/logs/eval_teacher_yolo11n_seed42.log").write_text("CUDA out of memory\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "bukan path data lama"):
                self.prepare(self.build(directory, mutate))

    def test_unexpected_status_sequence_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "Urutan status"):
                self.prepare(self.build(directory, lambda root, events: events.pop(1)))

    def test_missing_fix_is_refused(self):
        def mutate(root, events):
            (root / "scripts/evaluate_val_ablation.py").write_text("old\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "git pull"):
                self.prepare(self.build(directory, mutate))

    def test_existing_later_output_is_refused(self):
        def mutate(root, events):
            (root / "models_local/teacher_ablation_t42/server2/training/teacher_yolo11s_seed42").mkdir(parents=True)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):
                self.prepare(self.build(directory, mutate))

    def test_changed_recipe_is_refused(self):
        def mutate(root, events):
            (root / "configs/kd_hybrid_full.yaml").write_bytes(b"changed\n")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "Resep"):
                self.prepare(self.build(directory, mutate))


if __name__ == "__main__":
    unittest.main()
