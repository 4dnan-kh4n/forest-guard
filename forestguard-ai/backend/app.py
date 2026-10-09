"""Local saved-data API. No external inference, tiles or model claims."""
import csv
import hashlib
import hmac
import html
import io
import json
import re
import sqlite3
import secrets
import shutil
import time
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from contextlib import closing, contextmanager
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform_geom
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from inspect_local import inspect
from verify_pair import verify_pair
from verify_bundle import verify
from monthly_demo import build_history
from detect_change import compare as compare_change
from register_research_ui import OUTPUT as RESEARCH_UI, verify_registration

STATE=ROOT/'data/app'
STATE.mkdir(parents=True,exist_ok=True)
app=FastAPI(title='ForestGuard local API',docs_url=None,redoc_url=None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])


@contextmanager
def database():
    # SQLite's transaction context does not close its Windows file handle.
    with closing(sqlite3.connect(STATE/'activity.sqlite')) as connection:
        with connection:
            yield connection


def officer_session(request):
    token=request.cookies.get('forestguard_session','')
    if not token or not (STATE/'activity.sqlite').exists(): return False
    with database() as db:
        db.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, expires REAL)')
        return db.execute('SELECT 1 FROM sessions WHERE token=? AND expires>?',
            (hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone() is not None


@app.middleware('http')
async def require_officer(request,call_next):
    if request.url.path.startswith('/api/') and request.url.path not in {'/api/login','/api/logout','/api/session','/api/health'}:
        if not officer_session(request): return JSONResponse({'detail':'Please sign in to the officer workspace'},status_code=401)
    response=await call_next(request)
    if request.url.path.startswith('/api/'): response.headers['Cache-Control']='no-store'
    return response


@app.post('/api/login')
async def login(request:Request):
    payload=bytearray()
    async for chunk in request.stream():
        payload.extend(chunk)
        if len(payload)>4096: raise HTTPException(413,'Login request too large')
    try: credentials=json.loads(payload)
    except ValueError: raise HTTPException(400,'Invalid login request')
    if (not isinstance(credentials,dict) or credentials.get('district')!='Harda'
            or credentials.get('beat')!='Joga' or not isinstance(credentials.get('password'),str)
            or not hmac.compare_digest(credentials['password'].encode(),b'joga@123')):
        raise HTTPException(401,'Incorrect district, beat or password')
    # ponytail: one loopback demo account; use per-officer accounts before deployment.
    token=secrets.token_urlsafe(32)
    with database() as db:
        db.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, expires REAL)')
        db.execute('DELETE FROM sessions WHERE expires<=?',(time.time(),))
        db.execute('INSERT INTO sessions VALUES (?,?)',(hashlib.sha256(token.encode()).hexdigest(),time.time()+8*3600))
    response=JSONResponse({'authenticated':True,'district':'Harda','beat':'Joga'})
    response.set_cookie('forestguard_session',token,httponly=True,samesite='strict',max_age=8*3600)
    return response


@app.get('/api/session')
def session(request:Request):
    return {'authenticated':officer_session(request),'district':'Harda','beat':'Joga'}


@app.post('/api/logout')
def logout(request:Request):
    token=request.cookies.get('forestguard_session','')
    with database() as db:
        db.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, expires REAL)')
        # Single presentation account: end all of its local sessions on logout.
        db.execute('DELETE FROM sessions')
    response=JSONResponse({'authenticated':False}); response.delete_cookie('forestguard_session')
    return response


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def history(action,dataset,status,detail):
    with database() as db:
        db.execute('CREATE TABLE IF NOT EXISTS activity (id INTEGER PRIMARY KEY, at TEXT, action TEXT, dataset TEXT, status TEXT, detail TEXT)')
        db.execute('INSERT INTO activity(at,action,dataset,status,detail) VALUES(?,?,?,?,?)',
                   (datetime.now(timezone.utc).isoformat(),action,dataset,status,detail))


def catalog():
    items=[]
    if (RESEARCH_UI/'registered.json').exists():
        record=read(RESEARCH_UI/'registered.json')
        items.append(dict(record,folder=RESEARCH_UI,boundary=read(RESEARCH_UI/'boundary.geojson'),boundary_crs='EPSG:4326',
                          views=[dict(v,folder=RESEARCH_UI/v['id']) for v in record['views']]))
    pair=ROOT/'data/phase2/pair_version7'
    if (pair/'pair_report.json').exists():
        report=read(pair/'pair_report.json')
        views=[]
        for i,when in enumerate(report['dates'],1):
            views.append({'id':str(i),'date':when[:10],'name':when[:10],
                'pixels':report['candidate_pixels'],'usable':report['usable_pixels_by_date'][i-1],
                'coverage':report['usable_pixels_by_date'][i-1]/report['candidate_pixels'],
                'forest_ha':None,'folder':pair/f'date_{i}'})
        items.append({'id':'sentinel','title':'Historical pipeline crop · saved observations','kind':'real',
            'subtitle':'Aligned March observations','scope':'Candidate outline · pipeline checks',
            'coverage':report['common_usable_fraction'],'resolution':10,'verified_files':23,
            'version':'pipeline-5f9a7ea39daafa3f','views':views,'folder':pair,
            'boundary':read(pair/'boundary_input.geojson'),'boundary_crs':'EPSG:4326',
            'attribution':'Contains modified Copernicus Sentinel data 2024 and 2025',
            'layers':['imagery','coverage','ndvi']})
    demo=ROOT/'data/demo/fixture_v1'
    if (demo/'manifest.json').exists():
        report=read(demo/'manifest.json'); views=[]
        for sample in report['samples']:
            counts=sample['synthetic_class_counts_inside_split']; total=sum(counts.values())
            views.append({'id':sample['split'],'date':sample['simulated_date'],'name':sample['split'].title(),
                'pixels':total,'usable':counts['0']+counts['1'],'coverage':(counts['0']+counts['1'])/total,
                'forest_ha':counts['1']*.01,'folder':demo/sample['directory']})
        area=read(demo/'assumed_study_area.json')
        items.append({'id':'demo','title':'Synthetic forest sandbox','kind':'synthetic',
            'subtitle':'Generated fixture · seed 42','scope':'Fictional study grid · simulated classes',
            'coverage':None,'resolution':10,'verified_files':20,'version':'synthetic-fixture-v1',
            'views':views,'folder':demo,'boundary':{'type':'Feature','geometry':area['geometry'],'properties':{}},
            'boundary_crs':area['geometry_crs'],'attribution':'Project-generated synthetic data',
            'layers':['imagery','classes','coverage']})
    imports=STATE/'imports'
    if imports.exists():
        for folder in sorted(imports.iterdir()):
            if re.fullmatch(r'import-[a-f0-9]{12}',folder.name) and (folder/'import_complete.json').exists():
                r=read(folder/'report.json'); total=r['study_pixels']; usable=r['usable_pixels']
                items.append({'id':folder.name,'title':r['scene_id'],'kind':'real','subtitle':'Imported saved sample',
                    'scope':r.get('area_label','Research crop'),'coverage':usable/total,'resolution':10,
                    'verified_files':7,'version':folder.name,'folder':folder,'boundary':None,
                    'attribution':r.get('attribution','Saved sample'),'layers':['imagery','coverage'],
                    'views':[{'id':'1','date':r['acquisition'][:10],'name':r['acquisition'][:10],
                        'pixels':total,'usable':usable,'coverage':usable/total,'forest_ha':None,'folder':folder}]})
    return items


def dataset(identity):
    item=next((d for d in catalog() if d['id']==identity),None)
    if item is None: raise HTTPException(404,'Dataset not found')
    return item


def view(item,identity):
    found=next((v for v in item['views'] if v['id']==identity),None)
    if found is None: raise HTTPException(404,'Observation not found')
    return found


def public(item):
    result={k:v for k,v in item.items() if k not in {'folder','boundary','boundary_crs','views'}}
    result['views']=[{k:v for k,v in obs.items() if k!='folder'} for obs in item['views']]
    first=item['views'][0]
    with rasterio.open(first['folder']/'reflectance.tif',driver='GTiff') as raster:
        result.update(width=raster.width,height=raster.height,crs=str(raster.crs),band_order=list(raster.descriptions))
    result['model_version']=None
    return result


def pixel_outline(item,geojson,crs):
    if not isinstance(geojson,dict): raise HTTPException(400,'Use polygon GeoJSON')
    with rasterio.open(item['views'][0]['folder']/'reflectance.tif',driver='GTiff') as raster:
        inverse=~raster.transform; polygons=[]
        features=geojson.get('features',[geojson])
        if not isinstance(features,list) or not features: raise HTTPException(400,'Use polygon GeoJSON')
        for feature in features:
            if not isinstance(feature,dict): raise HTTPException(400,'Use polygon GeoJSON')
            geometry=feature.get('geometry',feature)
            if not isinstance(geometry,dict): raise HTTPException(400,'Use polygon GeoJSON')
            if geometry.get('type') not in {'Polygon','MultiPolygon'}: raise HTTPException(400,'Use polygon GeoJSON')
            coordinates=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
            if not coordinates: raise HTTPException(400,'Empty outline')
            for polygon in coordinates:
                if not polygon: raise HTTPException(400,'Empty polygon')
                for ring in polygon:
                    if not 4<=len(ring)<=5000 or ring[0]!=ring[-1]: raise HTTPException(400,'Use closed polygon rings')
                    for point in ring:
                        if len(point)<2 or not np.isfinite(point[:2]).all(): raise HTTPException(400,'Invalid coordinates')
                        if crs=='EPSG:4326' and (abs(point[0])>180 or abs(point[1])>90): raise HTTPException(400,'Use longitude/latitude coordinates')
            projected=transform_geom(crs,raster.crs,geometry)
            parts=projected['coordinates'] if geometry['type']=='MultiPolygon' else [projected['coordinates']]
            for polygon in parts:
                for ring in polygon:
                    if not 4<=len(ring)<=5000: raise HTTPException(400,'Outline exceeds vertex limit')
                    points=[list(inverse*(p[0],p[1])) for p in ring]
                    if not np.isfinite(points).all(): raise HTTPException(400,'Invalid coordinates')
                    polygons.append(points)
        return polygons


@app.get('/api/health')
def health(): return {'status':'ok','operation':'local stored data','model_connected':False,'change_workflow_connected':True}


CHANGE_FIXTURE=ROOT/'data/phase4/synthetic_change_v1'
CHANGE_INPUTS=['before.tif','after.tif','study_mask.tif']


def change_run(identity):
    if not re.fullmatch(r'change-[a-f0-9]{12}',identity): raise HTTPException(404,'Change run not found')
    folder=STATE/'change_runs'/identity
    if not (folder/'dashboard_complete.json').exists(): raise HTTPException(404,'Change run not found')
    return folder


def change_result(folder):
    with rasterio.open(folder/'result/change.tif') as raster:
        return dict(read(folder/'result/change_report.json'),run_id=folder.name,width=raster.width,height=raster.height)


@app.get('/api/change')
def change_status():
    runs=STATE/'change_runs'
    complete=[f for f in runs.iterdir() if re.fullmatch(r'change-[a-f0-9]{12}',f.name) and (f/'dashboard_complete.json').exists()] if runs.exists() else []
    latest=max(complete,key=lambda f:f.stat().st_mtime_ns) if complete else None
    return {'available':all((CHANGE_FIXTURE/name).exists() for name in CHANGE_INPUTS),
            'source':'synthetic engineering check','real_analysis_ready':False,
            'latest':change_result(latest) if latest else None,
            'missing_requirements':'Reviewed labels, independently evaluated forest model and suitable same-season observations.'}


@app.post('/api/change/run')
def run_change():
    if not all((CHANGE_FIXTURE/name).exists() for name in CHANGE_INPUTS):
        raise HTTPException(409,'Saved synthetic comparison inputs are missing. Run scripts/check_change.py first.')
    identity='change-'+uuid.uuid4().hex[:12]
    folder=STATE/'change_runs'/identity
    folder.mkdir(parents=True)
    try:
        # Only the named project fixture is supported; no arbitrary files/model uploads.
        for name in CHANGE_INPUTS:
            source=CHANGE_FIXTURE/name
            if source.stat().st_size>30*1024**2: raise ValueError('Input crop too large')
            shutil.copyfile(source,folder/name)
        result=compare_change(*(folder/name for name in CHANGE_INPUTS),folder/'result')
        if result['synthetic_fixture'] is not True: raise ValueError('Expected synthetic engineering inputs')
        (folder/'dashboard_complete.json').write_text(json.dumps({'status':'complete','synthetic_fixture':True})+'\n')
    except (OSError,ValueError,KeyError,TypeError,rasterio.errors.RasterioError) as error:
        history('Change comparison',identity,'failed','Saved comparison input validation failed')
        raise HTTPException(400,'Saved comparison failed validation; no completed result published') from error
    history('Change comparison',identity,'passed','Synthetic maps compared over common valid coverage')
    return change_result(folder)


@app.get('/api/change/runs/{identity}/image/{layer}')
def change_image(identity,layer):
    folder=change_run(identity)
    if layer not in {'before','after','change','loss','gain','coverage'}: raise HTTPException(404,'Change layer not found')
    target=folder/(layer+'.png')
    if not target.exists():
        source=folder/(layer+'.tif') if layer in {'before','after'} else folder/'result/change.tif'
        with rasterio.open(source) as raster:
            if raster.width*raster.height>250000: raise HTTPException(400,'Only small crops supported')
            values=raster.read(1,masked=True).filled(255)
            if layer in {'before','after'}:
                with rasterio.open(folder/'study_mask.tif') as study:values[study.read(1)!=1]=255
            rgba=np.zeros((4,*values.shape),dtype='uint8')
            colors={0:(211,186,144),1:(57,125,81)} if layer in {'before','after'} else {0:(211,186,144),1:(57,125,81),2:(207,70,55),3:(34,149,164)}
            if layer=='loss':colors={2:(207,70,55)}
            if layer=='gain':colors={3:(34,149,164)}
            if layer=='coverage':colors={n:(106,151,112) for n in range(4)}
            for label,color in colors.items():
                for channel,value in enumerate(color):rgba[channel,values==label]=value
                rgba[3,values==label]=255
            with rasterio.open(target,'w',driver='PNG',width=raster.width,height=raster.height,count=4,dtype='uint8') as preview:preview.write(rgba)
    return FileResponse(target,media_type='image/png')


@app.get('/api/change/runs/{identity}/report/{format}')
def change_report(identity,format):
    folder=change_run(identity)
    if format in {'json','csv','geotiff'}:
        name,mime={'json':('change_report.json','application/json'),'csv':('transitions.csv','text/csv'),'geotiff':('change.tif','image/tiff')}[format]
        response=FileResponse(folder/'result'/name,media_type=mime,filename='forestguard-synthetic-'+name)
    elif format=='html':
        report=change_result(folder)
        labels={'stable_non_forest':'Stable non-forest','stable_forest':'Stable forest','suspected_loss':'Suspected cover loss','suspected_gain':'Suspected cover gain'}
        rows=''.join(f'<tr><td>{label}</td><td>{report["transition_pixels"][key]}</td><td>{report["transition_area_ha"][key]:.2f}</td></tr>' for key,label in labels.items())
        content=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>ForestGuard change report</title><style>body{{font:16px system-ui;max-width:850px;margin:40px auto;padding:20px;color:#203b31}}table{{border-collapse:collapse}}td,th{{padding:12px;border:1px solid #ddd;text-align:left}}</style><h1>ForestGuard change report</h1><p><strong>SYNTHETIC PIPELINE CHECK — not findings about Joga.</strong></p><p>Simulated dates: {html.escape(report["before_date"])} to {html.escape(report["after_date"])}</p><p>Study mask: {report["study_mask_area_ha"]:.2f} ha. Common observable area: {report["observable_area_ha"]:.2f} ha ({report["common_coverage_fraction"]*100:.2f}%).</p><table><tr><th>Transition</th><th>Pixels</th><th>Hectares</th></tr>{rows}</table><p>Model: {html.escape(report["model_version"])}. Study: {html.escape(report["study_area_version"])}.</p><p>{html.escape(report["limits"])}</p><p>Fire risk and real forest accuracy have not been evaluated.</p></html>'
        response=Response(content,media_type='text/html',headers={'Content-Disposition':'attachment; filename="forestguard-synthetic-change.html"'})
    else:raise HTTPException(404,'Change report format not supported')
    history('Change report exported',identity,'passed',format.upper()+' synthetic change report')
    return response


def monthly_history():
    path=ROOT/'data/demo/forest_fire_history_demo_v1.json'
    result=read(path) if path.exists() else build_history()
    if result.get('schema')!='forestguard-synthetic-history-v1' or len(result.get('months',[]))!=60:
        raise HTTPException(500,'Monthly demonstration data is incomplete')
    return result


@app.get('/api/reports/monthly-demo')
def monthly_demo_report(): return monthly_history()


@app.get('/api/reports/monthly-demo.csv')
def monthly_demo_csv():
    rows=monthly_history()['months']; buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return Response(buffer.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="forestguard-simulated-monthly-history.csv"'})


@app.get('/api/datasets')
def datasets(): return [public(d) for d in catalog()]


@app.get('/api/activity')
def activity():
    if not (STATE/'activity.sqlite').exists(): return []
    with database() as db:
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='activity'").fetchone() is None:
            return []
        db.row_factory=sqlite3.Row
        return [dict(r) for r in db.execute('SELECT * FROM activity ORDER BY id DESC LIMIT 20')]


@app.get('/api/datasets/{identity}/outline')
def outline(identity):
    item=dataset(identity)
    return {'rings':pixel_outline(item,item['boundary'],item['boundary_crs']) if item['boundary'] else []}


@app.post('/api/datasets/{identity}/boundary')
async def import_boundary(identity,request:Request):
    payload=bytearray()
    async for chunk in request.stream():
        payload.extend(chunk)
        if len(payload)>1024**2: raise HTTPException(413,'Boundary limit is 1 MiB')
    try:
        geojson=json.loads(payload)
        rings=pixel_outline(dataset(identity),geojson,'EPSG:4326')
    except (ValueError,KeyError,TypeError,IndexError,rasterio.errors.RasterioError) as error:
        raise HTTPException(400,'Could not read polygon GeoJSON') from error
    return {'rings':rings,'use':'display-only imported outline'}


@app.get('/api/datasets/{identity}/{observation}/image/{layer}')
def image(identity,observation,layer):
    item=dataset(identity); obs=view(item,observation)
    if layer not in item['layers']: raise HTTPException(404,'Layer not available')
    if layer=='imagery': return FileResponse(obs['folder']/'preview.png',media_type='image/png')
    if layer=='ndvi':
        values,valid,profile=vegetation(item,obs)
        target=STATE/'previews'/f'{identity}-{observation}-ndvi.png'
        target.parent.mkdir(exist_ok=True)
        rgba=np.zeros((4,*values.shape),dtype='uint8')
        level=np.clip((values+1)/2,0,1)
        rgba[0]=(190*(1-level)).astype('uint8'); rgba[1]=(70+140*level).astype('uint8')
        rgba[2]=(65+15*level).astype('uint8'); rgba[3,valid]=255
        with rasterio.open(target,'w',driver='PNG',height=profile['height'],width=profile['width'],count=4,dtype='uint8') as saved: saved.write(rgba)
        return FileResponse(target,media_type='image/png')
    source=obs['folder']/('labels.tif' if layer=='classes' else item.get('usable_filename','usable.tif'))
    if layer=='coverage' and (identity=='sentinel' or item.get('common_mask')): source=item['folder']/'common_usable.tif'
    target=STATE/'previews'/f'{identity}-{observation}-{layer}-{source.stat().st_mtime_ns}.png'
    if not target.exists():
        target.parent.mkdir(exist_ok=True)
        with rasterio.open(source,driver='GTiff') as raster:
            if max(raster.shape)>512: raise HTTPException(400,'Only small crops supported')
            values=raster.read(1); rgba=np.zeros((4,*raster.shape),dtype='uint8')
            if layer=='classes':
                for cls,color in [(0,(212,183,136)),(1,(66,150,101))]:
                    for channel,value in enumerate(color): rgba[channel,values==cls]=value
                    rgba[3,values==cls]=255
            else:
                for channel,value in enumerate([103,189,154]): rgba[channel,values==1]=value
                rgba[3,values==1]=255
            with rasterio.open(target,'w',driver='PNG',height=raster.height,width=raster.width,
                               count=4,dtype='uint8',transform=raster.transform,crs=raster.crs) as saved: saved.write(rgba)
    return FileResponse(target,media_type='image/png')


def vegetation(item,obs):
    with rasterio.open(obs['folder']/'reflectance.tif',driver='GTiff') as raster:
        if max(raster.shape)>512: raise HTTPException(400,'Only small crops supported')
        red,nir=raster.read([raster.descriptions.index('B04')+1,raster.descriptions.index('B08')+1]); profile=raster.profile
        valid=np.isfinite(red)&np.isfinite(nir)&(red!=raster.nodata)&(nir!=raster.nodata)&(np.abs(nir+red)>1e-6)
    with rasterio.open(obs['folder']/item.get('usable_filename','usable.tif')) as quality: valid &= quality.read(1)==1
    study= item['folder']/'common_usable.tif' if item['id']=='sentinel' or item.get('common_mask') else obs['folder']/('split_mask.tif' if item['kind']=='synthetic' else item.get('study_filename','study.tif'))
    with rasterio.open(study) as area: valid &= area.read(1)==1
    ndvi=np.zeros(red.shape,dtype='float32'); np.divide(nir-red,nir+red,out=ndvi,where=valid)
    return np.clip(ndvi,-1,1),valid,profile


@app.post('/api/datasets/{identity}/analyze')
def analyze(identity):
    item=dataset(identity); observations=[]
    for obs in item['views']:
        values,valid,_=vegetation(item,obs)
        if not valid.any(): raise HTTPException(400,'No usable observations')
        observations.append({'date':obs['date'],'valid_pixels':int(valid.sum()),
            'median_ndvi':round(float(np.median(values[valid])),4),
            'vegetation_signal_percent':round(float((values[valid]>.35).mean()*100),2)})
    result={'method':'NDVI = (B08 − B04) / (B08 + B04)','kind':item['kind'],'observations':observations,
        'interpretation':'Vegetation indicator; not forest classification or verified forest loss.'}
    if item.get('limits'):result['interpretation']+=' '+item['limits']
    if identity=='sentinel': result['median_ndvi_difference']=round(observations[1]['median_ndvi']-observations[0]['median_ndvi'],4)
    history('Imagery analyzed',identity,'passed','Stored reflectance vegetation indicators calculated')
    return result


@app.post('/api/datasets/{identity}/validate')
def validate(identity):
    item=dataset(identity)
    try:
        if identity=='compartment-279':
            result=verify_registration(item['folder']);detail=f"{result['registered_files']} registered files and {result['source_files_verified']} source hashes verified"
        elif identity=='sentinel':
            result=verify_pair(item['folder']); detail=f"{result['verified_files']} hashes and common coverage verified"
        elif identity=='demo':
            manifest=read(item['folder']/'checksums.json')
            for name,record in manifest.items():
                path=(item['folder']/name).resolve()
                if not path.is_relative_to(item['folder'].resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
                    raise ValueError('Synthetic file integrity failure')
            detail=f'{len(manifest)} synthetic fixture hashes verified'
        else:
            result=inspect(item['folder']); detail='Saved sample hashes, grids and masks verified'
        history('Data check',identity,'passed',detail)
        return {'status':'passed','detail':detail}
    except (OSError,ValueError,KeyError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        history('Data check',identity,'failed','Stored input validation failed')
        raise HTTPException(400,'Stored input validation failed') from error


@app.post('/api/import')
async def import_sample(request:Request):
    payload=bytearray()
    async for chunk in request.stream():
        payload.extend(chunk)
        if len(payload)>10*1024**2: raise HTTPException(413,'Sample ZIP limit is 10 MiB')
    uploads=STATE/'uploads'; uploads.mkdir(exist_ok=True)
    source=uploads/f'{uuid.uuid4().hex}.zip'; source.write_bytes(payload)
    identity='import-'+hashlib.sha256(payload).hexdigest()[:12]
    folder=STATE/'imports'/identity
    try:
        verify(source)
        if not folder.exists():
            folder.mkdir(parents=True)
            (folder/'forestguard_phase0.zip').write_bytes(payload)
            with zipfile.ZipFile(source) as archive:
                for name in archive.namelist(): (folder/name).write_bytes(archive.read(name))
        inspect(folder)
        (folder/'import_complete.json').write_text(json.dumps({'status':'validated','id':identity}))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        raise HTTPException(400,'Use a valid exported forestguard_phase0.zip sample') from error
    history('Sample imported',identity,'passed','Saved crop imported and checked')
    return public(dataset(identity))


@app.get('/api/datasets/{identity}/report/{format}')
def report(identity,format):
    original=dataset(identity); item=public(original)
    rows=[{'dataset':item['title'],'data_kind':item['kind'],
        'date_type':'simulated' if item['kind']=='synthetic' else 'acquired',
        'date':v['date'],'total_pixels':v['pixels'],'usable_pixels':v['usable'],
        'coverage_percent':round(v['coverage']*100,4),'scene_id':v.get('scene_id',''),
        'study_version':item.get('study_area_version',''),'resolution_m':item['resolution'],
        'dataset_version':item['version'],'crs':item['crs'],'band_order':'|'.join(item['band_order']),
        'source_license_url':v.get('source_license_url',''),
        'source_bundle_sha256':item.get('source_sha256',{}).get('bundle',''),
        'limits':item.get('limits',''),
        'simulated_forest_ha':v['forest_ha'] if item['kind']=='synthetic' else ''} for v in item['views']]
    for row,obs in zip(rows,original['views']):
        values,valid,_=vegetation(original,obs)
        row['ndvi_median']=round(float(np.median(values[valid])),4) if valid.any() else ''
        row['ndvi_valid_pixels']=int(valid.sum())
    if format=='csv':
        buffer=io.StringIO(); writer=csv.DictWriter(buffer,fieldnames=list(rows[0])); writer.writeheader()
        for row in rows:
            writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in row.items()})
        content=buffer.getvalue(); mime='text/csv'
    elif format=='html':
        columns=['date','date_type','total_pixels','usable_pixels','coverage_percent','ndvi_median']
        if item['kind']=='synthetic':columns.append('simulated_forest_ha')
        cells=''.join('<tr>'+''.join(f'<td>{html.escape(str(row[k]))}</td>' for k in columns)+'</tr>' for row in rows)
        headers=''.join(f'<th>{html.escape(k)}</th>' for k in columns)
        content=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>ForestGuard report</title><style>body{{font:16px system-ui;margin:48px;color:#193d31}}table{{border-collapse:collapse}}td,th{{padding:12px;border:1px solid #ddd;text-align:left}}small{{color:#68776e}}</style><h1>ForestGuard AI</h1><h2>{html.escape(item["title"])}</h2><p>{html.escape(item["scope"])}</p><table><thead>{headers}</thead><tbody>{cells}</tbody></table><p>Data kind: {item["kind"]}. Coverage is imagery/label observability, not model accuracy. No trained model is connected.</p><small>{html.escape(item["attribution"])}</small></html>'
        mime='text/html'
        provenance={k:rows[0][k] for k in ['dataset_version','study_version','crs','resolution_m','band_order','source_bundle_sha256','limits']}
        provenance['observations']=[{k:r[k] for k in ['date','scene_id','source_license_url']} for r in rows]
        content=content.replace('</html>','<h3>Source and processing metadata</h3><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+html.escape(json.dumps(provenance,indent=2))+'</pre></html>')
    else: raise HTTPException(404,'Report format not supported')
    history('Report exported',identity,'passed',format.upper()+' report')
    return Response(content,media_type=mime,headers={'Content-Disposition':f'attachment; filename="forestguard-{identity}.{format}"'})


DIST=ROOT/'frontend/dist'
if DIST.exists(): app.mount('/',StaticFiles(directory=DIST,html=True),name='frontend')
