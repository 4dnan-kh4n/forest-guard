"""Real-data offline, wrong-boundary, corruption and overwrite checks."""
import csv
import hashlib
import json
import socket
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from inspect_research import inspect, export

root = Path(__file__).resolve().parents[1]
bundle = root/'data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip'
boundary = root/'data/study/compartment_279_v1/boundary.geojson'
before = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [bundle,boundary]}
base = root/'data/phase1/research_checks'
base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=base) as temporary, patch.object(socket,'socket',side_effect=AssertionError('Python networking disabled')):
    working = Path(temporary).resolve()
    assert working.is_relative_to(base.resolve())
    result = inspect(bundle,boundary)
    assert result['forest_area_ha'] is None and result['prediction_used'] is False
    assert [r['usable_pixels'] for r in result['coverage']] == [12381,12362,12338]
    assert all(r['total_pixels'] == 13099 for r in result['coverage'])
    assert abs(result['coverage'][-1]['usable_fraction']-12338/13099) < 1e-12
    output = working/'report'
    export(result,output)
    assert json.loads((output/'coverage.json').read_text()) == result
    with (output/'coverage.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 3 and int(rows[-1]['usable_pixels']) == 12338
    written = {p:p.read_bytes() for p in output.iterdir()}
    try:
        export(result,output)
    except ValueError:
        assert all(p.read_bytes() == content for p,content in written.items())
    else:
        raise AssertionError('Existing report overwritten.')
    wrong = json.loads(boundary.read_text())
    wrong['features'][0]['geometry']['coordinates'][0][0][1][0] += .0001
    wrong_path = working/'wrong.geojson'
    wrong_path.write_text(json.dumps(wrong))
    try:
        inspect(bundle,wrong_path)
    except ValueError as error:
        assert 'geometry differs' in str(error)
    else:
        raise AssertionError('Wrong study boundary accepted.')
    damaged = working/'damaged.zip'
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(damaged,'w',zipfile.ZIP_DEFLATED) as target:
        for name in source.namelist():
            content = source.read(name)
            if name == 'dry/reflectance.tif':
                content = content[:-1] + bytes([content[-1]^1])
            target.writestr(name,content)
    try:
        inspect(damaged,boundary)
    except ValueError as error:
        assert 'Integrity failure' in str(error)
    else:
        raise AssertionError('Changed raster accepted.')
    try:
        inspect(working/'missing.zip',boundary)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError('Missing bundle accepted.')
assert all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p,digest in before.items())
summary = {'status':'PASS','offline_real_data':True,'counts_match_cloud':True,
           'wrong_boundary_rejected':True,'corruption_rejected':True,
           'missing_input_rejected':True,'overwrite_rejected':True,
           'json_csv_roundtrip':True,'source_inputs_unchanged':True,'runtime':result['runtime']}
(base.parent/'research_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
