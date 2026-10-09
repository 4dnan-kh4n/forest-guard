"""Check training safeguards and metric arithmetic; never fit a local model."""
import copy
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from rasterio.warp import transform

root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'cloud'))
from train_forest import metrics,validate_labels,extract_samples,run

assert metrics([0,0,1,1],[0,1,0,1]) == {
    'precision':.5,'recall':.5,'f1':.5,'iou':1/3,
    'confusion_matrix':{'tn':1,'fp':1,'fn':1,'tp':1},
    'sampled_area_error_ha':0.,'sampled_absolute_area_error_ha':0.,
    'area_scope':'sampled reference pixels only; not full compartment area'}
assert metrics([0,1],[0,0])['sampled_area_error_ha']==-.04
assert metrics([0,1],[1,1])['sampled_area_error_ha']==.04
assert metrics([0,0],[0,0])['f1']==0
for truth,prediction in [([],[]),([0],[0,1]),([2],[0])]:
    try:metrics(truth,prediction)
    except ValueError:pass
    else:raise AssertionError('Invalid metric vectors accepted.')
labels = root/'data/labels/compartment_279_november_comparison_v2/satellite_interpretations.geojson'
document = json.loads(labels.read_bytes())
try:validate_labels(document)
except ValueError as error:assert 'splits must be frozen' in str(error)
else:raise AssertionError('Actual unresolved labels accepted for training.')
try:extract_samples(Path('unread.zip'),Path('unread.geojson'),labels)
except ValueError as error:assert 'splits must be frozen' in str(error)
else:raise AssertionError('Current labels did not fail before imagery loading.')
try:run(None,None,None,root/'data/phase3/should_not_exist')
except RuntimeError as error:assert 'hosted' in str(error)
else:raise AssertionError('Local training guard failed.')
assert not (root/'data/phase3/should_not_exist').exists()

# Synthetic metadata fixtures test the contract, not project geography or truth.
fixture = {'type':'FeatureCollection','features':[]}
for split,date,longitude in [('train','2023-04-01',76.70),('validation','2024-04-01',76.72),('test','2025-04-01',76.74)]:
    for number,cls in enumerate(['forest','non_forest']):
        feature = copy.deepcopy(document['features'][0])
        feature['geometry']={'type':'Point','coordinates':[longitude,22.3+number*.01]}
        feature['properties'].update(label_id='synthetic-'+split+'-'+cls,class_=cls,
                                     split=split,observation_date=date,reference_date=date,
                                     confidence='high',reference_independent=True,reviewer='Synthetic checker fixture')
        feature['properties']['class']=feature['properties'].pop('class_')
        feature['properties'].update(canopy_cover_percent=20,qualifying_stand_area_ha=1,
                                     height_evidence='Synthetic evidence only',forest_use_evidence='Synthetic evidence only')
        fixture['features'].append(feature)
assert validate_labels(fixture)['split_checks_complete'] is True
for field,value in [('canopy_cover_percent',10),('qualifying_stand_area_ha',.5),('height_evidence',None),('forest_use_evidence','')]:
    changed = copy.deepcopy(fixture)
    changed['features'][0]['properties'][field]=value
    try:validate_labels(changed)
    except ValueError:pass
    else:raise AssertionError('Missing qualifying-forest evidence accepted: '+field)

base = root/'data/phase3/checks'
base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=base) as temporary:
    working = Path(temporary).resolve()
    assert working.is_relative_to(base.resolve())
    points = [f['geometry']['coordinates'] for f in fixture['features']]
    xs,ys = transform('EPSG:4326','EPSG:32643',[p[0] for p in points],[p[1] for p in points])
    grid = from_origin(min(xs)-40,max(ys)+40,20,20)
    width,height = int((max(xs)-min(xs))/20)+5,int((max(ys)-min(ys))/20)+5
    def raster_bytes(values):
        with MemoryFile() as memory:
            with memory.open(driver='GTiff',height=height,width=width,count=values.shape[0],
                             dtype=str(values.dtype),crs='EPSG:32643',transform=grid) as raster:
                raster.write(values)
            return memory.read()
    features = raster_bytes(np.ones((2,height,width),dtype='float32'))
    quality = raster_bytes(np.ones((1,height,width),dtype='uint8'))
    records = [{'acquisition':date+'T00:00:00Z','season':split,'feature_order':['synthetic_a','synthetic_b']}
               for split,date in [('train','2023-04-01'),('validation','2024-04-01'),('test','2025-04-01')]]
    synthetic_bundle = working/'synthetic.zip'
    with zipfile.ZipFile(synthetic_bundle,'w') as archive:
        archive.writestr('research_report.json',json.dumps({'acquisitions':records}))
        for record in records:
            archive.writestr(record['season']+'/features.tif',features)
            archive.writestr(record['season']+'/usable_mask.tif',quality)
    synthetic_boundary = working/'synthetic_boundary.geojson'
    synthetic_boundary.write_text(json.dumps({'features':[{'properties':{'study_area_version':fixture['features'][0]['properties']['study_area_version']}}]}))
    synthetic_labels = working/'synthetic_labels.geojson'
    synthetic_labels.write_text(json.dumps(fixture))
    # Integrity itself is covered by real-data checks; this fixture isolates sampling.
    with patch('train_forest.inspect',return_value={'synthetic_fixture':True}):
        samples,order,*_ = extract_samples(synthetic_bundle,synthetic_boundary,synthetic_labels)
        assert order==['synthetic_a','synthetic_b']
        assert all(g['X'].shape==(2,2) and sorted(g['y'].tolist())==[0,1] for g in samples.values())
        overlap = copy.deepcopy(fixture)
        duplicate = copy.deepcopy(overlap['features'][0])
        duplicate['properties']['label_id']='synthetic-overlap'
        overlap['features'].append(duplicate)
        synthetic_labels.write_text(json.dumps(overlap))
        try:extract_samples(synthetic_bundle,synthetic_boundary,synthetic_labels)
        except ValueError as error:assert 'Overlapping reference pixels' in str(error)
        else:raise AssertionError('Duplicate sampling accepted.')

notebook = json.loads((root/'notebooks/08_forest_training.ipynb').read_text())
for cell in notebook['cells']:
    if cell['cell_type']=='code':
        assert cell['execution_count'] is None and cell['outputs']==[]
        compile(''.join(cell['source']),'training notebook','exec')
bootstrap = ''.join(next(c for c in notebook['cells'] if c['id']=='source')['source'])
assert 'SOURCE_FILES = ' in bootstrap
source_literal = bootstrap.split('SOURCE_FILES = ',1)[1].split('\nfor name, content',1)[0]
import ast
for name,source in ast.literal_eval(source_literal).items():
    expected = (root/name).read_bytes().decode('utf-8') if name.endswith('.md') else (root/name).read_text(encoding='utf-8')
    assert source == expected
paths = ''.join(next(c for c in notebook['cells'] if c['id']=='paths')['source'])
assert paths=='BUNDLE = None\nBOUNDARY = None\nLABELS = None\n'
smoke = json.loads((root/'notebooks/09_synthetic_training_check.ipynb').read_text())
for cell in smoke['cells']:
    if cell['cell_type']=='code':
        assert cell['execution_count'] is None and cell['outputs']==[]
        compile(''.join(cell['source']),'synthetic training notebook','exec')
assert ''.join(next(c for c in smoke['cells'] if c['id']=='source')['source'])==bootstrap
assert ''.join(next(c for c in smoke['cells'] if c['id']=='smoke-source')['source'])==(root/'cloud/synthetic_training_check.py').read_text(encoding='utf-8')
summary = {'status':'PASS','metric_arithmetic_checked':True,'actual_unready_labels_rejected':True,
           'qualifying_reference_contract_checked':True,'local_training_blocked':True,
           'synthetic_sample_extraction_and_overlap_checked':True,
           'notebook_source_parity':True,'model_fit_executed':False,'accuracy_measured':False}
output = root/'data/phase3'
output.mkdir(exist_ok=True)
(output/'engineering_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
