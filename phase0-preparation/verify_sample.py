"""Verify an exported research sample offline; --rasters requires Rasterio/NumPy."""
import argparse
import hashlib
import json
import math
from pathlib import Path

FILES = {
    'reflectance.tif', 'scene_classes.tif', 'usable_mask.tif',
    'study_mask.tif', 'preview.png', 'source_stac_item.json', 'sample_report.json',
}


def verify(folder, rasters=False):
    folder = Path(folder)
    manifest = json.loads((folder / 'checksums.json').read_text(encoding='utf-8'))
    if set(manifest) != FILES:
        raise ValueError('Manifest does not list the expected sample files.')
    for name, record in manifest.items():
        path = folder / name
        if path.stat().st_size != record['bytes']:
            raise ValueError(f'File size mismatch: {name}')
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != record['sha256']:
            raise ValueError(f'Checksum mismatch: {name}')
    report = json.loads((folder / 'sample_report.json').read_text(encoding='utf-8'))
    source = json.loads((folder / 'source_stac_item.json').read_text(encoding='utf-8'))
    if report['scene_id'] != source['id'] or report['date'] != source['properties']['datetime']:
        raise ValueError('Scene/date provenance mismatch.')
    if report['band_order'] != ['B02', 'B03', 'B04', 'B08']:
        raise ValueError('Unexpected band order.')
    if report['model_trained'] or report['forest_labels_available']:
        raise ValueError('A research sample cannot claim a trained model or forest labels.')
    height, width = report['shape']
    if not (0 < height <= 512 and 0 < width <= 512):
        raise ValueError('Research crop exceeds the size limit.')
    study, usable = report['study_pixels'], report['usable_pixels']
    if not (0 < usable <= study <= height * width):
        raise ValueError('Invalid coverage counts.')
    if not math.isclose(report['usable_fraction'], usable / study, abs_tol=1e-12):
        raise ValueError('Coverage denominator mismatch.')
    if sum(report['scene_class_counts_inside_study'].values()) != study:
        raise ValueError('SCL histogram count mismatch.')

    if rasters:
        import numpy as np
        import rasterio
        from rasterio.warp import transform as project_points
        with rasterio.open(folder / 'reflectance.tif') as image:
            if (image.count != 4 or image.shape != (height, width)
                    or str(image.crs) != report['crs'] or image.res != (10.0, 10.0)
                    or image.nodata != -9999 or image.dtypes != ('float32',) * 4
                    or list(image.transform)[:6] != report['transform']):
                raise ValueError('Reflectance grid/type mismatch.')
            arrays = {}
            for name in ['scene_classes', 'usable_mask', 'study_mask']:
                with rasterio.open(folder / f'{name}.tif') as layer:
                    if (layer.crs != image.crs or layer.transform != image.transform
                            or layer.shape != image.shape or layer.count != 1
                            or layer.dtypes != ('uint8',)):
                        raise ValueError(f'Layer grid/type mismatch: {name}')
                    arrays[name] = layer.read(1)
            if any(not np.isin(arrays[n], [0, 1]).all() for n in ['usable_mask', 'study_mask']):
                raise ValueError('Masks must be binary.')
            valid, inside = arrays['usable_mask'].astype(bool), arrays['study_mask'].astype(bool)
            rows, cols = np.indices(image.shape)
            x = image.transform.c + (cols + .5) * image.transform.a
            y = image.transform.f + (rows + .5) * image.transform.e
            lon, lat = project_points(image.crs, 'EPSG:4326', x.ravel(), y.ravel())
            lon, lat = np.array(lon).reshape(image.shape), np.array(lat).reshape(image.shape)
            west, south, east, north = report['bbox_lon_lat']
            expected_inside = (lon >= west) & (lon <= east) & (lat >= south) & (lat <= north)
            if not np.array_equal(inside, expected_inside):
                raise ValueError('Study mask differs from research box pixel centers.')
            if (int(inside.sum()) != study or int(valid.sum()) != usable
                    or (valid & ~inside).any()
                    or not np.isin(arrays['scene_classes'][valid], [4, 5, 6]).all()):
                raise ValueError('Quality/coverage mask mismatch.')
            for band in image.read():
                if (not np.isfinite(band[valid]).all()
                        or not (band[~valid] == image.nodata).all()
                        or (band[valid] == image.nodata).any()):
                    raise ValueError('Reflectance validity mismatch.')
            classes, counts = np.unique(arrays['scene_classes'][inside], return_counts=True)
            histogram = {str(int(k)): int(v) for k, v in zip(classes, counts)}
            if histogram != report['scene_class_counts_inside_study']:
                raise ValueError('SCL histogram differs from raster.')
    return {
        'checks': 'checksums, provenance, coverage' + (', saved raster grids and masks' if rasters else ''),
        'scene_id': report['scene_id'], 'study_pixels': study, 'usable_pixels': usable,
        'usable_fraction': report['usable_fraction'],
        'scope': 'Provisional research crop only; not forest labels or beat totals.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--rasters', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.folder, args.rasters), indent=2))
    except (ValueError, KeyError, TypeError, OSError, ImportError) as error:
        parser.exit(1, f'Sample verification failed: {error}\n')
