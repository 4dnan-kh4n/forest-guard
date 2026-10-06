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
location = json.loads((root/'notebooks/01_location_review.ipynb').read_text(encoding='utf-8'))
location_code = [c for c in location['cells'] if c['cell_type'] == 'code']
assert ''.join(location_code[0]['source']) == 'LOCATION_SETTINGS = None\n'
assert ''.join(location_code[1]['source']) == source.split("if __name__ == '__main__':")[0]
for cell in location_code:
    assert cell['outputs'] == [] and cell['execution_count'] is None
    compile(''.join(cell['source']), 'location review notebook', 'exec')
boundary = json.loads((root/'notebooks/02_boundary_check.ipynb').read_text(encoding='utf-8'))
boundary_code = [c for c in boundary['cells'] if c['cell_type'] == 'code']
assert ''.join(boundary_code[0]['source']) == 'BOUNDARY = None\n'
assert ''.join(boundary_code[1]['source']) == source.split("if __name__ == '__main__':")[0]
for cell in boundary_code:
    assert cell['outputs'] == [] and cell['execution_count'] is None
    compile(''.join(cell['source']), 'boundary check notebook', 'exec')
pair = json.loads((root/'notebooks/03_two_date_data.ipynb').read_text(encoding='utf-8'))
pair_code = [c for c in pair['cells'] if c['cell_type'] == 'code']
assert ''.join(pair_code[0]['source']) == 'BOUNDARY = None\n'
assert ''.join(pair_code[1]['source']) == source.split("if __name__ == '__main__':")[0]
for cell in pair_code:
    assert cell['outputs'] == [] and cell['execution_count'] is None
    compile(''.join(cell['source']), 'two-date notebook', 'exec')
compile(source, 'cloud notebook', 'exec')
with contextlib.redirect_stdout(io.StringIO()):
    namespace = runpy.run_path(str(root/'cloud/inspect_sample.py'))
try:
    namespace['run']()
except RuntimeError as error:
    assert 'hosted' in str(error), str(error)
else:
    raise AssertionError('Local runtime must be rejected')
print('PASS: four source notebooks, empty outputs, private-settings separation and local execution guard.')
