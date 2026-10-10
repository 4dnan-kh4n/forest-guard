"""Back up and recover the saved compartment 279 dashboard imagery without overwrites."""
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

from register_research_ui import ROOT, BUNDLE, BOUNDARY, OUTPUT, verify_registration

LIMIT = 64 * 1024**2
SOURCE_NAMES = {p.relative_to(ROOT).as_posix() for p in (BUNDLE, BOUNDARY)}
REGISTERED = OUTPUT.relative_to(ROOT).as_posix()
ALLOWED = SOURCE_NAMES | {REGISTERED+'/'+name for name in
    ['registered.json', 'checksums.json', 'boundary.geojson', 'research_report.json', 'common_usable.tif']}
for season in ('dry', 'post_monsoon'):
    ALLOWED.update(REGISTERED+'/'+season+'/'+name for name in
        ['reflectance.tif', 'preview.png', 'usable_mask.tif', 'study_mask.tif', 'source.json'])


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(archive, trusted_sha256, files=ALLOWED, backup_format='forestguard-279-imagery-backup-v1', limit=LIMIT):
    archive = Path(archive)
    if archive.stat().st_size > limit or digest(archive) != trusted_sha256:
        raise ValueError('Backup size/checksum differs from the separately retained SHA-256.')
    with zipfile.ZipFile(archive) as saved:
        items = saved.infolist()
        if (len(items) != len(files)+1 or {i.filename for i in items} != files|{'backup_manifest.json'}
                or sum(i.file_size for i in items) > limit
                or saved.getinfo('backup_manifest.json').file_size > 512*1024):
            raise ValueError('Unexpected backup members or expanded size.')
        manifest = json.loads(saved.read('backup_manifest.json'))
        if not isinstance(manifest,dict) or manifest.get('format') != backup_format or not isinstance(manifest.get('files'),dict) or set(manifest['files']) != files:
            raise ValueError('Unexpected backup manifest.')
        for name, record in manifest['files'].items():
            if not isinstance(record,dict) or not isinstance(record.get('bytes'),int) or not isinstance(record.get('sha256'),str):
                raise ValueError('Invalid file record: '+name)
            with saved.open(name) as stream:
                checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
            if saved.getinfo(name).file_size != record['bytes'] or checksum != record['sha256']:
                raise ValueError('Backup file integrity failure: '+name)
    return manifest


def create(archive, files=ALLOWED, scope='Selected compartment 279 imagery only; no labels, models, application code or sessions.', backup_format='forestguard-279-imagery-backup-v1', limit=LIMIT):
    archive = Path(archive)
    if archive.exists():
        raise ValueError('Backup already exists; preserve it.')
    verify_registration(OUTPUT)
    paths = {name: ROOT/name for name in sorted(files)}
    total = sum(p.stat().st_size for p in paths.values())
    if total > limit:
        raise ValueError('Backup exceeds the bounded size limit.')
    archive.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(archive.parent).free < total*2+limit:
        raise ValueError('Insufficient free space for a verified backup.')
    manifest = {'format':backup_format,
                'scope':scope,
                'files':{name:{'bytes':p.stat().st_size, 'sha256':digest(p)} for name,p in paths.items()}}
    with tempfile.TemporaryDirectory(prefix='backup_', dir=archive.parent) as temporary:
        candidate = Path(temporary)/'research.zip'
        with zipfile.ZipFile(candidate, 'w', compression=zipfile.ZIP_DEFLATED) as saved:
            for name,p in paths.items():
                saved.write(p, name)
            saved.writestr('backup_manifest.json', json.dumps(manifest, indent=2)+'\n')
        checksum = digest(candidate)
        verify(candidate, checksum, files, backup_format, limit)
        candidate.rename(archive)
    return {'status':'PASS', 'files':len(paths), 'bytes':archive.stat().st_size, 'sha256':checksum}


def restore(archive, trusted_sha256, destination, files=ALLOWED, backup_format='forestguard-279-imagery-backup-v1', limit=LIMIT):
    destination = Path(destination).resolve()
    # shortcut: recovery stays in a new local data folder; move verified copies manually to a fresh checkout.
    if not destination.is_relative_to((ROOT/'data').resolve()) or destination == (ROOT/'data').resolve():
        raise ValueError('Restore into a new folder inside this project data directory.')
    if destination.exists():
        raise ValueError('Restore destination exists; no files will be overwritten.')
    manifest = verify(archive, trusted_sha256, files, backup_format, limit)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(destination.parent).free < limit:
        raise ValueError('Insufficient free space for recovery.')
    with tempfile.TemporaryDirectory(prefix='restore_', dir=destination.parent) as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(archive) as saved:
            for name in manifest['files']:
                target = folder/name
                target.parent.mkdir(parents=True, exist_ok=True)
                with saved.open(name) as source, target.open('xb') as output:
                    shutil.copyfileobj(source, output, length=64*1024)
                if digest(target) != manifest['files'][name]['sha256']:
                    raise ValueError('Recovered file integrity failure: '+name)
        # Windows scanners can briefly hold newly extracted files open.
        for attempt in range(5):
            try:
                if destination.exists():raise ValueError('Restore destination appeared; do not overwrite it.')
                folder.rename(destination)
                break
            except PermissionError:
                if sys.platform!='win32':raise
                if attempt==4:
                    # Publish only to our new recovery folder; never touch live data.
                    destination.mkdir()
                    try:
                        shutil.copytree(folder,destination,dirs_exist_ok=True)
                        for name,record in manifest['files'].items():
                            if digest(destination/name)!=record['sha256']:raise ValueError('Copied recovery integrity failure')
                    except Exception:
                        if destination.is_symlink() or not destination.resolve().is_relative_to((ROOT/'data').resolve()):raise ValueError('Unsafe recovery cleanup path')
                        shutil.rmtree(destination)
                        raise
                    break
                time.sleep(.5)
    return {'status':'PASS', 'files':len(manifest['files']), 'destination':str(destination)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'verify', 'restore'])
    parser.add_argument('archive', type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    if args.action != 'create' and not args.sha256:
        parser.error('Retain and provide the original backup SHA-256 separately.')
    if args.action == 'restore' and not args.destination:
        parser.error('A new restore destination is required.')
    result = (create(args.archive) if args.action == 'create' else
              restore(args.archive, args.sha256, args.destination) if args.action == 'restore' else
              {'status':'PASS', 'files':len(verify(args.archive, args.sha256)['files'])})
    print(json.dumps(result, indent=2))
