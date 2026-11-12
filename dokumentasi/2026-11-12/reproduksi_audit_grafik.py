import importlib.util, json, hashlib, tempfile, sys
from pathlib import Path
from PIL import Image, ImageChops
root=Path.cwd(); spec=importlib.util.spec_from_file_location('grafik',root/'scripts/build_grafik_garis_model_20261111.py'); g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
manifest=json.loads((g.OUT/'manifest_grafik_garis_akurasi.json').read_text()); tmp=Path(tempfile.mkdtemp(prefix='op3_audit_grafik_')); rows=[]
def save(fig,name,folder):
 out=tmp/folder/name;out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,facecolor=g.SURFACE,dpi=200);g.plt.close(fig)
 orig=g.OUT/folder/name;a=Image.open(orig).convert('RGB');b=Image.open(out).convert('RGB'); diff=ImageChops.difference(a,b); pix=diff.getbbox(); rel=orig.relative_to(root).as_posix(); h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 rows.append({'file':rel,'manifest_sha256':manifest['outputs_sha256'][rel],'git_file_sha256':h(orig),'recreated_sha256':h(out),'pixels_identical':pix is None,'dimensions_original':a.size,'dimensions_recreated':b.size})
g.save=save
curves={f:{s:g.load_epochs(r) for s,r in zip(g.SEEDS,g.MODELS[f]['runs'])} for f in ('supervised','kd_murni','kd_hybrid')};t11=g.load_t11()
for lang in ('id','en'):
 for folder in curves: g.accuracy_model(folder,lang,curves[folder])
 for folder in g.ORDER:g.sweep_model(folder,lang,t11[g.MODELS[folder]['t11']])
 g.accuracy_combined(lang,curves);g.sweep_combined(lang,t11)
report={'matplotlib':g.matplotlib.__version__,'temporary_directory':str(tmp),'count':len(rows),'same_pixel_count':sum(r['pixels_identical'] for r in rows),'images':rows}
Path('/tmp/op3_audit_grafik_20261112.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({k:v for k,v in report.items() if k!='images'}))
