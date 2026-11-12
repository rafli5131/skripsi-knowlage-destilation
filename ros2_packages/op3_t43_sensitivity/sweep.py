"""Offline T43 confidence sweep; verify AP and operating results before publication."""
import csv,hashlib,json,math,platform,sys
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'ros2_packages/op3_camera_eval'),str(ROOT/'ros2_packages/op3_multi_session_eval')]
import numpy as np
import torch,ultralytics
from ultralytics import YOLO
from op3_camera_eval.evaluate import CLASSES,sha256
from op3_multi_session_eval.evaluate import inspect_sessions,build_dataset,ap_metrics,score_frame,empty_counts,add_counts,score_counts
EXP=ROOT/'data/op3_camera_eval/experiments/t43_20261112'
BASE=ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260'
OUT=ROOT/'runs/op3_t43_sensitivity/20261112_confidence_01'

def verify():
 plan_path=EXP/'frozen_plan.json'; audit_path=EXP/'review_260_audit_and_frozen_hashes.json'; cap=EXP/'capture_260_manifest.json'; blind=EXP/'blind_review_completion.json'; selection=EXP/'blind_review_52/selection_manifest.json'; result_path=BASE/'results.json'
 plan=json.loads(plan_path.read_text()); audit=json.loads(audit_path.read_text()); completion=json.loads(blind.read_text()); m=json.loads((ROOT/'dokumentasi/2026-11-12/percobaan-39-evaluasi-t43/manifest_hasil_sha256.json').read_text())['files']
 checks={str(audit_path):m[str(audit_path.relative_to(ROOT))],str(cap):audit['capture_manifest_sha256'],str(blind):audit['blind_completion_sha256'],str(selection):completion['selection_manifest_sha256'],str(result_path):m[str(result_path.relative_to(ROOT))]}
 for p,expected in checks.items():
  if sha256(Path(p))!=expected:raise ValueError(f'Hash mismatch: {p}')
 for name,model in plan['checkpoints'].items():
  if sha256(Path(model['path']))!=model['sha256']:raise ValueError(f'Checkpoint mismatch: {name}')
 groups={'primary':[],'negative':[]}
 for sid,s in audit['sessions'].items():groups['negative' if 'kosong' in s['role'] else 'primary'].append(ROOT/'data/op3_camera_eval/sessions'/sid)
 frames,manifest=inspect_sessions(groups)
 if len(frames)!=260:raise ValueError('Expected 260 frames')
 for f in frames:
  frozen=audit['frames'][f"{f['session']}/{f['image'].name}"]
  if sha256(f['image'])!=frozen['image_sha256'] or sha256(f['label'])!=frozen['reviewed_label_sha256']:raise ValueError(f'Frozen frame/label mismatch {f["key"]}')
 for sid,s in manifest['sessions'].items():
  if s['review_log_sha256']!=audit['sessions'][sid]['review_log_sha256']:raise ValueError(f'Review log mismatch {sid}')
 return plan,frames,manifest,checks,json.loads(result_path.read_text())

def compare_metrics(name,got,expected):
 for key in ('mAP50','mAP50-95'):
  if not math.isclose(got[key],expected[key],rel_tol=1e-9,abs_tol=1e-9):raise ValueError(f'{name} {key} mismatch: {got[key]} vs {expected[key]}')
 for cls,vals in expected['per_class'].items():
  for key in ('mAP50','mAP50-95'):
   if not math.isclose(got['per_class'][cls][key],vals[key],rel_tol=1e-9,abs_tol=1e-9):raise ValueError(f'{name} {cls} {key} mismatch')

def main():
 plan,frames,source,checks,old=verify()
 OUT.mkdir(parents=True,exist_ok=False)
 info={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'running','input_hashes':checks,'models':plan['checkpoints'],'frames':len(frames),'thresholds':[i/20 for i in range(1,19)],'threshold_comparison':'>','match_iou':0.5,'prediction_floor':0.001,'nms_iou':0.7,'device':'cpu','versions':{'python':platform.python_version(),'torch':torch.__version__,'ultralytics':ultralytics.__version__},'limitations':['one scene; correlated frames','same four evaluated models used for prelabels','retrospective sweep is not threshold selection','goal lower region and robot body label conventions']}
 (OUT/'run_manifest.json').write_text(json.dumps(info,indent=2)+'\n')
 yaml=build_dataset(OUT/'combined',frames,{'primary','negative'})
 thresholds=[i/20 for i in range(1,19)];rows=[];summaries={}
 for name,model_info in plan['checkpoints'].items():
  print(f'Validasi AP {name}',flush=True);model=YOLO(model_info['path'],task='detect')
  if tuple(model.names.values())!=CLASSES:raise ValueError('Class order mismatch')
  new_ap=ap_metrics(model,yaml,OUT,f'val_combined_{name}'); compare_metrics(name,new_ap,old['models'][name]['splits']['combined']['ap'])
  old_per_frame={x['key']:x for x in (json.loads(s) for s in (BASE/f'per_frame_{name}.jsonl').read_text().splitlines())}
  if len(old_per_frame)!=260:raise ValueError('Original per-frame baseline incomplete')
  counters={(scope,t):empty_counts() for scope in ('idle','walking','combined') for t in thresholds};goal_conf=[];negative=defaultdict(int)
  with (OUT/f'predictions_{name}.jsonl').open('x') as stream:
   for i,f in enumerate(frames,1):
    res=model.predict(source=str(f['image']),imgsz=640,conf=0.001,iou=0.7,device='cpu',augment=False,verbose=False)[0]
    if res.orig_shape!=(480,640):raise ValueError('Unexpected image size')
    det=[{'class_id':int(c),'confidence':float(q),'xyxy':[float(v) for v in xy]} for c,q,xy in zip(res.boxes.cls.cpu().tolist(),res.boxes.conf.cpu().tolist(),res.boxes.xyxy.cpu().tolist())]
    baseline_counts,_=score_frame(f['gt'],[d for d in det if d['confidence']>0.25])
    if baseline_counts!=old_per_frame[f['key']]['counts']:raise ValueError(f'{name} baseline mismatch frame {f["key"]}: {baseline_counts} vs {old_per_frame[f["key"]]["counts"]}')
    _,low_details=score_frame(f['gt'],det)
    goal_conf.extend(d['confidence'] for d in low_details if d['class_id']==1 and d['matched'])
    cond='idle' if 'idle_' in f['session'] else 'walking'
    for t in thresholds:
     filtered=[d for d in det if d['confidence']>t];cnt,_=score_frame(f['gt'],filtered)
     add_counts(counters[(cond,t)],cnt);add_counts(counters[('combined',t)],cnt)
     if f['role']=='negative' and filtered:negative[(cond,t)]+=1;negative[('combined',t)]+=1
    stream.write(json.dumps({'key':f['key'],'session':f['session'],'role':f['role'],'detections':det})+'\n')
    if i%50==0 or i==260:print(f'{name}: {i}/260',flush=True)
  for scope in ('idle','walking','combined'):
   for t in thresholds:
    score=score_counts(counters[(scope,t)])
    for cls,val in score['per_class'].items():rows.append({'model':name,'condition':scope,'threshold':f'{t:.2f}','class':cls,'ground_truth':val['ground_truth'],'predictions':val['predictions'],'TP':val['true_positives'],'FP':val['false_positives'],'FN':val['false_negatives'],'precision':val['precision'],'recall':val['recall'],'F1':val['F1'],'negative_frames_with_fp':negative[(scope,t)]})
    p=score['macro']['precision'];r=score['macro']['recall'];f1=2*p*r/(p+r) if p+r else 0
    rows.append({'model':name,'condition':scope,'threshold':f'{t:.2f}','class':'macro','ground_truth':score['ground_truth'],'predictions':score['predictions'],'TP':score['true_positives'],'FP':score['false_positives'],'FN':score['false_negatives'],'precision':p,'recall':r,'F1':f1,'negative_frames_with_fp':negative[(scope,t)]})
  if goal_conf:
   q=np.percentile(goal_conf,[0,25,50,75,100]);distribution=dict(zip(['min','q1','median','q3','max'],map(float,q)))
  else:distribution=None
  summaries[name]={'recomputed_ap':new_ap,'baseline_frame_counts_equal':True,'matched_goal_confidence':{'count':len(goal_conf),'distribution':distribution}}
  print(f'{name}: AP and 260 baseline frame counts match',flush=True)
 with (OUT/'confidence_sweep.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 info['status']='complete';info['models_verified']=summaries;info['outputs']={'confidence_sweep_sha256':sha256(OUT/'confidence_sweep.csv'),'predictions_sha256':{n:sha256(OUT/f'predictions_{n}.jsonl') for n in summaries}}
 (OUT/'run_manifest.json').write_text(json.dumps(info,indent=2)+'\n')
 print('COMPLETED',OUT,flush=True)
if __name__=='__main__':main()
