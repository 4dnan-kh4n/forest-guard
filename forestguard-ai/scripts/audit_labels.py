"""Audit declared label provenance and split separation; never generate classes."""
import argparse
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path

import rasterio
from rasterio.warp import transform
from check_boundary import check_ring

REQUIRED={'label_id','class','observation_date','reference_source','reference_access_license',
          'reference_date','reviewer','review_date','confidence','uncertainty_notes','study_area_version',
          'split','reference_kind','review_status','reference_independent'}


def audit(document):
    if document.get('type')!='FeatureCollection': raise ValueError('Expected label FeatureCollection.')
    features=document.get('features',[])
    if len(features)>1000: raise ValueError('Initial review audit limited to 1,000 features.')
    ids=set(); footprints=[]; counts=Counter(); reviewed=Counter()
    for feature in features:
        props=feature['properties']; missing=REQUIRED-set(props)
        if missing: raise ValueError(f'Missing provenance fields: {sorted(missing)}')
        label_id=props['label_id']
        if not isinstance(label_id,str) or not label_id.strip() or label_id in ids:
            raise ValueError('Label IDs must be unique nonempty strings.')
        ids.add(label_id)
        cls=props['class']; split=props['split']
        if cls not in {'forest','non_forest','unknown'} or split not in {'unassigned','train','validation','test'}:
            raise ValueError('Invalid class or split.')
        status=props['review_status']
        if status not in {'unreviewed','reviewed','weak_only'}:
            raise ValueError('Invalid review status or confidence.')
        pending=status=='unreviewed' and split=='unassigned' and cls=='unknown'
        if props['confidence'] not in ({None,'high','medium','low'} if pending else {'high','medium','low'}):
            raise ValueError('Invalid review status or confidence.')
        kind=props['reference_kind']
        if kind not in {'field_observation','dated_reference_imagery','weak_map','historical_management_document'}:
            raise ValueError('Invalid reference kind.')
        if not isinstance(props['reference_independent'],bool): raise ValueError('Independence must be boolean.')
        for field in ['reference_source','reference_access_license','study_area_version']:
            if not isinstance(props[field],str) or not props[field].strip(): raise ValueError(f'Empty {field}.')
        if not (pending and props['reviewer'] is None) and (not isinstance(props['reviewer'],str) or not props['reviewer'].strip()):
            raise ValueError('Empty reviewer.')
        dates={'observation_date':date.fromisoformat(props['observation_date'])}
        for field in ['reference_date','review_date']:
            value=props[field]
            if pending and value is None:
                dates[field]=None
                continue
            try:dates[field]=date.fromisoformat(value)
            except (ValueError,TypeError):
                if (field=='reference_date' and split=='unassigned' and kind=='weak_map'
                        and isinstance(value,str) and len(value)>=4 and value[:4].isdigit()
                        and ('annual' in value or len(value)==4)):
                    dates[field]=None
                else:raise ValueError(f'Invalid or insufficiently precise {field}.')
        temporal_support=dates['reference_date'] is not None and abs((dates['reference_date']-dates['observation_date']).days)<=31
        if status=='reviewed' and dates['review_date']<max(dates['observation_date'],dates['reference_date'] or dates['observation_date']):
            raise ValueError('Review predates its observation/reference evidence.')
        if cls=='unknown' and (not isinstance(props['uncertainty_notes'],str) or not props['uncertainty_notes'].strip()):
            raise ValueError('Unknown label needs uncertainty notes.')
        if split!='unassigned':
            if cls=='unknown' or props['review_status']!='reviewed' or props['confidence']=='low':
                raise ValueError('Uncertain/unreviewed examples cannot enter frozen model splits.')
            if kind in {'weak_map','historical_management_document'} or not props['reference_independent']:
                raise ValueError('Independent reviewed reference evidence required for model splits.')
            if not temporal_support: raise ValueError('Reference exceeds preliminary 31-day observation-date tolerance.')
        geometry=feature['geometry']
        if geometry['type']=='Point': points=[geometry['coordinates']]
        elif geometry['type']=='Polygon' and len(geometry['coordinates'])==1:
            points=geometry['coordinates'][0]; check_ring(points)
        else: raise ValueError('Initial audit supports points or single-ring polygons without holes.')
        if not all(len(p)==2 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in p)
                   and -180<=p[0]<=180 and -90<=p[1]<=90 for p in points):
            raise ValueError('Invalid geographic coordinates.')
        if not all(72<=p[0]<=78 and 0<=p[1]<=84 for p in points):
            raise ValueError('Initial metric split audit is limited to the pilot UTM zone 43N region.')
        with rasterio.Env(PROJ_NETWORK='OFF'):
            x,y=transform('EPSG:4326','EPSG:32643',[p[0] for p in points],[p[1] for p in points])
        box=(min(x),min(y),max(x),max(y))
        footprints.append((label_id,split,box,props['observation_date']))
        counts[cls]+=1
        if temporal_support and props['review_status']=='reviewed' and props['reference_independent'] and kind not in {'weak_map','historical_management_document'}:
            reviewed[cls]+=1
    # Conservative footprint-buffer check before extracting samples; bounded review list.
    for i,(aid,asp,a,adate) in enumerate(footprints):
        for bid,bsp,b,bdate in footprints[i+1:]:
            if asp=='unassigned' or bsp=='unassigned' or asp==bsp: continue
            dx=max(0,a[0]-b[2],b[0]-a[2]); dy=max(0,a[1]-b[3],b[1]-a[3])
            if math.hypot(dx,dy)<100: raise ValueError(f'Spatial leakage risk: {aid}, {bid} within 100 m.')
            if adate==bdate: raise ValueError(f'Date shared between splits: {aid}, {bid}.')
    splits=Counter(p[1] for p in footprints)
    complete=bool(features) and all(splits[s]>0 for s in ['train','validation','test']) and not splits['unassigned']
    return {'schema_checks':'PASS','label_count':len(features),'class_counts':{c:counts[c] for c in ['forest','non_forest','unknown']},
            'declared_independent_reviewed_counts':{c:reviewed[c] for c in ['forest','non_forest','unknown']},
            'split_counts':{s:splits[s] for s in ['unassigned','train','validation','test']},
            'split_checks_complete':complete,'training_eligible':False,
            'scope':'declared provenance and split audit; not verification of class truth or model readiness',
            'reference_evidence_supplied':bool(features),'no_classes_generated':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('geojson',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.geojson.stat().st_size>2*1024**2: raise ValueError('Review input exceeds 2 MiB.')
        result=audit(json.loads(args.geojson.read_text()))
        if args.output.exists(): raise ValueError('Audit exists; choose a new output path.')
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(1,f'Label audit failed: {error}\n')
