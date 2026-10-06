"""Lightweight syntax/source/guard check; does not process imagery locally."""
import contextlib
import io
import json
import runpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
notebook = json.loads((root/'notebooks/00_feasibility.ipynb').read_text(encoding='utf-8'))
code = [c for c in notebook['cells'] if c['cell_type'] == 'code']
for cell in code:
    assert cell['outputs'] == [] and cell['execution_count'] is None
    compile(''.join(cell['source']), 'cloud notebook', 'exec')
source = ''.join(code[0]['source'])
assert source == (root/'cloud/inspect_sample.py').read_text(encoding='utf-8')
compile(source, 'cloud notebook', 'exec')
with contextlib.redirect_stdout(io.StringIO()):
    namespace = runpy.run_path(str(root/'cloud/inspect_sample.py'))
try:
    namespace['run']()
except RuntimeError as error:
    assert 'hosted' in str(error), str(error)
else:
    raise AssertionError('Local runtime must be rejected')
print('PASS: fresh notebook syntax, source equality, empty outputs and local execution guard.')
