"""Offline isolated CPU replay of frozen T43 frames; no ROS or robot I/O."""
import argparse,csv,hashlib,json,os,statistics,time
from datetime import datetime,timezone
from pathlib import Path
os.environ["YOLO_AUTOINSTALL"] = "False"
import cv2,numpy as np,psutil,torch,ultralytics,yaml
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'runs/op3_single_path_eval/20261116_runtime_01';EXP=ROOT/'data/op3_camera_eval/experiments/t43_20261112';N=300;WARM=30

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def threads():
 out={}
 for x in psutil.Process().threads():
  try:name=Path(f'/proc/self/task/{x.id}/comm').read_text().strip()
  except (FileNotFoundError,ProcessLookupError):name='<terminated>'
  out[x.id]={'name':name,'cpu_seconds':x.user_time+x.system_time}
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['teacher_fp32','hybrid_full_seed1337'],required=True);ap.add_argument('--variant',choices=['tracking','no_tracking','cv_one_thread','no_gmc'],required=True);args=ap.parse_args()
 assert json.loads((ROOT/'runs/op3_single_path_eval/20261116_identity_01/identity.json').read_text())['status']=='complete'
 plan=json.loads((EXP/'frozen_plan.json').read_text());entry=plan['checkpoints'][args.model];assert sha(Path(entry['path']))==entry['sha256'];capture=json.loads((EXP/'capture_260_manifest.json').read_text());frames=[];hashes=[]
 for sess in capture['sessions']:
  for name,h in sess['images'].items():
   path=ROOT/'data/op3_camera_eval/sessions'/sess['session']/'images'/name
   if sha(path)!=h:raise ValueError('Frame hash mismatch')
   im=cv2.imread(str(path))
   if im is None or im.shape!=(480,640,3):raise ValueError('Image invalid')
   frames.append(im);hashes.append(h)
 if len(frames)!=260:raise ValueError('Expected 260 distinct source frames')
 torch.set_num_threads(4);torch.set_num_interop_threads(2)
 if args.variant=='cv_one_thread':cv2.setNumThreads(1)
 tracker=Path(ultralytics.__file__).parent/'cfg/trackers/botsort.yaml';cfg=yaml.safe_load(tracker.read_text());variant_dir=OUT/'replay'/args.model/args.variant;variant_dir.mkdir(parents=True,exist_ok=False)
 track_path=str(tracker)
 if args.variant=='no_gmc':
  cfg['gmc_method']='none';local=variant_dir/'botsort_no_gmc.yaml';local.write_text(yaml.safe_dump(cfg,sort_keys=False));track_path=str(local.resolve())
 model=YOLO(entry['path'],task='detect');use_track=args.variant!='no_tracking'
 def infer(i):
  opts={'source':frames[i%260],'imgsz':640,'batch':1,'device':'cpu','conf':.25,'iou':.45,'verbose':False,'save':False,'plots':False,'stream':False,'max_det':300}
  if use_track:r=model.track(**opts,tracker=track_path,persist=True)[0]
  else:r=model.predict(**opts)[0]
  r.plot();return r
 for i in range(WARM):infer(i)
 process=psutil.Process();before=process.cpu_times();before_cpu=before.user+before.system;start=time.perf_counter();initial=threads();last={k:v.copy() for k,v in initial.items()};maximum_threads=len(initial);records=[]
 for i in range(N):
  t=time.perf_counter();r=infer(WARM+i);elapsed=(time.perf_counter()-t)*1000;speed=r.speed
  records.append({'frame_index':i+1,'source_index':(WARM+i)%260,'preprocess_ms':float(speed.get('preprocess',0)),'inference_ms':float(speed.get('inference',0)),'postprocess_ms':float(speed.get('postprocess',0)),'replay_end_to_end_ms':elapsed,'residual_ms':elapsed-sum(float(speed.get(x,0)) for x in ('preprocess','inference','postprocess'))})
  snap=threads();maximum_threads=max(maximum_threads,len(snap));last.update(snap)
  if (i+1)%100==0:print(args.model,args.variant,i+1,'/',N,flush=True)
 stop=time.perf_counter();after=process.cpu_times();used=after.user+after.system-before_cpu;wall=stop-start
 with (variant_dir/'frame_log.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
 thread_data=[]
 for tid,x in last.items():
  start_cpu=initial.get(tid,{}).get('cpu_seconds',0.0);dt=max(0.0,x['cpu_seconds']-start_cpu)
  thread_data.append({'tid':tid,'name':x['name'],'cpu_seconds_sampled':dt,'present_at_start':tid in initial})
 thread_data.sort(key=lambda x:x['cpu_seconds_sampled'],reverse=True)
 result={'model':args.model,'variant':args.variant,'created_utc':datetime.now(timezone.utc).isoformat(),'frames':N,'warmup_frames':WARM,'unique_source_images':len(frames),'frame_reuse':'260 source frames cycled deterministically; 300 measurement frames include repeats; 30 preceding warmup frames','tracking':use_track,'preview_plot':True,'tracker_config':track_path if use_track else None,'installed_tracker_sha256':sha(tracker),'gmc_method':cfg.get('gmc_method') if use_track else None,'opencv_num_threads':cv2.getNumThreads(),'torch_num_threads':torch.get_num_threads(),'torch_interop_threads':torch.get_num_interop_threads(),'checkpoint_sha256':entry['sha256'],'capture_manifest_sha256':sha(EXP/'capture_260_manifest.json'),'process_cpu_seconds':used,'wall_seconds':wall,'cpu_ms_per_frame':used*1000/N,'cpu_percent_one_logical':100*used/wall,'cpu_percent_16_logical':100*used/wall/16,'input_rate_fps':N/wall,'max_thread_count_sampled':maximum_threads,'thread_cpu_sampled':thread_data,'thread_cpu_note':'Sampled once per frame via psutil /proc; short-lived threads may be missed or undercounted; total process CPU is measured separately.','timings':{},'limitations':['Replay input is preloaded arrays, no ROS or camera, no messages are published','replay end-to-end includes model.track/predict and result.plot but excludes ROS conversion, publish and CSV logging','frame repetitions and different image content may affect tracking/GMC','CPU and wall measurements include per-frame thread sampling overhead','thread CPU time is sampled and is a lower bound for short-lived threads'],'frame_log_sha256':sha(variant_dir/'frame_log.csv')}
 for k in ['preprocess_ms','inference_ms','postprocess_ms','replay_end_to_end_ms','residual_ms']:
  v=[x[k] for x in records];result['timings'][k]={'mean_ms':statistics.mean(v),'median_ms':statistics.median(v),'p95_ms':float(np.percentile(v,95))}
 (variant_dir/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print('REPLAY COMPLETE',args.model,args.variant,flush=True)
if __name__=='__main__':main()
