"""Create bounded, offline error-context views; never assign reviewed forest labels."""
import argparse
import base64
import hashlib
import html
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import joblib
import numpy as np
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom

from assess_observation_pair import assess
from verify_weak_export import verify
from verify_liss4_crop import verify as verify_reference

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'cloud'))
from train_weak_proxy import inspect_dataset

DATA=ROOT/'data/phase2/weak_december_experiment_v1/weak_experiment.zip'
DATA_SHA='b4d93e7db778b51addcea7e9c574e1f593b56c48786778a1629cf3921cf7f8ec'
MODEL=ROOT/'data/phase3/weak_december_run_v1/forestguard_weak_proxy_run1.zip'
MODEL_SHA='8bf0858faaee969b35e003c466de19ab1767a96c5c8ed9098cb8010f13d3a6b8'
BEFORE=ROOT/'data/study/compartment_279_v1/december_2024_v1/forestguard_279_research.zip'
AFTER=ROOT/'data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip'
REFERENCE=ROOT/'data/reference/bhoonidhi_20261009/november_crop_v1/liss4_279_reference.zip'
NAMES={10:'Tree cover',20:'Shrubland',30:'Grassland',40:'Cropland',60:'Bare/sparse vegetation',80:'Permanent water'}


def choose(pixels,codes,predicted,shape):
    selected=[]
    for code in [20,40,10]:
        found=0
        for index in np.flatnonzero((codes==code)&(predicted!=(codes==10))):
            row,col=map(int,pixels[index])
            if not (2<=row<shape[0]-2 and 2<=col<shape[1]-2):continue
            if any(np.hypot(row-r,col-c)*20<150 for _,r,c in selected):continue
            selected.append((int(index),row,col));found+=1
            if found==3:break
    if not selected:raise ValueError('No supported disagreement contexts.')
    return selected


def generate(output):
    output=Path(output)
    if output.exists():raise ValueError('Preserve existing error inspection output.')
    output.parent.mkdir(parents=True,exist_ok=True)
    model_check=verify(MODEL,MODEL_SHA,DATA,DATA_SHA)
    samples,manifest=inspect_dataset(DATA,DATA_SHA)
    reference_check=verify_reference(REFERENCE)
    with tempfile.TemporaryDirectory(prefix='proxy_errors_',dir=output.parent) as temporary:
        folder=Path(temporary)
        pair=assess(BEFORE,AFTER,folder/'pair')
        if pair['source_sha256']['before']!=manifest['source_hashes']['before_bundle'] or pair['source_sha256']['after']!=manifest['source_hashes']['bundle']:
            raise ValueError('Imagery differs from the fitted dataset.')
        with zipfile.ZipFile(MODEL) as archive:
            model=joblib.load(io.BytesIO(archive.read('random_forest.joblib')))
        model.n_jobs=1
        predicted=model.predict(samples['validation_X'])
        with zipfile.ZipFile(AFTER) as archive,MemoryFile(archive.read('post_monsoon/worldcover_2021_weak.tif')) as memory,memory.open() as raster:
            weak=raster.read(1);grid=raster.transform;crs=raster.crs;shape=raster.shape
        rows,cols=samples['validation_pixels'].T
        codes=weak[rows,cols]
        if not np.array_equal(samples['validation_y'],(codes==10).astype('uint8')):raise ValueError('Proxy target grid mismatch.')
        selected=choose(samples['validation_pixels'],codes,predicted,shape)
        features=[]
        for number,(index,row,col) in enumerate(selected,1):
            points=[grid*(c,r) for c,r in [(col-2,row-2),(col+3,row-2),(col+3,row+3),(col-2,row+3),(col-2,row-2)]]
            geometry=transform_geom(crs,'EPSG:4326',{'type':'Polygon','coordinates':[points]})
            features.append({'type':'Feature','geometry':geometry,'properties':{'case_id':f'279-proxy-error-{number:02d}',
                'validation_sample_index':index,'row':row,'col':col,'reference_code':int(codes[index]),
                'reference_name':NAMES[int(codes[index])],'prediction':'tree-cover proxy' if predicted[index]==1 else 'other-cover proxy',
                'class':'unknown','review_status':'unreviewed','reference_independent':False,'split':'unassigned',
                'observation_date':'2025-12-09','context_side_m':100,'limits':'Prediction/target describe the central 20 m pixel, not this entire 100 m context footprint.'}})
        views=[[] for _ in features]
        layers=[(BEFORE,'post_monsoon/features.tif','post_monsoon/preview.png','2024-12-16','Natural colour; 20 m analysis grid'),
                (REFERENCE,'raw_dn.tif','false_colour_NIR_red_green.png',None,'NIR/red/green false colour; native 5.8 m detail, 5 m grid spacing. Red does not mean forest; nonzero pixels are not a cloud mask.'),
                (AFTER,'post_monsoon/features.tif','post_monsoon/preview.png','2025-12-09','Natural colour; 20 m analysis grid')]
        reference_coverage=[]
        for path,raster_name,image_name,date,caption in layers:
            with zipfile.ZipFile(path) as archive,MemoryFile(archive.read(raster_name)) as memory,memory.open() as raster:
                if path==REFERENCE:date=json.loads(archive.read('crop_report.json'))['capture_date']
                encoded=base64.b64encode(archive.read(image_name)).decode('ascii')
                available=~(raster.read()==0).all(axis=0) if path==REFERENCE else None
                for i,feature in enumerate(features):
                    projected=transform_geom('EPSG:4326',raster.crs,feature['geometry'])
                    vertices=[~raster.transform*tuple(p) for p in projected['coordinates'][0]]
                    left,top=min(p[0] for p in vertices),min(p[1] for p in vertices)
                    width,height=max(p[0] for p in vertices)-left,max(p[1] for p in vertices)-top
                    polygon=' '.join(f'{x:.4f},{y:.4f}' for x,y in vertices)
                    views[i].append(f'<section><h3>{date}</h3><svg viewBox="{left-width:.4f} {top-height:.4f} {width*3:.4f} {height*3:.4f}" role="img" aria-label="{feature["properties"]["case_id"]}, {date} context"><image width="{raster.width}" height="{raster.height}" href="data:image/png;base64,{encoded}"/><polygon points="{polygon}" fill="none" stroke="#ffff00" stroke-width="0.3"/></svg><p>{html.escape(caption)}</p></section>')
                    if available is not None:
                        from rasterio.features import geometry_mask
                        patch=geometry_mask([projected],raster.shape,raster.transform,invert=True)
                        reference_coverage.append({'case_id':feature['properties']['case_id'],'context_pixels':int(patch.sum()),'nonzero_pixels':int((patch&available).sum())})
        cards=[]
        for feature,panels in zip(features,views):
            props=feature['properties']
            cards.append(f'<article><h2>{props["case_id"]}</h2><p>Historical 2021 map: {props["reference_name"]}. December 2025 model: {props["prediction"]}. Central 20 m pixel only; yellow outline is a 100 m context. Reviewed class: unknown.</p><div class="views">{"".join(panels)}</div></article>')
        page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compartment 279 proxy disagreements</title><style>body{font:16px system-ui;background:#f3f7f3;color:#173b2d;margin:24px}.views{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}svg{width:100%;background:#173b2d}article{border-top:1px solid #bacaba;margin-top:24px}h3{margin-bottom:8px}@media(max-width:750px){.views{grid-template-columns:1fr}}</style><h1>Compartment 279: proxy disagreements</h1><p>Research-only diagnostic selection from validation errors, not independent or representative forest evaluation. These examples show disagreements with an old map; no forest labels, causes, changes or fire conclusions are assigned.</p><p>Up to three shrub, crop and tree cases; row-order selection with at least 150 m between centres. Context includes neighboring and potentially masked pixels. Images are different dates/sensors and are not evidence of stand height, land use or legal forest status.</p>'+''.join(cards)+'<p>Contains modified Copernicus Sentinel data 2024/2025; ISRO-IRS reference imagery. WorldCover 2021 v200, CC BY 4.0. Original source metadata and license records retained.</p></html>'
        (folder/'inspection.html').write_text(page,encoding='utf-8')
        (folder/'diagnostic_cases.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},indent=2)+'\n')
        breakdown={str(int(c)):{'validation_samples':int((codes==c).sum()),'disagreements':int(((codes==c)&(predicted!=samples['validation_y'])).sum())} for c in np.unique(codes)}
        report={'status':'PASS','case_count':len(features),'selection':'Validation disagreements only; up to three each for shrub/crop/tree; deterministic row order, 150 m centre separation.',
                'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BEFORE,AFTER,REFERENCE,DATA,MODEL]},
                'model_integrity':model_check,'reference_integrity':reference_check,'reference_nonzero_coverage':reference_coverage,
                'by_reference_class':breakdown,'labels_assigned':0,'independent_forest_accuracy_measured':False,'operational_use_approved':False,
                'limits':'Post-validation error inspection. Historical-map disagreement does not prove a model error against current forest truth. No independent reviewer available.'}
        (folder/'inspection_report.json').write_text(json.dumps(report,indent=2)+'\n')
        folder.rename(output)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    print(json.dumps(generate(parser.parse_args().output),indent=2))
