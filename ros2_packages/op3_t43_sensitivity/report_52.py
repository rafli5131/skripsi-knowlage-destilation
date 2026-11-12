"""Create the completed label-sensitivity table and comparison figures."""
import csv,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'runs/op3_t43_sensitivity/20261112_confidence_01';D=ROOT/'dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43';T=ROOT/'analisis_performa/tabel';sets=['bhre','dipo','alternative'];names={'teacher_fp32':'Teacher YOLO11n','hybrid_full_seed1337':'KD Hybrid','supervised_seed1337':'Supervised','kd_seed42':'KD Murni'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 data={s:json.loads((R/'label_52'/s/'results.json').read_text()) for s in sets};assert all(x['status']=='complete' and len(x['models'])==4 for x in data.values());ag=json.loads((R/'reviewer2_agreement.json').read_text());files=[json.loads((R/'label_52'/s/'input_manifest.json').read_text()) for s in sets];keys=set(files[0]['frames']);assert len(keys)==52 and all(set(x['frames'])==keys for x in files)
 assert all(len({f['frames'][k]['image_sha256'] for f in files})==1 for k in keys)
 csvpath=T/'T43_sensitivitas_label_52.csv';csvpath.parent.mkdir(exist_ok=True,parents=True)
 with csvpath.open('x',newline='') as f:
  fields=['label_set','model','class','ground_truth','predictions','TP','FP','FN','precision','recall','F1','mean_class_F1','mAP50','mAP50_95','negative_frames_with_fp'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for s in sets:
   for name,v in data[s]['models'].items():
    op=v['operating'];macro=op['macro'];a=v['ap'];w.writerow({'label_set':s,'model':name,'class':'macro','ground_truth':op['ground_truth'],'predictions':op['predictions'],'TP':op['true_positives'],'FP':op['false_positives'],'FN':op['false_negatives'],'precision':macro['precision'],'recall':macro['recall'],'F1':macro['F1_harmonic_macro_precision_recall'],'mean_class_F1':macro['F1_mean_per_class'],'mAP50':a['mAP50'],'mAP50_95':a['mAP50-95'],'negative_frames_with_fp':v['negative_frames_with_fp']})
    for cls,row in op['per_class'].items():
     ap=a['per_class'].get(cls,{});w.writerow({'label_set':s,'model':name,'class':cls,'ground_truth':row['ground_truth'],'predictions':row['predictions'],'TP':row['true_positives'],'FP':row['false_positives'],'FN':row['false_negatives'],'precision':row['precision'],'recall':row['recall'],'F1':row['F1'],'mAP50':ap.get('mAP50'),'mAP50_95':ap.get('mAP50-95')})
 model_rows=[]
 for n,label in names.items():
  parts=[]
  for s in sets:
   v=data[s]['models'][n];parts.extend([f"{v['ap']['mAP50']:.4f}",f"{v['ap']['mAP50-95']:.4f}",f"{v['operating']['macro']['precision']:.4f}",f"{v['operating']['macro']['recall']:.4f}",f"{v['operating']['macro']['F1_harmonic_macro_precision_recall']:.4f}",str(v['operating']['per_class']['gawang']['true_positives'])])
  model_rows.append('| '+label+' | '+' | '.join(parts)+' |')
 ranks={}
 for s in sets:
  ranks[s]={}
  for metric in ('mAP50-95','F1'):
   def score(n):return data[s]['models'][n]['ap']['mAP50-95'] if metric=='mAP50-95' else data[s]['models'][n]['operating']['macro']['F1_harmonic_macro_precision_recall']
   rank=[]
   for name in sorted(names,key=score,reverse=True):
    value=score(name)
    if rank and abs(value-rank[-1]['value'])<1e-12:rank[-1]['models'].append(names[name])
    else:rank.append({'models':[names[name]],'value':value})
   ranks[s][metric]=rank
 (D/'urutan_model_52.json').write_text(json.dumps(ranks,indent=2)+'\n')
 before=D/'arsip_sebelum_hasil_akhir';before.mkdir(exist_ok=False);shutil.copy2(T/'T43_sensitivitas_label_52.md',before/'T43_sensitivitas_label_52.md');shutil.copy2(D/'README_ID.md',before/'README_ID.md');shutil.copy2(D/'README_EN.md',before/'README_EN.md');shutil.copy2(D/'manifest_hasil_sha256.json',before/'manifest_hasil_sha256.json')
 agreements='\n'.join(f"| {cls} | {v['matches']}/{v['bhre']} | {v['matches']}/{v['dipo']} | {v['bhre_unmatched']} | {v['dipo_unmatched']} | {v['iou_mean']:.4f} | {v['iou_median']:.4f} |" for cls,v in ag['classes'].items())
 body='\n'.join(model_rows);ranklines=[]
 for s in sets:
  for metric in ('mAP50-95','F1'):
   ranklines.append(f"- {s} — {metric}: "+' > '.join(' = '.join(x['models'])+f" ({x['value']:.4f})" for x in ranks[s][metric]))
 labels=' | '.join(f'{s} {metric}' for s in ['Bhre','Dipo','Alternatif'] for metric in ['AP50','AP50–95','P','R','F1','TP gawang'])
 text=f'''# T43 — sensitivitas label pada 52 frame

Tiga set label pada **52 frame yang sama**: label final Bhre (T43 awal), label Dipo mengikuti aturan T43 yang diperjelas, dan label alternatif Dipo (seluruh rangka gawang dan seluruh tubuh robot terlihat). Dua sesi Dipo dilakukan berurutan; aturan awal diperjelas setelah anotasi Bhre, sehingga efek aturan dan peninjau tidak dapat dipisahkan. Tidak ada pelatihan atau pemilihan ulang model.

## Kesesuaian peninjau pada konvensi T43

Pasangan satu-ke-satu berkelas sama dengan IoU ≥0,5; jumlah pasangan dimaksimalkan, kemudian jumlah IoU. Label awal Bhre dan Dipo sama-sama memuat 40 kotak per kelas.

| Kelas | Pasangan/Bhre | Pasangan/Dipo | Bhre tanpa pasangan | Dipo tanpa pasangan | IoU rata-rata | IoU median |
|---|---:|---:|---:|---:|---:|---:|
{agreements}

## Hasil empat model

P, R dan F1 adalah makro pada confidence >0,25 dan IoU ≥0,5; F1 utama adalah harmonik P dan R makro (D11). AP menggunakan confidence floor 0,001. TP gawang adalah jumlah gawang terdeteksi pada ambang operasi. Per kelas, TP/FP/FN, dan negatif tersedia dalam [CSV](T43_sensitivitas_label_52.csv).

| Model | {labels} |
|---|'''+('---:|'*18)+f'''
{body}

## Urutan model

'''+ '\n'.join(ranklines)+'''

Urutan dinyatakan untuk sampel dan konvensi ini, bukan untuk memilih ulang model. Perbandingan antarsesi Dipo juga dapat mengandung efek urutan dan ingatan. Frame diambil dari satu setup dan saling berkorelasi; 52 frame bukan 52 adegan independen. Pra-label T43 memakai gabungan model yang diuji dan Bhre telah melihat preview Hybrid. Konvensi alternatif tidak sama dengan anotasi awal.

Penghitungan AP menggunakan `model.val`, sedangkan P/R/F1 menggunakan `model.predict`; tensor padding dan NMS berbeda pada pemeriksaan teacher. Jangan menafsirkan selisih AP dan F1 semata sebagai perbedaan kalibrasi confidence. Lihat [sensitivitas confidence](T43_sensitivitas_confidence.md) dan [dokumentasi](../../dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/README_ID.md).
'''
 (T/'T43_sensitivitas_label_52.md').write_text(text)
 for lang in ('id','en'):
  fig,axes=plt.subplots(1,2,figsize=(12,5));x=np.arange(4);w=.24
  for j,s in enumerate(sets):
   for ax,metric in zip(axes,['mAP50-95','F1']):
    vals=[data[s]['models'][n]['ap']['mAP50-95'] if metric=='mAP50-95' else data[s]['models'][n]['operating']['macro']['F1_harmonic_macro_precision_recall'] for n in names]
    lbl=({'bhre':'Bhre','dipo':'Dipo','alternative':'Alternatif' if lang=='id' else 'Alternative'})[s];bars=ax.bar(x+(j-1)*w,vals,w,label=lbl);ax.bar_label(bars,labels=[f'{v:.3f}' for v in vals],rotation=90,padding=3,fontsize=7)
    ax.set_xticks(x,list(names.values()),rotation=15,ha='right');ax.set_ylim(0,1.14);ax.set_ylabel('Nilai (0–1)' if lang=='id' else 'Score (0–1)');ax.set_title(metric);ax.grid(axis='y',alpha=.2)
  axes[0].legend(fontsize=8);fig.suptitle('Sensitivitas tiga set label — 52 frame' if lang=='id' else 'Sensitivity to three label sets — 52 frames');fig.tight_layout();fig.savefig(D/'grafik'/f'perbandingan_tiga_label_{lang}.png',dpi=300);plt.close(fig)
 p=D/'README_ID.md';s=p.read_text().replace('**Bagian A selesai; label Bhre dan Dipo selesai, sedangkan sesi label alternatif sedang berlangsung.**','**Bagian A dan B selesai.**').replace('Konvensi alternatif sedang dilabeli Dipo.','Konvensi alternatif telah dilabeli Dipo dan dievaluasi.');s+='\n## Hasil lengkap tiga set label\n\n[Tabel, kesepakatan, urutan dan batas interpretasi](../../../analisis_performa/tabel/T43_sensitivitas_label_52.md) · [CSV per kelas](../../../analisis_performa/tabel/T43_sensitivitas_label_52.csv) · [Grafik perbandingan](grafik/perbandingan_tiga_label_id.png). Hasil tiga set menggunakan 52 frame identik; koreksi label bila ada dicatat pada manifest penyelesaian label alternatif. Data mentah, label, log dan prediksi per frame tetap lokal.\n';p.write_text(s)
 p=D/'README_EN.md';s=p.read_text().replace('**Part A and the Bhre–Dipo comparison are complete; the alternative-label session is in progress.**','**Parts A and B are complete.**');s+='\nThe [three-label comparison](grafik/perbandingan_tiga_label_en.png) evaluates the same 52 frames. Bhre used the initial convention; Dipo annotated the clarified convention and then the alternative convention. Reviewer, rule clarification and annotation order effects cannot be isolated. See the [detailed CSV](../../../analisis_performa/tabel/T43_sensitivitas_label_52.csv).\n';p.write_text(s)
 old=json.loads((D/'manifest_hasil_sha256.json').read_text());paths=set(old['files']);paths.update(str(x.relative_to(ROOT)) for x in D.rglob('*') if x.is_file() and x!=D/'manifest_hasil_sha256.json');paths.update(str(x.relative_to(ROOT)) for x in [csvpath,T/'T43_sensitivitas_label_52.md',Path(__file__),R/'label_52/alternative/input_manifest.json',R/'label_52/alternative/results.json',ROOT/'data/op3_camera_eval/experiments/t43_sensitivity_20261112_01/alternative_completion_manifest.json']);old['status']='part_A_and_B_complete';old['updated_at_utc']=datetime.now(timezone.utc).isoformat();old['previous_manifest_sha256']=sha(before/'manifest_hasil_sha256.json');old['previous_versions_archived_in']=str(before.relative_to(ROOT));old['files']={x:sha(ROOT/x) for x in sorted(paths)};(D/'manifest_hasil_sha256.json').write_text(json.dumps(old,indent=2)+'\n');print('COMPLETE',json.dumps(ranks))
if __name__=='__main__':main()
