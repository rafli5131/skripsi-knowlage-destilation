import io, json, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
import op3_t43_walk_capture.__main__ as g

class Publisher:
 def __init__(self):self.calls=0
 def get_subscription_count(self):
  self.calls+=1
  return 0 if self.calls<3 else 1
class Node:
 instance=None
 def __init__(self,*args):
  Node.instance=self;self.commands=[];self.last_joint_monotonic=time.monotonic();self.head_violation=False;self.ack_utc=None;self.stop_ack_utc=None;self.publisher=Publisher();self.max_head_delta=0;self.sample_stream=io.StringIO()
 def command(self,s):self.commands.append(s)
 def destroy_node(self):pass

class Safety(unittest.TestCase):
 def run_case(self, alive, violate):
  with tempfile.TemporaryDirectory() as t:
   d=Path(t);preview=d/'preview.csv';preview.write_text('test')
   argv=['test','--session-id','abc123','--out-dir',str(d/'out'),'--baseline-pan','0','--baseline-tilt','0','--preview-csv',str(preview),'--viewer-pid','1']
   def spin(node,timeout_sec):
    if violate and 'start' in node.commands:node.head_violation=True
   with patch.object(g,'ROOT',d),patch.object(g,'Guard',Node),patch.object(g,'alive',return_value=alive),patch.object(g.rclpy,'init'),patch.object(g.rclpy,'shutdown'),patch.object(g.rclpy,'spin_once',side_effect=spin),patch.object(sys,'argv',argv),patch.object(g.subprocess,'Popen') as capture:
    result=g.main()
   report=json.loads((d/'out/gait_guard.json').read_text());self.assertEqual(result,1);self.assertEqual(report['status'],'failed');capture.assert_not_called()
   return Node.instance.commands
 def test_preview_missing_prevents_start(self):self.assertEqual(self.run_case(False,False),[])
 def test_head_violation_after_start_sends_stop(self):
  commands=self.run_case(True,True);self.assertEqual(commands[0],'start');self.assertIn('stop',commands);self.assertGreaterEqual(Node.instance.publisher.calls,3)
if __name__=='__main__':unittest.main()
