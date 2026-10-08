"""Small public NASA metadata inventory only; never download lidar granules or credentials."""
import hashlib
import json
import argparse
from datetime import date,datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--start',type=date.fromisoformat,default=date(2025,1,1))
parser.add_argument('--end',type=date.fromisoformat,default=date(2025,12,31))
args=parser.parse_args()
if args.start>args.end: parser.error('Start date must not follow end date.')
root=Path(__file__).resolve().parents[1]
config=json.loads((root/'config/study_area.json').read_text(encoding='utf-8'))
boundary=json.loads((root/config['geometry_path']).read_text(encoding='utf-8'))
output=root/'data/reference/gedi_catalogue'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
output.mkdir(parents=True)

def fetch(endpoint,parameters,name):
    url='https://cmr.earthdata.nasa.gov/search/'+endpoint+'?'+urlencode(parameters)
    with urlopen(Request(url,headers={'User-Agent':'ForestGuard-research-metadata/1.0'}),timeout=30) as response:
        content=response.read(2*1024**2+1)
        hits=response.headers.get('CMR-Hits')
    if len(content)>2*1024**2:raise ValueError('Public metadata response exceeds 2 MiB; no large download attempted.')
    data=json.loads(content)
    (output/name).write_bytes(content)
    return data,{'source_url':url,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'total_metadata_hits':hits}

result={'study_id':config['study_id'],'study_area_version':config['study_area_version'],
        'query_interval':f'{args.start}T00:00:00Z,{args.end}T23:59:59Z','collections':[],
        'shot_coverage_verified':False,'lidar_files_downloaded':False,'reference_labels_created':False}
try:
    for product in ['GEDI02_A','GEDI02_B']:
        collections,source=fetch('collections.json',{'short_name':product,'page_size':20},product+'_collections.json')
        entries=collections['feed']['entry']
        eligible=[entry for entry in entries if entry.get('version_id','').isdigit()]
        if not eligible:raise ValueError('No numbered GEDI collection returned for '+product)
        entry=max(eligible,key=lambda item:int(item['version_id']))
        granules,inventory=fetch('granules.json',{'collection_concept_id':entry['id'],
            'bounding_box':','.join(map(str,boundary['bbox'])),'temporal':result['query_interval'],'page_size':100},product+'_granules.json')
        records=granules['feed']['entry']
        if int(inventory['total_metadata_hits'])>len(records):
            raise ValueError('Inventory exceeds the bounded page; do not claim complete coverage.')
        result['collections'].append({'short_name':product,'version':entry['version_id'],'concept_id':entry['id'],
            'collection_metadata':source,'granule_metadata':inventory,'returned_granules':len(records),
            'granule_ids':[record.get('producer_granule_id',record.get('title')) for record in records],
            'reported_granule_size_mb':[record.get('granule_size') for record in records],
            'limits':'Granule spatial footprints may intersect the box without any usable shots inside the polygon. Download and inspect filtered shots before labeling.'})
    result['status']='METADATA_INVENTORY_COMPLETE'
except Exception as error:
    result['status']='METADATA_INVENTORY_FAILED';result['error']=str(error)
(output/'inventory_report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'saved_folder':str(output),'inventory':result},indent=2))
if result['status']!='METADATA_INVENTORY_COMPLETE':raise SystemExit(1)
