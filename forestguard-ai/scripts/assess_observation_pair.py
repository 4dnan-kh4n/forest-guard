"""Assess aligned same-calendar-season crops; never infer forest area or changes."""
import argparse
import base64
import hashlib
import html
import json
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile

from verify_research_bundle import verify


def season_gap(first,last):
    a,b=[date(2000,d.month,d.day).timetuple().tm_yday for d in [first,last]]
    gap=abs(a-b)
    return min(gap,366-gap)


def assess(before,after,output):
    before,after,output=map(Path,[before,after,output])
    if output.exists():raise ValueError('Keep existing assessment; choose a new folder.')
    checked=[verify(path) for path in [before,after]]
    arrays=[];records=[];features=[];hashes=[];boundaries=[];previews=[]
    for path in [before,after]:
        with zipfile.ZipFile(path) as source:
            report=json.loads(source.read('research_report.json'))
            boundaries.append(json.loads(source.read('boundary.geojson')))
            matches=[item for item in report['acquisitions'] if item['season']=='post_monsoon']
            if len(matches)!=1:raise ValueError('Exactly one saved post-monsoon observation required per bundle.')
            record=matches[0];records.append(record)
            previews.append(base64.b64encode(source.read('post_monsoon/preview.png')).decode('ascii'))
            layers={}
            for name in ['study_mask','usable_mask','features']:
                with MemoryFile(source.read('post_monsoon/'+name+'.tif')) as memory,memory.open() as raster:
                    layers[name]=raster.read(masked=True).filled(0 if name!='features' else np.nan)
            arrays.append(layers)
            hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
    if boundaries[0]['features'][0]['geometry']!=boundaries[1]['features'][0]['geometry'] or boundaries[0]['features'][0]['properties']['study_area_version']!=boundaries[1]['features'][0]['properties']['study_area_version']:
        raise ValueError('Selected study geometry/version differs.')
    if any(records[0][key]!=records[1][key] for key in ['shape','crs','transform','band_order','feature_order']):
        raise ValueError('Crop grids or feature order differ; do not compare unmatched pixels.')
    first,last=[date.fromisoformat(item['acquisition'][:10]) for item in records]
    if first>=last or season_gap(first,last)>14:raise ValueError('Dates must be chronological and within 14 calendar-season days.')
    study=arrays[0]['study_mask'][0]==1
    if not study.any() or not np.array_equal(study,arrays[1]['study_mask'][0]==1):raise ValueError('Study masks differ or are empty.')
    common=study&(arrays[0]['usable_mask'][0]==1)&(arrays[1]['usable_mask'][0]==1)
    if not common.any():raise ValueError('No common observable study pixels.')
    for record,layers in zip(records,arrays):
        if not np.isfinite(layers['features'][:,common]).all():raise ValueError('Invalid common feature values.')
        ndvi=layers['features'][record['feature_order'].index('NDVI')]
        features.append({'date':record['acquisition'][:10],'scene_id':record['scene_id'],
                         'source_license_url':record['source_license_url'],'attribution':record['attribution'],
                         'usable_pixels':int((study&(layers['usable_mask'][0]==1)).sum()),
                         'common_pixel_median_ndvi':round(float(np.median(ndvi[common])),4)})
    result={'status':'PASS_DATA_CHECKS' if common.sum()/study.sum()>=.9 else 'INSUFFICIENT_COMMON_COVERAGE',
            'grid_alignment':'PASS','study_area_version':boundaries[0]['features'][0]['properties']['study_area_version'],
            'crs':records[0]['crs'],'resolution_m':20,'shape':records[0]['shape'],
            'calendar_season_gap_days':season_gap(first,last),'study_mask_pixels':int(study.sum()),
            'common_observable_pixels':int(common.sum()),'common_usable_fraction':float(common.sum()/study.sum()),
            'observations':features,'source_sha256':{'before':hashes[0],'after':hashes[1]},
            'verified_source_files':[c['verified_files'] for c in checked],
            'phenology_weather_comparability_reviewed':False,'forest_area_ha':None,'forest_loss_ha':None,'forest_gain_ha':None,
            'limits':'Calendar-aligned observation assessment only. NDVI differences are vegetation signals, not verified forest changes. Weather, phenology, alignment uncertainty and land-use references still need review.'}
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pair_assessment_',dir=output.parent) as temporary:
        folder=Path(temporary);(folder/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
        panels=''.join(f'<section><h2>{item["date"]}</h2><p>{html.escape(item["scene_id"])}</p><img alt="Saved observation {item["date"]}" src="data:image/png;base64,{preview}"><p>Original per-date valid-pixel preview. Common pixels alone are used in the assessment statistics.</p><p>{html.escape(item["attribution"])}</p></section>' for item,preview in zip(features,previews))
        page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compartment 279 December observations</title><style>body{{font:16px system-ui;background:#f3f7f3;color:#173b2d;margin:24px}}.panels{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}img{{width:100%;background:#1d3329;image-rendering:pixelated}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}@media(max-width:700px){{.panels{{grid-template-columns:1fr}}}}</style><h1>Compartment 279: December observations</h1><p>Selected research polygon; not full Joga beat. Calendar-season difference: {result["calendar_season_gap_days"]} days. Common clear coverage: {result["common_usable_fraction"]:.2%}, {result["common_observable_pixels"]:,} pixels on a 20 m grid.</p><p>No forest classification, forest area, loss/gain or fire inference. Weather and vegetation conditions still need review.</p><div class="panels">{panels}</div><h2>Verified observation metadata</h2><pre>{html.escape(json.dumps(result,indent=2))}</pre></html>'
        (folder/'comparison.html').write_text(page,encoding='utf-8')
        with zipfile.ZipFile(after) as source,MemoryFile(source.read('post_monsoon/study_mask.tif')) as memory,memory.open() as reference:
            profile=reference.profile.copy();profile.update(count=1,dtype='uint8',nodata=0,compress='deflate')
        with rasterio.open(folder/'common_usable.tif','w',**profile) as raster:raster.write(common.astype('uint8'),1)
        folder.rename(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['before','after','output']:parser.add_argument(name,type=Path)
    args=parser.parse_args();print(json.dumps(assess(args.before,args.after,args.output),indent=2))
