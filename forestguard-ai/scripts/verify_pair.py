"""Verify two real stored observations and export a versioned pipeline registry."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from inspect_local import inspect


def verify_pair(folder):
    folder=Path(folder).resolve(strict=True)
    sample_names={'forestguard_phase0.zip','source.json','report.json','reflectance.tif','scl.tif','study.tif','usable.tif','preview.png','checksums.json'}
    expected={f'date_{i}/{name}' for i in [1,2] for name in sample_names}
    expected |= {'pair_report.json','boundary_input.geojson','candidate_mask.tif','common_usable.tif','pair_preview.png'}
    with zipfile.ZipFile(folder/'phase2_pair.zip') as archive:
        if set(archive.namelist()) != expected|{'pair_checksums.json'} or len(archive.infolist())!=len(expected)+1:
            raise ValueError('Unexpected pair archive members.')
        if sum(i.file_size for i in archive.infolist())>30*1024**2:
            raise ValueError('Pair archive exceeds bounded size.')
        manifest=json.loads(archive.read('pair_checksums.json'))
        if set(manifest)!=expected:
            raise ValueError('Pair checksum manifest mismatch.')
        for name,record in manifest.items():
            content=archive.read(name)
            path=folder/name
            if len(content)!=record['bytes'] or hashlib.sha256(content).hexdigest()!=record['sha256']:
                raise ValueError(f'Archive integrity failure: {name}')
            if path.stat().st_size!=record['bytes']:
                raise ValueError(f'Extracted size mismatch: {name}')
            with path.open('rb') as stream:
                if hashlib.file_digest(stream,'sha256').hexdigest()!=record['sha256']:
                    raise ValueError(f'Extracted integrity failure: {name}')
    reports=[inspect(folder/f'date_{i}') for i in [1,2]]
    pair=json.loads((folder/'pair_report.json').read_text())
    boundary=json.loads((folder/'boundary_input.geojson').read_text())
    if boundary['features'][0]['properties']['pilot_approved'] is not False or pair['source_boundary_sha256']!=boundary['features'][0]['properties']['source_sha256']:
        raise ValueError('Candidate status/source mismatch.')
    if pair['pilot_approved'] or pair['model_trained'] or pair['reviewed_label_count'] or pair['splits_frozen']:
        raise ValueError('Pipeline pair must not claim study approval, labels, model or frozen splits.')
    if [r['scene_id'] for r in reports]!=pair['scene_ids'] or [r['acquisition'] for r in reports]!=pair['dates']:
        raise ValueError('Pair provenance mismatch.')
    raw_first=json.loads((folder/'date_1/report.json').read_text())
    for key in ['shape','crs','transform','band_order']:
        if pair[key]!=raw_first[key]: raise ValueError(f'Pair grid metadata mismatch: {key}')
    with rasterio.Env(PROJ_NETWORK='OFF',GDAL_CACHEMAX=32*1024**2):
        with rasterio.open(folder/'date_1/usable.tif',driver='GTiff') as a, rasterio.open(folder/'date_2/usable.tif',driver='GTiff') as b, rasterio.open(folder/'candidate_mask.tif',driver='GTiff') as c, rasterio.open(folder/'common_usable.tif',driver='GTiff') as d:
            for raster in [b,c,d]:
                if raster.shape!=a.shape or raster.crs!=a.crs or raster.transform!=a.transform or raster.count!=1:
                    raise ValueError('Dates/masks are not on the same grid.')
            if max(a.shape)>512:
                raise ValueError('Crop exceeds size bound.')
            geometry=transform_geom('EPSG:4326',a.crs,boundary['features'][0]['geometry'])
            inside=geometry_mask([geometry],out_shape=a.shape,transform=a.transform,invert=True,all_touched=False)
            if not np.array_equal(c.read(1),inside):
                raise ValueError('Candidate raster mask differs from source geometry.')
            va,vb=a.read(1).astype(bool)&inside,b.read(1).astype(bool)&inside
            common=va&vb
            if not np.array_equal(d.read(1),common):
                raise ValueError('Common valid mask differs from both dates.')
            measured={'candidate_pixels':int(inside.sum()),'usable_pixels_by_date':[int(va.sum()),int(vb.sum())],
                      'common_usable_pixels':int(common.sum())}
            for key,value in measured.items():
                if pair[key]!=value: raise ValueError(f'Pair count mismatch: {key}')
            if abs(pair['common_usable_fraction']-common.sum()/inside.sum())>1e-12:
                raise ValueError('Pair coverage denominator mismatch.')
    entries=[]
    for i,result in enumerate(reports,1):
        raw=json.loads((folder/f'date_{i}/report.json').read_text())
        entries.append({'id':result['scene_id'],'acquisition':result['acquisition'],
            'sample_bundle_sha256':result['sample_bundle_sha256'],'band_order':result['band_order'],
            'crs':result['crs'],'resolution_m':10,'calibration':raw['calibration'],
            'quality_rule':raw['quality_rule'],'scl_resampling':raw['scl_resampling'],
            'source_url':raw['metadata_url'],'license_url':raw['license_url'],'attribution':raw['attribution'],
            'cloud_runtime':raw['runtime'],'local_runtime':result['runtime'],'use':'pipeline checks only'})
    version=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()[:16]
    return {'dataset_version':f'pipeline-{version}','integrity':'PASS','verified_files':len(manifest),
            'grid_alignment':'PASS','common_coverage':measured,'common_usable_fraction':pair['common_usable_fraction'],
            'samples':entries,'role':'pipeline checks only','training_eligible':False,
            'reviewed_label_count':0,'evaluation_splits_frozen':False,
            'forest_loss_ha':None,'forest_gain_ha':None}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        result=verify_pair(args.folder)
        if args.output.exists(): raise ValueError('Registry exists; choose a new output path.')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:result[k] for k in ['dataset_version','integrity','verified_files','common_coverage','common_usable_fraction','training_eligible']},indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        parser.exit(1,f'Pair verification failed: {error}\n')
