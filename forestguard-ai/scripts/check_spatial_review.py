"""Check mask-only candidate geometry, spacing, deterministic generation and original preservation."""
import hashlib
import json
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom

from prepare_spatial_review import choose,generate,ROOT,OUTPUT,PACK
from review_labels import validate

full=np.ones((100,100),dtype=bool)
assert choose(full)==choose(full.copy())
for grid in [np.zeros((100,100),dtype=bool),np.ones((513,2),dtype=bool),np.ones((100,100),dtype='uint8')]:
    try:choose(grid)
    except ValueError:pass
    else:raise AssertionError('Invalid/empty mask accepted')
original={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [PACK/'reviewer_cases.geojson',ROOT/'data/phase2/compartment_279_dataset_v1/labels.geojson']}
with tempfile.TemporaryDirectory(prefix='spatial_review_check_',dir=ROOT/'data/phase2') as temporary:
    with patch.object(socket,'socket',side_effect=AssertionError('Network forbidden')):
        folder=Path(temporary)/'review';report=generate(folder)
        cases=json.loads((folder/'candidates.geojson').read_bytes())
        with rasterio.open(OUTPUT/'common_usable.tif') as raster:
            common=raster.read(1)==1
            masks=[]
            for feature in cases['features']:
                p=feature['properties']
                assert p['class']=='unknown' and p['split']=='unassigned' and p['reference_independent'] is False
                geom=transform_geom('EPSG:4326',raster.crs,feature['geometry'])
                mask=geometry_mask([geom],raster.shape,raster.transform,invert=True)
                assert int(mask.sum())==25 and (common[mask]).all()
                assert not any((mask&m).any() for m in masks)
                masks.append(mask)
        for i,a in enumerate(report['locations']):
            for b in report['locations'][i+1:]:
                dx=max(0,a['col']-(b['col']+5),b['col']-(a['col']+5))
                dy=max(0,a['row']-(b['row']+5),b['row']-(a['row']+5))
                assert np.hypot(dx,dy)*20>=100
        page=(folder/'form/review.html').read_text(encoding='utf-8')
        assert '100 m footprints' in page and '300 m context' in page and '120 m patch' not in page
        assert 'common clear study masks only' in page and 'Historical WorldCover hints selected' not in page
        exported=json.loads((folder/'form/reviewer_cases.geojson').read_bytes())
        assert validate(exported,folder/'comparison/reviewer_cases.geojson')['class_counts']['unknown']==report['candidate_count']
        try:generate(folder)
        except ValueError:pass
        else:raise AssertionError('Existing candidates overwritten')
assert original=={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in original}
summary={'status':'PASS','real_candidate_count':report['candidate_count'],'common_clear_pixels_per_patch':25,
         'minimum_patch_gap_m':100,'empty_blocks':report['empty_blocks'],'mask_only_selection_checked':True,
         'nonoverlap_geometry_quality_spacing_and_form_checked':True,'offline_generation_checked':True,
         'source_reviews_and_registry_unchanged':True,'labels_or_evaluation_splits_generated':False}
(ROOT/'data/phase2/spatial_review_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
