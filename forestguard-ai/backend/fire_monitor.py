"""Bounded NASA FIRMS observations; detections are not confirmed forest fires."""
import csv
import hashlib
import io
import math
from datetime import datetime, timezone
from urllib.request import Request, urlopen

SOURCES={
    'NOAA-20':'https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_Asia_7d.csv',
    'NOAA-21':'https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_South_Asia_7d.csv',
}
MAX_BYTES=2*1024**2


def inside_ring(x,y,ring):
    inside=False
    for a,b in zip(ring,ring[1:]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside=not inside
    return inside


def location_scope(lon,lat,geometry):
    polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
    if any(inside_ring(lon,lat,p[0]) and not any(inside_ring(lon,lat,r) for r in p[1:]) for p in polygons):
        return 'inside'
    # Local distance approximation is adequate for a 2 km context, not surveying.
    sx=111320*math.cos(math.radians(lat));sy=111320
    closest=float('inf')
    for polygon in polygons:
        for ring in polygon:
            for a,b in zip(ring,ring[1:]):
                ax,ay=(a[0]-lon)*sx,(a[1]-lat)*sy
                bx,by=(b[0]-lon)*sx,(b[1]-lat)*sy
                dx,dy=bx-ax,by-ay
                t=max(0,min(1,-(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
                closest=min(closest,math.hypot(ax+t*dx,ay+t*dy))
    return 'nearby' if closest<=2000 else None


def parse(raw,sensor,boundary):
    if len(raw)>MAX_BYTES:raise ValueError('FIRMS feed exceeds 2 MiB budget')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    required={'latitude','longitude','acq_date','acq_time','confidence','frp','scan','track'}
    if not required<=set(reader.fieldnames or []):raise ValueError('FIRMS CSV schema mismatch')
    bbox=boundary['bbox'];geometry=boundary['features'][0]['geometry'];events=[];count=0;dates=[]
    for row in reader:
        count+=1
        if count>15000:raise ValueError('FIRMS feed exceeds row budget')
        lat,lon=float(row['latitude']),float(row['longitude'])
        if not math.isfinite(lat+lon) or not -90<=lat<=90 or not -180<=lon<=180:raise ValueError('Invalid fire location')
        clock=row['acq_time'].zfill(4)
        observed=datetime.strptime(row['acq_date']+' '+clock,'%Y-%m-%d %H%M').replace(tzinfo=timezone.utc)
        dates.append(observed)
        if not bbox[0]-.025<=lon<=bbox[2]+.025 or not bbox[1]-.025<=lat<=bbox[3]+.025:continue
        scope=location_scope(lon,lat,geometry)
        if not scope:continue
        frp,scan,track=[float(row[k]) for k in ['frp','scan','track']]
        if not all(math.isfinite(v) and v>=0 for v in [frp,scan,track]):raise ValueError('Invalid fire measurement')
        if row['confidence'] not in {'l','n','h'}:raise ValueError('Unexpected VIIRS confidence class')
        events.append({'latitude':lat,'longitude':lon,'observed_at':observed.isoformat(),
                       'sensor':sensor,'scope':scope,'confidence':{'l':'low','n':'nominal','h':'high'}[row['confidence']],
                       'frp_mw':frp,'scan_km':scan,'track_km':track,'daynight':row.get('daynight'),
                       'instrument':'VIIRS','source':'NASA FIRMS'})
    return events,{'regional_rows':count,'earliest_observation':min(dates).isoformat() if dates else None,
                   'latest_observation':max(dates).isoformat() if dates else None}


def fetch(boundary,opener=urlopen):
    events=[];sources=[];errors=[]
    for sensor,url in SOURCES.items():
        try:
            with opener(Request(url,headers={'User-Agent':'ForestGuard research/1.0'}),timeout=12) as response:
                if response.geturl().split('/')[2]!='firms.modaps.eosdis.nasa.gov':raise ValueError('Unexpected FIRMS redirect')
                raw=response.read(MAX_BYTES+1)
            selected,details=parse(raw,sensor,boundary)
            events.extend(selected)
            sources.append(dict(details,sensor=sensor,url=url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
        except Exception as error:
            errors.append({'sensor':sensor,'error':type(error).__name__})
    if not sources:raise ValueError('Neither NASA fire feed could be obtained; keep the last saved report')
    unique={(e['sensor'],e['latitude'],e['longitude'],e['observed_at']):e for e in events}
    events=sorted(unique.values(),key=lambda e:e['observed_at'],reverse=True)
    return {'format':'forestguard-firms-recent-v1','fetched_at':datetime.now(timezone.utc).isoformat(),
            'window_days':7,'status':'complete' if not errors else 'partial','sources':sources,'errors':errors,
            'study_area_version':boundary['features'][0]['properties']['study_area_version'],
            'boundary':boundary,'detections':events,'inside_count':sum(e['scope']=='inside' for e in events),
            'nearby_count':sum(e['scope']=='nearby' for e in events),'nearby_radius_m':2000,
            'attribution':'NASA FIRMS / LANCE, VIIRS NOAA-20 and NOAA-21; original feed checksums retained.',
            'reference_url':'https://firms.modaps.eosdis.nasa.gov/active_fire/',
            'limits':'Satellite thermal detections, not confirmed forest fires or burned area. No detection is not proof of no fire. Inside means detection centre inside the polygon; the pixel footprint may cross its boundary. Latest feed observation is not proof this compartment was observed then.'}
