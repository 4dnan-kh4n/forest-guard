"""Register the verified small compartment 279 imagery for the local dashboard."""
import argparse
import os
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

from inspect_research import inspect
from inspect_local import check_files

PROJECT_ROOT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ['FORESTGUARD_DATA_ROOT']) if os.environ.get('FORESTGUARD_DATA_ROOT') else PROJECT_ROOT/('deployment_data' if os.environ.get('VERCEL')=='1' else '.')
BUNDLE=ROOT/'data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip'
BOUNDARY=ROOT/'data/study/compartment_279_v1/boundary.geojson'
OUTPUT=ROOT/'data/app/registered/compartment-279'


def verify_registration(folder):
    folder=Path(folder)
    record=json.loads((folder/'registered.json').read_text(encoding='utf-8'))
    manifest=json.loads((folder/'checksums.json').read_text(encoding='utf-8'))
    expected={'registered.json','boundary.geojson','research_report.json','common_usable.tif'}
    if record['id']!='compartment-279' or record['kind']!='real' or record['model_version'] is not None:
        raise ValueError('Invalid real-imagery registration scope.')
    seasons=[v['id'] for v in record['views']]
    if len(seasons)!=len(set(seasons)) or not seasons or not set(seasons)<={'dry','wet','post_monsoon'}:
        raise ValueError('Invalid observation directories.')
    for season in seasons:
        expected.update(season+'/'+name for name in ['reflectance.tif','preview.png','usable_mask.tif','study_mask.tif','source.json'])
    if set(manifest)!=expected or sum(r['bytes'] for r in manifest.values())>30*1024**2:
        raise ValueError('Registration manifest mismatch/size limit.')
    check_files(folder,manifest)
    coverage=inspect(BUNDLE,BOUNDARY)
    report=json.loads((folder/'research_report.json').read_text(encoding='utf-8'))
    if (record['resolution']!=20 or record['coverage']!=coverage['verification']['common_feature_coverage_fraction']
            or record['verified_files']!=coverage['verification']['verified_files']
            or record['version']!='imagery-279-'+coverage['bundle_sha256'][:16]
            or record['study_area_version']!=json.loads(BOUNDARY.read_bytes())['features'][0]['properties']['study_area_version']
            or seasons!=[item['season'] for item in report['acquisitions']]):
        raise ValueError('Registered coverage/resolution/observations differ from verified source.')
    for view,item in zip(record['views'],report['acquisitions']):
        if any(view[key]!=value for key,value in {'date':item['acquisition'][:10],'scene_id':item['scene_id'],
                'pixels':item['inside_study_pixels'],'usable':item['usable_feature_pixels'],
                'coverage':item['usable_fraction_inside_study'],'forest_ha':None}.items()):
            raise ValueError('Registered observation metadata differs from verified source.')
    if record['source_sha256']!={'bundle':coverage['bundle_sha256'],'boundary':coverage['boundary_sha256']}:
        raise ValueError('Registration source hashes differ from verified project inputs.')
    with zipfile.ZipFile(BUNDLE) as archive:
        for name in expected-{'registered.json','common_usable.tif','boundary.geojson'}:
            if (folder/name).read_bytes()!=archive.read(name):raise ValueError('Registered input differs from verified archive: '+name)
    if (folder/'boundary.geojson').read_bytes()!=BOUNDARY.read_bytes():
        raise ValueError('Registered boundary differs from selected geometry.')
    masks=[]
    for season in seasons:
        with rasterio.open(folder/season/'usable_mask.tif') as raster:masks.append(raster.read(1)==1)
    with rasterio.open(folder/'common_usable.tif') as raster:
        if raster.count!=1 or raster.dtypes!=('uint8',) or raster.nodata!=0:
            raise ValueError('Registered common coverage format mismatch.')
        with rasterio.open(folder/seasons[0]/'usable_mask.tif') as reference:
            if raster.crs!=reference.crs or raster.transform!=reference.transform or raster.shape!=reference.shape:
                raise ValueError('Registered common coverage grid mismatch.')
        if not np.array_equal(raster.read(1),np.logical_and.reduce(masks)):
            raise ValueError('Registered common coverage differs from observation masks.')
    if int(np.logical_and.reduce(masks).sum())!=coverage['verification']['common_feature_valid_pixels']:
        raise ValueError('Registered common coverage count mismatch.')
    return {'status':'PASS','registered_files':len(manifest),'source_files_verified':coverage['verification']['verified_files'],
            'source_inputs_unchanged':True,'forest_accuracy_measured':False}


def register(output=OUTPUT):
    output=Path(output)
    if output.exists():raise ValueError('Registration exists; verify and preserve it instead of overwriting.')
    coverage=inspect(BUNDLE,BOUNDARY)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='registration_',dir=output.parent) as temporary:
        folder=Path(temporary)
        with zipfile.ZipFile(BUNDLE) as archive:
            report=json.loads(archive.read('research_report.json'))
            views=[]
            for item in report['acquisitions']:
                season=item['season'];(folder/season).mkdir()
                for name in ['reflectance.tif','preview.png','usable_mask.tif','study_mask.tif','source.json']:
                    (folder/season/name).write_bytes(archive.read(season+'/'+name))
                views.append({'id':season,'date':item['acquisition'][:10],'name':item['acquisition'][:10],
                              'scene_id':item['scene_id'],'pixels':item['inside_study_pixels'],
                              'usable':item['usable_feature_pixels'],'coverage':item['usable_fraction_inside_study'],
                              'forest_ha':None,'source_license_url':item['source_license_url']})
            (folder/'research_report.json').write_bytes(archive.read('research_report.json'))
        (folder/'boundary.geojson').write_bytes(BOUNDARY.read_bytes())
        from contextlib import ExitStack
        with ExitStack() as stack:
            masks=[stack.enter_context(rasterio.open(folder/v['id']/'usable_mask.tif')) for v in views]
            profile=masks[0].profile.copy();profile.update(compress='deflate',nodata=0)
            with rasterio.open(folder/'common_usable.tif','w',**profile) as target:
                for row in range(0,masks[0].height,16):
                    window=Window(0,row,masks[0].width,min(16,masks[0].height-row))
                    target.write(np.logical_and.reduce([m.read(1,window=window)==1 for m in masks]).astype('uint8'),1,window=window)
        registered={'id':'compartment-279','kind':'real','title':'Compartment 279 · real saved observations',
                    'subtitle':'April and December 2025 · different seasons',
                    'scope':'User-confirmed compartment 279 research polygon · not full Joga beat',
                    'version':'imagery-279-'+coverage['bundle_sha256'][:16],'model_version':None,
                    'study_area_version':json.loads(BOUNDARY.read_bytes())['features'][0]['properties']['study_area_version'],
                    'coverage':coverage['verification']['common_feature_coverage_fraction'],'resolution':20,
                    'verified_files':coverage['verification']['verified_files'],'views':views,
                    'source_sha256':{'bundle':coverage['bundle_sha256'],'boundary':coverage['boundary_sha256']},
                    'attribution':report['acquisitions'][0]['attribution'],'layers':['imagery','coverage','ndvi'],
                    'usable_filename':'usable_mask.tif','study_filename':'study_mask.tif','common_mask':True,
                    'limits':'Different seasons. Inspect imagery and vegetation indicators only; no forest classification, fire detection or forest-cover change measured.'}
        (folder/'registered.json').write_text(json.dumps(registered,indent=2)+'\n',encoding='utf-8')
        manifest={str(p.relative_to(folder)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                  for p in folder.rglob('*') if p.is_file()}
        (folder/'checksums.json').write_text(json.dumps(manifest,indent=2)+'\n')
        checked=verify_registration(folder)
        folder.rename(output)
    return checked


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    print(json.dumps(verify_registration(OUTPUT) if args.verify else register(),indent=2))
