"""Inspect a bounded GEDI L2A V003 subset offline, without assigning forest labels."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import h5py
import numpy as np
from check_boundary import check_ring

FIELDS = ['degrade_flag','delta_time','l2a_quality_flag_rel2','l2a_quality_flag_rel3',
          'lat_lowestmode','lon_lowestmode','rh','sensitivity','shot_number','solar_elevation']


def inside_ring(x, y, ring):
    inside = False
    for (ax, ay), (bx, by) in zip(ring, ring[1:]):
        cross = (x-ax)*(by-ay)-(y-ay)*(bx-ax)
        if abs(cross)<1e-12 and min(ax,bx)<=x<=max(ax,bx) and min(ay,by)<=y<=max(ay,by):
            return True
        if (ay>y)!=(by>y) and x < ax+(y-ay)*(bx-ax)/(by-ay):
            inside = not inside
    return inside


def inspect(source, boundary_path, output):
    source, boundary_path, output = map(Path, [source, boundary_path, output])
    if output.exists(): raise ValueError('Existing evidence directory; choose a new output.')
    if source.stat().st_size>10*1024**2: raise ValueError('Only subsets up to 10 MiB may be inspected locally.')
    boundary=json.loads(boundary_path.read_text(encoding='utf-8'))
    if len(boundary['features'])!=1: raise ValueError('Expected one study geometry.')
    geometry=boundary['features'][0]['geometry']
    polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
    if geometry['type'] not in {'Polygon','MultiPolygon'} or any(len(p)!=1 for p in polygons):
        raise ValueError('Initial inspection supports polygons without holes.')
    for polygon in polygons: check_ring(polygon[0])
    rows=[]; beams=[]; seen=set()
    with h5py.File(source,'r') as handle:
        if handle.attrs.get('short_name')!='GEDI_L2A': raise ValueError('Not a GEDI L2A subset.')
        if 'Harmony Trajectory Subsetter' not in str(handle.attrs.get('history','')):
            raise ValueError('Missing Harmony subset provenance.')
        metadata=handle['METADATA/DatasetIdentification'].attrs
        original_name=str(metadata.get('fileName',''))
        if not original_name.startswith('GEDI02_A_') or not original_name.endswith('_V003.h5'):
            raise ValueError('Expected original L2A V003 filename metadata.')
        source_version_id=str(metadata.get('VersionID',''))
        for name in sorted(handle):
            if not name.startswith('BEAM'): continue
            group=handle[name]
            if not set(FIELDS)<=set(group): raise ValueError('Missing required shot fields: '+name)
            n=group['shot_number'].shape[0]
            if n>2000 or group['rh'].shape!=(n,101): raise ValueError('Unexpected or oversized beam.')
            if any(group[field].shape!=(n,) for field in FIELDS if field!='rh'):
                raise ValueError('Mismatched shot dimensions.')
            if group['shot_number'].dtype.kind!='u': raise ValueError('Shot identifiers must be unsigned integers.')
            data={field:group[field][:] for field in FIELDS if field!='rh'}
            rh98=group['rh'][:,98]
            beam_rows=[]
            for i in range(n):
                x,y=float(data['lon_lowestmode'][i]),float(data['lat_lowestmode'][i])
                if not np.isfinite([x,y]).all() or not (-180<=x<=180 and -90<=y<=90):
                    raise ValueError('Invalid shot coordinates.')
                shot=str(int(data['shot_number'][i]))
                if shot in seen: raise ValueError('Duplicate shot identifier.')
                seen.add(shot)
                row={field:int(data[field][i]) if data[field].dtype.kind in 'iu' else float(data[field][i])
                     for field in data}
                if not all(np.isfinite(value) for value in row.values()): raise ValueError('Nonfinite shot field.')
                row.update(shot_number=shot,beam=name,rh98_m=float(rh98[i]),
                    inside_study=any(inside_ring(x,y,p[0]) for p in polygons))
                row['screen_pass']=bool(row['inside_study'] and row['l2a_quality_flag_rel3']==1
                    and row['degrade_flag']==0 and 0.95<=row['sensitivity']<=1
                    and np.isfinite(row['rh98_m']) and -213<=row['rh98_m']<=213)
                # ponytail: RH98 is a measurement hint; add land-use/canopy evidence before forest labeling.
                if not np.isfinite(row['rh98_m']): row['rh98_m']=None
                rows.append(row);beam_rows.append(row)
            beams.append({'beam':name,'description':str(group.attrs.get('description','')),
                'returned_shots':n,'inside_study':sum(r['inside_study'] for r in beam_rows),
                'screen_pass':sum(r['screen_pass'] for r in beam_rows),
                'delta_time_units':str(group['delta_time'].attrs.get('units',''))})
        history=str(handle.attrs['history'])
    selected=[r for r in rows if r['screen_pass']]
    interior=[r for r in rows if r['inside_study']]
    report={'source_file':source.name,'source_bytes':source.stat().st_size,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'boundary_sha256':hashlib.sha256(boundary_path.read_bytes()).hexdigest(),
        'study_area_version':boundary['features'][0]['properties']['study_area_version'],
        'product_doi':'10.5067/GEDI/GEDI02_A.003','harmony_history':history,'beams':beams,
        'original_file_name':original_name,'source_metadata_VersionID':source_version_id,
        'returned_shots':len(rows),'inside_study_shots':sum(r['inside_study'] for r in rows),
        'screen_pass_shots':len(selected),'screen_pass_night_shots':sum(r['solar_elevation']<0 for r in selected),
        'inside_degrade_flag_counts':dict(Counter(str(r['degrade_flag']) for r in interior)),
        'inside_release3_quality_flag_counts':dict(Counter(str(r['l2a_quality_flag_rel3']) for r in interior)),
        'screen_pass_rh98_range_m':[min(r['rh98_m'] for r in selected),max(r['rh98_m'] for r in selected)] if selected else None,
        'screen':'inside exact polygon; V003 L2A release-3 flag=1; degrade=0; sensitivity 0.95..1; finite RH98 within product range',
        'labels_created':0,'independent_forest_accuracy_measured':False,
        'versions':{'numpy':np.__version__,'h5py':h5py.__version__},
        'limits':'Point-centre inclusion only, not entire ~25 m footprint containment. Sparse transects are not representative coverage. RH98 does not establish forest use or stand canopy fraction. V003 quality flags use ancillary land-cover maps; screen is preliminary. Delta time retained as supplied; no unverified UTC conversion.'}
    output.mkdir(parents=True)
    (output/'inspection_report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    if rows:
        with (output/'shots.csv').open('w',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    points={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point',
        'coordinates':[r['lon_lowestmode'],r['lat_lowestmode']]},'properties':r} for r in rows]}
    (output/'shots.geojson').write_text(json.dumps(points,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('subset',type=Path);parser.add_argument('boundary',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(inspect(args.subset,args.boundary,args.output),indent=2))
