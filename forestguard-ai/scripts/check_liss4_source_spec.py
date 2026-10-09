"""Reject mismatched reference specifications before opening any source file."""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cloud'))
from liss4_reference_crop import run_liss4

valid = dict(product='RAF09NOV2025046306009700056SSANSTUC00GTDD',
             capture_date='2025-11-09', archive_sha256='a'*64,
             archive_bytes=1, band_bytes=1)
for change in [dict(product='../unknown'), dict(capture_date='2025-04-07'),
               dict(archive_sha256='not-a-hash'), dict(archive_bytes=0),
               dict(band_bytes=2*1024**3)]:
    spec = valid | change
    with patch('platform.system', return_value='Linux'), patch.object(Path, 'is_dir', return_value=True):
        try:
            run_liss4('never-opened.zip', {'type':'FeatureCollection'}, spec)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid source specification accepted.')
print('PASS: unknown product, wrong date, invalid checksum and unsafe sizes rejected before I/O.')
