"""Execute OP3 action page 9 on body joints only while monitoring head."""
from __future__ import annotations
import hashlib,json,math,os,struct,time
from datetime import datetime,timezone
from pathlib import Path
import rclpy
from robotis_controller_msgs.msg import StatusMsg
from robotis_controller_msgs.srv import SetJointModule
from op3_action_module_msgs.msg import StartAction
from std_msgs.msg import String
from op3_t43_walk_ready.__main__ import Monitor,spin_until,get_modules,HEAD,LEGS

BODY=['r_sho_pitch','l_sho_pitch','r_sho_roll','l_sho_roll','r_el','l_el','r_hip_yaw','l_hip_yaw','r_hip_roll','l_hip_roll','r_hip_pitch','l_hip_pitch','r_knee','l_knee','r_ank_pitch','l_ank_pitch','r_ank_roll','l_ank_roll']
MOTION=Path('/home/humanoid/ros2_jazzy/install/op3_action_module/share/op3_action_module/data/motion_4095.bin')
PREVIEW=Path('/tmp/op3-t43-preview-ziwkQm/hybrid_preview.csv');VIEWER_PID=23446

class ActionMonitor(Monitor):
 def __init__(self):
  super().__init__();self.statuses=[];self.done=None
  self.create_subscription(StatusMsg,'/robotis/status',self.status_cb,10)
  self.create_subscription(String,'/robotis/movement_done',self.done_cb,10)
  self.action_pub=self.create_publisher(StartAction,'/robotis/action/start_action',10)
 def status_cb(self,msg):self.statuses.append({'module':msg.module_name,'message':msg.status_msg,'utc':datetime.now(timezone.utc).isoformat()})
 def done_cb(self,msg):self.done=msg.data

def preview_ready():
 try:
  os.kill(VIEWER_PID,0)
  return Path(f'/proc/{VIEWER_PID}/stat').read_text().split()[2]!='Z' and time.time()-PREVIEW.stat().st_mtime<5
 except (OSError,IndexError):return False

def main():
 out=Path('runs/op3_t43_action_ready');out.mkdir(parents=True,exist_ok=True);path=out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 report={'started_utc':datetime.now(timezone.utc).isoformat(),'status':'starting','page':9,'body_joints':BODY,'head_mapped':False,'head_action_requested':False,'walking_start_sent':False}
 rclpy.init();node=ActionMonitor();action_sent=False
 try:
  raw=MOTION.read_bytes();page=raw[9*512:10*512]
  if len(page)!=512 or page[:14].split(b'\0')[0]!=b'walkready' or sum(page)%256!=255 or page[20]!=1:raise RuntimeError('Page 9 bukan walkready yang tervalidasi')
  steps=struct.unpack('<31HBB',page[64:128]);report['motion_file_sha256']=hashlib.sha256(raw).hexdigest();report['page_body_values']=list(steps[1:19]);report['page_head_values_not_used']=list(steps[19:21])
  if not preview_ready():raise RuntimeError('Preview kamera tidak aktif')
  if not node.get_client.wait_for_service(timeout_sec=5) or not node.set_client.wait_for_service(timeout_sec=5):raise RuntimeError('Service controller tidak tersedia')
  spin_until(node,lambda:len(node.history)>=15,5);node.baseline=dict(node.history[-1]['head']);report['head_baseline_rad']=node.baseline
  before=get_modules(node,(*HEAD,*BODY));report['modules_before']=before
  if any(before.get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala bukan none')
  req=SetJointModule.Request();req.joint_name=BODY;req.module_name=['action_module']*len(BODY)
  future=node.set_client.call_async(req);spin_until(node,lambda:future.done(),8)
  if not future.result() or not future.result().result:raise RuntimeError('Permintaan pemetaan body gagal')
  deadline=time.monotonic()+8
  while True:
   modules=get_modules(node,(*HEAD,*BODY))
   if any(modules.get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala berubah')
   if all(modules.get(k)=='action_module' for k in BODY):break
   if time.monotonic()>deadline:raise RuntimeError('Pemetaan body action belum selesai')
   rclpy.spin_once(node,timeout_sec=.05)
  report['modules_before_action']=modules
  if not preview_ready() or node.last is None or time.monotonic()-node.last>1:raise RuntimeError('Preview atau telemetry tidak aktif')
  if node.action_pub.get_subscription_count()<1:raise RuntimeError('Action subscriber tidak ada')
  cmd=StartAction();cmd.page_num=9;cmd.joint_name_array=BODY;node.action_pub.publish(cmd);action_sent=True;report['action_command_utc']=datetime.now(timezone.utc).isoformat();print('MEMULAI ACTION WALKREADY BODY-ONLY',flush=True)
  deadline=time.monotonic()+20
  while node.done is None and time.monotonic()<deadline:
   rclpy.spin_once(node,timeout_sec=.05)
   if node.violation:raise RuntimeError('Kepala menyimpang lebih dari dua count')
   if node.last is None or time.monotonic()-node.last>1:raise RuntimeError('Telemetry sendi terputus')
   if not preview_ready():raise RuntimeError('Preview tidak aktif')
  if node.done!='action':raise RuntimeError('Action tidak selesai dengan bukti sukses: '+str(node.done))
  report['action_done']=node.done
  end=time.monotonic()+2
  while time.monotonic()<end:
   rclpy.spin_once(node,timeout_sec=.05)
   if node.violation:raise RuntimeError('Kepala menyimpang setelah action')
  report['modules_after']=get_modules(node,(*HEAD,*BODY))
  if any(report['modules_after'].get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala berubah sesudah action')
  report['head_max_delta_rad']={k:max(abs(x['head'][k]-node.baseline[k]) for x in node.history) for k in HEAD};report['status']='action_completed_operator_inspection_required'
 except BaseException as e:
  report['status']='failed';report['error']=f'{type(e).__name__}: {e}'
  if action_sent:
   brake=StartAction();brake.page_num=-2;brake.joint_name_array=[];node.action_pub.publish(brake);report['brake_sent']=True
 finally:
  report['statuses']=node.statuses;report['samples']=node.history;report['finished_utc']=datetime.now(timezone.utc).isoformat()
  with path.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
  print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));print('report='+str(path),flush=True)
  node.destroy_node();rclpy.shutdown()
 return 0 if report['status']=='action_completed_operator_inspection_required' else 1

if __name__=='__main__':raise SystemExit(main())
