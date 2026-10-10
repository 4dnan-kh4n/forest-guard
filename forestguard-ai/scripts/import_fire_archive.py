"""Verify NASA request 820485 and register measured historical detections."""
import csv
import hashlib
import io
import json
import shutil
import sys
import zipfile
from datetime import date,datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.fire_monitor import parse


def register(path):
    if path.is_symlink() or path.stat().st_size>2*1024**2:raise ValueError('Archive exceeds budget')
    with zipfile.ZipFile(path) as archive:
        expected={'fire_archive_J1V-C2_820485.csv','Readme.txt'}
        if set(archive.namelist())!=expected or len(archive.infolist())!=2 or sum(item.file_size for item in archive.infolist())>2*1024**2:
            raise ValueError('Unexpected NASA archive contents')
        raw=archive.read('fire_archive_J1V-C2_820485.csv')
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    for row in rows:
        day=date.fromisoformat(row['acq_date'])
        if not date(2022,1,1)<=day<=date(2026,10,10) or row['satellite']!='N20' or row['instrument']!='VIIRS' or row['type']!='0' or row['version']!='2':
            raise ValueError('Unreviewed archive sensor, type, version or period')
        if not 76.76<=float(row['longitude'])<=76.85 or not 22.37<=float(row['latitude'])<=22.44:raise ValueError('Detection outside requested box')
    boundary=json.loads((ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes())
    events,source=parse(raw,'NOAA-20',boundary)
    events=list({(event['latitude'],event['longitude'],event['observed_at']):event for event in events}.values())
    events.sort(key=lambda event:event['observed_at'],reverse=True)
    yearly=[]
    for year in range(2022,2027):
        selected=[event for event in events if event['observed_at'].startswith(str(year))]
        yearly.append({'year':year,'detections':selected,'inside_count':sum(e['scope']=='inside' for e in selected),
          'nearby_count':sum(e['scope']=='nearby' for e in selected),'requested_box_records':sum(r['acq_date'].startswith(str(year)) for r in rows),
          'partial_year':year==2026})
    report={'format':'forestguard-firms-history-v1','request_id':820485,'requested_start':'2022-01-01','requested_end':'2026-10-10',
      'imported_at':datetime.now(timezone.utc).isoformat(),'sensor':'NOAA-20','version':'VIIRS Collection 2 standard archive',
      'archive_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_url':'https://firms.modaps.eosdis.nasa.gov/data/download/DL_FIRE_J1V-C2_820485.zip',
      'source':source,'observations':yearly,'boundary':boundary,'attribution':'NASA FIRMS / VIIRS NOAA-20 Collection 2; detection centres filtered to compartment 279 and its 2 km surroundings.',
      'limits':'Counts are satellite detection pixels, not confirmed fire incidents or burned area. Zero detections do not prove no fire. Only NOAA-20 is used for consistent yearly comparison. The 2026 archive is partial; standard data may arrive months late. Last detected date is not a coverage-completeness date.'}
    folder=ROOT/'data/fire/archive_2022_2026_v1';folder.mkdir(exist_ok=True)
    if (folder/'report.json').exists():raise ValueError('Preserve existing archive version before replacing')
    shutil.copyfile(path,folder/'source.zip')
    (folder/'source.csv').write_bytes(raw)
    (folder/'report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    hashes={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in ['source.csv','report.json']}
    (folder/'checksums.json').write_bytes((json.dumps(hashes,indent=2)+'\n').encode())
    print(json.dumps({'status':'PASS','source_rows':len(rows),'years':[{k:v for k,v in row.items() if k!='detections'} for row in yearly]},indent=2))


if __name__=='__main__':register(Path(sys.argv[1]))
