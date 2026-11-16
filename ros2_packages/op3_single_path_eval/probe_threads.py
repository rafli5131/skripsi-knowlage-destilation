"""Probe OpenBLAS and CPU backend thread settings using isolated processes."""
import json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'runs/op3_single_path_eval/20261116_runtime_01/thread_probe.json'
CHILD=r'''
import cv2,psutil,torch,ultralytics,yaml
import numpy as np,ctypes,glob,json,os
from pathlib import Path
from ultralytics.utils.torch_utils import select_device
p=glob.glob(str(Path(np.__file__).resolve().parents[1]/'numpy.libs/libopenblas64_p-*.so'))[0];lib=ctypes.CDLL(p);f=lib.openblas_get_num_threads64_;f.restype=ctypes.c_int
torch.set_num_threads(4);before=torch.get_num_threads();select_device('cpu',verbose=False);after=torch.get_num_threads()
print(json.dumps({'openblas_num_threads':f(),'opencv_num_threads':cv2.getNumThreads(),'torch_before_select_device':before,'torch_after_select_device':after,'openblas_env':os.getenv('OPENBLAS_NUM_THREADS'),'omp_env':os.getenv('OMP_NUM_THREADS')}))
'''
def main():
 res={}
 for label in ('default','blas_one'):
  env=os.environ.copy();env.pop('OPENBLAS_NUM_THREADS',None);env.pop('OMP_NUM_THREADS',None)
  if label=='blas_one':env['OPENBLAS_NUM_THREADS']='1'
  p=subprocess.run([sys.executable,'-c',CHILD],env=env,capture_output=True,text=True,check=True);res[label]=json.loads(p.stdout.strip().splitlines()[-1])
 if res['default']['openblas_num_threads']!=16 or res['blas_one']['openblas_num_threads']!=1:raise ValueError(f'Unexpected environment: {res}')
 with OUT.open('x') as f:json.dump({'created_utc':datetime.now(timezone.utc).isoformat(),'method':'separate processes, same core import order as node; no camera or model loaded','results':res},f,indent=2);f.write('\n')
 print(json.dumps(res))
if __name__=='__main__':main()
