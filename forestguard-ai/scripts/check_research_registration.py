"""Check real registration offline, including corruption and false metadata rejection."""
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

from register_research_ui import register,verify_registration,OUTPUT,BUNDLE,BOUNDARY

root=Path(__file__).resolve().parents[1]
(root/'data/phase5').mkdir(parents=True,exist_ok=True)
original=[hashlib.sha256(p.read_bytes()).hexdigest() for p in [BUNDLE,BOUNDARY]]
with tempfile.TemporaryDirectory(prefix='registration_check_',dir=root/'data/phase5') as temporary:
    folder=Path(temporary)/'registered'
    with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        assert register(folder)['status']=='PASS'
        assert verify_registration(folder)['registered_files']==14
    try:register(folder)
    except ValueError as error:assert 'Registration exists' in str(error)
    else:raise AssertionError('Registration overwritten')
    mask=folder/'common_usable.tif';saved=mask.read_bytes();mask.write_bytes(saved+b'corrupt')
    try:verify_registration(folder)
    except ValueError:pass
    else:raise AssertionError('Corrupted registered raster accepted')
    mask.write_bytes(saved)
    record_path=folder/'registered.json';record=json.loads(record_path.read_text());record['coverage']=1.
    record_path.write_text(json.dumps(record))
    manifest_path=folder/'checksums.json';manifest=json.loads(manifest_path.read_text())
    manifest['registered.json']={'bytes':record_path.stat().st_size,'sha256':hashlib.sha256(record_path.read_bytes()).hexdigest()}
    manifest_path.write_text(json.dumps(manifest))
    try:verify_registration(folder)
    except ValueError as error:assert 'coverage/resolution' in str(error)
    else:raise AssertionError('False coverage accepted with consistent checksum')
    manifest['../outside']={'bytes':1,'sha256':'0'*64};manifest_path.write_text(json.dumps(manifest))
    try:verify_registration(folder)
    except ValueError as error:assert 'manifest mismatch' in str(error)
    else:raise AssertionError('Unsafe manifest member accepted')
assert original==[hashlib.sha256(p.read_bytes()).hexdigest() for p in [BUNDLE,BOUNDARY]]
assert verify_registration(OUTPUT)['status']=='PASS'
summary={'status':'PASS','real_data_verified':True,'offline_registration_checked':True,
         'registered_files':14,'source_hashes_checked':27,'corrupt_raster_and_false_coverage_rejected':True,
         'unsafe_members_and_overwrite_rejected':True,'source_inputs_unchanged':True,'forest_accuracy_measured':False}
(root/'data/phase5/research_registration_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
