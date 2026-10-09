"""Create an offline, geographically aligned comparison; never assign classes."""
import argparse
import base64
import html
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom
from verify_liss4_crop import verify as verify_reference
from verify_research_bundle import verify as verify_research
from audit_labels import audit


def blind_cases(document, reference_report):
    features = []
    for feature in document['features']:
        original = feature['properties']
        props = {'label_id':original['label_id'],'class':'unknown'}
        props.update(observation_date=original['observation_date'],
                     reference_source='Bhoonidhi Resourcesat-2A '+reference_report['product'],
                     reference_access_license=reference_report['license_url']+'; attribution ISRO-IRS',
                     reference_date=reference_report['capture_date'], reviewer=None, review_date=None,
                     confidence=None, uncertainty_notes='Awaiting fresh review; stand height, canopy and land use are not established.',
                     study_area_version=original['study_area_version'],split='unassigned',
                     reference_kind='dated_reference_imagery',review_status='unreviewed',reference_independent=False,
                     height_evidence=None,canopy_cover_percent=None,qualifying_stand_area_ha=None,
                     forest_use_evidence=None,origin='unknown')
        features.append(dict(type='Feature',geometry=feature['geometry'],properties=props))
    result = dict(type='FeatureCollection',features=features)
    audit(result)
    return result


def prepare(research, reference, cases, output, blind=False):
    output = Path(output)
    if output.exists():
        raise FileExistsError('Keep previous reviews; choose a new output folder.')
    reference_check = verify_reference(reference)
    research_check = verify_research(research)
    document = json.loads(Path(cases).read_text(encoding='utf-8'))
    audit(document)
    if len(document['features']) > 30:
        raise ValueError('This initial comparison is limited to 30 review patches.')
    panels, coverage = [], []
    details = [[] for _ in document['features']]
    with zipfile.ZipFile(reference) as ref, zipfile.ZipFile(research) as obs:
        reference_report = json.loads(ref.read('crop_report.json'))
        reference_date = reference_report['capture_date']
        if blind:
            document = blind_cases(document,reference_report)
        records = json.loads(obs.read('research_report.json'))['acquisitions']
        inputs = [(obs, record['season'] + '/features.tif', record['season'] + '/preview.png',
                   'Sentinel ' + record['acquisition'][:10], 'Natural-colour preview; 20 m analysis grid') for record in records]
        inputs.insert(1, (ref, 'raw_dn.tif', 'false_colour_NIR_red_green.png',
                         'Resourcesat ' + reference_date, 'False colour: NIR/red/green; native 5.8 m detail, 5 m spacing. Red does not mean forest.'))
        for bundle, raster_name, image_name, title, caption in inputs:
            with MemoryFile(bundle.read(raster_name)) as memory, memory.open() as raster:
                boxes = []
                encoded = base64.b64encode(bundle.read(image_name)).decode('ascii')
                if bundle is ref:
                    available = ~(raster.read() == 0).all(axis=0)
                for number, feature in enumerate(document['features'], 1):
                    projected = transform_geom('EPSG:4326', raster.crs, feature['geometry'])
                    vertices = [~raster.transform * tuple(point) for point in projected['coordinates'][0]]
                    points = ' '.join(f'{x:.3f},{y:.3f}' for x,y in vertices)
                    x, y = vertices[0]
                    boxes.append(f'<polygon points="{points}" fill="none" stroke="#ffff00" stroke-width="1"/>'
                                 f'<text x="{x:.3f}" y="{y-2:.3f}" fill="#ffff00" font-size="8">{number}</text>')
                    left, top = min(v[0] for v in vertices), min(v[1] for v in vertices)
                    width = max(v[0] for v in vertices)-left
                    height = max(v[1] for v in vertices)-top
                    details[number-1].append(f'<section><h3>{html.escape(title)}</h3>'
                        f'<svg viewBox="{left-width:.3f} {top-height:.3f} {width*3:.3f} {height*3:.3f}" role="img" aria-label="Case {number} surrounding stand, {html.escape(title)}">'
                        f'<image width="{raster.width}" height="{raster.height}" href="data:image/png;base64,{encoded}"/>'
                        f'<polygon points="{points}" fill="none" stroke="#ffff00" stroke-width="0.2"/></svg></section>')
                    if bundle is ref:
                        patch = geometry_mask([projected], raster.shape, raster.transform, invert=True)
                        count = int(patch.sum())
                        candidate_count = int((patch & available).sum())
                        coverage.append(dict(label_id=feature['properties']['label_id'], patch_pixels=count,
                                             nonzero_candidate_pixels=candidate_count,
                                             nonzero_fraction=candidate_count/count if count else 0))
                height, width = raster.shape
                panels.append(f'<section><h2>{html.escape(title)}</h2><p>{html.escape(caption)}</p>'
                              f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)} numbered review footprints">'
                              f'<image width="{width}" height="{height}" href="data:image/png;base64,{encoded}"/>{"".join(boxes)}</svg></section>')
    assert len(coverage) == len(document['features']) and len(panels) == len(records)+1
    rows = ''.join(f'<tr><td>{n}</td><td>{html.escape(feature["properties"]["label_id"])}</td>' +
                   ('' if blind else f'<td>{html.escape(feature["properties"]["weak_class_name"])}</td>') +
                   f'<td>{item["nonzero_fraction"]:.1%}</td><td>{html.escape(feature["properties"].get("class", "unknown"))}; '
                   f'{html.escape(feature["properties"].get("review_status", "unreviewed"))}</td></tr>'
                   for n,(feature,item) in enumerate(zip(document['features'],coverage),1))
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    page += '<title>Compartment 279 dated reference comparison</title><style>body{font:16px system-ui;margin:24px;color:#17372c;background:#f4f7f3}h1{font-size:25px}.panels{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}h2{font-size:19px}svg{width:100%;background:#15251c}td,th{padding:9px;border-bottom:1px solid #bbb;text-align:left}table{border-collapse:collapse;width:100%}@media(max-width:800px){.panels{grid-template-columns:1fr}}</style>'
    page += '<h1>Compartment 279: dated reference comparison</h1><p>Same numbered 120 m footprints on each image, projected onto each saved grid. This script generates no labels. Differences in colour, season and sensor do not establish forest loss.</p>'
    page += ('<p>Blind review: earlier interpretations and class hints are hidden. Edit reviewer_cases.geojson only after inspecting permitted evidence. This pack uses convenience-selected locations; it is not an independent test set.</p>' if blind else '<p>Recorded AI-assisted interpretations are displayed; they have no field or forest-staff validation.</p>')
    page += f'<div class="panels">{"".join(panels)}</div><h2>Reference availability by patch</h2><p>Nonzero pixels are candidates only: no cloud validation or field height evidence. Historical WorldCover hints selected these convenience cases; they are not independent test samples.</p>'
    hint_heading = '' if blind else '<th>2021 weak hint</th>'
    page += f'<table><tr><th>Number</th><th>Case</th>{hint_heading}<th>Nonzero reference</th><th>Interpretation</th></tr>{rows}</table>'
    if blind:
        page += '<h2>Required review record</h2><p>For each footprint, record forest / non_forest / unknown, reviewer and review date, confidence, evidence source/date and reuse permission, canopy assessment, height or supported height potential, stand extent and forest versus agricultural use. Our forest target requires a stand above 0.5 ha, canopy above 10%, and height or supported height potential above 5 m, excluding agricultural orchards/crops. Use unknown when evidence is insufficient. No field photographs are requested.</p><p>Leave split unassigned. Do not mark reference_independent true merely because this page hides hints; source independence and reviewer provenance need a separate assessment. Fill the JSON template and run audit_labels.py before proposing model splits.</p>'
    for number, panels_for_case in enumerate(details, 1):
        note = document['features'][number-1]['properties'].get('uncertainty_notes') or 'Awaiting interpretation.'
        page += f'<h2>Case {number}: approximately 360 m context; yellow outline is the 120 m patch</h2><p>{html.escape(note)}</p><div class="panels">{"".join(panels_for_case)}</div>'
    page += '<p>ISRO-IRS. Contains modified Copernicus Sentinel data 2025. WorldCover 2021 hints: CC BY 4.0. All original sources and checksums retained.</p></html>'
    output.mkdir(parents=True)
    (output/'comparison.html').write_text(page, encoding='utf-8')
    if blind:
        (output/'reviewer_cases.geojson').write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    summary = dict(patch_coverage=coverage, reference_integrity=reference_check,
                   observation_integrity=research_check, classes_assigned=0,
                   reference_cloud_quality_reviewed=False, evaluation_splits_frozen=False,
                   prior_interpretations_hidden=blind,independent_test_set=False)
    (output/'comparison_report.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['research', 'reference', 'cases', 'output']:
        parser.add_argument(name, type=Path)
    parser.add_argument('--blind',action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.research,args.reference,args.cases,args.output,blind=args.blind),indent=2))
