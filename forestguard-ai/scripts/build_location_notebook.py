"""Build a safe template and a Git-ignored execution copy for private site review."""
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
source=(root/'cloud/inspect_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
candidate_path=root/'reports/joga_records/coordinate_candidates.json'
candidate=json.loads(candidate_path.read_text(encoding='utf-8'))
points=[{'label':p['label'],'latitude':p['latitude_decimal'],'longitude':p['longitude_decimal']}
        for p in candidate['points']]
margin=.004
bbox=[math.floor((min(p['longitude'] for p in points)-margin)*1000)/1000,
      math.floor((min(p['latitude'] for p in points)-margin)*1000)/1000,
      math.ceil((max(p['longitude'] for p in points)+margin)*1000)/1000,
      math.ceil((max(p['latitude'] for p in points)+margin)*1000)/1000]
settings={'bbox':bbox,'points':points,'scene_id':'S2A_T43QFE_20250328T052953_L2A',
    'area_label':'Historical Salyakhedi 320 PF proposed planting-site vicinity; not Joga beat boundary',
    'source_datum':None,'plot_datum_assumption':'EPSG:4326 solely for exploratory comparison; not verified',
    'reviewed_labels_exist':False,'official_boundary_verified':False}
review_code=r"""
if LOCATION_SETTINGS is None:
    raise RuntimeError('Supply authorized site-review settings in this private notebook before running.')
output = run(bbox=LOCATION_SETTINGS['bbox'],area_label=LOCATION_SETTINGS['area_label'],scene_id=LOCATION_SETTINGS['scene_id'])
import matplotlib.pyplot as plt
from rasterio.warp import transform as project_points
from PIL import Image
import numpy as np
import rasterio
report=json.loads((output/'report.json').read_text())
with rasterio.open(output/'reflectance.tif') as raster:
    fig,ax=plt.subplots(figsize=(7,7))
    ax.imshow(Image.open(output/'preview.png'))
    points=LOCATION_SETTINGS['points']
    x,y=project_points('EPSG:4326',raster.crs,
        [p['longitude'] for p in points],[p['latitude'] for p in points])
    inverse=~raster.transform
    for point,px,py in zip(points,x,y):
        col,row=inverse*(px,py)
        assert 0<=col<raster.width and 0<=row<raster.height,'Candidate point outside crop'
        ax.plot(col-.5,row-.5,'o',color='yellow',markeredgecolor='black')
        ax.annotate(point['label'],(col-.5,row-.5),xytext=(5,5),textcoords='offset points',
                    color='yellow',bbox={'facecolor':'black','alpha':.6,'pad':2})
    ax.set_title('Historical GPS candidates on '+report['acquisition'][:10]+' imagery\n'
                 'Datum assumed for review; no boundary or forest labels')
    ax.set_xlabel('10 m raster column'); ax.set_ylabel('10 m raster row')
    fig.tight_layout()
    fig.savefig(output/'location_review.png',dpi=150)
    plt.show(); plt.close(fig)
    valid=raster.read(4)!=raster.nodata
    with rasterio.open(output/'scl.tif') as quality:
        report['usable_land_pixels']=int((valid & np.isin(quality.read(1),[4,5])).sum())
(output/'location_settings.json').write_text(json.dumps(LOCATION_SETTINGS,indent=2))
(output/'location_review.json').write_text(json.dumps(report,indent=2))
# Keep the independently verified sample ZIP and add the site-review evidence separately.
with zipfile.ZipFile(output/'location_review.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for name in ['location_settings.json','location_review.json','location_review.png']:
        archive.write(output/name,arcname=name)
print('Site-review export:',output/'location_review.zip')
print('Usable land pixels (quality only, not forest):',report['usable_land_pixels'])
"""

def notebook(configuration):
    return {'nbformat':4,'nbformat_minor':5,
        'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},
        'cells':[
            {'id':'purpose','cell_type':'markdown','metadata':{},'source':[
                '# ForestGuard AI — provisional location review\n',
                'Private hosted CPU notebook. Internet On, Accelerator None.\n',
                'Historical proposed-site coordinates have unverified datum/order.\n',
                'Points are displayed for review only. No polygon or forest labels are generated.\n']},
            {'id':'settings','cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
             'source':('LOCATION_SETTINGS = '+repr(configuration)+'\n').splitlines(keepends=True)},
            {'id':'pipeline','cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
             'source':source.splitlines(keepends=True)},
            {'id':'review','cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
             'source':review_code.splitlines(keepends=True)}]}

template=root/'notebooks/01_location_review.ipynb'
private_copy=root/'reports/joga_records/01_location_review.private.ipynb'
for path,configuration in [(template,None),(private_copy,settings)]:
    document=notebook(configuration)
    for cell in document['cells']:
        if cell['cell_type']=='code':compile(''.join(cell['source']),str(path),'exec')
    path.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
print('PASS: template/private notebook syntax; template has no private coordinates.')
print('Research bbox:',bbox,'Private run copy:',private_copy)
