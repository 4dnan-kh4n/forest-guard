"""Prepare unlabeled geographic review cases from a verified research ZIP."""
import argparse
import base64
import html
import json
import zipfile
from pathlib import Path

import numpy as np
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom
from verify_research_bundle import verify


def prepare(bundle,output):
    output=Path(output)
    if output.exists():raise ValueError('Review output exists; preserve it and choose a new folder.')
    verification=verify(bundle)
    with zipfile.ZipFile(bundle) as archive:
        report=json.loads(archive.read('research_report.json'))
        boundary=json.loads(archive.read('boundary.geojson'))
        study_version=boundary['features'][0]['properties']['study_area_version']
        reference=report.get('weak_reference')
        if not reference or not report['acquisitions']:
            raise ValueError('Accepted imagery and the historical weak map are needed for review preparation.')
        records=report['acquisitions']
        common=None
        for record in records:
            with MemoryFile(archive.read(record['season']+'/usable_mask.tif')) as memory,memory.open() as raster:
                valid=raster.read(1).astype(bool)
                common=valid if common is None else common & valid
        with MemoryFile(archive.read(records[0]['season']+'/worldcover_2021_weak.tif')) as memory,memory.open() as raster:
            hints=raster.read(1);grid=raster.transform;crs=raster.crs
        template=json.loads((Path(__file__).resolve().parents[1]/'config/label_review_template.geojson').read_text(encoding='utf-8'))
        template['review_status']='UNREVIEWED CASES: classes unknown; no training labels or frozen splits'
        template['source_bundle_verification']=verification
        template['features']=[]
        centres=[]
        for code in [10,20,40,80,30,50,60]:
            count=0
            for row in range(4,hints.shape[0]-4,6):
                for col in range(4,hints.shape[1]-4,6):
                    patch=np.s_[row-3:row+3,col-3:col+3]
                    if not common[patch].all() or not (hints[patch]==code).all():continue
                    x,y=grid*(col,row)
                    if any(np.hypot(x-a,y-b)<240 for a,b in centres):continue
                    left,bottom=x-60,y-60;right,top=x+60,y+60
                    geometry={'type':'Polygon','coordinates':[[[left,bottom],[right,bottom],[right,top],[left,top],[left,bottom]]]}
                    geometry=transform_geom(crs,'EPSG:4326',geometry)
                    properties={key:None for key in template['required_feature_properties']}
                    properties.update({'label_id':f'279-review-{len(centres)+1:03d}','class':'unknown',
                        'observation_date':records[-1]['acquisition'][:10],
                        'observation_dates':[record['acquisition'][:10] for record in records],
                        'reference_source':reference['source_url'],'reference_access_license':reference['license'],
                        'reference_date':'2021 (annual map; exact observation date unavailable)',
                        'reference_kind':'weak_map','reference_independent':False,'review_status':'unreviewed',
                        'uncertainty_notes':'Historical map hint only; inspect current imagery and forest-use/height evidence before labeling.',
                        'study_area_version':study_version,'split':'unassigned',
                        'weak_class_code':code,'weak_class_name':reference['class_mapping'][str(code)],
                        'footprint_m':120,'minimum_case_centre_spacing_m':240})
                    template['features'].append({'type':'Feature','geometry':geometry,'properties':properties})
                    centres.append((x,y));count+=1
                    if count==3:break
                if count==3:break
        if not centres:raise ValueError('No homogeneous, observable review patches found; no cases fabricated.')
        panels=[]
        for record in records:
            image=base64.b64encode(archive.read(record['season']+'/preview.png')).decode('ascii')
            boxes=[]
            for number,(x,y) in enumerate(centres,1):
                col,row=~grid*(x,y)
                boxes.append(f'<rect x="{col-3}" y="{row-3}" width="6" height="6" fill="none" stroke="white" stroke-width="0.4"/>'
                             f'<text x="{col+3.5}" y="{row}" fill="white" font-size="3">{number}</text>')
            height,width=hints.shape
            panels.append(f'<section><h2>{html.escape(record["acquisition"][:10])}</h2>'
                f'<p>{record["usable_fraction_inside_study"]:.2%} valid feature coverage</p>'
                f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Satellite preview with numbered unreviewed cases">'
                f'<image width="{width}" height="{height}" href="data:image/png;base64,{image}"/>{"".join(boxes)}</svg></section>')
        rows=''.join(f'<tr><td>{html.escape(feature["properties"]["label_id"])}</td>'
                     f'<td>{html.escape(feature["properties"]["weak_class_name"])}</td><td>Unknown; unreviewed</td></tr>'
                     for feature in template['features'])
        document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        document+='<title>Compartment 279 research review</title><style>body{font:16px system-ui;max-width:1200px;margin:24px auto;padding:0 20px;color:#18392d;background:#f6f8f5}h1{font-size:28px}.maps{display:flex;gap:24px;flex-wrap:wrap}section{flex:1;min-width:280px}svg{width:100%;background:#071c15}td,th{padding:10px;border-bottom:1px solid #cbd7cd;text-align:left}table{border-collapse:collapse;width:100%}</style>'
        document+='<h1>Compartment 279: reference review preparation</h1><p>Real satellite observations; numbered 120 m review footprints. Gaps show excluded observations. All cases remain unknown. This is not a forest classification or loss report.</p>'
        document+=f'<p>Common valid feature coverage: {verification["common_feature_coverage_fraction"]:.2%}. These seasonal dates support feature review; seasonal colour differences do not establish deforestation.</p><div class="maps">{"".join(panels)}</div>'
        document+=f'<h2>Historical hints to check</h2><p>WorldCover 2021 predicted classes guide case selection. Tree cover can include plantations and agricultural trees. These convenience cases do not form an independent or representative test set.</p><table><tr><th>Case</th><th>2021 map hint</th><th>Current label</th></tr>{rows}</table>'
        document+='<h2>Review procedure</h2><p>Inspect both dates and the full surrounding stand, then record the evidence, source date, land use, confidence and uncertainty in review_cases.geojson. Keep scrub, orchard/plantation ambiguity and unsupported canopy height unknown. Review separately from training and freeze independent locations/dates before extracting samples.</p>'
        document+=f'<p>Contains modified Copernicus Sentinel data (2025). {html.escape(reference["attribution"])}. Historical reference: CC BY 4.0. {html.escape(reference["citation"])}</p></html>'
    output.mkdir(parents=True)
    (output/'review_cases.geojson').write_text(json.dumps(template,indent=2)+'\n',encoding='utf-8')
    summary={'case_count':len(centres),'reviewed_label_count':0,'splits_frozen':False,
             'source_bundle':str(Path(bundle).resolve()),'common_feature_coverage_fraction':verification['common_feature_coverage_fraction'],
             'limits':'Convenience cases for feasibility, not a representative test sample. Historical hints do not establish current forest classes.'}
    (output/'review_preparation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (output/'review.html').write_text(document,encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(prepare(args.zip,args.output),indent=2))
