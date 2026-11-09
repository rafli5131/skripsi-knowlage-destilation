#!/usr/bin/env python3
"""Visualisasi skripsi dari tabel/telemetry yang tersedia; keluaran ke folder baru."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'analisis_performa/tabel'
AUDIT = ROOT / 'dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/audit_telemetry.csv'
MODELS = ['teacher', 'hybrid1337', 'sup1337', 'kd42']
DISPLAY = {'teacher': 'Teacher YOLO11n', 'hybrid1337': 'KD Hybrid', 'sup1337': 'Supervised', 'kd42': 'KD Murni'}
SHORT = {'teacher': 'Teacher', 'hybrid1337': 'Hybrid', 'sup1337': 'Supervised', 'kd42': 'KD Murni'}
COLORS = {'teacher': '#31599B', 'hybrid1337': '#009C83', 'sup1337': '#E19A35', 'kd42': '#C85B67'}
T38 = {'teacher': 'teacher_fp32', 'hybrid1337': 'hybrid_full_seed1337', 'sup1337': 'supervised_seed1337', 'kd42': 'kd_seed42'}
LANGS = ('id', 'en')


def read(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def tr(lang, a, b):
    return a if lang == 'id' else b


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def init_style():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 13,
                         'axes.titleweight': 'bold', 'axes.labelsize': 10, 'figure.facecolor': 'white',
                         'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True,
                         'grid.alpha': .18, 'axes.axisbelow': True, 'savefig.facecolor': 'white'})


def header(fig, title, subtitle):
    fig.suptitle(title, x=.06, y=.98, ha='left', fontsize=17, fontweight='bold', color='#12233C')
    fig.text(.06, .934, subtitle, ha='left', va='top', fontsize=10, color='#51637A')
    fig.subplots_adjust(left=.08, right=.97, bottom=.15, top=.86, hspace=.47, wspace=.28)


def foot(fig, msg):
    fig.text(.06, .035, msg, fontsize=8.8, color='#506175', va='bottom', wrap=True)


def save(fig, out, stem, lang):
    fig.savefig(out / f'{stem}_{lang}.png', dpi=200)
    plt.close(fig)


def plot_test(out, lang, test, paired):
    fig, ax = plt.subplots(figsize=(12, 7.5))
    metrics = ['mAP50', 'mAP50-95', 'precision', 'recall', 'F1']
    x = np.arange(len(metrics)); w = .19
    for i, model in enumerate(MODELS):
        vals = [test[model][key] * 100 for key in metrics]
        bars = ax.bar(x + (i - 1.5) * w, vals, width=w, color=COLORS[model], label=SHORT[model])
        ax.bar_label(bars, labels=[f'{v:.1f}' for v in vals], padding=2, fontsize=7.7, rotation=90)
    ax.set_xticks(x, ['mAP50', 'mAP50–95', 'Precision', 'Recall', 'F1'])
    ax.set_ylim(0, 112); ax.set_ylabel(tr(lang, 'Nilai (%) · lebih tinggi lebih baik', 'Score (%) · higher is better'))
    ax.legend(ncol=4, loc='upper center', frameon=False)
    header(fig, tr(lang, 'Hasil akurasi pada dataset TEST', 'Accuracy on the TEST dataset'),
           tr(lang, 'Empat model · 592 gambar · batang menunjukkan nilai rata-rata', 'Four models · 592 images · bars show mean scores'))
    foot(fig, tr(lang, 'Teacher: 1 checkpoint; student: rerata 3 seed. F1 dihitung dari precision dan recall makro. TEST pernah digunakan sebelumnya.',
                 'Teacher: one checkpoint; students: mean of 3 seeds. F1 is calculated from macro precision and recall. TEST was used previously.'))
    save(fig, out, '01_test_empat_model', lang)

    fig, axes = plt.subplots(1, 2, figsize=(12, 7.5))
    for ax, metric, title in zip(axes, ['mAP50-95', 'F1'], ['mAP50–95', 'F1']):
        points = [r for r in paired if r['row_type'] == 'seed' and r['metric'] == metric]
        vals = [100 * float(r['delta_hybrid_minus_supervised']) for r in points]
        seeds = [r['seed'] for r in points]; y = np.arange(3)
        ax.axvline(0, color='#455568', linewidth=1.4)
        ax.barh(y, vals, color=[COLORS['hybrid1337'] if v >= 0 else COLORS['sup1337'] for v in vals], height=.5)
        ax.set_yticks(y, [f'Seed {s}' for s in seeds]); ax.invert_yaxis()
        for yy, value in zip(y, vals):
            ax.annotate(f'{value:+.2f} pp', (value, yy), xytext=(5 if value >= 0 else -5, 0),
                        textcoords='offset points', ha='left' if value >= 0 else 'right', va='center', fontsize=10)
        max_abs = max(abs(v) for v in vals) * 1.5
        ax.set_xlim(-max_abs, max_abs); ax.set_title(title)
        ax.set_xlabel(tr(lang, 'Selisih Hybrid − Supervised (poin persentase)', 'Hybrid − Supervised (percentage points)'))
    header(fig, tr(lang, 'Perbedaan kecil: Hybrid dibanding Supervised', 'Small differences: Hybrid compared with Supervised'),
           tr(lang, 'Setiap batang adalah satu pasangan seed pada TEST · nol berarti sama', 'Each bar is a matched seed on TEST · zero means equal'))
    foot(fig, tr(lang, 'Skala tiap panel berbeda untuk memperjelas selisih. Nilai positif mendukung Hybrid; negatif mendukung Supervised. Bukan uji signifikansi.',
                 'Each panel uses a different scale to make differences readable. Positive favors Hybrid; negative favors Supervised. Not a significance test.'))
    save(fig, out, '02_selisih_test_hybrid_supervised', lang)


def plot_op3(out, lang, camera):
    fig, axes = plt.subplots(1, 2, figsize=(12, 7.5))
    for i, (key, title) in enumerate([('mAP50-95', 'mAP50–95'), ('F1', tr(lang, 'F1 makro', 'Macro F1'))]):
        ax = axes[i]; vals = [float(camera[(m, 'macro')][key]) * 100 for m in MODELS]
        bars = ax.barh(np.arange(4), vals, color=[COLORS[m] for m in MODELS], height=.65)
        ax.set_yticks(np.arange(4), [SHORT[m] for m in MODELS]); ax.invert_yaxis(); ax.set_xlim(0, 112)
        ax.bar_label(bars, labels=[f'{v:.1f}%' for v in vals], padding=5, fontsize=10)
        ax.set_xlabel(tr(lang, 'Nilai (%) · lebih tinggi lebih baik', 'Score (%) · higher is better')); ax.set_title(title)
    header(fig, tr(lang, 'Akurasi kamera OP3 pada frame yang sama', 'OP3 camera accuracy on the same frames'),
           tr(lang, '260 frame: 200 berobjek + 60 tanpa target · evaluasi offline', '260 frames: 200 with targets + 60 without · offline evaluation'))
    foot(fig, tr(lang, 'T38: 1 checkpoint per model. F1 = rata-rata F1 per kelas. Data satu rangkaian; label awal dibantu model lalu ditinjau.',
                 'T38: one checkpoint per model. F1 = mean per-class F1. Single capture series; labels were model-assisted then reviewed.'))
    save(fig, out, '03_akurasi_kamera_op3', lang)

    fig, axes = plt.subplots(1, 2, figsize=(12, 7.5))
    x = np.arange(3); w = .2
    for i, m in enumerate(MODELS):
        vals = [float(camera[(m, k)]['recall']) * 100 for k in ('ball', 'gawang', 'robot')]
        bars = axes[0].bar(x+(i-1.5)*w, vals, w, label=SHORT[m], color=COLORS[m])
        axes[0].bar_label(bars, labels=[f'{v:.1f}' for v in vals], padding=2, fontsize=7, rotation=90)
    axes[0].set_xticks(x, [tr(lang,'Bola','Ball'), tr(lang,'Gawang','Goal'), 'Robot']); axes[0].set_ylim(0,120)
    axes[0].set_ylabel(tr(lang,'Recall per kelas (%)','Recall by class (%)')); axes[0].set_title(tr(lang,'Target yang berhasil ditemukan','Targets found'))
    vals=[int(camera[(m,'macro')]['negative_fp_frames']) for m in MODELS]
    bars=axes[1].barh(np.arange(4),vals,color=[COLORS[m] for m in MODELS],height=.6)
    axes[1].set_yticks(np.arange(4),[SHORT[m] for m in MODELS]); axes[1].invert_yaxis(); axes[1].set_xlim(0,60)
    axes[1].bar_label(bars,labels=[f'{v}/60' for v in vals],padding=4)
    axes[1].set_xlabel(tr(lang,'Frame tanpa target yang menghasilkan deteksi salah','Target-free frames containing a false detection'))
    axes[1].set_title(tr(lang,'Alarm palsu pada 60 frame kosong','False alarms on 60 empty frames'))
    axes[0].legend(ncol=2,fontsize=8,frameon=False,loc='upper right')
    header(fig, tr(lang,'Deteksi tiap objek dan alarm palsu','Per-object detection and false alarms'),
           tr(lang,'T38 · confidence > 0,25 dan pencocokan IoU ≥ 0,5','T38 · confidence > 0.25 and matching IoU ≥ 0.5'))
    foot(fig,tr(lang,'Satu rangkaian kamera; ground truth ditinjau dengan bantuan pra-label. Frame kosong dengan FP bukan jumlah total kotak salah.',
                'Single camera series; ground truth was reviewed after assisted pre-labeling. Frames with FP are not the total number of false boxes.'))
    save(fig,out,'04_kelas_dan_alarm_palsu',lang)


def plot_runtime(out, lang, runs):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    metrics = [('latency_mean_ms',tr(lang,'Latensi (ms) ↓','Latency (ms) ↓')),
               ('fps',tr(lang,'Kecepatan (frame/detik) ↑','Throughput (frames/second) ↑')),
               ('cpu_percent_16_cores',tr(lang,'CPU proses (% dari 16 CPU logis)','Process CPU (% of 16 logical CPUs)')),
               ('rss_mib',tr(lang,'RAM proses (MiB)','Process memory RSS (MiB)'))]
    for ax,(key,label) in zip(axes.flat,metrics):
        for i,m in enumerate(MODELS):
            for j,cond in enumerate(('idle','walk')):
                vals=[float(r[key]) for r in runs if r['model']==m and r['condition']==cond]
                x=i + (-.19 if j==0 else .19); mean=np.mean(vals)
                ax.bar(x,mean,width=.32,color=COLORS[m],alpha=1 if j==0 else .45,edgecolor=COLORS[m],hatch=None if j==0 else '//')
                ax.scatter([x-.055,x,x+.055],vals,marker='o',s=13,color='#1C2A3A',zorder=3)
                ax.annotate(f'{mean:.1f}', (x, max(max(vals),mean)), xytext=(0,4), textcoords='offset points',
                            ha='center',va='bottom',fontsize=7.4,rotation=90)
        ax.set_xticks(range(4),[SHORT[m] for m in MODELS],fontsize=8); ax.set_ylabel(label)
        ax.set_ylim(0,ax.get_ylim()[1]*1.25)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor='#607D8B',label=tr(lang,'Diam (idle)','Idle')),
                        Patch(facecolor='#B0BEC5',hatch='//',edgecolor='#607D8B',label=tr(lang,'Berjalan','Walking'))],
               loc='lower center',bbox_to_anchor=(.5,.085),ncol=2,frameon=False)
    header(fig,tr(lang,'Perbandingan kinerja di robot OP3','Performance comparison on the OP3 robot'),
           tr(lang,'Tiap batang: rata-rata 3 run · titik: masing-masing run','Each bar: mean of 3 runs · dots: individual runs'))
    foot(fig,tr(lang,'CPU dan RAM hanya proses detektor. FPS tidak sama dengan 1000/latensi. Run lintas hari; hasil deskriptif.',
                'CPU and RAM cover the detector process only. FPS is not 1000/latency. Runs span different days; descriptive results.'))
    save(fig,out,'05_runtime_empat_model_idle_berjalan',lang)


def plot_t42(out,lang,rows):
    fig,axes=plt.subplots(1,2,figsize=(12,7.5)); x=np.arange(3); seeds=[42,1337,2025]
    for teacher,color,label in [('yolo11n','#31599B','YOLO11n'),('yolo11s','#C85B67','YOLO11s')]:
        vals=[100*float(next(r for r in rows if r['teacher_variant']==teacher and int(r['student_seed'])==s)['student_map50_95']) for s in seeds]
        axes[0].plot(x,vals,marker='o',linewidth=2.4,color=color,label=label)
        for xx,v in zip(x,vals): axes[0].annotate(f'{v:.3f}',(xx,v),xytext=(0,9 if teacher=='yolo11n' else -15),textcoords='offset points',ha='center',fontsize=9)
    axes[0].set_xticks(x,[str(s) for s in seeds]); axes[0].set_xlabel('Seed'); axes[0].set_ylabel('mAP50–95 (%)')
    axes[0].set_title(tr(lang,'Student: nilai per seed (skala diperbesar)','Student: scores by seed (zoomed scale)')); axes[0].legend(title='Teacher',frameon=False)
    vals=[]
    for s in seeds:
        a=float(next(r for r in rows if r['teacher_variant']=='yolo11n' and int(r['student_seed'])==s)['student_map50_95'])
        b=float(next(r for r in rows if r['teacher_variant']=='yolo11s' and int(r['student_seed'])==s)['student_map50_95'])
        vals.append((b-a)*100)
    axes[1].axhline(0,color='#425466',linewidth=1.4); bars=axes[1].bar(x,vals,color='#C85B67',width=.55)
    for rect,val in zip(bars,vals): axes[1].text(rect.get_x()+rect.get_width()/2,val-.012,f'{val:+.3f} pp',ha='center',va='top',fontsize=10)
    axes[1].set_xticks(x,[str(s) for s in seeds]); axes[1].set_xlabel('Seed')
    axes[1].set_ylabel(tr(lang,'Selisih mAP (poin persentase)','mAP difference (percentage points)'))
    axes[1].set_title(tr(lang,'Selisih student: teacher s − n','Student difference: teacher s − n'))
    axes[1].set_ylim(min(vals)*1.65,max(.02,max(vals)*-.35))
    header(fig,tr(lang,'Ablasi teacher: perbedaan yang sangat kecil','Teacher ablation: very small differences'),
           tr(lang,'T42 · VAL 1.213 gambar · hasil tiga seed berpasangan','T42 · VAL 1,213 images · three matched seeds'))
    foot(fig,tr(lang,'Grafik kiri memakai skala terpotong dan diperbesar. Teacher masing-masing satu checkpoint; selisih kecil bukan bukti signifikansi.',
                'Left chart uses a zoomed, truncated axis. One checkpoint per teacher; small differences are not evidence of significance.'))
    save(fig,out,'06_ablasi_teacher_T42',lang)


def plot_training(out,lang,rows):
    fig,ax=plt.subplots(figsize=(12,7.5)); seeds=[42,1337,2025]; x=np.arange(3); w=.23
    for i,(prefix,model) in enumerate([('hybrid_full','hybrid1337'),('supervised','sup1337'),('kd','kd42')]):
        vals=[float(next(r for r in rows if r['phase']=='training' and r['model_or_group']==f'{prefix}_seed{s}')['duration_seconds'])/3600 for s in seeds]
        bars=ax.bar(x+(i-1)*w,vals,width=w,label=SHORT[model],color=COLORS[model]); ax.bar_label(bars,labels=[f'{v:.2f}' for v in vals],padding=4)
    ax.set_xticks(x,[str(s) for s in seeds]); ax.set_xlabel('Seed'); ax.set_ylabel(tr(lang,'Waktu training (jam)','Training time (hours)')); ax.set_ylim(0,7)
    ax.legend(ncol=3,frameon=False,loc='upper right')
    header(fig,tr(lang,'Waktu pelatihan student','Student training time'),tr(lang,'Sembilan run student · dicatat pada server bersama','Nine student runs · recorded on a shared server'))
    foot(fig,tr(lang,'T35: beban server dan periode dapat berbeda. Supervised seed 1337 dijumlah dari dua segmen, tanpa jeda interupsi.',
                'T35: server load and experiment periods may differ. Supervised seed 1337 combines two segments, excluding interruption.'))
    save(fig,out,'07_waktu_training_student',lang)


def plot_individual(out,lang,model,runs,camera):
    fig,axes=plt.subplots(2,2,figsize=(12,8.5)); labels=[tr(lang,'Bola','Ball'),tr(lang,'Gawang','Goal'),'Robot']
    for i,(key,title) in enumerate([('precision','Precision'),('recall','Recall')]):
        vals=[float(camera[(model,k)][key])*100 for k in ('ball','gawang','robot')]
        bars=axes.flat[i].bar(labels,vals,color=COLORS[model],width=.55); axes.flat[i].bar_label(bars,labels=[f'{v:.1f}%' for v in vals],padding=4)
        axes.flat[i].set_ylim(0,115); axes.flat[i].set_title(f'{title} · OP3 T38'); axes.flat[i].set_ylabel(tr(lang,'Nilai (%)','Score (%)'))
    for ax,key,title in [(axes.flat[2],'latency_mean_ms',tr(lang,'Latensi tiap run (ms)','Latency per run (ms)')),
                         (axes.flat[3],'fps',tr(lang,'FPS tiap run','FPS per run'))]:
        for cond,marker,color in [('idle','o','#007F72'),('walk','s','#C97417')]:
            vals=[float(next(r for r in runs if r['model']==model and r['condition']==cond and r['ulangan']==str(i))[key]) for i in (1,2,3)]
            ax.plot([1,2,3],vals,marker=marker,color=color,linewidth=2,label=tr(lang,'Diam','Idle') if cond=='idle' else tr(lang,'Berjalan','Walking'))
            for x,y in zip([1,2,3],vals):
                ax.annotate(f'{y:.2f}',(x,y),xytext=(8 if cond=='idle' else -8,9 if cond=='idle' else -12),
                            textcoords='offset points',ha='left' if cond=='idle' else 'right',fontsize=8)
        ax.margins(x=.16, y=.25)
        ax.set_xticks([1,2,3]); ax.set_xlabel(tr(lang,'Ulangan','Run')); ax.set_ylabel(title); ax.set_title(title + tr(lang,' · skala diperbesar',' · zoomed scale'))
        ax.legend(frameon=False,fontsize=8)
    header(fig,f'{DISPLAY[model]} — '+tr(lang,'hasil per model','individual results'),
           tr(lang,'Atas: 260 frame OP3 · bawah: tiga ulangan per kondisi','Top: 260 OP3 frames · bottom: three runs per condition'))
    foot(fig,tr(lang,'Panel bawah memakai sumbu terpotong agar beda kecil terbaca. T38: precision/recall pada confidence >0,25, IoU ≥0,5.',
                'Bottom panels use truncated axes to show small differences. T38: precision/recall at confidence >0.25, IoU ≥0.5.'))
    save(fig,out,f'08_ringkasan_{model}',lang)


def bins(path):
    rows=read(path); grouped=defaultdict(list); first=None
    for r in rows:
        if r.get('error'): continue
        t=datetime.fromisoformat(r['receive_time_utc'].replace('Z','+00:00')).timestamp()
        if first is None: first=t
        b=int((t-first)//2)
        if 0<=b<30: grouped[b].append(float(r['end_to_end_ms']))
    return grouped


def plot_series(out,lang,model,runs,folders):
    fig,axes=plt.subplots(2,2,figsize=(12,8.5)); line_colors=['#31599B','#009C83','#C85B67']
    for column,cond in enumerate(('idle','walk')):
        for run in (1,2,3):
            row=next(r for r in runs if r['model']==model and r['condition']==cond and r['ulangan']==str(run))
            grouped=bins(ROOT / folders[row['run_id']] / 'jendela_runtime.csv')
            idx=sorted(grouped); t=[2*k+1 for k in idx]
            means=[float(np.mean(grouped[k])) for k in idx]; fps=[len(grouped[k])/2 for k in idx]
            for ax,values in [(axes[0,column],means),(axes[1,column],fps)]:
                ax.plot(t,values,color=line_colors[run-1],linewidth=1.35,label=f'{tr(lang,"Ulangan","Run")} {run}')
        axes[0,column].set_title(tr(lang,'Robot diam','Robot idle') if cond=='idle' else tr(lang,'Robot berjalan','Robot walking'))
        axes[0,column].set_ylabel(tr(lang,'Latensi rata-rata (ms)','Mean latency (ms)'))
        axes[1,column].set_ylabel(tr(lang,'Frame diterima / detik','Received frames / second'))
        for ax in (axes[0,column],axes[1,column]):
            ax.set_xlim(0,60); ax.set_xlabel(tr(lang,'Waktu sejak frame pertama (detik)','Time since first frame (seconds)'))
            ax.legend(fontsize=7.5,ncol=3,frameon=False,loc='upper right')
    header(fig,DISPLAY[model]+' — '+tr(lang,'grafik selama pengujian','performance over time'),
           tr(lang,'Tiga garis adalah tiga ulangan · setiap titik dirata-ratakan per 2 detik',
              'Three lines show three runs · each point summarizes a 2-second bin'))
    foot(fig,tr(lang,'Latensi = rata-rata frame per bin; FPS = frame diterima / 2 detik. Sumbu Y diperbesar; run tidak bersamaan.',
                'Latency = mean frames per bin; FPS = received frames / 2 seconds. Y axes are zoomed; runs were not simultaneous.'))
    save(fig,out,f'09_garis_waktu_{model}',lang)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True); args=parser.parse_args()
    out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False); init_style()
    t05=read(DATA/'T05_akurasi_test_keseluruhan.csv'); paired=read(DATA/'T30_kd_hybrid_test_berpasangan.csv')
    runs=read(DATA/'T36_runtime_live_setara_per_run.csv'); t38=read(DATA/'T38_akurasi_op3_empat_model_260.csv')
    t42=read(DATA/'T42_ablasi_teacher_yolo11s_val.csv'); train=read(DATA/'T35_waktu_training_dan_pengujian.csv')
    folders={r['run_id']:r['folder'] for r in read(AUDIT)}
    assert len(runs)==24 and len(folders)==24 and len(t42)==6
    camera={(m,r['class']):r for m in MODELS for r in t38 if r['model']==T38[m]}
    test={m:{} for m in MODELS}
    for m,method in [('teacher','Teacher'),('sup1337','Supervised student'),('kd42','Pure KD')]:
        for metric in ('mAP50','mAP50_95','precision','recall','F1'):
            key='mAP50-95' if metric=='mAP50_95' else metric
            test[m][key]=float(next(r for r in t05 if r['method']==method and r['metric']=='test_'+metric)['mean'])
    for metric in ('mAP50','mAP50-95','precision','recall','F1'):
        test['hybrid1337'][metric]=float(next(r for r in paired if r['row_type']=='mean_sd' and r['metric']==metric)['hybrid_full'])
    for lang in LANGS:
        SHORT['kd42'] = 'KD Murni' if lang == 'id' else 'Pure KD'
        DISPLAY['kd42'] = 'KD Murni' if lang == 'id' else 'Pure KD'
        plot_test(out,lang,test,paired); plot_op3(out,lang,camera); plot_runtime(out,lang,runs)
        plot_t42(out,lang,t42); plot_training(out,lang,train)
        for model in MODELS:
            plot_individual(out,lang,model,runs,camera); plot_series(out,lang,model,runs,folders)
    sources=[DATA/p for p in ['T05_akurasi_test_keseluruhan.csv','T30_kd_hybrid_test_berpasangan.csv',
             'T35_waktu_training_dan_pengujian.csv','T36_runtime_live_setara_per_run.csv',
             'T38_akurasi_op3_empat_model_260.csv','T42_ablasi_teacher_yolo11s_val.csv']]+[AUDIT]
    sources += [ROOT / folders[r['run_id']] / 'jendela_runtime.csv' for r in runs]
    manifest={'generator':str(Path(__file__).resolve().relative_to(ROOT)),
              'generator_sha256':sha(Path(__file__).resolve()),
              'sources_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources},'bins_seconds':2,
              'notes':'FPS grafik garis = jumlah frame per bin 2 detik, tidak sama dengan FPS kumulatif. Run tidak simultan.',
              'generated_files':{p.name:sha(p) for p in sorted(out.glob('*.png'))}}
    (out/'manifest_grafik.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


if __name__=='__main__': main()
