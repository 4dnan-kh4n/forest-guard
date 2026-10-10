"""Fail the build when versioned officer data are missing, corrupt or unsafe."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def check(folder):
    folder=Path(folder)
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    required={'data/app/registered/compartment-279/registered.json',
              'data/phase3/research_proxy_map_v1/checksums.json',
              'data/phase4/research_proxy_change_v1/checksums.json'}
    if not required <= set(manifest):raise ValueError('Required officer datasets missing from manifest')
    total=0
    for name,record in manifest.items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name or not name.startswith('data/'):
            raise ValueError('Unsafe deployment path')
        path=folder/relative
        if path.is_symlink() or not path.is_file() or 'private' in name.lower():raise ValueError('Missing or unsafe deployment file: '+name)
        if path.stat().st_size!=record['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('Corrupt deployment file: '+name)
        total+=record['bytes']
    if total>=40*1024**2:raise ValueError('Deployment data exceeds 40 MiB budget')
    return {'status':'PASS','files':len(manifest),'bytes':total}


if __name__=='__main__':print(json.dumps(check(ROOT/'deployment_data')))
