"""Audit T43 reviewed labels without modifying annotations or images."""
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / 'data/op3_camera_eval/experiments/t43_20261112'
SESSIONS = ROOT / 'data/op3_camera_eval/sessions'
CLASSES = ['ball', 'gawang', 'robot']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_boxes(path):
    result = []
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) != 5 or fields[0] not in ('0', '1', '2'):
            raise ValueError(f'Invalid label {path}: {line}')
        x, y, w, h = map(float, fields[1:])
        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
            raise ValueError(f'Out of bounds label {path}: {line}')
        result.append((int(fields[0]), x - w/2, y - h/2, x + w/2, y + h/2))
    return result

def iou(a, b):
    inter = max(0, min(a[3], b[3])-max(a[1], b[1])) * max(0, min(a[4], b[4])-max(a[2], b[2]))
    union = (a[3]-a[1])*(a[4]-a[2]) + (b[3]-b[1])*(b[4]-b[2]) - inter
    return inter/union if union else 0

def main():
    capture_path = EXP/'capture_260_manifest.json'
    capture = json.loads(capture_path.read_text())
    completion_path = EXP/'blind_review_completion.json'
    completion = json.loads(completion_path.read_text())
    frames, sessions = {}, {}
    for s in capture['sessions']:
        p = SESSIONS/s['session']
        log_path = p/'labels_reviewed/review_log.jsonl'
        log = [json.loads(x) for x in log_path.read_text().splitlines() if x.strip()]
        if {x['image'] for x in log} != set(s['images']) or {x['reviewer'] for x in log} != {'bhre'}:
            raise ValueError(f'Incomplete review log: {p}')
        label_paths = list((p/'labels_reviewed').glob('frame_*.txt'))
        if {x.stem for x in label_paths} != {Path(x).stem for x in s['images']}:
            raise ValueError(f'Incomplete labels: {p}')
        counts=collections.Counter(); empty=0
        for name, digest in s['images'].items():
            image = p/'images'/name; label = p/'labels_reviewed'/(Path(name).stem+'.txt')
            if sha(image) != digest: raise ValueError(f'Image hash mismatch: {image}')
            bs=read_boxes(label); empty += not bs
            for b in bs: counts[CLASSES[b[0]]] += 1
            key=f"{s['session']}/{name}"
            frames[key]={'image_sha256':digest,'reviewed_label_sha256':sha(label)}
        sessions[s['session']]={'role':s['role'],'images':len(s['images']),'review_log_entries':len(log),'review_log_sha256':sha(log_path),'empty_labels':empty,'class_boxes':dict(counts)}
    if len(frames)!=260: raise ValueError('Expected 260 images')
    agreement={c:{'blind':0,'reviewed':0,'matched':0,'matched_ious':[]} for c in CLASSES}
    for sample in completion['samples']:
        for field in ('image','label','review_log'):
            data=sample[field]
            if sha(Path(data['path'])) != data['sha256']: raise ValueError(f'Blind snapshot changed: {data["path"]}')
        a=read_boxes(Path(sample['label']['path']))
        b=read_boxes(SESSIONS/sample['original_session']/'labels_reviewed'/(Path(sample['original_image']).stem+'.txt'))
        for c,name in enumerate(CLASSES):
            aa=[x for x in a if x[0]==c]; bb=[x for x in b if x[0]==c]
            pairs=sorted(((iou(x,y),i,j) for i,x in enumerate(aa) for j,y in enumerate(bb)),reverse=True)
            ua=set();ub=set(); result=agreement[name]
            for overlap,i,j in pairs:
                if overlap < .5: break
                if i not in ua and j not in ub:
                    ua.add(i);ub.add(j);result['matched_ious'].append(overlap)
            result['blind']+=len(aa);result['reviewed']+=len(bb);result['matched']+=len(ua)
    for result in agreement.values():
        vals=result.pop('matched_ious');result['mean_matched_iou']=sum(vals)/len(vals) if vals else None
        result['fraction_blind_matched']=result['matched']/result['blind'] if result['blind'] else None
        result['fraction_reviewed_matched']=result['matched']/result['reviewed'] if result['reviewed'] else None
    out={'created_at_utc':datetime.now(timezone.utc).isoformat(),'capture_manifest_sha256':sha(capture_path),'blind_completion_sha256':sha(completion_path),'reviewer':'bhre','total_frames':len(frames),'sessions':sessions,'agreement_iou_threshold':.5,'agreement':agreement,'limitations':['Same reviewer for both passes, not inter-rater agreement','Hybrid preview seen earlier; model union prelabels and feedback can bias review','Goal lower region and robot body convention clarified after initial annotation; goal cutoff lacks fixed landmark','Agreement at IoU 0.5 is not proof of accurate labels or high-IoU agreement'], 'frames':frames}
    target=EXP/'review_260_audit_and_frozen_hashes.json'
    with target.open('x') as stream: json.dump(out,stream,indent=2);stream.write('\n')
    print(json.dumps({'output':str(target),'sha256':sha(target),'total_frames':len(frames),'sessions':sessions,'agreement':agreement},indent=2))
if __name__=='__main__': main()
