"""Audit actual pending research cases and verify that none can silently enter training."""
import copy
import json
from pathlib import Path
from audit_labels import audit

root=Path(__file__).resolve().parents[1]
document=json.loads((root/'data/labels/compartment_279_v2_review_pack/review_cases.geojson').read_text(encoding='utf-8'))
result=audit(document)
assert result['label_count']==7 and result['class_counts']=={'forest':0,'non_forest':0,'unknown':7}
assert result['training_eligible'] is False and result['split_checks_complete'] is False
assert sum(result['declared_independent_reviewed_counts'].values())==0
for change in [{'split':'train'},{'class':'forest'},{'review_status':'reviewed'},{'uncertainty_notes':None}]:
    altered=copy.deepcopy(document)
    altered['features'][0]['properties'].update(change)
    try:audit(altered)
    except ValueError:pass
    else:raise AssertionError('Invalid transition accepted: '+str(change))
print('PASS: actual pending records accepted, annual dates remain imprecise, and premature training/review transitions rejected.')
