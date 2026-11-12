"""Run T43 offline, using shared T38 scoring with the frozen reviewed dataset."""
import csv
import json
import platform
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'ros2_packages/op3_camera_eval'), str(ROOT/'ros2_packages/op3_multi_session_eval')]
import torch
import ultralytics
from ultralytics import YOLO
from op3_camera_eval.evaluate import CLASSES, sha256
from op3_multi_session_eval.evaluate import inspect_sessions, build_dataset, ap_metrics, predict_frames, empty_counts, add_counts, score_counts

EXP = ROOT/'data/op3_camera_eval/experiments/t43_20261112'
SR = ROOT/'data/op3_camera_eval/sessions'

def main():
    plan_path=EXP/'frozen_plan.json'; plan=json.loads(plan_path.read_text())
    audit_path=EXP/'review_260_audit_and_frozen_hashes.json'; audit=json.loads(audit_path.read_text())
    cap_path=EXP/'capture_260_manifest.json'
    if sha256(cap_path)!=audit['capture_manifest_sha256']: raise ValueError('capture manifest changed')
    groups={'primary':[], 'negative':[]}
    for sid, data in audit['sessions'].items(): groups['negative' if 'kosong' in data['role'] else 'primary'].append(SR/sid)
    frames, manifest=inspect_sessions(groups)
    if Counter(f['role'] for f in frames) != {'primary':200,'negative':60}: raise ValueError('unexpected dataset composition')
    for f in frames:
        frozen=audit['frames'][f"{f['session']}/{f['image'].name}"]
        if sha256(f['image'])!=frozen['image_sha256'] or sha256(f['label'])!=frozen['reviewed_label_sha256']:
            raise ValueError(f'Frozen input changed: {f["key"]}')
    for sid,v in manifest['sessions'].items():
        if v['review_log_sha256'] != audit['sessions'][sid]['review_log_sha256']: raise ValueError('review log changed')
    for name, m in plan['checkpoints'].items():
        if sha256(Path(m['path'])) != m['sha256']: raise ValueError(f'Checkpoint mismatch: {name}')
    out=ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260'
    out.mkdir(parents=True, exist_ok=False)
    manifest.update({'created_at_utc':datetime.now(timezone.utc).isoformat(),'audit_sha256':sha256(audit_path),'plan_sha256':sha256(plan_path),'checkpoints':plan['checkpoints'],'settings':plan['evaluation'],'versions':{'python':platform.python_version(),'torch':torch.__version__,'ultralytics':ultralytics.__version__},'meaning':'exploratory, all goal-containing frames partial; goal lower-region labels and robot body labels'})
    (out/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    subsets={
      'idle':[f for f in frames if 'idle_' in f['session']],
      'walking':[f for f in frames if 'walk_' in f['session']],
      'combined':frames,
      'partial_goal':[f for f in frames if f['role']=='primary']}
    if [len(subsets[x]) for x in subsets] != [130,130,260,200]: raise ValueError('unexpected split sizes')
    yamls={name:build_dataset(out/name,items,{'primary','negative'}) for name,items in subsets.items()}
    report={'status':'in_progress','labels':'goal lower region and robot body; all goal frames partial','composition':{k:len(v) for k,v in subsets.items()},'models':{}}
    for name, checkpoint in plan['checkpoints'].items():
        print(f'Evaluasi {name}',flush=True)
        model=YOLO(checkpoint['path'],task='detect')
        if tuple(model.names.values()) != CLASSES: raise ValueError('Unexpected class order')
        ap={s:ap_metrics(model,yaml,out,f'val_{s}_{name}') for s,yaml in yamls.items()}
        operating=predict_frames(model,frames,out/f'per_frame_{name}.jsonl')
        results={}
        for subset,items in subsets.items():
            sessions={f['session'] for f in items}
            counts=empty_counts()
            for sid in sessions:
                for cls,row in operating['by_session'][sid]['per_class'].items():
                    for k in counts[cls]: counts[cls][k]+=row[k]
            scores=score_counts(counts)
            p=scores['macro']['precision']; r=scores['macro']['recall']
            scores['macro']['F1_mean_per_class']=scores['macro']['F1']
            scores['macro']['F1_harmonic_macro_precision_recall']=2*p*r/(p+r) if p is not None and r is not None and p+r else 0
            results[subset]={'ap':ap[subset],'operating':scores}
        negative_frames={s:0 for s in ('idle','walking')}
        for line in (out/f'per_frame_{name}.jsonl').read_text().splitlines():
            f=json.loads(line)
            if f['role']=='negative' and f['detections']:
                negative_frames['idle' if 'idle_' in f['session'] else 'walking']+=1
        report['models'][name]={'splits':results,'negative_frames_with_fp':negative_frames}
        (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    report['status']='complete'; (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    with (out/'summary.csv').open('w',newline='') as stream:
        fields=['model','split','class','ground_truth','predictions','TP','FP','FN','precision','recall','F1','F1_mean_per_class','mAP50','mAP50_95']; writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for model,data in report['models'].items():
            for split,v in data['splits'].items():
                op=v['operating']; ap=v['ap']; macro=op['macro']
                writer.writerow({'model':model,'split':split,'class':'macro','ground_truth':op['ground_truth'],'predictions':op['predictions'],'TP':op['true_positives'],'FP':op['false_positives'],'FN':op['false_negatives'],'precision':macro['precision'],'recall':macro['recall'],'F1':macro['F1_harmonic_macro_precision_recall'],'F1_mean_per_class':macro['F1_mean_per_class'],'mAP50':ap['mAP50'],'mAP50_95':ap['mAP50-95']})
                for cls,x in op['per_class'].items():
                    ac=ap['per_class'].get(cls,{})
                    writer.writerow({'model':model,'split':split,'class':cls,'ground_truth':x['ground_truth'],'predictions':x['predictions'],'TP':x['true_positives'],'FP':x['false_positives'],'FN':x['false_negatives'],'precision':x['precision'],'recall':x['recall'],'F1':x['F1'],'mAP50':ac.get('mAP50'),'mAP50_95':ac.get('mAP50-95')})
    print('DONE',out,flush=True)
if __name__=='__main__': main()
