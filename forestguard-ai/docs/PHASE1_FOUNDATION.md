# Phase 1: lightweight local foundation

Completed and verified on 6 October 2026, Windows with Python 3.11.5.

Updated and verified on 9 October 2026 for the selected compartment 279 study.
The original inspector remains supported; no new dependencies or training stack
were installed.

## Compartment 279 command

The selected study uses a bounded research bundle with a 20 m analysis grid.
`inspect_research.py` reuses the existing bundle verifier and CSV/JSON exporter,
checks the selected boundary geometry against the saved geometry, and reports
coverage per observation and over their common valid mask. It verifies all 27
bundle files, masks, grids, feature calculations and source metadata offline.
Different boundary-wrapper metadata is allowed; geometry must match exactly.

```powershell
.\.venv\Scripts\python.exe scripts/inspect_research.py --input data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip --boundary data/study/compartment_279_v1/boundary.geojson --output data/phase1/my_279_report
.\.venv\Scripts\python.exe scripts/check_research_local.py
```

Choose a new output folder. The actual first command's outputs are preserved in
`data/phase1/compartment_279_coverage_run1/coverage.json` and `coverage.csv`.
The reproducible check record is `data/phase1/research_verification.json`.

| Observation | Study pixels | Usable feature pixels | Coverage |
|---|---:|---:|---:|
| 3 April 2025 | 13,099 | 12,381 | 94.5187% |
| 9 December 2025 | 13,099 | 12,362 | 94.3736% |
| Common valid mask | 13,099 | 12,338 | 94.1904% |

Checks passed with Python networking disabled and PROJ network access off:
real-data counts, JSON/CSV roundtrip, wrong-boundary rejection, raster-integrity
failure, missing input and overwrite prevention. Original inputs were unchanged.
The older `check_local.py` also passes; `pip check` reports no broken requirements.
The areas in these exports are pixel-centre mask estimates, not surveyed vector
area or forest canopy area. Forest area remains null. The differently seasoned
observations do not establish deforestation; no trained model is involved.
Only this bounded export format is supported, not arbitrary full-scene imports.

## Objective, inputs, processing and outputs

Run a small reproducible command on stored satellite data, with no hosted service
or training stack required. Input is a previously exported sample directory,
including its verified ZIP, checksums, reflectance and quality/mask GeoTIFFs.

The command verifies both archive and extracted files, checks source provenance,
band order, grid, dtype and resolution, recomputes quality coverage in 128-row
windows, and checks saved masks/counts against the cloud report. It supports
native-10 m sample crops up to 512 pixels per side; it rejects full scenes and
non-GeoTIFF drivers. An optional candidate mask gets its own coverage denominator.

Outputs are `coverage.json` and `coverage.csv`. They describe measured imagery
coverage; forest area is null and no prediction is substituted for missing labels.
Source files remain unchanged. Existing reports are never silently overwritten.

## Setup from the project root

Use Python 3.11 (tested patch version: 3.11.5):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-lock.txt
```

Internet is needed for first package acquisition. On this machine, all nine
Windows/Python 3.11 wheels are already retained under
`data/tooling/wheels/windows-cp311/`. With that folder copied from backup, setup
can instead use only stored wheels:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links=data/tooling/wheels/windows-cp311 --only-binary=:all: -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
```

The actual fresh environment was installed using this offline wheel route and
`pip check` reported no broken requirements. The lock is for the tested local
Windows/Python 3.11 environment, not the cloud training runtime. Do not assume
the same native wheels work on another operating system or Python minor version.

## Working command

```powershell
.\.venv\Scripts\python.exe scripts/inspect_local.py --input data/phase0/boundary_check_version6 --output data/phase1/my_first_report
```

Choose a new output folder on each run. The verified first run is preserved at
`data/phase1/coverage_run1/`. The command also works on original sample folders
without a candidate mask. It is an inspector for our exported sample format,
not yet a general image-import interface or forest classifier.

## Verification

```powershell
.\.venv\Scripts\python.exe scripts/check_local.py
```

The real Joga candidate pipeline crop reproduced cloud counts exactly:

| Scope | Total pixels | Usable pixels | Usable coverage |
|---|---:|---:|---:|
| Research bounding box | 101,065 | 99,389 | 98.3417% |
| Candidate polygon | 58,971 | 58,439 | 99.0979% |

The check passed with Python networking disabled. Processing uses local files,
GTiff-only reads and PROJ network access disabled. It also rejected a corrupted
extracted raster, missing input and attempts to overwrite reports; original
source hashes remained unchanged. Test corruption is confined to disposable
copies, not the saved datasets. Results are stored in `data/phase1/verification.json`.

The latest measured inspection call took 0.1476 seconds in the already loaded check
process. This excludes interpreter/native-library startup and is not a general
runtime guarantee. Large-scene processing is deliberately outside this command.
The older crop format without a candidate mask or area-label field also passed;
its missing label is recorded explicitly rather than inferred.

## Dependencies, resources and preservation

Local NumPy 2.1.3, Rasterio 1.4.3 and GDAL 3.9.3 passed the real-data check against
exports produced by cloud Rasterio 1.5.1/GDAL 3.12.4. `requirements.txt` pins the
two direct dependencies; `requirements-lock.txt` pins all nine resolved packages.

Before acquisition, available RAM was 1,109,053,440 bytes and free disk space was
43,880,574,976 bytes. Windows wheel download sizes were checked on PyPI first;
all nine wheels total 38,807,174 bytes. No local scikit-learn, PyTorch, TensorFlow,
web server or frontend stack was installed. Training stays remote.

Wheel names, versions, hashes, sizes, license metadata and bundled notice paths
are retained in `data/tooling/wheels/windows-cp311/wheel_manifest.json`. See
`docs/LOCAL_DEPENDENCIES.md` before redistributing a runtime. Preserve wheels,
data and generated reports in separate backups; Git intentionally excludes them.

## Next concrete step

Phase 2 is data and labels: compartment 279 is the accepted provisional research
area and saved observations are available. Establish credible reviewed labels
and freeze evaluation locations/dates before pixel
sampling. The local foundation does not turn pipeline-only geography or absent
labels into approved scientific inputs. Predictions must remain distinguishable
from measurements and reviewed reference labels.

## Later inference environment update — 9 October 2026

The original Phase 1 runtime above is retained in its lockfile. Separately pinned
CPU inference dependencies are now installed in the working virtual environment;
see [offline inference](OFFLINE_MODEL_INFERENCE.md). No local training is run.
The real imagery inspector and pip dependency check still pass after installation.
