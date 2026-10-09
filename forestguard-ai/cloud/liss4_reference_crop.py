"""Cloud-only, bounded raw-DN reference crop; does not create forest labels."""
import hashlib
import importlib.metadata
import json
import math
import platform
import shutil
import zipfile
from pathlib import Path

PRODUCT = 'RAF07APR2025043238009700056SSANSTUC00GTDC'
ARCHIVE_SHA256 = '1bbc0619381dcc85515cf35f15a1e0769ccb770d18890012deae281943e19947'


def accepted_liss4_crs(crs):
    if crs is None:
        return False
    if crs.to_epsg() == 32643:
        return True
    parameters = crs.to_dict()
    # The supplier rounds WGS84 inverse flattening; retain its original CRS.
    return (parameters.get('proj') == 'utm' and parameters.get('zone') == 43
            and not parameters.get('south', False) and parameters.get('units') == 'm'
            and parameters.get('a') == 6378137
            and math.isclose(parameters.get('rf', 0), 298.257223563, rel_tol=0, abs_tol=1e-6))


def run_liss4(archive, study, source_spec=None):
    if platform.system() == 'Windows' or not Path('/kaggle/working').is_dir():
        raise RuntimeError('Run this reference crop in a hosted Kaggle CPU notebook.')
    if not isinstance(study, dict) or study.get('type') != 'FeatureCollection':
        raise ValueError('Supply the selected private study GeoJSON.')
    spec = source_spec if source_spec is not None else dict(product=PRODUCT,
        archive_sha256=ARCHIVE_SHA256, archive_bytes=626385051,
        band_bytes=588419918, capture_date='2025-04-07')
    product = spec['product']
    if product not in {PRODUCT, 'RAF09NOV2025046306009700056SSANSTUC00GTDD'}:
        raise ValueError('Only the two inspected reference products are supported.')
    expected_date = '2025-04-07' if product == PRODUCT else '2025-11-09'
    if spec['capture_date'] != expected_date:
        raise ValueError('Capture date does not match the inspected product.')
    if (len(spec['archive_sha256']) != 64 or any(c not in '0123456789abcdef' for c in spec['archive_sha256'])
            or not 0 < spec['archive_bytes'] < 2 * 1024**3
            or not 0 < spec['band_bytes'] < 1024**3):
        raise ValueError('Supply verified archive and band sizes and SHA-256.')
    import numpy as np
    import rasterio
    from rasterio.features import bounds, geometry_mask
    from rasterio.warp import transform_geom, transform as project_coordinates
    from rasterio.windows import Window, from_bounds
    from PIL import Image

    archive = Path(archive)
    if archive.name not in {product + '.zip', product + '.zip.bin'} or archive.stat().st_size != spec['archive_bytes']:
        raise ValueError('Wrong source archive or download size.')
    digest = hashlib.sha256()
    with archive.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    if digest.hexdigest() != spec['archive_sha256']:
        raise ValueError('Source archive checksum mismatch.')
    output = Path('/kaggle/working/liss4_279_reference')
    if output.exists():
        raise FileExistsError('Output exists; preserve it before starting another run.')
    if shutil.disk_usage(output.parent).free < 3 * 1024**3:
        raise RuntimeError('At least 3 GiB of cloud disk space is required.')
    if len(study.get('features', [])) != 1:
        raise ValueError('Expected the single selected compartment feature.')
    properties = study['features'][0].get('properties', {})
    if properties.get('study_area_version') != 'compartment-279-user-kml-v1':
        raise ValueError('Expected the selected compartment 279 boundary version.')
    geometry = study['features'][0]['geometry']
    output.mkdir()
    (output / 'boundary.geojson').write_text(json.dumps(study, indent=2) + '\n')
    stack, masks = [], []
    grid = None
    with zipfile.ZipFile(archive) as bundle:
        for name in ['BAND_META.txt', 'ACC_REP.txt']:
            entry = bundle.getinfo(product + '/' + name)
            if entry.file_size > 10000:
                raise ValueError('Unexpected metadata size.')
            (output / name).write_bytes(bundle.read(entry))
        for number in [2, 3, 4]:
            entry = bundle.getinfo(product + f'/BAND{number}.tif')
            if entry.file_size != spec['band_bytes']:
                raise ValueError('Unexpected band size.')
            scratch = Path('/kaggle/temp/liss4_source_band.tmp.tif')
            scratch.parent.mkdir(parents=True, exist_ok=True)
            # ZIP extraction streams one band on cloud disk and checks its CRC.
            with bundle.open(entry) as source, scratch.open('xb') as target:
                shutil.copyfileobj(source, target, 1024 * 1024)
            with rasterio.open(scratch) as source:
                source_grid = dict(crs=str(source.crs), epsg=source.crs.to_epsg() if source.crs else None,
                                   resolution=list(source.res), count=source.count,
                                   transform=list(source.transform)[:6], nodata=source.nodata,
                                   shape=list(source.shape), dtype=source.dtypes[0])
                (output / 'source_grid.json').write_text(json.dumps(source_grid, indent=2) + '\n')
                print('Actual source grid:', json.dumps(source_grid), flush=True)
                if not accepted_liss4_crs(source.crs) or source.res != (5.0, 5.0) or source.count != 1:
                    raise ValueError('Unexpected source CRS, pixel spacing or band count.')
                west, south, east, north = bounds(geometry)
                longitudes, latitudes = [west, east, east, west], [south, south, north, north]
                actual_x, actual_y = project_coordinates('EPSG:4326', source.crs, longitudes, latitudes)
                canonical_x, canonical_y = project_coordinates('EPSG:4326', 'EPSG:32643', longitudes, latitudes)
                crs_offset = max(abs(a-b) for a,b in zip(actual_x + actual_y, canonical_x + canonical_y))
                if crs_offset >= 0.001:
                    raise ValueError('Source CRS normalization exceeds 1 mm at study corners.')
                projected = transform_geom('EPSG:4326', 'EPSG:32643', geometry)
                floating = from_bounds(*bounds(projected), transform=source.transform)
                x, y = int(np.floor(floating.col_off)), int(np.floor(floating.row_off))
                right = int(np.ceil(floating.col_off + floating.width))
                bottom = int(np.ceil(floating.row_off + floating.height))
                window = Window(x, y, right - x, bottom - y)
                if x < 0 or y < 0 or right > source.width or bottom > source.height:
                    raise ValueError('Study envelope extends beyond raster grid.')
                if window.width * window.height > 1000000:
                    raise ValueError('Crop exceeds one million pixels.')
                transform = source.window_transform(window)
                current_grid = (int(window.height), int(window.width), transform, source.crs)
                if grid is not None and current_grid != grid:
                    raise ValueError('Source bands do not align.')
                grid = current_grid
                stack.append(source.read(1, window=window))
                masks.append(source.read_masks(1, window=window) > 0)
            scratch.unlink()
    values = np.stack(stack)
    inside = geometry_mask([projected], values.shape[1:], grid[2], invert=True)
    observed = inside & np.logical_and.reduce(masks)
    if not inside.any() or not observed.any():
        raise ValueError('No observed study pixels.')
    profile = dict(driver='GTiff', width=grid[1], height=grid[0],
                   crs='EPSG:32643', transform=grid[2], compress='deflate')
    with rasterio.open(output / 'raw_dn.tif', 'w', count=3, dtype=values.dtype, **profile) as saved:
        saved.write(values)
        saved.write_mask(observed.astype('uint8') * 255)
        for index, label in enumerate(['BAND2_green_DN', 'BAND3_red_DN', 'BAND4_NIR_DN'], 1):
            saved.set_band_description(index, label)
    with rasterio.open(output / 'observed_mask.tif', 'w', count=1, dtype='uint8', **profile) as saved:
        saved.write(observed.astype('uint8'), 1)
    rgb = np.zeros((*observed.shape, 4), dtype='uint8')
    for channel, band in enumerate([values[2], values[1], values[0]]):
        low, high = np.percentile(band[observed], [2, 98])
        rgb[:, :, channel] = np.clip((band.astype('float32') - low) / max(high - low, 1) * 255, 0, 255)
    rgb[:, :, 3] = observed.astype('uint8') * 255
    Image.fromarray(rgb).save(output / 'false_colour_NIR_red_green.png')
    with rasterio.open(output / 'raw_dn.tif') as saved:
        assert saved.crs.to_epsg() == 32643
        assert saved.transform == grid[2] and np.array_equal(saved.read(), values)
        assert np.array_equal(saved.dataset_mask() > 0, observed)
    report = dict(product=product, capture_date=spec['capture_date'], archive_sha256=spec['archive_sha256'],
                  study_area_version=properties['study_area_version'], crs='EPSG:32643',
                  source_crs_normalization='Supplier ellipsoid rounding normalized; original WKT in source_grid.json; no pixel resampling',
                  source_crs_max_corner_offset_m=crs_offset,
                  shape=list(values.shape), transform=list(grid[2])[:6],
                  attribution='ISRO-IRS', license_url='https://bhoonidhi.nrsc.gov.in/bhoonidhi/htmls/TnC.html',
                  native_resolution_m=5.8, output_spacing_m=5.0, radiometry='raw digital numbers; not surface reflectance',
                  band_order=['green', 'red', 'NIR'], study_pixels=int(inside.sum()),
                  observed_pixels=int(observed.sum()), cloud_quality_screened=False,
                  usable_coverage=None, labels_reviewed=False,
                  versions={name: importlib.metadata.version(name) for name in ['numpy', 'rasterio', 'Pillow']})
    report['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}
    (output / 'crop_report.json').write_text(json.dumps(report, indent=2) + '\n')
    exported = shutil.make_archive(str(output), 'zip', output)
    print(json.dumps(report, indent=2))
    print('Download:', exported)
    return output
