"""Check proposal-only review exports with explicitly hypothetical records, no label writes."""
import copy
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

from review_labels import TEMPLATE,PACK,ROOT,build,validate


def reject(document):
    try:validate(document)
    except ValueError:return
    raise AssertionError('Invalid review accepted')


original={name:hashlib.sha256((PACK/name).read_bytes()).hexdigest() for name in ['reviewer_cases.geojson','comparison.html']}
document=json.loads(TEMPLATE.read_bytes())
document['review_template_sha256']=original['reviewer_cases.geojson']
with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
    assert validate(document)['class_counts']['unknown']==7
    example=copy.deepcopy(document);p=example['features'][0]['properties']
    p.update(review_status='reviewed',reviewer='hypothetical test reviewer',review_date='2026-10-10',
             confidence='medium',uncertainty_notes='Hypothetical parser check only; not a real observation.')
    assert validate(example)['training_eligible'] is False
    p['class']='forest';reject(example)
    p.update(canopy_cover_percent=25.,qualifying_stand_area_ha=1.,height_evidence='Hypothetical test evidence',
             forest_use_evidence='Hypothetical test context',origin='natural_forest')
    checked=validate(example)
    assert checked['class_counts']['forest']==1 and not checked['source_truth_verified'] and not checked['training_eligible']
    for key,value in [('reference_independent',True),('split','test'),('reference_date','2026-10-10'),
                      ('reference_source','different source'),('canopy_cover_percent',10),('qualifying_stand_area_ha',.5),
                      ('height_evidence',''),('origin','agricultural_orchard_or_crop')]:
        bad=copy.deepcopy(example);bad['features'][0]['properties'][key]=value;reject(bad)
    bad=copy.deepcopy(document);bad['features'][0]['geometry']['coordinates'][0][0][0]+=.001;reject(bad)
    bad=copy.deepcopy(document);bad['features'].pop();reject(bad)
    bad=copy.deepcopy(document);bad['review_template_sha256']='0'*64;reject(bad)
    base=ROOT/'data/phase2';base.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='review_form_check_',dir=base) as temporary:
        folder=Path(temporary)/'form';assert build(folder)['classes_generated']==0
        page=(folder/'review.html').read_text(encoding='utf-8')
        assert page.count('data-case="')==7 and page.count('data:image/png;base64,')==24
        assert 'Download proposed labels' in page and '2021 weak hint' not in page and 'weak_class_name' not in page
        try:build(folder)
        except ValueError:pass
        else:raise AssertionError('Existing form overwritten')
assert original=={name:hashlib.sha256((PACK/name).read_bytes()).hexdigest() for name in original}
result={'status':'PASS','original_cases_preserved':7,'network_blocked':True,'hypothetical_parser_cases_only':True,
        'geometry_provenance_split_and_independence_changes_rejected':True,'unsupported_forest_proposals_rejected':True,
        'training_and_truth_approval_not_generated':True,'form_and_overwrite_checked':True}
(ROOT/'data/phase2/review_form_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
