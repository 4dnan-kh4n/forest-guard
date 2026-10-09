"""Compare local saved-model inference with the preserved synthetic cloud test."""
import copy
import hashlib
import io
import json
import shutil
import socket
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_origin

from predict_crop import predict
from verify_training_smoke import verify

root = Path(__file__).resolve().parents[1]
saved = root/'data/phase3/synthetic_check_v1/synthetic_training_check.zip'
assert verify(saved)['integrity']=='PASS'
with zipfile.ZipFile(saved) as archive:
    model_bytes = archive.read('synthetic_model_export.zip')
with zipfile.ZipFile(io.BytesIO(model_bytes)) as archive:
    manifest = json.loads(archive.read('model_manifest.json'))
    evaluation = json.loads(archive.read('evaluation.json'))
trusted = hashlib.sha256(model_bytes).hexdigest()
rng = np.random.default_rng(42)
for count in [64,32,32]:
    truth = np.tile([0,1],count//2).astype('uint8')
    values = rng.normal(size=(count,15)).astype('float32')*.15+truth[:,None]
truth[:2] = 1-truth[:2]
expected = truth.copy()
for failure in evaluation['failure_pixels']:
    index = failure['date_row_col'][1]
    assert failure['reference']==truth[index]
    expected[index] = failure['prediction']
# This fixture has fewer than the export's 20-error cap, so all cloud predictions are reconstructible.
confusion = evaluation['test'][evaluation['selected_model']]['confusion_matrix']
assert confusion['fp']+confusion['fn']==len(evaluation['failure_pixels'])
features = np.tile(values.T.reshape(15,4,8),(1,8,1))
expected = np.tile(expected.reshape(4,8),(8,1))
mask = np.ones(expected.shape,dtype='uint8');mask.flat[[0,9,100]]=0
expected[mask==0] = 255


def write_rasters(folder,data=features,quality=mask,order=None,synthetic=True,shift=0):
    profile = dict(driver='GTiff',height=32,width=8,crs='EPSG:32643',transform=from_origin(500000,2500000,20,20))
    with rasterio.open(folder/'features.tif','w',count=15,dtype='float32',**profile) as out:
        out.write(data)
        out.descriptions = tuple(order or manifest['feature_order'])
        out.update_tags(synthetic_fixture=str(synthetic).lower())
    profile['transform'] = from_origin(500000+shift,2500000,20,20)
    with rasterio.open(folder/'mask.tif','w',count=1,dtype='uint8',**profile) as out:out.write(quality,1)


with tempfile.TemporaryDirectory(dir=root/'data/phase3',prefix='check_inference_') as temporary:
    folder = Path(temporary)
    model = folder/'model.zip';model.write_bytes(model_bytes)
    write_rasters(folder)
    with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        result = predict(model,trusted,folder/'features.tif',folder/'mask.tif',folder/'prediction')
    with rasterio.open(folder/'prediction/classes.tif') as raster:
        assert np.array_equal(raster.read(1),expected)
        assert raster.nodata==255 and raster.tags()['synthetic_fixture']=='true'
        assert raster.tags()['class_mapping']=='0:non_forest,1:forest'
        assert raster.tags()['forest_definition_version']==manifest['forest_definition_version']
        assert raster.tags()['operational_use_approved']=='false'
    assert result['predicted_pixels']==253 and result['nodata_pixels']==3 and result['forest_area_ha'] is None
    fixture = root/'data/phase3/inference_fixture_v1'
    if not fixture.exists():
        fixture.mkdir()
        for name in ['model.zip','features.tif','mask.tif']:shutil.copyfile(folder/name,fixture/name)
        shutil.copytree(folder/'prediction',fixture/'prediction')
    else:
        assert (fixture/'model.zip').read_bytes()==model_bytes
        with rasterio.open(fixture/'prediction/classes.tif') as raster:assert np.array_equal(raster.read(1),expected)
    try: predict(model,trusted,folder/'features.tif',folder/'mask.tif',folder/'prediction')
    except ValueError as error:assert 'Output exists' in str(error)
    else:raise AssertionError('Existing output overwritten')
    variants = [({'order':list(reversed(manifest['feature_order']))},'feature count/order'),
                ({'synthetic':False},'scope mismatch'),({'shift':20},'grids must match'),
                ({'quality':np.full(mask.shape,2,dtype='uint8')},'zero/one')]
    invalid = features.copy();invalid[0,1,1]=np.nan
    # Row 1/column 1 is deliberately masked out; invalid features there may be ignored.
    write_rasters(folder,data=invalid)
    predict(model,trusted,folder/'features.tif',folder/'mask.tif',folder/'masked_nan')
    invalid[0,2,2]=np.nan
    variants.append(({'data':invalid},'nonfinite'))
    for index,(options,message) in enumerate(variants):
        write_rasters(folder,**options)
        out = folder/('bad'+str(index))
        try:predict(model,trusted,folder/'features.tif',folder/'mask.tif',out)
        except ValueError as error:assert message in str(error),str(error)
        else:raise AssertionError('Invalid crop accepted')
        assert not out.exists()
    try:predict(model,'0'*64,folder/'features.tif',folder/'mask.tif',folder/'bad_hash')
    except ValueError as error:assert 'trusted archive checksum' in str(error)
    else:raise AssertionError('Untrusted model accepted')
    # Alter metadata with consistent hashes to test the scientific approval gate.
    with zipfile.ZipFile(io.BytesIO(model_bytes)) as archive:members={n:archive.read(n) for n in archive.namelist()}
    baseline = copy.deepcopy(manifest)
    baseline['selected_model_file']='baseline.joblib'
    baseline['model_version']='synthetic-baseline-'+hashlib.sha256(members['baseline.joblib']).hexdigest()[:16]
    members['model_manifest.json']=json.dumps(baseline).encode()
    members['checksums.json']=json.dumps({n:hashlib.sha256(b).hexdigest() for n,b in members.items() if n!='checksums.json'}).encode()
    with zipfile.ZipFile(model,'w') as archive:
        for name,data in members.items():archive.writestr(name,data)
    write_rasters(folder)
    baseline_result = predict(model,hashlib.sha256(model.read_bytes()).hexdigest(),folder/'features.tif',folder/'mask.tif',folder/'baseline')
    assert baseline_result['class_pixels']=={'0':253,'1':0}
    changed = copy.deepcopy(manifest);changed['synthetic_fixture']=False
    members['model_manifest.json']=json.dumps(changed).encode()
    members['checksums.json']=json.dumps({n:hashlib.sha256(b).hexdigest() for n,b in members.items() if n!='checksums.json'}).encode()
    with zipfile.ZipFile(model,'w') as archive:
        for name,data in members.items():archive.writestr(name,data)
    try:predict(model,hashlib.sha256(model.read_bytes()).hexdigest(),folder/'features.tif',folder/'mask.tif',folder/'unapproved')
    except ValueError as error:assert 'operational review' in str(error)
    else:raise AssertionError('Unapproved real model accepted')

summary = {'status':'PASS','synthetic_fixture':True,'real_forest_accuracy_measured':False,
           'cloud_local_predictions_identical':True,'tested_pixels':256,'masked_pixels':3,
           'saved_baseline_inference_checked':True,
           'offline_prediction_checked':True,'multiple_windows_checked':True,
           'input_order_grid_scope_finite_mask_guards_checked':True,
           'overwrite_and_partial_output_prevention_checked':True,'untrusted_and_unapproved_model_rejected':True}
(root/'data/phase3/inference_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
