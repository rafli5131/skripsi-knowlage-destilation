"""Check predictor factor endpoint for AP and operating statistics."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'runs/op3_single_path_eval/20261116_analysis_01';SRC=RUN/'comparison.json';OUT=RUN/'endpoint_operating_audit.json'
def main():
 x=json.loads(SRC.read_text());assert x['status']=='complete';out=[]
 for n,groups in x['models'].items():
  for group,y in groups.items():
   a=y['variants']['predict_protocol'];b=y['variants']['480_single'];issues=[]
   for cls in ('ball','gawang','robot'):
    for k in ('precision','recall','F1','ground_truth_count','predictions_above_confidence','true_positives_at_iou50'):
     if abs(a['operating']['per_class'][cls][k]-b['operating']['per_class'][cls][k])>1e-9:issues.append(f'{cls}/{k}')
   for k in ('precision','recall','F1','F1_rerata_per_kelas'):
    if abs(a['operating']['overall'][k]-b['operating']['overall'][k])>1e-9:issues.append('macro/'+k)
   if a['negative_frames_with_false_positive']!=b['negative_frames_with_false_positive']:issues.append('negative_frame_fp')
   out.append({'model':n,'dataset':group,'predict_operating_matches':not issues,'issues':issues,'val_AP_endpoint_matches':y['factor_endpoint_validation']['val_reproduced'],'predict_AP_endpoint_matches':y['factor_endpoint_validation']['predict_reproduced']})
 if len(out)!=20:raise ValueError('expected 20 model/dataset pairs')
 payload={'created_utc':datetime.now(timezone.utc).isoformat(),'comparison_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'tolerance':1e-9,'checks':out}
 with OUT.open('x') as f:json.dump(payload,f,indent=2);f.write('\n')
 print('Predict operating endpoint matches:',sum(a['predict_operating_matches'] for a in out),'/',len(out),'validator AP matches:',sum(a['val_AP_endpoint_matches'] for a in out),'/',len(out))
if __name__=='__main__':main()
