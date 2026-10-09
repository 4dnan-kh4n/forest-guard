"""Compare aligned, dated classification crops only on common observable coverage."""
import argparse
import csv
import hashlib
import json
import tempfile
from datetime import date
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window


def compare(before, after, study_mask, output):
    paths = [Path(p) for p in [before,after,study_mask]]
    output = Path(output)
    if output.exists():
        raise ValueError('Output exists; preserve it and choose a new folder.')
    if any(p.stat().st_size>30*1024**2 for p in paths):
        raise ValueError('Only small stored classification crops are supported.')
    with rasterio.Env(PROJ_NETWORK='OFF',GDAL_CACHEMAX=16*1024**2), rasterio.open(paths[0]) as earlier, rasterio.open(paths[1]) as later, rasterio.open(paths[2]) as study:
        rasters = [earlier,later,study]
        if any(r.driver!='GTiff' or r.count!=1 or r.dtypes!=('uint8',) for r in rasters):
            raise ValueError('Inputs must be single-band uint8 GeoTIFFs.')
        if (earlier.width*earlier.height>250000 or earlier.width>2048 or earlier.crs is None
                or earlier.crs.to_epsg()!=32643 or earlier.transform.a!=20 or earlier.transform.e!=-20
                or earlier.transform.b!=0 or earlier.transform.d!=0
                or any(r.crs!=earlier.crs or r.transform!=earlier.transform or r.shape!=earlier.shape for r in rasters)):
            raise ValueError('All inputs must share the supported 20 m EPSG:32643 grid.')
        if earlier.nodata!=255 or later.nodata!=255:
            raise ValueError('Classifications require explicit no-data value 255.')
        left,right,mask_tags = [r.tags() for r in rasters]
        for key in ['model_version','forest_definition_version','study_area_version','synthetic_fixture']:
            if not left.get(key) or left[key]!=right.get(key):
                raise ValueError('Observation metadata mismatch: '+key)
        if left['synthetic_fixture'] not in {'true','false'} or mask_tags.get('study_area_version')!=left['study_area_version']:
            raise ValueError('Study mask/scope metadata mismatch.')
        synthetic = left['synthetic_fixture']=='true'
        if mask_tags.get('synthetic_fixture')!=left['synthetic_fixture']:
            raise ValueError('Synthetic/real study mask mismatch.')
        if any(t.get('class_mapping')!='0:non_forest,1:forest' for t in [left,right]):
            raise ValueError('Classification semantics must be explicit and consistent.')
        first,last = [date.fromisoformat(t['acquisition_date']) for t in [left,right]]
        if first>=last:
            raise ValueError('Acquisition dates must be distinct and chronological.')
        # Date proximity is a screening rule, not proof of comparable vegetation conditions.
        days = abs(first.replace(year=2000).timetuple().tm_yday-last.replace(year=2000).timetuple().tm_yday)
        if min(days,366-days)>45 or any(t.get('season_review_status')!='comparable' for t in [left,right]):
            raise ValueError('Comparable seasonal conditions must be reviewed; dates must be within 45 seasonal days.')
        if not synthetic and any(t.get('operational_use_approved')!='true' for t in [left,right]):
            raise ValueError('Real classification models must pass operational review.')
        output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='change_',dir=output.parent) as temporary:
            temporary = Path(temporary)
            counts = [0]*4
            study_pixels = 0
            profile = earlier.profile.copy()
            profile.update(compress='deflate')
            with rasterio.open(temporary/'change.tif','w',**profile) as destination:
                destination.set_band_description(1,'synthetic_change' if synthetic else 'suspected_cover_change')
                destination.update_tags(synthetic_fixture=str(synthetic).lower(),study_area_version=left['study_area_version'],
                                        before_date=first.isoformat(),after_date=last.isoformat(),
                                        class_mapping='0:stable_non_forest,1:stable_forest,2:suspected_loss,3:suspected_gain')
                for row in range(0,earlier.height,16):
                    window = Window(0,row,earlier.width,min(16,earlier.height-row))
                    a,b = [r.read(1,window=window,masked=True).filled(255) for r in [earlier,later]]
                    inside = study.read(1,window=window,masked=True).filled(0)
                    if not np.isin(inside,[0,1]).all() or any(not np.isin(v,[0,1,255]).all() for v in [a,b]):
                        raise ValueError('Invalid study mask or classification values.')
                    inside = inside.astype(bool)
                    study_pixels+=int(inside.sum())
                    common = inside & (a!=255) & (b!=255)
                    change = np.full(a.shape,255,dtype='uint8')
                    for label,condition in enumerate([(a==0)&(b==0),(a==1)&(b==1),(a==1)&(b==0),(a==0)&(b==1)]):
                        selected = common & condition
                        change[selected]=label
                        counts[label]+=int(selected.sum())
                    destination.write(change,1,window=window)
            observed = sum(counts)
            if not study_pixels or not observed:
                raise ValueError('Study area and common observable coverage must be nonempty.')
            names = ['stable_non_forest','stable_forest','suspected_loss','suspected_gain']
            report = {'synthetic_fixture':synthetic,'scope':'synthetic pipeline check' if synthetic else 'selected study area only',
                      'before_date':first.isoformat(),'after_date':last.isoformat(),
                      'model_version':left['model_version'],'forest_definition_version':left['forest_definition_version'],
                      'study_area_version':left['study_area_version'],'study_mask_pixels':study_pixels,
                      'common_observable_pixels':observed,'unobservable_study_pixels':study_pixels-observed,
                      'common_coverage_fraction':observed/study_pixels,'pixel_area_ha':.04,
                      'study_mask_area_ha':study_pixels*.04,'observable_area_ha':observed*.04,
                      'transition_pixels':dict(zip(names,counts)),
                      'transition_area_ha':{name:count*.04 for name,count in zip(names,counts)},
                      'before_cover_on_common_ha':(counts[1]+counts[2])*.04,
                      'after_cover_on_common_ha':(counts[1]+counts[3])*.04,
                      'net_cover_change_on_common_ha':(counts[3]-counts[2])*.04,
                      'area_method':'pixel-centre study mask times 20 m pixel area; not surveyed boundary or tree-crown area',
                      'input_sha256':{name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in zip(['before','after','study_mask'],paths)},
                      'limits':'Synthetic transitions only; not findings about Joga.' if synthetic else 'Suspected cover transitions only. Seasonal/alignment/classification errors require review; no fire, illegal activity or permanent deforestation attribution.'}
            (temporary/'change_report.json').write_text(json.dumps(report,indent=2)+'\n')
            with (temporary/'transitions.csv').open('w',newline='',encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(['synthetic_fixture','before_date','after_date','transition','pixels','area_ha'])
                for name,count in zip(names,counts):writer.writerow([synthetic,first.isoformat(),last.isoformat(),name,count,count*.04])
            temporary.rename(output)
    return report


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['before','after','study-mask','output']:parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    try:print(json.dumps(compare(args.before,args.after,args.study_mask,args.output),indent=2))
    except (OSError,ValueError,KeyError,TypeError,rasterio.errors.RasterioError) as error:
        parser.exit(1,f'Change comparison failed: {error}\n')
