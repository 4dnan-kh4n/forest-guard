"""Check saved historical predicted-height crops; no forest accuracy claim."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom


def verify(bundle, boundary, cases):
    study = json.loads(Path(boundary).read_text())
    review = json.loads(Path(cases).read_text())
    arrays = {}
    grid = None
    with zipfile.ZipFile(bundle) as archive:
        expected = {'height.tif','standard_deviation.tif','reference_report.json'}
        if set(archive.namelist()) != expected or len(archive.namelist()) != 3:
            raise ValueError('Unexpected or duplicate export files.')
        if sum(e.file_size for e in archive.infolist()) > 5*1024**2:
            raise ValueError('Export exceeds the bounded crop size.')
        report = json.loads(archive.read('reference_report.json'))
        if (report['reference_year'] != 2020 or report['reference_independent'] is not False
                or report['labels_generated'] is not False or report['license'] != 'CC BY 4.0'
                or set(report['files']) != expected - {'reference_report.json'}):
            raise ValueError('Provenance or checksum manifest mismatch.')
        for name,digest in report['files'].items():
            raw = archive.read(name)
            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError('Checksum mismatch: '+name)
            kind = Path(name).stem
            with MemoryFile(raw) as memory, memory.open() as raster:
                current = (raster.shape,raster.transform,raster.crs)
                if raster.count != 1 or max(raster.shape) > 512 or raster.dtypes[0] != 'float32':
                    raise ValueError('Unexpected crop dimensions or type.')
                if grid is not None and grid != current:
                    raise ValueError('Height/uncertainty grids differ.')
                grid = current
                values = raster.read(1)
                inside = geometry_mask([transform_geom('EPSG:4326',raster.crs,study['features'][0]['geometry'])],raster.shape,raster.transform,invert=True)
                valid = np.isfinite(values)
                if np.any(valid & ~inside):
                    raise ValueError('Valid crop values outside the selected polygon.')
                source = next(s for s in report['sources'] if s['kind'] == kind)
                if int(inside.sum()) != source['study_centres'] or int(valid.sum()) != source['valid_centres']:
                    raise ValueError('Coverage count mismatch.')
                arrays[kind] = values
        if [c['label_id'] for c in report['cases']] != [f['properties']['label_id'] for f in review['features']]:
            raise ValueError('Review case IDs differ.')
        for item,feature in zip(report['cases'],review['features']):
            assert item['class_assigned'] is False
            mask = geometry_mask([transform_geom('EPSG:4326',grid[2],feature['geometry'])],grid[0],grid[1],invert=True)
            for kind,values in arrays.items():
                selected = values[mask & np.isfinite(values)]
                recorded = item[kind]
                assert recorded['valid_centres'] == selected.size
                for name,function in [('median',np.median),('minimum',np.min),('maximum',np.max)]:
                    actual = float(function(selected)) if selected.size else None
                    assert recorded[name] == actual
    return dict(integrity='PASS',verified_files=2,case_statistics_recomputed=len(report['cases']),
                reference_year=2020,independent_2025_truth=False,labels_assigned=0,cases=report['cases'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['bundle','boundary','cases']:
        parser.add_argument(key,type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle,args.boundary,args.cases),indent=2))
