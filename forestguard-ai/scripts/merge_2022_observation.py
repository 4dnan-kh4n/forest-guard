"""Add a verified 2022 cloud export, retaining the prior annual version."""
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
import rasterio
from rasterio.io import MemoryFile
from import_annual_observations import ROOT, verify
from build_annual_changes import save


def merge(path):
    incoming, hashes = verify(path)
    if [row['year'] for row in incoming['observations']] != [2022]:
        raise ValueError('Require the verified 2022-only export')
    target = ROOT/'data/annual/observations_v1'
    backup = ROOT/'data/annual/observations_before_2022'
    assert target.resolve().is_relative_to(ROOT.resolve()) and backup.resolve().is_relative_to(ROOT.resolve())
    if backup.exists(): raise ValueError('Previous version already preserved; do not repeat the merge')
    current = json.loads((target/'annual_report.json').read_bytes())
    if [row['year'] for row in current['observations']] != [2023,2024,2025,2026]:
        raise ValueError('Unexpected existing annual version')
    for key in ['model_sha256','model_available','study_area_version']:
        if current[key] != incoming[key]: raise ValueError('Annual provenance differs: '+key)
    with zipfile.ZipFile(path) as archive:
        with MemoryFile(archive.read('2022/features.tif')) as memory:
            with memory.open() as src: new_grid = (src.shape,src.crs,src.transform,src.descriptions)
        with rasterio.open(target/'2023/features.tif') as src:
            if new_grid != (src.shape,src.crs,src.transform,src.descriptions):
                raise ValueError('2022 does not align with the existing observations')
        with tempfile.TemporaryDirectory(prefix='merge_2022_',dir=target.parent) as temporary:
            staged = Path(temporary)/'observations'
            shutil.copytree(target,staged)
            for name in hashes:
                if name.startswith('2022/'):
                    destination=staged/name; destination.parent.mkdir(exist_ok=True)
                    destination.write_bytes(archive.read(name))
            current['observations'] = incoming['observations']+current['observations']
            (staged/'annual_report.json').write_bytes((json.dumps(current,indent=2)+'\n').encode())
            sources=json.loads((staged/'annual_checksums.json').read_bytes())
            sources.update({name:digest for name,digest in hashes.items() if name.startswith('2022/')})
            sources['annual_report.json']=hashlib.sha256((staged/'annual_report.json').read_bytes()).hexdigest()
            (staged/'annual_checksums.json').write_bytes((json.dumps(sources,indent=2)+'\n').encode())
            # The prior comparisons remain in the preserved original directory.
            (staged/'annual_changes.json').unlink()
            selected=['annual_report.json']+[f'{year}/preview.png' for year in range(2022,2027)]
            (staged/'ui_checksums.json').write_bytes((json.dumps({name:hashlib.sha256((staged/name).read_bytes()).hexdigest() for name in selected},indent=2)+'\n').encode())
            save(staged,current)
            record=json.loads((staged/'import_record.json').read_bytes())
            record['additional_archive_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            record['verified_years']=list(range(2022,2027))
            (staged/'import_record.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
            for name,digest in sources.items():
                assert hashlib.sha256((staged/name).read_bytes()).hexdigest()==digest
            target.rename(backup)
            try: shutil.move(str(staged),str(target))
            except Exception:
                backup.rename(target)
                raise
    print(json.dumps({'status':'PASS','years':record['verified_years'],'previous_version':str(backup)}))


if __name__=='__main__': merge(Path(sys.argv[1]))
