"""Retrieve an already-generated small public NASA HDF subset without credentials."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen


def download(url, output):
    output=Path(output)
    parts=urlsplit(url)
    if (parts.scheme!='https' or parts.netloc!='harmony.earthdata.nasa.gov'
            or not parts.path.startswith('/service-results/harmony-prod-staging/public/')
            or not parts.path.endswith('_subsetted.h5') or parts.query or parts.fragment):
        raise ValueError('Expected a public Harmony subset link without authentication tokens.')
    if output.exists(): raise ValueError('Existing output directory; preserve evidence.')
    with urlopen(Request(url,headers={'User-Agent':'ForestGuard-small-reference-subset/1.0'}),timeout=30) as response:
        if int(response.headers.get('Content-Length',0))>10*1024**2:
            raise ValueError('Subset exceeds the 10 MiB limit.')
        raw=response.read(10*1024**2+1)
    if len(raw)>10*1024**2 or raw[:8]!=b'\x89HDF\r\n\x1a\n':
        raise ValueError('Oversized or non-HDF response; no data saved.')
    output.mkdir(parents=True)
    name=parts.path.rsplit('/',1)[-1]
    (output/name).write_bytes(raw)
    manifest={'source_url':url,'file_name':name,'bytes':len(raw),
              'sha256':hashlib.sha256(raw).hexdigest(),'authentication_used':False}
    (output/'download_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('public_subset_url');parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(download(args.public_subset_url,args.output),indent=2))
