"""Prepare real-image samples with historical weak-map targets; not reviewed forest labels."""
import argparse
import hashlib
import json
import tempfile
import zipfile
from contextlib import ExitStack
from pathlib import Path

import numpy as np
from rasterio.io import MemoryFile

from inspect_research import inspect
from register_research_ui import ROOT,BUNDLE,BOUNDARY


def spatial_masks(shape):
    if len(shape)!=2 or max(shape)>512 or min(shape)<20:raise ValueError('Expected a bounded crop grid.')
    rows=np.arange(shape[0])[:,None]
    cut=shape[0]//2
    return {'train':np.broadcast_to(rows<cut-5,shape),'validation':np.broadcast_to(rows>=cut+5,shape)}


def prepare(output,before=None):
    output=Path(output)
    if output.exists():raise ValueError('Preserve existing experiment; choose a new output folder.')
    checked=inspect(BUNDLE,BOUNDARY)
    output.parent.mkdir(parents=True,exist_ok=True)
    pair=None
    if before is not None:
        from assess_observation_pair import assess
        with tempfile.TemporaryDirectory(prefix='weak_pair_',dir=output.parent) as temporary:
            pair=assess(before,BUNDLE,Path(temporary)/'assessment')
        if pair['status']!='PASS_DATA_CHECKS':raise ValueError('Insufficient same-season common coverage.')
    arrays={};groups={}
    with ExitStack() as stack:
        source=stack.enter_context(zipfile.ZipFile(BUNDLE))
        earlier=stack.enter_context(zipfile.ZipFile(before)) if before is not None else None
        report=json.loads(source.read('research_report.json'))
        records={item['season']:item for item in report['acquisitions']}
        if set(records)!={'dry','post_monsoon'}:raise ValueError('Expected the preserved two-date research source.')
        earlier_record=next(item for item in json.loads(earlier.read('research_report.json'))['acquisitions'] if item['season']=='post_monsoon') if earlier else None
        for group,season in [('train','post_monsoon' if earlier else 'dry'),('validation','post_monsoon')]:
            imagery=earlier if earlier and group=='train' else source
            record=earlier_record if imagery is earlier and earlier else records[season]
            def read(name):
                archive=source if name=='worldcover_2021_weak' else imagery
                with MemoryFile(archive.read(season+'/'+name+'.tif')) as memory,memory.open() as raster:
                    return raster.read()
            values=read('features');weak=read('worldcover_2021_weak')[0]
            usable=read('usable_mask')[0]==1;inside=read('study_mask')[0]==1
            regions=spatial_masks(weak.shape)
            valid=usable&inside&regions[group]&np.isfinite(values).all(axis=0)&np.isin(weak,[10,20,30,40,50,60,70,80,90,95,100])
            rows,cols=np.where(valid)
            X=values[:,valid].T.astype('float32');y=(weak[valid]==10).astype('uint8')
            if not 0<len(y)<=10000 or set(np.unique(y))!={0,1}:raise ValueError('Both proxy classes and bounded samples required per group.')
            arrays[group+'_X']=X;arrays[group+'_y']=y;arrays[group+'_pixels']=np.stack([rows,cols],axis=1).astype('int32')
            groups[group]={'acquisition_date':record['acquisition'][:10],'scene_id':record['scene_id'],
                           'samples':len(y),'proxy_class_counts':{str(c):int((y==c).sum()) for c in [0,1]},
                           'region':'north' if group=='train' else 'south'}
        if groups['train']['acquisition_date']==groups['validation']['acquisition_date']:raise ValueError('Observation dates must differ.')
        reference=report['weak_reference']
        manifest={'format':'forestguard-weak-proxy-dataset-v1','reference_kind':'weak_map',
                  'reference_independent':False,'reviewed_labels_exist':False,'independent_test_set_exists':False,
                  'operational_use_approved':False,'target':'Historical WorldCover tree-cover-map agreement; not current forest cover',
                  'class_mapping':{'0':'WorldCover 2021 other known land cover','1':'WorldCover 2021 tree cover'},
                  'groups':groups,'split_rule':'Choose north training/south validation regions before sampling; 10-row (200 m) excluded strip and different observation dates.',
                  'feature_order':records['dry']['feature_order'],'band_order':checked['band_order'],'resolution_m':20,
                  'preprocessing':'Preserved calibrated 15-feature crops. No additional reflectance scaling.',
                  'reference':reference,'source_hashes':{'bundle':checked['bundle_sha256'],'boundary':checked['boundary_sha256']},
                  'limits':'2021 model-generated map targets paired with real imagery. Tree cover includes agricultural trees/plantations. Spatial/date validation against the same historical teacher is not independent forest accuracy. No test set, forest area, changes or fire predictions.'}
        if pair:
            manifest['source_hashes']['before_bundle']=pair['source_sha256']['before']
            manifest['observation_pair']=pair
            manifest['reference_year_gap_by_group']={key:int(value['acquisition_date'][:4])-2021 for key,value in groups.items()}
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='weak_dataset_',dir=output.parent) as temporary:
        folder=Path(temporary)
        np.savez_compressed(folder/'samples.npz',**arrays)
        manifest['dataset_version']='weak-proxy-279-'+hashlib.sha256((folder/'samples.npz').read_bytes()).hexdigest()[:16]
        (folder/'dataset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
        (folder/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n')
        with zipfile.ZipFile(folder/'weak_experiment.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for name in ['samples.npz','dataset_manifest.json','checksums.json']:archive.write(folder/name,name)
        folder.rename(output)
    return {'status':'PASS','groups':groups,'zip_bytes':(output/'weak_experiment.zip').stat().st_size,
            'zip_sha256':hashlib.sha256((output/'weak_experiment.zip').read_bytes()).hexdigest(),
            'independent_forest_accuracy_measured':False,'production_training_gate_changed':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    parser.add_argument('--before',type=Path,help='Verified earlier December bundle; reuse the preserved 2021 weak map on its identical grid.')
    args=parser.parse_args();print(json.dumps(prepare(args.output,args.before),indent=2))
