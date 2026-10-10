"""Run only an isolated test copy on port 8001, denying non-loopback Python networking."""
import socket
import argparse
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/'offline_check_only.json').exists():
    raise ValueError('Use the isolated project created by check_offline_app.py --prepare.')
sys.path.insert(0,str(ROOT))
import uvicorn
from backend.app import app

connect=socket.socket.connect
connect_ex=socket.socket.connect_ex
getaddrinfo=socket.getaddrinfo


def local(address):
    if not isinstance(address,tuple) or address[0] not in {'127.0.0.1','::1'}:
        raise OSError('Offline check: external networking is disabled')


def guarded_connect(sock,address):
    local(address)
    return connect(sock,address)


def guarded_connect_ex(sock,address):
    local(address)
    return connect_ex(sock,address)


def guarded_dns(host,*args,**kwargs):
    if host not in {'localhost','127.0.0.1','::1',None}:
        raise OSError('Offline check: external DNS is disabled')
    return getaddrinfo(host,*args,**kwargs)


socket.socket.connect=guarded_connect
socket.socket.connect_ex=guarded_connect_ex
socket.getaddrinfo=guarded_dns
for blocked in [('203.0.113.1',443),('example.invalid',443)]:
    try:
        with socket.socket() as probe:probe.connect(blocked)
    except OSError:pass
    else:raise AssertionError('External connection guard failed')
print('External Python connections and DNS blocked; browser policy restricts resources to this local origin.',flush=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port',type=int,default=8001)
args=parser.parse_args()
if not 8001<=args.port<=8010:parser.error('Use an isolated loopback test port between 8001 and 8010.')
uvicorn.run(app,host='127.0.0.1',port=args.port)
