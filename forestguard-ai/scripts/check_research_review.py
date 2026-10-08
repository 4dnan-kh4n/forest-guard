"""Check real review preparation without assigning or approving any labels."""
import argparse
import json
import tempfile
from pathlib import Path

from prepare_research_review import prepare

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('zip',type=Path)
args=parser.parse_args()
with tempfile.TemporaryDirectory() as temporary:
    output=Path(temporary)/'review'
    result=prepare(args.zip,output)
    cases=json.loads((output/'review_cases.geojson').read_text(encoding='utf-8'))
    assert result['reviewed_label_count']==0 and result['splits_frozen'] is False
    assert 0<len(cases['features'])<=21
    page=(output/'review.html').read_text(encoding='utf-8')
    assert 'data:image/png;base64,' in page and 'Unknown; unreviewed' in page
    assert '<script' not in page and '<iframe' not in page
    ids=set()
    for feature in cases['features']:
        properties=feature['properties']
        assert set(cases['required_feature_properties'])<=set(properties)
        assert properties['class']=='unknown' and properties['review_status']=='unreviewed'
        assert properties['reviewer'] is None and properties['confidence'] is None
        assert properties['reference_independent'] is False and properties['split']=='unassigned'
        assert feature['geometry']['coordinates'][0][0]==feature['geometry']['coordinates'][0][-1]
        assert properties['label_id'] not in ids
        ids.add(properties['label_id'])
    before=(output/'review_cases.geojson').read_bytes()
    try:prepare(args.zip,output)
    except ValueError as error:assert 'exists' in str(error)
    else:raise AssertionError('Existing review overwritten')
    assert (output/'review_cases.geojson').read_bytes()==before
print('PASS: real source cases retain unknown classes, no reviewer/confidence, unassigned splits and overwrite protection.')
