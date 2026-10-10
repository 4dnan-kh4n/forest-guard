"""Reproduce trusted cloud proxy predictions offline; no fitting or forest approval."""
import hashlib
import argparse
import io
import json
import socket
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
from sklearn.metrics import confusion_matrix,precision_score,recall_score,f1_score,jaccard_score

from verify_weak_export import verify
from predict_crop import load_model

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cloud'))
from train_weak_proxy import inspect_dataset

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle',type=Path,default=ROOT/'data/phase3/weak_proxy_run_v1/forestguard_weak_proxy_run1.zip')
parser.add_argument('--sha256',default='eca2839185a91e729bbf9ab4c52813f2137a6e056b13c432b97bbe9a8ae7061c')
parser.add_argument('--dataset',type=Path,default=ROOT/'data/phase2/weak_proxy_experiment_v1/weak_experiment.zip')
parser.add_argument('--dataset-sha256',default='15d7c83557657a116f10080953405f521f100e64b389ef8b0dcaea3632945279')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
bundle,trusted=args.bundle,args.sha256
folder=bundle.parent
if args.output and args.output.exists():raise ValueError('Preserve existing verification output.')
report=verify(bundle,trusted,args.dataset,args.dataset_sha256)
samples,data=inspect_dataset(args.dataset,args.dataset_sha256)
diagnostics={}
with patch.object(socket,'socket',side_effect=AssertionError('Networking forbidden')),zipfile.ZipFile(bundle) as source:
    for name in ['baseline','random_forest']:
        model=joblib.load(io.BytesIO(source.read(name+'.joblib')))
        if hasattr(model,'n_jobs'):model.n_jobs=1
        predicted=model.predict(samples['validation_X'])
        actual=confusion_matrix(samples['validation_y'],predicted,labels=[0,1]).tolist()
        assert actual==report['validation_reference_agreement_metrics'][name]['confusion_matrix']
        for key,metric in [('precision',precision_score),('recall',recall_score),('f1',f1_score),('iou',jaccard_score)]:
            assert np.isclose(metric(samples['validation_y'],predicted,zero_division=0),report['validation_reference_agreement_metrics'][name][key],rtol=0,atol=1e-12)
        if name=='baseline':assert (predicted==np.bincount(samples['train_y']).argmax()).all()
    for group in ['train','validation']:
        diagnostics[group]={}
        for cls in [0,1]:
            values=samples[group+'_X'][samples[group+'_y']==cls]
            diagnostics[group][str(cls)]={feature:round(float(np.median(values[:,data['feature_order'].index(feature)])),4)
                                        for feature in ['B04','B08','NDVI','NDMI_B8A_B11']}
    try:load_model(bundle,trusted)
    except (ValueError,KeyError):pass
    else:raise AssertionError('Production forest loader accepted a weak proxy export')
with tempfile.TemporaryDirectory(prefix='weak_corrupt_',dir=folder) as temporary:
    broken=Path(temporary)/'broken.zip';broken.write_bytes(bundle.read_bytes()+b'corrupt')
    try:verify(broken,trusted)
    except ValueError:pass
    else:raise AssertionError('Corrupted export accepted')
summary={'status':'PASS','offline_confusion_matrices_match_cloud':True,'offline_metrics_match_cloud':True,
         'expected_dataset_verified':True,'export_sha256':trusted,'dataset_sha256':args.dataset_sha256,
         'validation_samples':len(samples['validation_y']),
         'both_models_checked':True,'constant_baseline_behavior_verified':True,'corrupt_export_rejected':True,
         'production_forest_loader_rejects_proxy':True,'local_fitting_performed':False,
         'feature_medians_by_proxy_class':diagnostics,'independent_forest_accuracy_measured':False,
         'operational_use_approved':False}
(args.output or folder/'offline_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
