"""Verify original XML calibration and fail closed on incomplete metadata."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cloud.observation_2022 import calibration_xml,run_2022,BAND_IDS
raw=(ROOT/'data/annual/2022_2026_v1/pc_2022_product.xml').read_bytes()
calibration=calibration_xml(raw)
assert set(calibration)==set(BAND_IDS)
assert all(value=={'scale':.0001,'offset':-.1} for value in calibration.values())
assert 1500*calibration['B04']['scale']+calibration['B04']['offset']==.04999999999999999
for invalid in [b'<!DOCTYPE x><x/>',b'<x/>',raw.replace(b'<BOA_QUANTIFICATION_VALUE unit="none">10000',b'<BOA_QUANTIFICATION_VALUE unit="none">0')]:
    try:calibration_xml(invalid)
    except (ValueError,KeyError):pass
    else:raise AssertionError('Invalid calibration accepted')
try:run_2022(None,None,None)
except RuntimeError:pass
else:raise AssertionError('Local acquisition was allowed')
print('PASS: verified product XML, band offsets, invalid metadata rejection and local acquisition guard.')
