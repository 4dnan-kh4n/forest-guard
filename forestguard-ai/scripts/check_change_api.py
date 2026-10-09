"""Exercise the running authenticated change dashboard API without new packages."""
import csv
import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import rasterio
from rasterio.io import MemoryFile

from check_ui import request

root=Path(__file__).resolve().parents[1]
request('/api/change',expected=401)
request('/api/change/run',b'',401)
request('/api/login',json.dumps({'district':'Harda','beat':'Joga','password':'joga@123'}).encode())
status=json.loads(request('/api/change'))
assert status['available'] and status['real_analysis_ready'] is False
report=json.loads(request('/api/change/run',b''))
assert report['synthetic_fixture'] is True and report['width']==4 and report['height']==32
assert report['common_observable_pixels']==64 and report['transition_area_ha']['suspected_loss']==.64
run=report['run_id'];prefix='/api/change/runs/'+run
for layer,valid in [('before',96),('after',64),('change',64),('loss',16),('gain',16),('coverage',64)]:
    raw=request(prefix+'/image/'+layer)
    assert raw.startswith(b'\x89PNG\r\n\x1a\n')
    with MemoryFile(raw) as memory, memory.open() as raster:
        assert raster.count==4 and raster.shape==(32,4)
        assert int((raster.read(4)==255).sum())==valid
rows=list(csv.DictReader(io.StringIO(request(prefix+'/report/csv').decode())))
assert len(rows)==4 and all(row['synthetic_fixture']=='True' for row in rows)
assert json.loads(request(prefix+'/report/json'))['input_sha256']==report['input_sha256']
assert b'not findings about Joga' in request(prefix+'/report/html')
with MemoryFile(request(prefix+'/report/geotiff')) as memory, memory.open() as raster:
    assert raster.tags()['synthetic_fixture']=='true' and raster.nodata==255
assert json.loads(request('/api/change'))['latest']['run_id']==run
for path in [prefix+'/image/invalid',prefix+'/report/invalid','/api/change/runs/change-000000000000/image/change','/api/change/runs/invalid/report/json']:
    request(path,expected=404)
request('/api/logout',b'')
request(prefix+'/report/json',expected=401)
request(prefix+'/image/change',expected=401)

# Direct failure checks use a separate temporary state and never modify saved inputs.
sys.path.insert(0,str(root))
import backend.app as backend
from fastapi import HTTPException
with tempfile.TemporaryDirectory(prefix='change_api_check_',dir=root/'data/phase4') as temporary:
    folder=Path(temporary);fixture=folder/'fixture';fixture.mkdir()
    with patch.object(backend,'STATE',folder),patch.object(backend,'CHANGE_FIXTURE',fixture):
        with backend.database() as db:db.execute('CREATE TABLE sessions (token TEXT PRIMARY KEY, expires REAL)')
        assert backend.activity()==[]  # Fresh login creates sessions before any activity is recorded.
        try:backend.run_change()
        except HTTPException as error:assert error.status_code==409
        else:raise AssertionError('Missing fixture accepted')
        for name in backend.CHANGE_INPUTS:(fixture/name).write_bytes(b'corrupt')
        try:backend.run_change()
        except HTTPException as error:assert error.status_code==400
        else:raise AssertionError('Corrupt inputs accepted')
        assert backend.change_status()['latest'] is None
        assert not list(folder.rglob('dashboard_complete.json'))
summary={'status':'PASS','synthetic_fixture':True,'real_change_accuracy_measured':False,
         'authenticated_run_and_persistence_checked':True,'map_layers_checked':6,'download_formats_checked':4,
         'unauthenticated_access_and_invalid_routes_rejected':True,'missing_corrupt_inputs_rejected':True,
         'failed_runs_not_published':True,'fresh_login_activity_checked':True}
(root/'data/phase4/dashboard_api_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
