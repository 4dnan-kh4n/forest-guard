# Compartment 279 imagery backup and recovery

Objective: preserve the current real imagery independently of Git and recover it
without overwriting working data. SHA-256 checks detect changed files; they do not
establish forest classification accuracy.

## Saved deliverable

`data/backups/compartment_279_imagery_v1.zip` — 6,395,731 bytes, 17 files plus a
manifest. Separately retained archive SHA-256:

```text
ef1e98ec3a0551c60d5fcc28c28cb997e9150aac68d5dc0c837bcd5c9881b8ce
```

Contains the original 27-file research archive, selected compartment boundary,
and 15 dashboard files (including its checksums manifest). Calibration metadata,
scene IDs, dates, license attribution, masks and registered previews are preserved.
It contains no application code, login database, labels, higher-resolution
references, other datasets, training artifacts, Python wheels or frontend build.
Those remain in their existing locations and require separate preservation.

The ZIP is ignored by Git. This on-drive copy protects against accidental file
changes, **not drive failure**. Copy it to existing separate storage when available;
keep this document and its checksum separately. No external copy has been made.

## Verify and recover

From the project folder, using the existing environment:

```powershell
.\.venv\Scripts\python.exe scripts/backup_research.py verify data/backups/compartment_279_imagery_v1.zip --sha256 ef1e98ec3a0551c60d5fcc28c28cb997e9150aac68d5dc0c837bcd5c9881b8ce
.\.venv\Scripts\python.exe scripts/backup_research.py restore data/backups/compartment_279_imagery_v1.zip --sha256 ef1e98ec3a0551c60d5fcc28c28cb997e9150aac68d5dc0c837bcd5c9881b8ce --destination data/recovery/compartment_279_v1
```

The named recovery folder already exists from the successful check. For another
run, choose a new folder inside `data/recovery/`. Existing archives/destinations
are refused. Unsafe ZIP members, altered checksums and missing files are rejected.
Interrupted copies do not publish a completed recovery folder. Recovery uses
bounded streaming and a 64 MiB archive/expanded-data limit.

The recovered folder mirrors project-relative paths: its `data/study/` and
`data/app/registered/compartment-279/` contain the recovered inputs. Keep it
isolated while checking. To populate a fresh checkout, copy these into the matching
absent locations, preserve existing files, then run:

```powershell
.\.venv\Scripts\python.exe scripts/register_research_ui.py --verify
.\start_ui.ps1
```

A fresh checkout additionally needs Python 3.11, the locked dependencies, and a
built frontend. Retain `data/tooling/wheels/windows-cp311/` for offline Python
installation, and retain the built `frontend/dist/` for startup without Node.
See [startup instructions](UI_STARTUP.md).

## Reproduce the checks

```powershell
.\.venv\Scripts\python.exe scripts/check_research_backup.py
```

Measured result: PASS, 17 restored files, source and registered-raster verification,
all six real map-layer PNGs generated from a fresh cache, 12,338 common valid pixels.
Python sockets were blocked throughout. Existing inputs remained unchanged.
Wrong checksum, unsafe member, missing/corrupt file, overwrite and interrupted
copy checks passed. Evidence: `data/phase5/research_backup_verification.json`.
The actual saved ZIP was also restored into `data/recovery/compartment_279_v1`.

The subsequent [fresh installation check](OFFLINE_INSTALL_CHECK.md) installed all
22 UI packages from the retained wheel folder and verified the restored application.
OS Internet was not disabled, and browser startup on a disconnected machine remains
unchecked.

This recovery milestone does not complete Phase 9 or the scientific validation
gates. No actual forest/fire model or independently validated change results exist.
