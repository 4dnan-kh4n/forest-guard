"""Check real December weak-map samples, provenance, separation and hosted-only fitting."""
import base64
import hashlib
import json
import socket
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from rasterio.io import MemoryFile

from prepare_weak_experiment import ROOT,BUNDLE,prepare
sys.path.insert(0,str(ROOT/'cloud'))
from train_weak_proxy import inspect_dataset,run

before=ROOT/'data/study/compartment_279_v1/december_2024_v1/forestguard_279_research.zip'
labels=ROOT/'data/phase2/compartment_279_dataset_v1/labels.geojson'
paths=[before,BUNDLE,labels,ROOT/'data/phase2/weak_proxy_experiment_v1/weak_experiment.zip']
original={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
with tempfile.TemporaryDirectory(prefix='december_check_',dir=ROOT/'data/phase2') as temporary:
    folder=Path(temporary)/'nested'/'dataset'
    with patch.object(socket,'socket',side_effect=AssertionError('Networking forbidden')):
        report=prepare(folder,before)
        bundle=folder/'weak_experiment.zip'
        samples,manifest=inspect_dataset(bundle,report['zip_sha256'])
    assert len(samples['train_y'])==4939 and len(samples['validation_y'])==6067
    assert manifest['groups']['train']['acquisition_date']=='2024-12-16'
    assert manifest['groups']['validation']['acquisition_date']=='2025-12-09'
    assert manifest['reference_year_gap_by_group']=={'train':3,'validation':4}
    assert manifest['source_hashes']['before_bundle']==original[before]
    assert manifest['observation_pair']['common_observable_pixels']==12362
    assert manifest['operational_use_approved'] is False
    assert not manifest['reference_independent'] and not manifest['independent_test_set_exists']
    assert samples['validation_pixels'][:,0].min()-samples['train_pixels'][:,0].max()>=11
    with zipfile.ZipFile(before) as archive,MemoryFile(archive.read('post_monsoon/features.tif')) as memory,memory.open() as raster:
        values=raster.read()
        rows,cols=samples['train_pixels'].T
        assert np.array_equal(samples['train_X'],values[:,rows,cols].T)
    with zipfile.ZipFile(BUNDLE) as archive,MemoryFile(archive.read('post_monsoon/worldcover_2021_weak.tif')) as memory,memory.open() as raster:
        weak=raster.read(1)
        for group in ['train','validation']:
            rows,cols=samples[group+'_pixels'].T
            assert np.array_equal(samples[group+'_y'],(weak[rows,cols]==10).astype('uint8'))
    for operation in [lambda:prepare(folder,before),lambda:prepare(Path(temporary)/'invalid',BUNDLE),
                      lambda:inspect_dataset(bundle,'0'*64)]:
        try:operation()
        except ValueError:pass
        else:raise AssertionError('Overwrite, invalid pair or checksum accepted.')
    assert not (Path(temporary)/'invalid').exists()
    try:run(bundle,report['zip_sha256'],folder/'model')
    except RuntimeError:pass
    else:raise AssertionError('Local fitting permitted.')

public=json.loads((ROOT/'notebooks/12_december_weak_proxy.ipynb').read_text())
private=json.loads((ROOT/'data/phase3/weak_december_run_v1/private_run.ipynb').read_text())
for notebook in [public,private]:
    for cell in notebook['cells']:
        if cell['cell_type']=='code':
            assert cell['execution_count'] is None and not cell['outputs']
            compile(''.join(cell['source']),'December notebook','exec')
    assert ''.join(notebook['cells'][2]['source'])==(ROOT/'cloud/train_weak_proxy.py').read_text(encoding='utf-8')
assert ''.join(public['cells'][1]['source'])=='BUNDLE = None\nTRUSTED_SHA256 = None\n'
input_code=''.join(private['cells'][1]['source'])
encoded=input_code.split('base64.b64decode(',1)[1].split('))',1)[0]
import ast
embedded=base64.b64decode(ast.literal_eval(encoded))
saved=ROOT/'data/phase2/weak_december_experiment_v1/weak_experiment.zip'
assert embedded==saved.read_bytes()
assert original=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
summary={'status':'PASS','samples':{'train':4939,'validation':6067},'dates':['2024-12-16','2025-12-09'],
         'actual_2024_features_and_historical_targets_checked':True,'spatial_date_separation_checked':True,
         'network_blocked_preparation_checked':True,'original_sources_and_review_gate_unchanged':True,
         'notebook_embedded_data_verified':True,'local_fitting_rejected':True,'model_trained':False,
         'dataset_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),
         'independent_forest_accuracy_measured':False,'limits':'No cloud run performed by this check.'}
(ROOT/'data/phase2/december_experiment_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
