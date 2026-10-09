"""Verify real registry reproducibility and reject unsafe label preparation."""
import copy
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

from prepare_study_dataset import prepare

root = Path(__file__).resolve().parents[1]
bundle = root/'data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip'
boundary = root/'data/study/compartment_279_v1/boundary.geojson'
labels = root/'data/labels/compartment_279_november_comparison_v2/satellite_interpretations.geojson'
before = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [bundle,boundary,labels]}
document = json.loads(labels.read_bytes())
base = root/'data/phase2/study_checks'
base.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(dir=base) as temporary, patch.object(socket,'socket',side_effect=AssertionError('Python networking disabled')):
    working = Path(temporary).resolve()
    assert working.is_relative_to(base.resolve())
    first = prepare(bundle,boundary,labels,working/'first')
    second = prepare(bundle,boundary,labels,working/'second')
    assert first == second
    assert first == json.loads((root/'data/phase2/compartment_279_dataset_v1/dataset_registry.json').read_bytes())
    assert json.loads((working/'first/dataset_registry.json').read_bytes()) == first
    assert (working/'first/labels.geojson').read_bytes() == labels.read_bytes()
    assert first['training_eligible'] is False and first['evaluation_splits_frozen'] is False
    assert first['training_samples_extracted'] == 0
    assert first['label_audit']['class_counts'] == {'forest':0,'non_forest':3,'unknown':4}
    assert len(first['label_pixel_support']) == 7
    assert all(p['footprint_pixels']==p['common_usable_pixels']>0 for p in first['label_pixel_support'])
    written = (working/'first/dataset_registry.json').read_bytes()
    try:
        prepare(bundle,boundary,labels,working/'first')
    except ValueError:
        assert (working/'first/dataset_registry.json').read_bytes() == written
    else:
        raise AssertionError('Registry overwritten.')
    changes = [('wrong_version',{'study_area_version':'wrong'},'study version/date'),
               ('unmatched_date',{'observation_date':'2025-11-09'},'study version/date'),
               ('premature_split',{'split':'train'},'Uncertain/unreviewed'),
               ('non_independent_split',{'class':'non_forest','confidence':'high','split':'train'},'Independent reviewed')]
    for name,properties,message in changes:
        altered = copy.deepcopy(document)
        altered['features'][0]['properties'].update(properties)
        path = working/(name+'.geojson')
        path.write_text(json.dumps(altered))
        try:
            prepare(bundle,boundary,path,working/name)
        except ValueError as error:
            assert message in str(error),str(error)
            assert not (working/name).exists()
        else:
            raise AssertionError('Unsafe label input accepted: '+name)
    altered = copy.deepcopy(document)
    altered['features'][0]['geometry']={'type':'Point','coordinates':[76.9,22.5]}
    path = working/'outside.geojson'
    path.write_text(json.dumps(altered))
    try:
        prepare(bundle,boundary,path,working/'outside')
    except ValueError as error:
        assert 'outside the crop' in str(error)
        assert not (working/'outside').exists()
    else:
        raise AssertionError('Outside footprint accepted.')
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in before.items())
summary = {'status':'PASS','dataset_version':first['dataset_version'],'offline_real_data':True,
           'reproducible_registry':True,'unmodified_label_snapshot':True,
           'wrong_version_date_and_outside_footprint_rejected':True,
           'premature_split_rejected':True,'overwrite_rejected':True,'source_inputs_unchanged':True}
(base.parent/'study_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
