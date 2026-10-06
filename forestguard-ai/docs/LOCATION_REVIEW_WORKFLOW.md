# Phase 0 location review workflow

Objective: compare a bounded real satellite crop with historical site-location
evidence before choosing a confirmed study area or creating forest labels.

The public source template is `notebooks/01_location_review.ipynb`. It contains
no private site coordinates. The builder reads the local coordinate-candidate
file under `reports/joga_records/`, adds a small envelope margin and creates a
private execution copy in that same Git-ignored folder. This envelope is a
research search box, not a survey boundary or the Joga beat polygon.

Run `python scripts/build_location_notebook.py` only when the authorized local
candidate JSON is present. Otherwise use the source notebook with explicitly
reviewed `LOCATION_SETTINGS`. Its required fields are `bbox` (west, south,
east, north in degrees), `points` (label, latitude, longitude), `scene_id`, `area_label`,
`source_datum`, and `plot_datum_assumption`. Do not invent coordinates or silently
assume a historical GPS datum has been confirmed.

Import the private execution copy into the private Kaggle notebook. Keep
Internet On and Accelerator None. The core experiment stays below 512 pixels
per side, uses the existing four-band Collection 1 processing and verifies
metadata/header calibration agreement, saved pixels, grids and the sample ZIP.
The additional plot uses the cloud runtime's existing Matplotlib package;
no packages are installed automatically on the laptop or in the notebook.

Outputs include the standard georeferenced sample bundle plus a point-overlay
figure, execution settings and site-review report. The report distinguishes
usable pixels from usable land-quality pixels (SCL 4/5). Neither is forest
coverage. The overlay explicitly states that the datum is assumed for review
and that no boundary/forest labels are established.

Download saved outputs using Output actions > Download output. Preserve them
under `data/phase0/` and verify the sample ZIP with `scripts/verify_bundle.py`.
Keep source IDs, dates, package versions, quality rules and original source
records. Preserve the earlier river crop for comparison rather than replacing it.

## Reference-label requirements

Historical management proposals and compartment status provide context. They
do not establish that planting occurred or that specific pixels were forest
in a later satellite observation. A tree-cover map can suggest weak labels;
it cannot supply an independent final test set.

Each reviewed label needs geometry, observation date, forest/non-forest/unknown
class, reference evidence and its access/attribution conditions, reviewer,
review date and uncertainty notes. Keep agricultural trees, orchards, scrub and
ambiguous pixels unknown until the forest definition and evidence justify a
class. Separate training, validation and test areas/dates before pixel sampling,
with an appropriate separation buffer to prevent neighboring leakage.

Before Phase 0 completion, establish a confirmed study polygon, demonstrate
credible reviewed examples and set attainable baseline/evaluation criteria.
No model is trained by this location-review notebook.

## Coverage rejection observed

Private Version 4 (scriptVersionId 355677849) completed successfully, but its
29 March 2025 acquisition provided only 290 usable pixels out of 80,032 study
pixels (0.3624%) in the neighboring-site crop. SCL marked 79,742 pixels missing;
only 26 usable pixels were land-quality classes. This is a rejected acquisition
for this crop, not evidence about forest cover. All seven sample file checksums
passed after download. Outputs remain under `data/phase0/location_review_version4/`.

A public EarthSearch catalogue search for March/April 2025 returned a low-cloud
28 March acquisition, `S2A_T43QFE_20250328T052953_L2A`, selected for another
bounded check. Tile cloud percentage and catalogue bounds cannot establish usable
coverage: the actual crop mask must be measured before accepting it.

## Replacement crop verified

Private Version 5 (scriptVersionId 355679695) completed in 47.0 seconds as shown
by Kaggle; recorded core processing time was 18.561 seconds. Its 28 March 2025
crop has 292 x 283 pixels, EPSG:32643, native 10 m resolution. Of 80,032 pixels
inside the research box, 79,924 are usable (99.8651%) and 77,784 are usable
land-quality pixels. These are quality/coverage measurements, not forest totals.
SCL 7 excluded 108 pixels; water accounts for 2,140 usable pixels.

All seven sample SHA-256 checks passed after download. Saved outputs are under
`data/phase0/location_review_version5/`; a separate local checksum manifest covers
the review settings, figure, extended report and original downloaded archive.
Both source notebooks passed syntax, shared-source, empty-output and cloud-only
guard checks. Existing ignore rules cover data and private execution settings,
while the public notebook and instructions remain trackable.

Visual inspection shows rectangular field patterns and extensive brown textured
cover. This one dry-season, 10 m image cannot resolve whether that cover is forest,
scrub or another land use. Points A/B/D/E lie on that textured cover; C is near
field patterns. These are exploratory observations, not reviewed class labels.
The GPS datum and historical survey order remain unverified. No boundary is
drawn. The user has chosen to retain this crop for pipeline checks only. It is
not a confirmed provisional study area; do not use it for pilot model training,
accuracy evaluation or forest-area/change reporting. Preserve both runs as
technical evidence while seeking authoritative Joga geographic information.
