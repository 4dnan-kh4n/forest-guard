# Real compartment 279 dashboard — 9 October 2026

The map workspace now defaults to the selected compartment 279 research polygon.
It displays the real saved observations from 3 April and 9 December 2025. The
historical pipeline crop and synthetic sandbox remain separate library entries.
No real forest model or forest-loss/fire finding has been introduced.

## Objective and inputs

Use the verified small research archive and the user's selected boundary;
register only the imagery and geographic metadata needed by the application.
Original files remain unchanged. This is the user-confirmed compartment polygon,
not a confirmed full Joga beat boundary or independently surveyed registration.

Source bundle SHA-256:
`bdc1f3b07c91446bfd6bcf504f4fbed516ec104509e4993b5e0504073558fbfb`.
UI imagery version: `imagery-279-bdc1f3b07c91446b`.
Study version: `compartment-279-user-kml-v1`.
Source scenes: `S2B_T43QFE_20250403T053649_L2A` and
`S2B_T43QFE_20251209T053610_L2A`.

The archive's 27 source files are verified before registration. Fourteen local
dashboard files preserve exact selected observations, boundary, research report
and registration metadata; the derived common mask is checked against both
usable masks. File hashes, source dates, counts, resolution and versions are
checked. The registration is a small crop copy, not a new large download or
local training step. No dependency or service was added.

## Reproduce

From the project folder:

```powershell
# First registration only; an existing registration is never overwritten.
.\.venv\Scripts\python.exe scripts/register_research_ui.py
# For the already prepared workspace:
.\.venv\Scripts\python.exe scripts/register_research_ui.py --verify
.\.venv\Scripts\python.exe scripts/check_research_registration.py
.\start_ui.ps1
```

Open http://127.0.0.1:8000/, sign in with the existing local presentation account,
then choose Map workspace. Compartment 279 is selected by default. Compare shows
both dates, with pan/zoom/fit and the selected boundary outline. True colour,
Common clear pixels and Vegetation signal use stored inputs. Check saved image
verifies the registration and original source archive again.

Analyze saved images computes a vegetation indicator over common usable pixels;
it does not classify forest or estimate loss. The banner makes the seasonal and
model limitations explicit. A 20 m analysis grid is correctly displayed; this
does not increase the native detail of coarser bands. NDVI bands are selected by
their stored names, rather than assuming a fixed band position.

CSV/HTML exports include actual dates, coverage, scene IDs, dataset/study version,
CRS, resolution, band order, source-license URLs, attribution and source bundle
hash. The HTML keeps a compact observation table and puts provenance separately.
No private office records or review interpretations are served by this registration.

## Verified observations and limitations

The study mask contains 13,099 pixels. April has 12,381 usable feature pixels
(94.5187%); December has 12,362 (94.3736%). The common mask has 12,338
(94.1904%). These are measured observability counts, not forest area or accuracy.
Both indicator summaries use those same common pixels. April and December are
different seasons; no median-difference change conclusion is generated for this
dataset. Forest area and model version remain unset.

Offline registration checks passed with networking disabled. Corrupt copies,
false coverage with internally consistent hashes, unsafe manifest members and
output overwrite were rejected; original source hashes were unchanged. Results:
`data/phase5/research_registration_verification.json`.

The final local API regression passed 23 image responses, nine invalid-input
cases, sample import, authentication, vegetation analysis and compartment 279
date/count/outline/export checks. Results: `data/phase5/ui_api_verification.json`.
The synthetic change API also passed after real-data integration. Production
build and dependency checks pass.

Browser verification covered both dates, all three image layers, two loaded
boundary overlays, date selection, map fitting, source verification and an actual
HTML download containing the source hashes and seasonal limit. Observed desktop
viewport was 1280 × 720 with no horizontal overflow. Requested mobile viewport
overrides did not apply in this browser session, so this milestone does not claim
a mobile check. Screenshots and browser results are preserved in
`data/phase5/compartment_279_dashboard_v1/`.

## Next step and preservation

Keep `data/app/registered/compartment-279/`, the original archive/boundary and the
study/reference data in a separate backup. They remain ignored by Git; track the
scripts, application changes and these instructions. No commit or push was made.
The original Copernicus attribution and license links are preserved. The existing
20 m preprocessing/calibration settings remain in the copied research report and
original source bundle.

Real forest-positive reviewed references, independent evaluation splits, trained
and evaluated real models, same-season change observations and change references
remain outstanding. This milestone connects real observations to the application;
it does not complete those scientific gates. Full offline installation, broader
artifact backup restoration and interrupted-job validation remain release work.
Saved imagery now has a verified isolated recovery path; see
[backup instructions and measured checks](RESEARCH_BACKUP.md).
