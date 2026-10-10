"""Verify a bounded cloud export before registering officer-facing annual images."""
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path,PurePosixPath

import numpy as np
import rasterio
from rasterio.io import MemoryFile

ROOT=Path(__file__).resolve().parents[1]
MODEL_SHA='8bf0858faaee969b35e003c466de19ab1767a96c5c8ed9098cb8010f13d3a6b8'


def verify(path):
    if path.is_symlink() or path.stat().st_size>30*1024**2:raise ValueError('Archive exceeds budget or is a link')
    with zipfile.ZipFile(path) as archive:
        entries=archive.infolist();names=[entry.filename for entry in entries]
        if len(names)>64 or len(names)!=len(set(names)) or sum(entry.file_size for entry in entries)>50*1024**2:
            raise ValueError('Archive exceeds file budget or contains duplicates')
        if any(PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or '\\' in name or ':' in name for name in names):
            raise ValueError('Unsafe archive path')
        hashes=json.loads(archive.read('annual_checksums.json'))
        if set(names)!={*hashes,'annual_checksums.json'}:raise ValueError('Unexpected archive files')
        for name,digest in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=digest:raise ValueError('Corrupt annual file: '+name)
        report=json.loads(archive.read('annual_report.json'))
        if (report.get('format')!='forestguard-annual-observations-v1' or report.get('model_sha256')!=MODEL_SHA
                or report.get('independent_forest_accuracy_measured') is not False):raise ValueError('Unsupported annual report')
        boundary=json.loads(archive.read('boundary.geojson'))
        if boundary!=json.loads((ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes()):raise ValueError('Boundary differs from selected compartment')
        rows=report['observations'];years=[row['year'] for row in rows]
        if not rows:raise ValueError('Run exported no accepted annual images; inspect research_report.json')
        if len(years)!=len(set(years)) or not set(years)<=set(range(2022,2027)):raise ValueError('Invalid annual years')
        first=None
        for row in rows:
            year=row['year'];prefix=str(year)+'/'
            acquired=date.fromisoformat(row['date'])
            if acquired.year!=year or acquired>date.today() or row.get('synthetic') is not False:raise ValueError('Invalid acquisition provenance')
            details=json.loads(archive.read(prefix+'report.json'))
            if details['scene_id']!=row['scene_id'] or details['acquisition'][:10]!=row['date']:raise ValueError('Scene provenance differs')
            def raster(name):
                with MemoryFile(archive.read(prefix+name+'.tif')) as memory:
                    with memory.open() as src:
                        if max(src.shape)>256 or src.crs!=rasterio.crs.CRS.from_epsg(32643) or src.res!=(20.,20.):raise ValueError('Unexpected annual grid')
                        return src.read(),(src.shape,src.crs,src.transform),src.descriptions
            features,grid,order=raster('features');mask,maskgrid,_=raster('usable_mask');study,studygrid,_=raster('study_mask')
            if first is None:first=grid
            if grid!=first or maskgrid!=grid or studygrid!=grid or features.shape[0]!=15:raise ValueError('Annual layers are not aligned')
            if not np.isin(mask,[0,1]).all() or not np.isin(study,[0,1]).all():raise ValueError('Invalid mask values')
            valid=mask[0]==1;inside=study[0]==1
            if not valid.any() or (valid&~inside).any() or not np.isfinite(features[:,valid]).all():raise ValueError('Invalid feature coverage')
            count=int(valid.sum());total=int(inside.sum())
            if count!=row['usable_pixels'] or total!=row['study_pixels'] or not np.isclose(count/total,row['coverage_fraction']):raise ValueError('Coverage statistics differ')
            if report['model_available']:
                classes,classgrid,_=raster('proxy_classes')
                if classgrid!=grid or not np.isin(classes[0,valid],[0,1]).all() or not (classes[0,~valid]==255).all():raise ValueError('Invalid proxy classes')
                trees=int((classes[0]==1).sum())
                if not np.isclose(trees*.04,row['tree_cover_proxy_ha']) or not np.isclose(100*trees/count,row['tree_cover_proxy_percent']):raise ValueError('Tree extent statistics differ')
            elif row['tree_cover_proxy_percent'] is not None or row['tree_cover_proxy_ha'] is not None:raise ValueError('Missing model produced estimates')
            with MemoryFile(archive.read(prefix+'preview.png')) as memory:
                with memory.open() as image:
                    if image.driver!='PNG' or image.shape!=grid[0]:raise ValueError('Preview grid differs')
                    image.read()
        return report,hashes


def register(path):
    report,hashes=verify(path)
    target=ROOT/'data/annual/observations_v1'
    if target.exists():raise ValueError('Preserve the existing annual version before registering a replacement')
    with tempfile.TemporaryDirectory(prefix='annual_import_',dir=ROOT/'data/annual') as temporary:
        saved=Path(temporary)/'observations';saved.mkdir()
        with zipfile.ZipFile(path) as archive:
            for name in [*hashes,'annual_checksums.json']:
                destination=saved/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(archive.read(name))
        selected=['annual_report.json']+[str(row['year'])+'/preview.png' for row in report['observations']]
        (saved/'ui_checksums.json').write_bytes((json.dumps({name:hashes[name] for name in selected},indent=2)+'\n').encode())
        from build_annual_changes import save
        save(saved,report)
        (saved/'import_record.json').write_bytes((json.dumps({'archive_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'verified_years':[r['year'] for r in report['observations']]},indent=2)+'\n').encode())
        shutil.move(str(saved),str(target))
    print(json.dumps({'status':'PASS','years':[r['year'] for r in report['observations']],'independent_forest_accuracy_measured':False}))


if __name__=='__main__':register(Path(sys.argv[1]))
