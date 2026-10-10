"""Check authenticated research API, exports and corrupt/missing results offline."""
import asyncio
import hashlib
import json
import shutil
import socket
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend import app as api


async def check():
    cookie=''
    async def request(path,payload=None,status=200):
        nonlocal cookie
        body=b'' if payload is None else json.dumps(payload).encode()
        scope={'type':'http','asgi':{'version':'3.0','spec_version':'2.4'},'http_version':'1.1','method':'GET' if payload is None else 'POST',
               'scheme':'http','path':path,'raw_path':path.encode(),'query_string':b'','root_path':'',
               'headers':[(b'host',b'localhost'),(b'content-type',b'application/json'),(b'cookie',cookie.encode())],
               'client':('127.0.0.1',12345),'server':('localhost',8000)}
        messages=[];delivered=False;completed=asyncio.Event()
        async def receive():
            nonlocal delivered
            if not delivered:delivered=True;return {'type':'http.request','body':body,'more_body':False}
            await completed.wait();return {'type':'http.disconnect'}
        async def send(message):
            messages.append(message)
            if message['type']=='http.response.body' and not message.get('more_body',False):completed.set()
        await asyncio.wait_for(api.app(scope,receive,send),15)
        start=next(m for m in messages if m['type']=='http.response.start')
        assert start['status']==status,(path,start['status'])
        headers=dict(start['headers'])
        assert b"connect-src 'self'" in headers[b'content-security-policy']
        for key,value in start['headers']:
            if key==b'set-cookie':cookie=value.decode().split(';')[0]
        return b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body'),headers

    with tempfile.TemporaryDirectory(prefix='research_api_check_',dir=ROOT/'data/phase5') as temporary:
        folder=Path(temporary);state=folder/'state';state.mkdir()
        with patch.object(api,'STATE',state),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect_ex',side_effect=AssertionError('Network forbidden')),patch.object(socket,'getaddrinfo',side_effect=AssertionError('DNS forbidden')):
            for path in ['/api/research/proxy','/api/research/proxy/image','/api/research/proxy/download/json']:
                await request(path,status=401)
            await request('/api/login',{'district':'Harda','beat':'Joga','password':'joga@123'})
            body,_=await request('/api/research/proxy');report=json.loads(body)
            assert report['available'] and report['predicted_pixels']==12362 and not report['operational_use_approved']
            assert report['forest_area_ha'] is None
            hashes=json.loads((api.PROXY_RESULT/'checksums.json').read_text())
            body,headers=await request('/api/research/proxy/image')
            assert hashlib.sha256(body).hexdigest()==hashes['proxy_preview.svg']
            assert headers[b'content-type'].startswith(b'image/svg+xml')
            for format,(name,mime) in api.PROXY_FILES.items():
                body,headers=await request('/api/research/proxy/download/'+format)
                assert hashlib.sha256(body).hexdigest()==hashes[name]
                assert headers[b'content-disposition'].startswith(b'attachment;')
            await request('/api/research/proxy/download/exe',status=404)
            body,_=await request('/api/change');assert json.loads(body)['real_analysis_ready'] is False
            body,_=await request('/api/datasets');assert any(d['id']=='compartment-279' for d in json.loads(body))
            with patch.object(api,'PROXY_RESULT',folder/'missing'):
                body,_=await request('/api/research/proxy');assert not json.loads(body)['available']
                await request('/api/research/proxy/image',status=404)
            copied=folder/'corrupted';shutil.copytree(api.PROXY_RESULT,copied)
            with patch.object(api,'PROXY_RESULT',copied):
                target=copied/'proxy_preview.svg';target.write_bytes(target.read_bytes()+b'corrupt')
                for path in ['/api/research/proxy','/api/research/proxy/image','/api/research/proxy/download/classes']:
                    await request(path,status=503)
                target.write_bytes((ROOT/'data/phase3/research_proxy_map_v1/proxy_preview.svg').read_bytes())
                (copied/'checksums.json').write_text('{}')
                await request('/api/research/proxy',status=503)
            await request('/api/logout',{})
            await request('/api/research/proxy',status=401)
    summary={'status':'PASS','authenticated_metadata_map_and_four_exports_checked':True,
             'download_bytes_match_saved_checksums':True,'missing_result_checked':True,'corrupt_result_and_manifest_rejected':True,
             'unsupported_export_rejected':True,'logout_denies_access':True,'outbound_connections_and_dns_blocked':True,
             'existing_datasets_available':True,'real_change_analysis_still_gated':True,'browser_interactions_checked':False}
    out=ROOT/'data/phase5/research_dashboard_v1';out.mkdir(exist_ok=True)
    (out/'api_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':asyncio.run(check())
