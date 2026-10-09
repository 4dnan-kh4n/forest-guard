"""Build a self-contained cloud notebook without private imagery or labels."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
paths = ['scripts/check_boundary.py','scripts/audit_labels.py','scripts/verify_bundle.py',
         'scripts/verify_research_bundle.py','scripts/inspect_local.py','scripts/inspect_research.py',
         'cloud/research_features.py','cloud/train_forest.py','docs/FOREST_COVER_DEFINITION.md']
sources = {name:((root/name).read_bytes().decode('utf-8') if name.endswith('.md')
                else (root/name).read_text(encoding='utf-8')) for name in paths}
bootstrap = """import platform, sys, tempfile
from pathlib import Path
if platform.system() == 'Windows' or not (Path('/kaggle/working').exists() or Path('/content').exists()):
    raise RuntimeError('Use a hosted Kaggle/Colab CPU runtime; do not train on the laptop.')
work_root = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('/content')
source_root = Path(tempfile.mkdtemp(prefix='forestguard_training_source_',dir=work_root))
"""
bootstrap += 'SOURCE_FILES = '+repr(sources)+'\n'
bootstrap += """for name, content in SOURCE_FILES.items():
    path = source_root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding='utf-8')
sys.path[:0] = [str(source_root/'scripts'),str(source_root/'cloud')]
from train_forest import run, metrics
"""
cells = [{'id':'purpose','cell_type':'markdown','metadata':{},'source':[
    '# ForestGuard baseline and Random Forest training\n',
    'Engineering preparation only: no completed training or measured accuracy.\n',
    'Run privately on hosted CPU with Accelerator None. After input upload, no online model service or imagery acquisition is required. Free compute has quotas.\n',
    'Attach the verified research ZIP, exact boundary and evidence-supported frozen label GeoJSON. Current seven review records are not eligible. At least three separate observation dates are needed under the existing date-separated split policy.\n',
    'Forest labels need documented canopy/stand extent, height or height potential and forest-use evidence. Do not alter independence flags merely to pass checks. Model exports use joblib: load only trusted project artifacts.\n']}]
for identifier,source in [('paths',"BUNDLE = None\nBOUNDARY = None\nLABELS = None\n"),('source',bootstrap),
                         ('synthetic-check',"# Synthetic metric fixture only; no project labels or model accuracy.\nassert metrics([0,0,1,1],[0,1,0,1])['f1'] == 0.5\nprint('PASS: synthetic metric calculation only')\n"),
                         ('train',"if any(value is None for value in [BUNDLE,BOUNDARY,LABELS]):\n    raise ValueError('Provide attached input paths only after reviewed splits are ready.')\nmodel_archive = run(BUNDLE,BOUNDARY,LABELS,work_root/'forestguard_model_run1')\nprint('Exported:',model_archive)\n")]:
    cells.append({'id':identifier,'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
                  'source':source.splitlines(keepends=True)})
notebook = {'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},
            'nbformat':4,'nbformat_minor':5}
path = root/'notebooks/08_forest_training.ipynb'
path.write_text(json.dumps(notebook,indent=2)+'\n',encoding='utf-8')
print('Prepared cloud notebook with empty input paths and no private labels or geometry.')

smoke_source = (root/'cloud/synthetic_training_check.py').read_text(encoding='utf-8')
smoke_cells = [dict(cells[0],source=['# ForestGuard synthetic training engineering check\n',
    'Synthetic samples only. Tests fitting, evaluation and export; no forest accuracy or independent reference truth. Private hosted CPU, Accelerator None; no inputs or Internet needed.\n']),
    dict(cells[2]),
    {'id':'smoke-source','cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
     'source':smoke_source.splitlines(keepends=True)},
    {'id':'execute-smoke','cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
     'source':['synthetic_output = run_check(work_root)\n',"print('Synthetic engineering export:', synthetic_output)\n"]}]
smoke_notebook = dict(notebook,cells=smoke_cells)
(root/'notebooks/09_synthetic_training_check.ipynb').write_text(json.dumps(smoke_notebook,indent=2)+'\n',encoding='utf-8')
print('Prepared separate synthetic fitting/export check notebook.')
