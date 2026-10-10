"""Verify real weak-map data preparation, separation, scope and hosted-only fitting guard."""
import hashlib
import json
import socket
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

from prepare_weak_experiment import ROOT,prepare,spatial_masks
sys.path.insert(0,str(ROOT/'cloud'))
from train_weak_proxy import inspect_dataset,run

labels=ROOT/'data/phase2/compartment_279_dataset_v1/labels.geojson'
original=hashlib.sha256(labels.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='weak_check_',dir=ROOT/'data/phase2') as temporary:
    folder=Path(temporary)/'dataset'
    with patch.object(socket,'socket',side_effect=AssertionError('Networking forbidden')):
        report=prepare(folder);bundle=folder/'weak_experiment.zip';checksum=report['zip_sha256']
        samples,manifest=inspect_dataset(bundle,checksum)
    assert len(samples['train_y'])==4915 and len(samples['validation_y'])==6067
    assert manifest['reference']['reference_year']==2021
    assert manifest['groups']['train']['acquisition_date']=='2025-04-03'
    assert manifest['groups']['validation']['acquisition_date']=='2025-12-09'
    assert manifest['operational_use_approved'] is False and manifest['reference_independent'] is False
    assert np.isfinite(samples['train_X']).all() and samples['train_X'].shape[1]==15
    masks=spatial_masks((123,172));assert not (masks['train']&masks['validation']).any()
    assert np.where(masks['validation'])[0].min()-np.where(masks['train'])[0].max()==11
    try:inspect_dataset(bundle,'0'*64)
    except ValueError:pass
    else:raise AssertionError('Wrong checksum accepted')
    try:prepare(folder)
    except ValueError:pass
    else:raise AssertionError('Output overwritten')
    try:run(bundle,checksum,folder/'model')
    except RuntimeError:pass
    else:raise AssertionError('Local fitting was permitted')
notebook=json.loads((ROOT/'notebooks/10_weak_tree_cover_proxy.ipynb').read_text())
code=[c for c in notebook['cells'] if c['cell_type']=='code']
assert ''.join(code[1]['source'])==(ROOT/'cloud/train_weak_proxy.py').read_text(encoding='utf-8')
for cell in code:
    assert cell['execution_count'] is None and not cell['outputs']
    compile(''.join(cell['source']),'weak notebook','exec')
assert original==hashlib.sha256(labels.read_bytes()).hexdigest()
summary={'status':'PASS','real_features_with_historical_weak_targets':True,'samples':{'train':4915,'validation':6067},
         'spatial_date_separation_checked':True,'network_blocked_preparation_checked':True,
         'original_reviewed_training_gate_unchanged':True,'local_fitting_rejected':True,
         'notebook_source_syntax_checked':True,'model_trained':False,'independent_forest_accuracy_measured':False}
(ROOT/'data/phase2/weak_experiment_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
