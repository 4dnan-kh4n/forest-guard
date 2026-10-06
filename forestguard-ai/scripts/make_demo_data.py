"""Generate a small reproducible synthetic fixture; no real forest observations."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

SIZE=128
SPLITS=[('train',0,40,'2023-03-21'),('validation',56,80,'2024-03-21'),('test',96,128,'2025-03-21')]


def generate(output, seed=42):
    output=Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output is nonempty; choose a new directory to preserve existing artifacts.')
    output.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    row,col=np.indices((SIZE,SIZE))
    # Fictional metric grid, unrelated to any verified Joga polygon.
    grid=from_origin(500000,2500000,10,10)
    geometry={'type':'Polygon','coordinates':[[[500000,2500000],[501280,2500000],
        [501280,2498720],[500000,2498720],[500000,2500000]]]}
    (output/'assumed_study_area.json').write_text(json.dumps({
        'data_kind':'synthetic','geometry_crs':'EPSG:32643','geometry':geometry,
        'description':'Fictional 1.28 km square fixture, not the Joga beat boundary',
        'official_boundary':False},indent=2))
    forest=((row//16+col//20)%3!=0)&((row-64)**2+(col-64)**2<70**2)
    prototypes=np.array([[.11,.14,.18,.25],[.045,.09,.04,.43]],dtype='float32')
    samples=[]
    for split,start,end,simulated_date in SPLITS:
        folder=output/split; folder.mkdir()
        split_mask=(col>=start)&(col<end)
        usable=rng.random((SIZE,SIZE))>.04
        uncertain=(row+2*col)%47==0
        labels=np.where(forest,1,0).astype('uint8')
        labels[~split_mask|~usable|uncertain]=255
        values=prototypes[forest.astype('uint8')].transpose(2,0,1)
        values=np.clip(values+rng.normal(0,.012,values.shape),0,1).astype('float32')
        # Simulated green agricultural pixels overlap some forest-like spectra.
        crop_like=(~forest)&((row//12+col//13)%4==0)
        values[3,crop_like]=.37+rng.normal(0,.012,int(crop_like.sum()))
        values[:,~usable]=-9999
        profile=dict(driver='GTiff',height=SIZE,width=SIZE,crs='EPSG:32643',
                     transform=grid,compress='deflate')
        with rasterio.open(folder/'reflectance.tif','w',**profile,count=4,dtype='float32',nodata=-9999) as dst:
            dst.write(values); dst.descriptions=('B02','B03','B04','B08')
            dst.update_tags(data_kind='synthetic',split=split,simulated_date=simulated_date)
        for name,array in [('labels',labels),('usable',usable.astype('uint8')),('split_mask',split_mask.astype('uint8'))]:
            with rasterio.open(folder/f'{name}.tif','w',**profile,count=1,dtype='uint8',
                               nodata=255 if name=='labels' else None) as dst:
                dst.write(array,1); dst.update_tags(data_kind='synthetic')
        rgb=(np.clip(values[[2,1,0]]/.3,0,1)*255).astype('uint8')
        with rasterio.open(folder/'preview.png','w',driver='PNG',height=SIZE,width=SIZE,
                           count=3,dtype='uint8',crs=profile['crs'],transform=grid) as dst:
            dst.write(rgb)
        with rasterio.open(folder/'labels.tif') as saved:
            assert np.array_equal(saved.read(1),labels)
        with rasterio.open(folder/'reflectance.tif') as saved:
            assert np.array_equal(saved.read(),values) and saved.transform==grid
        counts={str(c):int(((labels==c)&split_mask).sum()) for c in [0,1,255]}
        assert counts['0']>0 and counts['1']>0
        samples.append({'split':split,'simulated_date':simulated_date,'directory':split,
            'columns':[start,end],'synthetic_class_counts_inside_split':counts,
            'label_origin':'procedural generator; not independently reviewed ground truth'})
    manifest={'data_kind':'synthetic','purpose':'demonstration/testing only',
        'seed':seed,'numpy_version':np.__version__,'shape':[SIZE,SIZE],
        'crs':'EPSG:32643','resolution_m':10,'band_order':['B02','B03','B04','B08'],
        'calibration':'synthetic reflectance-like values generated directly; no satellite scale/offset',
        'class_mapping':{'0':'simulated_non_forest','1':'simulated_forest','255':'unknown_or_excluded'},
        'study_area':'assumed fictional metric grid; not an official forest boundary',
        'split_policy':'disjoint column regions, 160 m gaps, distinct simulated dates; assigned before samples',
        'samples':samples,'reviewed_real_label_count':0,'real_pilot_validation':False,
        'demo_training_eligible':True,'real_forest_training_eligible':False,
        'model_trained':False,'source':'project-generated fixture; no downloaded imagery used'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files={}
    for path in sorted(output.rglob('*')):
        if path.is_file():
            files[path.relative_to(output).as_posix()]={'bytes':path.stat().st_size,
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (output/'checksums.json').write_text(json.dumps(files,indent=2)+'\n')
    with zipfile.ZipFile(output/'synthetic_demo.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name in list(files)+['checksums.json']: archive.write(output/name,arcname=name)
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args()
    try:
        result=generate(args.output,args.seed)
        print(json.dumps({'data_kind':result['data_kind'],'samples':result['samples'],
                          'output':str(args.output),'real_pilot_validation':False},indent=2))
    except (OSError,ValueError) as error:
        parser.exit(1,f'Demo generation failed: {error}\n')
