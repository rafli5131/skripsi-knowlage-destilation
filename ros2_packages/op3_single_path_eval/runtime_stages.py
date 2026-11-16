"""Recalculate 24-run runtime stage distributions from frozen logs, offline."""
import csv,hashlib,json,statistics
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'runs/op3_single_path_eval/20261116_runtime_01'; AUDIT=ROOT/'dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/T36_runtime_per_run.csv';CAMPAIGN=ROOT/'dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model'; IDENTITY=ROOT/'runs/op3_single_path_eval/20261116_identity_01/identity.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stats(xs):return {'mean_ms':statistics.mean(xs),'median_ms':statistics.median(xs),'p95_ms':float(np.percentile(xs,95))}
def main():
 assert json.loads(IDENTITY.read_text())['status']=='complete'
 audited=list(csv.DictReader(AUDIT.open())); schedule={(r['model'],r['condition'],r['ulangan']):r for r in csv.DictReader((CAMPAIGN/'jadwal_run.csv').open())}; assert len(audited)==24 and len(schedule)==24
 OUT.mkdir(parents=True,exist_ok=False); rows=[];pooled=defaultdict(list);sources={}
 keys=['preprocess_ms','inference_ms','postprocess_ms','end_to_end_ms','residual_ms']
 for a in audited:
  rid=a['run_id']; raw=ROOT/'runs/op3_pytorch'/f'{rid}.csv';meta=ROOT/'runs/op3_pytorch'/f'{rid}.json'
  if sha(raw)!=a['raw_csv_sha256'] or sha(meta)!=a['metadata_sha256']:raise ValueError('Source hash mismatch: '+rid)
  s=schedule[(a['model'],a['condition'],a['ulangan'])];start=datetime.fromisoformat(s['window_start_utc']);end=datetime.fromisoformat(s['window_end_utc'])
  selected=[r for r in csv.DictReader(raw.open()) if start<=datetime.fromisoformat(r['receive_time_utc'])<=end and not r['error']]
  vals={k:[float(x[k]) for x in selected] for k in keys[:-1]};vals['residual_ms']=[e-(p+i+q) for p,i,q,e in zip(*(vals[k] for k in keys[:-1]))]
  if not vals['end_to_end_ms'] or abs(statistics.mean(vals['end_to_end_ms'])-float(a['latency_mean_ms']))>1e-6:raise ValueError('T36 latency mismatch: '+rid)
  if len(selected)!=int(a['frames'])-int(a['error_frames']):raise ValueError('Frame count mismatch: '+rid)
  for k in keys:
   rows.append({'scope':'run','model':a['model'],'condition':a['condition'],'run_id':rid,'stage':k,'frames':len(selected),**stats(vals[k]),'cpu_percent_one_core':float(a['cpu_percent_one_core']),'cpu_percent_16_cores':float(a['cpu_percent_16_cores'])});pooled[(a['model'],a['condition'],k)].extend(vals[k])
  sources[rid]={'raw_csv_sha256':sha(raw),'metadata_sha256':sha(meta),'frames':len(selected),'e2e_mean_match_t36':True}
 for (model,cond,k),values in sorted(pooled.items()):
  subset=[r for r in audited if r['model']==model and r['condition']==cond];rows.append({'scope':'model_condition_pooled','model':model,'condition':cond,'run_id':'','stage':k,'frames':len(values),**stats(values),'cpu_percent_one_core':statistics.mean(float(x['cpu_percent_one_core']) for x in subset),'cpu_percent_16_cores':statistics.mean(float(x['cpu_percent_16_cores']) for x in subset)})
 with (OUT/'runtime_stages.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 report={'status':'complete','created_utc':datetime.now(timezone.utc).isoformat(),'runs':24,'rows':len(rows),'window_rule':'receive_time_utc inclusive within jadwal_run, error empty; identical to op3_runtime_audit_24','pooled_statistics':'per frame pooled across three runs; CPU is mean of three run means','schedule_sha256':sha(CAMPAIGN/'jadwal_run.csv'),'audit_T36_sha256':sha(AUDIT),'sources':sources,'stages_csv_sha256':sha(OUT/'runtime_stages.csv'),'residual':'end_to_end_ms - (preprocess_ms + inference_ms + postprocess_ms), computed per frame; not isolated tracker latency'}
 (OUT/'runtime_stages_manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('RUNTIME_STAGE_PASS 24 runs',flush=True)
if __name__=='__main__':main()
