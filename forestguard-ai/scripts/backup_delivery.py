"""Preserve the bounded research release: code/build, references, reviews, fixtures and wheels."""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

import backup_research as backup

ROOT=backup.ROOT
FORMAT='forestguard-research-delivery-v1'
# Annual imagery and deployable data increased the measured release to 281 MiB.
LIMIT=320*1024**2
DATA_DIRS=[
    'data/study/compartment_279_v1/research_v2_20261008',
    'data/study/compartment_279_v1/december_2024_v1',
    'data/phase2/same_season_2024_v1','data/phase2/december_pair_assessment_v3',
    'data/labels', 'data/phase2/compartment_279_dataset_v1',
    'data/phase2/weak_proxy_experiment_v1', 'data/phase3/weak_proxy_run_v1',
    'data/phase2/weak_december_experiment_v1', 'data/phase3/weak_december_run_v1',
    'data/phase3/weak_december_error_inspection_v1',
    'data/phase3/exploratory_handoff_v1',
    'data/phase3/research_proxy_map_v1',
    'data/phase5/research_dashboard_v1',
    'data/reference/bhoonidhi_20261009/november_crop_v1',
    'data/reference/bhoonidhi_20261009/crop_v5',
    'data/reference/eth_canopy_height_2020/crop_v1',
    'data/reference/user_comp_pf_2026_10_08',
    'data/phase3/synthetic_check_v1', 'data/phase3/inference_fixture_v1',
    'data/phase3/offline_prediction_run1', 'data/phase3/inference_wheels',
    'data/phase4/synthetic_change_v1', 'data/phase4/comparison_run1',
    'data/tooling/wheels/windows-cp311', 'data/app/change_runs',
    'data/annual/observations_v1','data/annual/2022_pc_v1','data/annual/2022_2026_v1',
    'data/fire/recent_v1','data/fire/archive_2022_2026_v1',
]
CODE_DIRS=['backend','scripts','cloud','config','docs','notebooks','frontend/src','frontend/public','frontend/dist','deployment_data']
ROOT_FILES=['.gitignore','.env.example','AGENTS.md','README.md','PROJECT_PLAN.md','start_ui.ps1',
            'requirements-lock.txt','requirements-ui-lock.txt','requirements-inference.txt',
            'pyproject.toml','app.py','vercel.json','.vercelignore','.gitattributes','requirements-ui.txt','requirements.txt',
            'frontend/index.html','frontend/package.json','frontend/pnpm-lock.yaml','frontend/vite.config.js',
            'data/phase5/offline_install_v1/wheel_inventory.json']


def allowed(name):
    path=PurePosixPath(name)
    if path.is_absolute() or '\\' in name or ':' in name or '..' in path.parts or '__pycache__' in path.parts:
        return False
    if any(part.startswith('.env') for part in path.parts) and name!='.env.example':return False
    if path.suffix.lower() in {'.sqlite','.db','.pem','.key','.bin','.log'} or 'private' in path.name.lower():return False
    if path.name.lower().startswith(('credentials','kaggle.json','service-account')):return False
    return name in backup.ALLOWED or name in ROOT_FILES or any(name.startswith(p+'/') for p in DATA_DIRS+CODE_DIRS)


def selection():
    tracked=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','--','.'],cwd=ROOT,
                           check=True,capture_output=True,text=True).stdout.splitlines()
    names={n for n in tracked if allowed(n) and (ROOT/n).is_file()}
    names.update(backup.ALLOWED)
    for folder in DATA_DIRS+['frontend/dist']:
        for path in (ROOT/folder).rglob('*'):
            name=path.relative_to(ROOT).as_posix()
            if path.is_file() and not path.is_symlink() and allowed(name):names.add(name)
    names.update(n for n in ROOT_FILES if (ROOT/n).is_file())
    if any(not allowed(n) or (ROOT/n).is_symlink() or (ROOT/n).stat().st_size>64*1024**2 for n in names):
        raise ValueError('Unsafe or oversized delivery input.')
    return names


def archive_files(archive,checksum):
    if Path(archive).stat().st_size>LIMIT or backup.digest(archive)!=checksum:
        raise ValueError('Delivery backup checksum/size mismatch.')
    with zipfile.ZipFile(archive) as saved:
        if saved.getinfo('backup_manifest.json').file_size>512*1024:raise ValueError('Oversized manifest')
        manifest=json.loads(saved.read('backup_manifest.json'))
    if not isinstance(manifest,dict) or not isinstance(manifest.get('files'),dict):raise ValueError('Invalid manifest.')
    names=set(manifest['files'])
    if not backup.ALLOWED<=names or any(not allowed(n) for n in names):raise ValueError('Unsafe/incomplete delivery paths.')
    return names


def create(archive):
    return backup.create(archive,selection(),
        'Current compartment 279 research release. Real observations, unreviewed references and cloud-trained weak-label proxy; synthetic training/change fixtures. No independently validated forest model. Excludes accounts, full scenes and environments.',FORMAT,LIMIT)


def verify(archive,checksum):
    return backup.verify(archive,checksum,archive_files(archive,checksum),FORMAT,LIMIT)


def restore(archive,checksum,destination):
    return backup.restore(archive,checksum,destination,archive_files(archive,checksum),FORMAT,LIMIT)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['create','verify','restore'])
    parser.add_argument('archive',type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--destination',type=Path)
    args=parser.parse_args()
    if args.action!='create' and not args.sha256:parser.error('Provide the separately retained backup checksum.')
    if args.action=='restore' and not args.destination:parser.error('Provide a new destination inside data/.')
    result=(create(args.archive) if args.action=='create' else restore(args.archive,args.sha256,args.destination)
            if args.action=='restore' else {'status':'PASS','files':len(verify(args.archive,args.sha256)['files'])})
    print(json.dumps(result,indent=2))
