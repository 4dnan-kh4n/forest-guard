"""Prepare a public hosted-CPU notebook with empty input paths and explicit weak-map scope."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'cloud/train_weak_proxy.py').read_text(encoding='utf-8')
cells=[{'cell_type':'markdown','metadata':{},'source':[
    '# ForestGuard exploratory tree-cover-map agreement\n',
    'Weak ESA WorldCover 2021 targets with real image features. No independent forest accuracy, test set, forest area, change or fire prediction. This does not approve the production forest model.\n',
    'Run privately on Kaggle CPU (Accelerator None) or Colab, using the prepared small ZIP and its separately retained SHA-256. No Internet or package installation is needed after attaching inputs. Free compute has quotas. Export the completed model ZIP before session termination.\n',
    'Tree cover includes agricultural trees and plantations; do not rename it forest. Consult the dataset manifest for observation dates and historical reference age.\n']}]
for identifier,text in [('inputs',"BUNDLE = None\nTRUSTED_SHA256 = None\n"),('source',source),('run',
    "if BUNDLE is None or TRUSTED_SHA256 is None:\n    raise ValueError('Attach the prepared weak dataset and provide its independently retained checksum.')\nwork_root=Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('/content')\nexport=run(BUNDLE,TRUSTED_SHA256,work_root/'forestguard_weak_proxy_run1')\nprint('Exploratory export:',export)\nprint('No independent forest accuracy or operational approval.')\n")]:
    cells.append({'id':identifier,'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(keepends=True)})
notebook={'cells':cells,'nbformat':4,'nbformat_minor':5,
          'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}}}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'notebooks/10_weak_tree_cover_proxy.ipynb')
parser.add_argument('--dataset',type=Path,help='Embed a bounded dataset in a private data-folder notebook only.')
args=parser.parse_args()
if args.dataset:
    if not args.output.resolve().is_relative_to(ROOT/'data') or args.output.exists():raise ValueError('Embedded inputs require a new private data-folder notebook.')
    raw=args.dataset.read_bytes()
    if len(raw)>1024**2:raise ValueError('Embedded dataset exceeds 1 MiB limit.')
    encoded=base64.b64encode(raw).decode('ascii');checksum=hashlib.sha256(raw).hexdigest()
    cells[1]['source']=("import base64\nfrom pathlib import Path\nwork_root=Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('/content')\nif not work_root.exists(): raise RuntimeError('Run this private notebook only in hosted Kaggle/Colab.')\nBUNDLE=work_root/'weak_december_dataset.zip'\nBUNDLE.write_bytes(base64.b64decode("+repr(encoded)+"))\nTRUSTED_SHA256="+repr(checksum)+"\n").splitlines(keepends=True)
for cell in cells:
    if cell['cell_type']=='code':compile(''.join(cell['source']),'weak notebook','exec')
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(notebook,indent=2)+'\n')
print('Prepared hosted exploratory notebook; no fitting performed.')
