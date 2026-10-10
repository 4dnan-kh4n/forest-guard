"""Exercise disk-full handling and kill an owned disposable analysis subprocess."""
import errno
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import backend.app as api
from fastapi import HTTPException


with tempfile.TemporaryDirectory(prefix='phase9_failures_',dir=ROOT/'data/phase5') as temporary:
    state=Path(temporary)
    with patch.object(api,'STATE',state):
        original=api.run_change()
        disk_full=OSError(errno.ENOSPC,'Injected disk full')
        with patch.object(api.shutil,'copyfile',side_effect=disk_full),patch.object(api,'history',side_effect=disk_full):
            try:api.run_change()
            except HTTPException as error:assert error.status_code==507
            else:raise AssertionError('Disk full was not rejected')
        assert api.change_status()['latest']['run_id']==original['run_id']
        with patch.object(Path,'mkdir',side_effect=disk_full),patch.object(api,'history',side_effect=disk_full):
            try:api.run_change()
            except HTTPException as error:assert error.status_code==507
            else:raise AssertionError('Disk full during run-directory creation was not rejected')
        with patch.object(api,'history',side_effect=disk_full):
            assert api.run_change()['synthetic_fixture'] is True
        from fastapi.responses import FileResponse
        complete=api.change_run(original['run_id'])
        with patch.object(Path,'replace',side_effect=disk_full):
            try:api.change_image(original['run_id'],'loss')
            except HTTPException as error:assert error.status_code==507
            else:raise AssertionError('Preview disk-full failure accepted')
        assert not (complete/'loss.png').exists()
        with patch.object(Path,'replace',side_effect=KeyboardInterrupt()):
            try:api.change_image(original['run_id'],'gain')
            except KeyboardInterrupt:pass
            else:raise AssertionError('Preview interruption did not occur')
        assert not (complete/'gain.png').exists()
        response=api.change_image(original['run_id'],'gain')
        assert isinstance(response,FileResponse) and Path(response.path).read_bytes().startswith(b'\x89PNG')
    worker="""import json,sys,time
from pathlib import Path
import backend.app as api
api.STATE=Path(sys.argv[1])
compare=api.compare_change
def paused(*args):
    compare(*args)
    (api.STATE/'ready.json').write_text('{}')
    time.sleep(120)
api.compare_change=paused
api.run_change()
"""
    process=subprocess.Popen([sys.executable,'-c',worker,str(state)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        deadline=time.monotonic()+30
        while not (state/'ready.json').exists():
            if process.poll() is not None:raise AssertionError(process.communicate())
            if time.monotonic()>deadline:raise AssertionError('Analysis subprocess did not reach interruption point')
            time.sleep(.1)
        process.kill()  # Only the disposable subprocess created above; never the user's server.
        process.wait(timeout=10)
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=10)
        process.stdout.close();process.stderr.close()
    probe="import json,sys; from pathlib import Path; import backend.app as api; api.STATE=Path(sys.argv[1]); print(json.dumps(api.change_status()))"
    restarted=subprocess.run([sys.executable,'-c',probe,str(state)],cwd=ROOT,check=True,capture_output=True,text=True,timeout=30)
    recovered=json.loads(restarted.stdout)
    assert recovered['latest'] is not None
    incomplete=[p for p in (state/'change_runs').iterdir() if not (p/'dashboard_complete.json').exists()]
    assert len(incomplete)==2 and any((p/'result/change.tif').exists() for p in incomplete)
result={'status':'PASS','enospc_http_507_checked':True,'failed_history_does_not_mask_disk_full':True,
        'disk_full_during_directory_creation_checked':True,'interrupted_and_disk_full_previews_not_published':True,
        'completed_result_survives_activity_disk_full':True,'owned_analysis_subprocess_killed':True,
        'restart_excludes_killed_run':True,'synthetic_fixture':True,'power_loss_tested':False}
(ROOT/'data/phase5/phase9_failure_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
