# Spatial review candidates — 10 October 2026

Working deliverable: `data/labels/compartment_279_spatial_review_v2/` contains
14 unlabeled candidate polygons, their selection report, a dated image comparison,
and a self-contained proposal form. Version 2 corrects the displayed patch size
and selection provenance; version 1 is retained as a superseded intermediate.

The purpose is to broaden spatial coverage beyond the seven original cases, which
were convenience-selected with historical weak-map hints. The new selection uses
only the verified study mask and common-clear image mask. It reads no spectral
bands, vegetation scores, weak land-cover classes or predicted classes when
choosing locations. Embedded images are used only to display the chosen candidates.

## Measured selection and checks

- Divide the saved raster extent into 4 × 4 geographic grid blocks.
- Choose the eligible 100 × 100 m patch closest to each block's centre, using
  deterministic row/column tie-breaking and at least 100 m between patch edges.
- Require all 25 patch pixels and the surrounding 40 m buffer to be within
  common-clear study pixels on the 20 m grid.
- Fourteen blocks supplied candidates; blocks 4 and 16 had none satisfying all rules.
- All 14 footprint rasterizations match 25 usable pixels, without overlap.
- November reference crops have nonzero pixels throughout each selected footprint;
  this does not establish cloud-free reference quality, tree height or class truth.

The existing seven-case records and registry remained unchanged. Offline generation,
mask validation, empty-mask rejection, spacing, geometry, alternate-pack form
validation and overwrite safeguards passed. The previous review-form and comparison
checks also passed. Evidence: `data/phase2/spatial_review_verification.json`.

## Open and reproduce

Open `data/labels/compartment_279_spatial_review_v2/form/review.html` directly in a
browser. The images and form are embedded, so it needs no Internet. Use the review
instructions in [the proposal-form guide](PHASE2_REVIEW_FORM.md).

```powershell
.\.venv\Scripts\python.exe scripts/check_spatial_review.py
.\.venv\Scripts\python.exe scripts/prepare_spatial_review.py data/labels/a_new_spatial_review_folder
.\.venv\Scripts\python.exe scripts/review_labels.py validate "PATH_TO_DOWNLOADED_PROPOSALS.geojson" --pack data/labels/compartment_279_spatial_review_v2/comparison
```

The form validator now accepts the specific preserved comparison pack via `--pack`.
Its original seven-case default remains compatible. It continues to reject changed
geometry/provenance, assigned splits and independence upgrades. Existing output
folders are refused. Inputs, review records and generated forms stay ignored by Git;
scripts, instructions and the progress checklist remain trackable. Preserve this
new folder separately; the earlier Phase 9 archive predates it.

## Scientific status and next decision

The user confirmed on 10 October 2026 that no independent reviewer is available.
All 14 candidates remain **unknown / unreviewed / unassigned / non-independent**.
They are spatially distributed review candidates, not a probability sample, proof
of class balance or an independent evaluation set. Clear/interior-only selection
excludes difficult edges and masked areas; those omissions must be addressed in
an eventual representative evaluation design. Boundary position remains unverified.

There are still no independent reviewed forest-positive references, and only two
accepted Sentinel acquisition dates. The current strict train/validation/test
date policy cannot be satisfied using those two dates alone. Training is not
approved, and no forest accuracy, area or loss/gain result is inferred.

Do not generate more forms or repeat validation to pretend this evidence gap is
closed. Resume scientific labeling when qualified review or sufficiently informative
permitted dated reference evidence becomes available. A separately scoped weak-label
experiment could measure agreement with a reference map, but that would not measure
real forest accuracy or complete the current evaluation requirements.
