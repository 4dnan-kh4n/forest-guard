"""Check real error locations, images, scope and preservation without networking or fitting."""
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from prepare_proxy_errors import ROOT,BEFORE,AFTER,REFERENCE,DATA,MODEL,choose,generate

labels=ROOT/'data/phase2/compartment_279_dataset_v1/labels.geojson'
paths=[BEFORE,AFTER,REFERENCE,DATA,MODEL,labels]
original={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
with tempfile.TemporaryDirectory(prefix='error_check_',dir=ROOT/'data/phase3') as temporary:
    output=Path(temporary)/'inspection'
    with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        report=generate(output)
    document=json.loads((output/'diagnostic_cases.geojson').read_text())
    features=document['features'];assert len(features)==9
    props=[f['properties'] for f in features]
    assert [p['reference_code'] for p in props]==[20]*3+[40]*3+[10]*3
    assert all(p['class']=='unknown' and p['review_status']=='unreviewed' and not p['reference_independent'] and p['split']=='unassigned' for p in props)
    assert all(p['prediction']==('other-cover proxy' if p['reference_code']==10 else 'tree-cover proxy') for p in props)
    assert len({p['validation_sample_index'] for p in props})==9
    assert all(np.hypot(p['row']-q['row'],p['col']-q['col'])*20>=150 for i,p in enumerate(props) for q in props[i+1:])
    assert sum(v['disagreements'] for v in report['by_reference_class'].values())==220
    assert sum(v['validation_samples'] for v in report['by_reference_class'].values())==6067
    assert len(report['reference_nonzero_coverage'])==9
    assert all(v['context_pixels']>0 and v['nonzero_pixels']==v['context_pixels'] for v in report['reference_nonzero_coverage'])
    page=(output/'inspection.html').read_text()
    assert page.count('<svg ')==27 and page.count('data:image/png;base64,')==27
    assert all(date in page for date in ['2024-12-16','2025-12-09','2025-11-09'])
    assert 'no forest labels' in page.lower() and 'not independent' in page.lower()
    assert report['labels_assigned']==0 and not report['operational_use_approved']
    try:generate(output)
    except ValueError:pass
    else:raise AssertionError('Existing inspection overwritten.')
    try:choose(np.array([[3,3]]),np.array([20]),np.array([0]),(20,20))
    except ValueError:pass
    else:raise AssertionError('Agreement accepted as an error.')
assert original=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
summary={'status':'PASS','real_disagreement_cases':9,'embedded_dated_views':27,'selection_and_150m_spacing_checked':True,
         'old_reference_class_counts_match':True,'network_blocked_generation':True,'sources_and_labels_unchanged':True,
         'overwrite_and_empty_error_guards_checked':True,'labels_assigned':0,'independent_forest_accuracy_measured':False,
         'browser_rendering_checked':False}
(ROOT/'data/phase3/weak_december_error_inspection_v1/verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
