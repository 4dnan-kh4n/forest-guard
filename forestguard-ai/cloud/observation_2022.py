"""Bounded hosted 2022 crop using original product XML calibration."""
import hashlib
import json
import math
import platform
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen

BAND_IDS={'B02':'1','B03':'2','B04':'3','B08':'7','B05':'4','B06':'5','B07':'6','B8A':'8','B11':'11','B12':'12'}
PC_ITEM=None


def calibration_xml(raw):
    if len(raw)>1024**2 or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('Unsafe product XML')
    root=ET.fromstring(raw)
    values={}
    offsets={}
    for element in root.iter():
        tag=element.tag.split('}')[-1]
        if tag in ['BOA_QUANTIFICATION_VALUE','PROCESSING_BASELINE']:values[tag]=element.text
        if tag=='BOA_ADD_OFFSET':offsets[element.attrib['band_id']]=float(element.text)
    quant=float(values['BOA_QUANTIFICATION_VALUE'])
    if not math.isfinite(quant) or quant<=0 or float(values['PROCESSING_BASELINE'])<5:raise ValueError('Require reprocessed Collection-1 metadata')
    if any(key not in offsets or not math.isfinite(offsets[key]) for key in BAND_IDS.values()):raise ValueError('Missing band offsets')
    return {band:{'scale':1/quant,'offset':offsets[key]/quant} for band,key in BAND_IDS.items()}


def run_2022(boundary,base_run,feature_builder):
    base=Path('/kaggle/working') if Path('/kaggle/working').is_dir() else Path('/content')
    if platform.system()=='Windows' or not base.is_dir():raise RuntimeError('Use private Kaggle/Colab CPU runtime')
    if shutil.disk_usage(base).free<250*1024**2:raise ValueError('Insufficient cloud storage')
    if boundary is None or PC_ITEM is None:raise ValueError('Use prepared private notebook')
    import numpy as np
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.windows import from_bounds,Window
    from rasterio.warp import transform_bounds,transform_geom,Resampling
    from rasterio.vrt import WarpedVRT
    from PIL import Image
    item=PC_ITEM
    if item['id']!='S2A_MSIL2A_20221001T052651_R105_T43QFE_20240724T063709':raise ValueError('Unreviewed source scene')
    with urlopen('https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel2l2a01/sentinel2-l2',timeout=30) as response:token=json.loads(response.read(16385))['token']
    def signed(href):
        if not href.startswith('https://sentinel2l2a01.blob.core.windows.net/sentinel2-l2/') or '?' in href:raise ValueError('Unexpected asset URL')
        return href+'?'+token
    with urlopen(signed(item['assets']['product-metadata']['href']),timeout=30) as response:xml=response.read(1024**2+1)
    calibration=calibration_xml(xml)
    output=base/'forestguard_2022'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');folder=output/'2022';folder.mkdir(parents=True)
    (output/'boundary.geojson').write_bytes((json.dumps(boundary,indent=2)+'\n').encode())
    (folder/'product.xml').write_bytes(xml)
    (folder/'source.json').write_bytes((json.dumps(item,indent=2)+'\n').encode())
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT=60,GDAL_CACHEMAX=64*1024**2):
        with rasterio.open(signed(item['assets']['B05']['href'])) as src:
            bounds=transform_bounds('EPSG:4326',src.crs,*boundary['bbox'])
            crop=from_bounds(*bounds,transform=src.transform)
            left,top=math.floor(crop.col_off),math.floor(crop.row_off)
            right,bottom=math.ceil(crop.col_off+crop.width),math.ceil(crop.row_off+crop.height)
            if not (src.res==(20.,20.) and 0<=left<right<=src.width and 0<=top<bottom<=src.height and max(right-left,bottom-top)<=256):raise ValueError('Invalid crop budget/grid')
            window=Window(left,top,right-left,bottom-top);grid=src.window_transform(window);crs=src.crs;shape=(bottom-top,right-left)
        arrays=[];valid=np.ones(shape,dtype=bool)
        for band in BAND_IDS:
            with rasterio.open(signed(item['assets'][band]['href'])) as src:
                expected=10. if band in ['B02','B03','B04','B08'] else 20.
                if src.crs!=crs or src.res!=(expected,expected):raise ValueError('Unexpected native band grid')
                # These COGs preserve SAFE digital numbers; XML supplies calibration.
                if (src.scales[0],src.offsets[0])!=(1.,0.):raise ValueError('Encoded calibration requires review before applying XML')
                with WarpedVRT(src,crs=crs,transform=grid,height=shape[0],width=shape[1],resampling=Resampling.average) as aligned:raw=aligned.read(1,masked=True).astype('float32')
            valid&=~np.ma.getmaskarray(raw)
            arrays.append(raw.filled(np.nan)*calibration[band]['scale']+calibration[band]['offset'])
        with rasterio.open(signed(item['assets']['SCL']['href'])) as src:
            if src.crs!=crs or src.res!=(20.,20.):raise ValueError('Invalid SCL grid')
            with WarpedVRT(src,crs=crs,transform=grid,height=shape[0],width=shape[1],resampling=Resampling.nearest) as aligned:scl=aligned.read(1)
    inside=geometry_mask([transform_geom('EPSG:4326',crs,boundary['features'][0]['geometry'])],shape,grid,invert=True)
    stack=np.stack(arrays);valid&=inside&np.isin(scl,[4,5,6])&np.isfinite(stack).all(axis=0)
    features,usable,names=feature_builder(stack,list(BAND_IDS),valid)
    fraction=float(usable.sum()/inside.sum())
    if fraction<.5:raise ValueError(f'2022 feature coverage below viewing threshold: {fraction:.3f}')
    profile=dict(driver='GTiff',crs=crs,transform=grid,height=shape[0],width=shape[1],compress='deflate')
    for name,array,order in [('features',features,names),('reflectance',stack,list(BAND_IDS))]:
        with rasterio.open(folder/f'{name}.tif','w',**profile,count=len(array),dtype='float32',nodata=-9999) as dst:
            dst.write(np.where(np.isfinite(array),array,-9999).astype('float32'));dst.descriptions=tuple(order)
    for name,array in [('usable_mask',usable),('study_mask',inside),('scene_classes',scl)]:
        with rasterio.open(folder/f'{name}.tif','w',**profile,count=1,dtype='uint8') as dst:dst.write(array.astype('uint8'),1)
    rgb=(np.moveaxis(np.nan_to_num(np.clip(stack[[2,1,0]]/0.3,0,1)),0,-1)*255).astype('uint8')
    Image.fromarray(np.dstack([rgb,usable.astype('uint8')*255])).save(folder/'preview.png')
    record={'season':'2022','scene_id':item['id'],'acquisition':item['properties']['datetime'],'shape':list(shape),'crs':str(crs),'transform':list(grid)[:6],
            'feature_order':names,'band_order':list(BAND_IDS),'inside_study_pixels':int(inside.sum()),'usable_feature_pixels':int(usable.sum()),
            'usable_fraction_inside_study':fraction,'calibration':calibration,'product_xml_sha256':hashlib.sha256(xml).hexdigest(),
            'calibration_source':item['assets']['product-metadata']['href'],'attribution':'Contains modified Copernicus Sentinel data 2022',
            'source_license_url':'https://cds.climate.copernicus.eu/licences/ec-sentinel','analysis_resolution_m':20,
            'quality_rule':'Valid bands; SCL 4/5/6; valid 3x3 texture neighbourhood; native 20m grid',
            'resampling':'10m reflectance bands averaged to 20m; SCL nearest; 20m bands retained at native resolution'}
    (folder/'report.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
    (output/'research_report.json').write_bytes((json.dumps({'acquisitions':[record],'cloud_runtime':{'numpy':np.__version__,'rasterio':rasterio.__version__}},indent=2)+'\n').encode())
    print('Verified 2022 crop:',fraction)
    return output
