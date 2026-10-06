# Phase 5 — local UI preview

Objective: inspect saved observations through a working local interface.
Inputs: preserved real Sentinel-2 pair, generated synthetic fixture, or a valid
exported forestguard_phase0.zip. Processing: bounded raster display, stored-data
integrity checks, display-only GeoJSON outlines and traceable CSV/HTML exports.
Outputs: React dashboard, offline raster maps, date comparison, dataset library,
reports and SQLite activity history. No classifier/change model is connected yet.

## Start the built application

From the project folder in PowerShell:

```powershell
.\start_ui.ps1
```

Open http://127.0.0.1:8000. Stop with Ctrl+C. The single FastAPI process serves
the forest landing page and officer login (Harda / Joga, password joga@123), then
both the built React files and API. Node is needed only to build/develop the UI.
Keep this preview bound to loopback; authentication is required before network sharing.

## Reproduce setup/build

Use the existing Python 3.11 environment (Phase 1 instructions) and Node
20.19+ or 22.12+. Tested: Python 3.11.5, Node 24.19.0, React 19.3.0,
Vite 8.3.3, Leaflet 1.9.4, FastAPI 0.142.2 and Uvicorn 0.54.0.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ui-lock.txt
cd frontend
pnpm install --frozen-lockfile
pnpm run build
cd ..
.\start_ui.ps1
```

If pnpm attempts an unavailable store/symlink operation while running a build,
the already-installed Vite CLI is sufficient: `node node_modules/vite/bin/vite.js build`.
For frontend development: `pnpm run dev` with the API running on port 8000.
The dev proxy forwards only /api; production needs no separate frontend server.

Initial dependency acquisition needs Internet; operating the built UI with saved
data does not. Locally retained Python wheels also permit:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links=data/tooling/wheels/windows-cp311 -r requirements-ui-lock.txt
```

## What works

- Overview: actual coverage, acquisition dates, raster dimensions and provenance.
- Maps: pan/zoom/fit, true colour, coverage masks and synchronized date comparison.
- Synthetic sandbox: visibly simulated classes and class-pixel hectare counts.
- Library: saved datasets, search and validated sample ZIP import (10 MiB maximum).
- GeoJSON: polygon/multipolygon outline display (1 MiB maximum); does not approve
  a study boundary or recompute area/classification.
- Reports: downloadable CSV and standalone HTML, with data kind and dates.
- Checks: reuse saved-data verifiers; SQLite records actual checks/imports/exports.

Data, SQLite, uploads, preview caches, environments, node_modules and build
outputs are ignored by Git. Preserve data/ and rebuild frontend/dist after a
fresh checkout. If saved data is absent, generate the synthetic fixture using
docs/DEMO_DATA.md or import a valid sample through the empty-state screen.
Private office files are not served. The API serves only registered raster previews.

## Verification and limits

Run the server, then:

```powershell
.\.venv\Scripts\python.exe scripts/check_ui.py
```

This check requires the preserved real pair and synthetic fixture. It checks
HTML serving, public metadata, all image layers, integrity checks, reports,
valid real sample import and invalid input rejection. It records actual test
activity in the local workspace. Browser checks cover navigation, map layers,
comparison, selection, ZIP/GeoJSON imports, search and downloads. The final API
run passed 15 image responses and nine invalid-input cases. Desktop and narrow
layouts had no horizontal overflow; no browser console errors were observed.
Coverage is observability, not accuracy.

Phase 5's observation UI is delivered ahead of model training at the user's
request. Model inference, suspected forest-loss/gain maps and analysis jobs
remain dependent on Phases 3/4. The real candidate outline remains pipeline-only.

## Dependency licenses

React/ReactDOM, Vite and FastAPI: MIT; Leaflet: BSD-2-Clause; Uvicorn: BSD-3-Clause.
Their packaged notices are retained with installed dependencies. Core raster
dependencies are documented in LOCAL_DEPENDENCIES.md. Real imagery displays
Copernicus attribution; generated data is explicitly identified as synthetic.
No external tiles, fonts, paid services or hosted LLM calls are used.
