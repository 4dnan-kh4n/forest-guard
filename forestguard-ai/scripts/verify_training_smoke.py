"""Check downloaded synthetic training artifacts without loading any model."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path


def verify(path):
    with zipfile.ZipFile(path) as outer:
        if (len(outer.infolist())!=2 or set(outer.namelist())!={'check_report.json','synthetic_model_export.zip'}
                or sum(i.file_size for i in outer.infolist())>10*1024**2 or outer.testzip() is not None):
            raise ValueError('Invalid/oversized synthetic check archive.')
        report = json.loads(outer.read('check_report.json'))
        required = ['synthetic_fixture','baseline_and_random_forest_fitted','validation_selection_checked',
                    'serialization_roundtrip_checked','checksum_archive_checked',
                    'feature_count_rejection_checked','failure_reporting_checked']
        if report['status']!='PASS' or report['real_forest_accuracy_measured'] is not False or any(report[k] is not True for k in required):
            raise ValueError('Check must declare synthetic engineering success, not forest accuracy.')
        with zipfile.ZipFile(io.BytesIO(outer.read('synthetic_model_export.zip'))) as inner:
            entries = inner.infolist()
            names = set(inner.namelist())
            expected = {'baseline.joblib','random_forest.joblib','model_manifest.json','evaluation.json',
                        'labels.geojson','research_features.py','FOREST_COVER_DEFINITION.md','checksums.json'}
            if names!=expected or len(entries)!=len(names) or sum(i.file_size for i in entries)>10*1024**2 or inner.testzip() is not None:
                raise ValueError('Unexpected/oversized model archive.')
            hashes = json.loads(inner.read('checksums.json'))
            if set(hashes)!=names-{'checksums.json'}:
                raise ValueError('Model manifest member mismatch.')
            for name,digest in hashes.items():
                if hashlib.sha256(inner.read(name)).hexdigest()!=digest:
                    raise ValueError('Integrity failure: '+name)
            manifest = json.loads(inner.read('model_manifest.json'))
            evaluation = json.loads(inner.read('evaluation.json'))
            if (manifest['synthetic_fixture'] is not True or evaluation['synthetic_fixture'] is not True
                    or manifest['operational_use_approved'] is not False
                    or not manifest['model_version'].startswith('synthetic-')
                    or not manifest['dataset_version'].startswith('synthetic-')
                    or manifest['versions']!=report['versions']):
                raise ValueError('Synthetic scope/version mismatch.')
    return {'integrity':'PASS','verified_model_files':len(hashes),'synthetic_fixture':True,
            'real_forest_accuracy_measured':False,'model_loaded_locally':False,
            'versions':report['versions'],'bundle_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest()}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle),indent=2))
