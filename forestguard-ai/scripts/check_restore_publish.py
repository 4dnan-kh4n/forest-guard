"""Small synthetic fixture for Windows recovery fallback and cleanup."""
import errno
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch
import backup_research as backup

with tempfile.TemporaryDirectory(prefix='publish_check_',dir=backup.ROOT/'data/recovery') as temporary:
    folder=Path(temporary);archive=folder/'fixture.zip';raw=b'Synthetic recovery test only'
    manifest={'format':'forestguard-279-imagery-backup-v1','scope':'Synthetic test fixture',
      'files':{'sample.txt':{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}}}
    with zipfile.ZipFile(archive,'w') as saved:
        saved.writestr('sample.txt',raw);saved.writestr('backup_manifest.json',json.dumps(manifest))
    with patch.object(Path,'rename',side_effect=PermissionError('Injected Windows lock')),patch.object(backup.time,'sleep'):
        target=folder/'success'
        result=backup.restore(archive,backup.digest(archive),target,files={'sample.txt'})
        assert result['status']=='PASS' and (target/'sample.txt').read_bytes()==raw
        failed=folder/'failed'
        with patch.object(backup.shutil,'copytree',side_effect=OSError(errno.ENOSPC,'Injected copy failure')):
            try:backup.restore(archive,backup.digest(archive),failed,files={'sample.txt'})
            except OSError:pass
            else:raise AssertionError('Copy failure accepted')
        assert not failed.exists()
print('PASS: blocked rename fallback preserves bytes; failed copy removes only its new recovery directory.')
