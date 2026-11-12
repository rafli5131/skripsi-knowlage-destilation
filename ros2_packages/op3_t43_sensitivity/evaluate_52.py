"""Offline evaluation of four frozen T43 models on one reviewed 52-frame label set."""
import argparse,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'ros2_packages/op3_camera_eval'),str(ROOT/'ros2_packages/op3_multi_session_eval')]
from ultralytics import YOLO
from op3_camera_eval.evaluate import CLASSES,read_labels,sha256
from op3_multi_session_eval.evaluate import build_dataset,ap_metrics,score_frame,empty_counts,add_counts,score_counts
E=ROOT/'data/op3_camera_eval/experiments/t43_20261112';S=ROOT/'data/op3_camera_eval/experiments/t43_sensitivity_20261112_01';SESS=ROOT/'data/op3_camera_eval/sessions';RUN=ROOT/'runs/op3_t43_sensitivity/20261112_confidence_01'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--label-set',choices=['bhre','dipo','alternative'],required=True);args=parser.parse_args();kind=args.label_set
 selection=json.loads((E/'blind_review_52/selection_manifest.json').read_text());audit=json.loads((E/'review_260_audit_and_frozen_hashes.json').read_text());plan=json.loads((E/'frozen_plan.json').read_text());sweep=json.loads((RUN/'run_manifest.json').read_text());assert sweep['status']=='complete'
 completion=json.loads((S/'reviewer2_completion_manifest.json').read_text());assert len(completion['items'])==52
 if kind=='alternative':
  alt=json.loads((S/'alternative_completion_manifest.json').read_text());assert len(alt['items'])==52
 else:alt=None
 by_sample={x['blind_image']:x for x in completion['items']};by_alt={x['blind_image']:x for x in alt['items']} if alt else {};frames=[];manifest={'label_set':kind,'created_utc':datetime.now(timezone.utc).isoformat(),'models':plan['checkpoints'],'selection_sha256':sha256(E/'blind_review_52/selection_manifest.json'),'reviewer2_completion_sha256':sha256(S/'reviewer2_completion_manifest.json'),'alternative_completion_sha256':sha256(S/'alternative_completion_manifest.json') if alt else None,'frames':{}}
 for item in selection['samples']:
  name=item['blind_image']; image=S/'reviewer2/images'/name;src=SESS/item['session'];entry=by_sample[name]
  if kind=='bhre':label=src/'labels_reviewed'/(Path(item['image']).stem+'.txt');expected=entry['bhre_label_sha256']
  elif kind=='dipo':label=S/'reviewer2/labels_reviewed'/(Path(name).stem+'.txt');expected=entry['dipo_label_sha256']
  else:label=S/'alternative_convention/labels_reviewed'/(Path(name).stem+'.txt');expected=by_alt[name]['label_sha256']
  if sha256(image)!=item['sha256'] or sha256(label)!=expected:raise ValueError('Changed image or frozen label: '+name)
  gt=read_labels(label);key=item['session']+'__'+Path(item['image']).stem;role='negative' if item['role'].endswith('kosong') else 'primary'
  frames.append({'key':key,'image':image,'label':label,'gt':gt,'role':role,'session':item['session']});manifest['frames'][key]={'image_sha256':sha256(image),'label_sha256':sha256(label),'role':role}
 if len(frames)!=52:raise ValueError('Expected 52 frames')
 out=RUN/'label_52'/kind;out.mkdir(parents=True,exist_ok=False);(out/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 yaml=build_dataset(out,frames,{'primary','negative'});report={'status':'running','label_set':kind,'models':{}}
 for name,chk in plan['checkpoints'].items():
  print(kind,name,flush=True)
  if sha256(Path(chk['path']))!=chk['sha256']:raise ValueError('Changed checkpoint '+name)
  predpath=RUN/f'predictions_{name}.jsonl'
  if sha256(predpath)!=sweep['outputs']['predictions_sha256'][name]:raise ValueError('Changed predictions '+name)
  pred={x['key']:x for x in (json.loads(line) for line in predpath.read_text().splitlines())}
  model=YOLO(chk['path'],task='detect');assert tuple(model.names.values())==CLASSES
  ap=ap_metrics(model,yaml,out,f'val_{name}');counts=empty_counts();negfp=0
  for frame in frames:
   detections=[d for d in pred[frame['key']]['detections'] if d['confidence']>.25];c,_=score_frame(frame['gt'],detections);add_counts(counts,c)
   if frame['role']=='negative' and detections:negfp+=1
  op=score_counts(counts);p=op['macro']['precision'];r=op['macro']['recall'];op['macro']['F1_mean_per_class']=op['macro']['F1'];op['macro']['F1_harmonic_macro_precision_recall']=2*p*r/(p+r) if p+r else 0
  report['models'][name]={'ap':ap,'operating':op,'negative_frames_with_fp':negfp};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 report['status']='complete';(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print('DONE',kind,flush=True)
if __name__=='__main__':main()
