# Exploratory model milestone: complete — 10 October 2026

The December model experiment and disagreement inspection are complete. This
handoff closes that bounded research scope. Scientific Phase 2 and Phase 3 remain
open because independent forest references and an evaluated forest classifier are
absent. A successful weak-map experiment cannot substitute for those requirements.

## What works and how it was checked

| Deliverable | Verification | Decision |
| --- | --- | --- |
| Compartment 279 December observations | Matching 20 m grid; 12,362 common usable pixels / 13,099 (94.37%); source integrity passed | Data check passed |
| Spatially separated weak-map dataset | 4,939 training / 6,067 validation pixels; excluded 200 m strip; actual source features checked | Exploratory data passed |
| Cloud baseline and Random Forest | Dataset-bound export hashes passed; both confusion matrices and four metrics reproduced offline | Research artifacts passed |
| Error-context pack | Nine disagreements, 27 dated views, 150 m centre spacing; originals/review records preserved | Inspection deliverable passed |
| Reproducibility and preservation | Source notebooks/scripts, provenance, false approval flags and checksum backups retained | Engineering handoff passed |

Random Forest historical tree-cover-map agreement: precision 0.968315,
recall 0.987040, F1 0.977588, IoU 0.956158. Majority baseline F1: 0.889641.
Random Forest disagrees on 220/6,067 validation pixels, including 69/78 shrub and
69/244 crop reference pixels. Its production approval remains false and the forest
model loader rejects its format. No observed forest area, loss/gain or fire output
has been established by this experiment.

The learning point is that matching observation seasons improved this experiment,
while class-specific inspection exposed weaknesses hidden by aggregate F1. This
does not prove seasonal matching alone caused the improvement or that the model
recognizes current qualifying forest. The 2021 teacher is older than both dates,
includes agricultural trees/plantations, and is not an independently reviewed test.

## Open the deliverables

- `data/phase2/december_pair_assessment_v3/comparison.html`: offline dated images
  and common-coverage assessment.
- `data/phase3/weak_december_run_v1/`: the model ZIP, evaluation, manifests, receipt,
  class-error breakdown and offline verification.
- `data/phase3/weak_december_error_inspection_v1/inspection.html`: nine locations
  with embedded image contexts; `representative_contexts.png` is the inspected figure.

Full commands are in [the experiment report](DECEMBER_WEAK_EXPERIMENT.md),
[observation assessment](SAME_SEASON_OBSERVATIONS.md) and
[error inspection](PROXY_ERROR_INSPECTION.md). Generated files remain Git-ignored;
retain them through the separately verified preservation packages. Source and docs
are trackable. No commit or push was performed.

## Acceptance gate and next work

The remaining scientific work is concrete:

1. Obtain permitted, dated land-use/forest reference evidence sufficient to support
   the project's stand-height, canopy, area and agricultural-exclusion definition.
   Field photography remains prohibited and a qualified independent reviewer is
   currently unavailable. Unresolved cases stay unknown.
2. Freeze representative, spatially and temporally separated train/validation/test
   locations before sample extraction. The nine error-selected cases cannot become
   an independent test set after they have informed development.
3. Evaluate a forest classifier against that untouched reference set, including
   both class errors, IoU, area error and failure examples. Only then approve a model
   for real forest-cover/change analysis in the application.

We will not add a larger neural network or keep generating error cases as a substitute
for evidence. Existing local application functionality and explicit synthetic checks
can continue independently; they do not change this scientific gate.

Cloud version/runtime for the supplied December export were not accessible. Its
artifact and offline results were verified. HTML browser rendering was not verified;
the representative scientific figure was visually inspected. E: and C: share one
physical disk, so matching E: backups do not protect against physical drive failure.
