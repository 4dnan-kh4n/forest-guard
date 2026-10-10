"""Reuse the bounded cloud crop pipeline to assess December 2024 against saved December 2025."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
study=json.loads((ROOT/'data/study/compartment_279_v1/boundary.geojson').read_bytes())
sources=[('pipeline',(ROOT/'cloud/inspect_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]),
         ('features',(ROOT/'cloud/research_features.py').read_text(encoding='utf-8')),
         ('research',(ROOT/'cloud/multiseason_research.py').read_text(encoding='utf-8')),
         ('execute',"SEASONS=[('post_monsoon','2024-12-01T00:00:00Z/2024-12-19T23:59:59Z')]\nSCL_SCREEN_LIMIT=4\nPROCESS_LIMIT=2\nsame_season_output=run_research(STUDY,run,research_features)\nprint('December 2024 screening only; no labels, models or forest changes.')\n")]
for path,boundary in [(ROOT/'notebooks/11_same_season_observation.ipynb',None),
                      (ROOT/'data/phase2/same_season_2024_v1/private_run.ipynb',study)]:
    cells=[{'id':'purpose','cell_type':'markdown','metadata':{},'source':[
        '# ForestGuard December 2024 observation screening\n',
        'Compare calendar season with the saved December 9, 2025 observation. Dates alone do not prove comparable weather, phenology or land cover.\n',
        'Private hosted Kaggle/Colab CPU, Accelerator None, Internet On for public COG range reads. Free compute has quotas. Do not run acquisition on the laptop.\n',
        'Screen at most four small scene-classification windows; process at most two candidate crops. Existing calibration/quality/grid pipeline, 20 m analysis resolution, no full-scene in-memory processing.\n',
        'At least 250 MiB cloud disk required. Preserve the exported ZIP and source metadata. Missing/unclear imagery stays missing; no predicted replacement. No weak-map download, labels, training, forest area or loss/gain inference.\n']}]
    for key,code in [('study','STUDY = '+repr(boundary)+'\n'),*sources]:
        compile(code,str(path),'exec')
        cells.append({'id':key,'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':code.splitlines(keepends=True)})
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}},'cells':cells},indent=2)+'\n')
print('Prepared public and private bounded same-season screening notebooks; no acquisition performed locally.')
