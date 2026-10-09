# Phase 0 exit check

Update, 9 October 2026: the user-confirmed compartment 279 research geometry
replaces 278 as the selected target. The current gate decisions and measurements
are in [the feasibility result](PHASE0_FEASIBILITY_RESULT.md). The bounded real
crop and reference-download inspections are finished. Credible forest-positive
reference feasibility remains unmet; reviewed labels and model scores are not
invented to close it. The older status and 278 evidence below remain historical.

Status on 6 October 2026: **incomplete**. No trained model or reviewed labels.
The user keeps both Salyakhedi and Joga compartment 278 for pipeline checks only.
Neither is an approved study area; do not infer approval from a deadline.

## Verified deliverables

- Real Sentinel-2 L2A crop processing, calibration/header agreement, aligned quality
  masks, saved-pixel/grid checks and offline file-integrity verification work.
- Official Handia PDF/KML originals and source metadata are preserved locally.
- One KML feature identifies HANDIA / JOGA / 278 / RF. Its source area attribute
  differs from the historical record; neither is measured forest area.
- The 57-vertex candidate passed a bounded simple-ring topology check: 1,484
  nonadjacent edge pairs tested, no intersections/touches, no zero-length or
  backtracking edges, closed ring and nonzero signed area.
- This topology check assumes one local polygon without holes; it does not prove
  positional accuracy, current administrative membership or field boundaries.
- Empty label-review template prepared; no invented feature geometries or classes.
- Version 6 cloud boundary overlay/mask check exported successfully: 99.0979%
  usable candidate coverage, seven sample and four boundary-review hashes pass.
  No independent positional-accuracy result or study-area approval is implied.
- .gitignore covers downloaded evidence, populated labels and generated reports
  under /data/. Public scripts, empty template and documentation remain trackable.

Reproduce the technical checks without a local training stack:

```powershell
python scripts/check_boundary.py data/reference/handia_working_plan_2022_2032/joga_278.candidate.geojson
python scripts/check_notebook.py
python scripts/verify_bundle.py data/phase0/version3/forestguard_phase0.zip
python scripts/verify_bundle.py data/phase0/boundary_check_version6/forestguard_phase0.zip
```

## Required geography

Obtain authoritative current beat mapping, or explicitly confirm a provisional
study polygon. Current published-plan attributes are evidence, but the candidate
has not been accepted as our study area. Verify geometry registration before
using imagery clipped to it. Keep historical/source/geometric/observable area
separate; investigate differences without editing geometry to force an area match.

Useful request to the responsible office (draft only; not sent):

> Please provide the current Joga beat boundary and compartment membership for
> Handia range, Harda Division, preferably as KML, GeoJSON or shapefile with CRS,
> date/version and access/reuse conditions. The 2022-23 to 2031-32 working-plan
> KML identifies Joga/278/RF with AREA_HA 589.361535; historical project records
> refer to 580.770 ha. Please clarify whether these represent different boundaries
> or periods, and identify village/revenue exclusions.

## Credible-label feasibility

Use config/label_review_template.geojson as an empty schema. Each real reviewed
patch needs the listed provenance, dates, reviewer, uncertainty and class fields.
For the initial feasibility review, seek at least three distinct examples each
of forest, non-forest and unknown. This small demonstration is not a model test
set and cannot establish accuracy. Set final label/sample requirements after review.

Forest examples need dated evidence of forest vegetation consistent with a stated
cover definition. Administrative RF/PF status, green management-map fill and SCL
vegetation alone are insufficient. Exclude annual crops, orchards and other green
land uses from forest. Keep scrub, mixed edges and uncertain tree cover unknown
until evidence supports a class. Record tree-cover versus legal forest distinctions.

Candidate weak reference: ESA WorldCover 2021 v200, CC BY 4.0 with provider
acknowledgement and dataset citation. License checked against
[official data access](https://esa-worldcover.org/en/data-access); not downloaded
or adopted as independent truth. Its 2021 map cannot automatically label 2025
imagery. Comparing 2020/2021 maps also mixes land-cover and algorithm changes.
No independent accuracy score may be derived by testing on reused weak labels.

## Measurable acceptance and evaluation policy

- Data integrity: all exported checksums, source IDs/dates, band order and saved
  grids pass; scale/offset applied once and missing/uncertain pixels excluded.
- Acquisition screening: initially seek at least 90% usable coverage **inside the
  accepted study polygon**; inspect seasonal suitability. This is an acquisition
  screening target, not a measured result or accuracy guarantee.
- Change workflow: identical aligned grids and common valid coverage; record
  both dates and observable area. Exclude uncertainty rather than treating it as loss.
- Labels: reviewed examples for all three review classes, provenance complete,
  chosen cover definition documented. Ambiguous examples remain unknown.
- Evaluation: divide locations/dates before sample extraction. Start planning
  spatial blocks of at least 200 m with at least 100 m separation, then revise
  based on patch sizes/spatial correlation. These are preliminary design choices,
  not frozen splits. Actual locations depend on an accepted study area and labels.
- Keep the independently reviewed test set untouched during tuning. Compare a
  simple baseline and Random Forest using precision, recall, F1, IoU, area error
  and representative failures. Later-date change examples need separate review.
- F1 >= 0.85 / IoU >= 0.70 remain aspirations. Decide attainable performance gates
  after baseline and label-quality review; never present them as achieved scores.
- Delivery: saved-data/local inference, exportable artifacts, bounded resource use
  and honest dates/coverage/version/limits. Free cloud quotas are not guaranteed.

## Exact remaining gates

1. Accepted geography plus spatial registration/current-boundary assessment.
2. Real credible reviewed label examples and finalized forest-cover definition.
3. Actual independent evaluation locations/dates and attainable evaluation criteria.

The project can prepare lightweight tooling independently. It cannot honestly
declare Phase 0 complete or start credible pilot model training from the available
pipeline-only polygons and absent labels.

See `docs/PHASE0_FEASIBILITY_RESULT.md` for the completed engineering assessment
and saved run evidence. Phase 1 foundation is an independent next step while
the scientific pilot gates remain open.
