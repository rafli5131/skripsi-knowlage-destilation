"""Create T43 tables, documentation and illustrative manually labelled frames."""
import csv, json, shutil, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'ros2_packages/op3_camera_eval'))
from op3_camera_eval.evaluate import read_labels, sha256
RUN=ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260'; DOC=ROOT/'dokumentasi/2026-11-12/percobaan-39-evaluasi-t43'; TABLE=ROOT/'analisis_performa/tabel'
NAMES={'teacher_fp32':'Teacher YOLO11n','hybrid_full_seed1337':'KD Hybrid','supervised_seed1337':'Supervised','kd_seed42':'KD Murni'}
def main():
 r=json.loads((RUN/'results.json').read_text()); assert r['status']=='complete'
 TABLE.mkdir(parents=True,exist_ok=True);shutil.copy2(RUN/'summary.csv',TABLE/'T43_akurasi_op3_empat_model_260.csv')
 rows=[]
 for n,d in r['models'].items():
  a=d['splits']['combined']['ap'];m=d['splits']['combined']['operating']['macro']; goal=d['splits']['combined']['operating']['per_class']['gawang']
  rows.append(f"| {NAMES[n]} | {a['mAP50']:.4f} | {a['mAP50-95']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | {m['F1_harmonic_macro_precision_recall']:.4f} | {goal['true_positives']}/200 |")
 tab='\n'.join(rows)
 text=f'''# T43 — akurasi empat model pada 260 frame OP3

Ini adalah evaluasi eksploratif **offline** pada satu susunan adegan; bukan pengukuran FPS/latensi dan bukan uji generalisasi lintas adegan. Set terdiri atas 100 frame berobjek dan 30 negatif per kondisi diam dan berjalan. Seluruh gawang pada frame berobjek bersifat parsial; kotak gawang adalah bagian bawah dan kotak robot hanya badan, sesuai keputusan operator setelah 52 label awal. Konvensi tersebut berbeda dari T38; jangan membandingkan nilainya sebagai pengaruh model atau kondisi yang setara.

| Model | mAP50 | mAP50–95 | Precision makro | Recall makro | F1 utama | Gawang TP |
|---|---:|---:|---:|---:|---:|---:|
{tab}

mAP menggunakan confidence floor 0,001; precision, recall, F1 dan TP menggunakan confidence **> 0,25** serta IoU ≥ 0,5; NMS IoU 0,7. F1 utama adalah harmonik precision makro dan recall makro; rerata F1 per kelas tersedia di CSV. Perbedaan kedua ambang menjelaskan mengapa mAP50 tinggi dapat terjadi meskipun tidak ada prediksi gawang di atas 0,25. Pada setiap model, 0/60 frame negatif menghasilkan prediksi di atas ambang tersebut; angka ini hanya untuk adegan dan set ini.

Pra-label berasal dari gabungan keempat model yang dievaluasi. Operator juga telah melihat preview Hybrid dan mendapat masukan selama pelabelan; tinjauan awal bukan independen sempurna. Pada 52 sampel, satu orang yang sama menghasilkan 40/40 pasangan IoU ≥0,5 di masing-masing kelas; itu bukan kesepakatan antarpeninjau dan tidak memastikan kotak benar. Batas atas kotak gawang bagian bawah belum dipatok pada landmark tetap, dan konvensi kotak berdampak pada AP terutama IoU tinggi. Frame berurutan tidak independen; jangan menafsirkan 260 frame sebagai 260 adegan.

Rincian per kondisi/kelas/TP/FP/FN dalam [CSV](T43_akurasi_op3_empat_model_260.csv). Rincian metodologi, grafik dan confusion matrix tersedia di [dokumentasi T43](../../dokumentasi/2026-11-12/percobaan-39-evaluasi-t43/README_ID.md). Hasil ini tidak menggantikan T38 atau hasil pengujian runtime yang ada.
'''
 (TABLE/'T43_akurasi_op3_empat_model_260.md').write_text(text)
 manifest=json.loads((RUN/'input_manifest.json').read_text());frames=manifest['frames']; selected=[]
 for sid in ['20261112_t43_idle_objek_ulang_01','20261112_t43_walk_objek_ulang_01']:
  key=next(k for k in sorted(frames) if k.startswith(sid+'__'));selected.append((key,frames[key]))
 fig,axes=plt.subplots(1,2,figsize=(12,5))
 for ax,(key,f),title in zip(axes,selected,['Diam / Idle','Berjalan / Walking']):
  ax.imshow(Image.open(f['image'])); colors=['#ff4242','#39df71','#3aa2ff']
  for cls,x,y,w,h in read_labels(Path(f['label'])):
   ax.add_patch(Rectangle(((x-w/2)*640,(y-h/2)*480),w*640,h*480,fill=False,edgecolor=colors[cls],linewidth=2))
   ax.text((x-w/2)*640,max(10,(y-h/2)*480-4),['ball','gawang','robot'][cls],color=colors[cls],fontsize=8,bbox={'facecolor':'black','alpha':.6,'pad':1})
  ax.set_title(title);ax.axis('off')
 fig.suptitle('Contoh frame dengan label manusia / Examples with human labels');fig.tight_layout();fig.savefig(DOC/'contoh_frame_label_manusia.png',dpi=200);plt.close(fig)
 common='[Tabel ringkasan](../../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.md) · [CSV rinci](../../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.csv) · [Grafik mAP](grafik/perbandingan_map_id.png) · [Confusion matrix gabungan](confusion_matrix/empat_model_id.png)'
 (DOC/'README_ID.md').write_text('# T43 — evaluasi offline kamera OP3\n\n'+common+'\n\n'+text.split('\n',2)[2].replace('Rincian per kondisi/kelas/TP/FP/FN dalam [CSV](T43_akurasi_op3_empat_model_260.csv). Rincian metodologi, grafik dan confusion matrix tersedia di [dokumentasi T43](../../dokumentasi/2026-11-12/percobaan-39-evaluasi-t43/README_ID.md).','Rincian per kondisi/kelas/TP/FP/FN tersedia dalam CSV pada tautan di atas.')+'\n## Berkas dan interpretasi\n\nGrafik individual dan gabungan tersedia dalam `grafik/`; confusion matrix empat model, tiap model, dan hitungannya tersedia dalam `confusion_matrix/`, masing-masing bahasa Indonesia dan Inggris. Contoh frame berlabel manusia, data mentah dan prediksi per frame tetap lokal; hanya hasil agregat dan manifest hash dibagikan. Matriks memakai baris prediksi, kolom label manual, pencocokan antar kelas berdasarkan IoU tertinggi ≥ 0,5, confidence > 0,25, dan kategori latar untuk pasangan yang tidak cocok; aturan ini bisa menghasilkan rincian berbeda dari pencocokan per kelas untuk precision/recall.\n\nStatistik tindakan edit tidak tercatat per tindakan pada antarmuka; tidak dapat menghitung secara andal jumlah kotak yang digeser atau diubah kelas hanya dari log. Label draf dan final tersimpan sehingga dapat dibandingkan, tetapi peristiwa edit tidak boleh direkayasa.\n')
 (DOC/'README_EN.md').write_text('# T43 — offline OP3 camera evaluation\n\n[Detailed CSV](../../../analisis_performa/tabel/T43_akurasi_op3_empat_model_260.csv) · [mAP chart](grafik/perbandingan_map_en.png) · [Combined confusion matrices](confusion_matrix/empat_model_en.png)\n\nThis exploratory evaluation uses the same 260 frames for four models: 130 idle and 130 walking in place, including 30 negative frames per condition. All goal frames are partial; the reviewer chose a lower-goal-region box and a robot-body box. These conventions differ from T38, so results are not directly comparable. Images come from one setup and adjacent frames are correlated.\n\nAP uses confidence floor 0.001, while operating precision/recall/F1 use confidence > 0.25 and matching IoU ≥ 0.5; NMS IoU is 0.7. Primary macro F1 is the harmonic mean of macro precision and macro recall. Matrix rows are predictions and columns are manual labels, matched class-agnostically by descending IoU; background denotes unmatched boxes.\n\nPrelabels are a union of all four evaluated models. The operator saw a Hybrid preview and received feedback while annotating. The 52-frame audit compares two passes by the same reviewer, not independent raters; the partial-goal upper boundary has no fixed landmark. These limitations and the dataset scope must accompany any results. Runtime speed is not measured here. Individual and combined plots and matrices are in the respective folders.\n')
 print('Wrote tables and documentation')
if __name__=='__main__':main()
