"""Compare verified annual proxy classes only on their common clear coverage."""
import hashlib
import json
from pathlib import Path
import numpy as np
import rasterio
from predict_research_change import transitions

ROOT=Path(__file__).resolve().parents[1]


def calculate(folder,report):
    rows=report['observations'];pairs=[]
    if not report['model_available']:return pairs
    for before,after in zip(rows,rows[1:]):
        if after['year']-before['year']!=1:continue
        maps=[];grid=None
        for row in [before,after]:
            with rasterio.open(folder/str(row['year'])/'proxy_classes.tif') as src:
                current=(src.shape,src.crs,src.transform)
                if grid is not None and current!=grid:raise ValueError('Annual class grids differ')
                grid=current;maps.append(src.read(1))
        common=(maps[0]!=255)&(maps[1]!=255)
        changed=transitions(*maps,common)
        counts={str(code):int((changed==code).sum()) for code in range(4)}
        if sum(counts.values())!=int(common.sum()):raise ValueError('Annual area conservation failed')
        pairs.append({'before_year':before['year'],'after_year':after['year'],'before_date':before['date'],'after_date':after['date'],
                      'common_pixels':int(common.sum()),'common_area_ha':float(common.sum())*.04,
                      'common_coverage_percent':100*float(common.sum())/before['study_pixels'],
                      'suspected_tree_proxy_loss_ha':counts['2']*.04,'suspected_tree_proxy_gain_ha':counts['3']*.04,
                      'transition_pixels':counts,'independent_forest_accuracy_measured':False})
    return pairs


def save(folder,report):
    path=folder/'annual_changes.json'
    raw=(json.dumps({'comparisons':calculate(folder,report),'limits':'Research tree-class transitions on common clear coverage, not independently validated deforestation or regrowth.'},indent=2)+'\n').encode()
    if path.exists() and path.read_bytes()!=raw:raise ValueError('Preserve the existing comparison before replacing it')
    path.write_bytes(raw)
    checks=json.loads((folder/'ui_checksums.json').read_bytes())
    checks[path.name]=hashlib.sha256(raw).hexdigest()
    (folder/'ui_checksums.json').write_bytes((json.dumps(checks,indent=2)+'\n').encode())
    return json.loads(raw)


if __name__=='__main__':
    folder=ROOT/'data/annual/observations_v1'
    print(json.dumps(save(folder,json.loads((folder/'annual_report.json').read_bytes())),indent=2))
