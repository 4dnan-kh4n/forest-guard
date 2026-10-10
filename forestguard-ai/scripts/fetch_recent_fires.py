"""Fetch small official regional feeds and preserve a versioned compartment report."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.fire_monitor import fetch

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    output=parser.parse_args().output
    if output.exists():raise ValueError('Preserve the existing fire snapshot; choose a new output file')
    boundary=json.loads((ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes())
    report=fetch(boundary)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({k:report[k] for k in ['fetched_at','status','inside_count','nearby_count','sources']}))
