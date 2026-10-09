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

liss4_source = (root/'cloud/liss4_reference_crop.py').read_text(encoding='utf-8')
execute = "archives = list(Path('/kaggle/input').rglob(PRODUCT + '.zip*'))\nif len(archives) != 1:\n    raise ValueError('Attach exactly one preserved source ZIP (or .zip.bin).')\nreference_output = run_liss4(archives[0], STUDY)\n"
reference_jobs = [(root/'notebooks/05_liss4_reference.ipynb',None,None),
                  (root/'data/study/compartment_279_v1/05_liss4_reference.private.ipynb',boundary,None)]
november_spec_path = root/'data/reference/bhoonidhi_20261009/november_product/source_spec.json'
if november_spec_path.exists():
    november_spec = json.loads(november_spec_path.read_text())
    reference_jobs.extend([(root/'notebooks/06_liss4_november_reference.ipynb',None,november_spec),
        (root/'data/study/compartment_279_v1/06_liss4_november_reference.private.ipynb',boundary,november_spec)])
for path, selected, source_spec in reference_jobs:
    run_code = execute
    if source_spec is not None:
        run_code = ('SOURCE_SPEC = ' + repr(source_spec) + '\n'
                    "archives = list(Path('/kaggle/input').rglob(SOURCE_SPEC['product'] + '.zip*'))\n"
                    "if len(archives) != 1:\n    raise ValueError('Attach exactly one preserved November source ZIP (or .zip.bin).')\n"
                    'reference_output = run_liss4(archives[0], STUDY, SOURCE_SPEC)\n')
    cells = [{'id':'purpose','cell_type':'markdown','metadata':{},'source':[
        '# Compartment 279: independent-sensor reference crop\n',
        'Private Kaggle CPU; Accelerator None. No Internet required after input upload.\n',
        'Attach the matching preserved archive; retain it as .zip.bin if upload would unpack it.\n',
        'Requires 3 GiB free cloud disk; never loads a full raster into memory.\n',
        'Exports raw digital numbers and NIR/red/green display; no calibrated reflectance, cloud accuracy or labels.\n']}]
    for key, code in [('study','STUDY = '+repr(selected)+'\n'),('crop',liss4_source),('execute',run_code)]:
        compile(code,str(path),'exec')
        cells.append({'id':key,'cell_type':'code','metadata':{},'source':code.splitlines(keepends=True),
                      'execution_count':None,'outputs':[]})
    path.write_text(json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{
        'name':'python3','display_name':'Python 3','language':'python'}},'cells':cells},indent=2)+'\n',encoding='utf-8')
print('PASS: LISS-IV cloud notebook prepared with private geometry separated.')
