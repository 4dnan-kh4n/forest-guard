"""Check URL, response-size, content and overwrite guards without network requests."""
import tempfile
from pathlib import Path
from unittest.mock import patch
from download_gedi_subset import download

url='https://harmony.earthdata.nasa.gov/service-results/harmony-prod-staging/public/job/id/small_subsetted.h5'
with tempfile.TemporaryDirectory() as directory:
    target=Path(directory)/'result'
    for invalid in [url+'?token=secret',url.replace('https:','http:'),url.replace('public/','private/'),url.replace('harmony.earthdata.nasa.gov','example.org')]:
        with patch('download_gedi_subset.urlopen') as network:
            try:download(invalid,target)
            except ValueError:pass
            else:raise AssertionError('Unsafe URL accepted')
            network.assert_not_called()
    class Response:
        headers={'Content-Length':str(11*1024**2)}
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,limit):raise AssertionError('Oversized response read')
    with patch('download_gedi_subset.urlopen',return_value=Response()):
        try:download(url,target)
        except ValueError:pass
        else:raise AssertionError('Oversized response accepted')
    class HTML(Response):
        headers={}
        def read(self,limit):return b'Login page, not measurements'
    with patch('download_gedi_subset.urlopen',return_value=HTML()):
        try:download(url,target)
        except ValueError:pass
        else:raise AssertionError('HTML saved as data')
    assert not target.exists()
    target.mkdir()
    with patch('download_gedi_subset.urlopen') as network:
        try:download(url,target)
        except ValueError:pass
        else:raise AssertionError('Existing output reused')
        network.assert_not_called()
print('PASS: unsafe/authenticated URLs, large/non-HDF responses and existing output rejected.')
