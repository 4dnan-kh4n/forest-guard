"""Hosted-only exploratory agreement fitting; never an approved forest classifier."""
import hashlib
import io
import json
import platform
import tempfile
import zipfile
from pathlib import Path

import numpy as np


def inspect_dataset(bundle,trusted_sha256):
    bundle=Path(bundle)
    if bundle.stat().st_size>30*1024**2 or hashlib.sha256(bundle.read_bytes()).hexdigest()!=trusted_sha256:
        raise ValueError('Weak dataset does not match trusted size/checksum.')
    with zipfile.ZipFile(bundle) as archive:
        if len(archive.infolist())!=3 or set(archive.namelist())!={'samples.npz','dataset_manifest.json','checksums.json'} or sum(i.file_size for i in archive.infolist())>30*1024**2:
            raise ValueError('Unexpected weak dataset members/size.')
        hashes=json.loads(archive.read('checksums.json'))
        if set(hashes)!={'samples.npz','dataset_manifest.json'}:raise ValueError('Unexpected checksum manifest.')
        for name,checksum in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=checksum:raise ValueError('Weak dataset file changed.')
        manifest=json.loads(archive.read('dataset_manifest.json'))
        if manifest['format']!='forestguard-weak-proxy-dataset-v1' or manifest['reference_kind']!='weak_map' or any(manifest[k] is not False for k in ['reference_independent','reviewed_labels_exist','independent_test_set_exists','operational_use_approved']):
            raise ValueError('Weak-map scope/approval flags invalid.')
        raw=archive.read('samples.npz')
    with zipfile.ZipFile(io.BytesIO(raw)) as arrays:
        if sum(i.file_size for i in arrays.infolist())>30*1024**2:raise ValueError('Expanded samples exceed limit.')
    with np.load(io.BytesIO(raw),allow_pickle=False) as stored:
        expected={g+'_'+key for g in ['train','validation'] for key in ['X','y','pixels']}
        if set(stored.files)!=expected:raise ValueError('Unexpected sample arrays.')
        samples={key:stored[key] for key in expected}
    for group in ['train','validation']:
        X,y,pixels=[samples[group+'_'+key] for key in ['X','y','pixels']]
        if X.dtype!=np.dtype('float32') or X.ndim!=2 or X.shape!=(len(y),15) or not np.isfinite(X).all() or not 0<len(y)<=10000:
            raise ValueError('Invalid feature samples.')
        if y.dtype!=np.dtype('uint8') or y.ndim!=1 or set(np.unique(y))!={0,1} or pixels.dtype!=np.dtype('int32') or pixels.shape!=(len(y),2):
            raise ValueError('Invalid proxy targets/coordinates.')
        if manifest['groups'][group]['samples']!=len(y):raise ValueError('Sample counts differ from metadata.')
    if len(manifest['feature_order'])!=15 or manifest['groups']['train']['acquisition_date']==manifest['groups']['validation']['acquisition_date']:
        raise ValueError('Feature/date separation invalid.')
    if samples['validation_pixels'][:,0].min()-samples['train_pixels'][:,0].max()<11:
        raise ValueError('Training/validation regions lack the excluded 200 m strip.')
    return samples,manifest


def run(bundle,trusted_sha256,output):
    if platform.system()=='Windows' or not (Path('/kaggle/working').exists() or Path('/content').exists()):
        raise RuntimeError('Exploratory fitting runs only in hosted Kaggle/Colab; not on the laptop.')
    output=Path(output)
    if output.exists() or output.with_suffix('.zip').exists():raise ValueError('Preserve existing output.')
    samples,manifest=inspect_dataset(bundle,trusted_sha256)
    import joblib,sklearn
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import precision_score,recall_score,f1_score,jaccard_score,confusion_matrix
    models={'baseline':DummyClassifier(strategy='most_frequent'),
            'random_forest':RandomForestClassifier(n_estimators=100,max_depth=12,min_samples_leaf=2,class_weight='balanced',random_state=42,n_jobs=2)}
    evaluations={};predictions={}
    for name,model in models.items():
        model.fit(samples['train_X'],samples['train_y'])
        predicted=model.predict(samples['validation_X']);predictions[name]=predicted
        target=samples['validation_y']
        evaluations[name]={'precision':float(precision_score(target,predicted,zero_division=0)),
            'recall':float(recall_score(target,predicted,zero_division=0)),'f1':float(f1_score(target,predicted,zero_division=0)),
            'iou':float(jaccard_score(target,predicted,zero_division=0)),'confusion_matrix':confusion_matrix(target,predicted,labels=[0,1]).tolist()}
    selected='random_forest' if evaluations['random_forest']['f1']>evaluations['baseline']['f1'] else 'baseline'
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='weak_model_',dir=output.parent) as temporary:
        folder=Path(temporary)
        for name,model in models.items():
            path=folder/(name+'.joblib');joblib.dump(model,path,compress=3)
            assert np.array_equal(joblib.load(path).predict(samples['validation_X']),predictions[name])
        export=dict(manifest,selected_model_file=selected+'.joblib',model_kind='exploratory_weak_map_proxy',
                    model_version='weak-proxy-'+hashlib.sha256((folder/(selected+'.joblib')).read_bytes()).hexdigest()[:16],
                    runtime={'python':platform.python_version(),'numpy':np.__version__,'sklearn':sklearn.__version__,'joblib':joblib.__version__})
        (folder/'model_manifest.json').write_text(json.dumps(export,indent=2)+'\n')
        evaluation={'validation_reference_agreement_metrics':evaluations,'selected_model':selected,
                    'independent_test_results':None,'independent_forest_accuracy_measured':False,
                    'operational_use_approved':False,'limits':manifest['limits']}
        (folder/'evaluation.json').write_text(json.dumps(evaluation,indent=2)+'\n')
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
        (folder/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n')
        folder.rename(output)
    with zipfile.ZipFile(output.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
        for path in output.iterdir():archive.write(path,path.name)
    return output.with_suffix('.zip')
