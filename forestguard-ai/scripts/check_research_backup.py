"""Exercise real-data backup/recovery offline without touching the live dashboard."""
import json
import shutil
import socket
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import backup_research as backup
import register_research_ui as registration


def rejected(action):
    try:
        action()
    except (ValueError, OSError, zipfile.BadZipFile):
        return
    raise AssertionError('Invalid recovery accepted')


root = backup.ROOT
(root/'data/phase5').mkdir(parents=True, exist_ok=True)
before = {name:backup.digest(root/name) for name in backup.ALLOWED}
with tempfile.TemporaryDirectory(prefix='recovery_check_', dir=root/'data/phase5') as temporary:
    folder = Path(temporary)
    archive = folder/'saved.zip'
    with patch.object(socket, 'socket', side_effect=AssertionError('Network forbidden')):
        result = backup.create(archive)
        checksum = result['sha256']
        destination = folder/'restored'
        restored = backup.restore(archive, checksum, destination)
        assert all(backup.digest(destination/name) == value for name,value in before.items())
        with patch.object(registration, 'BUNDLE', destination/registration.BUNDLE.relative_to(root)), \
             patch.object(registration, 'BOUNDARY', destination/registration.BOUNDARY.relative_to(root)):
            assert registration.verify_registration(destination/backup.REGISTERED)['status'] == 'PASS'
        # Recover with an empty application state; neither cached previews nor login sessions are required.
        sys.path.insert(0, str(root))
        import importlib
        api = importlib.import_module('backend.app')
        state = destination/'data/app'
        with patch.object(api, 'ROOT', destination), patch.object(api, 'STATE', state), \
             patch.object(api, 'RESEARCH_UI', destination/backup.REGISTERED):
            items = api.catalog()
            assert len(items) == 1 and items[0]['id'] == 'compartment-279'
            for observation in items[0]['views']:
                values, valid, profile = api.vegetation(items[0], observation)
                assert int(valid.sum()) == 12338
                for layer in ('imagery', 'coverage', 'ndvi'):
                    response = api.image('compartment-279', observation['id'], layer)
                    assert Path(response.path).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        rejected(lambda:backup.create(archive))
        rejected(lambda:backup.restore(archive, checksum, destination))
        rejected(lambda:backup.restore(archive, '0'*64, folder/'wrong_hash'))
        rejected(lambda:backup.restore(archive, checksum, root))
        bad = folder/'bad.zip'
        shutil.copyfile(archive, bad)
        with zipfile.ZipFile(bad, 'a') as saved:
            saved.writestr('../outside', b'unsafe')
        rejected(lambda:backup.restore(bad, backup.digest(bad), folder/'unsafe'))
        shutil.copyfile(archive, bad)
        with zipfile.ZipFile(bad) as saved:
            entries = {name:saved.read(name) for name in saved.namelist()}
        name = next(iter(backup.SOURCE_NAMES))
        entries[name] += b'corrupt'
        with zipfile.ZipFile(bad, 'w') as saved:
            for member, content in entries.items(): saved.writestr(member, content)
        rejected(lambda:backup.restore(bad, backup.digest(bad), folder/'corrupt'))
        del entries[name]
        with zipfile.ZipFile(bad, 'w') as saved:
            for member, content in entries.items(): saved.writestr(member, content)
        rejected(lambda:backup.restore(bad, backup.digest(bad), folder/'missing'))
        with patch.object(backup.shutil, 'copyfileobj', side_effect=OSError('Interrupted copy')):
            rejected(lambda:backup.restore(archive, checksum, folder/'interrupted'))
        assert not any((folder/name).exists() for name in ('unsafe','corrupt','missing','interrupted','wrong_hash'))
assert before == {name:backup.digest(root/name) for name in backup.ALLOWED}
summary = {'status':'PASS', 'backup_files':restored['files'], 'real_restored_registration_checked':True,
           'python_network_sockets_blocked':True, 'restored_map_layers':6, 'restored_common_valid_pixels':12338,
           'missing_corrupt_unsafe_wrong_hash_rejected':True, 'overwrite_and_interruption_checked':True,
           'live_sources_unchanged':True, 'os_network_disabled':False, 'forest_accuracy_measured':False}
(root/'data/phase5/research_backup_verification.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
