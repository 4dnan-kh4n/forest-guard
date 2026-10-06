"""Build a two-date cloud pipeline check; no labels, training or change claims."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
source=(root/'cloud/inspect_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
candidate=root/'data/reference/handia_working_plan_2022_2032/joga_278.candidate.geojson'
review=r'''
if BOUNDARY is None:
    raise RuntimeError('Supply the pipeline-check candidate in a private notebook.')
assert BOUNDARY['features'][0]['properties']['pilot_approved'] is False
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
import matplotlib.pyplot as plt
from PIL import Image
scene_ids=['S2A_T43QFE_20240321T053116_L2A','S2A_T43QFE_20250328T052953_L2A']
outputs=[run(bbox=BOUNDARY['bbox'],area_label='Joga 278 candidate: pipeline checks only',scene_id=scene) for scene in scene_ids]
pair=Path('/kaggle/working/forestguard_phase2') if Path('/kaggle/working').exists() else Path('/content/forestguard_phase2')
pair.mkdir(exist_ok=True)
reports=[json.loads((p/'report.json').read_text()) for p in outputs]
for key in ['shape','crs','transform','band_order','resolution_m']:
    assert reports[0][key]==reports[1][key],f'Dates are not aligned: {key}'
with rasterio.open(outputs[0]/'reflectance.tif') as ref:
    geometry=transform_geom('EPSG:4326',ref.crs,BOUNDARY['features'][0]['geometry'])
    inside=geometry_mask([geometry],out_shape=ref.shape,transform=ref.transform,invert=True,all_touched=False)
    profile=ref.profile.copy(); profile.update(count=1,dtype='uint8',nodata=None)
    grid=ref.transform
masks=[]
for output in outputs:
    with rasterio.open(output/'usable.tif') as raster:
        assert raster.transform==grid
        masks.append(raster.read(1).astype(bool)&inside)
common=masks[0]&masks[1]
assert common.any(), 'No common usable candidate coverage'
for name,mask in [('candidate_mask',inside),('common_usable',common)]:
    with rasterio.open(pair/f'{name}.tif','w',**profile) as dst: dst.write(mask.astype('uint8'),1)
    with rasterio.open(pair/f'{name}.tif') as saved: assert np.array_equal(saved.read(1),mask)
fig,axes=plt.subplots(1,2,figsize=(12,6))
inverse=~grid
for ax,output,report in zip(axes,outputs,reports):
    ax.imshow(Image.open(output/'preview.png'))
    for polygon in geometry['coordinates']:
        for ring in polygon:
            pixels=np.asarray([inverse*(x,y) for x,y in ring])
            ax.plot(pixels[:,0]-.5,pixels[:,1]-.5,color='yellow',linewidth=1)
    ax.set_title(report['acquisition'][:10]); ax.set_xlabel('10 m raster column'); ax.set_ylabel('10 m raster row')
fig.suptitle('Aligned observations: pipeline checks only; no forest/change labels')
fig.tight_layout(); fig.savefig(pair/'pair_preview.png',dpi=120)
plt.show(); plt.close(fig)
report={'dataset_role':'pipeline checks only','scene_ids':scene_ids,'dates':[r['acquisition'] for r in reports],
    'shape':reports[0]['shape'],'crs':reports[0]['crs'],'transform':reports[0]['transform'],
    'band_order':reports[0]['band_order'],'candidate_pixels':int(inside.sum()),
    'usable_pixels_by_date':[int(m.sum()) for m in masks],
    'common_usable_pixels':int(common.sum()),'common_usable_fraction':float(common.sum()/inside.sum()),
    'quality_rule':reports[0]['quality_rule'],'grid_alignment':'PASS',
    'source_boundary_sha256':BOUNDARY['features'][0]['properties']['source_sha256'],
    'pilot_approved':False,'reviewed_label_count':0,'splits_frozen':False,'model_trained':False,
    'forest_loss_ha':None,'forest_gain_ha':None,
    'attribution':[r['attribution'] for r in reports],
    'seasonal_note':'Both March observations; similar calendar season does not guarantee identical phenology or water level.'}
(pair/'pair_report.json').write_text(json.dumps(report,indent=2))
(pair/'boundary_input.geojson').write_text(json.dumps(BOUNDARY,indent=2))
bundle=pair/'phase2_pair.zip'
manifest={}
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
    for i,output in enumerate(outputs):
        for name in ['forestguard_phase0.zip','source.json','report.json','reflectance.tif','scl.tif','study.tif','usable.tif','preview.png','checksums.json']:
            dest=f'date_{i+1}/{name}'
            archive.write(output/name,arcname=dest)
            manifest[dest]={'sha256':hashlib.sha256((output/name).read_bytes()).hexdigest(),'bytes':(output/name).stat().st_size}
    for name in ['pair_report.json','boundary_input.geojson','candidate_mask.tif','common_usable.tif','pair_preview.png']:
        archive.write(pair/name,arcname=name)
        manifest[name]={'sha256':hashlib.sha256((pair/name).read_bytes()).hexdigest(),'bytes':(pair/name).stat().st_size}
    archive.writestr('pair_checksums.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(bundle) as archive:
    assert archive.testzip() is None
    for name,record in manifest.items(): assert hashlib.sha256(archive.read(name)).hexdigest()==record['sha256']
print(json.dumps(report,indent=2)); print('Verified pair ZIP:',bundle,'bytes',bundle.stat().st_size)
'''
for path,boundary in [(root/'notebooks/03_two_date_data.ipynb',None),(candidate.parent/'03_two_date_data.private.ipynb',json.loads(candidate.read_text()))]:
    cells=[{'id':'purpose','cell_type':'markdown','metadata':{},'source':['# Phase 2 two-date pipeline dataset\n','Private hosted CPU. Internet On, Accelerator None. No labels or training.\n']}]
    for key,code in [('boundary','BOUNDARY = '+repr(boundary)+'\n'),('pipeline',source),('pair',review)]:
        compile(code,str(path),'exec')
        cells.append({'id':key,'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':code.splitlines(keepends=True)})
    path.write_text(json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}},'cells':cells},indent=2)+'\n',encoding='utf-8')
print('PASS: two-date notebook template/private copy compile; source outputs empty.')
