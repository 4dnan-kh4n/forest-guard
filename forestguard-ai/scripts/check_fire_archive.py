"""Recalculate real archive counts and reject corrupt or missing inputs."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend import app as api
from backend.fire_monitor import parse
from import_fire_archive import register

report=api.fire_history()
folder=api.DATA_ROOT/'data/fire/archive_2022_2026_v1'
events,source=parse((folder/'source.csv').read_bytes(),'NOAA-20',report['boundary'])
assert source['regional_rows']==66 and len(events)==44
assert len({(e['latitude'],e['longitude'],e['observed_at']) for e in events})==44
for row in report['observations']:
    expected=[event for event in events if event['observed_at'].startswith(str(row['year']))]
    assert [row['inside_count'],row['nearby_count']]==[sum(event['scope']==scope for event in expected) for scope in ['inside','nearby']]
with tempfile.TemporaryDirectory(prefix='archive_check_',dir=ROOT/'data/fire') as temporary:
    root=Path(temporary)
    with patch.object(api,'DATA_ROOT',root):
        assert api.fire_history()=={'available':False}
        saved=root/'data/fire/archive_2022_2026_v1';saved.mkdir(parents=True)
        for name in ['report.json','source.csv','checksums.json']:(saved/name).write_bytes((folder/name).read_bytes())
        (saved/'source.csv').write_bytes(b'corrupt')
        try:api.fire_history()
        except HTTPException as error:assert error.status_code==503
        else:raise AssertionError('Corrupt historical source accepted')
    invalid=root/'invalid.zip';invalid.write_bytes(b'x'*(2*1024**2+1))
    try:register(invalid)
    except ValueError:pass
    else:raise AssertionError('Oversized archive accepted')
print('PASS: measured historical counts, duplicates, missing/corrupt sources and archive budget.')
