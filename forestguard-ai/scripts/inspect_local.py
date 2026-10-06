"""Audit an exported small satellite crop offline and export measured coverage."""
import argparse
import csv
import hashlib
import json
import math
import platform
import zipfile
from contextlib import ExitStack
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
from verify_bundle import verify


def check_files(folder, manifest):
    for name, record in manifest.items():
        path = folder/name
        if path.stat().st_size != record['bytes'] or path.stat().st_size > 10*1024**2:
            raise ValueError(f'Unexpected file size: {name}')
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream,'sha256').hexdigest()
        if digest != record['sha256']:
            raise ValueError(f'File integrity failure: {name}')


def inspect(folder):
    folder = Path(folder).resolve(strict=True)
    verify(folder/'forestguard_phase0.zip')
    manifest = json.loads((folder/'checksums.json').read_text())
    with zipfile.ZipFile(folder/'forestguard_phase0.zip') as archive:
        if manifest != json.loads(archive.read('checksums.json')):
            raise ValueError('Extracted manifest differs from verified bundle.')
    expected = {'source.json','reflectance.tif','scl.tif','study.tif','usable.tif','preview.png','report.json'}
    if set(manifest) != expected:
        raise ValueError('Unexpected sample manifest.')
    # Check the extracted files too: an intact ZIP does not validate changed siblings.
    check_files(folder, manifest)
    report = json.loads((folder/'report.json').read_text())
    source = json.loads((folder/'source.json').read_text())
    if report['scene_id'] != source['id'] or report['acquisition'] != source['properties']['datetime']:
        raise ValueError('Extracted provenance mismatch.')
    boundary = (folder/'boundary_mask.tif').exists()
    if boundary:
        extra = json.loads((folder/'boundary_checksums.json').read_text())
        if set(extra) != {'boundary_input.geojson','boundary_mask.tif','boundary_overlay.png','boundary_review.json'}:
            raise ValueError('Unexpected boundary manifest.')
        with zipfile.ZipFile(folder/'boundary_review.zip') as archive:
            if (set(archive.namelist()) != set(extra)|{'boundary_checksums.json'}
                    or len(archive.infolist()) != 5
                    or sum(i.file_size for i in archive.infolist()) > 10*1024**2
                    or json.loads(archive.read('boundary_checksums.json')) != extra):
                raise ValueError('Boundary archive/manifest mismatch.')
            for name,record in extra.items():
                if hashlib.sha256(archive.read(name)).hexdigest() != record['sha256']:
                    raise ValueError(f'Boundary archive integrity failure: {name}')
        check_files(folder,extra)
    counts = {'crop_box':[0,0]}
    if boundary:
        counts['candidate_polygon'] = [0,0]
    with rasterio.Env(GDAL_CACHEMAX=32*1024**2, PROJ_NETWORK='OFF', GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR'), ExitStack() as stack:
        images = {name:stack.enter_context(rasterio.open(folder/f'{name}.tif',driver='GTiff'))
                  for name in ['reflectance','scl','study','usable']+(['boundary_mask'] if boundary else [])}
        raster = images['reflectance']
        if raster.count != 4 or raster.dtypes != ('float32',)*4 or raster.nodata != -9999:
            raise ValueError('Expected exported four-band float32 reflectance with nodata -9999.')
        if max(raster.shape) > 512 or min(raster.shape) <= 0:
            raise ValueError('Only small crops up to 512 pixels per side are supported.')
        if raster.descriptions != ('B02','B03','B04','B08') or report['band_order'] != list(raster.descriptions):
            raise ValueError('Band order mismatch.')
        if not raster.crs or not raster.crs.is_projected or not math.isclose(raster.crs.linear_units_factor[1],1.):
            raise ValueError('Expected a projected grid in metres.')
        if raster.res != (10.,10.) or raster.transform.b != 0 or raster.transform.d != 0:
            raise ValueError('Expected an unrotated native 10 m grid.')
        if list(raster.shape) != report['shape'] or str(raster.crs) != report['crs'] or list(raster.transform)[:6] != report['transform']:
            raise ValueError('Raster/report grid mismatch.')
        for name,image in images.items():
            if image.driver != 'GTiff' or image.crs != raster.crs or image.shape != raster.shape or image.transform != raster.transform:
                raise ValueError(f'Layer grid/driver mismatch: {name}')
            if name != 'reflectance' and (image.count != 1 or image.dtypes != ('uint8',)):
                raise ValueError(f'Expected a single uint8 mask/quality layer: {name}')
        # Bounded row windows: no full scene or training samples loaded locally.
        for row in range(0,raster.height,128):
            window = Window(0,row,raster.width,min(128,raster.height-row))
            values = raster.read(window=window)
            study = images['study'].read(1,window=window)
            saved_valid = images['usable'].read(1,window=window)
            if not np.isin(study,[0,1]).all() or not np.isin(saved_valid,[0,1]).all():
                raise ValueError('Mask contains non-binary values.')
            valid = study.astype(bool) & (raster.read_masks(window=window)>0).all(axis=0)
            valid &= np.isfinite(values).all(axis=0) & np.isin(images['scl'].read(1,window=window),[4,5,6])
            if not np.array_equal(valid,saved_valid.astype(bool)):
                raise ValueError('Stored usable mask differs from raster/quality validity.')
            counts['crop_box'][0] += int(study.sum())
            counts['crop_box'][1] += int(valid.sum())
            if boundary:
                mask = images['boundary_mask'].read(1,window=window)
                if not np.isin(mask,[0,1]).all() or (mask.astype(bool) & ~study.astype(bool)).any():
                    raise ValueError('Candidate mask is non-binary or extends outside the research box.')
                counts['candidate_polygon'][0] += int(mask.sum())
                counts['candidate_polygon'][1] += int((mask.astype(bool)&valid).sum())
        if counts['crop_box'] != [report['study_pixels'],report['usable_pixels']]:
            raise ValueError('Measured crop coverage differs from exported report.')
        if boundary:
            review = json.loads((folder/'boundary_review.json').read_text())
            if counts['candidate_polygon'] != [review['candidate_pixels'],review['candidate_usable_pixels']]:
                raise ValueError('Measured candidate coverage differs from exported report.')
        pixel_ha = abs(raster.transform.a*raster.transform.e)/10000
    rows = [{'scope':scope,'total_pixels':total,'usable_pixels':usable,
             'usable_fraction':usable/total if total else None,
             'boundary_or_box_ha':total*pixel_ha,'observable_ha':usable*pixel_ha}
            for scope,(total,usable) in counts.items()]
    return {'measurement_type':'imagery quality coverage; not forest area',
            'scene_id':report['scene_id'],'acquisition':report['acquisition'],
            'crs':report['crs'],'resolution_m':10,'band_order':report['band_order'],
            'scope_status':report.get('area_label','exported research crop; no area label recorded'),
            'forest_area_ha':None,'prediction_used':False,
            'coverage':rows,'attribution':report['attribution'],
            'sample_bundle_sha256':hashlib.sha256((folder/'forestguard_phase0.zip').read_bytes()).hexdigest(),
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,
                       'rasterio':rasterio.__version__,'gdal':rasterio.__gdal_version__}}


def export(result, output):
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    for name in ['coverage.json','coverage.csv']:
        if (output/name).exists():
            raise ValueError(f'Report already exists; choose another output directory: {output/name}')
    (output/'coverage.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with (output/'coverage.csv').open('w',newline='',encoding='utf-8') as stream:
        writer = csv.DictWriter(stream,fieldnames=list(result['coverage'][0]))
        writer.writeheader(); writer.writerows(result['coverage'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.input)
        export(result,args.output)
        print(json.dumps(result,indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        parser.exit(1,f'Inspection failed: {error}\n')
