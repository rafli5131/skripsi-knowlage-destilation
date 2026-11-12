"""Map legs and shoulder pitch to walking; monitor head throughout."""
import json,time,os
from datetime import datetime,timezone
from pathlib import Path
import rclpy
from robotis_controller_msgs.srv import SetJointModule
from std_msgs.msg import String
from op3_t43_walk_ready.__main__ import Monitor,spin_until,get_modules,HEAD,LEGS

JOINTS=LEGS+['l_sho_pitch','r_sho_pitch'];PREVIEW=Path('/tmp/op3-t43-preview-ziwkQm/hybrid_preview.csv');VIEWER_PID=23446

def preview_ready():
 try:os.kill(VIEWER_PID,0);return Path(f'/proc/{VIEWER_PID}/stat').read_text().split()[2]!='Z' and time.time()-PREVIEW.stat().st_mtime<5
 except (OSError,IndexError):return False

def main():
 out=Path('runs/op3_t43_return_walking');out.mkdir(parents=True,exist_ok=True);path=out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 report={'started_utc':datetime.now(timezone.utc).isoformat(),'status':'starting','requested_joints':JOINTS,'head_commanded':False,'walking_start_sent':False}
 rclpy.init();node=Monitor();mapped=False
 try:
  if not preview_ready():raise RuntimeError('Preview tidak aktif')
  if not node.get_client.wait_for_service(timeout_sec=5) or not node.set_client.wait_for_service(timeout_sec=5):raise RuntimeError('Service controller tidak tersedia')
  spin_until(node,lambda:len(node.history)>=15,5);node.baseline=dict(node.history[-1]['head']);report['head_baseline_rad']=node.baseline
  before=get_modules(node,(*HEAD,*JOINTS));report['modules_before']=before
  if any(before.get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala bukan none')
  if any(before.get(k)!='action_module' for k in JOINTS):raise RuntimeError('Sendi badan bukan pada action_module')
  req=SetJointModule.Request();req.joint_name=JOINTS;req.module_name=['walking_module']*len(JOINTS)
  print('MEMULAI PEMETAAN KAKI DAN BAHU KE MODUL JALAN',flush=True);future=node.set_client.call_async(req);mapped=True
  spin_until(node,lambda:future.done(),8)
  if not future.result() or not future.result().result:raise RuntimeError('Pemetaan gagal')
  end=time.monotonic()+10
  while time.monotonic()<end:
   rclpy.spin_once(node,timeout_sec=.05)
   if node.violation:raise RuntimeError('Kepala menyimpang lebih dari dua count')
   if node.last is None or time.monotonic()-node.last>1:raise RuntimeError('Telemetry sendi terputus')
   if not preview_ready():raise RuntimeError('Preview berhenti')
  after=get_modules(node,(*HEAD,*JOINTS));report['modules_after']=after
  if any(after.get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala berubah')
  if any(after.get(k)!='walking_module' for k in JOINTS):raise RuntimeError('Modul kaki/bahu tidak sesuai')
  report['head_max_delta_rad']={k:max(abs(x['head'][k]-node.baseline[k]) for x in node.history) for k in HEAD};report['head_last_rad']=node.history[-1]['head'];report['status']='mapped_inspection_required'
 except BaseException as e:
  report['status']='failed';report['error']=str(e)
  if mapped:node.stop_pub.publish(String(data='stop'));report['stop_sent']=True;report['stop_limitation']='Stop may not interrupt a walking-init-pose transition.'
 finally:
  report['samples']=node.history;report['finished_utc']=datetime.now(timezone.utc).isoformat()
  with path.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
  print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));print('report='+str(path),flush=True)
  node.destroy_node();rclpy.shutdown()
 return 0 if report['status']=='mapped_inspection_required' else 1
if __name__=='__main__':raise SystemExit(main())
