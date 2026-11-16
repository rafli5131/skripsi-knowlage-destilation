"""Reproduce frozen T38/T43 validator AP and predictor operating counts offline."""
import json,math,platform,subprocess,sys,traceback
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'ros2_packages/op3_camera_eval'),str(ROOT/'ros2_packages/op3_multi_session_eval')]
import torch,ultralytics
from ultralytics import YOLO
from op3_camera_eval.evaluate import CLASSES,read_labels,sha256
from op3_multi_session_eval.evaluate import build_dataset,ap_metrics,score_frame,empty_counts,add_counts,score_counts
RUN=ROOT/'runs/op3_single_path_eval/20261116_identity_01'
T38=ROOT/'runs/op3_multi_session_eval/20261105_empat_model_primary260_v1';T43=ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260'
PLAN=ROOT/'data/op3_camera_eval/experiments/t43_20261112/frozen_plan.json'
def make_frames(folder):
 d=json.loads((folder/'input_manifest.json').read_text());out=[]
 for key,x in d['frames'].items():
  image=Path(x['image']);label=Path(x['label'])
  if sha256(image)!=x['image_sha256'] or sha256(label)!=x['label_sha256']:raise ValueError(f'Input hash mismatch: {key}')
  out.append({'key':key,'role':x['role'],'session':x['session'],'image':image,'label':label,'gt':read_labels(label)})
 return out

def compare_ap(actual,expected,label):
 for key in ('mAP50','mAP50-95'):
  if not math.isclose(actual[key],expected[key],rel_tol=1e-9,abs_tol=1e-9):raise ValueError(f'{label}: {key} {actual[key]} != {expected[key]}')
 if set(actual['per_class'])!=set(expected['per_class']):raise ValueError(f'{label} class mismatch')
 for c in actual['per_class']:
  for k in ('mAP50','mAP50-95'):
   if not math.isclose(actual['per_class'][c][k],expected['per_class'][c][k],rel_tol=1e-9,abs_tol=1e-9):raise ValueError(f'{label} {c} {k} mismatch')

def compare_counts(got,exp,label):
 for c in CLASSES:
  for k in ('ground_truth','predictions','true_positives','false_positives','false_negatives'):
   if got['per_class'][c][k]!=exp['per_class'][c][k]:raise ValueError(f"{label} {c} {k} {got['per_class'][c][k]} != {exp['per_class'][c][k]}")
 for k in ('precision','recall','F1'):
  if not math.isclose(got['macro'][k],exp['macro'][k],rel_tol=1e-9,abs_tol=1e-9):raise ValueError(f'{label} macro {k} mismatch')

def main():
 t38=make_frames(T38);t43=make_frames(T43);assert Counter(x['role'] for x in t38)=={'primary':200,'negative':60,'partial':50} and len(t43)==260
 splits={'t38_primary':[x for x in t38 if x['role'] in ('primary','negative')],'t38_partial':[x for x in t38 if x['role']=='partial'],'t43_idle':[x for x in t43 if 'idle_' in x['session']],'t43_walking':[x for x in t43 if 'walk_' in x['session']],'t43_combined':t43,'t43_partial_goal':[x for x in t43 if x['role']=='primary']}
 assert [len(splits[k]) for k in splits]==[260,50,130,130,260,200]
 old38=json.loads((T38/'results.json').read_text());old43=json.loads((T43/'results.json').read_text());models=json.loads(PLAN.read_text())['checkpoints']
 for name,c in models.items():
  if sha256(Path(c['path']))!=c['sha256']:raise ValueError(f'Model mismatch {name}')
 RUN.mkdir(parents=True,exist_ok=False)
 report={'status':'running','created_utc':datetime.now(timezone.utc).isoformat(),'repository_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'prompt_source':'origin/main:prompt/PROMPT_SESI_OP3_OFFLINE_JALUR_TUNGGAL_DAN_RUNTIME_2026-11-13.md','environment':{'python':platform.python_version(),'torch':torch.__version__,'ultralytics':ultralytics.__version__},'sources':{str(p.relative_to(ROOT)):sha256(p) for p in [T38/'input_manifest.json',T38/'results.json',T43/'input_manifest.json',T43/'results.json',PLAN]},'counts':{k:len(v) for k,v in splits.items()},'checks':[]}
 def save():(RUN/'identity.json').write_text(json.dumps(report,indent=2)+'\n')
 save()
 try:
  yamls={key:build_dataset(RUN/key,frames,{'primary','negative','partial'}) for key,frames in splits.items()}
  for name,c in models.items():
   print('VALIDATING',name,flush=True);model=YOLO(c['path'],task='detect')
   if tuple(model.names.values())!=CLASSES:raise ValueError('Class mismatch')
   for k,yaml in yamls.items():
    actual=ap_metrics(model,yaml,RUN,f'val_{k}_{name}')
    expected=old38['models'][name][k.split('_',1)[1]]['ap'] if k.startswith('t38') else old43['models'][name]['splits'][k[4:]]['ap']
    compare_ap(actual,expected,name+'/'+k);report['checks'].append({'model':name,'dataset':k,'check':'AP50/AP50-95 overall and per class','pass':True});save()
   for label,frames in [('t38',t38),('t43',t43)]:
    counts={k:empty_counts() for k in splits if k.startswith(label)};neg=Counter()
    for i,frame in enumerate(frames,1):
     r=model.predict(source=str(frame['image']),imgsz=640,conf=.25,iou=.7,device='cpu',augment=False,verbose=False)[0]
     if r.orig_shape!=(480,640):raise ValueError('Unexpected image shape')
     det=[{'class_id':int(c),'confidence':float(q),'xyxy':[float(v) for v in xy]} for c,q,xy in zip(r.boxes.cls.cpu().tolist(),r.boxes.conf.cpu().tolist(),r.boxes.xyxy.cpu().tolist()) if q>.25]
     score,_=score_frame(frame['gt'],det)
     for k,subset in splits.items():
      if k.startswith(label) and frame in subset:add_counts(counts[k],score)
     if frame['role']=='negative' and det:neg['all']+=1
     if i%100==0:print(name,label,i,'/',len(frames),flush=True)
    for k,raw in counts.items():
     got=score_counts(raw)
     exp=old38['models'][name][k.split('_',1)[1]]['operating'] if label=='t38' else old43['models'][name]['splits'][k[4:]]['operating']
     compare_counts(got,exp,name+'/'+k);report['checks'].append({'model':name,'dataset':k,'check':'operating per-class TP/FP/FN, precision/recall/mean-class-F1','pass':True});save()
   print('MODEL PASS',name,flush=True)
  report['status']='complete';save();print('IDENTITY PASS',flush=True)
 except Exception as e:
  report['status']='failed';report['error']=str(e);save();traceback.print_exc();raise
if __name__=='__main__':main()
