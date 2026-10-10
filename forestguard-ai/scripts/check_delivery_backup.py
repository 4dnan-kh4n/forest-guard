"""Verify the delivery backup and restore without writing to the live application."""
import sys
import errno
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import backup_delivery as delivery
import backup_research as backup
import register_research_ui as registration


def reject(action):
    try:action()
    except (ValueError,OSError,zipfile.BadZipFile):return
    raise AssertionError('Invalid backup accepted')


archive=Path(sys.argv[1]) if len(sys.argv)>1 else delivery.ROOT/'data/backups/research_delivery_v2.zip'
receipt=json.loads(archive.with_suffix('.receipt.json').read_text())
checksum=receipt['sha256']
manifest=delivery.verify(archive,checksum)
destination=delivery.ROOT/'data/recovery'/('verified_'+archive.stem)
result=delivery.restore(archive,checksum,destination)
assert result['files']==len(manifest['files'])
assert any(n.endswith('model.zip') for n in manifest['files'])
assert any(n.startswith('data/labels/') for n in manifest['files'])
assert any(n.endswith('november_crop_v1/liss4_279_reference.zip') for n in manifest['files'])
assert any(n.startswith('frontend/dist/') for n in manifest['files'])
with patch.object(registration,'BUNDLE',destination/registration.BUNDLE.relative_to(delivery.ROOT)), \
     patch.object(registration,'BOUNDARY',destination/registration.BOUNDARY.relative_to(delivery.ROOT)):
    assert registration.verify_registration(destination/backup.REGISTERED)['status']=='PASS'
reject(lambda:delivery.restore(archive,checksum,destination))
with tempfile.TemporaryDirectory(prefix='delivery_faults_',dir=delivery.ROOT/'data/phase5') as temporary:
    folder=Path(temporary)
    with patch.object(backup.shutil,'disk_usage',return_value=shutil._ntuple_diskusage(100,100,0)):
        reject(lambda:delivery.restore(archive,checksum,folder/'no_space'))
    with patch.object(backup.shutil,'copyfileobj',side_effect=OSError(errno.ENOSPC,'Injected disk full')):
        reject(lambda:delivery.restore(archive,checksum,folder/'partial'))
    assert not (folder/'partial').exists()
    unsafe=folder/'unsafe.zip'
    with zipfile.ZipFile(unsafe,'w') as saved:
        saved.writestr('backup_manifest.json',json.dumps({'files':{'../outside':{}}}))
    reject(lambda:delivery.verify(unsafe,backup.digest(unsafe)))
    assert not delivery.allowed('.env') and not delivery.allowed('data/app/activity.sqlite')
    assert not delivery.allowed('docs/credentials-secret.json') and not delivery.allowed('/outside')
    assert not delivery.allowed('data/labels/../../outside')
summary={'status':'PASS','files_restored':result['files'],'archive_sha256':checksum,
         'real_reference_reviews_and_synthetic_models_preserved':True,'code_build_and_wheels_preserved':True,
         'real_registration_verified':True,'disk_full_partial_restore_overwrite_and_unsafe_paths_rejected':True,
         'credentials_and_sessions_excluded':True,'restore_folder':str(destination),'real_model_accuracy_measured':False}
(delivery.ROOT/'data/phase5/delivery_backup_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
