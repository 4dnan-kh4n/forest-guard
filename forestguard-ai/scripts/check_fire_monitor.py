"""Small deterministic tests; synthetic CSV is only a parser fixture."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.fire_monitor import parse,fetch,location_scope,SOURCES,MAX_BYTES

ring=[[76,22],[76.01,22],[76.01,22.01],[76,22.01],[76,22]]
hole=[[76.004,22.004],[76.006,22.004],[76.006,22.006],[76.004,22.006],[76.004,22.004]]
geometry={'type':'Polygon','coordinates':[ring,hole]}
boundary={'bbox':[76,22,76.01,22.01],'features':[{'geometry':geometry,'properties':{'study_area_version':'synthetic-test'}}]}
assert location_scope(76.002,22.002,geometry)=='inside'
assert location_scope(76.005,22.005,geometry)=='nearby'
assert location_scope(76.02,22.005,geometry)=='nearby'
assert location_scope(77,23,geometry) is None
assert location_scope(76.002,22.002,{'type':'MultiPolygon','coordinates':[[ring,hole]]})=='inside'
header='latitude,longitude,acq_date,acq_time,confidence,frp,scan,track\n'
csv=(header+'22.002,76.002,2026-10-10,605,n,2.5,0.4,0.5\n'+'23,77,2026-10-09,1300,h,1,0.4,0.4\n').encode()
events,details=parse(csv,'NOAA-20',boundary)
assert len(events)==1 and events[0]['confidence']=='nominal' and events[0]['observed_at'].endswith('06:05:00+00:00')
assert details['regional_rows']==2
for invalid in [b'wrong\n',b'x'*(MAX_BYTES+1),csv.replace(b'22.002',b'nan'),csv.replace(b',n,',b',bad,'),csv.replace(b',2.5,',b',-1,')]:
    try:parse(invalid,'NOAA-20',boundary)
    except (ValueError,UnicodeError):pass
    else:raise AssertionError('Invalid feed accepted')

class Response:
    def __init__(self,url):self.url=url
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def geturl(self):return self.url
    def read(self,size):return csv[:size]

def complete(request,timeout):return Response(request.full_url)
report=fetch(boundary,complete)
assert report['status']=='complete' and report['inside_count']==2 and len(report['sources'])==2
def partial(request,timeout):
    if request.full_url==SOURCES['NOAA-21']:raise OSError('fixture offline')
    return Response(request.full_url)
assert fetch(boundary,partial)['status']=='partial'
def unavailable(request,timeout):raise OSError('fixture offline')
try:fetch(boundary,unavailable)
except ValueError:pass
else:raise AssertionError('Unavailable feed presented as zero fires')
print('PASS: fire locations, holes, CSV validation, partial sources and unavailable feeds.')
