# ForestGuard AI: request for compartment 279 reference data

Status update, 8 October 2026: original field photography is prohibited, and the
user confirms the supplied boundary. The photo-collection instructions below are
archived preparation, not an active request. Do not forward them as a request to
take prohibited photos. Existing permitted documentary records may still help;
current work follows `SATELLITE_RESEARCH_PROTOCOL.md`.

Prepared 8 October 2026. This is a request for records and observed field evidence,
not permission to invent missing values or undertake a new paid survey. The first
goal is to evaluate forest-cover mapping and later suspected cover changes.

## Message to forward to the forest officer

We are developing ForestGuard AI for compartment 279, Handia range, Harda Division.
We need dated, geolocated reference evidence to check satellite forest-cover maps.
We have a Google Earth KML showing 279 as PF; a separate working-plan file lists
the compartment under Rampura beat/Joga circle. Please confirm its current beat,
range, legal status and authoritative boundary version, including any village,
revenue/private-land or river exclusions represented by that boundary.

Please share the current compartment boundary in KML, GeoJSON or shapefile format,
if available, with its survey/revision date, CRS/datum, source and permitted use.
If no digital version exists, a dated official map with identifiable reference
features/boundary pillars and a statement of its status will help. Please clarify
which area record applies: our user file has an AREA_HA attribute of 523.391065 ha;
the saved working-plan file has 519.622059 ha. We will keep the geometry unchanged
and will not treat compartment area as tree-covered area.

For a first feasibility review, please provide existing dated GPS-linked field
photos/survey observations, or record about 10–15 representative, separate patches
during available routine field work. Include tree stands, non-forest land uses,
and uncertain scrub/mixed vegetation across the compartment. For each patch we
need a site ID, coordinates and GPS accuracy, observation date/time, observed patch
extent, original photos with viewing directions, vegetation/land-use notes,
available canopy/height evidence with its assessment method, and the observer's
confidence. Please record uncertainty instead of forcing a forest/non-forest label.

Please also identify any existing dated stock/inventory/plantation records,
site photos, harvest/change maps or records that can support interpretation for
earlier periods. For later fire analysis, existing incident registers with dates,
locations/perimeters and confirmation status would be useful. No new five-year
monthly satellite collection, drone purchase or paid software is required.

Please specify which records we may use internally, for model development and
independent evaluation, and which may be published. Share original files with
their dates and provenance; do not fill missing history with estimates presented
as observations. We can work with partial records and document gaps.

## Priority 1: boundary and administrative context

Ask for these existing records first:

| Record | Required information | How the officer can obtain it |
|---|---|---|
| Current 279 boundary | Geometry; compartment/beat/range/division; PF/RF status; survey/revision date; CRS/datum; exclusions; authoritative version | Export from the division/range GIS records or share the original shapefile set, KML or GeoJSON. A shapefile needs its `.shp`, `.shx`, `.dbf` and `.prj` files together. |
| Boundary status | Whether the submitted 279 outline is current; boundary pillars/control points if available; explanation of different area records | Check the compartment register, relevant approved map/working plan and subsequent revisions. Record unresolved discrepancies rather than editing geometry to match area text. |
| Access/reuse conditions | Whether research, ML labeling/training/evaluation and any public redistribution are permitted | Obtain the department's applicable sharing statement or written permission through its normal procedure; user handles any formal agreements. |

Boundary maps and legal PF/RF status describe administration. They do not label
every pixel inside the boundary as forest. Original survey/observation dates are
needed; a recent file-export date alone is insufficient.

## Priority 2: contemporary reference observations

### Site selection

Start with roughly 10–15 distinct patches, distributed among different accessible
parts of 279, not all beside one road. This first batch establishes label feasibility;
it is not an accuracy test or a sufficient final training dataset. Additional
independent sites and date coverage will be planned after reviewing it.

Cover the land uses actually present: natural tree stands (including open/deciduous
stands), confirmed forestry plantations, fields/orchards, settlement, water, bare
ground, grassland and uncertain scrub/regeneration. Do not force a category quota
when that category is absent. Include difficult mixed cases and describe them as
uncertain. Existing departmental observations can replace a new visit when they
have usable dates, locations, extent and provenance.

### Collection using existing equipment

1. Assign a unique site ID such as `FG279_001`; reuse it on every associated photo,
   note and map. Leave training/validation/test grouping unassigned at collection.
2. Use the existing departmental GPS or a phone with GPS/location enabled. Obtain
   a stable location fix. Record latitude/longitude, WGS84/coordinate format,
   device and its displayed accuracy. Decimal degrees are preferred. If existing
   records use degrees/minutes/seconds or another datum, retain their format/datum
   explicitly so we can convert correctly. Extra decimal digits are not proof of
   GPS accuracy. The coordinate must identify the observed site, not a screenshot's
   map cursor.
3. Record the actual local date and time, including time zone (IST, UTC+05:30).
   Enable camera location tagging if available, but also write coordinates in the
   form because image metadata may be absent or removed during transfer.
4. Identify the patch being described. Prefer a relatively uniform patch with an
   interior spanning several 10 m pixels; a roughly 30–50 m extent is useful when
   it really exists and is observed. Mark its observed extent as a polygon/sketch
   or size plus site notes. A camera point is not a patch boundary, and a view from
   a road does not verify unseen land behind it. Record edge/mixed cases rather
   than enlarging a point into an assumed homogeneous square.
5. Preserve about 3–4 original photos per site when practical: an overview and
   different viewing directions covering the patch. Record each filename and
   approximate direction; canopy/understory views are useful for trees versus scrub.
   Keep original image files and metadata, not just screenshots or compressed copies.
6. Describe the observed vegetation and land use before choosing a final class.
   Record natural versus forestry plantation versus orchard/agriculture, dominant
   vegetation if known, leaf-on/leaf-off condition, and visible bare/burnt/cleared
   areas. Canopy cover may be recorded in broad bands `<10%`, `10–40%`, `40–70%`,
   `70%+`, or `not assessed`. Height may be a measured value, an explicitly marked
   field estimate, or `not assessed`. Record the method. Do not turn a guess into
   an exact measurement. Note whether young trees are expected to reach forest
   stature when supported by site/species evidence.
7. Record observer ID, uncertainty/confidence, and who reviews the interpretation.
   When location accuracy, observed extent, date or vegetation type is insufficient,
   retain the site as uncertain. Phone errors under canopy must be recorded; no
   new survey equipment is required just to start the feasibility review.
8. Transfer the originals with the completed forms/map marks. Group by site ID;
   preserve original timestamps and filenames or record any renaming. Missing
   observations remain blank/unknown. A forest officer's review can resolve cover
   interpretation, but it does not replace missing spatial/date evidence.

Use `FIELD_OBSERVATION_FORM.md` for each site. We will convert reviewed evidence
into the existing provenance-aware `config/label_review_template.geojson`; field
forms are raw observations, not automatically accepted training/test labels.
The observed reference patch can be smaller than a qualifying forest stand;
the minimum stand-area rule is assessed from wider context, not inferred from
the size of one camera view or a small field patch.

### What we will classify

ForestGuard's first target is current tree cover associated with qualifying forest
stands/verified forestry plantations, using the documented stand/canopy/height and
non-agricultural context criteria in `FOREST_COVER_DEFINITION.md`. Crops, orchards,
settlement and water are excluded. Ambiguous scrub/regeneration and mixed pixels
remain unknown. Tree height, land use and exact canopy percentages cannot be
established by four satellite bands alone. A leafless dry-season stand is not
automatically non-forest; it needs reference context/seasonal comparison.

The officer should provide actual observed evidence and uncertainty, rather than
only confirming a label generated by our model. Independently reviewed test sites
will be reserved before tuning; their observations should not be revised to agree
with model predictions.

## Priority 3: historical evidence for cover-change evaluation

Provide existing dated/geolocated inventory or stock-survey plots, original photos,
plantation establishment/maintenance records, harvest or cover-change records,
and maps tied to actual observation dates. Record the site/patch geometry, date
or honest date interval, how change was confirmed, source and uncertainty.

We need evidence for both comparison periods at reviewed locations. Useful dated
2024/2025 records may support those years; observations made in 2026 cannot be
backdated to validate older imagery. If historical evidence is unavailable, we
will choose a new contemporary baseline and arrange revisits at appropriate dates.
Officers need not create observations for every historical month.

Working circles, old management colors or broad area totals provide context and
may guide investigation. They are not independent pixel-level ground truth unless
supported by dated, geolocated field/reference observations. The existing 278
satellite crops will not be relabeled as 279 data. We obtain the free satellite
crops and match seasons/dates to the evidence available.

## Later phases: existing fire and other incident records

If already available, share about five years of existing fire records up to the
actual latest observation date: incident ID, detection/start/end date and time
or interval, location/perimeter, burned area and its measurement method, confirmed
versus suspected status, source report and uncertainty. Add cause only when
documented; otherwise use unknown. Record missing months and patrol/reporting
coverage so that an absent incident entry is not treated as proof of no fire.

These records are useful later and do not delay the first boundary/cover review.
We will obtain appropriate public satellite fire/weather inputs. Identifiable
accused persons, phone numbers and unrelated confidential enforcement details
are not needed for model development. Sufficient independent events may still
be unavailable; a predictive fire model is not promised just because a register
exists.

## Package to return and responsibilities

- Boundary files and a note identifying their current status/date/CRS/reuse conditions.
- One completed field form (or equivalent table) per site, plus original photo
  files linked by site ID and observed patch map/extent.
- Existing historical maps/records in original form, with a note explaining date,
  measurement method, missing periods and meaning of their fields.
- Department/source permission and an observer/reviewer identifier. Personal IDs
  can stay private; public summaries need not expose staff details.

The officer supplies/reviews reference evidence. ForestGuard handles satellite
acquisition, image preprocessing, geographic matching, label audits, split design,
cloud training and independent evaluation. All new software/dataset purchases
remain INR 0. Sensitive evidence and supplied geometry stay in Git-ignored local
data folders with separate backups; only safe schemas/instructions/summaries are
tracked.
