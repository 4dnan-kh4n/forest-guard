"""Bounded offline map for our trusted weak-map proxy; never operational forest inference."""
import argparse
import base64
import hashlib
import html
import io
import json
import tempfile
import zipfile
from pathlib import Path

import joblib
import numpy as np
import rasterio
import sklearn
from rasterio.io import MemoryFile
from sklearn.ensemble import RandomForestClassifier

from prepare_proxy_errors import ROOT,MODEL,MODEL_SHA,DATA,DATA_SHA,AFTER
from verify_weak_export import verify
from verify_research_bundle import verify as verify_observation


def predict(output):
    output=Path(output)
    if output.exists():raise ValueError('Preserve existing research inference output.')
    verified=verify(MODEL,MODEL_SHA,DATA,DATA_SHA)
    verify_observation(AFTER)
    with zipfile.ZipFile(MODEL) as archive:
        manifest=json.loads(archive.read('model_manifest.json'))
        for name,version in [('numpy',np.__version__),('sklearn',sklearn.__version__),('joblib',joblib.__version__)]:
            if manifest['runtime'][name]!=version:raise ValueError('Inference version mismatch: '+name)
        if hashlib.sha256(AFTER.read_bytes()).hexdigest()!=manifest['source_hashes']['bundle']:
            raise ValueError('Only the verified saved observation from this experiment is supported.')
        model=joblib.load(io.BytesIO(archive.read(manifest['selected_model_file'])))
    if type(model) is not RandomForestClassifier or model.n_features_in_!=15 or not np.array_equal(model.classes_,[0,1]):
        raise ValueError('Unsupported research estimator.')
    model.n_jobs=1
    with zipfile.ZipFile(AFTER) as archive:
        record=next(item for item in json.loads(archive.read('research_report.json'))['acquisitions'] if item['season']=='post_monsoon')
        preview=base64.b64encode(archive.read('post_monsoon/preview.png')).decode('ascii')
        with MemoryFile(archive.read('post_monsoon/features.tif')) as memory,memory.open() as raster:
            if max(raster.shape)>512 or raster.count!=15 or list(raster.descriptions)!=manifest['feature_order']:
                raise ValueError('Unsupported feature crop/order.')
            values=raster.read(masked=True).filled(np.nan);profile=raster.profile.copy()
        masks={}
        for name in ['usable_mask','study_mask']:
            with MemoryFile(archive.read('post_monsoon/'+name+'.tif')) as memory,memory.open() as raster:
                masks[name]=raster.read(1)
        valid=(masks['usable_mask']==1)&(masks['study_mask']==1)
    if not valid.any() or not np.isfinite(values[:,valid]).all():raise ValueError('Invalid observable features.')
    classes=np.full(valid.shape,255,dtype='uint8');votes=np.full(valid.shape,-1,dtype='float32')
    for start in range(0,valid.shape[0],16):
        mask=valid[start:start+16]
        if not mask.any():continue
        batch=values[:,start:start+16][:,mask].T.astype('float32')
        predicted=model.predict(batch);probability=model.predict_proba(batch)[:,1]
        if not np.isin(predicted,[0,1]).all() or not np.isfinite(probability).all() or not ((probability>=0)&(probability<=1)).all():
            raise ValueError('Invalid proxy outputs.')
        classes[start:start+16][mask]=predicted
        votes[start:start+16][mask]=probability
    count={str(label):int((classes==label).sum()) for label in [0,1]}
    study_pixels=int((masks['study_mask']==1).sum())
    report={'format':'forestguard-research-proxy-result-v1','scope':'User-confirmed compartment 279 research polygon, not full Joga beat',
            'acquisition_date':record['acquisition'],'scene_id':record['scene_id'],'model_version':manifest['model_version'],
            'dataset_version':manifest['dataset_version'],'model_sha256':MODEL_SHA,'dataset_sha256':DATA_SHA,
            'observation_sha256':manifest['source_hashes']['bundle'],'model_kind':'exploratory_weak_map_proxy',
            'class_mapping':{'0':'other-cover proxy','1':'tree-cover proxy','255':'unobserved/outside study'},
            'study_mask_pixels':study_pixels,'predicted_pixels':int(valid.sum()),'usable_fraction':float(valid.sum()/study_pixels),
            'class_pixels':count,'resolution_m':20,'crs':str(profile['crs']),'shape':list(valid.shape),
            'vote_meaning':'Uncalibrated mean tree-class probability across fitted decision trees; not accuracy, canopy percentage or validated confidence.',
            'operational_use_approved':False,'independent_forest_accuracy_measured':False,'forest_area_ha':None,
            'forest_loss_ha':None,'forest_gain_ha':None,'local_training_performed':False,
            'limits':'Single-observation research inference. Validation pixels were already used in model selection; this map is not an independent test. Historical reference errors, crop/shrub confusion and uncertain land use remain.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='proxy_prediction_',dir=output.parent) as temporary:
        folder=Path(temporary)
        for name,array,dtype,nodata,description in [('proxy_classes.tif',classes,'uint8',255,'historical_tree_cover_proxy'),('tree_vote_share.tif',votes,'float32',-1,'uncalibrated_tree_class_vote')]:
            settings=dict(profile,count=1,dtype=dtype,nodata=nodata,compress='deflate')
            with rasterio.open(folder/name,'w',**settings) as raster:
                raster.write(array,1);raster.set_band_description(1,description)
                raster.update_tags(model_kind='exploratory_weak_map_proxy',operational_use_approved='false',model_version=manifest['model_version'],acquisition_date=record['acquisition'],independent_forest_accuracy_measured='false')
        cells=''.join(f'<rect x="{col}" y="{row}" width="1" height="1" fill="{"#25b86e" if classes[row,col]==1 else "#e9a345"}"/>' for row,col in zip(*np.where(valid)))
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {valid.shape[1]} {valid.shape[0]}" role="img" aria-label="Research tree-cover proxy map"><image width="{valid.shape[1]}" height="{valid.shape[0]}" href="data:image/png;base64,{preview}"/><g opacity="0.7">{cells}</g></svg>'
        (folder/'proxy_preview.svg').write_text(svg,encoding='utf-8')
        page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compartment 279 research proxy map</title><style>body{font:16px system-ui;color:#173b2d;background:#f3f7f3;max-width:1000px;margin:24px auto;padding:16px}svg{width:100%;background:#173b2d;image-rendering:pixelated}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Research tree-cover proxy — compartment 279</h1><p>Stored observation: '+record['acquisition'][:10]+'. Green: tree-cover proxy; orange: other-cover proxy. Unobserved/outside-study pixels receive no class.</p><p>This is an unapproved research model trained against a historical map. It does not establish natural forest, deforestation or fire. Model vote values are not calibrated confidence.</p>'+svg+'<p>'+html.escape(record['attribution'])+'</p><h2>Actual output metadata</h2><pre>'+html.escape(json.dumps(report,indent=2))+'</pre></html>'
        (folder/'map.html').write_text(page,encoding='utf-8')
        (folder/'prediction_report.json').write_text(json.dumps(report,indent=2)+'\n')
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
        (folder/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n')
        folder.rename(output)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    print(json.dumps(predict(parser.parse_args().output),indent=2))
