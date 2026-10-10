"""Verify packaging preserves bytes and fails clearly on missing libraries."""
import tempfile
from pathlib import Path
from prepare_vercel_native import prepare


with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    source = root/'system'
    source.mkdir()
    (source/'libexpat.so.1').write_bytes(b'packaging-test-only')
    target = prepare([root/'missing', source], root/'bundle')
    assert target.read_bytes() == (source/'libexpat.so.1').read_bytes()
    try:
        prepare([root/'missing'], root/'bad')
    except RuntimeError as error:
        assert 'libexpat.so.1' in str(error)
    else:
        raise AssertionError('Missing native dependency was accepted.')
print('PASS: native packaging and missing-library error; actual Linux loading requires Vercel.')
