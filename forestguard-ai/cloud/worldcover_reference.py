"""Bounded public WorldCover crop: historical weak reference, never forest ground truth."""
import json
import math
from urllib.request import Request, urlopen

WORLD_COVER_CLASSES={10:'Tree cover',20:'Shrubland',30:'Grassland',40:'Cropland',50:'Built-up',
                     60:'Bare / sparse vegetation',70:'Snow and ice',80:'Permanent water',
                     90:'Herbaceous wetland',95:'Mangroves',100:'Moss and lichen'}


def worldcover_tile(bbox):
    west,south,east,north=bbox
    lon,lat=math.floor(west/3)*3,math.floor(south/3)*3
    if not (lon<=west<east<=lon+3 and lat<=south<north<=lat+3):
        raise ValueError('This bounded experiment needs a study within one WorldCover tile.')
    return f'{"N" if lat>=0 else "S"}{abs(lat):02d}{"E" if lon>=0 else "W"}{abs(lon):03d}'


def prepare_worldcover(output,boundary,observations):
    import platform
    from pathlib import Path
    if platform.system()=='Windows' or not (Path('/kaggle/working').is_dir() or Path('/content').is_dir()):
        raise RuntimeError('Use the private hosted notebook for reference acquisition.')
    import numpy as np
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.warp import Resampling,reproject,transform_geom
    from rasterio.windows import Window,from_bounds
    from affine import Affine
    bbox=boundary['bbox']
    tile=worldcover_tile(bbox)
    url=f'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif'
    folder=output/'weak_reference';folder.mkdir()
    with urlopen(Request(url,method='HEAD'),timeout=30) as response:
        source_bytes=int(response.headers['Content-Length'])
        etag=response.headers.get('ETag')
        if source_bytes>1024**3:
            raise ValueError('Source metadata exceeds the expected 1 GiB tile bound; no full download attempted.')
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT='60',GDAL_CACHEMAX=32*1024**2):
        with rasterio.open(url) as source:
            if str(source.crs)!='EPSG:4326' or source.count!=1 or not np.allclose(source.res,[1/12000,1/12000],rtol=1e-6):
                raise ValueError('Unexpected WorldCover source CRS/band count/resolution.')
            window=from_bounds(*bbox,transform=source.transform)
            left,top=math.floor(window.col_off),math.floor(window.row_off)
            right,bottom=math.ceil(window.col_off+window.width),math.ceil(window.row_off+window.height)
            if not (0<=left<right<=source.width and 0<=top<bottom<=source.height and max(right-left,bottom-top)<=512):
                raise ValueError('Reference window is invalid or exceeds 512 pixels per side.')
            window=Window(left,top,right-left,bottom-top)
            values=source.read(1,window=window,masked=True).filled(0)
            grid=source.window_transform(window)
            colors=source.colormap(1)
    if not set(np.unique(values))<=set(WORLD_COVER_CLASSES)|{0}:
        raise ValueError('Unrecognized WorldCover class codes.')
    inside=geometry_mask([boundary['features'][0]['geometry']],values.shape,grid,invert=True,all_touched=False)
    if not inside.any():raise ValueError('Reference has no study pixel centres.')
    profile=dict(driver='GTiff',crs='EPSG:4326',transform=grid,height=values.shape[0],width=values.shape[1],
                 count=1,dtype='uint8',nodata=0,compress='deflate')
    with rasterio.open(folder/'worldcover_2021_native.tif','w',**profile) as saved:
        saved.write(values,1);saved.write_colormap(1,colors)
        saved.set_band_description(1,'WorldCover 2021 v200 class code; weak historical reference')
    with rasterio.open(folder/'worldcover_2021_native.tif') as saved:
        if saved.transform!=grid or not np.array_equal(saved.read(1),values):
            raise ValueError('Saved native reference differs from source crop.')
    aligned=[]
    for observation in observations:
        shape=observation['shape'];transform=Affine(*observation['transform'])
        target=np.zeros(shape,dtype='uint8')
        reproject(values,target,src_transform=grid,src_crs='EPSG:4326',dst_transform=transform,
                  dst_crs=observation['crs'],src_nodata=0,dst_nodata=0,resampling=Resampling.nearest)
        mask=geometry_mask([transform_geom('EPSG:4326',observation['crs'],boundary['features'][0]['geometry'])],
                          shape,transform,invert=True,all_touched=False)
        target[~mask]=0
        with rasterio.open(output/observation['season']/'worldcover_2021_weak.tif','w',**{
            **profile,'crs':observation['crs'],'transform':transform,'height':shape[0],'width':shape[1]}) as saved:
            saved.write(target,1);saved.write_colormap(1,colors)
        with rasterio.open(output/observation['season']/'worldcover_2021_weak.tif') as saved:
            if saved.transform!=transform or not np.array_equal(saved.read(1),target):
                raise ValueError('Saved aligned weak reference differs from computed crop.')
        codes,counts=np.unique(target[mask],return_counts=True)
        aligned.append({'season':observation['season'],'grid_class_pixel_counts':dict(zip(map(str,codes),map(int,counts)))})
    codes,counts=np.unique(values[inside],return_counts=True)
    record={'dataset':'ESA WorldCover 2021 v200','reference_year':2021,'tile_id':tile,'source_url':url,
            'source_tile_bytes':source_bytes,'source_etag':etag,'full_tile_downloaded':False,
            'native_crs':'EPSG:4326','native_resolution_degrees':1/12000,'native_shape':list(values.shape),
            'native_transform':list(grid)[:6],'class_mapping':WORLD_COVER_CLASSES,
            'class_pixel_counts_inside_study':dict(zip(map(str,codes),map(int,counts))),
            'aligned_grids':aligned,'categorical_resampling':'nearest neighbour to observation pixel centres',
            'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/',
            'attribution':'© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium',
            'citation':'Zanaga et al. (2022). ESA WorldCover 10 m 2021 v200. https://doi.org/10.5281/zenodo.7254221',
            'reference_kind':'weak_map','reference_independent':False,'reviewed_labels_exist':False,
            'limits':'2021 predicted classes; tree cover includes plantations and agricultural trees. No conversion to verified current forest labels or area.'}
    (folder/'reference_report.json').write_text(json.dumps(record,indent=2))
    print('Verified small WorldCover weak reference:',tile,values.shape)
    return record
