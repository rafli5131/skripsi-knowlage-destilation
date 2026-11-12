"""Buat label awal union empat model T43 setelah audit label buta selesai."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0., x2-x1) * max(0., y2-y1)
    total = max(0., a[2]-a[0]) * max(0., a[3]-a[1]) + max(0., b[2]-b[0]) * max(0., b[3]-b[1]) - intersection
    return intersection / total if total else 0.


def classwise_nms(boxes, threshold):
    """Deterministic NMS over model outputs; different classes remain separate."""
    ordered = sorted(boxes, key=lambda b: (-b['confidence'], b['class_id'], b['model'], b['xyxy']))
    kept = []
    for box in ordered:
        if all(box['class_id'] != prior['class_id'] or iou(box['xyxy'], prior['xyxy']) <= threshold for prior in kept):
            kept.append(box)
    return kept


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--session-dir', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--blind-completion', type=Path, required=True, help='Manifest audit label buta yang telah selesai')
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    blind = json.loads(args.blind_completion.read_text())
    if blind.get('status') != 'complete' or blind.get('frozen_plan_sha256') != sha(args.plan):
        p.error('Audit label buta harus selesai dan terikat ke hash frozen plan.')
    samples = blind.get('samples')
    if not isinstance(samples, list) or len(samples) != 52:
        p.error('Manifest audit buta harus mencantumkan 52 sampel beserta hash label dan log review.')
    for sample in samples:
        for key in ('image', 'label', 'review_log'):
            path = Path(sample[key]['path'])
            if not path.is_file() or sha(path) != sample[key]['sha256']:
                p.error('Berkas atau hash audit buta tidak cocok: ' + str(path))
    cfg = plan['prelabel']
    if cfg['method'] != 'four_model_union_classwise_nms':
        p.error('Metode pra-label pada plan bukan union empat model.')
    sessions = args.session_dir.resolve()
    if not (sessions/'capture_manifest.json').is_file():
        p.error('capture_manifest.json tidak ditemukan')
    images = sorted(x for x in (sessions/'images').iterdir() if x.suffix.lower() in ('.jpg', '.jpeg', '.png'))
    if not images:
        p.error('Tidak ada frame di direktori sesi')
    out = sessions/'labels_auto'
    if out.exists():
        p.error('labels_auto sudah ada; tidak akan ditimpa.')
    from ultralytics import YOLO
    import cv2
    models = []
    for name, entry in plan['checkpoints'].items():
        path = Path(entry['path'])
        if not path.is_file() or sha(path) != entry['sha256'] or cfg['member_sha256'].get(name) != entry['sha256']:
            p.error('Checkpoint tidak tersedia atau hash tidak cocok: '+name)
        model = YOLO(str(path))
        names = {int(k): str(v) for k, v in model.names.items()}
        if names != {0: 'ball', 1: 'gawang', 2: 'robot'}:
            p.error('Mapping kelas tidak sesuai: '+name)
        models.append((name, model))
    if len(models) != 4:
        p.error('Diperlukan tepat empat checkpoint.')
    out.mkdir()
    with (out/'predictions.jsonl').open('x', encoding='utf-8') as log:
        for image in images:
            im = cv2.imread(str(image))
            if im is None:
                raise RuntimeError('Gambar tidak dapat dibaca: '+str(image))
            height, width = im.shape[:2]
            candidates = []
            for name, model in models:
                result = model.predict(source=str(image), imgsz=640, conf=cfg['confidence'], iou=cfg['model_nms_iou'], device='cpu', verbose=False)[0]
                for class_id, conf, xyxy in zip(result.boxes.cls.tolist(), result.boxes.conf.tolist(), result.boxes.xyxy.tolist()):
                    x1,y1,x2,y2 = xyxy
                    xyxy = [max(0., min(width,x1)),max(0., min(height,y1)),max(0., min(width,x2)),max(0., min(height,y2))]
                    if xyxy[2] > xyxy[0] and xyxy[3] > xyxy[1]:
                        candidates.append({'class_id':int(class_id),'confidence':float(conf),'xyxy':xyxy,'model':name})
            boxes = classwise_nms(candidates, cfg['cross_model_classwise_nms_iou'])
            lines=[]
            for b in boxes:
                x1,y1,x2,y2=b['xyxy']; values=((x1+x2)/(2*width),(y1+y2)/(2*height),(x2-x1)/width,(y2-y1)/height)
                lines.append(str(b['class_id'])+' '+' '.join(f'{v:.8f}' for v in values))
            (out/(image.stem+'.txt')).write_text('\n'.join(lines)+('\n' if lines else ''))
            log.write(json.dumps({'image':image.name,'image_sha256':sha(image),'candidates':candidates,'kept':boxes})+'\n')
    manifest={'status':'draft_requires_human_review','created_at_utc':datetime.now(timezone.utc).isoformat(),'session':str(sessions),'images':len(images),'plan_sha256':sha(args.plan),'blind_completion_sha256':sha(args.blind_completion),'models':{n:e['sha256'] for n,e in plan['checkpoints'].items()},'settings':cfg,'prediction_log_sha256':sha(out/'predictions.jsonl')}
    (out/'prelabel_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('Label awal dibuat:',len(images),'frame; tinjauan manusia wajib:',out)


if __name__ == '__main__':
    main()
