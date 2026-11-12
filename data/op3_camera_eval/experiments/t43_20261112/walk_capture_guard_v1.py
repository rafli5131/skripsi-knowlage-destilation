"""Satu sesi gait maksimum 63 detik dengan capture setelah ack start."""
from __future__ import annotations
import argparse,json,os,signal,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import rclpy
from std_msgs.msg import String
from op3_equal_live_walk.guard import Guard,HEAD_LIMIT_RAD

ROOT=Path(__file__).resolve().parents[3]

def alive(pid):
 try:
  os.kill(pid,0)
  return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except (OSError,IndexError):return False

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--session-id',required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--baseline-pan',type=float,required=True);p.add_argument('--baseline-tilt',type=float,required=True);p.add_argument('--preview-csv',type=Path,required=True);p.add_argument('--viewer-pid',type=int,required=True);args=p.parse_args()
 if (ROOT/'data/op3_camera_eval/sessions'/args.session_id).exists():p.error('Sesi sudah ada')
 args.out_dir.mkdir(parents=True,exist_ok=False)
 report={'started_utc':datetime.now(timezone.utc).isoformat(),'session_id':args.session_id,'status':'starting','max_gait_seconds':63,'max_head_delta_rad':HEAD_LIMIT_RAD,'frames_requested':50,'preview_csv':str(args.preview_csv),'viewer_pid':args.viewer_pid}
 def stop_signal(_signum,_frame):raise KeyboardInterrupt('operator interrupt')
 signal.signal(signal.SIGTERM,stop_signal)
 rclpy.init();node=Guard(args.baseline_pan,args.baseline_tilt,args.out_dir/'head_guard_samples.csv');proc=None;capture_log=None;started=False;stop_ack=False
 def check():
  if node.head_violation:raise RuntimeError('Kepala menyimpang lebih dari dua count')
  if node.last_joint_monotonic is None or time.monotonic()-node.last_joint_monotonic>2:raise RuntimeError('Telemetry sendi terputus')
  if not alive(args.viewer_pid):raise RuntimeError('Proses preview tertutup')
  if not args.preview_csv.is_file() or time.time()-args.preview_csv.stat().st_mtime>5:raise RuntimeError('Detector preview tidak menerima frame baru')
 try:
  deadline=time.monotonic()+8
  while node.last_joint_monotonic is None and time.monotonic()<deadline:rclpy.spin_once(node,timeout_sec=.05)
  check()
  discovery_deadline=time.monotonic()+8
  while node.publisher.get_subscription_count()<1 and time.monotonic()<discovery_deadline:
   rclpy.spin_once(node,timeout_sec=.05);check()
  if node.publisher.get_subscription_count()<1:raise RuntimeError('Subscriber walking tidak tersedia setelah waktu tunggu')
  node.command('start');started=True;report['start_command_utc']=datetime.now(timezone.utc).isoformat()
  deadline=time.monotonic()+3
  while node.ack_utc is None and time.monotonic()<deadline:rclpy.spin_once(node,timeout_sec=.05);check()
  if node.ack_utc is None:raise RuntimeError('Ack start walking tidak diterima')
  report['start_ack_utc']=node.ack_utc.isoformat();print('GAIT_STARTED '+report['start_ack_utc'],flush=True)
  cmd=[sys.executable,str(ROOT/'scripts/capture_op3_frames.py'),'--session-id',args.session_id,'--condition','walking','--topic','/thesis/image_raw','--max-frames','50','--interval-sec','1.0','--duration-sec','80.0']
  capture_log=(args.out_dir/'capture_stdout.log').open('x');proc=subprocess.Popen(cmd,cwd=str(ROOT),stdout=capture_log,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=node.ack_monotonic+63
  while proc.poll() is None:
   rclpy.spin_once(node,timeout_sec=.05);check()
   if node.stop_ack_utc is not None:raise RuntimeError('Gait berhenti sebelum capture selesai')
   if time.monotonic()>=deadline:raise TimeoutError('Batas gait 63 detik terlampaui')
  report['capture_exit_code']=proc.returncode
  if proc.returncode!=0:raise RuntimeError('Proses capture gagal')
  manifest=ROOT/'data/op3_camera_eval/sessions'/args.session_id/'capture_manifest.json'
  data=json.loads(manifest.read_text());report['capture_manifest']=str(manifest);report['frames_captured']=data['frame_count'];report['capture_status']=data['status']
  if data['frame_count']!=50 or data['status']!='max_frames_reached':raise RuntimeError('Capture tidak lengkap')
  report['status']='capture_completed'
 except BaseException as e:report['status']='failed';report['error']=f'{type(e).__name__}: {e}'
 finally:
  if started:
   node.command('stop');report['stop_command_utc']=datetime.now(timezone.utc).isoformat()
  if proc is not None and proc.poll() is None:
   os.killpg(proc.pid,signal.SIGINT)
   try:proc.wait(timeout=4)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM)
  if started:
   deadline=time.monotonic()+3
   while node.stop_ack_utc is None and time.monotonic()<deadline:
    try:rclpy.spin_once(node,timeout_sec=.05)
    except Exception:break
   stop_ack=node.stop_ack_utc is not None
   report['stop_ack_utc']=node.stop_ack_utc.isoformat() if stop_ack else None
   if not stop_ack:node.command('stop');report['status']='failed';report['stop_error']='Ack stop tidak diterima; stop dikirim ulang'
  if capture_log is not None:capture_log.close()
  report['max_head_delta_rad_observed']=node.max_head_delta;report['head_violation']=node.head_violation;report['finished_utc']=datetime.now(timezone.utc).isoformat();node.sample_stream.close()
  with (args.out_dir/'gait_guard.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
  print(json.dumps(report,indent=2),flush=True);node.destroy_node();rclpy.shutdown()
 return 0 if report['status']=='capture_completed' and stop_ack else 1

if __name__=='__main__':raise SystemExit(main())
