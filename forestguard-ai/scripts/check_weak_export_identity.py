"""Check dataset binding with real saved artifacts; never fit or unpickle a model."""
import json
import socket
from unittest.mock import patch
from pathlib import Path

from verify_weak_export import verify

ROOT=Path(__file__).resolve().parents[1]
export=ROOT/'data/phase3/weak_proxy_run_v1/forestguard_weak_proxy_run1.zip'
export_sha='eca2839185a91e729bbf9ab4c52813f2137a6e056b13c432b97bbe9a8ae7061c'
original=ROOT/'data/phase2/weak_proxy_experiment_v1/weak_experiment.zip'
original_sha='15d7c83557657a116f10080953405f521f100e64b389ef8b0dcaea3632945279'
december=ROOT/'data/phase2/weak_december_experiment_v1/weak_experiment.zip'
december_sha='b4d93e7db778b51addcea7e9c574e1f593b56c48786778a1629cf3921cf7f8ec'
with patch.object(socket,'socket',side_effect=AssertionError('Networking forbidden')):
    assert verify(export,export_sha)['expected_dataset_verified'] is False
    assert verify(export,export_sha,original,original_sha)['expected_dataset_verified'] is True
    for dataset,digest,reason in [(december,december_sha,'different dataset'),
                                  (original,'0'*64,'checksum'),(original,None,'both expected')]:
        try:verify(export,export_sha,dataset,digest)
        except ValueError as error:assert reason in str(error)
        else:raise AssertionError('Wrong experiment, hash or incomplete binding accepted.')
summary={'status':'PASS','original_export_accepted_with_original_dataset':True,
         'earlier_export_rejected_for_december_dataset':True,'invalid_dataset_checksum_rejected':True,
         'network_blocked':True,'model_unpickled':False,'december_training_completed':False}
(ROOT/'data/phase3/weak_december_run_v1/export_identity_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
