"""Synthetic arithmetic fixture and actual annual area conservation checks."""
import json
import tempfile
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin
from build_annual_changes import ROOT,calculate

with tempfile.TemporaryDirectory(dir=ROOT/'data/annual',prefix='synthetic_change_check_') as temporary:
    folder=Path(temporary)
    for year,values in [(2024,[0,1,1,0,255]),(2025,[0,1,0,1,255])]:
        (folder/str(year)).mkdir()
        with rasterio.open(folder/str(year)/'proxy_classes.tif','w',driver='GTiff',crs='EPSG:32643',transform=from_origin(684080,2479720,20,20),width=5,height=1,count=1,dtype='uint8',nodata=255) as dst:dst.write(np.array([values],dtype='uint8'),1)
    rows=[{'year':year,'date':f'{year}-10-01','study_pixels':5} for year in [2024,2025]]
    report={'observations':rows,'model_available':True}
    pair=calculate(folder,report)[0]
    assert pair['common_pixels']==4 and pair['common_coverage_percent']==80
    assert pair['suspected_tree_proxy_loss_ha']==.04 and pair['suspected_tree_proxy_gain_ha']==.04
    assert calculate(folder,dict(report,model_available=False))==[]
folder=ROOT/'data/annual/observations_v1'
report=json.loads((folder/'annual_report.json').read_bytes())
pairs=calculate(folder,report)
assert len(pairs)==4
assert all(sum(p['transition_pixels'].values())==p['common_pixels'] for p in pairs)
assert pairs==json.loads((folder/'annual_changes.json').read_bytes())['comparisons']
print('PASS: annual common coverage, all transitions, excluded pixels and actual saved comparison reproducibility.')
