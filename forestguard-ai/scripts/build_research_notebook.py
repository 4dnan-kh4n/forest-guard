"""Prepare public source and a private 279 multi-season cloud research notebook."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
settings = json.loads((root/'config/study_area.json').read_text(encoding='utf-8'))
boundary = json.loads((root/settings['geometry_path']).read_text(encoding='utf-8'))
sources = [('pipeline',(root/'cloud/inspect_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]),
           ('features',(root/'cloud/research_features.py').read_text(encoding='utf-8')),
           ('research',(root/'cloud/multiseason_research.py').read_text(encoding='utf-8')),
           ('reference',(root/'cloud/worldcover_reference.py').read_text(encoding='utf-8')),
           ('execute','research_output = run_research(STUDY, run, research_features, prepare_worldcover)\n')]
for path,selected in [(root/'notebooks/04_multiseason_research.ipynb',None),
                      (root/'data/study/compartment_279_v1/04_multiseason_research.private.ipynb',boundary)]:
    cells=[{'id':'purpose','cell_type':'markdown','metadata':{},'source':[
        '# Compartment 279: satellite-only research screening\n',
        'Private Kaggle/Colab hosted CPU. Internet On; Accelerator None.\n',
        'Three 2025 seasonal windows; 20 m analysis grid; bounded crops.\n',
        'Rank up to 12 quality crops inside the polygon per season; process at most 3 candidates.\n',
        'WorldCover 2021 crop is a historical weak reference, not verified forest labels.\n',
        'Exports calibrated bands, numerical features, masks and a verified ZIP. No labels or trained model.\n',
        'Failed seasonal coverage stays missing; it is never replaced by predictions.\n']}]
    for key,code in [('study','STUDY = '+repr(selected)+'\n'),*sources]:
        compile(code,str(path),'exec')
        cells.append({'id':key,'cell_type':'code','metadata':{},'source':code.splitlines(keepends=True),
                      'execution_count':None,'outputs':[]})
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{
        'name':'python3','display_name':'Python 3','language':'python'}},'cells':cells},indent=2)+'\n',encoding='utf-8')
print('PASS: public/private research notebook sources compile; private geometry stays under ignored data/.')
