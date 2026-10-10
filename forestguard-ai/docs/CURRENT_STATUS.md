# Current development checkpoint — 10 October 2026

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
| Change detection | Verified synthetic workflow and aligned real observations | Accepted forest maps and reviewed seasonal/alignment errors |
| Application | Local maps, checks, exports and research output; user reports hosted login works | Live hosted feature acceptance and durable hosted state remain unverified |
| Fire and future loss | Presentation history is explicitly synthetic | Credible event/weather and multi-year change data; assess feasibility before training |

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
