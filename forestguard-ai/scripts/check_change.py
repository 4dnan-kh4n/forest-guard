"""Verify change arithmetic and guards with explicit synthetic classifications."""
import csv
import hashlib
import json
import shutil
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.transform import from_origin

from detect_change import compare

root = Path(__file__).resolve().parents[1]
work = root/'data/phase4';work.mkdir(exist_ok=True)
before = np.tile(np.array([[0,1,1,0],[255,1,0,255]],dtype='uint8'),(16,1))
after = np.tile(np.array([[0,1,0,1],[0,255,255,255]],dtype='uint8'),(16,1))
study = np.ones(before.shape,dtype='uint8');study[1::2,0]=0
tags = {'synthetic_fixture':'true','model_version':'synthetic-fixture-v1',
        'forest_definition_version':'forestguard-cover-v1','study_area_version':'synthetic-study-v1',
        'class_mapping':'0:non_forest,1:forest','season_review_status':'comparable','operational_use_approved':'false'}


def write(folder,a=before,b=after,mask=study,later_tags=None,shift=0):
    profile = dict(driver='GTiff',height=32,width=4,count=1,dtype='uint8',crs='EPSG:32643',transform=from_origin(500000,2500000,20,20))
    for name,values,extra in [('before',a,{'acquisition_date':'2025-01-10'}),('after',b,{'acquisition_date':'2026-01-12',**(later_tags or {})}),('study_mask',mask,{})]:
        grid = dict(profile)
        if name=='after':grid['transform']=from_origin(500000+shift,2500000,20,20)
        grid['nodata']=0 if name=='study_mask' else 255
        with rasterio.open(folder/(name+'.tif'),'w',**grid) as raster:
            raster.write(values,1)
            raster.update_tags(**(tags|extra))


with tempfile.TemporaryDirectory(prefix='check_change_',dir=work) as temporary:
    folder = Path(temporary);write(folder)
    paths = [folder/(name+'.tif') for name in ['before','after','study_mask']]
    original = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        report = compare(*paths,folder/'result')
    assert report['study_mask_pixels']==112 and report['common_observable_pixels']==64
    assert report['unobservable_study_pixels']==48 and report['observable_area_ha']==2.56
    assert report['transition_pixels']==dict.fromkeys(['stable_non_forest','stable_forest','suspected_loss','suspected_gain'],16)
    assert report['transition_area_ha']==dict.fromkeys(report['transition_pixels'],.64)
    assert report['net_cover_change_on_common_ha']==0 and report['common_coverage_fraction']==64/112
    with rasterio.open(folder/'result/change.tif') as raster:
        expected = np.tile(np.array([[0,1,2,3],[255,255,255,255]],dtype='uint8'),(16,1))
        assert np.array_equal(raster.read(1),expected) and raster.nodata==255
        assert raster.tags()['synthetic_fixture']=='true'
    assert json.loads((folder/'result/change_report.json').read_text())==report
    with (folder/'result/transitions.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
        assert len(rows)==4 and all(row['synthetic_fixture']=='True' and float(row['area_ha'])==.64 for row in rows)
    assert original==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    fixture = work/'synthetic_change_v1'
    if not fixture.exists():
        fixture.mkdir()
        for p in paths:shutil.copyfile(p,fixture/p.name)
        shutil.copytree(folder/'result',fixture/'result')
    else:
        assert json.loads((fixture/'result/change_report.json').read_text())==report
    try:compare(*paths,folder/'result')
    except ValueError as error:assert 'Output exists' in str(error)
    else:raise AssertionError('Output overwritten')
    invalid = before.copy();invalid[0,0]=2
    variants = [({'shift':20},'share the supported'),({'later_tags':{'model_version':'other'}},'metadata mismatch'),
                ({'later_tags':{'acquisition_date':'2024-01-10'}},'chronological'),
                ({'later_tags':{'acquisition_date':'2026-06-12'}},'seasonal'),
                ({'later_tags':{'season_review_status':'unreviewed'}},'seasonal'),
                ({'later_tags':{'synthetic_fixture':'false'}},'metadata mismatch'),
                ({'later_tags':{'class_mapping':'0:forest,1:non_forest'}},'semantics'),
                ({'a':invalid},'classification values'),
                ({'mask':np.full(study.shape,2,dtype='uint8')},'classification values'),
                ({'b':np.full(study.shape,255,dtype='uint8')},'coverage must be nonempty')]
    for index,(options,message) in enumerate(variants):
        write(folder,**options)
        output = folder/('bad_'+str(index))
        try:compare(*paths,output)
        except ValueError as error:assert message in str(error),str(error)
        else:raise AssertionError('Invalid comparison accepted')
        assert not output.exists()
    write(folder,a=np.ones(before.shape,dtype='uint8'),b=np.ones(after.shape,dtype='uint8'))
    stable = compare(*paths,folder/'stable')
    assert stable['transition_pixels']['stable_forest']==112
    assert stable['transition_pixels']['suspected_loss']==stable['transition_pixels']['suspected_gain']==0
    for p in paths:
        with rasterio.open(p,'r+') as raster:raster.update_tags(synthetic_fixture='false')
    try:compare(*paths,folder/'unapproved')
    except ValueError as error:assert 'operational review' in str(error)
    else:raise AssertionError('Unapproved real maps accepted')

summary = {'status':'PASS','synthetic_fixture':True,'real_change_accuracy_measured':False,
           'all_four_transitions_checked':True,'common_coverage_and_hectares_checked':True,
           'no_data_excluded':True,'offline_multiple_windows_checked':True,'json_csv_raster_checked':True,
           'grid_metadata_date_season_scope_value_guards_checked':True,
           'empty_overlap_and_unapproved_real_maps_rejected':True,'stable_map_no_change_checked':True,
           'overwrite_and_partial_output_prevention_checked':True,'source_inputs_unchanged':True}
(work/'engineering_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
