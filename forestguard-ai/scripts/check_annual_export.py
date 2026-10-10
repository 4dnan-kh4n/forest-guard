"""Offline export checks using explicitly synthetic temporary rasters, no training."""
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import rasterio
from rasterio.transform import from_origin
import struct
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cloud.annual_observations import annual_run
from import_annual_observations import verify,MODEL_SHA
import cloud.multiseason_research as research

assert research.MIN_FEATURE_COVERAGE==.9
study=json.loads((ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes())
raw=(ROOT/'data/phase3/weak_december_run_v1/forestguard_weak_proxy_run1.zip').read_bytes()
with zipfile.ZipFile(__import__('io').BytesIO(raw)) as modelzip:manifest=json.loads(modelzip.read('model_manifest.json'))
with tempfile.TemporaryDirectory(dir=ROOT/'data/annual',prefix='synthetic_export_check_') as temporary:
    folder=Path(temporary)/'research'/'run';folder.mkdir(parents=True)
    (folder/'boundary.geojson').write_text(json.dumps(study))
    year=folder/'2025';year.mkdir()
    profile=dict(driver='GTiff',crs='EPSG:32643',transform=from_origin(684080,2479720,20,20),height=3,width=3)
    mask=np.ones((3,3),dtype='uint8');mask[0,0]=0
    for name,array in [('features',np.full((15,3,3),.3,dtype='float32')),('usable_mask',mask[None]),('study_mask',np.ones((1,3,3),dtype='uint8'))]:
        with rasterio.open(year/f'{name}.tif','w',**profile,count=array.shape[0],dtype=array.dtype) as dst:
            dst.write(array)
            if name=='features':dst.descriptions=tuple(manifest['feature_order'])
    record={'season':'2025','scene_id':'SYNTHETIC_TEST_ONLY','acquisition':'2025-10-01T00:00:00Z','inside_study_pixels':9,'usable_fraction_inside_study':8/9,'feature_order':manifest['feature_order'],'attribution':'Synthetic parser fixture','source_license_url':'test-only'}
    (year/'report.json').write_text(json.dumps(record));(year/'source.json').write_text('{}')
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    (year/'preview.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',3,3,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+b'\0'*12+b'\0'+b'\0'*12+b'\0'+b'\0'*12))+chunk(b'IEND',b''))
    (folder/'research_report.json').write_text(json.dumps({'acquisitions':[record]}))
    def output(*args):return folder
    with patch('builtins.print'):
        archive=annual_run(study,None,None,raw,MODEL_SHA,output)
    assert archive.parent==Path(temporary) and archive.exists()
    report,hashes=verify(archive)
    assert report['observations'][0]['usable_pixels']==8 and report['observations'][0]['coverage_fraction']==8/9
    assert report['observations'][0]['canopy_density_percent'] is None
    with zipfile.ZipFile(archive) as good:
        bad=Path(temporary)/'corrupt.zip'
        with zipfile.ZipFile(bad,'w') as saved:
            for name in good.namelist():saved.writestr(name,b'corrupt' if name=='2025/preview.png' else good.read(name))
    try:verify(bad)
    except ValueError:pass
    else:raise AssertionError('Corrupt annual image accepted')
print('PASS: annual batching, invalid mask pixels, coverage, ZIP checksums, root download and corrupt-image rejection. Synthetic fixtures only.')
