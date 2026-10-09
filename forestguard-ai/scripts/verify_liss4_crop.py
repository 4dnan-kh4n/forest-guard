"""Verify a small exported LISS-IV reference ZIP offline; not forest accuracy."""
import argparse
import hashlib
import json
import zipfile
import sys
from pathlib import Path

import numpy as np
from rasterio.features import geometry_mask
from rasterio.crs import CRS
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cloud'))
from liss4_reference_crop import accepted_liss4_crs


def verify(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = archive.namelist()
        if len(names) != len(set(names)) or sum(e.file_size for e in entries) > 20 * 1024**2:
            raise ValueError('Duplicate members or oversized reference export.')
        required = {'boundary.geojson', 'BAND_META.txt', 'ACC_REP.txt', 'source_grid.json', 'raw_dn.tif',
                    'observed_mask.tif', 'false_colour_NIR_red_green.png', 'crop_report.json'}
        if set(names) not in [required, required | {'raw_dn.tif.msk'}]:
            raise ValueError('Unexpected reference export files.')
        report = json.loads(archive.read('crop_report.json'))
        if set(report['files']) != set(names) - {'crop_report.json'}:
            raise ValueError('Reference checksum manifest does not match files.')
        for name, checksum in report['files'].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != checksum:
                raise ValueError('Reference checksum mismatch: ' + name)
        dates = {'RAF07APR2025043238009700056SSANSTUC00GTDC': '2025-04-07',
                 'RAF09NOV2025046306009700056SSANSTUC00GTDD': '2025-11-09'}
        if (report.get('product') not in dates or report['capture_date'] != dates[report['product']]
                or report['labels_reviewed'] is not False
                or report['cloud_quality_screened'] is not False or report['usable_coverage'] is not None
                or report['study_area_version'] != 'compartment-279-user-kml-v1'
                or report['attribution'] != 'ISRO-IRS'):
            raise ValueError('Reference provenance or claims mismatch.')
        boundary = json.loads(archive.read('boundary.geojson'))
        with MemoryFile(archive.read('raw_dn.tif')) as memory, memory.open() as raster:
            if (raster.count != 3 or not accepted_liss4_crs(raster.crs) or raster.res != (5., 5.)
                    or raster.crs != CRS.from_string(report['crs'])
                    or raster.width * raster.height > 1000000
                    or list(raster.transform)[:6] != report['transform']
                    or [raster.count, raster.height, raster.width] != report['shape']
                    or list(raster.descriptions) != ['BAND2_green_DN', 'BAND3_red_DN', 'BAND4_NIR_DN']):
                raise ValueError('Reference raster grid/bands mismatch.')
            inside = geometry_mask([transform_geom('EPSG:4326', raster.crs,
                                   boundary['features'][0]['geometry'])],
                                   raster.shape, raster.transform, invert=True)
            expected_grid = (raster.shape, raster.crs, raster.transform)
            values = raster.read()
            assert values.dtype == np.uint16
        with MemoryFile(archive.read('observed_mask.tif')) as memory, memory.open() as raster:
            if (raster.shape, raster.crs, raster.transform) != expected_grid:
                raise ValueError('Reference mask grid mismatch.')
            mask = raster.read(1)
            if not np.isin(mask, [0, 1]).all() or np.any(mask.astype(bool) & ~inside):
                raise ValueError('Reference mask contains invalid/outside pixels.')
        if int(inside.sum()) != report['study_pixels'] or int(mask.sum()) != report['observed_pixels']:
            raise ValueError('Reference coverage denominator mismatch.')
        suspected_fill = mask.astype(bool) & (values == 0).all(axis=0)
        candidates = mask.astype(bool) & ~suspected_fill
    return {'integrity': 'PASS', 'verified_files': len(report['files']),
            'study_pixels': report['study_pixels'], 'observed_pixels': report['observed_pixels'],
            'suspected_all_zero_fill_pixels': int(suspected_fill.sum()),
            'nonzero_candidate_pixels': int(candidates.sum()),
            'nonzero_candidate_fraction': float(candidates.sum() / inside.sum()),
            'limits': 'Observed count follows source-declared masks; all-zero pixels are suspected fill. Nonzero candidates are not cloud-screened or forest labels.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    print(json.dumps(verify(parser.parse_args().archive), indent=2))
