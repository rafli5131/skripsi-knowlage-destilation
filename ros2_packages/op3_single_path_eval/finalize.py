"""Write T44/T45 tables and documentation from completed offline analyses."""
import csv,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import ultralytics
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'runs/op3_single_path_eval';C=RUN/'20261116_analysis_01';R=RUN/'20261116_runtime_01';I=RUN/'20261116_identity_01';DOC=ROOT/'dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3';T=ROOT/'analisis_performa/tabel';N={'teacher_fp32':'Teacher','hybrid_full_seed1337':'KD Hybrid','supervised_seed1337':'Supervised','kd_seed42':'KD Murni'};V={'tracking':'Tracking + preview','no_tracking':'Tanpa tracking','cv_one_thread':'Tracking + OpenCV 1 thread','no_gmc':'Tracking tanpa GMC','openblas_one':'Tracking + OpenBLAS 1 thread'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f(x):return f'{x:.4f}' if x is not None else '—'
def main():
 identity=json.loads((I/'identity.json').read_text());d=json.loads((C/'comparison.json').read_text());st=json.loads((R/'runtime_stages_manifest.json').read_text());assert identity['status']==d['status']==st['status']=='complete' and len(identity['checks'])==48
 replay={}
 for n in ['teacher_fp32','hybrid_full_seed1337']:
  for v in V:
   p=R/'replay_v2'/n/v/'summary.json';x=json.loads(p.read_text());assert x['frames']==300 and x['torch_num_threads']==4 and x['torch_interop_threads']==2 and x['preview_plot'];assert sha(p.parent/'frame_log.csv')==x['frame_log_sha256'];replay[(n,v)]=x
 for n in ['T44_jalur_tunggal_op3_t38_t43.csv','T44_jalur_tunggal_op3_t38_t43.md','T45_rincian_latensi_dan_cpu_op3.csv','T45_rincian_latensi_dan_cpu_op3.md','T45_cpu_thread_replay.csv']:
  if (T/n).exists():raise FileExistsError(T/n)
 DOC.mkdir(parents=True,exist_ok=False);(DOC/'grafik').mkdir()
 tracker=Path(ultralytics.__file__).parent/'cfg/trackers/botsort.yaml';shutil.copy2(tracker,DOC/'botsort_terpasang.yaml')
 old38=json.loads((ROOT/'runs/op3_multi_session_eval/20261105_empat_model_primary260_v1/results.json').read_text());old43=json.loads((ROOT/'runs/op3_t43_evaluation/20261112_reviewed_260/results.json').read_text());rows=[]
 for n,groups in d['models'].items():
  for g,data in groups.items():
   baseline=old38['models'][n][g[4:]] if g.startswith('t38') else old43['models'][n]['splits'][g[4:]];ap=baseline['ap'];op=baseline['operating'];p=op['macro']['precision'];r=op['macro']['recall'];gc=op['per_class']['gawang'];goalap=ap['per_class'].get('gawang',{})
   rows.append({'dataset':g,'model':n,'path':'historical_valAP_predictPR','input':'val padding / predict padding','nms_iou':.7,'operating_confidence_strict':.25,'AP50':ap['mAP50'],'AP50_95':ap['mAP50-95'],'goal_AP50':goalap.get('mAP50'),'goal_AP50_95':goalap.get('mAP50-95'),'precision':p,'recall':r,'F1_D11':2*p*r/(p+r) if p+r else 0,'F1_mean_classes':op['macro']['F1'],'goal_TP':gc['true_positives'],'negative_frames_FP':'','factor_endpoints_valid':''})
   for name,v in data['variants'].items():
    ap=v.get('ap',{});overall=ap.get('overall',{});goalap=ap.get('per_class',{}).get('gawang',{});o=v['operating'];factor=name in ('480_single','480_multi','512_single','512_multi')
    rows.append({'dataset':g,'model':n,'path':name,'input':'480x640' if name.startswith('480') or name.startswith('predict') else '512x672','nms_iou':.45 if name=='predict_runtime' else .7,'operating_confidence_strict':.25,'AP50':overall.get('mAP50'),'AP50_95':overall.get('mAP50-95'),'goal_AP50':goalap.get('mAP50'),'goal_AP50_95':goalap.get('mAP50-95'),'precision':o['overall']['precision'],'recall':o['overall']['recall'],'F1_D11':o['overall']['F1'],'F1_mean_classes':o['overall']['F1_rerata_per_kelas'],'goal_TP':o['per_class']['gawang']['true_positives_at_iou50'],'negative_frames_FP':v['negative_frames_with_false_positive'],'factor_endpoints_valid':data['factor_endpoint_validation']['factor_interpretation_allowed'] if factor else ''})
 with (T/'T44_jalur_tunggal_op3_t38_t43.csv').open('x',newline='') as fp:
  w=csv.DictWriter(fp,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 def select(g,n,path):return next(x for x in rows if x['dataset']==g and x['model']==n and x['path']==path)
 tab=[]
 for g in ('t38_primary','t38_partial','t43_idle','t43_walking','t43_combined'):
  for n in N:
   a=select(g,n,'historical_valAP_predictPR');b=select(g,n,'predict_protocol');c=select(g,n,'predict_runtime');tab.append(f"| {g} | {N[n]} | {f(a['AP50_95'])} | {f(b['AP50_95'])} | {f(b['F1_D11'])} | {f(c['F1_D11'])} | {c['goal_TP']} | {c['negative_frames_FP']} |")
 ranking={}
 for g in ('t38_primary','t43_combined'):
  ranking[g]={path:[N[n] for n in sorted(N,key=lambda n:select(g,n,path)['AP50_95'],reverse=True)] for path in ['historical_valAP_predictPR','predict_protocol']}
 bad=[]
 for n,groups in d['models'].items():
  for g,z in groups.items():
   x=z['factor_endpoint_validation']
   if not x['factor_interpretation_allowed']:bad.append(f"{N[n]} / {g}: sel val Δ maksimum {x['val_max_abs_diff']:.6f}, sel predict Δ {x['predict_max_abs_diff']:.6f}")
 factors=[]
 for name in ('480_single','480_multi','512_single','512_multi'):
  z=select('t43_combined','teacher_fp32',name);factors.append(f"| {name} | {f(z['goal_AP50'])} | {f(z['goal_AP50_95'])} | {z['goal_TP']} | {f(z['F1_D11'])} |")
 txt='''# T44 — Evaluasi jalur tunggal OP3 T38/T43

Uji identitas 48 pemeriksaan lulus pada empat model: AP validator dan hitungan kelas pada jalur prediktor mereproduksi hasil beku. T38 memuat 200 frame berobjek, 60 negatif, dan 50 parsial yang dilaporkan terpisah. T43 memiliki 130 diam, 130 berjalan di tempat, termasuk masing-masing 30 negatif. Set dan label tidak digabung.

| Set | Model | mAP50–95 historis (val) | mAP50–95 predict | F1 predict protokol | F1 predict runtime | TP gawang runtime | Frame negatif FP runtime |
|---|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(tab)+'''\n
Historis menggunakan AP `model.val` dan P/R/F1 `model.predict`. Predict protokol memakai floor 0,001, NMS IoU 0,7; metrik P/R/F1 pada confidence >0,25. Predict runtime memakai confidence 0,25 dan NMS IoU 0,45. Seluruh F1 pada tabel memakai harmonik precision dan recall makro (D11). AP predict memakai `ap_per_class` dan pencocokan sekelas serakah berdasarkan IoU dari `scripts/verify_test_inference_path.py`; TP gawang pada IoU ≥0,5. T38 awal menerbitkan rerata F1 per kelas sebagai metrik tambahan. [CSV lengkap](T44_jalur_tunggal_op3_t38_t43.csv) memuat AP50, per kelas gawang, keempat sel faktor dan indikator validasi.

## Urutan mAP50–95

'''+ '\n'.join(f"- {g}: historis {' > '.join(x['historical_valAP_predictPR'])}; predict {' > '.join(x['predict_protocol'])}." for g,x in ranking.items())+'''\n
Urutan berbeda antarjalur; jangan memakai hasil ini untuk memilih ulang model.\n
## Faktor teacher pada T43 gabungan

Endpoint 512×672/multi-label dan 480×640/single-label teacher T43 sama dengan jalur val dan predict pada toleransi 1e-6.\n
| Bentuk dan NMS | AP50 gawang | AP50–95 gawang | TP gawang >0,25 | F1 D11 |
|---|---:|---:|---:|---:|
'''+ '\n'.join(factors)+'''\n
Pada teacher T43, perubahan bentuk/padding memiliki dampak jauh lebih besar daripada perubahan multi-label NMS pada empat sel tersebut. Ini merupakan temuan untuk set ini, bukan generalisasi lintas adegan. Endpoint 512×672 pada tiga student T38 tidak mereproduksi AP validator dalam toleransi; tabel faktornya disimpan tetapi **tidak ditafsirkan**. Selisih maksimum:\n
'''+ '\n'.join('- '+x for x in bad)+'''\n
Semua frame, label dan prediksi per frame tetap lokal.\n'''
 (T/'T44_jalur_tunggal_op3_t38_t43.md').write_text(txt)
 stage=list(csv.DictReader((R/'runtime_stages.csv').open()));outrows=[]
 for r in stage:outrows.append({'kind':'stage_'+r['scope'],'model':r['model'],'condition':r['condition'],'run_id':r['run_id'],'variant':'','stage':r['stage'],'frames':r['frames'],'mean_ms':r['mean_ms'],'median_ms':r['median_ms'],'p95_ms':r['p95_ms'],'cpu_percent_one_core':r['cpu_percent_one_core'],'cpu_percent_16_cores':r['cpu_percent_16_cores'],'cpu_ms_per_frame':'','feed_fps':'','torch_threads':'','interop_threads':'','opencv_threads':''})
 for (n,v),x in replay.items():
  outrows.append({'kind':'offline_replay','model':n,'condition':'offline','run_id':'','variant':v,'stage':'replay_end_to_end_ms','frames':x['frames'],**x['timings']['replay_end_to_end_ms'],'cpu_percent_one_core':x['cpu_percent_one_logical'],'cpu_percent_16_cores':x['cpu_percent_16_logical'],'cpu_ms_per_frame':x['cpu_ms_per_frame'],'feed_fps':x['input_rate_fps'],'torch_threads':x['torch_num_threads'],'interop_threads':x['torch_interop_threads'],'opencv_threads':x['opencv_num_threads']})
 with (T/'T45_rincian_latensi_dan_cpu_op3.csv').open('x',newline='') as fp:
  w=csv.DictWriter(fp,fieldnames=list(outrows[0]),lineterminator='\n');w.writeheader();w.writerows(outrows)
 with (T/'T45_cpu_thread_replay.csv').open('x',newline='') as fp:
  w=csv.DictWriter(fp,fieldnames=['model','variant','tid','name','cpu_seconds_sampled','present_at_start'],lineterminator='\n');w.writeheader()
  for (n,v),x in replay.items():
   for thread in x['thread_cpu_sampled']:w.writerow({'model':n,'variant':v,**thread})
 def getstage(n,c,s):return next(x for x in stage if x['scope']=='model_condition_pooled' and x['model']==n and x['condition']==c and x['stage']==s)
 group=[]
 for n in ('teacher','hybrid1337','sup1337','kd42'):
  for c in ('idle','walk'):
   x={k:getstage(n,c,k) for k in ('preprocess_ms','inference_ms','postprocess_ms','residual_ms','end_to_end_ms')};group.append('| '+n+' | '+c+' | '+' | '.join(f"{float(x[k]['mean_ms']):.2f}" for k in ('preprocess_ms','inference_ms','postprocess_ms','residual_ms','end_to_end_ms'))+f" | {float(x['end_to_end_ms']['cpu_percent_one_core']):.1f} | {float(x['end_to_end_ms']['cpu_percent_16_cores']):.1f} |")
 rep=[]
 for (n,v),x in replay.items():rep.append(f"| {N[n]} | {V[v]} | {x['cpu_ms_per_frame']:.1f} | {x['cpu_percent_one_logical']:.1f} | {x['cpu_percent_16_logical']:.1f} | {x['input_rate_fps']:.2f} | {x['opencv_num_threads']} | {x['max_thread_count_sampled']} |")
 initial=[]
 for p in sorted((R/'replay').glob('*/*/summary.json')):
  x=json.loads(p.read_text());initial.append(f"| {N[x['model']]} | {V[x['variant']]} | {x['torch_num_threads']} | {x['cpu_percent_one_logical']:.1f} | {x['cpu_ms_per_frame']:.1f} |")
 text='''# T45 — rincian latensi dan diagnosis CPU OP3

Sebanyak 24 run dibaca dari log mentah dengan jendela dan filter yang sama seperti `op3_runtime_audit_24`. Rata-rata end-to-end setiap run cocok T36 pada toleransi 1e-6. Angka tabel berikut adalah **rerata seluruh frame yang digabung** dari tiga run; karena jumlah frame berbeda, nilai dapat sedikit berbeda dari rerata tiga rerata run T37. Median dan P95 per run serta per kelompok tersedia di [CSV](T45_rincian_latensi_dan_cpu_op3.csv).

| Model | Kondisi | Preprocess ms | Inference ms | Postprocess ms | Sisa ms | End-to-end ms | CPU % satu CPU logis | CPU % dari 16 CPU logis |
|---|---|---:|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(group)+'''\n
Sisa dihitung **per frame** sebagai end-to-end dikurangi tiga tahap Ultralytics. Di `scripts/op3_pytorch_detector.py`, timer end-to-end mencakup konversi pesan kamera, pemanggilan model/tracker, pembentukan dan penerbitan deteksi, `result.plot()`, konversi dan penerbitan gambar preview, serta penulisan/flush CSV deteksi sebelum timer berhenti. Pencatatan baris runtime terjadi sesudah timer. Di predictor Ultralytics terpasang, callback tracker `on_predict_postprocess_end` dipanggil **di luar** timer `postprocess`; gambar preview dan penerbitan ROS juga berada di luar tiga tahap `result.speed`. Karena itu sisa bukan waktu tracker murni.

## Replay CPU offline — 4/2 thread Torch diverifikasi

Replay memberi 300 frame sebagai array yang dimuat sebelumnya; set T43 berisi 260 gambar, sehingga frame diulang secara deterministik dan 30 frame awal digunakan untuk warm-up. Delapan varian utama diikuti dua kontrol tambahan OpenBLAS 1 thread. Semua varian membuat preview `result.plot()`, tetapi tidak mencakup konversi atau publikasi ROS, kamera, maupun log deteksi. Laju input adalah throughput replay tanpa jeda terjadwal; bukan FPS live T36/T37. CPU per frame dan persentase CPU dihitung dari waktu CPU proses/waktu dinding. Satu pengulangan per varian, urutan serial; pengambilan sampel thread menambah sedikit overhead.

| Model | Varian | CPU ms/frame | CPU % satu CPU logis | CPU % dari 16 | Laju replay frame/detik | Thread OpenCV | Maksimum thread teramati |
|---|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rep)+'''\n
Rincian waktu CPU dan nama masing-masing thread ada pada [CSV thread](T45_cpu_thread_replay.csv). Pembacaan thread dilakukan sekali per frame; thread sangat singkat dapat terlewat sehingga jumlah waktu per thread adalah batas bawah. Hanya satu percobaan per varian: perbedaan menunjukkan asosiasi dalam replay, bukan estimasi kausal pasti untuk seluruh 24 run.

## Pengaturan thread dan percobaan awal

Seluruh metadata T36 mencatat Torch 4 intra-op, 2 inter-op, BoT-SORT `botsort.yaml`, tracking dan preview aktif; file terpasang menggunakan `gmc_method: sparseOptFlow`. Isi lengkap [salinan konfigurasi tracker](../../dokumentasi/2026-11-16/percobaan-41-jalur-tunggal-dan-runtime-op3/botsort_terpasang.yaml) disertakan untuk audit. Metadata node dicatat saat inisialisasi sebelum inferensi pertama. Pada replay awal, pemanggilan CPU pertama melalui `ultralytics.utils.torch_utils.select_device` mengubah intra-op menjadi 8 (`NUM_THREADS`); karena tidak memenuhi syarat replay 4/2, data berikut dipertahankan sebagai **percobaan awal**, bukan varian 4/2 di atas:

| Model | Varian awal | Torch intra-op setelah inisialisasi | CPU % satu CPU logis | CPU ms/frame |
|---|---|---:|---:|---:|
'''+ '\n'.join(initial)+'''\n
Replay utama mengembalikan intra-op menjadi 4 setelah inisialisasi backend dan memverifikasinya selama setiap frame. Ini menjelaskan mengapa metadata pra-inferensi saja belum membuktikan jumlah thread saat 24 run asli; tidak ada pengukuran langsung jumlah thread aktual pasca-inferensi pada run historis, sehingga penyebab pasti CPU historis tetap belum pasti. Konfigurasi OpenCV terukur sesudah impor Ultralytics adalah 1 thread, dan varian satu thread harus dibaca dengan fakta ini. Pada proses uji terpisah dengan urutan import seperti node, NumPy OpenBLAS default terukur 16 thread; kontrol tambahan membatasi OpenBLAS ke satu thread melalui environment sebelum impor dan mencatat nilai aktual satu. CPU replay tracking turun dibanding kontrol awal, menunjukkan OpenBLAS sebagai faktor besar dalam replay ini. Jumlah OpenBLAS aktual pada 24 run historis tidak direkam; hasil tidak membuktikan penyebab tunggal pada run historis.

Perbandingan latensi teacher dengan angka skripsi Ivan belum dapat disimpulkan: definisi waktu, perangkat, model, dan prosedur pada sumber Ivan belum diverifikasi. Tidak ada pengaturan robot atau hasil T36/T37 yang diubah.
'''
 (T/'T45_rincian_latensi_dan_cpu_op3.md').write_text(text)
 for lang in ('id','en'):
  fig,axes=plt.subplots(1,2,figsize=(12,5));xx=np.arange(4);width=.34
  for j,(group,name) in enumerate([('t38_primary','T38'),('t43_combined','T43')]):
   vals=[select(group,n,'predict_protocol')['AP50_95'] for n in N];bars=axes[0].bar(xx+(j-.5)*width,vals,width,label=name);axes[0].bar_label(bars,labels=[f'{v:.3f}' for v in vals],padding=3,fontsize=7)
  axes[0].set(title='mAP50–95 predict',ylabel='Nilai' if lang=='id' else 'Score',xticks=xx,xticklabels=list(N.values()),ylim=(0,1.13));axes[0].tick_params(axis='x',rotation=15);axes[0].legend()
  for j,n in enumerate(['teacher_fp32','hybrid_full_seed1337']):
   vals=[replay[(n,v)]['cpu_ms_per_frame'] for v in V];bars=axes[1].bar(np.arange(len(V))+(j-.5)*width,vals,width,label=N[n]);axes[1].bar_label(bars,labels=[f'{v:.0f}' for v in vals],padding=3,fontsize=7)
  axes[1].set(title='CPU replay 4/2 thread',ylabel='CPU ms/frame',xticks=np.arange(len(V)),xticklabels=['Track','No track','CV=1','No GMC','BLAS=1']);axes[1].legend();fig.suptitle('Perbandingan jalur dan replay CPU' if lang=='id' else 'Inference paths and CPU replay');fig.tight_layout();fig.savefig(DOC/'grafik'/f'jalur_dan_cpu_{lang}.png',dpi=300);plt.close(fig)
 notes='''## Batas interpretasi

T38 dan T43 adalah set eksploratif berbeda, bukan data independen lintas adegan. Prediktor dan validator memakai pengaturan preprocessing/NMS yang berbeda; pada tiga student T38 endpoint faktor val tidak cocok, sehingga pengaruh faktor pada bagian tersebut tidak ditafsirkan. Replay CPU dilakukan offline sekali per varian dengan data yang diulang, tanpa ROS; pengukuran per-thread bersifat tersampel. Metadata historis Torch 4/2 dicatat sebelum backend mulai dan bukan bukti pengukuran thread sepanjang run. Definisi waktu pada sumber Ivan belum diperiksa. Model maupun ambang tetap.\n'''
 (DOC/'README_ID.md').write_text('# Sesi OP3 offline — jalur tunggal dan runtime\n\n[T44 perbandingan jalur](../../../analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.md) · [T45 rincian latensi dan CPU](../../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md) · [Grafik](grafik/jalur_dan_cpu_id.png)\n\nUji identitas 48/48 lulus. Empat model diuji dengan jalur prediktor dan faktor padding/NMS; rincian kondisi dan validasi endpoint ada pada T44. Rincian seluruh 24 run dan delapan replay utama dan dua kontrol OpenBLAS 4/2 ada pada T45. Bobot, frame, label, log mentah dan prediksi per frame tetap lokal.\n\nTeacher FP32 yang diverifikasi: `/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt`, 5.481.875 byte, SHA-256 `e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c`. Alias `models_local/teacher_fp32_best.pt` tidak ada; bobot tidak disalin di OP3.\n\n'+notes+'\n## Perintah salin dari laptop\n\nAlamat Wi-Fi OP3 terdeteksi `192.168.1.147`; pastikan alamat masih sesuai. Jalankan dari laptop:\n\n```bash\nscp humanoid@192.168.1.147:/home/humanoid/ros2_jazzy/skripsi-yolo11-op3/artifacts/checkpoints/fp32/best.pt ./teacher_fp32_best.pt\nsha256sum teacher_fp32_best.pt\nssh dindarosyidah@labkc-l40-debian \'mkdir -p "$HOME/skripsi/skripsi-knowlage-destilation/models_local/teacher_utama"\'\nscp teacher_fp32_best.pt dindarosyidah@labkc-l40-debian:skripsi/skripsi-knowlage-destilation/models_local/teacher_utama/best.pt\nssh dindarosyidah@labkc-l40-debian \'sha256sum "$HOME/skripsi/skripsi-knowlage-destilation/models_local/teacher_utama/best.pt"\'\n```\n')
 (DOC/'README_EN.md').write_text('# Offline OP3 single-path and runtime analysis\n\n[T44 paths](../../../analisis_performa/tabel/T44_jalur_tunggal_op3_t38_t43.md) · [T45 stages and CPU](../../../analisis_performa/tabel/T45_rincian_latensi_dan_cpu_op3.md) · [Chart](grafik/jalur_dan_cpu_en.png)\n\nAll 48 baseline identity checks passed. Four models were assessed offline on frozen T38/T43 frames. Factor endpoint reproduction failed for the three student models on T38; those factor differences are reported without causal interpretation. 24 historical runs were rechecked and ten replay variants used 300 array inputs with torch 4/2 threads confirmed throughout. The 260-frame source was cycled; replay is not a replacement for live ROS performance.\n\nInitial replay exposed an Ultralytics CPU backend reset to 8 intra-op threads after metadata was recorded; the primary replay resets and verifies 4. Historical post-initialization thread counts were not measured, so an additional one-thread OpenBLAS control reduces replay CPU substantially. Actual OpenBLAS and post-initialization thread counts were not observed during historical runs, so their CPU cause cannot be established conclusively. Teacher weights, images, labels, raw logs and frame-level predictions remain local.\n')
 # Preserve historical markdown bytes while appending only links, as specifically requested.
 archived=[]
 for filename in ('T38_akurasi_op3_empat_model_260.md','T43_akurasi_op3_empat_model_260.md'):
  p=T/filename;dest=DOC/('arsip_sebelum_T44_'+filename);shutil.copy2(p,dest);archived.append({'original':str(p.relative_to(ROOT)),'sha256_before':sha(dest),'archive':str(dest.relative_to(ROOT))})
  with p.open('a') as fp:fp.write('\n## Perbandingan jalur tunggal\n\n[Evaluasi T44 jalur tunggal OP3](T44_jalur_tunggal_op3_t38_t43.md) membandingkan hasil historis dan jalur predict tanpa mengubah angka sebelumnya.\n')
 p=ROOT/'analisis_performa/INDEKS.md';old=p.read_text();p.write_text(old+'\n- [T44 — jalur tunggal OP3](tabel/T44_jalur_tunggal_op3_t38_t43.md) dan [T45 — rincian latensi dan CPU](tabel/T45_rincian_latensi_dan_cpu_op3.md).\n')
 (DOC/'historical_markdown_archives.json').write_text(json.dumps({'reason':'append links only; pre-existing historical manifests retain hashes of archived prior bytes','files':archived},indent=2)+'\n')
 allfiles=[I/'identity.json',C/'comparison.json',R/'runtime_stages_manifest.json',R/'runtime_stages.csv',ROOT/'scripts/op3_pytorch_detector.py',ROOT/'ros2_packages/op3_single_path_eval/identity.py',ROOT/'ros2_packages/op3_single_path_eval/compare_paths.py',ROOT/'ros2_packages/op3_single_path_eval/runtime_stages.py',ROOT/'ros2_packages/op3_single_path_eval/replay.py',Path(__file__),T/'T38_akurasi_op3_empat_model_260.md',T/'T43_akurasi_op3_empat_model_260.md',T/'T44_jalur_tunggal_op3_t38_t43.csv',T/'T44_jalur_tunggal_op3_t38_t43.md',T/'T45_rincian_latensi_dan_cpu_op3.csv',T/'T45_rincian_latensi_dan_cpu_op3.md',T/'T45_cpu_thread_replay.csv',ROOT/'analisis_performa/INDEKS.md']+[p for p in DOC.rglob('*') if p.is_file()]+[R/'replay_v2'/n/v/'summary.json' for n,v in replay]+list((R/'replay').glob('*/*/summary.json'))+[R/'replay_initial_script.py',R/'replay_v2_script.py',R/'thread_probe.json',ROOT/'ros2_packages/op3_single_path_eval/probe_threads.py']
 (DOC/'manifest_hasil_sha256.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'status':'complete_with_factor_endpoint_limitations','source_prompt_git_revision':d['reference_git_revision'],'source_reference_script_sha256':d['reference_script_sha256'],'teacher_sha256':'e05b2b21f7faa68f65671f0aaae37ad962aa5e25c6b8b26853fd0b389d420b8c','raw_frames_labels_predictions_logs_remain_local':True,'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(allfiles))}},indent=2)+'\n')
 print('FINISHED T44 T45',DOC,flush=True)
if __name__=='__main__':main()
