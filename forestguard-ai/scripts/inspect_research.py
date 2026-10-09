"""Verify a saved compartment 279 research bundle and export coverage offline."""
import argparse
import hashlib
import json
import platform
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from inspect_local import export
from verify_research_bundle import verify


def inspect(bundle, boundary):
    bundle, boundary = Path(bundle).resolve(strict=True), Path(boundary).resolve(strict=True)
    if bundle.stat().st_size > 30*1024**2 or boundary.stat().st_size > 1024**2:
        raise ValueError('Only bounded research bundles and small boundaries are supported.')
    with rasterio.Env(PROJ_NETWORK='OFF', GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_CACHEMAX=32*1024**2):
        checked = verify(bundle)
    with zipfile.ZipFile(bundle) as archive:
        saved = json.loads(archive.read('boundary.geojson'))
        selected = json.loads(boundary.read_bytes())
        if (selected.get('type') != 'FeatureCollection' or len(selected['features']) != 1
                or len(saved['features']) != 1
                or selected['features'][0]['geometry'] != saved['features'][0]['geometry']):
            raise ValueError('Bundle geometry differs from the selected study boundary.')
        report = json.loads(archive.read('research_report.json'))
    observations = report['acquisitions']
    if not observations or any(item['crs'] != 'EPSG:32643' for item in observations):
        raise ValueError('Expected verified compartment 279 observations in UTM 43 north.')
    total = observations[0]['inside_study_pixels']
    if total <= 0 or any(item['inside_study_pixels'] != total for item in observations):
        raise ValueError('Observations must share a nonempty study mask.')
    # shortcut: this verified export uses 20 m pixels; extend with a new format verifier for other grids.
    pixel_ha = 20*20/10000
    rows = []
    for item in observations:
        rows.append({'scope':item['season'], 'acquisition':item['acquisition'],
                     'total_pixels':total, 'usable_pixels':item['usable_feature_pixels'],
                     'usable_fraction':item['usable_fraction_inside_study'],
                     'boundary_or_box_ha':total*pixel_ha,
                     'observable_ha':item['usable_feature_pixels']*pixel_ha})
    rows.append({'scope':'common_valid_coverage', 'acquisition':' & '.join(item['acquisition'] for item in observations),
                 'total_pixels':total, 'usable_pixels':checked['common_feature_valid_pixels'],
                 'usable_fraction':checked['common_feature_coverage_fraction'],
                 'boundary_or_box_ha':total*pixel_ha,
                 'observable_ha':checked['common_feature_valid_pixels']*pixel_ha})
    with bundle.open('rb') as stream:
        bundle_hash = hashlib.file_digest(stream,'sha256').hexdigest()
    return {'measurement_type':'imagery feature coverage; not forest area',
            'study_id':report['study_id'], 'scope_status':'user-confirmed compartment research geometry; not full Joga beat',
            'crs':'EPSG:32643', 'resolution_m':20, 'band_order':observations[0]['band_order'],
            'area_method':'pixel-centre mask counts times pixel area; not surveyed boundary or canopy area',
            'forest_area_ha':None, 'prediction_used':False, 'coverage':rows,
            'observations':[{'scene_id':i['scene_id'],'acquisition':i['acquisition']} for i in observations],
            'bundle_sha256':bundle_hash,
            'boundary_sha256':hashlib.sha256(boundary.read_bytes()).hexdigest(),
            'verification':checked,
            'limits':'Different seasons; no forest change, independent accuracy or boundary registration measured.',
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,
                       'rasterio':rasterio.__version__,'gdal':rasterio.__gdal_version__}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--boundary',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.input,args.boundary)
        export(result,args.output)
        print(json.dumps(result,indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        parser.exit(1,f'Inspection failed: {error}\n')
