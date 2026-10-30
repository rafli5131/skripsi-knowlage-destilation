"""Lanjutkan tepat dari evaluasi teacher n yang selesai; default hanya audit."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(root):
    spec = importlib.util.spec_from_file_location('t42_driver', root / 'scripts/run_t42_teacher_ablation.py')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    events = [json.loads(line) for line in driver.STATUS.read_text().splitlines()]
    last = events[-1]
    if last.get('event') != 'step_finished' or last.get('name') != 'eval_teacher_yolo11n_seed42' or last.get('exit_code') != 0:
        raise RuntimeError('Status bukan titik lanjut yang didukung; periksa log sebelum menjalankan.')
    if digest(root / 'configs/kd_hybrid_full.yaml') != events[0]['recipe_sha256']:
        raise RuntimeError('Resep training berubah.')
    run = driver.PRIVATE / driver.teacher_run_name('n')
    manifest = json.loads((run / 'manifest.json').read_text())
    evaluation = json.loads((driver.EVAL / 'teacher_yolo11n_seed42_val.json').read_text())
    sha = digest(run / 'weights/best.pt')
    if manifest['status'] != 'complete' or sha != manifest['teacher_best_sha256'] or sha != evaluation['checkpoint_sha256']:
        raise RuntimeError('Manifest/hash teacher n tidak cocok.')
    if evaluation['images'] != 1213 or evaluation['model'] != 'teacher_yolo11n_seed42':
        raise RuntimeError('Evaluasi VAL teacher n tidak cocok.')
    expected_s = '85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5'
    if digest(root / 'models_local/teacher_ablation_t42/pretrained/yolo11s.pt') != expected_s:
        raise RuntimeError('Hash pralatih teacher s tidak cocok.')
    # Jangan menimpa tahap yang mungkin sudah dikerjakan oleh proses lain.
    targets = [driver.PRIVATE / driver.teacher_run_name('s')]
    targets += [root / 'analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.md', root / 'analisis_performa/tabel/T42_ablasi_teacher_yolo11s_val.csv']
    labels = ['teacher_yolo11s_seed42'] + [f'student_teacher_yolo11{v}_seed{s}' for v in ('n', 's') for s in (42, 1337, 2025)]
    for label in labels:
        targets += [driver.EVAL / f'{label}_val.json', driver.PROJECT / 'logs' / f'train_{label}.log', driver.PROJECT / 'logs' / f'eval_{label}.log']
        if label.startswith('student'):
            targets += [driver.PROJECT / label, root / 'configs' / f't42_{label}.yaml']
    if any(p.exists() for p in targets):
        raise FileExistsError('Ada keluaran tahap lanjutan; audit manual diperlukan.')
    return driver, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('/mnt/nas-hpg9/rafli5131/bre'))
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    driver, sha = prepare(args.root.resolve())
    print(json.dumps({'status': 'preflight_passed', 'root': str(driver.ROOT), 'teacher_n_sha256': sha}), flush=True)
    if not args.execute:
        return
    with (driver.PROJECT / '.continue.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        driver, sha = prepare(args.root.resolve())
        driver.record('t42_continued', completed_step='eval_teacher_yolo11n_seed42', teacher_n_sha256=sha,
                      continuation_script=str(Path(__file__).resolve()), continuation_sha256=digest(Path(__file__)))
        try:
            label = 'teacher_yolo11s_seed42'
            driver.run_step(f'train_{label}', [driver.PYTHON, str(driver.ROOT / 'scripts/train_t42_teacher.py'), '--variant', 's'], gpu=True)
            run = driver.PRIVATE / label
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
