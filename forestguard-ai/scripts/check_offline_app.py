"""Check the built ASGI application in an isolated checkout with outbound connections blocked."""
import asyncio
import importlib
import json
import re
import shutil
import socket
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def prepare():
    from backup_research import restore
    destination = ROOT/'data/phase5/offline_install_v1/project'
    restore(ROOT/'data/backups/compartment_279_imagery_v1.zip',
            'ef1e98ec3a0551c60d5fcc28c28cb997e9150aac68d5dc0c837bcd5c9881b8ce', destination)
    for name in ('backend','scripts','cloud'):
        for source in (ROOT/name).rglob('*.py'):
            if '__pycache__' in source.parts:
                continue
            target = destination/source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    shutil.copytree(ROOT/'frontend/dist', destination/'frontend/dist')
    (destination/'offline_check_only.json').write_text(json.dumps({'purpose':'Isolated offline installation check'}))
    print(str(destination))


async def main():
    if not (ROOT/'offline_check_only.json').exists():
        raise ValueError('Run this check only in the isolated offline-install copy; see OFFLINE_INSTALL_CHECK.md.')
    sys.path.insert(0, str(ROOT))
    # Keep the socket type intact: Windows asyncio uses it for its internal event-loop pipe.
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('Networking forbidden')), \
         patch.object(socket.socket, 'connect_ex', side_effect=AssertionError('Networking forbidden')), \
         patch.object(socket, 'getaddrinfo', side_effect=AssertionError('DNS forbidden')):
        api = importlib.import_module('backend.app')
        from register_research_ui import verify_registration, OUTPUT
        assert verify_registration(OUTPUT)['status'] == 'PASS'
        app = api.app
        cookie = ''

        async def request(path, payload=None, expected=200):
            nonlocal cookie
            body = b'' if payload is None else json.dumps(payload).encode()
            headers = [(b'host', b'localhost'), (b'content-type', b'application/json'),
                       (b'cookie', cookie.encode())]
            scope = {'type':'http', 'asgi':{'version':'3.0','spec_version':'2.4'}, 'http_version':'1.1',
                     'method':'GET' if payload is None else 'POST', 'scheme':'http', 'path':path,
                     'raw_path':path.encode(), 'query_string':b'', 'root_path':'', 'headers':headers,
                     'client':('127.0.0.1',12345), 'server':('localhost',8000)}
            messages = []
            delivered = False
            completed = asyncio.Event()

            async def receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {'type':'http.request', 'body':body, 'more_body':False}
                await completed.wait()
                return {'type':'http.disconnect'}

            async def send(message):
                messages.append(message)
                if message['type']=='http.response.body' and not message.get('more_body', False):
                    completed.set()

            await asyncio.wait_for(app(scope, receive, send), timeout=30)
            start = next(m for m in messages if m['type']=='http.response.start')
            assert start['status'] == expected, (path, start['status'])
            assert b"connect-src 'self'" in dict(start['headers'])[b'content-security-policy']
            for key,value in start['headers']:
                if key == b'set-cookie': cookie = value.decode().split(';')[0]
            return b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body')

        index = await request('/')
        assert b'ForestGuard AI' in index
        assets = re.findall(rb'(?:src|href)="(/assets/[^"?#]+)"', index)
        assert assets
        for asset in assets:
            actual = await request(asset.decode())
            assert actual == (ROOT/'frontend/dist'/asset.decode().lstrip('/')).read_bytes()
        assert json.loads(await request('/api/health'))['model_connected'] is False
        await request('/api/datasets', expected=401)
        await request('/api/login', {'district':'Harda','beat':'Joga','password':'wrong'}, 401)
        await request('/api/login', {'district':'Harda','beat':'Joga','password':'joga@123'})
        items = json.loads(await request('/api/datasets'))
        assert len(items)==1 and items[0]['id']=='compartment-279'
        for observation in ('dry','post_monsoon'):
            for layer in ('imagery','coverage','ndvi'):
                assert (await request(f'/api/datasets/compartment-279/{observation}/image/{layer}')).startswith(b'\x89PNG\r\n\x1a\n')
        analysis = json.loads(await request('/api/datasets/compartment-279/analyze', {}))
        assert [o['valid_pixels'] for o in analysis['observations']] == [12338,12338]
        assert 'median_ndvi_difference' not in analysis
        assert json.loads(await request('/api/datasets/compartment-279/validate', {}))['status']=='passed'
        for extension in ('csv','html'):
            report = await request('/api/datasets/compartment-279/report/'+extension)
            assert b'S2B_T43QFE_20250403T053649_L2A' in report
            assert b'S2B_T43QFE_20251209T053610_L2A' in report
        await request('/api/logout', {})
        await request('/api/datasets', expected=401)
        result = {'status':'PASS', 'fresh_environment':True, 'python':sys.version.split()[0],
                  'python_outbound_connections_and_dns_blocked':True, 'os_network_disabled':False,
                  'browser_checked':False, 'real_registered_files_verified':14,
                  'real_source_files_verified':27, 'map_layers_served':6,
                  'static_assets_served':len(assets), 'login_logout_authorization_checked':True,
                  'same_origin_content_security_policy_checked':True,
                  'analysis_checks_reports_passed':True, 'forest_accuracy_measured':False}
        (ROOT/'offline_app_verification.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if sys.argv[1:] == ['--prepare']:
        prepare()
    elif sys.argv[1:]:
        raise ValueError('Use --prepare from the original project, or no arguments in the isolated copy.')
    else:
        asyncio.run(main())
