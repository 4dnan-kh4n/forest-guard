"""Cloud smoke test of fitting/export using synthetic samples, never forest truth."""
import hashlib
import json
import platform
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

from train_forest import run


def run_check(work_root):
    if platform.system()=='Windows':
        raise RuntimeError('Run this fitting check in hosted CPU, not on the laptop.')
    work_root = Path(work_root)
    target = work_root/'synthetic_training_check.zip'
    if target.exists():
        raise ValueError('Preserve existing synthetic check output.')
    rng = np.random.default_rng(42)
    order = ['synthetic_feature_'+str(i) for i in range(15)]
    samples = {}
    for name,count in [('train',64),('validation',32),('test',32)]:
        truth = np.tile([0,1],count//2).astype('uint8')
        values = rng.normal(size=(count,15)).astype('float32')*.15+truth[:,None]
        if name=='test':
            truth[:2] = 1-truth[:2]  # Synthetic label noise exercises failure reporting.
        samples[name] = {'X':values,'y':truth,'sites':['synthetic-'+name+'-'+str(i//4) for i in range(count)],
                         'pixels':[('synthetic-date',i,0) for i in range(count)]}
    import joblib
    import rasterio
    coverage = {'band_order':['synthetic_band_'+str(i) for i in range(10)],
                'bundle_sha256':hashlib.sha256(b'synthetic imagery').hexdigest(),
                'boundary_sha256':hashlib.sha256(b'synthetic boundary').hexdigest(),
                'runtime':{'python':platform.python_version(),'numpy':np.__version__,
                           'rasterio':rasterio.__version__,'gdal':rasterio.__gdal_version__}}
    with tempfile.TemporaryDirectory(prefix='synthetic_training_',dir=work_root) as temporary:
        working = Path(temporary)
        labels = working/'synthetic_labels.json'
        labels.write_text(json.dumps({'synthetic_fixture':True,'real_labels':0}))
        extracted = (samples,order,coverage,{'acquisitions':[]},
                     {'synthetic_fixture':True,'training_eligible':False,'scope':'Mock extraction; no real independent reference review'})
        with patch('train_forest.extract_samples',return_value=extracted):
            archive = run(working/'synthetic_input.zip',working/'synthetic_boundary.json',labels,working/'synthetic_model_export')
        with zipfile.ZipFile(archive) as bundle:
            assert bundle.testzip() is None
            checksums = json.loads(bundle.read('checksums.json'))
            assert set(bundle.namelist())==set(checksums)|{'checksums.json'}
            for name,digest in checksums.items():
                assert hashlib.sha256(bundle.read(name)).hexdigest()==digest
            manifest = json.loads(bundle.read('model_manifest.json'))
            evaluation = json.loads(bundle.read('evaluation.json'))
            assert manifest['synthetic_fixture'] and evaluation['synthetic_fixture']
            assert manifest['model_roundtrip_checked'] and not manifest['operational_use_approved']
            assert manifest['dataset_version'].startswith('synthetic-') and manifest['model_version'].startswith('synthetic-')
            assert manifest['feature_order']==order
            assert evaluation['selected_model']=='random_forest'
            assert evaluation['failure_pixels']
            selected = joblib.load(archive.parent/'synthetic_model_export'/manifest['selected_model_file'])
            assert selected.n_features_in_==15
            try:
                selected.predict(np.zeros((1,14),dtype='float32'))
            except ValueError:pass
            else:raise AssertionError('Wrong feature count accepted.')
        summary = {'status':'PASS','synthetic_fixture':True,'real_forest_accuracy_measured':False,
                   'baseline_and_random_forest_fitted':True,'validation_selection_checked':True,
                   'serialization_roundtrip_checked':True,'checksum_archive_checked':True,
                   'feature_count_rejection_checked':True,'failure_reporting_checked':True,
                   'versions':manifest['versions']}
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as saved:
            saved.write(archive,'synthetic_model_export.zip')
            saved.writestr('check_report.json',json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return target
