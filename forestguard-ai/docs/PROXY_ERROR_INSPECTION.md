# December proxy disagreement inspection — 10 October 2026

The [December experiment](DECEMBER_WEAK_EXPERIMENT.md) has high aggregate historical
map agreement but substantial shrub/crop disagreement. This milestone adds a
reproducible, offline context pack for inspecting that weakness. It assigns no
forest/non-forest labels and does not repair the missing independent reference set.

## Deliverables and selection

`data/phase3/weak_december_error_inspection_v1/inspection.html` contains nine
locations and 27 embedded dated image panels. `diagnostic_cases.geojson` preserves
their context polygons and exact validation sample/row/column. The report retains
model, dataset, image and reference source hashes, reference availability and errors.

Three historical shrub, three crop and three tree-cover disagreements are selected
deterministically from actual December 2025 validation predictions, in row order,
with at least 150 m between centres. The target and prediction refer to the central
20 m pixel; each yellow footprint is a 100 m context, with 300 m surroundings shown.
The context includes neighboring and possibly masked/outside-study pixels. All
classes remain unknown/unreviewed, with unassigned splits and false independence.

The dated views are Sentinel natural-colour crops from 16 December 2024 and
9 December 2025, plus Resourcesat LISS-IV from 9 November 2025. The latter is false
colour NIR/red/green with native 5.8 m detail on 5 m spacing. Its colours are not
land-cover classes, and nonzero pixels do not constitute a cloud mask. Original
product provenance, licenses and source attribution remain preserved.

These cases deliberately come from validation disagreements. They are neither a
probability sample nor an independent test set. Any later changes based on them
constitute validation-guided development; they cannot support new independent
performance claims. The full matrix still contains 220 disagreements / 6,067 pixels.

## Visual observations and remaining uncertainty

Three representative rows (cases 01, 04 and 07) were rendered directly from the
embedded SVG/image views using the already bundled sharp renderer; no new package
was installed, no imagery was synthesized and no cloud processing was required.
The saved scientific figure is `representative_contexts.png`; its small rendering
recipe is retained beside it. The figure was visually inspected.

- Case 01, historical shrub / predicted tree proxy: the finer reference view has
  mottled vegetation-coloured texture. It does not establish tree height, canopy
  percentage or land use, so shrub versus qualifying forest remains unresolved.
- Case 04, historical crop / predicted tree proxy: the reference shows a distinct
  green false-colour patch near the study edge; the surrounding Sentinel view is
  partly masked. This is a reason to review agricultural land use and boundary
  mixing, not proof of crop, forest or a change between dates.
- Case 07, historical tree / predicted other proxy: the finer reference contains
  a dark patch next to vegetation-coloured texture. Mixed pixels and disagreement
  with the old reference merit review; neither water/clearing nor forest loss is
  established from these panels alone.

No current class, cause or height was inferred from colour. These are visual
observations by the development assistant, not independent ground-truth review.
The actual model is left unchanged and remains unapproved for operational use.

## Verification and reproduction

```powershell
.venv\Scripts\python.exe scripts/prepare_proxy_errors.py data/phase3/weak_december_error_inspection_new
.venv\Scripts\python.exe scripts/check_proxy_errors.py
```

Generation verifies the model against its expected dataset before loading the
trusted project artifact; verifies both observation bundles, grid and source
identity; and verifies the saved reference archive. It uses bounded crops only and
performs no model fitting. Existing output folders are refused.

The assert-based check passes with networking blocked: nine actual disagreements,
three cases per group, unique sample IDs, 150 m separation, 27 dated embedded views,
matching 220/6,067 totals, reference nonzero availability, zero new labels, unchanged
source/review records and rejection of existing output or empty error selections.
The scientific figure was visually checked; HTML browser rendering was not checked
because browser control remains unavailable. Open the HTML directly offline.

`.gitignore` covers this generated/private pack. Source scripts and this explanation
remain trackable; the delivery backup recipe includes the new folder. A separate
preservation receipt contains the milestone's hashes and matching E: copy; that
partition shares C:'s physical disk and is not protection against drive failure.

Next: use the documented disagreement patterns to prioritize permitted land-use
reference evidence and a representative review set. Do not train a more complex
network or claim new forest accuracy from this error-selected pack. Independent
forest evidence remains the scientific gate.
