"""Compare predictor and 2x2 tensor/NMS paths on frozen OP3 frames."""
import hashlib,json,math,subprocess,sys,types
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import cv2,numpy as np,torch
from ultralytics import YOLO
from ultralytics.data.augment import LetterBox
from ultralytics.utils import nms
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'ros2_packages/op3_single_path_eval'))
from identity import ROOT as BASE, RUN as IDENTITY, T38,T43,PLAN,make_frames
from op3_camera_eval.evaluate import CLASSES,sha256
OUT=ROOT/'runs/op3_single_path_eval/20261116_analysis_01';REV='ade031a89d0e9d5cb088c5615e31746fd9c43a4c'

def ref_module():
 source=subprocess.check_output(['git','show',REV+':scripts/verify_test_inference_path.py'],cwd=ROOT);m=types.ModuleType('op3_test_reference');m.__file__=str(ROOT/'scripts/verify_test_inference_path.py');sys.modules[m.__name__]=m;exec(compile(source,m.__file__,'exec'),m.__dict__);return m,hashlib.sha256(source).hexdigest()

def gt(frame):
 cls=np.array([x[0] for x in frame['gt']],dtype=np.int64); boxes=np.array([[(x-w/2)*640,(y-h/2)*480,(x+w/2)*640,(y+h/2)*480] for _,x,y,w,h in frame['gt']],dtype=np.float64).reshape(-1,4);return cls,boxes

def eval_predictions(frames,preds,ref,with_ap=True):
 tps=[];confs=[];classes=[];targets=[];neg_fp=0
 for f in frames:
  pc,boxes,conf=preds[f['key']];gc,gb=gt(f);tps.append(ref.match_predictions(pc,gc,ref.box_iou(gb,boxes)));confs.append(conf);classes.append(pc);targets.append(gc)
  if f['role']=='negative' and (conf>.25).any():neg_fp+=1
 tp=np.concatenate(tps,axis=0);co=np.concatenate(confs);pc=np.concatenate(classes);g=np.concatenate(targets)
 out={'operating':ref.operating_point(tp,co,pc,g),'negative_frames_with_false_positive':neg_fp,'predictions':len(co)}
 if with_ap:out['ap']=ref.average_precision(tp,co,pc,g)
 return out

def manual_pair(model,frame,shape):
 if shape=='predict': image=frame;pad=(0,0)
 else: image=LetterBox(new_shape=(512,672),auto=False,scaleup=False)(image=frame);pad=(16,16)
 rgb=np.ascontiguousarray(image[:,:,::-1].transpose(2,0,1));tensor=torch.from_numpy(rgb).unsqueeze(0).float()/255
 with torch.inference_mode():raw=model.model(tensor)
 if isinstance(raw,(tuple,list)):raw=raw[0]
 result={}
 for multi in (False,True):
  out=nms.non_max_suppression(raw.clone(),conf_thres=.001,iou_thres=.7,nc=3,multi_label=multi,agnostic=False,max_det=300)[0]
  boxes=out[:,:4].cpu().numpy().astype(np.float64);boxes[:,[0,2]]-=pad[0];boxes[:,[1,3]]-=pad[1];boxes[:,[0,2]]=boxes[:,[0,2]].clip(0,640);boxes[:,[1,3]]=boxes[:,[1,3]].clip(0,480)
  result[multi]=(out[:,5].cpu().numpy().astype(np.int64),boxes,out[:,4].cpu().numpy().astype(np.float64))
 return result

def predict(model,image,conf,iou):
 r=model.predict(source=image,imgsz=640,conf=conf,iou=iou,device='cpu',augment=False,verbose=False,max_det=300,agnostic_nms=False)[0]
 return r.boxes.cls.cpu().numpy().astype(np.int64),r.boxes.xyxy.cpu().numpy().astype(np.float64),r.boxes.conf.cpu().numpy().astype(np.float64)

def diff(x,y):return abs(float(x)-float(y))

def main():
 if json.loads((IDENTITY/'identity.json').read_text())['status']!='complete':raise ValueError('Identity test incomplete')
 torch.set_num_threads(4);torch.set_num_interop_threads(2);ref,refsha=ref_module();t38=make_frames(T38);t43=make_frames(T43);allframes=t38+t43
 groups={'t38_primary':[x for x in t38 if x['role'] in ('primary','negative')],'t38_partial':[x for x in t38 if x['role']=='partial'],'t43_idle':[x for x in t43 if 'idle_' in x['session']],'t43_walking':[x for x in t43 if 'walk_' in x['session']],'t43_combined':t43}
 assert [len(g) for g in groups.values()]==[260,50,130,130,260]
 models=json.loads(PLAN.read_text())['checkpoints'];old38=json.loads((T38/'results.json').read_text());old43=json.loads((T43/'results.json').read_text());OUT.mkdir(parents=True,exist_ok=False)
 report={'status':'running','created_utc':datetime.now(timezone.utc).isoformat(),'identity_sha256':sha256(IDENTITY/'identity.json'),'reference_git_revision':REV,'reference_script_sha256':refsha,'settings':{'device':'cpu','precision':'FP32','imgsz':640,'confidence_floor':.001,'nms_iou_protocol':.7,'nms_iou_runtime':.45,'operating_confidence_strict':.25,'iou_match':.5,'matching':'same-class greedy IoU from server verification script','manual_480':'no scaling/padding','manual_512':'no scaling; 16 px pad per side, LetterBox scaleup=False','manual_nms':'ultralytics.utils.nms.non_max_suppression (ops alias absent in 8.4.130)'},'models':{}}
 def save():(OUT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
 save()
 for name,c in models.items():
  if sha256(Path(c['path']))!=c['sha256']:raise ValueError('checkpoint mismatch '+name)
  print('MODEL',name,flush=True);model=YOLO(c['path'],task='detect');predictions={v:{} for v in ['predict_protocol','predict_runtime','480_single','480_multi','512_single','512_multi']}
  detail=OUT/f'predictions_{name}.jsonl'
  with detail.open('x') as f:
   for i,fr in enumerate(allframes,1):
    image=cv2.imread(str(fr['image']));
    if image is None or image.shape!=(480,640,3):raise ValueError('Unexpected image '+str(fr['image']))
    outputs={'predict_protocol':predict(model,image,.001,.7),'predict_runtime':predict(model,image,.25,.45)}
    for shape in ('480','512'):
     pair=manual_pair(model,image,'predict' if shape=='480' else 'val')
     for multi in (False,True):outputs[shape+('_multi' if multi else '_single')]=pair[multi]
    for k,x in outputs.items():predictions[k][fr['key']]=x
    f.write(json.dumps({'key':fr['key'],'paths':{k:{'class':x[0].tolist(),'xyxy':x[1].tolist(),'confidence':x[2].tolist()} for k,x in outputs.items()}})+'\n')
    if i%100==0 or i==len(allframes):print(name,i,'/',len(allframes),flush=True)
  values={}
  for g,frames in groups.items():
   variants={k:eval_predictions(frames,x,ref,with_ap=(k!='predict_runtime')) for k,x in predictions.items()}
   val=old38['models'][name][g[4:]]['ap'] if g.startswith('t38') else old43['models'][name]['splits'][g[4:]]['ap']
   fval=variants['512_multi']['ap'];pred=variants['predict_protocol']['ap'];fp=variants['480_single']['ap']
   delta_val={k:diff(fval['overall'][k],val[k]) for k in ('mAP50','mAP50-95')};delta_pred={k:diff(fp['overall'][k],pred['overall'][k]) for k in ('mAP50','mAP50-95')}
   for c2 in val['per_class']:
    for metric in ('mAP50','mAP50-95'):delta_val[c2+'_'+metric]=diff(fval['per_class'][c2][metric],val['per_class'][c2][metric]);delta_pred[c2+'_'+metric]=diff(fp['per_class'][c2][metric],pred['per_class'][c2][metric])
   checks={'val_max_abs_diff':max(delta_val.values()),'val_deltas':delta_val,'predict_max_abs_diff':max(delta_pred.values()),'predict_deltas':delta_pred,'tolerance':1e-6}
   checks['val_reproduced']=checks['val_max_abs_diff']<=checks['tolerance'];checks['predict_reproduced']=checks['predict_max_abs_diff']<=checks['tolerance'];checks['factor_interpretation_allowed']=checks['val_reproduced'] and checks['predict_reproduced']
   values[g]={'variants':variants,'factor_endpoint_validation':checks}
  report['models'][name]=values;save();print('MODEL DONE',name,flush=True)
 report['status']='complete';save();print('COMPARE COMPLETE',flush=True)
if __name__=='__main__':main()
