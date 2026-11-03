"""Audit log 24 slot dan susun tabel serta grafik runtime OP3."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN = ROOT / 'dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model'
OUT = ROOT / 'dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run'
HASHES = {'teacher':'e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c',
          'hybrid1337':'cd6bcb8bd9316930a14f4f1c5f6ee408e8dd64dddb52fb3c1e8773cde310b363',
          'sup1337':'d41046c384c9795b7724db726a99abbbd26217ffa53c77412d5cfcf34a16e041',
          'kd42':'2da0c0e58a5c1884358fe814f8992cda19bb7b58f292edc15f53b9081b6129c3'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    slots = list(csv.DictReader((CAMPAIGN/'05-ringkasan/tabel_24_run.csv').open()))
    schedule = {(r['model'],r['condition'],r['ulangan']):r for r in csv.DictReader((CAMPAIGN/'jadwal_run.csv').open())}
    assert len(slots)==24 and len({(r['model'],r['condition'],r['ulangan']) for r in slots})==24
    results=[]; pooled=defaultdict(list)
    for slot in slots:
        model,cond,rep,rid=(slot[k] for k in ('model','condition','ulangan','run_id'))
        meta_path=ROOT/'runs/op3_pytorch'/f'{rid}.json'; raw_path=meta_path.with_suffix('.csv')
        meta=json.loads(meta_path.read_text()); rows=list(csv.DictReader(raw_path.open()))
        sch=schedule[(model,cond,rep)]; start=datetime.fromisoformat(sch['window_start_utc']); end=datetime.fromisoformat(sch['window_end_utc'])
        selected=[r for r in rows if start<=datetime.fromisoformat(r['receive_time_utc'])<=end]
        clean=[r for r in selected if not r['error']]; issues=[]
        def check(ok, label):
            if not ok: issues.append(label)
        check(meta['checkpoint_sha256']==HASHES[model], 'hash_checkpoint')
        for key,value in [('device','cpu'),('precision','FP32'),('imgsz',640),('confidence_threshold',0.25),('iou_threshold',0.45),('tracking_enabled',True),('tracker_config','botsort.yaml'),('preview_enabled',True),('warmup_frames',30),('torch_num_threads_actual',4),('torch_interop_threads_actual',2)]:
            check(meta.get(key)==value, 'config_'+key)
        check(meta.get('condition')==('walking' if cond=='walk' else 'servo_idle'), 'condition')
        times=[datetime.fromisoformat(r['receive_time_utc']) for r in rows]
        check(all(b>a for a,b in zip(times,times[1:])), 'waktu_receive_tidak_monoton')
        check(times[-1]>=end and (end-start).total_seconds()==60, 'jendela_tidak_lengkap')
        check(len(clean)>=2 and (len(selected)-len(clean))/max(1,len(selected))<=.01, 'error_frame')
        check(all(r['is_warmup'].lower()=='false' for r in selected), 'warmup')
        stamps=[int(r['capture_stamp_ns']) for r in clean]
        stamps_ok=all(x>0 for x in stamps) and all(b>a for a,b in zip(stamps,stamps[1:]))
        check(stamps_ok,'timestamp_kamera')
        fps=(len(stamps)-1)*1e9/(stamps[-1]-stamps[0]) if stamps_ok and len(stamps)>1 else None
        lat=[float(r['end_to_end_ms']) for r in clean]; cpu=[float(r['process_cpu_percent']) for r in clean]; rss=[float(r['process_rss_bytes'])/1048576 for r in clean]
        check(len(selected)==int(slot['frames_window']), 'jumlah_frame_tabel')
        check(fps is not None and abs(fps-float(slot['fps']))<1e-6, 'fps_tabel')
        check(abs(statistics.mean(lat)-float(slot['latency_mean_ms']))<1e-6, 'latensi_tabel')
        check(meta.get('status')=='stopped' and meta.get('stop_reason')=='duration_elapsed', 'stop_detector')
        pooled[(model,cond)].extend(lat)
        gaps=[(b-a).total_seconds() for a,b in zip([datetime.fromisoformat(r['receive_time_utc']) for r in selected],[datetime.fromisoformat(r['receive_time_utc']) for r in selected][1:])]
        results.append({'model':model,'condition':cond,'ulangan':rep,'run_id':rid,'tanggal_utc':start.date().isoformat(),'status_cek_sebelumnya':slot['status'],'audit_log': 'lulus' if not issues else 'perlu_tinjau','temuan':'|'.join(issues),'window_start_utc':start.isoformat(),'window_end_utc':end.isoformat(),'frames':len(selected),'error_frames':len(selected)-len(clean),'latency_mean_ms':statistics.mean(lat),'latency_median_ms':statistics.median(lat),'latency_p95_ms':float(np.percentile(lat,95)),'fps':fps,'cpu_percent_one_core':statistics.mean(cpu),'cpu_percent_16_cores':statistics.mean(cpu)/16,'rss_mib':statistics.mean(rss),'max_receive_gap_s':max(gaps) if gaps else None,'checkpoint_sha256':meta['checkpoint_sha256'],'raw_csv_sha256':digest(raw_path),'metadata_sha256':digest(meta_path)})
    aggregates=[]
    for cond in ('idle','walk'):
        for model in ('teacher','hybrid1337','sup1337','kd42'):
            group=[r for r in results if r['model']==model and r['condition']==cond]; item={'model':model,'condition':cond,'runs':len(group),'frames_total':sum(r['frames'] for r in group),'audit_log': 'lulus' if all(r['audit_log']=='lulus' for r in group) else 'perlu_tinjau'}
            for key in ('latency_mean_ms','fps','cpu_percent_one_core','rss_mib'):
                vals=[r[key] for r in group];item[key+'_mean']=statistics.mean(vals);item[key+'_sd_sample']=statistics.stdev(vals)
            item['latency_pooled_median_ms']=statistics.median(pooled[(model,cond)]);item['latency_pooled_p95_ms']=float(np.percentile(pooled[(model,cond)],95));aggregates.append(item)
    write_csv(OUT/'T36_runtime_per_run.csv',results);write_csv(OUT/'T37_runtime_ringkasan.csv',aggregates)
    labels={'teacher':'Teacher','hybrid1337':'KD Hybrid','sup1337':'Supervised','kd42':'KD murni'}
    for lang in ('id','en'):
        fig,axes=plt.subplots(2,2,figsize=(16,10));metrics=[('latency_mean_ms','Latensi rata-rata (ms)','Mean latency (ms)'),('fps','FPS efektif (frame/detik)','Effective FPS (frames/s)'),('cpu_percent_one_core','CPU proses (% satu CPU logis)','Process CPU (% of one logical CPU)'),('rss_mib','RAM RSS (MiB)','RAM RSS (MiB)')]
        for ax,(key,yl_id,yl_en) in zip(axes.flat,metrics):
            for idx,model in enumerate(labels):
                for offset,cond,color in ((-.18,'idle','#1872a4'),(.18,'walk','#d7852f')):
                    g=[r[key] for r in results if r['model']==model and r['condition']==cond]; x=idx+offset
                    ax.errorbar(x,statistics.mean(g),yerr=statistics.stdev(g),fmt='o',color=color,capsize=5,markersize=8,label=('Diam' if lang=='id' else 'Idle') if idx==0 and cond=='idle' else (('Berjalan' if lang=='id' else 'Walking') if idx==0 else None))
                    ax.scatter([x-.05,x,x+.05],g,marker='x',color=color,s=36)
            ax.set_xticks(range(4),list(labels.values()));ax.set_ylabel(yl_id if lang=='id' else yl_en);ax.grid(axis='y',alpha=.25);ax.legend()
        fig.suptitle('OP3: rata-rata ± SD; × = ulangan' if lang=='id' else 'OP3: mean ± SD; × = repetition',fontsize=16);fig.tight_layout();fig.savefig(OUT/f'grafik_runtime_24_run_{lang}_hd.png',dpi=180);plt.close(fig)
    manifest=json.loads((ROOT/'runs/op3_multi_session_eval/20261023_hybrid_supervised1337_primary260_v1/input_manifest.json').read_text());roles=Counter();label_errors=[]
    for key,frame in manifest['frames'].items():
        roles[frame['role']]+=1
        for kind in ('image','label'):
            p=Path(frame[kind]);
            if not p.is_file() or digest(p)!=frame[kind+'_sha256']:label_errors.append(f'{key}:{kind}')
    audit={'slots':len(results),'log_passed':sum(r['audit_log']=='lulus' for r in results),'log_issues':{r['run_id']:r['temuan'] for r in results if r['temuan']},'label_roles':dict(roles),'label_hash_errors':label_errors,'note':'Cek log tidak membuktikan torque, kontinuitas tampilan, atau kesetaraan adegan.'}
    (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))

if __name__=='__main__': main()
