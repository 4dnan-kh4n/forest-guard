# Compartment 279: NASA height-reference feasibility

Objective: find dated satellite laser measurements that can support height checks
without collecting prohibited field photographs. This is a reference-data check,
not model training or a forest classification.

## Inputs and acquisition

On 8 October 2026, the user completed Earthdata sign-in. Public NASA CMR metadata
identified GEDI L2A/L2B collection V003 and three intersecting 2025 granule dates:
6 March, 28 May and 23 June. Granule footprints are catalogue search aids; they
do not guarantee measurements inside our study polygon.

Stored inventory: `data/reference/gedi_catalogue/20261008T101954517276Z/`.
Collection IDs: `C3974616071-LPCLOUD` (L2A), `C3974616135-LPCLOUD` (L2B).
The saved collection UMM records declare `FreeAndOpenData: true` and no access
constraints. Retain the data DOI, NASA/University of Maryland credit, source IDs
and processing history when reporting derived measurements. Original licence
records and public Harmony capabilities are preserved alongside the inventory.

NASA Earthdata Search was configured for **Customize Download**, spatial trimming,
HDF output and ten fields for each of eight beams: `degrade_flag`, `delta_time`,
`l2a_quality_flag_rel2`, `l2a_quality_flag_rel3`, `lat_lowestmode`, `lon_lowestmode`,
`rh`, `sensitivity`, `shot_number`, `solar_elevation`.
The interface rounds coordinates to five decimals. Actual requested box:
`[76.78831, 22.39153, 76.82119, 22.41331]`; this differs slightly from the exact
polygon envelope. Inclusion checks subsequently use the stored exact polygon.
No full orbit files were downloaded; original files were roughly 1.4–1.6 GB each.
No passwords, cookies or authentication tokens are stored or used by our scripts.

## Measured result

| Acquisition | NASA subset result | Centres inside exact polygon | Pass initial quality screen |
|---|---|---:|---:|
| 2025-03-06 | 104,730-byte HDF; 81 shots across two full-power beams | 38 | 0 |
| 2025-05-28 | Harmony warning: `nodata`; no returned subset | Not established | Not established |
| 2025-06-23 | Harmony warning: `nodata`; no returned subset | Not established | Not established |

March source: `GEDI02_A_2025065001004_O35285_03_T05201_02_004_02_V003`.
HDF SHA-256: `3e4485ab452309601b43a42e8b6b38d162a4b92757c1a0fef8ac890d1dff93e8`.
Inside the polygon, all 38 shots have release-3 quality flag 1 but **degrade flag
70**. Sensitivity ranges from 0.95591 to 0.97108. The initial conservative screen
also requires degrade flag 0, so none pass. Do not relax the screen simply to
obtain labels. Detailed interpretation of nonzero degradation would need an
evidence-backed revision and geolocation assessment.

Initial screen: point centre inside polygon, release-3 L2A flag 1, degrade flag 0,
sensitivity between 0.95 and 1, finite RH98 inside the product's numerical range.
RH98 is read from column 98 of the 101-column `rh` dataset. Identifiers remain
strings in CSV/GeoJSON to preserve uint64 precision. Raw time and its units are
retained; no unverified conversion to UTC is introduced.
The original filename indicates V003; its embedded `VersionID` attribute is `02`.
Both values are preserved rather than silently rewritten.

March order: https://search.earthdata.nasa.gov/downloads/2685352493
May/June order: https://search.earthdata.nasa.gov/downloads/3963428275
The latter appears successful in Earthdata Search, but its underlying Harmony
workflow explicitly reports **two `nodata` warnings**. Service success does not
mean usable science data. Saved page text and screenshot:
`data/reference/gedi_2025_orders/`.

## Reproduce and inspect offline

The optional HDF reader is pinned in `requirements-reference.txt`.
h5py uses a BSD licence; retain its notices and bundled HDF5 licence if redistributing
the binaries. Official notices: https://docs.h5py.org/en/stable/licenses.html
The Windows/Python 3.11 wheel was 2.9 MB, installed without dependency upgrades.
Observed available RAM: 1,487,240 KiB; free disk after installation: 42,147,815,424
bytes. This small inspection runs locally; heavy preprocessing/training stays remote.

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-reference.txt
.venv\Scripts\python.exe scripts/verify_gedi_catalogue.py data/reference/gedi_catalogue/20261008T101954517276Z
.venv\Scripts\python.exe scripts/check_gedi_subset.py data/reference/gedi_20250306/GEDI02_A_2025065001004_O35285_03_T05201_02_004_02_V003_subsetted.h5 data/study/compartment_279_v1/boundary.geojson
.venv\Scripts\python.exe scripts/inspect_gedi_subset.py data/reference/gedi_20250306/GEDI02_A_2025065001004_O35285_03_T05201_02_004_02_V003_subsetted.h5 data/study/compartment_279_v1/boundary.geojson data/reference/gedi_20250306/new_inspection
```

Existing directories are protected. Stored final March inspection:
`data/reference/gedi_20250306/inspection_v2/` contains the report, all returned
points and CSV, including rejected points and their actual quality fields.
The inspector caps source files at 10 MiB and beam arrays at 2,000 shots. Tests
verify actual shot IDs, inclusion/screen counts and overwrite protection.
Data, private evidence and HDF files remain Git-ignored. Keep a separate backup
of ignored evidence; pushing code alone will not preserve it.

## What this teaches us and next step

Satellite laser observations sample sparse transects. A shot centre inside a
polygon does not guarantee its entire approximately 25 m footprint is inside.
RH98 alone does not establish forest land use or a stand's canopy fraction.
Version 3 quality flags themselves use ancillary land-cover information, so they
do not provide wholly independent forest truth. See the official
[GEDI Level 2 guide](https://lpdaac.usgs.gov/documents/2442/GEDI02_User_Guide_V3.pdf)
and [L2A dictionary](https://lpdaac.usgs.gov/documents/2439/gedi_l2a_v3_product_data_dictionary.html).

This check creates **zero forest labels** and measures no classifier accuracy.
L2B cover subsets were not ordered because the available L2A checks provide no
accepted locations. Next, examine permitted dated reference imagery and other
documented height/land-use evidence for suitable dates and locations. Preserve
uncertain natural forest/plantation/orchard/scrub cases as unknown. If no credible
independent reference is available, explicitly evaluate a tree-cover proxy
separately and keep the forest-accuracy gate open. Freeze independent evaluation
groups before extracting training pixels.
