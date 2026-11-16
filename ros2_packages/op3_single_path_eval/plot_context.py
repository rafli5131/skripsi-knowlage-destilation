"""Generate contextual OP3 path and CPU charts with study limitations."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'runs/op3_single_path_eval';DOC=ROOT/'dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3';d=json.loads((RUN/'20261116_analysis_01/comparison.json').read_text());N={'teacher_fp32':'Teacher','hybrid_full_seed1337':'KD Hybrid','supervised_seed1337':'Supervised','kd_seed42':'KD Murni'};vs=['tracking','no_tracking','cv_one_thread','no_gmc','openblas_one']
for lang in ('id','en'):
 fig,axes=plt.subplots(1,2,figsize=(12,5.5));x=np.arange(4);w=.34
 for j,(g,label) in enumerate([('t38_primary','T38'),('t43_combined','T43')]):
  vals=[d['models'][n][g]['variants']['predict_protocol']['ap']['overall']['mAP50-95'] for n in N];b=axes[0].bar(x+(j-.5)*w,vals,w,label=label);axes[0].bar_label(b,labels=[f'{v:.3f}' for v in vals],padding=3,fontsize=7)
 axes[0].set(title='mAP50–95 predict',ylabel='Nilai (0–1)' if lang=='id' else 'Score (0–1)',xticks=x,xticklabels=list(N.values()),ylim=(0,1.12));axes[0].tick_params(axis='x',rotation=15);axes[0].legend()
 for j,n in enumerate(['teacher_fp32','hybrid_full_seed1337']):
  vals=[json.loads((RUN/'20261116_runtime_01/replay_v2'/n/v/'summary.json').read_text())['cpu_ms_per_frame'] for v in vs];b=axes[1].bar(np.arange(5)+(j-.5)*w,vals,w,label=N[n]);axes[1].bar_label(b,labels=[f'{v:.0f}' for v in vals],padding=3,fontsize=7)
 axes[1].set(title='CPU replay 4/2 thread',ylabel='CPU ms/frame',xticks=np.arange(5),xticklabels=['Track','No track','CV=1','No GMC','BLAS=1']);axes[1].legend();fig.suptitle('Jalur inferensi dan diagnosis CPU' if lang=='id' else 'Inference paths and CPU diagnosis')
 fig.text(.5,.01,'T38 dan T43 berbeda adegan serta konvensi label; replay CPU offline bukan hasil live.' if lang=='id' else 'T38 and T43 differ in scene and label conventions; CPU replay is not live runtime.',ha='center',fontsize=9)
 fig.tight_layout(rect=(0,.06,1,.96));out=DOC/'grafik'/f'jalur_dan_cpu_konteks_{lang}.png';assert not out.exists();fig.savefig(out,dpi=300);plt.close(fig)
print('Contextual plots created')
