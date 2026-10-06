# Phase 0 feasibility result

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
