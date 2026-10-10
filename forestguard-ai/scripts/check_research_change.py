"""Verify real proxy transitions, offline reproducibility and saved API integrity."""
import hashlib
import json
import socket
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio

from predict_research_change import ROOT, BEFORE, AFTER, MODEL, predict, transitions

sys.path.insert(0, str(ROOT))
from backend import app as api
from fastapi import HTTPException

first = np.array([[0, 1, 1, 0, 255]], dtype='uint8')
last = np.array([[0, 1, 0, 1, 255]], dtype='uint8')
assert transitions(first, last, first != 255).tolist() == [[0, 1, 2, 3, 255]]
try:
    transitions(first, last, np.ones(first.shape, dtype=bool))
except ValueError:
    pass
else:
    raise AssertionError('Invalid observable classes accepted')
source_hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in [BEFORE, AFTER, MODEL]}
saved = ROOT / 'data/phase4/research_proxy_change_v1'
with tempfile.TemporaryDirectory(prefix='change_check_', dir=ROOT / 'data/phase4') as temporary:
    output = Path(temporary) / 'result'
    with patch.object(socket, 'socket', side_effect=AssertionError('Networking forbidden')):
        report = predict(output)
    assert report['transition_pixels'] == {'0': 3359, '1': 8634, '2': 60, '3': 309}
    assert report['common_observable_pixels'] == 12362 and report['synthetic'] is False
    assert report['forest_loss_ha'] is None and not report['operational_use_approved']
    hashes = json.loads((output / 'checksums.json').read_text())
    assert hashes == json.loads((saved / 'checksums.json').read_text())
    for name, digest in hashes.items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == digest
    arrays = []
    for name in ['before_classes.tif', 'after_classes.tif', 'change_classes.tif']:
        with rasterio.open(output / name) as raster:
            assert raster.nodata == 255 and raster.crs.to_epsg() == 32643 and raster.shape == (123, 172)
            assert raster.tags()['operational_use_approved'] == 'false'
            arrays.append(raster.read(1))
    with rasterio.open(output / 'observations/common_usable.tif') as raster:
        common = raster.read(1) == 1
    assert np.array_equal(transitions(*arrays[:2], common), arrays[2])
    assert all((array[~common] == 255).all() for array in arrays)
    try:
        predict(output)
    except ValueError:
        pass
    else:
        raise AssertionError('Existing output overwritten')
    with patch.object(api, 'RESEARCH_CHANGE', output):
        assert api.research_change_status()['available']
        for layer in ['before', 'after', 'changes']:
            assert Path(api.research_change_image(layer).path).exists()
        for fmt in api.RESEARCH_CHANGE_EXPORTS:
            assert Path(api.research_change_download(fmt).path).exists()
        for action in [lambda: api.research_change_image('../checksums'), lambda: api.research_change_download('bad')]:
            try:
                action()
            except HTTPException as error:
                assert error.status_code == 404
            else:
                raise AssertionError('Unknown artifact accepted')
        (output / 'changes.csv').write_text('corrupt')
        try:
            api.research_change_status()
        except HTTPException as error:
            assert error.status_code == 503
        else:
            raise AssertionError('Corrupt output accepted')
assert source_hashes == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_hashes}
print(json.dumps({'status':'PASS','real_common_pixels':12362,'offline_reproducible':True,
                  'four_transitions_and_nodata_checked':True,'area_conservation_checked':True,
                  'corrupt_saved_data_rejected':True,'originals_preserved':True,
                  'independent_forest_accuracy_measured':False},indent=2))
