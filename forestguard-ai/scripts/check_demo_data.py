"""Check real generated fixture integrity, split separation and determinism."""
import argparse
import json
import tempfile
from pathlib import Path
import hashlib
import zipfile
import numpy as np
import rasterio
from make_demo_data import generate

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('folder',type=Path)
args=parser.parse_args()
folder=args.folder.resolve(strict=True)
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['data_kind']=='synthetic' and not manifest['real_pilot_validation']
assert not manifest['real_forest_training_eligible'] and manifest['demo_training_eligible']
hashes=json.loads((folder/'checksums.json').read_text())
with zipfile.ZipFile(folder/'synthetic_demo.zip') as archive:
    assert archive.testzip() is None
    for name,record in hashes.items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==record['sha256']
        assert hashlib.sha256(archive.read(name)).hexdigest()==record['sha256']
masks=[]; dates=[]
for sample in manifest['samples']:
    with rasterio.open(folder/sample['directory']/'split_mask.tif') as src: mask=src.read(1).astype(bool)
    with rasterio.open(folder/sample['directory']/'labels.tif') as src: labels=src.read(1)
    with rasterio.open(folder/sample['directory']/'reflectance.tif') as src:
        assert src.descriptions==tuple(manifest['band_order'])
        assert src.tags()['data_kind']=='synthetic' and src.shape==tuple(manifest['shape'])
    assert np.all(labels[~mask]==255)
    assert set(np.unique(labels[mask]))=={0,1,255}
    masks.append(mask); dates.append(sample['simulated_date'])
assert len(set(dates))==3
for i,a in enumerate(masks):
    for b in masks[i+1:]: assert not (a&b).any()
for a,b in zip(manifest['samples'],manifest['samples'][1:]):
    assert (b['columns'][0]-a['columns'][1])*10>=100
base=folder.parent/'checks'; base.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=base) as temporary:
    temporary=Path(temporary).resolve(); assert temporary.is_relative_to(base.resolve())
    generate(temporary,manifest['seed'])
    repeated=json.loads((temporary/'checksums.json').read_text())
    assert hashes==repeated,'Same seed/runtime did not produce identical artifact bytes'
    try: generate(temporary,manifest['seed'])
    except ValueError: pass
    else: raise AssertionError('Nonempty fixture directory was overwritten')
summary={'status':'PASS','data_kind':'synthetic','verified_files':len(hashes),
    'same_seed_reproducible':True,'spatial_splits_disjoint':True,'gap_m':160,
    'simulated_dates_disjoint':True,'overwrite_rejected':True,'real_pilot_validation':False}
(folder/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
