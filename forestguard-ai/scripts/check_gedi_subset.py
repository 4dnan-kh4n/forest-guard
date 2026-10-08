"""Check actual GEDI evidence, polygon inclusion, integer IDs and overwrite protection."""
import argparse
import json
import tempfile
from pathlib import Path

import h5py
from inspect_gedi_subset import inspect, inside_ring

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('subset',type=Path);parser.add_argument('boundary',type=Path)
args=parser.parse_args()
square=[[0,0],[2,0],[2,2],[0,2],[0,0]]
assert inside_ring(1,1,square) and inside_ring(0,1,square)
assert not inside_ring(3,1,square)
assert inside_ring(1,1,list(reversed(square)))
with tempfile.TemporaryDirectory() as directory:
    output=Path(directory)/'evidence'
    report=inspect(args.subset,args.boundary,output)
    points=json.loads((output/'shots.geojson').read_text(encoding='utf-8'))
    with h5py.File(args.subset) as handle:
        expected={str(int(shot)) for beam in handle if beam.startswith('BEAM') for shot in handle[beam]['shot_number'][:]}
    assert {f['properties']['shot_number'] for f in points['features']}==expected
    assert len(points['features'])==report['returned_shots']
    assert report['screen_pass_shots']<=report['inside_study_shots']<=report['returned_shots']
    assert report['labels_created']==0 and not report['independent_forest_accuracy_measured']
    for feature in points['features']:
        row=feature['properties']
        assert isinstance(row['shot_number'],str)
        if row['screen_pass']:
            assert row['inside_study'] and row['degrade_flag']==0 and row['l2a_quality_flag_rel3']==1
            assert .95<=row['sensitivity']<=1 and row['rh98_m'] is not None
    before=(output/'inspection_report.json').read_bytes()
    try:inspect(args.subset,args.boundary,output)
    except ValueError as error:assert 'Existing' in str(error)
    else:raise AssertionError('Existing evidence overwritten')
    assert (output/'inspection_report.json').read_bytes()==before
print('PASS: actual shots, exact integer identifiers, quality screen and overwrite protection.')
