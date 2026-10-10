# Current development checkpoint — 10 October 2026

Officer-facing fire evidence now downloads as a one-page PDF; Reports also has a
four-page annual change PDF containing all five dated images, and a PDF summary
of older observations. JSON remains a technical API format but has no officer
export button. ReportLab exports run locally/offline with explicit dependency pins.
Actual PDF downloads, extracted content and all rendered pages passed verification;
authenticated hosted-mode checks now total 117. A 200-event table rendering fixture
was tested in memory only and is not an observed fire result. NASA's map link was
verified at the mapped Joga centre, 76.805 E / 22.402 N, zoom 14, seven-day window.
New PDF routes/dependencies and frontend links require a fresh Vercel deployment.


A separate Inspection plan now replaces the duplicate Satellite images sidebar
entry. It orders historical comparisons by possible-loss area, shows saved NASA
fire counts with retrieval time, lets the officer select checklist items and exports
those items as CSV. The view links to the correct annual image/change and fire feed.
It does not infer inspection coordinates or incident causes. Selection is temporary;
export it before leaving the section. Browser verification confirmed correct 2023
navigation and a real three-row selected-items CSV download. Priority/CSV checks
and the frontend production build passed. This addition still needs deployment.


Officer UI now opens yearly forest changes and offers only four sections. Selecting
2023 shows estimated net tree-cover decrease of 13.04 ha compared with 2022;
2024 shows estimated net increase of 3.08 ha. Percentages use the same common
clear area, not different annual coverage or measured canopy density. Sources,
exact mapped scope and model limitations are retained in expandable details.
Synthetic fixtures remain preserved for engineering checks but are unavailable
in officer navigation. Unexplained greenness scores and repeated status banners
were removed. All maps ignore mouse-wheel zoom so the page continues scrolling;
zoom buttons remain. Local browser checks and the frontend build passed; yearly
arithmetic checks and 112 hosted API checks passed. This UI update needs redeployment.


New local milestone: actual 2022–2026 annual images and weak-reference tree-cover
estimates, four common-coverage annual comparisons, and refreshed real NASA FIRMS
observations are connected. The 2022 image passed product-XML calibration and
alignment checks; the previous four-year version is preserved. The deployed
JavaScript includes the annual/fire views, but the new 2022 data still requires
the user's push/redeploy. See [annual/fire evidence](ANNUAL_AND_FIRE.md).
NASA historical-fire request 820485 is submitted and awaits processing. Independent
forest evaluation remains open; no missing data has been filled with generated results.

Real-image research change is now implemented: December 2024/2025 proxy
comparison, 94.37% common coverage, 2.40 ha suspected tree-proxy loss and
12.36 ha suspected tree-proxy gain. See [outputs and evaluation protocol](REAL_IMAGE_CHANGE.md).
Independent forest accuracy remains unmeasured. Actual Vercel saved observations,
analysis, source verification, research map, real-image change layers and reports
now work. Ten research/change downloads matched the local SHA-256 checksums.
The missing-data and Git line-ending deployment problems are resolved in the
current deployment. A temporary synthetic run lost one image during live testing;
the subsequent deployment uses its checked bundled comparison. Its before,
after, change and coverage images and four exports were verified live without
the earlier image failure. All six layers survive fresh temporary storage in
tests. A no-store response patch is deployed for app-served HTML, although Vercel
serves the public entry page with its own revalidation cache policy. The in-app
browser retained an old cached entry page; the verification URL loads the current
build. Use a fresh link or clear stale browser cache if an old page is blank.

Resume scientific Phase 2 before approving forest classification or observed
cover changes. The foundation and research application are usable; they do not
establish independent model accuracy.

| Work | Current evidence | Remaining |
| --- | --- | --- |
| Study scope | User-confirmed compartment 279 polygon | Do not report full Joga beat totals |
| Foundation | Bounded offline processing, locked dependencies and saved outputs | Retain reproducibility as changes continue |
| Reference labels | Fresh audit: seven records, zero forest, three non-forest interpretations, four unknown | Independent evidence-supported review; the three interpretations are not independently reviewed |
| Evaluation splits | All seven records unassigned | Freeze representative location/date splits before sampling |
| Model | Our exported Random Forest and real saved proxy map | Independent forest evaluation; historical map agreement is not forest accuracy |
| Change detection | Synthetic workflow plus computed real December tree-proxy transitions | Independent forest validation and reviewed seasonal/alignment errors |
| Application | Real-image changes/images/exports and bundled synthetic workflow verified on Vercel; 97 isolated hosted API checks pass | Independent scientific evaluation; durable hosted activity remains unsupported; stale browser cache may require refresh |
| Fire and future loss | Real recent NOAA-20/21 FIRMS feed connected locally; annual real proxy changes acquired | Archived fire records, credible weather and independent change labels; assess forecasting feasibility before training |

## Current audited deliverable

`data/phase2/resume_20261010_v1/label_audit.json` records the latest audit of
`data/phase2/compartment_279_dataset_v1/labels.geojson`. Schema checks passed;
independent reviewed counts are zero, splits are incomplete and training remains
ineligible. No labels were generated or altered. Data and private references stay
Git-ignored; source and this summary remain trackable.

## Next scientific step

Review the existing dated-image patches against permitted forest inventory or
land-use evidence. No prohibited field photography is required. The prepared
offline review form is described in `PHASE2_REVIEW_FORM.md`; spatial candidates
and their limits are in `PHASE2_SPATIAL_REVIEW.md`.

A qualified independent reviewer is currently unavailable. Additional forms,
repeated fitting or larger models will not resolve this evidence gap. Unknown
cases stay unknown, and development-selected error cases cannot become an
untouched independent test. Fire-data feasibility can proceed separately without
claiming that the first forest-cover release has passed its scientific gates.
