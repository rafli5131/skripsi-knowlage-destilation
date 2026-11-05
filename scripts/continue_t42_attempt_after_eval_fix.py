"""Lanjutkan percobaan T42 bernama setelah evaluasi VAL teacher n gagal karena path data lama.

Percobaan ``server2`` melatih teacher YOLO11n sampai selesai, lalu evaluasi VAL berhenti karena
``configs/data_train_val.yaml`` masih menunjuk dataset server lama yang tidak terbaca. Perbaikannya ada di
``server_paths.evaluation_data_yaml``. Skrip ini hanya melanjutkan dari titik itu dan default-nya hanya audit.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

TRAIN_STEP = 'train_teacher_yolo11n_seed42'
FAILED_EVAL_STEP = 'eval_teacher_yolo11n_seed42'
RETRY_EVAL_STEP = 'eval_teacher_yolo11n_seed42_retry1'
EXPECTED_S_SHA256 = '85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5'
EXPECTED_SEQUENCE = [
    ('t42_started', None), ('gpu_available', None), ('step_started', TRAIN_STEP), ('step_finished', TRAIN_STEP),
    ('step_started', FAILED_EVAL_STEP), ('step_failed', FAILED_EVAL_STEP), ('t42_failed', None),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_driver(root):
    # Driver mengimpor ``server_paths`` dengan nama modul biasa; jalankan juga dari folder skrip repo ini.
    if str(root / 'scripts') not in sys.path:
        sys.path.insert(0, str(root / 'scripts'))
    return load_module('t42_driver', root / 'scripts/run_t42_teacher_ablation.py')


def prepare(root):
    driver = load_driver(root)
    if not driver.LAYOUT.attempt:
        raise RuntimeError('Skrip ini hanya untuk percobaan T42 bernama; isi T42_ATTEMPT (misalnya server2).')
    events = [json.loads(line) for line in driver.STATUS.read_text(encoding='utf-8').splitlines()]
    sequence = [(event['event'], event.get('name')) for event in events]
    if sequence != EXPECTED_SEQUENCE:
        raise RuntimeError('Urutan status bukan titik lanjut yang didukung; periksa status dan log sebelum menjalankan.')
    if events[3]['exit_code'] != 0 or events[5]['exit_code'] != 1:
        raise RuntimeError('Kode keluar training/evaluasi tidak sesuai titik lanjut yang didukung.')
    failed_log = driver.PROJECT / 'logs' / f'{FAILED_EVAL_STEP}.log'
    text = failed_log.read_text(encoding='utf-8', errors='replace')
    legacy_root = sys.modules['server_paths'].LEGACY_DATA_ROOT
    if 'PermissionError' not in text or legacy_root not in text:
        raise RuntimeError('Penyebab kegagalan evaluasi bukan path data lama; jangan lanjutkan tanpa audit.')
    fixed = (root / 'scripts/evaluate_val_ablation.py').read_text(encoding='utf-8')
    if 'evaluation_data_yaml' not in fixed:
        raise RuntimeError('Perbaikan path data evaluasi belum ada di repo ini (git pull dulu).')
    if digest(root / 'configs/kd_hybrid_full.yaml') != events[0]['recipe_sha256']:
        raise RuntimeError('Resep training berubah.')
    run = driver.PRIVATE / driver.teacher_run_name('n')
    manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
    sha = digest(run / 'weights/best.pt')
    if manifest['status'] != 'complete' or sha != manifest['teacher_best_sha256']:
        raise RuntimeError('Manifest/hash teacher n tidak cocok.')
    if digest(driver.LAYOUT.pretrained / 'yolo11s.pt') != EXPECTED_S_SHA256:
        raise RuntimeError('Hash pralatih teacher s tidak cocok.')
    # Jangan menimpa tahap yang mungkin sudah dikerjakan oleh proses lain.
    targets = [driver.PRIVATE / driver.teacher_run_name('s'), driver.PROJECT / 'logs' / f'{RETRY_EVAL_STEP}.log',
               root / 'analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md',
               root / 'analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.csv']
    labels = [f'teacher_yolo11{v}_seed42' for v in ('n', 's')]
    labels += [f'student_teacher_yolo11{v}_seed{s}' for v in ('n', 's') for s in (42, 1337, 2025)]
    for label in labels:
        targets.append(driver.EVAL / f'{label}_val.json')
        if label != 'teacher_yolo11n_seed42':
            targets += [driver.PROJECT / 'logs' / f'train_{label}.log', driver.PROJECT / 'logs' / f'eval_{label}.log']
        if label.startswith('student'):
            targets += [driver.PROJECT / label, driver.LAYOUT.student_config_path(label)]
    if any(path.exists() for path in targets):
        raise FileExistsError('Ada keluaran tahap lanjutan; audit manual diperlukan.')
    return driver, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    driver, sha = prepare(root)
    print(json.dumps({'status': 'preflight_passed', 'root': str(driver.ROOT), 'attempt': driver.LAYOUT.attempt,
                      'teacher_n_sha256': sha}), flush=True)
    if not args.execute:
        return
    with (driver.PROJECT / '.continue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        driver, sha = prepare(root)
        driver.record('t42_continued', completed_step=TRAIN_STEP, failed_step=FAILED_EVAL_STEP, retry_step=RETRY_EVAL_STEP,
                      reason='Evaluasi VAL membaca configs/data_train_val.yaml dengan path dataset server lama; '
                             'diperbaiki lewat server_paths.evaluation_data_yaml',
                      teacher_n_sha256=sha, continuation_script=str(Path(__file__).resolve()),
                      continuation_sha256=digest(Path(__file__)))
        try:
            run = driver.PRIVATE / driver.teacher_run_name('n')
            driver.evaluate('teacher_yolo11n_seed42', run / 'weights/best.pt', run / 'manifest.json', step_name=RETRY_EVAL_STEP)
            label = 'teacher_yolo11s_seed42'
            driver.run_step(f'train_{label}', [driver.PYTHON, str(driver.ROOT / 'scripts/train_t42_teacher.py'), '--variant', 's'], gpu=True)
            run = driver.PRIVATE / driver.teacher_run_name('s')
            driver.evaluate(label, run / 'weights/best.pt', run / 'manifest.json')
            for variant in ('n', 's'):
                for seed in (42, 1337, 2025):
                    label = f'student_teacher_yolo11{variant}_seed{seed}'
                    config = driver.student_config(variant, seed)
                    driver.run_step(f'train_{label}', [driver.PYTHON, str(driver.ROOT / 'scripts/train_kd.py'), '--config', str(config), '--data-root', driver.DATA_ROOT], gpu=True)
                    run = driver.PROJECT / label
                    driver.evaluate(label, run / 'weights/best.pt', run / 'manifest.json')
            driver.run_step('build_t42', [driver.PYTHON, str(driver.ROOT / 'scripts/build_t42_teacher_ablation.py')], gpu=False)
            driver.record('t42_complete', table=str(driver.ROOT / 'analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md'))
        except BaseException as error:
            driver.record('t42_failed', error=f'{type(error).__name__}: {error}')
            raise


if __name__ == '__main__':
    main()
