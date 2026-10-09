"""Cloud-only baseline/Random Forest training from independently reviewed splits."""
import hashlib
import json
import math
import platform
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom

from audit_labels import audit
from inspect_research import inspect


def validate_labels(document):
    checked = audit(document)
    if not checked['split_checks_complete']:
        raise ValueError('Reviewed independent train/validation/test splits must be frozen before training.')
    groups = {name:[] for name in ['train','validation','test']}
    for feature in document['features']:
        p = feature['properties']
        if p['class']=='forest':
            for name,minimum,maximum in [('canopy_cover_percent',10,100),('qualifying_stand_area_ha',.5,float('inf'))]:
                value = p.get(name)
                if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not minimum < value <= maximum:
                    raise ValueError('Forest reference needs supported canopy and stand-area criteria.')
            if any(not isinstance(p.get(name),str) or not p[name].strip() for name in ['height_evidence','forest_use_evidence']):
                raise ValueError('Forest reference needs height/height-potential and forest-use evidence.')
        groups[p['split']].append(feature)
    if any({f['properties']['class'] for f in features}!={'forest','non_forest'} for features in groups.values()):
        raise ValueError('Each frozen split needs both forest and non-forest reference sites.')
    return checked


def metrics(truth, prediction, pixel_ha=.04):
    truth, prediction = np.asarray(truth), np.asarray(prediction)
    if truth.ndim!=1 or not truth.size or truth.shape!=prediction.shape or not np.isin(truth,[0,1]).all() or not np.isin(prediction,[0,1]).all():
        raise ValueError('Metrics require matching nonempty binary label vectors.')
    tp = int(((truth==1)&(prediction==1)).sum())
    fp = int(((truth==0)&(prediction==1)).sum())
    fn = int(((truth==1)&(prediction==0)).sum())
    tn = int(((truth==0)&(prediction==0)).sum())
    divide = lambda numerator,denominator: numerator/denominator if denominator else 0.
    return {'precision':divide(tp,tp+fp),'recall':divide(tp,tp+fn),
            'f1':divide(2*tp,2*tp+fp+fn),'iou':divide(tp,tp+fp+fn),
            'confusion_matrix':{'tn':tn,'fp':fp,'fn':fn,'tp':tp},
            'sampled_area_error_ha':(fp-fn)*pixel_ha,
            'sampled_absolute_area_error_ha':abs(fp-fn)*pixel_ha,
            'area_scope':'sampled reference pixels only; not full compartment area'}


def extract_samples(bundle, boundary, labels):
    labels = Path(labels)
    if labels.stat().st_size>2*1024**2:
        raise ValueError('Labels exceed 2 MiB.')
    document = json.loads(labels.read_bytes())
    label_check = validate_labels(document)
    coverage = inspect(bundle,boundary)
    selected = json.loads(Path(boundary).read_bytes())
    version = selected['features'][0]['properties']['study_area_version']
    samples = {split:{'X':[],'y':[],'sites':[],'pixels':[]} for split in ['train','validation','test']}
    seen = set()
    with rasterio.Env(PROJ_NETWORK='OFF'), zipfile.ZipFile(bundle) as archive:
        report = json.loads(archive.read('research_report.json'))
        records = {item['acquisition'][:10]:item for item in report['acquisitions']}
        order = report['acquisitions'][0]['feature_order']
        for feature in document['features']:
            p = feature['properties']
            if p['study_area_version']!=version or p['observation_date'] not in records:
                raise ValueError('Reference date/study version does not match attached imagery.')
            record = records[p['observation_date']]
            if record['feature_order']!=order:
                raise ValueError('Inconsistent feature order across observations.')
            prefix = record['season']+'/'
            with MemoryFile(archive.read(prefix+'features.tif')) as memory, memory.open() as raster:
                projected = transform_geom('EPSG:4326',raster.crs,feature['geometry'])
                points = [projected['coordinates']] if projected['type']=='Point' else projected['coordinates'][0]
                left,bottom,right,top = raster.bounds
                if not all(left<=x<=right and bottom<=y<=top for x,y in points):
                    raise ValueError('Reference footprint extends outside imagery.')
                mask = geometry_mask([projected],raster.shape,raster.transform,invert=True)
                values = raster.read()
            with MemoryFile(archive.read(prefix+'usable_mask.tif')) as memory, memory.open() as raster:
                valid = raster.read(1).astype(bool)
            if not mask.any() or (mask & ~valid).any() or not np.isfinite(values[:,mask]).all():
                raise ValueError('Reference footprint has missing/uncertain observation pixels.')
            rows,cols = np.where(mask)
            pixels = [(p['observation_date'],int(row),int(col)) for row,col in zip(rows,cols)]
            if seen.intersection(pixels):
                raise ValueError('Overlapping reference pixels; resolve duplicate/conflicting labels.')
            seen.update(pixels)
            if len(seen)>50000:
                raise ValueError('Initial CPU training limited to 50,000 reference pixels.')
            group = samples[p['split']]
            group['X'].append(values[:,mask].T)
            group['y'].extend([int(p['class']=='forest')]*len(rows))
            group['sites'].extend([p['label_id']]*len(rows))
            group['pixels'].extend(pixels)
    for group in samples.values():
        group['X'] = np.concatenate(group['X']).astype('float32')
        group['y'] = np.asarray(group['y'],dtype='uint8')
    return samples,order,coverage,report,label_check


def run(bundle, boundary, labels, output):
    if platform.system()=='Windows' or not (Path('/kaggle/working').exists() or Path('/content').exists()):
        raise RuntimeError('Training runs only in a hosted Kaggle/Colab runtime, not on this laptop.')
    output = Path(output)
    if output.exists() or output.with_suffix('.zip').exists():
        raise ValueError('Training output exists; preserve it and choose a new run folder.')
    samples,order,coverage,source_report,label_check = extract_samples(bundle,boundary,labels)
    import joblib
    import sklearn
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    models = {'baseline':DummyClassifier(strategy='most_frequent'),
              'random_forest':RandomForestClassifier(n_estimators=100,max_depth=12,min_samples_leaf=2,
                                                    class_weight='balanced',n_jobs=2,random_state=42)}
    validation = {}
    for name,model in models.items():
        model.fit(samples['train']['X'],samples['train']['y'])
        validation[name] = metrics(samples['validation']['y'],model.predict(samples['validation']['X']))
    selected = 'random_forest' if validation['random_forest']['f1']>validation['baseline']['f1'] else 'baseline'
    # Model choice is fixed before the untouched test split is read for evaluation.
    predictions = {name:model.predict(samples['test']['X']) for name,model in models.items()}
    test = {name:metrics(samples['test']['y'],prediction) for name,prediction in predictions.items()}
    failures = []
    for index in np.flatnonzero(predictions[selected]!=samples['test']['y'])[:20]:
        failures.append({'site':samples['test']['sites'][index],'date_row_col':samples['test']['pixels'][index],
                         'reference':int(samples['test']['y'][index]),'prediction':int(predictions[selected][index])})
    output.mkdir(parents=True)
    for name,model in models.items():
        path = output/(name+'.joblib')
        joblib.dump(model,path,compress=3)
        assert np.array_equal(joblib.load(path).predict(samples['test']['X']),predictions[name])
    evaluation = {'selected_model':selected,'selection_rule':'higher validation forest F1; baseline wins ties',
                  'synthetic_fixture':bool(label_check.get('synthetic_fixture',False)),
                  'validation':validation,'test':test,'failure_pixels':failures,
                  'split_counts':{s:{'pixels':len(g['y']),'sites':len(set(g['sites']))} for s,g in samples.items()},
                  'limits':'Declared independent references; pixel metrics are spatially correlated. No legal-status, fire or whole-area change inference.'}
    manifest = {'selected_model_file':selected+'.joblib','class_mapping':{'0':'non_forest','1':'forest'},
                'synthetic_fixture':bool(label_check.get('synthetic_fixture',False)),
                'feature_order':order,'input_band_order':coverage['band_order'],'resolution_m':20,
                'preprocessing':'Use verified calibrated feature export; do not apply reflectance scaling again.',
                'observation_processing':source_report['acquisitions'],
                'forest_definition_version':'forestguard-cover-v1',
                'input_hashes':{'bundle':coverage['bundle_sha256'],'boundary':coverage['boundary_sha256'],
                                'labels':hashlib.sha256(Path(labels).read_bytes()).hexdigest()},
                'versions':dict(coverage['runtime'],sklearn=sklearn.__version__,joblib=joblib.__version__),
                'random_seed':42,'model_parameters':{name:model.get_params() for name,model in models.items()},
                'label_audit':label_check,'model_roundtrip_checked':True,'operational_use_approved':False}
    source_root = Path(__file__).resolve().parents[1]
    for relative in ['cloud/research_features.py','docs/FOREST_COVER_DEFINITION.md']:
        path = source_root/relative
        (output/path.name).write_bytes(path.read_bytes())
    manifest['input_hashes']['definition'] = hashlib.sha256((output/'FOREST_COVER_DEFINITION.md').read_bytes()).hexdigest()
    manifest['feature_code_sha256'] = hashlib.sha256((output/'research_features.py').read_bytes()).hexdigest()
    dataset_inputs = {'imagery_bundle':manifest['input_hashes']['bundle'],'boundary':manifest['input_hashes']['boundary'],
                      'labels':manifest['input_hashes']['labels'],'forest_definition_document':manifest['input_hashes']['definition']}
    manifest['dataset_version'] = 'compartment-279-'+hashlib.sha256(json.dumps(dataset_inputs,sort_keys=True).encode()).hexdigest()[:16]
    manifest['model_version'] = selected+'-'+hashlib.sha256((output/(selected+'.joblib')).read_bytes()).hexdigest()[:16]
    if manifest['synthetic_fixture']:
        manifest['dataset_version'] = 'synthetic-'+manifest['dataset_version']
        manifest['model_version'] = 'synthetic-'+manifest['model_version']
    (output/'evaluation.json').write_text(json.dumps(evaluation,indent=2)+'\n')
    (output/'model_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (output/'labels.geojson').write_bytes(Path(labels).read_bytes())
    files = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    (output/'checksums.json').write_text(json.dumps(files,indent=2)+'\n')
    with zipfile.ZipFile(output.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
        for path in output.iterdir():
            archive.write(path,path.name)
    return output.with_suffix('.zip')
