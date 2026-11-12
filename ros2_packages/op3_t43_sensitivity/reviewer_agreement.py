"""Freeze Dipo review hashes and compare against final Bhre labels on 52 frames."""
import hashlib,json,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'ros2_packages/op3_camera_eval'))
from op3_camera_eval.evaluate import read_labels,iou_xyxy
EXP=ROOT/'data/op3_camera_eval/experiments/t43_20261112';SENS=ROOT/'data/op3_camera_eval/experiments/t43_sensitivity_20261112_01';RUN=ROOT/'runs/op3_t43_sensitivity/20261112_confidence_01';S=ROOT/'data/op3_camera_eval/sessions'; C=['ball','gawang','robot']
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def corners(b):
 _,x,y,w,hh=b;return [x-w/2,y-hh/2,x+w/2,y+hh/2]
def main():
 selection_path=EXP/'blind_review_52/selection_manifest.json'; audit_path=EXP/'review_260_audit_and_frozen_hashes.json';prep=json.loads((SENS/'preparation_manifest.json').read_text());samples=json.loads(selection_path.read_text())['samples'];audit=json.loads(audit_path.read_text())
 assert len(samples)==52 and h(selection_path)==prep['selection_manifest_sha256'] and h(SENS/'rules_konvensi_t43.json')==prep['rules_t43_sha256']
 reviewer=SENS/'reviewer2'; logs=reviewer/'labels_reviewed/review_log.jsonl';entries=[json.loads(x) for x in logs.read_text().splitlines() if x.strip()];expected={s['blind_image'] for s in samples}
 if {x['image'] for x in entries}!=expected or {x['reviewer'] for x in entries}!={'Dipo'}:raise ValueError('Review log incomplete or reviewer inconsistent')
 if {x.stem for x in (reviewer/'labels_reviewed').glob('*.txt')}!={Path(x).stem for x in expected}:raise ValueError('Missing/extra labels')
 counts={c:Counter() for c in C}; overlaps={c:[] for c in C}; per_frame=[];items=[]
 for s in samples:
  img=reviewer/'images'/s['blind_image']; label=reviewer/'labels_reviewed'/(Path(s['blind_image']).stem+'.txt'); orig=S/s['session']/'labels_reviewed'/(Path(s['image']).stem+'.txt'); actual=S/s['session']/'images'/s['image']; frozen=audit['frames'][f"{s['session']}/{s['image']}"]
  if h(img)!=s['sha256'] or h(actual)!=frozen['image_sha256'] or h(img)!=h(actual) or h(orig)!=frozen['reviewed_label_sha256']:raise ValueError('Image or original label hash mismatch')
  a=read_labels(orig);b=read_labels(label);detail={}
  for i,c in enumerate(C):
   aa=[x for x in a if x[0]==i];bb=[x for x in b if x[0]==i];matrix=np.array([[iou_xyxy(corners(x),corners(y)) for y in bb] for x in aa]);matches=[]
   if aa and bb:
    # Prefer the highest number of IoU>=0.5 matches, then their total IoU.
    rr,cc=linear_sum_assignment(-((matrix>=.5)*(1+matrix/(max(len(aa),len(bb))+1))))
    matches=[float(matrix[x,y]) for x,y in zip(rr,cc) if matrix[x,y]>=.5]
   counts[c].update({'bhre':len(aa),'dipo':len(bb),'matches':len(matches),'bhre_unmatched':len(aa)-len(matches),'dipo_unmatched':len(bb)-len(matches)})
   overlaps[c].extend(matches);detail[c]={'bhre':len(aa),'dipo':len(bb),'matched_ious':matches}
  per_frame.append({'blind_image':s['blind_image'],'session':s['session'],'image':s['image'],'classes':detail})
  items.append({'blind_image':s['blind_image'],'image_sha256':h(img),'dipo_label_sha256':h(label),'bhre_label_sha256':h(orig),'session':s['session'],'image':s['image']})
 result={}
 for c in C:
  v=dict(counts[c]); v['fraction_bhre_matched']=v['matches']/v['bhre'] if v['bhre'] else None;v['fraction_dipo_matched']=v['matches']/v['dipo'] if v['dipo'] else None;v['iou_mean']=float(np.mean(overlaps[c])) if overlaps[c] else None;v['iou_median']=float(np.median(overlaps[c])) if overlaps[c] else None;result[c]=v
 manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'Dipo','review_log_sha256':h(logs),'review_log_entries':len(entries),'selection_manifest_sha256':h(selection_path),'rules_sha256':prep['rules_t43_sha256'],'bhre_review_audit_sha256':h(audit_path),'items':items,'limitations':['Rules were clarified after Bhre initial T43 annotation; reviewer and convention effects are confounded','Bhre previously saw Hybrid preview; prior Dipo exposure is unknown','Images belong to one setting and are correlated']}
 with (SENS/'reviewer2_completion_manifest.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
 report={'created_utc':datetime.now(timezone.utc).isoformat(),'status':'reviewer2_complete','reviewer2_completion_sha256':h(SENS/'reviewer2_completion_manifest.json'),'matching':'one-to-one classwise, maximize match count at IoU >= 0.5 then IoU','frames':52,'classes':result,'per_frame':per_frame,'limitations':manifest['limitations']}
 with (RUN/'reviewer2_agreement.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'classes':result,'output':str(RUN/'reviewer2_agreement.json')},indent=2))
if __name__=='__main__':main()
