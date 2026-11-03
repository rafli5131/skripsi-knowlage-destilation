"""Audit ulang ringkasan sendi dan ack menggunakan fungsi shared laporan OP3."""
import csv
import json
from pathlib import Path
from op3_equal_live_report.report import summarize, read_joint

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run'
TABLE=ROOT/'dokumentasi/2026-11-02/percobaan-30-uji-live-setara-empat-model/05-ringkasan/tabel_24_run.csv'

def main():
    index={}
    for day in ('2026-11-02','2026-11-03'):
        for p in (ROOT/'dokumentasi'/day).rglob('summary_metrics.json'):
            if 'arsip' in str(p):continue
            data=json.loads(p.read_text());index.setdefault(data.get('run_id'),[]).append(p)
    audit=[]
    for row in csv.DictReader(TABLE.open()):
        rid=row['run_id']; matches=index.get(rid,[]); issues=[]; notes=[]
        if len(matches)!=1:
            audit.append({'run_id':rid,'status':'perlu_tinjau','issues':f'summary_matches={len(matches)}','notes':'','folder':''});continue
        folder=matches[0].parent; raw=ROOT/'runs/op3_pytorch'/f'{rid}.csv'
        summary,_=summarize(raw,folder)
        if summary['status']!='lulus_cek_otomatis':issues.extend(summary['reasons'])
        pre=folder/'telemetry_pre.txt'; npre=len(read_joint(pre)) if pre.is_file() else 0
        if npre!=20:notes.append(f'telemetry_pre_{npre}_sendi')
        if not (folder/'frame_deteksi_sesudah_jendela.png').is_file():notes.append('overlay_sesudah_tidak_tersedia')
        if row['condition']=='walk':
            guard=folder/'gait_guard.json'
            if not guard.is_file():issues.append('guard_tidak_tersedia')
            else:
                g=json.loads(guard.read_text())
                if g.get('status')!='completed' or not g.get('start_ack_receive_utc') or not g.get('stop_ack_receive_utc'):issues.append('ack_start_stop_tidak_lengkap')
                if g.get('head_violation'):issues.append('batas_kepala_terlampaui')
        audit.append({'run_id':rid,'status':'lulus_cek_sampel' if not issues else 'perlu_tinjau','issues':'|'.join(issues),'notes':'|'.join(notes),'folder':str(folder.relative_to(ROOT))})
    with (OUT/'audit_telemetry.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(audit[0]),lineterminator='\n');w.writeheader();w.writerows(audit)
    print(json.dumps({'runs':len(audit),'issues':[r for r in audit if r['issues']],'notes':[r for r in audit if r['notes']]},indent=2))

if __name__=='__main__':main()
