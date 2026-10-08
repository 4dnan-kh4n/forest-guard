"""Summarize measured features in pending review footprints; never generate labels."""
import argparse
import json
import zipfile
from pathlib import Path

import numpy as np
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom


def median_patch(values):
    valid=np.ma.asarray(values).compressed()
    if not len(valid) or not np.isfinite(valid).all(): raise ValueError('Empty or nonfinite review values.')
    return float(np.median(valid))


if __name__=='__main__':
    assert median_patch(np.ma.array([1,3,99],mask=[False,False,True]))==2
    try:median_patch(np.ma.masked_all(2))
    except ValueError:pass
    else:raise AssertionError('Empty masked patch accepted')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path);parser.add_argument('cases',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.output.exists(): raise ValueError('Existing inspection report; choose a new output.')
    cases=json.loads(args.cases.read_text(encoding='utf-8'))['features']
    result=[{'case':case['properties']['label_id'],'historical_hint':case['properties']['weak_class_name'],
             'observations':[]} for case in cases]
    with zipfile.ZipFile(args.bundle) as archive:
        report=json.loads(archive.read('research_report.json'))
        for observation in report['acquisitions']:
            with MemoryFile(archive.read(observation['season']+'/features.tif')) as memory,memory.open() as raster:
                values=raster.read(masked=True)
                assert max(raster.shape)<=256
                for case,record in zip(cases,result):
                    footprint=transform_geom('EPSG:4326',raster.crs,case['geometry'])
                    mask=geometry_mask([footprint],out_shape=raster.shape,transform=raster.transform,invert=True)
                    count=int(mask.sum())
                    if not count or np.ma.getmaskarray(values[:,mask]).any(): raise ValueError('Review footprint contains unavailable features.')
                    record['observations'].append({'date':observation['acquisition'],'pixel_count':count,
                        'median_features':{name:median_patch(values[raster.descriptions.index(name),mask])
                         for name in ['B04','B08','B11','NDVI','NDVI_STD_3X3']}})
    assert all(len(r['observations'])==len(report['acquisitions']) for r in result)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('PASS: masked medians, finite complete footprint features and overwrite protection; no labels created.')
