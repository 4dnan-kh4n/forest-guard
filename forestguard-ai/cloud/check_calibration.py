"""Compare one bounded blue-band crop with the provider's Collection 1."""
from urllib.request import Request, urlopen
import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds

assert Path('/kaggle/working').is_dir() or Path('/content').is_dir(), 'Hosted runtime required'
query = {'collections':['sentinel-2-c1-l2a'], 'bbox':[76.785,22.413,76.805,22.433],
         'datetime':'2025-03-29T00:00:00Z/2025-03-29T23:59:59Z', 'limit':5}
request = Request('https://earth-search.aws.element84.com/v1/search',
                  data=json.dumps(query).encode(), headers={'Content-Type':'application/json'})
with urlopen(request, timeout=30) as response:
    result = json.load(response)
out = Path('/kaggle/working' if Path('/kaggle/working').is_dir() else '/content')/'forestguard_calibration'
out.mkdir(exist_ok=True)
(out/'c1_candidates.json').write_text(json.dumps(result,indent=2))
diagnostics = []
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='60', GDAL_CACHEMAX=64*1024**2):
    for candidate in result['features']:
        if candidate['properties']['platform'] != 'sentinel-2c':
            continue
        asset = candidate['assets']['blue']
        if not asset['href'].startswith('https://') or asset.get('storage:requester_pays',False):
            continue
        calibration = asset['raster:bands'][0]
        with rasterio.open(asset['href']) as image:
            bounds = transform_bounds('EPSG:4326',image.crs,76.785,22.413,76.805,22.433)
            window = from_bounds(*bounds,transform=image.transform).round_offsets().round_lengths()
            assert max(window.height,window.width)<=512
            raw = image.read(1,window=window,masked=True).compressed()
            assert raw.size
            record = {'id':candidate['id'], 'date':candidate['properties']['datetime'],
                'source_product':candidate['properties'].get('s2:product_uri'),
                'asset':asset,'header_scales':image.scales,'header_offsets':image.offsets,
                'raw_quantiles':np.quantile(raw,[0,.01,.5,.99,1]).tolist(),
                'reflectance_quantiles':np.quantile(raw.astype('float32')*calibration['scale']+
                    calibration.get('offset',0),[0,.01,.5,.99,1]).tolist()}
            diagnostics.append(record)
(out/'comparison.json').write_text(json.dumps(diagnostics,indent=2))
print('Collection 1 calibration diagnostic:', json.dumps(diagnostics,indent=2))
print('This is a cross-source calibration check, not forest ground truth.')
