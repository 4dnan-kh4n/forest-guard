"""Prepare private Vercel environment values; never print passwords or secrets."""
import getpass
import json
import secrets
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.hosting import password_hash

if __name__=='__main__':
    password=getpass.getpass('New hosted officer password (at least 12 characters): ')
    if len(password)<12:raise ValueError('Use at least 12 characters.')
    if password!=getpass.getpass('Confirm password: '):raise ValueError('Passwords differ.')
    output=ROOT/'data/deployment/hosted-environment.private.json'
    if output.exists():raise ValueError('Private environment file exists; preserve it before rotating access.')
    output.parent.mkdir(parents=True,exist_ok=True)
    values={'FORESTGUARD_SESSION_SECRET':secrets.token_urlsafe(48),
            'FORESTGUARD_OFFICERS':json.dumps([{'id':'joga-officer-1','district':'Harda','beat':'Joga','password_hash':password_hash(password)}]),
            'FORESTGUARD_ALLOWED_HOSTS':'forest-guard-nu.vercel.app'}
    output.write_text(json.dumps(values,indent=2)+'\n',encoding='utf-8')
    print('Private environment values saved locally to '+str(output)+'. Do not commit this file.')
