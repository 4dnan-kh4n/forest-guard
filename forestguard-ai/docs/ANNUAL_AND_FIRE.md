# Annual observations and recent fire monitoring — 10 October 2026

## Working deliverable

The local officer workspace now has Forest history and Fire detections views.
The officer supplies no satellite files. The development pipeline manages acquisition,
verification and deployment of bounded saved data. The current scope is the
user-confirmed compartment 279 polygon, not all of Joga beat.

Kaggle private notebook version 357023991 completed successfully. The downloaded
2,170,035-byte annual ZIP is preserved locally at
`data/annual/2022_2026_v1/cloud_run2.zip`; registered rasters, previews, source
metadata and checksums are in `data/annual/observations_v1/`.

| Year | Real acquisition | Clear feature coverage | Predicted tree-class extent within clear area |
| --- | --- | --- | --- |
| 2022 | 1 October 2022 | 74.15% | 82.80% |
| 2023 | 8 October 2023 | 74.39% | 79.16% |
| 2024 | 2 October 2024 | 74.60% | 79.89% |
| 2025 | 2 October 2025 | 52.45% | 79.29% |
| 2026 | 2 October 2026 | 79.61% | 75.38% |

These are actual Sentinel observations and our existing Random Forest's weak-map
proxy predictions. The percentage is class extent, **not canopy density**.
Independent forest accuracy and transfer to these October observations remain
unmeasured. Cloud/shadow/missing/uncertain pixels and invalid texture neighbourhoods
are excluded. The 2026 observation is not a completed-year statistic.

Annual viewing uses a 50% minimum usable-feature coverage, while the original
research/training screening default remains 90%. No pixel-quality mask was relaxed.
This permits viewing partial observations, not claiming whole-compartment coverage.

| Pair | Common clear area | Suspected tree-class loss | Suspected tree-class gain |
| --- | --- | --- | --- |
| 2022 → 2023 | 383.48 ha | 13.24 ha | 0.20 ha |
| 2023 → 2024 | 384.56 ha | 1.64 ha | 4.72 ha |
| 2024 → 2025 | 272.40 ha | 6.56 ha | 8.16 ha |
| 2025 → 2026 | 273.16 ha | 9.12 ha | 6.60 ha |

These use common valid pixels on the same native 20 m grid. They are research
class transitions, not independently established deforestation/regrowth. Seasonal
variation and classifier errors still require review. Annual total hectares must
not be subtracted directly when observable coverage differs.

## Why the first run appeared empty

Version 357018392 succeeded but exported zero accepted acquisitions. All processed
2023–2026 candidates failed the previous 90% feature-coverage threshold; the C1
catalogue returned no 2022 candidate in the chosen seasonal window. Its ZIP was
inside a timestamped folder. The corrected notebook retains masks, accepts measured
partial viewing coverage and puts the annual ZIP at `/kaggle/working/` too.

An alternative public `sentinel-2-l2a` catalogue returned 2022 candidates. Legacy
COG scale/offset metadata includes an offset-applied flag and required review.
We instead acquired the reprocessed 1 October 2022 scene from Microsoft Planetary
Computer. Private Kaggle version 357030486 completed in 41.1 seconds and exported
564,886 bytes, preserved at `data/annual/2022_pc_v1/cloud_run3.zip`.
Its original product XML specifies processing baseline 05.10, quantification
10,000 and raw offsets −1,000 for all ten selected bands. These were applied to
the unscaled asset values. XML, source IDs and hashes are retained. Grid, masks,
statistics and archive hashes passed local verification; all four existing years
remain byte-identical in the merged dataset. The prior annual version is retained
at `data/annual/observations_before_2022/`. Source guidance and known metadata issues:
[Element 84 catalogue documentation](https://github.com/Element84/earth-search),
[legacy offset issue](https://github.com/Element84/earth-search/issues/66).
The supplied KML is the geographic boundary; it is not the source of satellite pixels.

## Real recent fire monitoring

The API checks NASA FIRMS NOAA-20 and NOAA-21 VIIRS public South Asia seven-day
CSV feeds. It filters detection centres against the actual polygon and a roughly
2 km surrounding context, retaining timestamps, confidence, radiant power,
source URLs and feed hashes. It refreshes stale data on opening while online and
every 15 minutes while the view stays open. A failed refresh preserves saved data;
saved observations remain available without external services.

The local browser refresh completed at 16:27:15 IST on 10 October 2026:
7,487 NOAA-20 and 6,825 NOAA-21 regional records checked; zero detection centres
inside the polygon and zero within the nearby context. This is not proof no fire
occurred. The image background is saved December 2025 context, not a live fire image.
Satellite observations are not continuous surveillance or verified incident reports.
[NASA FIRMS source and attribution](https://firms.modaps.eosdis.nasa.gov/active_fire/).
NASA archive request 820485 was submitted successfully on 10 October 2026 for
NOAA-20 VIIRS C2, 1 January 2022 through 10 October 2026, custom bounds
[76.76, 22.37, 76.85, 22.44], CSV output. It was processed and downloaded: 66 source records, 44 detection centres in the
polygon/2 km context. Verified yearly counts are documented in CURRENT_STATUS.md. The requested box provides context;
actual reporting must still filter centres using the compartment polygon.

## Reproduce and deploy

1. Build notebook: `.\.venv\Scripts\python.exe scripts/build_annual_notebook.py`.
2. Use the ignored private copy in Kaggle: CPU, Accelerator None, Internet On.
   Export the completed ZIP. The public notebook has no embedded private polygon/model.
3. Import a first verified version:
   `.\.venv\Scripts\python.exe scripts/import_annual_observations.py "PATH_TO_ZIP"`.
   The importer refuses replacing an existing version. Preserve it before replacement.
4. Verify annual classes/coverage:
   `.\.venv\Scripts\python.exe scripts/check_annual_export.py` and
   `.\.venv\Scripts\python.exe scripts/check_annual_changes.py`.
5. Verify fire parsing: `.\.venv\Scripts\python.exe scripts/check_fire_monitor.py`.
6. Package: `.\.venv\Scripts\python.exe scripts/prepare_vercel_data.py`, then
   `.\.venv\Scripts\python.exe scripts/check_deployment_data.py`.
7. Verify hosted API: `.\.venv\Scripts\python.exe scripts/check_hosted_app.py`.
8. Push source changes **and `deployment_data/`**, then redeploy using the existing
   Vercel configuration. Newly added features have been checked locally, not on the
   updated production deployment until that push occurs.

107 selected deployment files total 37,921,461 bytes, below the 40 MiB guard.
Only annual PNG previews, reports and hashes are packaged; full raster/model data
remains local. Git ignores private notebooks, downloaded rasters and training artifacts.

## Verification and next work

Frontend production build, fire parser/geometry/error checks, annual ZIP/mask/coverage
checks, common-area transition conservation and real saved comparison reproducibility
passed. Browser checks verified actual 2022/2023/2026 image views, the new
2022→2023 comparison and successful real NASA refresh. All 112 hosted API checks
passed with five image endpoints and four comparisons. Hosted checks block networking
and verify authentication, saved fire data and unavailable-refresh preservation.

The historical fire additions and their PDF passed actual Vercel checks. Next:
independently evaluate forest references before operational claims. Recent and
annual PDFs also passed actual Vercel downloads.
No new software dependency, paid API or local training stack was introduced.
