"""Prepare public/private bounded 2022–2026 imagery notebooks without local acquisition."""
import base64
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
model=ROOT/'data/phase3/weak_december_run_v1/forestguard_weak_proxy_run1.zip'
sha='8bf0858faaee969b35e003c466de19ab1767a96c5c8ed9098cb8010f13d3a6b8'
raw=model.read_bytes()
if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Unexpected model artifact')
study=json.loads((ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes())
sources=[('pipeline',(ROOT/'cloud/inspect_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]),
         ('features',(ROOT/'cloud/research_features.py').read_text(encoding='utf-8')),
         ('research',(ROOT/'cloud/multiseason_research.py').read_text(encoding='utf-8')),
         ('annual',(ROOT/'cloud/annual_observations.py').read_text(encoding='utf-8'))]
execute="SEASONS=[(str(year),f'{year}-09-20T00:00:00Z/{year}-10-09T23:59:59Z') for year in range(2022,2027)]\nSCL_SCREEN_LIMIT=6\nPROCESS_LIMIT=2\nMIN_FEATURE_COVERAGE=.5\nannual_output=annual_run(STUDY,run,research_features,MODEL_BYTES,MODEL_SHA,run_research)\n"
for path,boundary,embedded in [(ROOT/'notebooks/13_annual_observations.ipynb',None,None),
                              (ROOT/'data/annual/2022_2026_v1/private_run.ipynb',study,base64.b64encode(raw).decode())]:
    cells=[{'id':'purpose','cell_type':'markdown','metadata':{},'source':[
        '# ForestGuard annual satellite observations: 2022–2026\n',
        'Private Kaggle CPU, Accelerator None, Internet On. Existing NumPy, Rasterio, Pillow, scikit-learn and joblib only. No training or paid services.\n',
        'Same September 20–October 9 search window for all years; 2026 is a year-to-date observation. User-confirmed compartment 279 only.\n',
        'At most 6 small quality windows and 2 processing candidates per year; 20 m grid, maximum 256×256 crop, 16-row inference batches. At least 250 MiB cloud disk.\n',
        'Apply product calibration, cloud/shadow/missing masks and original grid checks. Annual viewing accepts at least 50% clear feature coverage, reports the measured fraction and excludes all invalid pixels. This is not a training-data acceptance target. Failed years remain missing.\n',
        'Our trusted historical-map proxy is embedded in the private copy. If runtime versions differ, imagery still exports but proxy percentages stay unavailable.\n',
        'Tree-cover class extent is not canopy density or confirmed deforestation. Preserve the ZIP before ending the cloud session.\n']}]
    setup='STUDY='+repr(boundary)+'\nMODEL_SHA='+repr(sha)+'\nMODEL_BYTES=base64.b64decode('+repr(embedded)+') if '+repr(embedded is not None)+' else b""\n'
    for key,code in [('imports','import base64\n'),('study',setup),*sources,('execute',execute)]:
        compile(code,str(path),'exec')
        cells.append({'id':key,'cell_type':'code','metadata':{},'source':code.splitlines(keepends=True),'execution_count':None,'outputs':[]})
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}},'cells':cells},indent=2)+'\n').encode())
print('PASS: annual public/private notebook sources compile; acquisition and inference remain cloud-only.')
