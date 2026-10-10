"""Check interrupted publication, corruption and fresh-process recovery in isolated state."""
import hashlib
import json
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import backend.app as backend
from fastapi import HTTPException


def interrupted(action):
    try:action()
    except KeyboardInterrupt:return
    raise AssertionError('Interruption did not occur')


def inaccessible(identity,code):
    try:backend.change_run(identity)
    except HTTPException as error:assert error.status_code==code
    else:raise AssertionError('Incomplete/corrupt comparison accepted')


def restart(state):
    source="""import json,sys,socket; from pathlib import Path
from unittest.mock import patch
import backend.app as api
api.STATE=Path(sys.argv[1])
with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
    print(json.dumps(api.change_status()))
"""
    process=subprocess.run([sys.executable,'-c',source,str(state)],cwd=ROOT,check=True,capture_output=True,text=True,timeout=30)
    return json.loads(process.stdout)


original={name:hashlib.sha256((backend.CHANGE_FIXTURE/name).read_bytes()).hexdigest() for name in backend.CHANGE_INPUTS}
base=ROOT/'data/phase5';base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='change_recovery_',dir=base) as temporary:
    state=Path(temporary)
    with patch.object(backend,'STATE',state),patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        first=backend.run_change();identity=first['run_id']
        complete=backend.change_run(identity)
        checksum=hashlib.sha256((complete/'result/change.tif').read_bytes()).hexdigest()
        copy=backend.shutil.copyfile
        calls=0

        def partial_copy(source,target):
            global calls
            calls+=1
            if calls==2:raise KeyboardInterrupt()
            return copy(source,target)

        with patch.object(backend.shutil,'copyfile',side_effect=partial_copy):
            interrupted(backend.run_change)
        compare=backend.compare_change

        def after_result(*args):
            compare(*args)
            raise KeyboardInterrupt()

        with patch.object(backend,'compare_change',side_effect=after_result):
            interrupted(backend.run_change)
        rename=Path.rename

        def before_commit(path,target):
            if path.name=='dashboard_complete.tmp':raise KeyboardInterrupt()
            return rename(path,target)

        with patch.object(Path,'rename',before_commit):interrupted(backend.run_change)
        incomplete=[p for p in (state/'change_runs').iterdir() if p!=complete]
        assert len(incomplete)==3
        for folder in incomplete:inaccessible(folder.name,404)
        assert backend.change_status()['latest']['run_id']==identity
        # A disconnect after publication must retain the completed result even if activity logging was interrupted.
        with patch.object(backend,'history',side_effect=KeyboardInterrupt()):interrupted(backend.run_change)
        newer=backend.change_status()['latest']['run_id']
        assert newer!=identity
        newer_folder=backend.change_run(newer)
        saved=(newer_folder/'result/change_report.json').read_bytes()
        (newer_folder/'result/change_report.json').write_bytes(saved+b'corrupt')
        inaccessible(newer,409)
        assert backend.change_status()['latest']['run_id']==identity
        (newer_folder/'result/change_report.json').write_bytes(saved)
        missing=newer_folder/'result/transitions.csv';content=missing.read_bytes();missing.unlink()
        inaccessible(newer,409)
        missing.write_bytes(content)
        marker=newer_folder/'dashboard_complete.json';saved_marker=marker.read_bytes()
        for invalid in (b'{',b'[]',b'{"status":"complete","synthetic_fixture":true}'):
            marker.write_bytes(invalid);inaccessible(newer,409)
            assert backend.change_status()['latest']['run_id']==identity
        marker.write_bytes(saved_marker)
        # Preview cache writes must not change which completed analysis is the latest.
        (complete/'before.png').write_bytes(b'cache placeholder')
        assert backend.change_status()['latest']['run_id']==newer
        assert hashlib.sha256((complete/'result/change.tif').read_bytes()).hexdigest()==checksum
    recovered=restart(state)
    assert recovered['latest']['run_id']==newer and recovered['latest']['common_observable_pixels']==64
    assert recovered['latest']['synthetic_fixture'] is True
assert original=={name:hashlib.sha256((backend.CHANGE_FIXTURE/name).read_bytes()).hexdigest() for name in backend.CHANGE_INPUTS}
result={'status':'PASS','synthetic_fixture':True,'interruptions_checked':4,
        'partial_input_result_and_marker_not_published':True,'completed_result_survives_logging_interruption':True,
        'corrupt_missing_malformed_legacy_results_rejected':True,'latest_uses_completion_time_not_cache_time':True,
        'fresh_process_recovery_checked':True,'original_inputs_unchanged':True,'real_change_accuracy_measured':False}
(base/'change_recovery_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
