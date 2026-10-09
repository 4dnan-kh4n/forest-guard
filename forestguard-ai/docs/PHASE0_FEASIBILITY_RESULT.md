# Phase 0 feasibility result

## Current assessment — 9 October 2026

Finer-image source/access checks are documented in
[the reference-source report](HIGH_RESOLUTION_REFERENCE_CHECK.md). Bhoonidhi's
free route has produced verified April 7 and November 9 LISS-IV crops. November
Version 1 (356648963) succeeds in 44.8 seconds; seven hashes/CRC, grid and coverage
counts pass offline. Excluding 106 all-zero centres leaves 209,362/209,468
(99.9494%) nonzero candidates, before cloud screening. All seven review footprints
now have nonzero reference coverage. Visual interpretation is preserved for all
seven November patches: three wooded-cover candidates and one mixed-cover case
remain unknown; three river cases are interpreted non-forest. Height and canopy
threshold evidence remain unresolved. This supplies no independent forest truth.

Earlier April result: final cloud Version 5
and offline integrity checks pass. Only 58.0576% of study centres remain nonzero
reference candidates after excluding suspected all-band-zero fill; cloud screening
and credible forest-positive interpretation remain pending. Seven patches were
visually compared across three dated images: three open-water/non-forest
interpretations and four unknowns are saved separately with AI-assisted reviewer
provenance. No independent reviewed test truth or model accuracy was produced.

Additional reference follow-up: original office-file hashes rechecked (42/42
unchanged); historical 279 planting/management references inspected, with no
matched contemporary patch labels established. ATL08 V007 public metadata offers
three 2025 candidates near our image dates, but their actual small spatial subset
request returns three `nodata` warnings and zero files. See
[the second reference check](ICESAT2_REFERENCE_CHECK.md). This does not change
the scientific exit decision below.

**Engineering feasible; scientific exit blocked by forest-reference evidence.**
Additional historical support is now verified: ETH 2020 predicted-height and
uncertainty crops pass offline hash/grid/mask/statistics checks. Candidate medians
are 4.5, 2 and 12 m, with respective median predictive standard deviations 7, 6
and 8 m. Case 3 is a stronger research priority; none is independently certified
2025 forest. See [historical height result](HISTORICAL_HEIGHT_REFERENCE.md).
This assessment supersedes the historical 278-only assessment retained below.
It closes the targeted acquisition/inspection work, not the unmet evidence gate.

Objective: determine whether the confirmed compartment 279 research polygon,
small real imagery and available reference evidence support a credible first
forest-cover model within the INR 0 budget. Inputs, processing and outputs are
preserved locally and reproducible; no trained model is required in Phase 0.

| Requirement | Verified outcome | Decision |
|---|---|---|
| Study scope | User confirms supplied 279 polygon; exact coordinates retained, source hashes/version preserved, topology checked | Accepted provisional research area; not full Joga beat |
| Geographic accuracy | Internal grid/polygon masks checked; no independent positional error measurement or current administrative verification | Unresolved accuracy limit; no surveyed boundary claim |
| Forest definition | Adopted forest-associated tree-cover criterion, forestry plantation inclusion, agricultural-tree exclusion, unknown cases retained | Defined in `FOREST_COVER_DEFINITION.md` |
| Real small crop | April 3 / December 9, 2025 real observations; 12,338 of 13,099 centres have common usable features (94.19%) | Processing feasible; seasons differ |
| Processing integrity | 27 bundle hashes, CRC, calibration/source provenance, grid, masks, indices, texture and weak-map alignment checked offline | Pass |
| Reference evidence | WorldCover 2021 weak predictions; separate AI-assisted review records three open-water/non-forest cases and four unknowns; original candidates preserved | Credible forest-positive feasibility unestablished; no independent test truth |
| NASA height research | March 2025: 38 interior centres; July 2020: 129; January 2020: 121. Zero pass the quality screen at each date | Not accepted as height truth or forest labels |
| Other requested NASA dates | May/June 2025 and March 2023/May 2024 yield `nodata` warnings | No measurements; service success is not data |
| Resources | 8,367,099,904 bytes total RAM, 815,579,136 available; 48,996,495,360 bytes free storage observed 9 October | Small inspections only locally; heavy work hosted |
| Budget/access/licenses | Existing cloud CPU run/export works; Sentinel license, WorldCover CC BY 4.0 and NASA free/open access decisions documented | INR 0 path demonstrated; quotas remain finite |
| Evaluation policy | Minimum reference-feasibility cases, independent spatial/date split policy and reported metrics defined | Actual labels and frozen splits belong to Phase 2 |

The three downloaded NASA dates contain 288 interior measurement centres in
total, counting observations across dates, not unique independent sites. None
passes the combined screen. This bounded experiment does not establish that all
GEDI data or every other remote-reference route is unusable.

### Acceptance criteria and next evidence task

Retain the existing exit criteria in `PHASE0_EXIT_CHECK.md`: at least three
distinct credible examples of forest, non-forest and uncertainty for feasibility,
with dates, geometry, source/reuse conditions, reviewer and uncertainty. This is
not a representative test set or a training sample-size guarantee. We do not yet
meet the forest-positive criterion. A vegetation index or weak-map prediction
cannot satisfy it.

Data acceptance requires complete provenance, calibration applied exactly once,
all integrity checks passing, valid aligned grids and measured coverage inside
the selected polygon; the initial observation coverage threshold remains 90%.
Change detection needs suitable same-season observations and common valid coverage.
April-versus-December appearance changes are not accepted deforestation findings.

Before Phase 2 sampling, assign independent spatial/date groups and exclude
neighboring or overlapping patches across splits. Reserve a reviewed test set
from tuning. Report precision, recall, F1, IoU, observable-area error and failures;
F1 0.85 / IoU 0.70 remain aspirations until baseline/label-quality review, not
achieved performance or a finalized acceptance promise.

Next evidence task: research a permitted, dated higher-resolution reference or
geolocated written stand/inventory record supporting both tree structure and
land use at candidate patches. No prohibited photography is needed. If evidence
remains insufficient, an explicitly weak-label tree-cover experiment can measure
agreement with its reference map, but cannot claim independently validated forest
accuracy or satisfy this project's original scientific gate.

Current decision: continue reusable tooling and input preparation; hold credible
forest model training/reporting until reference feasibility is established.
Do not rename this result as complete scientific Phase 0. The download backlog is
resolved, and there are no invented labels, accuracy values or fire/loss findings.

Source instructions: `SATELLITE_RESEARCH_PROTOCOL.md`, `GEDI_REFERENCE_CHECK.md`,
`SOURCES.md`. Actual imagery and reference artifacts remain under ignored `data/`;
back them up separately from Git. No new dependency, service or model was adopted
for this assessment. `.gitignore` already covers the new HDF and generated reports.

## Historical assessment — 6 October 2026

6 October 2026. **Engineering pipeline demonstrated; Phase 0 remains incomplete.**
This is a result report, not an approval of a study boundary or model accuracy.

## Objective and inputs

Test whether bounded real Sentinel-2 inputs and official-source candidate geometry
can be processed reproducibly with existing free cloud packages, exported, and
checked offline. The user limits both Salyakhedi and Joga 278 to pipeline checks.

Inputs: official Handia KML's Joga/278/RF candidate, Sentinel-2 Collection 1 L2A
`S2A_T43QFE_20250328T052953_L2A`, acquired 28 March 2025, B02/B03/B04/B08, SCL.
Original source metadata/hashes, calibration rules and versions are preserved.

## Working deliverables and measured results

Private Kaggle Version 6, scriptVersionId **355689497**, completed successfully.
Kaggle displayed 39.6 seconds total runtime; core crop processing recorded 16.636
seconds. Accelerator None, Internet On and Private were confirmed.

Processing reused the tested window-read/calibration pipeline, transformed the
candidate coordinates into the raster grid, rasterized pixel-center inclusion,
intersected that mask with valid coverage, plotted the outline and reopened the
saved mask. All runs remain research/pipeline checks, without model training.

| Observation | Measured result |
|---|---|
| Raster grid | 339 x 307, EPSG:32643, native 10 m |
| Bounding-box pixels | 101,065 |
| Usable bounding-box pixels | 99,389 (98.3417%) |
| Candidate polygon pixels | 58,971 |
| Usable candidate pixels | 58,439 (99.0979%) |
| Pixel-center polygon area | 589.71 ha, candidate geometry only |
| Projected vector area | 589.6453519571437 ha, candidate geometry only |
| KML AREA_HA attribute | 589.361535 ha, source attribute |
| Historical record attribute | 580.770 ha, source attribute |

The close raster/vector areas support mask consistency. They do not resolve the
historical discrepancy or prove current beat extent. Projection/grid/export
choices can affect numerical geometry area; the cause of each difference has
not been established. Do not force geometry to match an attribute.

Outputs are preserved under `data/phase0/boundary_check_version6/`, including
GeoTIFFs, preview, boundary overlay, input geometry, reports, original downloaded
archive and two verified ZIPs. Seven standard sample hashes and four additional
boundary-review hashes passed, as did archive CRC checks. The exported boundary
equals the original candidate JSON; no coordinates were adjusted to imagery.

Reproducible source: `scripts/build_boundary_notebook.py` generates the public
`notebooks/02_boundary_check.ipynb` template and an ignored private execution copy.
`scripts/check_notebook.py` checks all three source notebooks, empty outputs,
shared source, public/private separation and the cloud-only runtime guard.

Existing cloud versions: Python 3.13.15, NumPy 2.1.3, Rasterio 1.5.1, Pillow 12.3.0,
GDAL 3.12.4, Matplotlib 3.10.0. No local training/geospatial stack was installed.

## Image and geography assessment

Visual review shows the candidate overlapping the Narmada bend, a settled/field
area and brown textured vegetation. This is qualitatively consistent with the
official map's river/Joga-village context. The administrative geometry includes
water and settlement; its total area cannot be reported as forest-cover area.
No independent surveyed control points or registration error in metres were
measured. Current beat membership, boundary accuracy and study-area approval remain
unresolved. Polygon/mask alignment is a technical check, not field verification.

The candidate passes small single-ring structural checks (57 vertices, 1,484
nonadjacent edge comparisons). Both candidate and exported report keep
`pilot_approved=false`. The user's pipeline-only choice remains binding.

## Label feasibility result

Clear water provides potential non-forest review examples. Brown textured cover
cannot be reliably separated into forest, scrub, plantations or mixed land use
from this one dry-season 10 m preview alone. The historical descriptions and
management-map colors do not supply contemporary forest ground truth.

ESA WorldCover 2021 is a licensed candidate weak reference, but its age and
model-generated classes prevent treating it as independent 2025 truth. It has
not been downloaded or used to fabricate labels. A reviewed label dataset still
contains **zero examples**; there is no independent train/validation/test split.

The empty review template and evaluation policy are ready in
`config/label_review_template.geojson` and `docs/PHASE0_EXIT_CHECK.md`. The required
next evidence is dated field/reference imagery linked to geographic locations,
with uncertainty and provenance, sufficient to demonstrate all review classes.

## Feasibility decision and remaining gates

- **Proceed for engineering:** lightweight tooling, stored-input validation and
  reproducible artifact handling are feasible within the observed resources.
- **Do not proceed to credible pilot training/reporting yet:** no approved study
  area, no credible reviewed forest labels and no frozen independent evaluation
  locations/dates. These cannot be replaced by successful file-processing tests.
- The original requested Phase 0 completion gate remains unmet. No score, model,
  forest extent or cover-change result is claimed.

Phase 1's lightweight foundation can be built independently while these gaps
remain visible. It must not silently approve a polygon, invent labels, or claim
that the scientific pilot prerequisites have been met. Advanced models and paid
services remain outside the first-release path.

.gitignore continues to exclude all generated evidence under /data/, secrets,
private office records and models; scripts, empty templates and safe summaries
remain trackable. Ignored outputs must be backed up separately from Git.
