"""Build the fresh cloud notebook from this project's source; no old artifacts."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root/'cloud/inspect_sample.py').read_text(encoding='utf-8')
notebook = {
    'nbformat': 4, 'nbformat_minor': 5,
    'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                 'language_info': {'name': 'python'}},
    'cells': [
        {'id': 'purpose', 'cell_type': 'markdown', 'metadata': {}, 'source': [
            '# ForestGuard AI — fresh feasibility experiment\n',
            'Create a new private notebook. Hosted CPU only, Accelerator None, Internet On.\n',
            'No automatic package installation. No model training or forest-area claims.\n',
            'Inspect one provisional research crop; its box is not the Joga beat boundary.\n',
            'Download the verified ZIP before ending the cloud session.\n']},
        {'id': 'sample', 'cell_type': 'code', 'metadata': {}, 'execution_count': None,
         'outputs': [], 'source': source.splitlines(keepends=True)},
    ],
}
diagnostic = root/'cloud/check_calibration.py'
if diagnostic.exists():
    notebook['cells'].append({'id':'calibration', 'cell_type':'code', 'metadata':{},
        'execution_count':None,'outputs':[],
        'source':diagnostic.read_text(encoding='utf-8').splitlines(keepends=True)})
target = root/'notebooks/00_feasibility.ipynb'
target.parent.mkdir(exist_ok=True)
target.write_text(json.dumps(notebook, indent=2)+'\n', encoding='utf-8')
print('Built:', target)
