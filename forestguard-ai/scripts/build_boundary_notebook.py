"""Build a cloud-only candidate/imagery check, preserving pipeline-only status."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root/'cloud/inspect_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
candidate = root/'data/reference/handia_working_plan_2022_2032/joga_278.candidate.geojson'
review = r'''
if BOUNDARY is None:
    raise RuntimeError('Supply the authorized pipeline-check candidate in a private notebook.')
feature = BOUNDARY['features'][0]
assert feature['properties']['pilot_approved'] is False
output = run(bbox=BOUNDARY['bbox'], area_label='Joga 278 candidate: pipeline checks only; not approved study area',
             scene_id='S2A_T43QFE_20250328T052953_L2A')
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from PIL import Image
report = json.loads((output/'report.json').read_text())
with rasterio.open(output/'reflectance.tif') as raster:
    geometry = transform_geom('EPSG:4326', raster.crs, feature['geometry'])
    inside = geometry_mask([geometry], out_shape=raster.shape, transform=raster.transform,
                           invert=True, all_touched=False)
    assert inside.any()
    valid = raster.read(4) != raster.nodata
    usable = inside & valid
    profile = raster.profile.copy()
    profile.update(count=1, dtype='uint8', nodata=None)
    with rasterio.open(output/'boundary_mask.tif', 'w', **profile) as dst:
        dst.write(inside.astype('uint8'),1)
    with rasterio.open(output/'boundary_mask.tif') as saved:
        assert saved.transform == raster.transform and saved.crs == raster.crs
        assert np.array_equal(saved.read(1),inside)
    fig,ax = plt.subplots(figsize=(7,7))
    ax.imshow(Image.open(output/'preview.png'))
    inverse = ~raster.transform
    area_m2, perimeter_m = 0., 0.
    for polygon in geometry['coordinates']:
        for index,ring in enumerate(polygon):
            points = np.asarray(ring)[:,:2]
            shifted = points-points[0]
            signed = .5*np.sum(shifted[:-1,0]*shifted[1:,1]-shifted[1:,0]*shifted[:-1,1])
            area_m2 += abs(signed)*(1 if index == 0 else -1)
            perimeter_m += np.linalg.norm(np.diff(points,axis=0),axis=1).sum()
            pixels = np.asarray([inverse*(x,y) for x,y in points])
            ax.plot(pixels[:,0]-.5,pixels[:,1]-.5,color='yellow',linewidth=1.2)
    assert area_m2 > 0
    pixel_area_m2 = abs(raster.transform.a*raster.transform.e)
    raster_area_m2 = int(inside.sum())*pixel_area_m2
    assert abs(raster_area_m2-area_m2) <= perimeter_m*10, 'Rasterized area exceeds boundary-pixel tolerance'
    ax.set_title('Official-source Joga 278 candidate on 2025-03-28 imagery\nPipeline check only; no forest labels or boundary approval')
    ax.set_xlabel('10 m raster column'); ax.set_ylabel('10 m raster row')
    fig.tight_layout(); fig.savefig(output/'boundary_overlay.png',dpi=150)
    plt.show(); plt.close(fig)
    report.update(candidate_pixels=int(inside.sum()),candidate_usable_pixels=int(usable.sum()),
        candidate_usable_fraction=float(usable.sum()/inside.sum()),
        candidate_geometric_area_ha=float(area_m2/10000),candidate_pixel_area_ha=float(raster_area_m2/10000),
        candidate_perimeter_m=float(perimeter_m),source_area_attribute_ha=feature['properties']['AREA_HA'],
        historical_area_attribute_ha=580.770,area_kind='candidate geometry/coverage; not forest area or beat totals',
        polygon_mask_rule='pixel centers; all_touched=False',pilot_approved=False,
        current_beat_boundary_verified=False,positional_accuracy_measured=False,
        label_feasibility='Requires independent dated review; no forest classes assigned',
        boundary_source_sha256=feature['properties']['source_sha256'],
        matplotlib_version=importlib.metadata.version('matplotlib'))
(output/'boundary_input.geojson').write_text(json.dumps(BOUNDARY,indent=2))
(output/'boundary_review.json').write_text(json.dumps(report,indent=2))
names = ['boundary_input.geojson','boundary_mask.tif','boundary_overlay.png','boundary_review.json']
manifest = {name:{'bytes':(output/name).stat().st_size,'sha256':hashlib.sha256((output/name).read_bytes()).hexdigest()} for name in names}
(output/'boundary_checksums.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(output/'boundary_review.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for name in names+['boundary_checksums.json']:
        archive.write(output/name,arcname=name)
with zipfile.ZipFile(output/'boundary_review.zip') as archive:
    assert archive.testzip() is None
    for name,record in manifest.items():
        assert hashlib.sha256(archive.read(name)).hexdigest()==record['sha256']
print(json.dumps(report,indent=2))
print('Verified boundary-check export:',output/'boundary_review.zip')
'''
for path, boundary in [(root/'notebooks/02_boundary_check.ipynb',None),
                       (candidate.parent/'02_boundary_check.private.ipynb',json.loads(candidate.read_text()))]:
    cells = [{'id':'purpose','cell_type':'markdown','metadata':{},'source':[
        '# Joga candidate boundary pipeline check\n',
        'Private Kaggle CPU. Internet On. No model training, labels or study-area approval.\n']}]
    for cell_id,code in [('boundary','BOUNDARY = '+repr(boundary)+'\n'),('pipeline',source),('review',review)]:
        compile(code,str(path),'exec')
        cells.append({'id':cell_id,'cell_type':'code','metadata':{},'source':code.splitlines(keepends=True),
                      'outputs':[],'execution_count':None})
    document={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}},'cells':cells}
    path.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
print('PASS: public template/private execution copy compile; no saved notebook outputs.')
