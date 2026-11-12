"""Aggregate a locally saved teacher-validator prediction JSON for T43 diagnosis."""
import collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'ros2_packages/op3_camera_eval'),str(ROOT/'ros2_packages/op3_multi_session_eval')]
import numpy as np
from op3_camera_eval.evaluate import read_labels
from op3_multi_session_eval.evaluate import score_frame
RUN=ROOT/'runs/op3_t43_sensitivity/20261112_confidence_01';BASE=ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260';DOC=ROOT/'dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 path=RUN/'diagnostics/teacher_val/predictions.json';saved=json.loads(path.read_text());frames=json.loads((BASE/'input_manifest.json').read_text())['frames']; by=collections.defaultdict(list)
 for x in saved:
  b=x['bbox'];by[str(x['image_id'])].append({'class_id':x['category_id']-1,'confidence':x['score'],'xyxy':[b[0],b[1],b[0]+b[2],b[1]+b[3]]})
 result={}
 for threshold in (.001,.05,.15,.25):
  matched=0;confidence=[]
  for key,f in frames.items():
   cnt,details=score_frame(read_labels(Path(f['label'])),[x for x in by[key] if x['confidence']>threshold]);matched+=cnt['gawang']['true_positives'];confidence.extend(x['confidence'] for x in details if x['class_id']==1 and x['matched'])
  result[str(threshold)]={'goal_tp':matched,'confidence_median_of_matched':float(np.median(confidence)) if confidence else None}
 key='20261112_t43_idle_objek_ulang_01__frame_000001';sample=[x for x in by[key] if x['class_id']==1];pred=next(json.loads(line) for line in (RUN/'predictions_teacher_fp32.jsonl').read_text().splitlines() if json.loads(line)['key']==key);goal=[x for x in pred['detections'] if x['class_id']==1]
 out={'validator_saved_json_sha256':sha(path),'warning':'Validator JSON rounds scores to 5 decimals and boxes to 3 decimals; diagnostics only, not replacement for unrounded AP.','method':'shared T43 score_frame, class/IoU >=0.5, confidence strictly greater, teacher only','goal_tp_rounded_validator':result,'probe':{'validator_tensor_shape_nchw':[1,3,512,672],'predict_input_shape_nchw':[1,3,480,640],'validator_nms_multi_label':True,'predict_nms_multi_label':False,'example_frame':key,'validator_goal_scores':[x['confidence'] for x in sample],'predict_goal_scores':[x['confidence'] for x in goal],'one_frame_predict_alternative_input':{'rect_false_imgsz_640_goal_scores':[0.08711],'rect_false_imgsz_512x672_goal_scores':[0.49869]},'note':'Padding, preprocessor and NMS differ; individual causal contributions have not been isolated.'}}
 output=DOC/'diagnostik_teacher_agregat.json'
 with output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
