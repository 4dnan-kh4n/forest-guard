"""Fresh Phase 0 experiment: bounded real-data inspection in a hosted runtime."""
import hashlib
import importlib.metadata
import json
import math
import platform
import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

COLLECTION = 'sentinel-2-c1-l2a'
SCENE = 'S2C_T43QFE_20250329T053314_L2A'
BBOX = [76.785, 22.413, 76.805, 22.433]
BANDS = [('blue', 'B02'), ('green', 'B03'), ('red', 'B04'), ('nir', 'B08')]


def run():
    if platform.system() == 'Windows':
        raise RuntimeError('Use a hosted Kaggle or Colab CPU runtime; local processing is disabled.')
    if Path('/kaggle/working').is_dir():
        base, provider = Path('/kaggle/working'), 'Kaggle'
    elif Path('/content').is_dir():
        try:
            import google.colab
        except ImportError as error:
            raise RuntimeError('Use a hosted Colab runtime.') from error
        base, provider = Path('/content'), 'Colab'
    else:
        raise RuntimeError('Use a hosted Kaggle or Colab CPU runtime; local processing is disabled.')

    packages = {}
    for name in ['numpy', 'rasterio', 'Pillow']:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as error:
            raise RuntimeError(f'Cloud package missing: {name}. No automatic installation performed.') from error
    import numpy as np
    import rasterio
    from PIL import Image
    from rasterio.vrt import WarpedVRT
    from rasterio.warp import Resampling, transform as project_points, transform_bounds
    from rasterio.windows import Window, from_bounds

    if shutil.disk_usage(base).free < 100 * 1024**2:
        raise RuntimeError('Cloud runtime needs at least 100 MiB free for this bounded experiment.')
    output = base / 'forestguard_phase0' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output.mkdir(parents=True)
    started = time.monotonic()
    url = f'https://earth-search.aws.element84.com/v1/collections/{COLLECTION}/items/{SCENE}'
    try:
        with urlopen(url, timeout=30) as response:
            content = response.read(512001)
    except URLError as error:
        raise RuntimeError('Metadata request failed. Check cloud Internet and any account verification requirement.') from error
    if len(content) > 512000:
        raise ValueError('Metadata exceeds the 500 KiB safety limit.')
    item = json.loads(content)
    assert item['id'] == SCENE
    (output / 'source.json').write_bytes(content)
    assets = item['assets']
    calibration, measurements, masks = {}, [], []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='60',
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_CACHEMAX=64*1024**2):
        with rasterio.open(assets['red']['href']) as reference:
            bounds = transform_bounds('EPSG:4326', reference.crs, *BBOX, densify_pts=21)
            crop = from_bounds(*bounds, transform=reference.transform)
            left, top = math.floor(crop.col_off), math.floor(crop.row_off)
            right, bottom = math.ceil(crop.col_off+crop.width), math.ceil(crop.row_off+crop.height)
            assert 0 <= left < right <= reference.width and 0 <= top < bottom <= reference.height
            assert max(right-left, bottom-top) <= 512, 'Crop exceeds the research size limit'
            window = Window(left, top, right-left, bottom-top)
            crs, grid = reference.crs, reference.window_transform(window)
            full_grid = reference.transform
            shape = (bottom-top, right-left)
        for key, name in BANDS:
            asset = assets[key]
            assert asset['href'].startswith('https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/')
            scale = asset['raster:bands'][0]['scale']
            offset = asset['raster:bands'][0]['offset']
            assert math.isfinite(scale) and scale > 0 and math.isfinite(offset)
            with rasterio.open(asset['href']) as band:
                assert band.crs == crs and band.transform == full_grid and band.res == (10., 10.)
                assert math.isclose(band.scales[0],scale) and math.isclose(band.offsets[0],offset), 'Calibration metadata/header mismatch'
                raw = band.read(1, window=window, masked=True)
            calibration[name] = {'scale': scale, 'offset': offset, 'href': asset['href']}
            measurements.append(raw.filled(0).astype('float32') * scale + offset)
            masks.append(~np.ma.getmaskarray(raw))
        with rasterio.open(assets['scl']['href']) as quality:
            with WarpedVRT(quality, crs=crs, transform=grid, height=shape[0], width=shape[1],
                           resampling=Resampling.nearest) as aligned:
                scl = aligned.read(1)

    values = np.stack(measurements)
    row, col = np.indices(shape)
    x, y = grid.c+(col+.5)*grid.a, grid.f+(row+.5)*grid.e
    lon, lat = project_points(crs, 'EPSG:4326', x.ravel(), y.ravel())
    lon, lat = np.asarray(lon).reshape(shape), np.asarray(lat).reshape(shape)
    study = (lon >= BBOX[0]) & (lon <= BBOX[2]) & (lat >= BBOX[1]) & (lat <= BBOX[3])
    valid = study & np.logical_and.reduce(masks) & np.isfinite(values).all(axis=0) & np.isin(scl, [4, 5, 6])
    assert valid.any(), 'No usable pixels: inspect another observation or research crop'
    values[:, ~valid] = -9999
    profile = dict(driver='GTiff', crs=crs, transform=grid, height=shape[0], width=shape[1], compress='deflate')
    with rasterio.open(output/'reflectance.tif', 'w', **profile, count=4, dtype='float32', nodata=-9999) as dst:
        dst.write(values)
        dst.descriptions = tuple(name for _, name in BANDS)
    for name, array in [('scl', scl), ('study', study.astype('uint8')), ('usable', valid.astype('uint8'))]:
        with rasterio.open(output/f'{name}.tif', 'w', **profile, count=1, dtype='uint8') as dst:
            dst.write(array, 1)
    rgb = (np.clip(values[[2, 1, 0]] / .3, 0, 1)*255).astype('uint8').transpose(1, 2, 0)
    Image.fromarray(np.dstack([rgb, valid.astype('uint8')*255])).save(output/'preview.png')

    # Reopen outputs: successful writes alone are insufficient evidence.
    for name, expected in [('reflectance', values), ('scl', scl), ('study', study), ('usable', valid)]:
        with rasterio.open(output/f'{name}.tif') as saved:
            assert saved.crs == crs and saved.transform == grid and saved.shape == shape
            assert saved.res == (10., 10.)
            actual = saved.read() if expected.ndim == 3 else saved.read(1)
            assert np.array_equal(actual, expected), f'Saved pixels differ: {name}'
    classes, counts = np.unique(scl[study], return_counts=True)
    report = {
        'status': 'real research sample; not forest labels or beat reporting',
        'scene_id': SCENE, 'collection':COLLECTION, 'acquisition': item['properties']['datetime'], 'metadata_url': url,
        'bbox_lon_lat': BBOX, 'official_boundary_verified': False, 'shape': list(shape),
        'crs': str(crs), 'transform': list(grid)[:6], 'resolution_m': 10,
        'band_order': [name for _, name in BANDS], 'calibration': calibration,
        'reflectance_formula': 'raw * asset scale + asset offset, applied once',
        'calibration_limit': 'Collection 1 asset metadata matches all four raster headers; independent absolute radiometric validation not performed.',
        'quality_rule': 'all bands valid and finite; SCL 4/5/6; inside research-box pixel centers',
        'scl_resampling': 'nearest neighbor; native 20 m quality remains 20 m information',
        'study_pixels': int(study.sum()), 'usable_pixels': int(valid.sum()),
        'usable_fraction': float(valid.sum()/study.sum()),
        'scl_counts_inside_study': {str(int(k)): int(v) for k, v in zip(classes, counts)},
        'reflectance_quantiles': {name: np.quantile(values[i, valid], [0, .01, .5, .99, 1]).tolist()
                                 for i, (_, name) in enumerate(BANDS)},
        'runtime': {'provider': provider, 'python': platform.python_version(), 'packages': packages,
                    'gdal': rasterio.__gdal_version__},
        'processing_seconds': round(time.monotonic()-started, 3),
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'attribution': 'Contains modified Copernicus Sentinel data 2025',
        'license_url': 'https://cds.climate.copernicus.eu/licences/ec-sentinel',
        'model_trained': False, 'reviewed_labels_exist': False,
    }
    (output/'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    manifest = {}
    for file in sorted(output.iterdir()):
        with file.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        manifest[file.name] = {'sha256': digest, 'bytes': file.stat().st_size}
    (output/'checksums.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    bundle = output/'forestguard_phase0.zip'
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in [*manifest, 'checksums.json']:
            archive.write(output/name, arcname=name)
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for name, record in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == record['sha256']
    print(json.dumps(report, indent=2))
    print('Verified sample bundle:', bundle, '\nBundle bytes:', bundle.stat().st_size)
    return output


if __name__ == '__main__':
    run()
