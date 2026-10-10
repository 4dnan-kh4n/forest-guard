"""Check variable-window verification without weakening existing real-crop checks."""
import json
import tempfile
import zipfile
import hashlib
from pathlib import Path

from register_research_ui import ROOT,BUNDLE
from verify_research_bundle import verify

assert verify(BUNDLE)['integrity']=='PASS'
with zipfile.ZipFile(BUNDLE) as saved:
    original={name:saved.read(name) for name in saved.namelist()}
with tempfile.TemporaryDirectory(prefix='windows_check_',dir=ROOT/'data/phase2') as temporary:
    def altered(change):
        members=dict(original);report=json.loads(members['research_report.json']);change(report)
        members['research_report.json']=json.dumps(report).encode()
        checks=json.loads(members['checksums.json']);checks['research_report.json']={'sha256':hashlib.sha256(members['research_report.json']).hexdigest(),'bytes':len(members['research_report.json'])}
        members['checksums.json']=json.dumps(checks).encode()
        path=Path(temporary)/'test.zip'
        with zipfile.ZipFile(path,'w') as saved:
            for name,data in members.items():saved.writestr(name,data)
        return path
    two=altered(lambda r:r.update(season_windows=[w for w in r['season_windows'] if w[0]!='wet'],status='COMPLETE_DATA_SCREENING'))
    assert verify(two)['status']=='COMPLETE_DATA_SCREENING'
    for change in [lambda r:r.update(season_windows=[]),
                   lambda r:r.update(season_windows=r['season_windows']+r['season_windows'][:1]),
                   lambda r:r['season_windows'].__setitem__(0,['dry','2024-01-01T00:00:00Z/2024-12-31T23:59:59Z'])]:
        try:verify(altered(change))
        except ValueError:pass
        else:raise AssertionError('Invalid observation window accepted')
for name in ['notebooks/11_same_season_observation.ipynb','data/phase2/same_season_2024_v1/private_run.ipynb']:
    notebook=json.loads((ROOT/name).read_text())
    for cell in notebook['cells']:
        if cell['cell_type']=='code':
            assert cell['execution_count'] is None and not cell['outputs'];compile(''.join(cell['source']),name,'exec')
summary={'status':'PASS','existing_research_bundle_unchanged':True,'declared_window_completion_checked':True,
         'empty_duplicate_wrong_date_windows_rejected':True,'cloud_notebook_syntax_checked':True,
         'new_observation_acquired':False,'forest_accuracy_measured':False}
(ROOT/'data/phase2/observation_window_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
