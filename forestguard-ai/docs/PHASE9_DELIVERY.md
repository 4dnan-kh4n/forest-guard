# Phase 9 — current research application delivery

Scope: the current local application, real compartment 279 observations, unresolved
review records and explicitly synthetic trained-model/change fixtures. This is an
engineering delivery checkpoint. It cannot certify a real forest/fire product
before the earlier scientific phases are evaluated.

Current research-application engineering acceptance: **PASS**. This scoped checkpoint
does not close the earlier scientific phases or certify the future real-model product.
The final package must be rechecked when evaluated real models are integrated.

## Acceptance checks

- Reinstall the locked UI and lightweight inference runtime from saved local wheels.
- Restore code, build, real research inputs/references, review records, synthetic
  exported models, results and runtime wheels into a separate folder.
- Validate source checksums, calibration/grid metadata, corrupt/invalid inputs,
  model scope, overwrite guards and comparison output integrity.
- Confirm local browser operation while Python external connections/DNS are
  denied and browser subresources/connections are restricted to the local origin.
- Check interruption before/after result publication, actual termination of an
  owned disposable analysis process, and injected disk-full failures.
- Measure bounded local processing resource use; preserve reproduction instructions.

Evidence lives under `data/phase5/`: failure/recovery/resource/backup verification
JSON files, and `phase9_browser/`. The retained clean environment is
`data/phase5/offline_install_v1/env/`. Actual results and archive checksums are
listed in the delivery receipt and final handoff checklist after verification.

Observed checks: 23 imagery API responses and nine invalid-input cases passed;
six change-layer images/four exports passed. Small real inspection plus synthetic
inference took 2.222 seconds with 133.82 MiB peak process working set. The clean
runtime contains the 22 locked UI packages plus five inference packages installed
from local wheels; `pip check` passes. Saved synthetic predictions matched the
original fixture after recovery. Browser error logs were empty during the guarded
restored-map test. Preview files are display-only; their geographic context comes
from validated GeoTIFF grids and API metadata.

## Start and operate

From the project folder in PowerShell:

```powershell
.\start_ui.ps1
```

Open `http://127.0.0.1:8000/`. Local login: Harda / Joga / `joga@123`.
Use Map workspace for real observations and reports. Change detection currently
uses labelled synthetic classification fixtures. Stop the server with Ctrl+C.
Keep the service bound to loopback; the shared presentation password is unsuitable
for shared-network deployment. There are no external map tiles, model endpoints,
fonts or paid services required for stored-data operation.

## Backup and restore

The final package is `data/backups/research_delivery_v2.zip`; retain its separate
`research_delivery_v2.receipt.json`. The receipt contains the archive SHA-256.
Version 1 is retained as an earlier checkpoint; version 2 also handles disk-full
failure while creating a run directory and atomically publishes generated PNGs.
Archive bounds: 256 MiB total expanded content; 64 MiB per selected source file.
The ZIP covers the listed current research directories, Git-visible source and
the built frontend. Credentials, databases/sessions, private execution notebooks,
full reference scenes, Python environments, node_modules and stale preview caches
are excluded. It is not a backup of every historical download in `data/`.

A checksum-matching external-workspace copy is retained at
`E:\ForestGuard_Backups\2026-10-09\`. C: and E: are Disk 0 partitions. This copy
protects against deleting the workspace, not failure of that physical disk.
Keep an additional copy on existing separate storage when available.

```powershell
$deliveryReceipt = Get-Content -LiteralPath data/backups/research_delivery_v2.receipt.json -Raw | ConvertFrom-Json
.\.venv\Scripts\python.exe scripts/backup_delivery.py verify data/backups/research_delivery_v2.zip --sha256 $deliveryReceipt.sha256
.\.venv\Scripts\python.exe scripts/backup_delivery.py restore data/backups/research_delivery_v2.zip --sha256 $deliveryReceipt.sha256 --destination data/recovery/a_new_release_folder
```

Existing destinations are refused. Restoration checks every file before publishing
the new folder. Never replace live data with an unchecked recovery copy. The actual
verification restore is retained at `data/recovery/phase9_release_v2/`.

For a fresh working copy, enter the recovered folder and create a new environment
using the existing installed Python 3.11 interpreter:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links=data/tooling/wheels/windows-cp311 -r requirements-ui-lock.txt
.\.venv\Scripts\python.exe -m pip install --no-index --find-links=data/phase3/inference_wheels -r requirements-inference.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/register_research_ui.py --verify
.\start_ui.ps1
```

Python itself must already be installed; its installer is not bundled. Node is
unnecessary to run the stored frontend build. Editing/rebuilding the frontend
requires Node and its dependencies; package acquisition may need Internet.

## Reproduce reliability checks

```powershell
.\.venv\Scripts\python.exe scripts/check_research_backup.py
.\.venv\Scripts\python.exe scripts/check_change_recovery.py
.\.venv\Scripts\python.exe scripts/check_phase9_failures.py
.\.venv\Scripts\python.exe scripts/check_inference.py
.\.venv\Scripts\python.exe scripts/check_change.py
.\.venv\Scripts\python.exe scripts/check_resource_use.py
```

For the running original application, run `scripts/check_ui.py` and
`scripts/check_change_api.py` sequentially: their logout checks end the local
presentation account's sessions. Re-login afterwards. Model joblib artifacts may
execute code: load only the trusted project export with its independently retained
checksum. A checksum alone does not establish source trust.

## Retraining and release replacement

1. Finish evidence-supported labels and freeze independent location/date splits.
2. Version the dataset; run the guarded training notebook in a free hosted cloud
   session. Training on the local laptop remains disabled.
3. Export the selected model, definition, feature/band order, preprocessing,
   versions, metrics, error examples and checksums. Keep operational approval false
   until independent performance and local inference have been reviewed.
4. Test a replacement in a separate directory before integration. Retain the
   previous approved model and dataset for rollback; never overwrite them.
5. Repeat reliability checks with the real approved model and representative inputs.

See [training workflow](PHASE3_TRAINING.md), [offline inference](OFFLINE_MODEL_INFERENCE.md)
and [comparison recovery](CHANGE_RECOVERY.md). There is no approved real model to
retrain or roll back yet; current exported models are synthetic engineering fixtures.

## Limits

Internet was not disabled for the whole operating system. The offline check denies
external Python connections/DNS and enforces same-origin browser resource loading;
it establishes stored-data application independence from external services.
Hard power-loss/fsync durability is not claimed. Disk-full tests inject ENOSPC
instead of filling the user's drive. The resource check covers small current inputs,
not unlimited scene sizes or future models. A separate-volume backup does not prove
a separate physical device; physical drive-loss protection needs existing external
storage. Scientific accuracy and shared-network authorization remain release gates.
