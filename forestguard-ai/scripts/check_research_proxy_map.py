"""Verify bounded real proxy inference offline; retain operational forest gates."""
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from sklearn.metrics import confusion_matrix

from predict_research_proxy import predict
from prepare_proxy_errors import ROOT,MODEL,DATA,DATA_SHA,AFTER,MODEL_SHA
from train_weak_proxy import inspect_dataset
from predict_crop import load_model

labels=ROOT/'data/phase2/compartment_279_dataset_v1/labels.geojson'
paths=[MODEL,DATA,AFTER,labels]
original={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
with tempfile.TemporaryDirectory(prefix='proxy_map_check_',dir=ROOT/'data/phase3') as temporary:
    output=Path(temporary)/'map'
    with patch.object(socket,'socket',side_effect=AssertionError('Networking forbidden')):
        report=predict(output)
    hashes=json.loads((output/'checksums.json').read_text())
    for name,digest in hashes.items():assert hashlib.sha256((output/name).read_bytes()).hexdigest()==digest
    with rasterio.open(output/'proxy_classes.tif') as raster:
        classes=raster.read(1);assert raster.nodata==255 and raster.shape==(123,172)
        assert raster.crs.to_epsg()==32643 and raster.transform.a==20 and raster.transform.e==-20
        assert raster.tags()['operational_use_approved']=='false'
        assert set(np.unique(classes))=={0,1,255}
        grid=raster.transform
    with rasterio.open(output/'tree_vote_share.tif') as raster:
        votes=raster.read(1);assert raster.nodata==-1 and raster.transform==grid
        assert raster.tags()['model_kind']=='exploratory_weak_map_proxy'
    observed=classes!=255
    assert int(observed.sum())==12362 and report['study_mask_pixels']==13099
    assert (votes[~observed]==-1).all() and np.isfinite(votes[observed]).all()
    assert ((votes[observed]>=0)&(votes[observed]<=1)).all()
    assert np.array_equal(classes[observed],(votes[observed]>.5).astype('uint8'))
    samples,_=inspect_dataset(DATA,DATA_SHA);rows,cols=samples['validation_pixels'].T
    assert confusion_matrix(samples['validation_y'],classes[rows,cols],labels=[0,1]).tolist()==[[1049,157],[63,4798]]
    assert sum(report['class_pixels'].values())==12362
    assert not report['operational_use_approved'] and report['forest_area_ha'] is None
    assert not report['local_training_performed']
    page=(output/'map.html').read_text()
    assert '2025-12-09' in page and 'uncalibrated' in page.lower() and 'unapproved research' in page
    assert page.count('<rect ')==12362
    try:predict(output)
    except ValueError:pass
    else:raise AssertionError('Existing result overwritten.')
    try:load_model(MODEL,MODEL_SHA)
    except (ValueError,KeyError):pass
    else:raise AssertionError('Operational loader accepted the proxy.')
assert original=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
summary={'status':'PASS','network_blocked_inference':True,'predicted_pixels':12362,'class_and_vote_grids_checked':True,
         'validation_confusion_matrix_matches_cloud':True,'output_checksums_checked':True,'nodata_and_vote_bounds_checked':True,
         'originals_unchanged':True,'overwrite_rejected':True,'operational_forest_loader_rejects_proxy':True,
         'local_training_performed':False,'independent_forest_accuracy_measured':False,'browser_rendering_checked':False}
(ROOT/'data/phase3/research_proxy_map_v1/verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
