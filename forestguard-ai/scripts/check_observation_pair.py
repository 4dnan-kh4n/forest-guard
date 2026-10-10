"""Check real December-pair assessment, source preservation and comparison guards offline."""
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio

from assess_observation_pair import assess,season_gap
from register_research_ui import ROOT,BUNDLE

earlier=ROOT/'data/study/compartment_279_v1/december_2024_v1/forestguard_279_research.zip'
original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [earlier,BUNDLE]}
with tempfile.TemporaryDirectory(prefix='pair_check_',dir=ROOT/'data/phase2') as temporary:
    folder=Path(temporary)
    with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        result=assess(earlier,BUNDLE,folder/'result')
    assert result['status']=='PASS_DATA_CHECKS' and result['calendar_season_gap_days']==7
    assert result['study_mask_pixels']==13099 and result['common_observable_pixels']==12362
    assert result['observations'][0]['common_pixel_median_ndvi']==.5984
    assert result['observations'][1]['common_pixel_median_ndvi']==.6062
    assert result['forest_area_ha'] is result['forest_loss_ha'] is result['forest_gain_ha'] is None
    page=(folder/'result/comparison.html').read_text(encoding='utf-8')
    assert page.count('data:image/png;base64,')==2 and '94.37%' in page
    assert 'No forest classification' in page and '2024-12-16' in page and '2025-12-09' in page
    with rasterio.open(folder/'result/common_usable.tif') as raster:
        assert raster.shape==(123,172) and raster.res==(20.,20.) and str(raster.crs)=='EPSG:32643'
        assert set(np.unique(raster.read(1)))=={0,1} and int(raster.read(1).sum())==12362
    for before,after,output in [(earlier,BUNDLE,folder/'result'),(BUNDLE,earlier,folder/'reverse'),(BUNDLE,BUNDLE,folder/'same')]:
        try:assess(before,after,output)
        except ValueError:pass
        else:raise AssertionError('Overwrite or invalid date order accepted')
        if output.name!='result':assert not output.exists()
assert original=={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in original}
summary={'status':'PASS','new_real_observation_verified':True,'source_files_verified':[12,27],
         'common_valid_pixels':12362,'same_grid_and_calendar_season_checked':True,
         'offline_assessment_and_overwrite_date_guards_checked':True,'sources_unchanged':True,
         'forest_area_or_change_inferred':False,'phenology_weather_comparability_reviewed':False}
(ROOT/'data/phase2/december_pair_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
