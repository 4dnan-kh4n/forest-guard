# Phase 4 change-detection engineering — 9 October 2026

The offline comparison command and exports pass synthetic checks. No real
forest-cover change has been measured. Real cloud training, independently
evaluated classifications and reviewed change references remain prerequisites.
The existing April/December research imagery is not a comparable-season change
pair, and this command does not turn vegetation indices into forest labels.

## Inputs and interpretation

Inputs are two dated single-band classification GeoTIFFs and an explicit study
mask. The supported grid is 20 m EPSG:32643; rasters must match exactly in CRS,
transform and shape. Classified pixels are 0 (non-forest), 1 (forest) or 255
(no data). The study mask contains 0/1 and defines the denominator independently
of date-specific observable coverage. Crops are bounded to 250,000 pixels,
2,048 columns and 30 MiB per file; processing uses 16-row windows.

Required classification tags are `acquisition_date` (ISO date), `model_version`,
`forest_definition_version`, `study_area_version`, `synthetic_fixture`
(`true`/`false`), `class_mapping` (`0:non_forest,1:forest`) and
`season_review_status` (`comparable`). Both maps must share the model, definition,
study version and scope. The study mask must also carry the same study version
and synthetic flag. Real maps additionally require `operational_use_approved=true`.

These metadata declarations do not independently establish accuracy, seasonal
comparability or alignment quality. Before real use, inspect provenance, clouds,
seasonal conditions and stationary landmarks. The command also screens dates:
the later date must be after the earlier date, and the calendar seasons must be
within 45 days cyclically. That conservative initial rule is not a substitute
for review or a guarantee against crop/deciduous seasonal errors. Do not add tags
or approval merely to bypass a rejected comparison.

The prediction command now preserves available study/date/season-review tags
from feature inputs and adds model/definition/class/scope metadata. Missing date
or review metadata is not fabricated; it blocks comparison. Older exports without
this metadata need a provenance-supported re-export. No dashboard integration is
claimed yet.

## Outputs and area calculation

`change.tif` has four classes: 0 stable non-forest, 1 stable forest, 2 suspected
loss (forest to non-forest), 3 suspected gain (non-forest to forest). Value 255
means outside the study mask or not observable on both dates.

`change_report.json` and `transitions.csv` preserve dates, model/study/definition
versions, input hashes, scope, transition counts and hectares. Each 20 m pixel
represents 0.04 ha. Boundary-mask area and common observable area are reported
separately. Before/after cover and net change use exactly the same common valid
pixels; missing/cloud-masked coverage cannot become loss or gain. Empty overlap
is rejected. This is a pixel-centre area approximation, not a surveyed boundary
area or tree-crown measurement.

All single-pixel transitions are retained for inspection. No arbitrary patch
filter is imposed before representative errors are evaluated. These are suspected
cover transitions, not evidence of permanent deforestation, illegal logging,
fire or any person's responsibility. Definition/stand context and changes need
independent evaluation before operational reporting.

## Reproduce and verify

Uses existing NumPy/Rasterio; no new dependencies, downloads or accounts.

```powershell
.\.venv\Scripts\python.exe scripts/check_change.py
.\.venv\Scripts\python.exe scripts/detect_change.py --before data/phase4/synthetic_change_v1/before.tif --after data/phase4/synthetic_change_v1/after.tif --study-mask data/phase4/synthetic_change_v1/study_mask.tif --output data/phase4/my_synthetic_comparison
```

Choose a new output folder. The preserved fixture's coordinates, dates and classes
are fictional; these are not additional Joga satellite observations. Its expected
study mask has 112 pixels (4.48 ha), with 64 commonly observable pixels (2.56 ha)
and 48 unobservable study pixels. Each transition has 16 pixels (0.64 ha); net
change is zero. These numbers verify arithmetic only.

The offline check verifies all transitions, common coverage, no-data, hectares,
JSON/CSV/raster agreement, unchanged inputs, multiple windows, no-network use,
zero-change maps, wrong grids/models/classes, reverse/different-season dates,
unreviewed seasons, scope mismatch, empty coverage and unapproved real maps.
Output overwrite is rejected and failed comparisons publish no partial folder.
Checks are recorded in `data/phase4/engineering_verification.json` and the first
verified output is retained in `data/phase4/synthetic_change_v1/result/`.
The normal CLI run is retained separately in `data/phase4/comparison_run1/`.

`.gitignore` continues to cover generated data, TIFFs and reports; back them up
separately. Track the code and instructions. No Git commit or push was performed.
Next: independently reviewed real labels/splits, evaluated models and suitable
same-season observations, then real change evaluation and application integration.
