"""Check blind-review redaction, original comparison support and source preservation."""
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

from audit_labels import audit
from prepare_liss4_review import prepare

root = Path(__file__).resolve().parents[1]
research = root/'data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip'
reference = root/'data/reference/bhoonidhi_20261009/november_crop_v1/liss4_279_reference.zip'
cases = root/'data/labels/compartment_279_november_comparison_v2/satellite_interpretations.geojson'
before = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [research,reference,cases]}
original = json.loads(cases.read_bytes())
base = root/'data/phase2/blind_review_checks'
base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=base) as temporary, patch.object(socket,'socket',side_effect=AssertionError('Python networking disabled')):
    working = Path(temporary).resolve()
    assert working.is_relative_to(base.resolve())
    result = prepare(research,reference,cases,working/'blind',blind=True)
    page = (working/'blind/comparison.html').read_text(encoding='utf-8')
    document = json.loads((working/'blind/reviewer_cases.geojson').read_bytes())
    checked = audit(document)
    assert checked['class_counts']=={'forest':0,'non_forest':0,'unknown':7}
    assert checked['training_eligible'] is False and checked['split_counts']['unassigned']==7
    assert result['prior_interpretations_hidden'] is True and result['independent_test_set'] is False
    assert '2021 weak hint' not in page and page.count('data:image/png;base64,')==24
    for a,b in zip(original['features'],document['features']):
        assert a['geometry']==b['geometry']
        assert a['properties']['label_id']==b['properties']['label_id']
        assert a['properties']['uncertainty_notes'] not in page
        assert b['properties']['reviewer'] is None and b['properties']['reference_independent'] is False
        assert 'weak_class_name' not in b['properties'] and 'interpretation_subclass' not in b['properties']
    old = prepare(research,reference,cases,working/'original')
    assert old['prior_interpretations_hidden'] is False
    assert '2021 weak hint' in (working/'original/comparison.html').read_text(encoding='utf-8')
    assert not (working/'original/reviewer_cases.geojson').exists()
    written = (working/'blind/comparison.html').read_bytes()
    try:
        prepare(research,reference,cases,working/'blind',blind=True)
    except FileExistsError:
        assert (working/'blind/comparison.html').read_bytes()==written
    else:
        raise AssertionError('Existing review overwritten.')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in before.items())
summary = {'status':'PASS','offline_comparison':True,'seven_blank_unknown_records':True,
           'prior_hints_and_interpretations_hidden':True,'old_comparison_supported':True,
           'overwrite_rejected':True,'source_inputs_unchanged':True}
(base.parent/'blind_review_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
