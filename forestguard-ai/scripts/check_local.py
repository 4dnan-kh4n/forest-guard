"""Real-data offline check plus corruption/overwrite safeguards; stdlib runner."""
import hashlib
import json
import shutil
import socket
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from inspect_local import inspect, export

root = Path(__file__).resolve().parents[1]
sample = root/'data/phase0/boundary_check_version6'
source_before = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sample.iterdir() if p.is_file()}
started = time.perf_counter()
with patch.object(socket,'socket',side_effect=AssertionError('Python networking is disabled')):
    result = inspect(sample)
elapsed = time.perf_counter()-started
expected = json.loads((sample/'boundary_review.json').read_text())
candidate = result['coverage'][1]
assert candidate['total_pixels'] == expected['candidate_pixels'] == 58971
assert candidate['usable_pixels'] == expected['candidate_usable_pixels'] == 58439
assert result['prediction_used'] is False and result['forest_area_ha'] is None
with patch.object(socket,'socket',side_effect=AssertionError('Python networking is disabled')):
    legacy = inspect(root/'data/phase0/version3')
legacy_report = json.loads((root/'data/phase0/version3/report.json').read_text())
assert len(legacy['coverage']) == 1
assert legacy['coverage'][0]['usable_pixels'] == legacy_report['usable_pixels']
assert legacy['scope_status'] == 'exported research crop; no area label recorded'

base = root/'data/phase1/checks'
base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=base) as temporary:
    working = Path(temporary).resolve()
    assert working.is_relative_to(base.resolve())
    output = working/'reports'
    export(result,output)
    before = (output/'coverage.json').read_bytes()
    try:
        export(result,output)
    except ValueError:
        assert (output/'coverage.json').read_bytes() == before
    else:
        raise AssertionError('Existing report was overwritten.')
    damaged = working/'damaged_sample'
    shutil.copytree(sample,damaged)
    path = damaged/'usable.tif'
    content = bytearray(path.read_bytes()); content[-1] ^= 1
    path.write_bytes(content)
    try:
        inspect(damaged)
    except ValueError as error:
        assert 'integrity failure' in str(error),str(error)
    else:
        raise AssertionError('Corrupted extracted raster was accepted.')
    try:
        inspect(working/'missing_sample')
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('Missing sample was accepted.')
assert source_before == {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sample.iterdir() if p.is_file()}
summary = {'status':'PASS','real_data_counts_match_cloud':True,
           'older_crop_without_candidate_or_area_label_supported':True,
           'python_networking_disabled':True,'corruption_rejected':True,
           'missing_input_rejected':True,'report_overwrite_rejected':True,
           'source_files_unchanged':True,'inspection_seconds':round(elapsed,4),
           'runtime':result['runtime'],'test_data':'real stored crop; temporary corrupted copies only'}
(base.parent/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
