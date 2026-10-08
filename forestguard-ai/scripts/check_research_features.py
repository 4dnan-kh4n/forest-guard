"""Numerical feature/quality checks only; synthetic arrays are not project labels."""
import json
import sys
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'cloud'))
from research_features import research_features
from multiseason_research import run_research, scl_coverage
from worldcover_reference import worldcover_tile, prepare_worldcover

assert scl_coverage(np.array([[4,9],[6,3]]),np.array([[1,1],[1,0]],bool))==2/3
assert worldcover_tile([76.788,22.391,76.822,22.414])=='N21E075'
try:worldcover_tile([77.9,22.3,78.1,22.4])
except ValueError:pass
else:raise AssertionError('Cross-tile reference crop accepted')
try:prepare_worldcover(None,None,None)
except RuntimeError as error:assert 'hosted' in str(error)
else:raise AssertionError('Local reference acquisition must be blocked')

order=['B02','B03','B04','B08','B05','B06','B07','B8A','B11','B12']
values=np.broadcast_to(np.asarray([.05,.08,.1,.5,.2,.25,.3,.4,.2,.15],dtype='float32')[:,None,None],(10,7,7)).copy()
features,valid,names=research_features(values,order,np.ones((7,7),dtype=bool))
assert valid.sum()==25  # A 3x3 texture excludes the outer row/column.
assert np.isclose(features[names.index('NDVI'),3,3],2/3)
assert np.isclose(features[names.index('EVI'),3,3],1/1.725)
assert np.isclose(features[names.index('NDRE_B8A_B05'),3,3],1/3)
assert np.isclose(features[names.index('NDMI_B8A_B11'),3,3],1/3)
assert features[-1,3,3]<.001
values[order.index('B04'),3,3]=0;values[order.index('B08'),3,3]=0
_,masked,_=research_features(values,order,np.ones((7,7),dtype=bool))
assert not masked[2:5,2:5].any(), 'Undefined index must invalidate its texture neighborhood'
for bad_order,bad_mask in [(order[:-1],np.ones((7,7),bool)),(order,np.ones((2,2),bool))]:
    try:research_features(values,bad_order,bad_mask)
    except ValueError:pass
    else:raise AssertionError('Incompatible band stack/mask was accepted')
try:run_research(None,None,None)
except RuntimeError as error:assert 'hosted' in str(error)
else:raise AssertionError('Local research acquisition must be blocked')
for name in ['notebooks/04_multiseason_research.ipynb','data/study/compartment_279_v1/04_multiseason_research.private.ipynb']:
    notebook=json.loads((root/name).read_text())
    cells=[cell for cell in notebook['cells'] if cell['cell_type']=='code']
    for cell in cells:
        assert cell['outputs']==[] and cell['execution_count'] is None
        compile(''.join(cell['source']),name,'exec')
    if name.startswith('notebooks/'):
        assert ''.join(cells[0]['source'])=='STUDY = None\n'
print('PASS: analytical index values, invalid-index/texture masks, grid mismatch rejection, cloud guard and public/private notebook checks. No real labels or model accuracy measured.')
