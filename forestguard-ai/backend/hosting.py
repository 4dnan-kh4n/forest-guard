"""Server-side officer credentials and portable signed sessions for Vercel."""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from contextvars import ContextVar
from fastapi import HTTPException

HOSTED=os.environ.get('VERCEL')=='1'
DATA_ROOT=os.environ.get('FORESTGUARD_DATA_ROOT')
current_session=ContextVar('forestguard_officer',default=None)
TTL=1800


def password_hash(password):
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt.encode(),600000).hex()
    return f'{salt}:{digest}'


def settings():
    secret=os.environ.get('FORESTGUARD_SESSION_SECRET','')
    try:
        officers=json.loads(os.environ.get('FORESTGUARD_OFFICERS',''))
        assert len(secret)>=32 and isinstance(officers,list) and 1<=len(officers)<=20
        ids=set()
        for officer in officers:
            assert set(officer)=={'id','district','beat','password_hash'}
            assert re.fullmatch(r'[a-z0-9-]{1,40}',officer['id']) and officer['id'] not in ids
            assert officer['district']=='Harda' and officer['beat']=='Joga'
            assert re.fullmatch(r'[a-f0-9]{32}:[a-f0-9]{64}',officer['password_hash'])
            ids.add(officer['id'])
    except (ValueError,TypeError,AssertionError,KeyError):
        raise HTTPException(503,'Hosted officer credentials are not configured. Set the server environment variables and redeploy.')
    return secret.encode(),officers


def authenticate(credentials):
    secret,officers=settings()
    for officer in officers:
        salt,expected=officer['password_hash'].split(':')
        actual=hashlib.pbkdf2_hmac('sha256',credentials['password'].encode(),salt.encode(),600000).hex()
        if (hmac.compare_digest(actual,expected) and credentials.get('district')==officer['district']
                and credentials.get('beat')==officer['beat']):
            payload={'id':officer['id'],'district':officer['district'],'beat':officer['beat'],
                     'expires':int(time.time())+TTL,'nonce':secrets.token_hex(16),
                     'account_version':hashlib.sha256(officer['password_hash'].encode()).hexdigest()}
            body=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':')).encode()).decode().rstrip('=')
            signature=hmac.new(secret,body.encode(),'sha256').hexdigest()
            return body+'.'+signature,payload
    raise HTTPException(401,'Incorrect district, beat or password')


def session(token):
    if not token or len(token)>2048:return None
    secret,officers=settings()
    try:
        body,signature=token.split('.')
        if not hmac.compare_digest(hmac.new(secret,body.encode(),'sha256').hexdigest(),signature):return None
        payload=json.loads(base64.urlsafe_b64decode(body+'='*(-len(body)%4)))
        officer=next(o for o in officers if o['id']==payload['id'])
        if (not int(time.time())<payload['expires']<=int(time.time())+TTL
                or payload['district']!=officer['district'] or payload['beat']!=officer['beat']
                or not re.fullmatch(r'[a-f0-9]{32}',payload['nonce'])
                or payload['account_version']!=hashlib.sha256(officer['password_hash'].encode()).hexdigest()):return None
        return payload
    except (ValueError,TypeError,KeyError,StopIteration):return None
