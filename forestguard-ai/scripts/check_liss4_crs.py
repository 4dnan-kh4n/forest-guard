"""Regression: accept supplier WGS84 rounding, reject different zones/hemispheres."""
import sys
from pathlib import Path
from rasterio.crs import CRS
from rasterio.warp import transform
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cloud'))
from liss4_reference_crop import accepted_liss4_crs

supplier = CRS.from_dict(proj='utm', zone=43, a=6378137, rf=298.25722293287, units='m')
assert supplier.to_epsg() is None
assert accepted_liss4_crs(supplier) and accepted_liss4_crs(CRS.from_epsg(32643))
assert not accepted_liss4_crs(None)
assert not accepted_liss4_crs(CRS.from_epsg(32644))
assert not accepted_liss4_crs(CRS.from_epsg(32743))
assert not accepted_liss4_crs(CRS.from_dict(proj='utm', zone=43, a=6378137, rf=298.26, units='m'))
lon, lat = [76.78831, 76.82120], [22.39153, 22.41332]
x, y = transform('EPSG:4326', supplier, lon, lat)
u, v = transform('EPSG:4326', 'EPSG:32643', lon, lat)
assert max(abs(a-b) for a,b in zip(x+y,u+v)) < 0.001
with MemoryFile() as memory:
    with memory.open(driver='GTiff', width=2, height=2, count=1, dtype='uint16',
                     crs='EPSG:32643', transform=from_origin(684000,2480000,5,5)) as saved:
        saved.write(np.ones((1,2,2), dtype='uint16'))
    with memory.open() as saved:
        assert saved.crs.to_epsg() == 32643 and saved.res == (5., 5.)
print('PASS: rounded supplier ellipsoid; wrong zone, hemisphere and ellipsoid rejected; corner differences below 1 mm.')
