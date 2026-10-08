"""Offline self-check for saved public CMR inventory; no authentication or download."""
import argparse
import hashlib
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('folder',type=Path)
args=parser.parse_args()
report=json.loads((args.folder/'inventory_report.json').read_text(encoding='utf-8'))
assert report['status']=='METADATA_INVENTORY_COMPLETE'
assert not report['shot_coverage_verified'] and not report['lidar_files_downloaded'] and not report['reference_labels_created']
assert {r['short_name'] for r in report['collections']}=={'GEDI02_A','GEDI02_B'}
for record in report['collections']:
    product=record['short_name']
    for kind,suffix in [('collection_metadata','collections'),('granule_metadata','granules')]:
        raw=(args.folder/f'{product}_{suffix}.json').read_bytes()
        assert len(raw)==record[kind]['bytes'] and hashlib.sha256(raw).hexdigest()==record[kind]['sha256']
    collections=json.loads((args.folder/f'{product}_collections.json').read_text(encoding='utf-8'))['feed']['entry']
    versions=[int(c['version_id']) for c in collections if c.get('version_id','').isdigit()]
    assert int(record['version'])==max(versions)
    granules=json.loads((args.folder/f'{product}_granules.json').read_text(encoding='utf-8'))['feed']['entry']
    assert len(granules)==record['returned_granules']==int(record['granule_metadata']['total_metadata_hits'])
    assert [g.get('producer_granule_id',g.get('title')) for g in granules]==record['granule_ids']
print('PASS: saved source checksums, latest numbered versions and complete small inventory; shot coverage remains unverified by catalogue.')
