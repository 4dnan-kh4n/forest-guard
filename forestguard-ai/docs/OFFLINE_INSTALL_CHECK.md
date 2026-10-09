# Fresh local installation check — 9 October 2026

A clean Windows Python 3.11.5 virtual environment installed all 22 locked UI
packages from preserved wheels using `--no-index`, without a package download.
The nine original raster-package wheel hashes matched their historical manifest;
a current 22-wheel size/SHA-256 inventory is saved in
`data/phase5/offline_install_v1/wheel_inventory.json` for future checks. The other
13 wheels had no earlier checksum manifest, so this inventory does not establish
their historical integrity. `pip check` reported no broken requirements.
No training stack was installed in this environment.

The isolated project uses restored real compartment 279 inputs, copied Python code,
and the existing frontend build. Its source archive (27 files) and registered
imagery (14 checksummed files) verified successfully. It does not use the live
dashboard database, cached previews, or other datasets.

## Working deliverable and evidence

- Environment: `data/phase5/offline_install_v1/env/`.
- Isolated application: `data/phase5/offline_install_v1/project/`.
- Results: `data/phase5/offline_install_v1/project/offline_app_verification.json`.
- Check source: `scripts/check_offline_app.py`.

The ASGI check passed with Python outbound socket connections and DNS blocked:
landing HTML and two built frontend assets, authorization rejection, officer login,
six real raster PNG layers, vegetation analysis, saved-input verification, CSV/HTML
reports, logout and subsequent access rejection. Both observations retained
12,338 common valid pixels. This is clear observation coverage, not forest accuracy.

The clean environment also started Uvicorn on loopback port 8001. Actual HTTP requests
returned the landing page and healthy API. That temporary server was stopped;
the existing dashboard on port 8000 was not replaced.

## Reproduce from the original project

For a first run, with `offline_install_v1/env` and `project` absent:

```powershell
.\.venv\Scripts\python.exe -m venv data/phase5/offline_install_v1/env
.\data\phase5\offline_install_v1\env\Scripts\python.exe -m pip install --no-index --no-cache-dir --disable-pip-version-check --find-links=data/tooling/wheels/windows-cp311 -r requirements-ui-lock.txt
.\.venv\Scripts\python.exe scripts/check_offline_app.py --prepare
```

Preparation restores the specifically documented imagery backup; it refuses an
existing project destination. Do not remove preserved results merely to repeat
preparation. The environment and project already exist after this milestone.

Repeat checks using them:

```powershell
.\data\phase5\offline_install_v1\env\Scripts\python.exe -m pip check
.\data\phase5\offline_install_v1\env\Scripts\python.exe data/phase5/offline_install_v1/project/scripts/check_offline_app.py
```

The check overwrites only its own evidence file and modifies the isolated database
and previews. On Windows, asyncio needs an internal loopback socket pair before
the outbound-network guard is installed; a sandbox forbidding all loopback sockets
can hang event-loop creation. Normal local execution permits that internal pipe.

To inspect actual server startup:

```powershell
cd data/phase5/offline_install_v1/project
..\env\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8001
```

Open `http://127.0.0.1:8001/`; stop with Ctrl+C. Python is still required to be
installed. Operating this saved build needs no Node runtime; rebuilding the frontend
requires Node and preserved frontend dependencies. Keep the wheel directory,
source code, frontend build and imagery backup separately from a Git checkout,
because generated environments/data/builds remain ignored.

## Limits and next work

This verifies installation and saved-data API processing on this Windows machine.
OS Internet was not disabled, and a fresh browser session on a disconnected machine
was not tested. Rasterio emitted a non-georeferenced warning for display-only PNG
creation; geographic grids remain in the checked GeoTIFFs and map metadata.
No actual forest/fire model, field accuracy or validated forest-change result is
claimed. Shared-network deployment still requires proper per-officer authorization.

Next reliability work: broader reference/label/model/results backup coverage,
interrupted analysis recovery and invalid-input regression. Scientific release
still requires credible reviewed references, independent evaluation splits and
training/evaluation of a real forest model.
