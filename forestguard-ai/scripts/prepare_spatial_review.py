"""Select spatially spread, unlabeled patches from verified study/clear masks only."""
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform

from audit_labels import audit
from prepare_liss4_review import prepare
from register_research_ui import ROOT,OUTPUT,BUNDLE,verify_registration
from review_labels import build,PACK


def choose(valid):
    if valid.ndim!=2 or max(valid.shape)>512 or valid.dtype!=np.dtype('bool'):
        raise ValueError('Expected bounded boolean usable-study grid.')
    selected=[];empty=[]
    rows=np.linspace(0,valid.shape[0],5,dtype=int)
    cols=np.linspace(0,valid.shape[1],5,dtype=int)
    for y in range(4):
        for x in range(4):
            centre=((rows[y]+rows[y+1])/2,(cols[x]+cols[x+1])/2)
            candidates=[]
            for row in range(2,valid.shape[0]-6,5):
                for col in range(2,valid.shape[1]-6,5):
                    if not (rows[y]<=row+2.5<rows[y+1] and cols[x]<=col+2.5<cols[x+1]):continue
                    if not valid[row-2:row+7,col-2:col+7].all():continue
                    distance=(row+2.5-centre[0])**2+(col+2.5-centre[1])**2
                    candidates.append((distance,row,col))
            for _,row,col in sorted(candidates):
                separated=all(np.hypot(max(0,row-(r+5),r-(row+5)),max(0,col-(c+5),c-(col+5)))*20>=100
                              for _,r,c in selected)
                if separated:
                    selected.append((y*4+x+1,row,col));break
            else:empty.append(y*4+x+1)
    if not selected:raise ValueError('No fully clear patches with the study/quality buffer.')
    return selected,empty


def generate(output):
    output=Path(output)
    if output.exists():raise ValueError('Output exists; preserve it and choose a new folder.')
    verify_registration(OUTPUT)
    record=json.loads((OUTPUT/'registered.json').read_bytes())
    with rasterio.open(OUTPUT/'common_usable.tif') as raster:
        with rasterio.open(OUTPUT/'dry/study_mask.tif') as study:
            valid=(raster.read(1)==1)&(study.read(1)==1)
        grid=raster.transform;crs=raster.crs
    selected,empty=choose(valid)
    base=json.loads((PACK/'reviewer_cases.geojson').read_bytes())['features'][0]['properties']
    features=[];locations=[]
    for index,(block,row,col) in enumerate(selected,1):
        points=[grid*(c,r) for c,r in [(col,row),(col+5,row),(col+5,row+5),(col,row+5),(col,row)]]
        x,y=transform(crs,'EPSG:4326',[p[0] for p in points],[p[1] for p in points])
        props=dict(base,label_id=f'279-spatial-{index:03d}',
                   uncertainty_notes='Unlabeled mask-based spatial candidate; height, canopy and land use need evidence-supported review.')
        features.append({'type':'Feature','geometry':{'type':'Polygon','coordinates':[[list(p) for p in zip(x,y)]]},'properties':props})
        locations.append({'label_id':props['label_id'],'block':block,'row':row,'col':col,'valid_patch_pixels':25})
    document={'type':'FeatureCollection','features':features}
    audit(document)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='spatial_review_',dir=output.parent) as temporary:
        folder=Path(temporary)
        cases=folder/'candidates.geojson';cases.write_text(json.dumps(document,indent=2)+'\n')
        reference=ROOT/'data/reference/bhoonidhi_20261009/november_crop_v1/liss4_279_reference.zip'
        comparison=prepare(BUNDLE,reference,cases,folder/'comparison',blind=True,patch_side_m=100,mask_selected=True)
        build(folder/'form',folder/'comparison')
        summary={'status':'PASS','selection_method':'Deterministic 4-by-4 spatial strata; closest eligible 100 m patch to each block centre.',
                 'selection_inputs':'Verified common usable pixels AND study mask only; no spectra, indices, weak classes or model predictions.',
                 'source_version':record['version'],'common_mask_sha256':hashlib.sha256((OUTPUT/'common_usable.tif').read_bytes()).hexdigest(),
                 'grid_resolution_m':20,'patch_side_m':100,'quality_buffer_m':40,'minimum_between_patch_gap_m':100,
                 'candidate_count':len(features),'empty_blocks':empty,'locations':locations,
                 'reference_coverage':comparison['patch_coverage'],'classes_generated':0,'evaluation_splits_frozen':False,
                 'limits':'Spatial review candidates, not probability sampling or a representative independent test set. Masked/edge areas are excluded; original boundary positional accuracy is unverified.'}
        (folder/'selection_report.json').write_text(json.dumps(summary,indent=2)+'\n')
        folder.rename(output)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(generate(args.output),indent=2))
