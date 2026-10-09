"""Cloud-only small ETH 2020 predicted-height crop; never current forest truth."""
import hashlib
import json
import math
import platform
import shutil
from pathlib import Path
from urllib.request import Request, urlopen


def run_height_reference(study, cases, sources):
    if platform.system() == 'Windows' or not Path('/kaggle/working').is_dir():
        raise RuntimeError('Run the reference acquisition in a hosted Kaggle CPU notebook.')
    import numpy as np
    import rasterio
    from rasterio.features import bounds, geometry_mask
    from rasterio.warp import transform_geom
    from rasterio.windows import Window, from_bounds

    if len(study['features']) != 1 or len(cases['features']) > 30:
        raise ValueError('Expected one study polygon and at most 30 review cases.')
    output = Path('/kaggle/working/eth_2020_height_reference')
    if output.exists():
        raise FileExistsError('Preserve previous output before another run.')
    output.mkdir()
    record = dict(dataset='ETH Global Canopy Height 2020 v1', reference_year=2020,
        license='CC BY 4.0', citation='Lang et al. (2023), https://doi.org/10.1038/s41559-023-02206-6',
        dataset_doi='https://doi.org/10.3929/ethz-b-000609802',
        reference_kind='weak_map', reference_independent=False, labels_generated=False,
        limits='Model estimates from 2020 Sentinel-2/GEDI; stale and not independent 2025 ground truth. Standard deviation is predictive uncertainty, not a calibrated local confidence interval.',
        sources=[], cases=[])
    arrays = {}
    previous = None
    for spec in sources:
        url = spec['url']
        if not url.startswith('https://libdrive.ethz.ch/') or spec['kind'] not in ['height', 'standard_deviation']:
            raise ValueError('Unexpected source.')
        with urlopen(Request(url, headers={'Range':'bytes=0-1023'}), timeout=30) as response:
            if response.status != 206 or response.headers.get('Content-Range') != f"bytes 0-1023/{spec['bytes']}":
                raise ValueError('Source must support bounded range reads with the verified size.')
            header = response.read(1025)
        if len(header) != 1024 or hashlib.sha256(header).hexdigest() != spec['header_sha256']:
            raise ValueError('Source header changed; inspect before adoption.')
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='30',
                          GDAL_CACHEMAX=16*1024**2):
            with rasterio.open('/vsicurl/' + url) as source:
                if source.count != 1 or source.crs is None:
                    raise ValueError('Expected single-band georeferenced data.')
                projected = transform_geom('EPSG:4326', source.crs, study['features'][0]['geometry'])
                w = from_bounds(*bounds(projected), transform=source.transform)
                x,y = math.floor(w.col_off),math.floor(w.row_off)
                right,bottom = math.ceil(w.col_off+w.width),math.ceil(w.row_off+w.height)
                if not (0 <= x < right <= source.width and 0 <= y < bottom <= source.height
                        and max(right-x,bottom-y) <= 512):
                    raise ValueError('Study crop outside source or exceeds 512 pixels per side.')
                window = Window(x,y,right-x,bottom-y)
                grid = source.window_transform(window)
                raw = source.read(1,window=window,masked=True)
                current = (raw.shape, grid, source.crs)
                if previous is not None and current != previous:
                    raise ValueError('Height and uncertainty grids differ.')
                previous = current
                inside = geometry_mask([projected],raw.shape,grid,invert=True)
                values = raw.astype('float32') * source.scales[0] + source.offsets[0]
                valid = inside & ~np.ma.getmaskarray(values) & np.isfinite(values.filled(np.nan))
                if not valid.any():
                    raise ValueError('No valid study estimates.')
                saved_values = np.where(valid,values.filled(np.nan),np.nan).astype('float32')
                arrays[spec['kind']] = saved_values
                profile = dict(driver='GTiff',crs=source.crs,transform=grid,count=1,
                    height=raw.shape[0],width=raw.shape[1],dtype='float32',nodata=np.nan,compress='deflate')
                record['sources'].append(dict(**spec, source_crs=str(source.crs),
                    source_shape=list(source.shape), source_resolution=list(source.res), source_dtype=source.dtypes[0],
                    source_nodata=source.nodata, scale=source.scales[0], offset=source.offsets[0],
                    tags=source.tags(), band_tags=source.tags(1), source_units=source.units[0],
                    crop_shape=list(raw.shape), crop_transform=list(grid)[:6],
                    study_centres=int(inside.sum()),valid_centres=int(valid.sum()),
                    full_tile_downloaded=False))
        path = output/(spec['kind']+'.tif')
        with rasterio.open(path,'w',**profile) as saved:
            saved.write(saved_values,1)
            saved.set_band_description(1,'ETH 2020 model '+spec['kind']+'; weak historical reference')
        with rasterio.open(path) as saved:
            assert saved.transform == grid and np.array_equal(saved.read(1),saved_values,equal_nan=True)
    for feature in cases['features']:
        geometry = transform_geom('EPSG:4326',previous[2],feature['geometry'])
        patch = geometry_mask([geometry],previous[0],previous[1],invert=True)
        stats = dict(label_id=feature['properties']['label_id'],class_assigned=False)
        for kind,values in arrays.items():
            selected = values[patch & np.isfinite(values)]
            stats[kind] = dict(valid_centres=int(selected.size),median=float(np.median(selected)) if selected.size else None,
                               minimum=float(selected.min()) if selected.size else None,maximum=float(selected.max()) if selected.size else None)
        record['cases'].append(stats)
    record['files'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    (output/'reference_report.json').write_text(json.dumps(record,indent=2)+'\n')
    shutil.make_archive(str(output),'zip',output)
    print(json.dumps(record,indent=2))
    return output
