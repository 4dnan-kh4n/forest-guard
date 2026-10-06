"""Check label rejection rules with synthetic fixtures, and a real stored pair."""
import argparse
import copy
import json
import socket
from pathlib import Path
from unittest.mock import patch
from audit_labels import audit
from verify_pair import verify_pair

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('pair',type=Path)
args=parser.parse_args()
assert audit({'type':'FeatureCollection','features':[]})['training_eligible'] is False
def fixture(label_id,split,when,longitude):
    return {'type':'Feature','geometry':{'type':'Point','coordinates':[longitude,22.42]},
        'properties':{'label_id':label_id,'class':'forest','observation_date':when,
        'reference_source':'SYNTHETIC CHECKER FIXTURE: not a field observation',
        'reference_access_license':'synthetic test only','reference_date':when,
        'reviewer':'synthetic checker','review_date':'2026-10-06','confidence':'high',
        'uncertainty_notes':'Synthetic fixture, excluded from all project labels',
        'study_area_version':'synthetic test','split':split,'reference_kind':'field_observation',
        'review_status':'reviewed','reference_independent':True}}
weak=fixture('synthetic-weak','test','2025-03-28',76.8)
weak['properties']['reference_kind']='weak_map'
near=[fixture('synthetic-train','train','2024-03-21',76.8),fixture('synthetic-test','test','2025-03-28',76.8001)]
stale=fixture('synthetic-stale','test','2025-03-28',76.8)
stale['properties']['reference_date']='2021-03-28'
duplicate=copy.deepcopy(near[0])
for features,expected in [([weak],'Independent'),(near,'Spatial leakage'),([stale],'31-day'),([near[0],duplicate],'unique')]:
    try: audit({'type':'FeatureCollection','features':features})
    except ValueError as error: assert expected in str(error),str(error)
    else: raise AssertionError(f'Invalid label fixture accepted: {expected}')
with patch.object(socket,'socket',side_effect=AssertionError('Python networking disabled')):
    real=verify_pair(args.pair)
assert real['integrity']=='PASS' and real['training_eligible'] is False
assert real['reviewed_label_count']==0 and real['forest_loss_ha'] is None
summary={'status':'PASS','real_pair_version':real['dataset_version'],
    'real_pair_network_disabled_check':True,'weak_test_labels_rejected':True,
    'nearby_split_labels_rejected':True,'stale_reference_rejected':True,
    'duplicate_ids_rejected':True,'fixtures_not_saved_as_project_labels':True}
output=Path(__file__).resolve().parents[1]/'data/phase2/verification.json'
output.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
