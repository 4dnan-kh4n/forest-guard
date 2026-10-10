"""Measure bounded real inspection and synthetic inference on the existing Windows laptop."""
import ctypes
from ctypes import wintypes
import json
import sys
import tempfile
import time
from pathlib import Path

from inspect_research import inspect
from predict_crop import predict
from backup_research import digest
from register_research_ui import BUNDLE,BOUNDARY,ROOT

if sys.platform!='win32':raise ValueError('This measured resource check is Windows-specific.')


class Counters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
        ['peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile']]


started=time.perf_counter()
observations=inspect(BUNDLE,BOUNDARY)
fixture=ROOT/'data/phase3/inference_fixture_v1'
with tempfile.TemporaryDirectory(prefix='resource_check_',dir=ROOT/'data/phase5') as temporary:
    result=predict(fixture/'model.zip',digest(fixture/'model.zip'),fixture/'features.tif',fixture/'mask.tif',Path(temporary)/'prediction')
elapsed=time.perf_counter()-started
ctypes.windll.kernel32.GetCurrentProcess.restype=wintypes.HANDLE
memory=Counters();memory.cb=ctypes.sizeof(memory)
get_memory=ctypes.windll.psapi.GetProcessMemoryInfo
get_memory.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
assert get_memory(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(memory),memory.cb)
assert memory.peak<512*1024**2, 'Small stored-input checks exceeded the 512 MiB check budget.'
summary={'status':'PASS','elapsed_seconds':round(elapsed,3),'peak_process_working_set_mib':round(memory.peak/1024**2,2),
         'common_real_usable_pixels':observations['verification']['common_feature_valid_pixels'],
         'inference_fixture':'synthetic','real_model_accuracy_measured':False,
         'scope':'Real small-crop inspection plus synthetic saved-model inference; not UI/browser or future full-scale workloads.'}
(ROOT/'data/phase5/resource_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
