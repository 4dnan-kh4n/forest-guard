"""Exercise hosted authentication and existing features without an external service."""
import asyncio
import hashlib
import json
import os
import socket
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ['VERCEL']='1'
os.environ['FORESTGUARD_SESSION_SECRET']='test-only-'+('x'*48)
os.environ['FORESTGUARD_ALLOWED_HOSTS']='forestguard-test.vercel.app'
from backend import hosting
os.environ['FORESTGUARD_OFFICERS']=json.dumps([
    {'id':name,'district':'Harda','beat':'Joga','password_hash':hosting.password_hash('test-only-'+name)}
    for name in ['officer-a','officer-b']])
from backend import app as api


async def check():
    cookie='';calls=0
    async def request(path,payload=None,status=200,origin=None,host='forestguard-test.vercel.app'):
        nonlocal cookie,calls
        body=b'' if payload is None else payload if isinstance(payload,bytes) else json.dumps(payload).encode()
        headers=[(b'host',host.encode()),(b'content-type',b'application/json'),(b'cookie',cookie.encode())]
        if origin:headers.append((b'origin',origin.encode()))
        scope={'type':'http','asgi':{'version':'3.0','spec_version':'2.4'},'http_version':'1.1',
               'method':'GET' if payload is None else 'POST','scheme':'https','path':path,
               'raw_path':path.encode(),'query_string':b'','root_path':'','headers':headers,
               'client':('127.0.0.1',12345),'server':(host,443)}
        messages=[];delivered=False;completed=asyncio.Event()
        async def receive():
            nonlocal delivered
            if not delivered:delivered=True;return {'type':'http.request','body':body,'more_body':False}
            await completed.wait();return {'type':'http.disconnect'}
        async def send(message):
            messages.append(message)
            if message['type']=='http.response.body' and not message.get('more_body',False):completed.set()
        await asyncio.wait_for(api.app(scope,receive,send),30)
        start=next(m for m in messages if m['type']=='http.response.start')
        assert start['status']==status,(path,start['status'])
        for key,value in start['headers']:
            if key==b'set-cookie':cookie=value.decode().split(';')[0]
        calls+=1
        return b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body'),dict(start['headers'])

    with tempfile.TemporaryDirectory(prefix='hosted_check_',dir=ROOT/'data/phase5') as temporary:
        state=Path(temporary)/'state';state.mkdir()
        with patch.object(api,'STATE',state),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect_ex',side_effect=AssertionError('Network forbidden')),patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')):
            body,headers=await request('/')
            assert headers[b'cache-control']==b'no-store' and b'id="root"' in body
            await request('/api/datasets',status=401)
            await request('/api/research/change',status=401)
            await request('/api/fire',status=401)
            await request('/api/forest-history',status=401)
            credentials={'district':'Harda','beat':'Joga','password':'wrong'}
            await request('/api/login',credentials,status=401)
            credentials['password']='test-only-officer-a'
            await request('/api/login',credentials,status=403,origin='https://other.invalid')
            await request('/api/health',host='evil.invalid',status=400)
            body,headers=await request('/api/login',credentials)
            assert 'Secure' in headers[b'set-cookie'].decode() and 'HttpOnly' in headers[b'set-cookie'].decode()
            first_cookie=cookie;token=cookie.split('=',1)[1];current=hosting.session(token)
            assert current['id']=='officer-a' and hosting.session(token+'bad') is None
            with patch.object(hosting.time,'time',return_value=current['expires']+1):assert hosting.session(token) is None
            body,_=await request('/api/session');assert json.loads(body)['authenticated']
            body,_=await request('/api/fire');fire=json.loads(body)
            assert fire['available'] and fire['sources'] and fire['inside_count']==sum(e['scope']=='inside' for e in fire['detections'])
            assert all(s['url'] in api.FIRE_SOURCES.values() for s in fire['sources'])
            await request('/api/fire/report/json')
            with patch.object(api,'fetch_fires',side_effect=ValueError('fixture offline')),patch.object(api,'datetime') as clock:
                clock.fromisoformat.return_value.timestamp.return_value=0
                await request('/api/fire/refresh',{},status=503)
            body,_=await request('/api/fire');assert json.loads(body)['fetched_at']==fire['fetched_at']
            with patch.object(api,'fetch_fires',return_value={k:v for k,v in fire.items() if k not in ['available','image_bounds','background_date']}),patch.object(api,'datetime') as clock:
                clock.fromisoformat.return_value.timestamp.return_value=0
                await request('/api/fire/refresh',{})
            body,_=await request('/api/fire');assert json.loads(body)['fetched_at']==fire['fetched_at']
            body,_=await request('/api/forest-history');annual=json.loads(body)
            assert annual['available'] and [row['year'] for row in annual['observations']]==[2023,2024,2025,2026]
            assert len(annual['comparisons'])==3
            for row in annual['observations']:
                body,_=await request(f'/api/forest-history/{row["year"]}/image')
                assert body.startswith(b'\x89PNG')
            await request('/api/forest-history/2022/image',status=404)
            await request('/api/forest-history/2030/image',status=404)
            body,_=await request('/api/datasets');items=json.loads(body);assert {d['id'] for d in items}=={'compartment-279','sentinel','demo'}
            for item in items:
                identity=item['id']
                await request(f'/api/datasets/{identity}/outline')
                for obs in item['views']:
                    for layer in item['layers']:await request(f'/api/datasets/{identity}/{obs["id"]}/image/{layer}')
                await request(f'/api/datasets/{identity}/analyze',{})
                await request(f'/api/datasets/{identity}/validate',{})
                for fmt in ['csv','html']:await request(f'/api/datasets/{identity}/report/{fmt}')
            await request('/api/reports/monthly-demo');await request('/api/reports/monthly-demo.csv')
            body,_=await request('/api/research/proxy');assert json.loads(body)['predicted_pixels']==12362
            hashes=json.loads((api.PROXY_RESULT/'checksums.json').read_text())
            for fmt,(name,mime) in api.PROXY_FILES.items():
                body,_=await request('/api/research/proxy/download/'+fmt)
                assert hashlib.sha256(body).hexdigest()==hashes[name]
            body,_=await request('/api/research/change');comparison=json.loads(body)
            assert comparison['transition_pixels']=={'0':3359,'1':8634,'2':60,'3':309}
            assert comparison['synthetic'] is False and comparison['forest_loss_ha'] is None
            hashes=json.loads((api.RESEARCH_CHANGE/'checksums.json').read_text())
            for layer in ['before','after','changes']:
                body,_=await request('/api/research/change/image/'+layer)
                assert hashlib.sha256(body).hexdigest()==hashes[layer+'.svg']
            for fmt,(name,mime) in api.RESEARCH_CHANGE_EXPORTS.items():
                body,_=await request('/api/research/change/download/'+fmt)
                assert hashlib.sha256(body).hexdigest()==hashes[name]
            await request('/api/research/change/image/bad',status=404)
            await request('/api/research/change/download/bad',status=404)
            body,_=await request('/api/change/run',{});identity=json.loads(body)['run_id']
            assert identity==api.SAVED_CHANGE
            for layer in ['before','after','change','loss','gain','coverage']:await request(f'/api/change/runs/{identity}/image/{layer}')
            for fmt in ['json','csv','html','geotiff']:await request(f'/api/change/runs/{identity}/report/{fmt}')
            source=api.DATA_ROOT/'data/phase2/pair_version7/date_1/forestguard_phase0.zip'
            body,_=await request('/api/import',source.read_bytes());imported=json.loads(body)['id']
            await request(f'/api/datasets/{imported}/analyze',{})
            boundary=json.loads((api.DATA_ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes())
            await request('/api/datasets/compartment-279/boundary',boundary)
            credentials['password']='test-only-officer-b';await request('/api/login',credentials)
            body,_=await request('/api/activity');assert json.loads(body)==[]
            await request(f'/api/datasets/{imported}/analyze',{},status=404)
            await request(f'/api/change/runs/{identity}/report/json')
            await request('/api/change/runs/change-000000000000/report/json',status=404)
            cookie=first_cookie
            restarted=Path(temporary)/'restarted';restarted.mkdir()
            with patch.object(api,'STATE',restarted):
                body,_=await request('/api/session');assert json.loads(body)['authenticated']
                body,_=await request('/api/datasets');assert len(json.loads(body))==3
                await request('/api/research/proxy/image')
                await request('/api/research/change')
                await request(f'/api/change/runs/{identity}/report/json')
                for layer in ['before','after','change','loss','gain','coverage']:await request(f'/api/change/runs/{identity}/image/{layer}')
            await request('/api/logout',{});await request('/api/datasets',status=401)
            with patch.dict(os.environ,{'FORESTGUARD_SESSION_SECRET':''}):await request('/api/login',credentials,status=503)
    result={'status':'PASS','http_checks':calls,'hosted_login_secure_cookie':True,'forged_expired_tokens_rejected':True,
            'cross_origin_mutations_and_bad_hosts_rejected':True,'three_bundled_datasets_maps_analysis_validation_reports':True,
            'research_exports_byte_identical':True,'real_proxy_change_images_exports':True,'change_run_images_exports':True,'sample_boundary_imports':True,
            'sessions_isolated':True,'auth_and_bundled_data_survive_new_instance':True,
            'new_uploads_are_ephemeral':True,'bundled_synthetic_comparison_survives_new_instance':True,'external_networking_blocked':True,
            'fire_offline_snapshot_and_failed_refresh_preservation':True,'actual_vercel_deployment_tested':False}
    output=ROOT/'data/deployment';output.mkdir(parents=True,exist_ok=True)
    (output/'hosted_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':asyncio.run(check())
