"""Copy only bounded, selected dashboard data; never copy accounts or training models."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDERS=['data/app/registered/compartment-279','data/phase2/pair_version7',
         'data/demo/fixture_v1','data/phase3/research_proxy_map_v1','data/phase4/synthetic_change_v1',
         'data/phase4/research_proxy_change_v1']
FILES=['data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip',
       'data/study/compartment_279_v1/boundary.geojson','data/fire/recent_v1/report.json',
       'data/fire/archive_2022_2026_v1/report.json','data/fire/archive_2022_2026_v1/checksums.json','data/fire/archive_2022_2026_v1/source.csv']


def prepare():
    paths=[ROOT/name for name in FILES]
    annual=ROOT/'data/annual/observations_v1'
    if annual.exists():
        paths.extend([annual/'annual_report.json',annual/'ui_checksums.json',annual/'import_record.json',annual/'annual_changes.json'])
        paths.extend(annual.glob('*/preview.png'))
    for name in FOLDERS:
        paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file())
    paths=[p for p in paths if p.suffix.lower() in {'.tif','.png','.json','.geojson','.zip','.svg','.html','.csv','.xml'}]
    assert all(p.exists() and not p.is_symlink() and 'private' not in p.name.lower() for p in paths)
    assert sum(p.stat().st_size for p in paths)<40*1024**2,'Selected data exceeds 40 MiB budget'
    target=ROOT/'deployment_data';target.mkdir(exist_ok=True)
    manifest={}
    for source in paths:
        name=source.relative_to(ROOT).as_posix();saved=target/name
        saved.parent.mkdir(parents=True,exist_ok=True)
        checksum=hashlib.sha256(source.read_bytes()).hexdigest()
        if saved.exists() and hashlib.sha256(saved.read_bytes()).hexdigest()!=checksum:
            raise ValueError('Preserve changed deployment file before replacing: '+name)
        if not saved.exists():shutil.copyfile(source,saved)
        assert hashlib.sha256(saved.read_bytes()).hexdigest()==checksum
        manifest[name]={'bytes':saved.stat().st_size,'sha256':checksum}
    # The manifest is reviewed, versioned deployment data, not an unbounded upload directory.
    (target/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print(json.dumps({'status':'PASS','files':len(manifest),'bytes':sum(r['bytes'] for r in manifest.values())}))


if __name__=='__main__':prepare()
