"""Verify a bounded research ZIP offline; this is not classifier validation."""
import argparse
import hashlib
import io
import json
import math
import zipfile
import sys
from pathlib import Path
from affine import Affine

import numpy as np
from rasterio.io import MemoryFile
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom, reproject, Resampling
from verify_bundle import verify as verify_source_bundle

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cloud'))
from research_features import research_features


def verify(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = set(archive.namelist())
        if len(entries) != len(names) or sum(e.file_size for e in entries)>30*1024**2:
            raise ValueError('Duplicate or oversized research archive.')
        manifest = json.loads(archive.read('checksums.json'))
        if names != set(manifest)|{'checksums.json'} or archive.testzip() is not None:
            raise ValueError('Archive/manifest mismatch or failed CRC.')
        for name,record in manifest.items():
            if Path(name).is_absolute() or '\\' in name or ':' in name or '..' in Path(name).parts:
                raise ValueError('Unsafe archive member.')
            content = archive.read(name)
            if len(content)!=record['bytes'] or hashlib.sha256(content).hexdigest()!=record['sha256']:
                raise ValueError(f'Integrity failure: {name}')
        report = json.loads(archive.read('research_report.json'))
        boundary = json.loads(archive.read('boundary.geojson'))
        if (report['study_id']!='handia-compartment-279' or report['labels_reviewed']!=0
                or report['model_trained'] or report['independent_model_accuracy_measured']):
            raise ValueError('Invalid research scope/claims.')
        seasons=[item['season'] for item in report['acquisitions']]
        if len(seasons)!=len(set(seasons)) or not set(seasons)<={'dry','wet','post_monsoon'}:
            raise ValueError('Invalid accepted seasons.')
        expected_status='COMPLETE_DATA_SCREENING' if len(seasons)==3 else 'PARTIAL_DATA_SCREENING'
        if report['status']!=expected_status:
            raise ValueError('Screening status does not match acquired seasons.')
        checked=[]
        common=None
        study_count=None
        shared_grid=None
        for item in report['acquisitions']:
            grid_key=(item['shape'],item['crs'],item['transform'])
            if shared_grid is not None and grid_key!=shared_grid:
                raise ValueError('Accepted observations do not share a common grid.')
            shared_grid=grid_key
            prefix=item['season']+'/'
            source=json.loads(archive.read(prefix+'source.json'))
            if item['scene_id']!=source['id'] or item['acquisition']!=source['properties']['datetime']:
                raise ValueError('Scene/date provenance mismatch.')
            arrays={}
            for name in ['reflectance','features','study_mask','usable_mask']:
                with MemoryFile(archive.read(prefix+name+'.tif')) as memory, memory.open() as raster:
                    if (list(raster.shape)!=item['shape'] or max(raster.shape)>256 or raster.res!=(20.,20.)
                            or str(raster.crs)!=item['crs'] or list(raster.transform)[:6]!=item['transform']):
                        raise ValueError('Saved grid mismatch.')
                    arrays[name]=raster.read(masked=True)
                    if name in ['reflectance','features']:
                        expected=item['band_order'] if name=='reflectance' else item['feature_order']
                        if list(raster.descriptions)!=expected:
                            raise ValueError('Saved band/feature order mismatch.')
                    if name=='study_mask':
                        inside=geometry_mask([transform_geom('EPSG:4326',raster.crs,boundary['features'][0]['geometry'])],
                                             raster.shape,raster.transform,invert=True,all_touched=False)
            usable=arrays['usable_mask'][0].filled(0).astype(bool)
            common=usable.copy() if common is None else common & usable
            study_count=int(inside.sum())
            if not np.array_equal(arrays['study_mask'][0],inside) or np.any(usable & ~inside):
                raise ValueError('Saved boundary/coverage mask mismatch.')
            if (item['inside_study_pixels']!=int(inside.sum()) or item['usable_feature_pixels']!=int(usable.sum())
                    or not math.isclose(item['usable_fraction_inside_study'],usable.sum()/inside.sum(),abs_tol=1e-12)
                    or item['usable_fraction_inside_study']<.9):
                raise ValueError('Coverage count/denominator/threshold mismatch.')
            values=arrays['reflectance'].filled(np.nan)
            features=arrays['features'].filled(np.nan)
            if not np.isfinite(features[:,usable]).all() or np.isfinite(features[:,~usable]).any():
                raise ValueError('Feature validity differs from saved mask.')
            if not np.array_equal(values[:,usable],features[:len(values),usable]):
                raise ValueError('Reflectance features differ from saved inputs.')
            if 'source_crop_bundle' in item:
                original=archive.read(prefix+item['source_crop_bundle'])
                source_check=verify_source_bundle(io.BytesIO(original))
                if source_check['scene_id']!=item['scene_id']:
                    raise ValueError('Preserved source crop belongs to another acquisition.')
                with zipfile.ZipFile(io.BytesIO(original)) as crop:
                    with MemoryFile(crop.read('usable.tif')) as memory, memory.open() as raster:
                        support=np.zeros(item['shape'],dtype='float32')
                        reproject(raster.read(1),support,src_transform=raster.transform,src_crs=raster.crs,
                                  dst_transform=Affine(*item['transform']),dst_crs=item['crs'],resampling=Resampling.average)
                expected_quality=inside & (support>=.999999) & np.isfinite(values).all(axis=0)
                with MemoryFile(archive.read(prefix+'quality_mask.tif')) as memory, memory.open() as raster:
                    if (list(raster.shape)!=item['shape'] or str(raster.crs)!=item['crs']
                            or list(raster.transform)[:6]!=item['transform'] or not np.array_equal(raster.read(1),expected_quality)):
                        raise ValueError('Quality mask differs from preserved source observations.')
                rebuilt,rebuilt_mask,rebuilt_names=research_features(values,item['band_order'],expected_quality)
                if (rebuilt_names!=item['feature_order'] or not np.array_equal(rebuilt_mask,usable)
                        or not np.allclose(rebuilt,features,equal_nan=True,atol=1e-6)):
                    raise ValueError('Offline feature/texture reconstruction differs from saved computation.')
            bands=dict(zip(item['band_order'],values[:,usable]))
            formula=[(bands['B08']-bands['B04'])/(bands['B08']+bands['B04']),
                     2.5*(bands['B08']-bands['B04'])/(bands['B08']+6*bands['B04']-7.5*bands['B02']+1),
                     (bands['B8A']-bands['B05'])/(bands['B8A']+bands['B05']),
                     (bands['B8A']-bands['B11'])/(bands['B8A']+bands['B11'])]
            if not np.allclose(features[len(values):len(values)+4,usable],formula,atol=1e-6):
                raise ValueError('Saved index formulas differ from calibrated inputs.')
            checked.append({'season':item['season'],'date':item['acquisition'],
                            'feature_coverage_fraction':item['usable_fraction_inside_study']})
        reference=report.get('weak_reference')
        if reference:
            if (reference['reference_year']!=2021 or reference['reference_kind']!='weak_map'
                    or reference['reference_independent'] or reference['reviewed_labels_exist'] or reference['full_tile_downloaded']):
                raise ValueError('Weak reference must preserve date/type/limits.')
            with MemoryFile(archive.read('weak_reference/worldcover_2021_native.tif')) as memory, memory.open() as raster:
                if (list(raster.shape)!=reference['native_shape'] or max(raster.shape)>512
                        or str(raster.crs)!=reference['native_crs'] or list(raster.transform)[:6]!=reference['native_transform']):
                    raise ValueError('Weak reference native grid mismatch.')
                values=raster.read(1)
                native_grid=raster.transform
                inside=geometry_mask([boundary['features'][0]['geometry']],raster.shape,raster.transform,invert=True,all_touched=False)
            if not set(np.unique(values)) <= {int(code) for code in reference['class_mapping']}|{0}:
                raise ValueError('Invalid weak reference classes.')
            codes,counts=np.unique(values[inside],return_counts=True)
            if dict(zip(map(str,codes),map(int,counts)))!=reference['class_pixel_counts_inside_study']:
                raise ValueError('Weak reference counts differ from the saved crop.')
            if {entry['season'] for entry in reference['aligned_grids']}!=set(seasons):
                raise ValueError('Weak reference aligned-season list differs from observations.')
            for item in report['acquisitions']:
                target=np.zeros(item['shape'],dtype='uint8')
                transform=Affine(*item['transform'])
                reproject(values,target,src_transform=native_grid,src_crs='EPSG:4326',dst_transform=transform,
                          dst_crs=item['crs'],src_nodata=0,dst_nodata=0,resampling=Resampling.nearest)
                mask=geometry_mask([transform_geom('EPSG:4326',item['crs'],boundary['features'][0]['geometry'])],
                                   item['shape'],transform,invert=True,all_touched=False)
                target[~mask]=0
                with MemoryFile(archive.read(item['season']+'/worldcover_2021_weak.tif')) as memory, memory.open() as raster:
                    if (raster.transform!=transform or str(raster.crs)!=item['crs'] or not np.array_equal(raster.read(1),target)):
                        raise ValueError('Aligned historical classes differ from nearest-neighbor resampling.')
    return {'integrity':'PASS','verified_files':len(manifest),'status':report['status'],
            'accepted':checked,'failed_attempts':len(report['failed_attempts']),
            'weak_reference_verified':bool(reference),
            'common_feature_valid_pixels':int(common.sum()) if common is not None else 0,
            'common_feature_coverage_fraction':float(common.sum()/study_count) if common is not None else None,
            'limits':'Archive, grid, mask, counts and index checks; no independent forest accuracy or registration measurement.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.zip),indent=2))
