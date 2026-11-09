"""Matriks deteksi T38: pencocokan kelas T38, lalu pasangan salah kelas tersisa."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from op3_camera_eval.evaluate import CLASSES, iou_xyxy, read_labels, sha256
from op3_multi_session_eval.evaluate import score_frame

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / 'runs/op3_multi_session_eval/20261105_empat_model_primary260_v1'
TABLE = ROOT / 'analisis_performa/tabel/T38_akurasi_op3_empat_model_260.csv'
RUNTIME = ROOT / 'analisis_performa/tabel/T37_runtime_live_setara_ringkasan.csv'
TEST05 = ROOT / 'analisis_performa/tabel/T05_akurasi_test_keseluruhan.csv'
TEST30 = ROOT / 'analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.csv'
TRAINING = ROOT / 'analisis_performa/tabel/T35_waktu_training_dan_pengujian.csv'
T38_AUDIT = ROOT / 'dokumentasi/2026-11-05/percobaan-37-evaluasi-t38-empat-model/audit_t38.json'
MODELS = {
    'teacher_fp32': ('teacher_yolo11n', 'Teacher YOLO11n', 'teacher', 'teacher'),
    'hybrid_full_seed1337': ('kd_hybrid', 'KD Hybrid full seed 1337', 'hybrid1337', 'hybrid1337'),
    'supervised_seed1337': ('supervised', 'Supervised seed 1337', 'sup1337', 'sup1337'),
    'kd_seed42': ('kd_murni', 'KD Murni seed 42', 'kd42', 'kd42'),
}
MEDIA = {
    'teacher_fp32': 'teacher_berjalan_u1_sesudah.png',
    'hybrid_full_seed1337': 'hybrid_berjalan_u3_sesudah.png',
    'supervised_seed1337': 'supervised_berjalan_u1_sesudah.png',
    'kd_seed42': 'kd_murni_berjalan_u3_sesudah.png',
}


def rows(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def xyxy(gt):
    _, x, y, w, h = gt
    return [(x-w/2)*640, (y-h/2)*480, (x+w/2)*640, (y+h/2)*480]


def frame_matrix(gt, detections, threshold=.5):
    """Tetapkan dulu TP sekelas seperti T38, lalu pasangkan sisa lintas kelas berdasarkan IoU."""
    mat = np.zeros((4, 4), dtype=np.int64)
    ordered = sorted(detections, key=lambda d: d['confidence'], reverse=True)
    used_gt = set()
    leftover = []
    for det in ordered:
        if det['class_id'] not in (0, 1, 2) or not float(det['confidence']) > .25:
            raise ValueError('Prediksi di luar kelas/ambang T38')
        candidates = [(iou_xyxy(det['xyxy'], xyxy(item)), idx) for idx, item in enumerate(gt)
                      if item[0] == det['class_id'] and idx not in used_gt]
        if candidates and max(candidates)[0] >= threshold:
            idx = max(candidates)[1]
            used_gt.add(idx)
            mat[gt[idx][0], det['class_id']] += 1
        else:
            leftover.append(det)
    candidates = []
    for i, item in enumerate(gt):
        if i in used_gt:
            continue
        for j, det in enumerate(leftover):
            if item[0] == det['class_id']:
                continue
            overlap = iou_xyxy(det['xyxy'], xyxy(item))
            if overlap >= threshold:
                candidates.append((overlap, i, j))
    used_det = set()
    for _, i, j in sorted(candidates, reverse=True):
        if i not in used_gt and j not in used_det:
            mat[gt[i][0], leftover[j]['class_id']] += 1
            used_gt.add(i)
            used_det.add(j)
    for i, item in enumerate(gt):
        if i not in used_gt:
            mat[item[0], 3] += 1
    for j, det in enumerate(leftover):
        if j not in used_det:
            mat[3, det['class_id']] += 1
    return mat


def matrices(manifest, model, source, expected):
    frames = manifest['frames']; seen = set(); matrix = np.zeros((4, 4), dtype=np.int64); negative_fp_frames = 0
    for line in source.read_text(encoding='utf-8').splitlines():
        record = json.loads(line); key = record['key']
        if key in seen or key not in frames or record['role'] != frames[key]['role']:
            raise ValueError(f'Duplikasi atau identitas frame tidak sesuai: {key}')
        seen.add(key)
        if record['role'] not in ('primary', 'negative'):
            continue
        item = frames[key]; label = Path(item['label']); image = Path(item['image'])
        if sha256(label) != item['label_sha256'] or sha256(image) != item['image_sha256']:
            raise ValueError(f'Hash label atau gambar berubah: {key}')
        gt = read_labels(label)
        if record['role'] == 'negative' and gt:
            raise ValueError(f'Frame negatif memiliki label: {key}')
        if record['role'] == 'negative' and record['detections']:
            negative_fp_frames += 1
        counts, details = score_frame(gt, record['detections'])
        if counts != record['counts'] or [d['matched'] for d in details] != [d['matched'] for d in sorted(record['detections'], key=lambda d:d['confidence'], reverse=True)]:
            raise ValueError(f'Pencocokan T38 tidak cocok: {key}')
        matrix += frame_matrix(gt, record['detections'])
    if seen != set(frames):
        raise ValueError(f'Inventaris prediksi {model} tidak sama dengan manifest')
    if int(matrix[:3, :].sum()) != 400 or list(matrix[:3, :].sum(axis=1)) != [160, 80, 160]:
        raise ValueError(f'Jumlah ground truth bukan 400: {model}')
    if negative_fp_frames != int(expected[(model, 'macro')]['negative_fp_frames']):
        raise ValueError(f'Frame negatif dengan FP tidak cocok T38: {model}')
    for i, name in enumerate(CLASSES):
        e = expected[(model, name)]
        tp = int(matrix[i, i]); fn = int(matrix[i, :].sum() - tp); fp = int(matrix[:, i].sum() - tp)
        if (tp, fp, fn) != (int(e['TP']), int(e['FP']), int(e['FN'])):
            raise ValueError(f'Matriks tidak cocok dengan TP/FP/FN T38: {model}/{name}')
    return matrix


def text(lang, id_text, en_text):
    return id_text if lang == 'id' else en_text


def plot_matrix(ax, matrix, lang, normalized, title, v_max):
    value = matrix.astype(float)
    if normalized:
        value[:3] = 100 * value[:3] / value[:3].sum(axis=1, keepdims=True)
        value[3, :] = np.nan
    else:
        value[3, 3] = np.nan
    cmap = plt.get_cmap('Blues').copy(); cmap.set_bad('#eef1f4')
    img = ax.imshow(value, cmap=cmap, vmin=0, vmax=100 if normalized else v_max)
    ticks = [text(lang,'Bola','Ball'), text(lang,'Gawang','Goal'), 'Robot', text(lang,'Latar (FP)','Background (FP)')]
    xticks = ticks[:3] + [text(lang,'Terlewat (FN)','Missed (FN)')]
    ax.set_xticks(range(4), xticks, rotation=20, ha='right', fontsize=9)
    ax.set_yticks(range(4), ticks, fontsize=9)
    ax.set_xlabel(text(lang,'Prediksi model','Model prediction'), fontsize=10)
    ax.set_ylabel(text(lang,'Label acuan','Reference label'), fontsize=10)
    ax.set_title(title, fontsize=12, weight='bold', pad=12)
    ax.set_xticks(np.arange(-.5,4,1),minor=True); ax.set_yticks(np.arange(-.5,4,1),minor=True)
    ax.grid(which='minor',color='white',linestyle='-',linewidth=2); ax.tick_params(which='minor',bottom=False,left=False)
    for y in range(4):
        for x in range(4):
            val=value[y,x]
            label='—' if np.isnan(val) else (f'{val:.1f}%' if normalized else str(int(val)))
            color='white' if not np.isnan(val) and val > (.56*(100 if normalized else v_max)) else '#1a2a3e'
            ax.text(x,y,label,ha='center',va='center',fontsize=11,fontweight='bold',color=color)
    return img


def plot_one(matrix, output, lang, normalized, title, vmax):
    fig, ax = plt.subplots(figsize=(9,7.5))
    img=plot_matrix(ax,matrix,lang,normalized,title,vmax)
    fig.colorbar(img,ax=ax,fraction=.046,pad=.04,label=text(lang,'Persen per kelas acuan','Percent per reference class') if normalized else text(lang,'Jumlah kotak','Box count'))
    fig.suptitle(text(lang,'Confusion matrix deteksi kamera OP3','OP3 camera detection confusion matrix'),fontsize=16,weight='bold',y=.98)
    foot=text(lang,'260 frame · 400 kotak acuan · confidence > 0,25 · IoU ≥ 0,5\nPencocokan sekelas dahulu, lalu salah kelas; salah kelas dihitung FP dan FN.\nLatar = prediksi tidak cocok; latar–latar bukan true negative.',
              '260 frames · 400 reference boxes · confidence > 0.25 · IoU ≥ 0.5\nSame-class matches first, then cross-class; a wrong class counts as FP and FN.\nBackground = unmatched predictions; background–background is not a true-negative count.')
    if normalized: foot += '\n' + text(lang,'Baris latar tidak dinormalisasi; lihat matriks jumlah untuk false positive.', 'Background row is not normalized; see count matrix for false positives.')
    fig.text(.06,.025,foot,fontsize=8,color='#43536b'); fig.subplots_adjust(left=.20,right=.91,bottom=.24,top=.86)
    fig.savefig(output,dpi=240,facecolor='white');plt.close(fig)


def plot_combined(all_matrices, output, lang, normalized, vmax):
    fig, axes=plt.subplots(2,2,figsize=(13,11))
    for ax,(model,matrix) in zip(axes.flat,all_matrices.items()):
        title=MODELS[model][1] if lang=='id' else MODELS[model][1].replace('KD Murni','Pure KD')
        img=plot_matrix(ax,matrix,lang,normalized,title,vmax)
    fig.suptitle(text(lang,'Confusion matrix empat model — 260 frame OP3','Four-model confusion matrices — 260 OP3 frames'),fontsize=18,weight='bold',y=.98)
    note=text(lang,'Skala warna sama untuk semua panel. Baris = label; kolom = prediksi. Confidence > 0,25; IoU ≥ 0,5.\nPencocokan sekelas dahulu, lalu salah kelas. Salah kelas dihitung sebagai FP dan FN.\nLatar = prediksi tidak cocok; latar–latar bukan true negative.',
              'Shared color scale across panels. Rows = reference; columns = prediction. Confidence > 0.25; IoU ≥ 0.5.\nSame-class matches first, then cross-class. A wrong class counts as FP and FN.\nBackground = unmatched predictions; background–background is not a true-negative count.')
    if normalized: note += '\n'+text(lang,'Baris latar tidak dinormalisasi; lihat matriks jumlah untuk false positive.','Background row is not normalized; see count matrix for false positives.')
    fig.text(.07,.02,note,fontsize=8.5,color='#43536b')
    fig.subplots_adjust(left=.13,right=.9,bottom=.16,top=.9,wspace=.50,hspace=.60)
    cax=fig.add_axes([.925,.22,.016,.58]); fig.colorbar(img,cax=cax,label=text(lang,'Persen per kelas acuan','Percent per reference class') if normalized else text(lang,'Jumlah kotak','Box count'))
    fig.savefig(output,dpi=240,facecolor='white');plt.close(fig)


def relative(source, destination):
    return os.path.relpath(destination,source).replace(os.sep,'/')


def model_readme(folder, model, mat, table_rows, runtime_rows, checkpoint, test05, test30, training):
    directory, title, metric_key, graph_key = MODELS[model]
    macro=table_rows[(model,'macro')]
    runtime={r['condition']:r for r in runtime_rows if r['model']==metric_key}
    viz=ROOT/'dokumentasi/2026-11-09/visualisasi-tambahan-empat-model'
    overview=relative(folder,viz/'grafik-final'/f'08_ringkasan_{graph_key}_id.png')
    overview_en=relative(folder,viz/'grafik-final'/f'08_ringkasan_{graph_key}_en.png')
    timeline=relative(folder,viz/'grafik-final'/f'09_garis_waktu_{graph_key}_id.png')
    timeline_en=relative(folder,viz/'grafik-final'/f'09_garis_waktu_{graph_key}_en.png')
    screenshot=relative(folder,viz/'media'/MEDIA[model]); globaldoc=relative(folder,ROOT/'analisis_performa/tabel/T38_akurasi_op3_empat_model_260.md')
    links=f'[Ringkasan ID]({overview}) · [Overview EN]({overview_en}) · [Garis waktu ID]({timeline}) · [Timeline EN]({timeline_en}) · [Screenshot contoh]({screenshot})'
    if model=='supervised_seed1337': links+=f" · [Video deteksi 10 detik]({relative(folder,viz/'media/supervised_deteksi_tracking_10detik.mp4')})"
    def cell(k): return f'{float(macro[k]):.4f}'
    textout=f'''# {title}

Dokumentasi terindeks untuk checkpoint `{model}`. SHA-256 checkpoint: `{checkpoint}`. Sumber tabel dan run: [T38]({globaldoc}) dan T36/T37. Tidak ada pengujian baru dalam pembuatan folder ini.

## Akurasi dataset TEST

Evaluasi pada 592 gambar dataset TEST, berbeda dari frame kamera OP3. Nilai teacher memakai satu checkpoint; tiga model student memakai **rerata tiga seed** (42, 1337, 2025), bukan hanya checkpoint OP3 yang menjadi judul halaman ini. F1 dihitung dari precision dan recall makro. Sumber: [T05]({relative(folder,ROOT/'analisis_performa/tabel/T05_akurasi_test_keseluruhan.md')}) dan [T30]({relative(folder,ROOT/'analisis_performa/tabel/T30_kd_hybrid_test_berpasangan.md')}).

| mAP50 | mAP50–95 | Precision | Recall | F1 dari P/R makro |
|---:|---:|---:|---:|---:|
'''
    if model=='hybrid_full_seed1337':
        metrics={r['metric']:float(r['hybrid_full']) for r in test30 if r['row_type']=='mean_sd' and r['scope']=='overall'}
    else:
        method={'teacher_fp32':'Teacher','supervised_seed1337':'Supervised student','kd_seed42':'Pure KD'}[model]
        by_metric={r['metric']:float(r['mean']) for r in test05 if r['method']==method}
        metrics={k:by_metric['test_'+('mAP50_95' if k=='mAP50-95' else k)] for k in ('mAP50','mAP50-95','precision','recall','F1')}
    textout += '| ' + ' | '.join(f'{metrics[k]:.4f}' for k in ('mAP50','mAP50-95','precision','recall','F1')) + ' |\n'
    textout += f'''
TEST sudah pernah digunakan sebelumnya, dan hasilnya tidak sama dengan hasil kamera OP3 di bawah. Tiga seed memberikan ringkasan deskriptif, sementara teacher hanya satu checkpoint.

## Confusion matrix kamera OP3

- [Jumlah kotak — Indonesia](confusion_matrix_{directory}_jumlah_id.png) · [English](confusion_matrix_{directory}_jumlah_en.png)
- [Persen per kelas acuan — Indonesia](confusion_matrix_{directory}_persen_id.png) · [English](confusion_matrix_{directory}_persen_en.png)
- [Data jumlah CSV](confusion_matrix_{directory}.csv) · [Data persen CSV](confusion_matrix_{directory}_persen.csv) · [Metadata JSON](confusion_matrix_{directory}.json)

Data T38: 260 frame (200 berobjek + 60 negatif), 400 kotak acuan, confidence >0,25, IoU ≥0,5. Baris adalah label acuan; kolom adalah prediksi. Baris latar menunjukkan prediksi tanpa pasangan, termasuk duplikasi atau kotak yang lokasinya tidak mencapai IoU 0,5; tidak berarti semuanya berasal dari frame kosong. Kolom terlewat menunjukkan label tanpa pasangan. Pasangan sekelas ditetapkan sesuai T38, lalu sisa prediksi dan label berbeda kelas dipasangkan berdasarkan IoU. **FP suatu kelas adalah isi kolom kelas selain diagonal; FN adalah isi baris kelas selain diagonal**, sehingga salah kelas turut dihitung sebagai FP dan FN. Persentase hanya dinormalisasi pada tiga baris label, bukan baris latar. Sel latar–latar kosong karena true negative tidak terdefinisi.

| mAP50 | mAP50–95 | Precision makro | Recall makro | F1 makro per kelas | Frame negatif dengan FP |
|---:|---:|---:|---:|---:|---:|
| {cell('mAP50')} | {cell('mAP50-95')} | {cell('precision')} | {cell('recall')} | {cell('F1')} | {macro['negative_fp_frames']}/60 |

Ini evaluasi retrospektif satu rangkaian; label awal dibantu prediksi KD murni sebelum ditinjau manusia. Hasil bukan bukti generalisasi lintas adegan. Angka pada tabel ini berbeda lingkupnya dari TEST dan metrik runtime live.

## Runtime OP3

Rata-rata ± SD tiga run; sumber T37. CPU adalah persentase satu CPU logis, RSS adalah RAM proses detektor.

| Kondisi | Latensi (ms) | FPS | CPU (% satu CPU logis) | RSS (MiB) |
|---|---:|---:|---:|---:|
'''
    for condition,label in [('idle','Diam'),('walk','Berjalan')]:
        r=runtime[condition]
        def pair(k,sd): return f"{float(r[k]):.2f} ± {float(r[sd]):.2f}"
        textout += f"| {label} | {pair('latency_mean_ms_mean','latency_mean_ms_sd_sample')} | {pair('fps_mean','fps_sd_sample')} | {pair('cpu_percent_one_core_mean','cpu_percent_one_core_sd_sample')} | {pair('rss_mib_mean','rss_mib_sd_sample')} |\n"
    textout += f'''
Run dilakukan pada sesi berbeda dan digunakan sebagai analisis deskriptif. Rincian pengukuran serta batasnya ada pada [audit runtime]({relative(folder,ROOT/'dokumentasi/2026-11-03/percobaan-36-audit-runtime-24-run/README_ID.md')}).

## Waktu training

'''
    if model=='teacher_fp32':
        textout += 'Durasi training teacher utama dengan provenance setara tidak tersedia. Waktu teacher yang dilatih ulang dalam T42 adalah eksperimen berbeda dan tidak menggantikan angka ini.\n'
    else:
        prefix={'hybrid_full_seed1337':'hybrid_full','supervised_seed1337':'supervised','kd_seed42':'kd'}[model]
        selected={r['model_or_group']:r for r in training if r['phase']=='training'}
        textout += '| Seed | Durasi training (jam) |\n|---:|---:|\n'
        for seed in (42,1337,2025):
            r=selected[f'{prefix}_seed{seed}'];textout+=f"| {seed} | {float(r['duration_seconds'])/3600:.3f} |\n"
        textout += '\nServer dipakai bersama dan periode pengujian berbeda.'
        if model=='supervised_seed1337':
            textout += ' Durasi seed 1337 menjumlahkan dua segmen dan mengecualikan jeda interupsi.'
        textout += '\n'
    textout += f'''
Sumber dan rincian pengukuran waktu: [T35]({relative(folder,ROOT/'analisis_performa/tabel/T35_waktu_training_dan_pengujian.md')}).

## Grafik dan contoh kamera

{links}

Screenshot berasal dari frame sesudah jendela pengukuran berjalan, bukan bukti gerak dari gambar tunggal. Video, bila ada, adalah sesi Supervised lain dengan kondisi fisik `unknown`. [Indeks empat model]({relative(folder,folder.parent/'README.md')}).
'''
    (folder/'README.md').write_text(textout,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'dokumentasi/model')
    args=parser.parse_args(); out=args.output.resolve()
    manifest_path=RESULTS/'input_manifest.json'; raw_results=RESULTS/'results.json'
    manifest=json.loads(manifest_path.read_text()); audit=json.loads(T38_AUDIT.read_text())
    if sha256(manifest_path)!=audit['input_manifest_sha256'] or sha256(raw_results)!=audit['results_sha256'] or sha256(TABLE)!=audit['csv_sha256']:
        raise ValueError('Hash input T38 tidak cocok dengan audit')
    roles=[x['role'] for x in manifest['frames'].values()]
    if {x:roles.count(x) for x in ('primary','negative','partial')}!={'primary':200,'negative':60,'partial':50}:
        raise ValueError('Komposisi dataset berbeda dari T38')
    for session in manifest['sessions'].values():
        review_log = Path(session['path']) / 'labels_reviewed/review_log.jsonl'
        if sha256(review_log) != session['review_log_sha256']:
            raise ValueError(f'Hash log peninjauan berbeda: {review_log}')
    expected={(r['model'],r['class']):r for r in rows(TABLE)}; runtime=rows(RUNTIME)
    test05,test30,training=rows(TEST05),rows(TEST30),rows(TRAINING)
    result={}; source_files=[manifest_path,raw_results,TABLE,RUNTIME,T38_AUDIT,TEST05,TEST30,TRAINING]
    for model in MODELS:
        source=RESULTS/f'per_frame_{model}.jsonl';source_files.append(source)
        result[model]=matrices(manifest,model,source,expected)
    out.mkdir(parents=True,exist_ok=False)
    combined=out/'gabungan';combined.mkdir()
    vmax=max(int(np.max(v)) for v in result.values())
    output_hashes={}
    for model,matrix in result.items():
        directory,title,_,_=MODELS[model]; folder=out/directory;folder.mkdir()
        with (folder/f'confusion_matrix_{directory}.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.writer(f,lineterminator='\n'); writer.writerow(['label_acuan\\prediksi','ball','gawang','robot','terlewat_FN'])
            for i,(name,row) in enumerate(zip(['ball','gawang','robot','latar_FP'],matrix)):
                writer.writerow([name,*row[:3],'' if i==3 else row[3]])
        with (folder/f'confusion_matrix_{directory}_persen.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.writer(f,lineterminator='\n');writer.writerow(['label_acuan\\prediksi','ball','gawang','robot','terlewat_FN'])
            for i,(name,row) in enumerate(zip(['ball','gawang','robot','latar_FP'],matrix)):
                writer.writerow([name,*(['']*4 if i==3 else [f'{100*value/sum(row):.4f}' for value in row])])
        metadata={'model':model,'frames_main':260,'frames_targets':200,'frames_negative':60,'ground_truth_boxes':400,
                  'confidence_strictly_above':.25,'matching_iou_minimum':.5,'nms_iou':.7,
                  'axes':'baris label acuan; kolom prediksi','class_matching':'sekelas berdasar urutan confidence seperti T38, lalu lintas kelas IoU terbesar pada sisa',
                  'matrix_counts':[list(map(int,row)) for row in matrix[:3]] + [[*map(int,matrix[3,:3]),None]],
                  'bottom_right':'tidak terdefinisi; bukan true negative','checkpoint_sha256':audit['checkpoints'][model]['sha256']}
        (folder/f'confusion_matrix_{directory}.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        for lang in ('id','en'):
            for normalized,suffix in ((False,'jumlah'),(True,'persen')):
                plot_one(matrix,folder/f'confusion_matrix_{directory}_{suffix}_{lang}.png',lang,normalized,title.replace('KD Murni','Pure KD') if lang=='en' else title,vmax)
        model_readme(folder,model,matrix,expected,runtime,audit['checkpoints'][model]['sha256'],test05,test30,training)
    for lang in ('id','en'):
        for normalized,suffix in ((False,'jumlah'),(True,'persen')):
            plot_combined(result,combined/f'confusion_matrix_empat_model_{suffix}_{lang}.png',lang,normalized,vmax)
    for normalized,suffix in ((False,'jumlah'),(True,'persen')):
        with (combined/f'confusion_matrix_empat_model_{suffix}.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.writer(f,lineterminator='\n');writer.writerow(['model','label_acuan\\prediksi','ball','gawang','robot','terlewat_FN'])
            for model,matrix in result.items():
                for i,(label,row) in enumerate(zip(['ball','gawang','robot','latar_FP'],matrix)):
                    values=(['']*4 if i==3 else [f'{100*value/sum(row):.4f}' for value in row]) if normalized else [*row[:3],'' if i==3 else row[3]]
                    writer.writerow([model,label,*values])
    sources={str(p.relative_to(ROOT)):sha256(p) for p in source_files}
    outputs={str(p.relative_to(out)):sha256(p) for p in out.rglob('*') if p.is_file()}
    record={'generator':str(Path(__file__).resolve().relative_to(ROOT)),'generator_sha256':sha256(Path(__file__).resolve()),
            'shared_packages':['op3_camera_eval','op3_multi_session_eval'],'sources_sha256':sources,'files_sha256':outputs}
    (out/'manifest_confusion_matrix.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({m:v.tolist() for m,v in result.items()},indent=2))


if __name__=='__main__':main()
