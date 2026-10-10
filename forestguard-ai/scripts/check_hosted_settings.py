"""Credential diagnostics reject malformed input without exposing its contents."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi import HTTPException
from backend.hosting import settings

secret='private-test-value-'+('x'*32)
officer={'id':'test-officer','district':'Harda','beat':'Joga','password_hash':'a'*32+':'+'b'*64}
valid={'FORESTGUARD_SESSION_SECRET':secret,'FORESTGUARD_OFFICERS':json.dumps([officer])}
cases=[
    ({'FORESTGUARD_SESSION_SECRET':''},'FORESTGUARD_SESSION_SECRET is missing'),
    ({'FORESTGUARD_SESSION_SECRET':'short'},'at least 32'),
    ({'FORESTGUARD_OFFICERS':''},'FORESTGUARD_OFFICERS is missing'),
    ({'FORESTGUARD_OFFICERS':'not-json-private-content'},'invalid JSON'),
    ({'FORESTGUARD_OFFICERS':json.dumps(valid['FORESTGUARD_OFFICERS'])},'JSON array'),
    ({'FORESTGUARD_OFFICERS':json.dumps(valid)},'JSON array'),
    ({'FORESTGUARD_OFFICERS':'[]'},'1 to 20'),
    ({'FORESTGUARD_OFFICERS':'[null]'},'exactly id'),
    ({'FORESTGUARD_OFFICERS':json.dumps([officer,officer])},'unique'),
    ({'FORESTGUARD_OFFICERS':json.dumps([{**officer,'id':None}])},'unique'),
    ({'FORESTGUARD_OFFICERS':json.dumps([{**officer,'beat':'other'}])},'Harda and Joga'),
    ({'FORESTGUARD_OFFICERS':json.dumps([{**officer,'password_hash':'secret-password'}])},'password_hash is invalid'),
]
with patch.dict(os.environ,valid):
    assert settings()==(secret.encode(),[officer])
    for change,expected in cases:
        with patch.dict(os.environ,change):
            try:settings()
            except HTTPException as error:
                assert error.status_code==503 and expected in error.detail
                assert all(value not in error.detail for value in (secret,officer['password_hash'],'not-json-private-content','secret-password'))
            else:raise AssertionError('Malformed configuration accepted.')
print('PASS: valid credentials and 12 safe configuration diagnostics.')
