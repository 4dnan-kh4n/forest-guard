"""Bounded offline inference from a trusted project model and calibrated features."""
import argparse
import hashlib
import io
import importlib.metadata
import json
import platform
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window


def load_model(bundle, trusted_sha256):
    bundle = Path(bundle)
    if bundle.stat().st_size > 30*1024**2:
        raise ValueError('Model archive exceeds 30 MiB.')
    raw = bundle.read_bytes()
    if hashlib.sha256(raw).hexdigest() != trusted_sha256:
        raise ValueError('Model does not match the externally trusted archive checksum.')
    # Checksums detect corruption; only caller-established provenance makes pickle trusted.
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names)!=len(set(names)) or sum(i.file_size for i in archive.infolist())>30*1024**2:
            raise ValueError('Duplicate/oversized model archive.')
        hashes = json.loads(archive.read('checksums.json'))
        if set(names)!=set(hashes)|{'checksums.json'} or archive.testzip() is not None:
            raise ValueError('Model archive members/CRC mismatch.')
        for name,digest in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=digest:
                raise ValueError('Model artifact checksum mismatch: '+name)
        manifest = json.loads(archive.read('model_manifest.json'))
        if type(manifest['synthetic_fixture']) is not bool or manifest['resolution_m']!=20:
            raise ValueError('Unsupported model scope/resolution.')
        if manifest['class_mapping']!={'0':'non_forest','1':'forest'}:
            raise ValueError('Unsupported model class mapping.')
        order = manifest['feature_order']
        if not order or len(order)>32 or len(set(order))!=len(order) or not all(isinstance(n,str) for n in order):
            raise ValueError('Invalid feature order.')
        if not manifest['synthetic_fixture'] and manifest['operational_use_approved'] is not True:
            raise ValueError('Real model has not passed operational review.')
        selected = manifest['selected_model_file']
        if selected not in {'baseline.joblib','random_forest.joblib'}:
            raise ValueError('Unsupported selected model.')
        import joblib
        import sklearn
        for name,version in [('numpy',np.__version__),('sklearn',sklearn.__version__),('joblib',joblib.__version__)]:
            if version!=manifest['versions'][name]:
                raise ValueError('Inference dependency version mismatch: '+name)
        model = joblib.load(io.BytesIO(archive.read(selected)))
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    if type(model) not in {DummyClassifier,RandomForestClassifier} or model.n_features_in_!=len(order) or not np.array_equal(model.classes_,[0,1]):
        raise ValueError('Unsupported estimator/features/classes.')
    if type(model) is RandomForestClassifier:
        model.n_jobs = 1
    return model,manifest


def predict(bundle, trusted_sha256, features, mask, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Output exists; preserve it and choose a new folder.')
    model,manifest = load_model(bundle,trusted_sha256)
    features,mask = Path(features),Path(mask)
    if any(p.stat().st_size>30*1024**2 for p in [features,mask]):
        raise ValueError('Only small stored crops are supported.')
    with rasterio.Env(PROJ_NETWORK='OFF',GDAL_CACHEMAX=16*1024**2), rasterio.open(features) as source, rasterio.open(mask) as quality:
        if (source.driver!='GTiff' or quality.driver!='GTiff' or source.width*source.height>250000
                or source.width>2048 or source.count!=len(manifest['feature_order'])
                or list(source.descriptions)!=manifest['feature_order']):
            raise ValueError('Invalid crop size/feature count/order.')
        if (source.crs is None or source.crs.to_epsg()!=32643 or source.crs!=quality.crs
                or source.transform!=quality.transform or source.shape!=quality.shape or quality.count!=1
                or source.transform.b!=0 or source.transform.d!=0
                or source.transform.a!=20 or source.transform.e!=-20):
            raise ValueError('Feature/mask grids must match the supported 20 m projected grid.')
        synthetic = manifest['synthetic_fixture']
        if (source.tags().get('synthetic_fixture')=='true') != synthetic:
            raise ValueError('Synthetic model/input scope mismatch.')
        # shortcut: only verified 20 m feature crops; add a format adapter for new grids.
        output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='inference_',dir=output.parent) as temporary:
            temporary = Path(temporary)
            profile = source.profile.copy()
            profile.update(count=1,dtype='uint8',nodata=255,compress='deflate')
            counts = [0,0]
            with rasterio.open(temporary/'classes.tif','w',**profile) as destination:
                destination.set_band_description(1,'synthetic_class' if synthetic else 'forest_class')
                destination.update_tags(synthetic_fixture=str(synthetic).lower(),model_version=manifest['model_version'])
                destination.update_tags(forest_definition_version=manifest['forest_definition_version'],
                                        operational_use_approved=str(manifest['operational_use_approved']).lower(),
                                        class_mapping='0:non_forest,1:forest',
                                        **{key:value for key,value in source.tags().items() if key in ['study_area_version','acquisition_date','season_review_status']})
                for row in range(0,source.height,16):
                    window = Window(0,row,source.width,min(16,source.height-row))
                    valid = quality.read(1,window=window,masked=True).filled(0)
                    if not np.isin(valid,[0,1]).all():
                        raise ValueError('Usable mask must contain only zero/one.')
                    values = source.read(window=window,masked=True)
                    usable = valid.astype(bool)
                    if (usable & np.ma.getmaskarray(values).any(axis=0)).any() or not np.isfinite(values.data[:,usable]).all():
                        raise ValueError('Usable pixels contain missing/nonfinite features.')
                    result = np.full(usable.shape,255,dtype='uint8')
                    if usable.any():
                        predictions = model.predict(values.data[:,usable].T.astype('float32'))
                        if not np.isin(predictions,[0,1]).all():
                            raise ValueError('Estimator returned unsupported classes.')
                        result[usable] = predictions
                        for label in [0,1]: counts[label]+=int((predictions==label).sum())
                    destination.write(result,1,window=window)
            report = {'synthetic_fixture':synthetic,'operational_use_approved':manifest['operational_use_approved'],
                      'model_version':manifest['model_version'],'dataset_version':manifest['dataset_version'],
                      'predicted_pixels':sum(counts),'class_pixels':{'0':counts[0],'1':counts[1]},
                      'nodata_pixels':source.width*source.height-sum(counts),'forest_area_ha':None,
                      'class_mapping':manifest['class_mapping'],'feature_order':manifest['feature_order'],
                      'runtime':dict(python=platform.python_version(),**{name:importlib.metadata.version(name) for name in ['numpy','scikit-learn','joblib','scipy','threadpoolctl','cloudpickle','rasterio']}),
                      'limits':'Synthetic engineering output only.' if synthetic else 'Model output; no legal forest status or causal change attribution.',
                      'input_sha256':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in [('features',features),('mask',mask),('model',Path(bundle))]}}
            (temporary/'prediction_report.json').write_text(json.dumps(report,indent=2)+'\n')
            # Publish a complete folder only after all input windows pass.
            temporary.rename(output)
    return report


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['model','features','mask','output']: parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--trusted-model-sha256',required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(predict(args.model,args.trusted_model_sha256,args.features,args.mask,args.output),indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        parser.exit(1,f'Inference failed: {error}\n')
