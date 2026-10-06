"""Check the running local UI/API with stdlib only; records actual checks/exports."""
import json
import urllib.error
import urllib.request
from pathlib import Path

BASE='http://127.0.0.1:8000'
ROOT=Path(__file__).resolve().parents[1]

def request(path,body=None,expected=200):
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE+path,data=body),timeout=30) as response:
            assert response.status==expected
            return response.read()
    except urllib.error.HTTPError as error:
        assert error.code==expected,(path,error.code,error.read())
        return error.read()

def main():
    assert b'ForestGuard AI' in request('/')
    assert json.loads(request('/api/health'))['model_connected'] is False
    datasets=json.loads(request('/api/datasets'))
    assert {'sentinel','demo'}<={d['id'] for d in datasets}
    checks=0
    for data in datasets:
        identity=data['id']
        assert data['model_version'] is None and data['band_order']==['B02','B03','B04','B08']
        for observation in data['views']:
            for layer in data['layers']:
                assert request(f'/api/datasets/{identity}/{observation["id"]}/image/{layer}').startswith(b'\x89PNG\r\n\x1a\n')
                checks+=1
        assert json.loads(request(f'/api/datasets/{identity}/validate',b''))['status']=='passed'
        report=request(f'/api/datasets/{identity}/report/html').decode()
        assert 'not model accuracy' in report
        csv=request(f'/api/datasets/{identity}/report/csv').decode()
        assert data['kind'] in csv
    for payload in [b'null',b'[]',b'{}',b'{"type":"Feature","geometry":null}',b'not-json',b'{"type":"FeatureCollection","features":[]}']:
        request('/api/datasets/sentinel/boundary',payload,400)
    boundary=(ROOT/'data/phase2/pair_version7/boundary_input.geojson').read_bytes()
    assert json.loads(request('/api/datasets/sentinel/boundary',boundary))['rings']
    request('/api/import',b'invalid ZIP',400)
    request('/api/datasets/missing/outline',expected=404)
    request('/api/datasets/demo/train/image/missing',expected=404)
    archive=(ROOT/'data/phase2/pair_version7/date_1/forestguard_phase0.zip').read_bytes()
    imported=json.loads(request('/api/import',archive))
    assert imported['id'].startswith('import-') and imported['kind']=='real'
    assert json.loads(request(f'/api/datasets/{imported["id"]}/validate',b''))['status']=='passed'
    assert json.loads(request('/api/activity'))
    print(json.dumps({'status':'PASS','image_responses_checked':checks,'invalid_inputs_rejected':9,'real_sample_import':'PASS'}))

if __name__=='__main__': main()
