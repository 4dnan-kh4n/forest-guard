"""Verify a trusted weak-proxy export without unpickling or approving a forest model."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def verify(bundle,trusted_sha256,dataset=None,dataset_sha256=None):
    if (dataset is None)!=(dataset_sha256 is None):raise ValueError('Provide both expected dataset and its trusted checksum.')
    bundle=Path(bundle)
    if bundle.stat().st_size>30*1024**2 or hashlib.sha256(bundle.read_bytes()).hexdigest()!=trusted_sha256:
        raise ValueError('Weak model export checksum/size mismatch.')
    names={'baseline.joblib','random_forest.joblib','model_manifest.json','evaluation.json','checksums.json'}
    with zipfile.ZipFile(bundle) as saved:
        if len(saved.infolist())!=5 or set(saved.namelist())!=names or sum(i.file_size for i in saved.infolist())>30*1024**2:
            raise ValueError('Weak export members/size mismatch.')
        hashes=json.loads(saved.read('checksums.json'))
        if set(hashes)!=names-{'checksums.json'}:raise ValueError('Weak artifact manifest mismatch.')
        for name,checksum in hashes.items():
            if hashlib.sha256(saved.read(name)).hexdigest()!=checksum:raise ValueError('Weak artifact checksum mismatch.')
        manifest=json.loads(saved.read('model_manifest.json'));evaluation=json.loads(saved.read('evaluation.json'))
        if dataset is not None:
            import sys
            sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cloud'))
            from train_weak_proxy import inspect_dataset
            _,expected_dataset=inspect_dataset(dataset,dataset_sha256)
            if any(manifest.get(key)!=value for key,value in expected_dataset.items()):
                raise ValueError('Model export belongs to a different dataset or experiment.')
        if manifest['model_kind']!='exploratory_weak_map_proxy' or manifest['reference_kind']!='weak_map':
            raise ValueError('Unexpected model target.')
        if any(manifest[key] is not False for key in ['reference_independent','reviewed_labels_exist','independent_test_set_exists','operational_use_approved']):
            raise ValueError('Unjustified model scope/approval.')
        if evaluation['independent_test_results'] is not None or evaluation['independent_forest_accuracy_measured'] is not False or evaluation['operational_use_approved'] is not False:
            raise ValueError('Unjustified evaluation claims.')
        selected=evaluation['selected_model']
        metrics=evaluation['validation_reference_agreement_metrics']
        if set(metrics)!={'baseline','random_forest'}:raise ValueError('Missing baseline comparison.')
        expected='random_forest' if metrics['random_forest']['f1']>metrics['baseline']['f1'] else 'baseline'
        if selected!=expected or manifest['selected_model_file']!=selected+'.joblib':raise ValueError('Selection differs from validation rule.')
        if manifest['model_version']!='weak-proxy-'+hashes[selected+'.joblib'][:16]:raise ValueError('Model identity checksum mismatch.')
        for values in metrics.values():
            if any(not 0<=values[key]<=1 for key in ['precision','recall','f1','iou']):raise ValueError('Invalid agreement metric range.')
            matrix=values['confusion_matrix']
            if len(matrix)!=2 or any(len(row)!=2 for row in matrix) or sum(sum(row) for row in matrix)!=manifest['groups']['validation']['samples']:
                raise ValueError('Agreement confusion matrix size/count mismatch.')
    return {'status':'PASS','artifacts_verified':4,'selected_model':selected,'model_version':manifest['model_version'],
            'validation_reference_agreement_metrics':metrics,'model_export_sha256':trusted_sha256,
            'independent_forest_accuracy_measured':False,'operational_use_approved':False,'model_unpickled':False,
            'expected_dataset_verified':dataset is not None}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('bundle',type=Path);parser.add_argument('--sha256',required=True)
    parser.add_argument('--dataset',type=Path);parser.add_argument('--dataset-sha256')
    args=parser.parse_args();print(json.dumps(verify(args.bundle,args.sha256,args.dataset,args.dataset_sha256),indent=2))
