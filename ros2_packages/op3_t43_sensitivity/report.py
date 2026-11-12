"""Summarize the verified offline T43 confidence sweep without choosing a threshold."""
import csv,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]; RUN=ROOT/'runs/op3_t43_sensitivity/20261112_confidence_01'; DOC=ROOT/'dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43'; TABLE=ROOT/'analisis_performa/tabel'
NAMES={'teacher_fp32':'Teacher YOLO11n','hybrid_full_seed1337':'KD Hybrid','supervised_seed1337':'Supervised','kd_seed42':'KD Murni'};COLORS={'teacher_fp32':'#276c9e','hybrid_full_seed1337':'#d95f02','supervised_seed1337':'#27865e','kd_seed42':'#8847a9'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((RUN/'run_manifest.json').read_text());assert m['status']=='complete' and len(m['models_verified'])==4
 assert sha(RUN/'confidence_sweep.csv')==m['outputs']['confidence_sweep_sha256']
 rows=list(csv.DictReader((RUN/'confidence_sweep.csv').open()));assert len(rows)==4*3*18*4
 DOC.mkdir(parents=True,exist_ok=False); (DOC/'grafik').mkdir();TABLE.mkdir(parents=True,exist_ok=True)
 shutil.copy2(RUN/'confidence_sweep.csv',TABLE/'T43_sensitivitas_confidence.csv')
 for lang in ('id','en'):
  for cls in ('ball','gawang','robot'):
   fig,axes=plt.subplots(2,3,figsize=(14,7.5),sharex=True,sharey=True)
   for col,cond in enumerate(('idle','walking','combined')):
    for i,metric in enumerate(('recall','F1')):
     ax=axes[i,col]
     for name in NAMES:
      subset=[r for r in rows if r['model']==name and r['condition']==cond and r['class']==cls]
      ax.plot([float(r['threshold']) for r in subset],[float(r[metric]) for r in subset],color=COLORS[name],marker='o',markersize=2.3,linewidth=1.4,label=NAMES[name])
     ax.axvline(.25,color='black',linestyle='--',alpha=.45,linewidth=.9);ax.set_xlim(.05,.9);ax.set_ylim(-.03,1.05);ax.grid(alpha=.22);ax.set_xlabel('Ambang confidence (lebih besar dari)' if lang=='id' else 'Confidence threshold (strictly greater)')
     if col==0:ax.set_ylabel(metric+' (0–1)')
     if i==0:ax.set_title(({'idle':'Diam','walking':'Berjalan di tempat','combined':'Gabungan'} if lang=='id' else {'idle':'Idle','walking':'Walking in place','combined':'Combined'})[cond])
   h,l=axes[0,0].get_legend_handles_labels();fig.legend(h,l,loc='upper center',ncol=4,bbox_to_anchor=(.5,.93),frameon=False)
   fig.suptitle(('Sensitivitas confidence — ' if lang=='id' else 'Confidence sensitivity — ')+({'ball':'Bola' if lang=='id' else 'Ball','gawang':'Gawang' if lang=='id' else 'Goal','robot':'Robot'}[cls]),fontsize=15)
   fig.text(.5,.01,('Garis putus-putus: ambang operasi tetap 0,25; hasil deskriptif pada satu susunan.' if lang=='id' else 'Dashed line: fixed operating threshold 0.25; descriptive results on one setup.'),ha='center',fontsize=9)
   fig.tight_layout(rect=(0,.04,1,.90));fig.savefig(DOC/'grafik'/f'sapuan_{cls}_{lang}.png',dpi=300);plt.close(fig)
 summary=[]
 for name,v in m['models_verified'].items():
  data=[r for r in rows if r['model']==name and r['condition']=='combined' and r['class']=='gawang']; good=[r for r in data if float(r['recall'])>=.9];at05=data[0];at25=next(r for r in data if r['threshold']=='0.25');dist=v['matched_goal_confidence']['distribution'];count=v['matched_goal_confidence']['count'];
  summary.append({'model':name,'highest_threshold_recall_ge_0_9':good[-1]['threshold'] if good else None,'recall_0_05':float(at05['recall']),'recall_0_25':float(at25['recall']),'matched_count_floor':count,'confidence':dist})
 (DOC/'ringkasan_confidence.json').write_text(json.dumps({'status':'complete_part_A','models':summary,'caveat':'Prediction path sweep differs in padding and NMS from AP validation path; no causal or calibration-only conclusion.'},indent=2)+'\n')
 lines=[]
 for s in summary:
  q=s['confidence'];lines.append(f"| {NAMES[s['model']]} | {s['highest_threshold_recall_ge_0_9'] or 'Tidak ada'} | {s['recall_0_05']:.3f} | {s['recall_0_25']:.3f} | {s['matched_count_floor']}/200 | {q['median']:.4f} | {q['q1']:.4f}–{q['q3']:.4f} | {q['min']:.4f}–{q['max']:.4f} |")
 table='\n'.join(lines)
 narrative='''## Temuan perbedaan jalur AP dan prediksi

AP T43 dihitung dengan `model.val`, sedangkan sapuan dan precision/recall/F1 menggunakan `model.predict`. Pada pemeriksaan lokal model teacher, validator menerima tensor **512 × 672** setelah padding, sedangkan prediktor menerima **480 × 640**. Kode Ultralytics validator juga menggunakan NMS `multi_label=True`; tidak dapat diasumsikan kedua jalur memiliki postprocessing yang identik. Pada satu frame yang sama, prediksi gawang teacher tidak muncul di atas 0,001 pada jalur operasi default, tetapi confidence berubah ketika ukuran/padding prediksi diubah. Diagnosis ini menunjukkan bahwa perbedaan preprocessing dan postprocessing **dapat memengaruhi** hasil; pengaruh masing-masing belum diisolasi.

Sebagai pemeriksaan tambahan, keluaran validator teacher yang disimpan dalam JSON (nilai dan kotak dibulatkan) menghasilkan 200/200 pasangan gawang pada floor 0,001 dan 37/200 pada confidence >0,25; pada jalur prediksi operasi hasilnya 68/200 dan 0/200. Hasil ini tidak menggantikan tabel utama karena jalurnya berbeda. Jangan menyimpulkan bahwa selisih AP dan F1 hanya akibat confidence atau kalibrasi, dan jangan mengganti ambang operasi berdasarkan set ini.
'''
 txt=f'''# T43 — sensitivitas confidence (bagian A)

Empat model dievaluasi ulang **offline** pada 260 frame dan label yang sama. Prediksi T43 sebelumnya disimpan hanya di atas 0,25, sehingga prediksi dihitung ulang dari confidence 0,001. AP gabungan dan hitungan setiap frame pada confidence >0,25 cocok dengan baseline untuk keempat model. Sapuan memakai confidence **lebih besar dari** 0,05–0,90 per 0,05, NMS IoU 0,7 dan pencocokan kelas + IoU ≥0,5. F1 makro mengikuti D11. Kondisi diam, berjalan di tempat, dan gabungan serta detail TP/FP/FN semua kelas ada di [CSV](T43_sensitivitas_confidence.csv).

Ambang tertinggi berikut hanya berasal dari grid dan bukan ambang baru yang disarankan. Kuartil dihitung dari prediksi gawang yang cocok pada floor 0,001; jumlah pasangan dapat kurang dari 200, sehingga bukan distribusi untuk seluruh gawang.

| Model | Ambang tertinggi recall ≥ 0,9 | Recall >0,05 | Recall >0,25 | Pasangan pada floor | Median | Q1–Q3 | Min–maks |
|---|---:|---:|---:|---:|---:|---:|---:|
{table}

Pada jalur prediksi ini supervised mencapai recall 1,0 pada >0,05 seperti Hybrid; teacher tidak mencapai 0,9 pada grid, dengan recall 0 pada >0,05. KD Murni juga tidak mencapai 0,9 pada grid. Evaluasi ini bersifat deskriptif pada satu susunan adegan dengan frame berurutan dan pra-label gabungan dari model yang diuji.

{narrative}
Grafik ID/EN per kelas dan dokumentasi tersedia pada [folder percobaan](../../dokumentasi/2026-11-12/percobaan-40-sensitivitas-t43/README_ID.md). Ambang operasi D4 tetap 0,25. Bagian B menunggu sesi peninjau kedua dan pelabelan konvensi alternatif.
'''
 (TABLE/'T43_sensitivitas_confidence.md').write_text(txt)
 (TABLE/'T43_sensitivitas_label_52.md').write_text('# T43 — sensitivitas label 52 frame\n\n**Belum ada hasil.** Aturan awal dan aturan alternatif sudah disiapkan, tetapi peninjauan Dipo dan pelabelan konvensi alternatif belum dilakukan. Kesepakatan antarpeninjau, urutan model, dan CSV hasil baru dapat dilaporkan setelah kedua sesi lengkap dan diaudit.\n')
 (DOC/'README_ID.md').write_text('# Uji sensitivitas T43 — 12 November 2026\n\n**Bagian A selesai; bagian B menunggu peninjau kedua dan sesi label alternatif.**\n\n[Tabel dan metode](../../../analisis_performa/tabel/T43_sensitivitas_confidence.md) · [CSV rinci](../../../analisis_performa/tabel/T43_sensitivitas_confidence.csv) · [Bagian B: status](../../../analisis_performa/tabel/T43_sensitivitas_label_52.md)\n\nGrafik ID dan EN di `grafik/`: recall dan F1 masing-masing kelas untuk empat model, dalam kondisi diam, berjalan di tempat dan gabungan. Ambang operasi tetap >0,25. AP dan hasil operasi baseline per frame terverifikasi sebelum sapuan.\n\n'+narrative+'\n## Peninjauan manusia\n\nPeninjau kedua adalah Dipo. Aturan tertulis dibekukan setelah klarifikasi Bhre dan sebelum jendela peninjau dibuka; titik tengah bagian tiang yang terlihat adalah batas atas kotak gawang, dan kotak robot mencakup badan, tangan dan kaki namun mengecualikan bagian hitam di atas badan sesuai keputusan sebelumnya. Aturan ini dipertegas setelah label awal T43, sehingga perbedaan dengan label awal mungkin mencerminkan aturan dan peninjau sekaligus. Belum ada data Dipo; konvensi alternatif juga belum dilabeli. Frame, label, dan prediksi per frame tetap lokal.\n')
 (DOC/'README_EN.md').write_text('# T43 sensitivity analysis — 12 November 2026\n\n**Part A completed; Part B awaits the second reviewer and an alternative-label session.** The offline confidence sweep uses the same 260 reviewed frames; AP and per-frame counts at confidence >0.25 reproduce the T43 baseline for all four models. Thresholds 0.05–0.90 are descriptive only; the operating threshold remains 0.25. See the [detailed CSV](../../../analisis_performa/tabel/T43_sensitivitas_confidence.csv) and English plots in `grafik/`.\n\nImportant qualification: T43 AP uses `model.val` while operating metrics and this sweep use `model.predict`. For the teacher, measured padded input shapes were 512×672 and 480×640, respectively; validation also uses multi-label NMS. A single-frame check shows confidence changes with different padding. Their individual effects have not been isolated, so the AP–F1 discrepancy cannot be attributed solely to calibration.\n\nAll frames derive from one setup and are correlated. The same models helped produce prelabels. The second reviewer has not annotated yet; confidence analysis does not establish inter-rater reliability or generalization. Raw images, labels and per-frame predictions remain local.\n')
 print('REPORT_COMPLETE',DOC)
if __name__=='__main__':main()
