"""Create descriptive T43 plots and confusion matrices from stored predictions."""
import csv,json,sys
from pathlib import Path
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'ros2_packages/op3_camera_eval'))
from op3_camera_eval.evaluate import read_labels, iou_xyxy
OUT=ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260'
DOC=ROOT/'dokumentasi/2026-11-12/percobaan-39-evaluasi-t43'
NAMES={'teacher_fp32':'Teacher YOLO11n','hybrid_full_seed1337':'KD Hybrid','supervised_seed1337':'Supervised','kd_seed42':'KD Murni'}
COLORS=['#457b9d','#e76f51','#2a9d8f','#9b5de5']

def confusion(name,manifest):
    m=np.zeros((4,4),dtype=int)
    for line in (OUT/f'per_frame_{name}.jsonl').read_text().splitlines():
        item=json.loads(line); f=manifest['frames'][item['key']]
        gt=read_labels(Path(f['label'])); det=item['detections']; cand=[]
        for i,(cls,x,y,w,h) in enumerate(gt):
            box=[(x-w/2)*640,(y-h/2)*480,(x+w/2)*640,(y+h/2)*480]
            for j,d in enumerate(det):
                overlap=iou_xyxy(box,d['xyxy'])
                if overlap>=.5: cand.append((overlap,i,j))
        usedg=set(); usedd=set()
        for overlap,i,j in sorted(cand,reverse=True):
            if i not in usedg and j not in usedd:
                usedg.add(i); usedd.add(j); m[det[j]['class_id'],gt[i][0]]+=1
        for i,g in enumerate(gt):
            if i not in usedg: m[3,g[0]]+=1
        for j,d in enumerate(det):
            if j not in usedd: m[d['class_id'],3]+=1
    return m

def plot_matrix(ax,m,lang,title):
    classes=['Bola','Gawang','Robot','Latar'] if lang=='id' else ['Ball','Goal','Robot','Background']
    ax.imshow(m,cmap='Blues',vmin=0,vmax=max(1,m.max()))
    for (i,j),n in np.ndenumerate(m): ax.text(j,i,str(n),ha='center',va='center',color='white' if n>m.max()/2 else '#1d3557',fontsize=9)
    ax.set(xticks=range(4),yticks=range(4),xticklabels=classes,yticklabels=classes,title=title,xlabel='Label manual' if lang=='id' else 'Manual label',ylabel='Prediksi model' if lang=='id' else 'Model prediction')
    ax.tick_params(axis='x',rotation=15)

def main():
    report=json.loads((OUT/'results.json').read_text()); assert report['status']=='complete'
    manifest=json.loads((OUT/'input_manifest.json').read_text()); DOC.mkdir(parents=True,exist_ok=True)
    (DOC/'grafik').mkdir(exist_ok=True);(DOC/'confusion_matrix').mkdir(exist_ok=True)
    matrices={k:confusion(k,manifest) for k in report['models']}
    (DOC/'confusion_matrix'/'counts.json').write_text(json.dumps({'axes':'rows predicted, columns manual; background = no match','conf_gt':'> 0.25','match_iou':'>= 0.5','matching':'greedy descending IoU, class agnostic','matrices':{k:v.tolist() for k,v in matrices.items()}},indent=2)+'\n')
    for lang in ('id','en'):
        for name,m in matrices.items():
            fig,ax=plt.subplots(figsize=(7,6)); plot_matrix(ax,m,lang,NAMES[name]);fig.tight_layout();fig.savefig(DOC/'confusion_matrix'/f'{name}_{lang}.png',dpi=300);plt.close(fig)
        fig,axes=plt.subplots(2,2,figsize=(12,10));
        for ax,(name,m) in zip(axes.flat,matrices.items()): plot_matrix(ax,m,lang,NAMES[name])
        fig.suptitle('Matriks kebingungan — 260 frame' if lang=='id' else 'Confusion matrices — 260 frames',fontsize=16);fig.tight_layout();fig.savefig(DOC/'confusion_matrix'/f'empat_model_{lang}.png',dpi=300);plt.close(fig)
        names=list(report['models']); x=np.arange(4); width=.23
        fig,axes=plt.subplots(1,2,figsize=(12,5))
        for ax,key in zip(axes,['mAP50','mAP50-95']):
            for j,split in enumerate(['idle','walking','combined']):
                vals=[report['models'][n]['splits'][split]['ap'][key] for n in names]
                bars=ax.bar(x+(j-1)*width,vals,width,label=({'idle':'Diam','walking':'Berjalan','combined':'Gabungan'} if lang=='id' else {'idle':'Idle','walking':'Walking','combined':'Combined'})[split])
                ax.bar_label(bars,labels=[f'{v:.3f}' for v in vals],rotation=90,padding=3,fontsize=7)
            ax.set_xticks(x,[NAMES[n] for n in names],rotation=15,ha='right');ax.set_ylim(0,1.15);ax.set_ylabel('Nilai (0–1)' if lang=='id' else 'Score (0–1)');ax.set_title(key);ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8)
        fig.suptitle('Perbandingan mAP empat model — T43' if lang=='id' else 'Four-model mAP comparison — T43');fig.tight_layout();fig.savefig(DOC/'grafik'/f'perbandingan_map_{lang}.png',dpi=300);plt.close(fig)
        for name in names:
            metrics=['precision','recall','F1_harmonic_macro_precision_recall']; title=['Precision','Recall','F1']
            vals=[report['models'][name]['splits']['combined']['operating']['macro'][k] for k in metrics]
            fig,ax=plt.subplots(figsize=(7,4.5)); bars=ax.bar(title,vals,color=[COLORS[0],COLORS[1],COLORS[2]]);ax.bar_label(bars,labels=[f'{x:.3f}' for x in vals],padding=4);ax.set_ylim(0,1.12);ax.set_ylabel('Nilai makro (0–1)' if lang=='id' else 'Macro score (0–1)');ax.set_title(NAMES[name]+' — '+('gabungan 260 frame' if lang=='id' else 'combined 260 frames'));ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(DOC/'grafik'/f'{name}_precision_recall_f1_{lang}.png',dpi=300);plt.close(fig)
    print(DOC)
if __name__=='__main__':main()
