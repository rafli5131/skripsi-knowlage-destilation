import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('continuation', Path(__file__).resolve().parents[1] / 'scripts/continue_t42_after_teacher_n.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContinuationTests(unittest.TestCase):
    def exercise(self, fail=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            driver = Mock(ROOT=root, PROJECT=root, PRIVATE=root, PYTHON='python', DATA_ROOT='data')
            driver.student_config.return_value = root / 'config.yaml'
            if fail:
                driver.run_step.side_effect = RuntimeError('training failed')
            with patch.object(module, 'prepare', return_value=(driver, 'verified')), patch('sys.argv', ['continue', '--execute']):
                if fail:
                    with self.assertRaisesRegex(RuntimeError, 'training failed'):
                        module.main()
                else:
                    module.main()
            return driver

    def test_only_remaining_stages(self):
        driver = self.exercise()
        names = [call.args[0] for call in driver.run_step.call_args_list]
        self.assertEqual(names, ['train_teacher_yolo11s_seed42'] + [f'train_student_teacher_yolo11{v}_seed{s}' for v in ('n', 's') for s in (42, 1337, 2025)] + ['build_t42'])
        self.assertEqual(driver.evaluate.call_count, 7)
        self.assertEqual(driver.record.call_args.args[0], 't42_complete')

    def test_failure_stops_queue(self):
        driver = self.exercise(fail=True)
        self.assertEqual(driver.run_step.call_count, 1)
        driver.evaluate.assert_not_called()
        self.assertEqual(driver.record.call_args.args[0], 't42_failed')


if __name__ == '__main__':
    unittest.main()
