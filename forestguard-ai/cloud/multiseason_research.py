"""Hosted-only bounded 279 research experiment; supplied helpers reuse the sample pipeline."""
import hashlib
import json
import math
import platform
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

EXTRA_BANDS = [('rededge1','B05'),('rededge2','B06'),('rededge3','B07'),
               ('nir08','B8A'),('swir16','B11'),('swir22','B12')]
SEASONS = [('dry','2025-02-01T00:00:00Z/2025-04-30T23:59:59Z'),
           ('wet','2025-07-01T00:00:00Z/2025-09-30T23:59:59Z'),
           ('post_monsoon','2025-10-01T00:00:00Z/2025-12-31T23:59:59Z')]
SCL_SCREEN_LIMIT = 12
PROCESS_LIMIT = 3
MIN_FEATURE_COVERAGE = .9


def scl_coverage(classes, inside):
    import numpy as np
    if classes.shape != inside.shape or not inside.any():
        raise ValueError('Quality crop must share a nonempty study mask.')
    return float((np.isin(classes,[4,5,6]) & inside).sum()/inside.sum())


def run_research(boundary, base_run, feature_builder, reference_builder=None):
    if platform.system() == 'Windows' or not (Path('/kaggle/working').is_dir() or Path('/content').is_dir()):
        raise RuntimeError('Use the private hosted Kaggle/Colab notebook; local acquisition is disabled.')
    if boundary is None or boundary.get('type') != 'FeatureCollection' or len(boundary.get('features',[])) != 1:
        raise ValueError('Supply the selected 279 study polygon in the private notebook.')
    feature = boundary['features'][0]
    if feature['properties'].get('study_id') != 'handia-compartment-279':
        raise ValueError('Research input must identify the selected compartment 279 study.')
    base = Path('/kaggle/working') if Path('/kaggle/working').is_dir() else Path('/content')
    if shutil.disk_usage(base).free < 250*1024**2:
        raise RuntimeError('At least 250 MiB of hosted free storage is required.')
    import numpy as np
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.vrt import WarpedVRT
    from rasterio.warp import Resampling, reproject, transform_bounds, transform_geom
    from rasterio.windows import Window, from_bounds
    from PIL import Image

    output = base/'forestguard_279_research'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output.mkdir(parents=True)
    (output/'boundary.geojson').write_text(json.dumps(boundary,indent=2))
    results, failures, screens = [], [], []
    bbox = boundary['bbox']
    for season, interval in SEASONS:
        query = {'collections':['sentinel-2-c1-l2a'],'bbox':bbox,'datetime':interval,'limit':30,
                 'sortby':[{'field':'properties.eo:cloud_cover','direction':'asc'}]}
        request = Request('https://earth-search.aws.element84.com/v1/search',
                          data=json.dumps(query).encode(),headers={'Content-Type':'application/json'})
        try:
            with urlopen(request,timeout=60) as response:
                catalog_bytes = response.read(2*1024**2+1)
            if len(catalog_bytes) > 2*1024**2:
                raise ValueError('Season catalogue exceeds 2 MiB.')
            catalog = json.loads(catalog_bytes)
            (output/f'{season}_catalogue.json').write_bytes(catalog_bytes)
            candidates = sorted(catalog.get('features',[]),
                key=lambda item:(item['properties'].get('eo:cloud_cover',100),item['id']))[:SCL_SCREEN_LIMIT]
        except Exception as error:
            failures.append({'season':season,'stage':'catalogue','error':str(error)})
            continue
        if not candidates:
            failures.append({'season':season,'stage':'catalogue','error':'No candidate acquisitions returned.'})
        ranked=[]
        for item in candidates:
            try:
                href=item['assets']['scl']['href']
                if not href.startswith('https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/'):
                    raise ValueError('Unexpected quality asset host.')
                with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT='60',GDAL_CACHEMAX=32*1024**2):
                    with rasterio.open(href) as quality:
                        bounds=transform_bounds('EPSG:4326',quality.crs,*bbox,densify_pts=21)
                        raw_window=from_bounds(*bounds,transform=quality.transform)
                        left,top=math.floor(raw_window.col_off),math.floor(raw_window.row_off)
                        right,bottom=math.ceil(raw_window.col_off+raw_window.width),math.ceil(raw_window.row_off+raw_window.height)
                        if not (quality.res==(20.,20.) and 0<=left<right<=quality.width and 0<=top<bottom<=quality.height
                                and max(right-left,bottom-top)<=256):
                            raise ValueError('Invalid/oversized native quality window.')
                        window=Window(left,top,right-left,bottom-top)
                        classes=quality.read(1,window=window,masked=True).filled(0)
                        inside=geometry_mask([transform_geom('EPSG:4326',quality.crs,feature['geometry'])],
                                             classes.shape,quality.window_transform(window),invert=True,all_touched=False)
                fraction=scl_coverage(classes,inside)
                screens.append({'season':season,'scene_id':item['id'],'acquisition':item['properties']['datetime'],
                                'tile_cloud_percent':item['properties'].get('eo:cloud_cover'),
                                'local_scl_coverage_fraction':fraction,'inside_study_pixels':int(inside.sum())})
                ranked.append((fraction,item))
            except Exception as error:
                failures.append({'season':season,'scene_id':item['id'],'stage':'quality_screen','error':str(error)})
        ranked.sort(key=lambda pair:(-pair[0],pair[1]['id']))
        for _,item in ranked[:PROCESS_LIMIT]:
            try:
                cropped = base_run(bbox=bbox, area_label='Compartment 279 selected research polygon', scene_id=item['id'])
                source = json.loads((cropped/'source.json').read_text())
                assets = source['assets']
                with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='60', GDAL_CACHEMAX=64*1024**2):
                    href = assets['rededge1']['href']
                    if not href.startswith('https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/'):
                        raise ValueError('Unexpected asset host.')
                    with rasterio.open(href) as reference:
                        bounds = transform_bounds('EPSG:4326',reference.crs,*bbox,densify_pts=21)
                        window = from_bounds(*bounds,transform=reference.transform)
                        left,top = math.floor(window.col_off),math.floor(window.row_off)
                        right,bottom = math.ceil(window.col_off+window.width),math.ceil(window.row_off+window.height)
                        if not (0<=left<right<=reference.width and 0<=top<bottom<=reference.height and max(right-left,bottom-top)<=256):
                            raise ValueError('Invalid or oversized native-20 m crop.')
                        window = Window(left,top,right-left,bottom-top)
                        grid,crs,shape,full_grid = reference.window_transform(window),reference.crs,(bottom-top,right-left),reference.transform
                        if reference.res != (20.,20.):
                            raise ValueError('Red-edge reference must have native 20 m resolution.')
                    if results and (list(shape)!=results[0]['shape'] or str(crs)!=results[0]['crs'] or list(grid)[:6]!=results[0]['transform']):
                        raise ValueError('Seasonal observations must share the first accepted grid.')
                    with rasterio.open(cropped/'reflectance.tif') as saved:
                        with WarpedVRT(saved,crs=crs,transform=grid,height=shape[0],width=shape[1],resampling=Resampling.average) as aligned:
                            visible = aligned.read(masked=True)
                    support = np.zeros(shape,dtype='float32')
                    with rasterio.open(cropped/'usable.tif') as saved:
                        reproject(saved.read(1),support,src_transform=saved.transform,src_crs=saved.crs,
                                  dst_transform=grid,dst_crs=crs,resampling=Resampling.average)
                    values = list(visible.filled(np.nan))
                    band_order = ['B02','B03','B04','B08']
                    calibration = json.loads((cropped/'report.json').read_text())['calibration']
                    for key,name in EXTRA_BANDS:
                        asset = assets[key]
                        if not asset['href'].startswith('https://e84-earth-search-sentinel-data.s3.us-west-2.amazonaws.com/'):
                            raise ValueError('Unexpected asset host.')
                        scale,offset = asset['raster:bands'][0]['scale'],asset['raster:bands'][0]['offset']
                        with rasterio.open(asset['href']) as band:
                            if band.crs != crs or band.transform != full_grid or band.res != (20.,20.):
                                raise ValueError('Native 20 m bands do not share the reference grid.')
                            if not (math.isfinite(scale) and scale>0 and math.isfinite(offset) and
                                    math.isclose(band.scales[0],scale) and math.isclose(band.offsets[0],offset)):
                                raise ValueError('Calibration/header mismatch.')
                            raw = band.read(1,window=window,masked=True)
                        values.append(raw.filled(0).astype('float32')*scale+offset)
                        values[-1][np.ma.getmaskarray(raw)] = np.nan
                        band_order.append(name)
                        calibration[name] = {'scale':scale,'offset':offset,'href':asset['href']}
                inside = geometry_mask([transform_geom('EPSG:4326',crs,feature['geometry'])],shape,grid,invert=True,all_touched=False)
                if not inside.any():
                    raise ValueError('The study polygon has no raster pixel centres.')
                stack = np.stack(values)
                usable = inside & (support>=.999999) & np.isfinite(stack).all(axis=0) & ~np.ma.getmaskarray(visible).any(axis=0)
                features,feature_valid,names = feature_builder(stack,band_order,usable)
                fraction = float(feature_valid.sum()/inside.sum())
                if fraction < MIN_FEATURE_COVERAGE:
                    failures.append({'season':season,'scene_id':source['id'],'stage':'quality',
                                     'usable_fraction_inside_study':fraction,'error':f'Below {MIN_FEATURE_COVERAGE:.0%} feature-coverage screening target.'})
                    continue
                folder = output/season
                folder.mkdir()
                profile = dict(driver='GTiff',crs=crs,transform=grid,height=shape[0],width=shape[1],compress='deflate')
                for name,array,descriptions in [('reflectance',stack,band_order),('features',features,names)]:
                    stored = np.where(np.isfinite(array),array,-9999).astype('float32')
                    with rasterio.open(folder/f'{name}.tif','w',**profile,count=len(array),dtype='float32',nodata=-9999) as dst:
                        dst.write(stored); dst.descriptions = tuple(descriptions)
                    with rasterio.open(folder/f'{name}.tif') as saved:
                        if saved.transform != grid or saved.crs != crs or not np.array_equal(saved.read(),stored):
                            raise ValueError('Saved raster grid/pixels differ from computed outputs.')
                for name,array in [('study_mask',inside),('quality_mask',usable),('usable_mask',feature_valid)]:
                    with rasterio.open(folder/f'{name}.tif','w',**profile,count=1,dtype='uint8') as dst:
                        dst.write(array.astype('uint8'),1)
                    with rasterio.open(folder/f'{name}.tif') as saved:
                        if not np.array_equal(saved.read(1),array):
                            raise ValueError('Saved mask differs from computed mask.')
                rgb = (np.clip(np.nan_to_num(stack[[2,1,0]],nan=0)/.3,0,1)*255).astype('uint8').transpose(1,2,0)
                Image.fromarray(np.dstack([rgb,feature_valid.astype('uint8')*255])).save(folder/'preview.png')
                record = {'season':season,'scene_id':source['id'],'acquisition':source['properties']['datetime'],
                          'shape':list(shape),'crs':str(crs),'transform':list(grid)[:6],'analysis_resolution_m':20,
                          'band_order':band_order,'feature_order':names,'calibration':calibration,
                          'inside_study_pixels':int(inside.sum()),'usable_feature_pixels':int(feature_valid.sum()),
                          'usable_fraction_inside_study':fraction,'source_crop_path':str(cropped),
                          'source_crop_bundle':'source_crop.zip',
                          'quality_rule':'All included bands valid; SCL 4/5/6 support for all contributing 10 m pixels; valid 3x3 index neighborhood',
                          'resampling':'B02/B03/B04/B08 averaged from 10 m to native red-edge 20 m grid; extra bands read at native 20 m; no upsampling',
                          'texture_footprint_m':60,'model_trained':False,'labels_generated':False,
                          'source_license_url':'https://cds.climate.copernicus.eu/licences/ec-sentinel',
                          'attribution':f'Contains modified Copernicus Sentinel data {source["properties"]["datetime"][:4]}'}
                (folder/'source.json').write_text(json.dumps(source,indent=2))
                (folder/'report.json').write_text(json.dumps(record,indent=2))
                shutil.copy2(cropped/'forestguard_phase0.zip',folder/'source_crop.zip')
                results.append(record)
                print('Verified research crop:',season,source['id'],fraction)
                break
            except Exception as error:
                failures.append({'season':season,'scene_id':item['id'],'stage':'processing','error':str(error)})
                if (output/season).exists():
                    break  # Keep a partial failed write for diagnosis; never replace it with another scene.
    reference=None
    if reference_builder is not None:
        try:
            reference=reference_builder(output,boundary,results)
        except Exception as error:
            failures.append({'stage':'weak_reference','error':str(error)})
    report = {'study_id':'handia-compartment-279','status':'COMPLETE_DATA_SCREENING' if len(results)==len(SEASONS) else 'PARTIAL_DATA_SCREENING',
              'acquisitions':results,'failed_attempts':failures,'quality_screens':screens,'season_windows':SEASONS,
              'scl_screen_limit_per_season':SCL_SCREEN_LIMIT,'candidate_limit_per_season':PROCESS_LIMIT,
              'minimum_feature_coverage':MIN_FEATURE_COVERAGE,'weak_reference':reference,
              'labels_reviewed':0,'model_trained':False,'independent_model_accuracy_measured':False,
              'cloud_runtime':{'python':platform.python_version(),'numpy':np.__version__,'rasterio':rasterio.__version__,'gdal':rasterio.__gdal_version__}}
    (output/'research_report.json').write_text(json.dumps(report,indent=2))
    manifest = {str(path.relative_to(output)):{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
                for path in output.rglob('*') if path.is_file()}
    (output/'checksums.json').write_text(json.dumps(manifest,indent=2))
    bundle = output/'forestguard_279_research.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in [*manifest,'checksums.json']:
            archive.write(output/name,arcname=name)
    with zipfile.ZipFile(bundle) as archive:
        if archive.testzip() is not None:
            raise ValueError('Export archive is corrupt.')
        for name,record in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=record['sha256']:
                raise ValueError('Export archive hash mismatch.')
    print(json.dumps(report,indent=2)); print('Verified research ZIP:',bundle)
    return output
