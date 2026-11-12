"""Map only leg joints to walking_module and monitor the head during stance transition."""
import json, math, time
from datetime import datetime, timezone
from pathlib import Path
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from robotis_controller_msgs.srv import GetJointModule, SetJointModule
from sensor_msgs.msg import JointState
from std_msgs.msg import String

LEGS=[f'{side}_{joint}' for side in ('l','r') for joint in ('hip_yaw','hip_roll','hip_pitch','knee','ank_pitch','ank_roll')]
HEAD=('head_pan','head_tilt')
LIMIT=2*math.pi/2048

class Monitor(Node):
 def __init__(self):
  super().__init__('op3_t43_walk_ready_monitor');self.last=None;self.history=[];self.baseline=None;self.violation=False
  self.create_subscription(JointState,'/robotis/present_joint_states',self.callback,qos_profile_sensor_data)
  self.get_client=self.create_client(GetJointModule,'/robotis/get_present_joint_ctrl_modules')
  self.set_client=self.create_client(SetJointModule,'/robotis/set_present_joint_ctrl_modules')
  self.stop_pub=self.create_publisher(String,'/robotis/walking/command',10)
 def callback(self,msg):
  d=dict(zip(msg.name,msg.position))
  if not all(k in d and math.isfinite(d[k]) for k in (*HEAD,*LEGS)):return
  now=time.monotonic();self.last=now;record={'utc':datetime.now(timezone.utc).isoformat(),'monotonic':now,'head':{k:d[k] for k in HEAD},'legs':{k:d[k] for k in LEGS}}
  self.history.append(record)
  if self.baseline and any(abs(d[k]-self.baseline[k])>LIMIT for k in HEAD):self.violation=True

def spin_until(node,predicate,timeout):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  rclpy.spin_once(node,timeout_sec=.05)
  if node.violation:raise RuntimeError('Kepala menyimpang lebih dari dua count')
  if predicate():return
 raise TimeoutError('Batas waktu telemetry atau service')

def get_modules(node,names):
 req=GetJointModule.Request();req.joint_name=list(names);future=node.get_client.call_async(req)
 spin_until(node,lambda:future.done(),5);res=future.result()
 if res is None:raise RuntimeError('Service modul tidak menghasilkan jawaban')
 return dict(zip(res.joint_name,res.module_name))

def main():
 out=Path('runs/op3_t43_walk_ready');out.mkdir(parents=True,exist_ok=True);path=out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 report={'started_utc':datetime.now(timezone.utc).isoformat(),'status':'starting','requested_joints':LEGS,'head_commanded':False,'walking_start_sent':False}
 rclpy.init();node=Monitor();mapped=False
 try:
  if not node.get_client.wait_for_service(timeout_sec=5) or not node.set_client.wait_for_service(timeout_sec=5):raise RuntimeError('Service controller tidak tersedia')
  spin_until(node,lambda:len(node.history)>=15,5)
  node.baseline=dict(node.history[-1]['head']);report['head_baseline_rad']=node.baseline
  before=get_modules(node,(*HEAD,*LEGS));report['modules_before']=before
  if any(before.get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala bukan none')
  if any(before.get(k)!='none' for k in LEGS):raise RuntimeError('Modul kaki tidak dalam kondisi awal none')
  req=SetJointModule.Request();req.joint_name=LEGS;req.module_name=['walking_module']*len(LEGS)
  print('MEMULAI TRANSISI WALK-READY KAKI',flush=True);future=node.set_client.call_async(req);mapped=True
  spin_until(node,lambda:future.done(),8)
  if not future.result() or not future.result().result:raise RuntimeError('Pemetaan modul kaki gagal')
  end=time.monotonic()+10
  while time.monotonic()<end:
   rclpy.spin_once(node,timeout_sec=.05)
   if node.violation:raise RuntimeError('Kepala menyimpang lebih dari dua count')
   if node.last is None or time.monotonic()-node.last>1:raise RuntimeError('Telemetry sendi terputus')
  after=get_modules(node,(*HEAD,*LEGS));report['modules_after']=after
  if any(after.get(k)!='none' for k in HEAD):raise RuntimeError('Modul kepala berubah')
  if any(after.get(k)!='walking_module' for k in LEGS):raise RuntimeError('Tidak semua kaki berhasil dipetakan')
  recent=node.history[-min(len(node.history),125):]
  report['recent_leg_range_rad']={k:max(x['legs'][k] for x in recent)-min(x['legs'][k] for x in recent) for k in LEGS}
  report['head_max_delta_rad']={k:max(abs(x['head'][k]-node.baseline[k]) for x in node.history if x['monotonic']>=node.history[0]['monotonic']) for k in HEAD}
  report['status']='mapped_inspection_required'
 except BaseException as e:
  report['status']='failed';report['error']=str(e)
  if mapped:
   node.stop_pub.publish(String(data='stop'));report['stop_sent']=True
   report['stop_limitation']='Stop walking may not interrupt an ongoing walking-init-pose transition; operator must support robot.'
 finally:
  report['samples']=node.history;report['finished_utc']=datetime.now(timezone.utc).isoformat()
  with path.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
  print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));print('report='+str(path),flush=True)
  node.destroy_node();rclpy.shutdown()
 return 0 if report['status']=='mapped_inspection_required' else 1

if __name__=='__main__':raise SystemExit(main())
