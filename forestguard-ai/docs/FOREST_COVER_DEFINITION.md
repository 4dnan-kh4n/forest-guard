# ForestGuard cover definition v1 — 7 October 2026

Reference availability update, 8 October 2026: the user confirms the selected 279
boundary and reports that original field photography is prohibited. We will not
request or obtain prohibited photos. Follow the [satellite research protocol](SATELLITE_RESEARCH_PROTOCOL.md)
for permitted remote references. Feature richness does not replace independent
reference evidence; unsupported height, land use and forest-origin cases stay unknown.

This is the project's operational reference-label definition, selected under the
user's instruction to decide the cover target. It maps current forest-associated
tree cover, rather than legal forest designation or all green vegetation.

## Target and interpretation

Use a FAO-informed stand criterion: tree-covered patches larger than 0.5 ha,
with tree canopy cover above 10%, and trees ordinarily exceeding 5 m or supported
by reference evidence as able to reach that height in situ. Exclude predominantly
agricultural and urban land use. The underlying criteria are described in the
[FAO terms and definitions](https://fra-data.fao.org/definitions/fra/2020/en/tad).

This is a current-cover research target, not a complete FAO forest-land-use
inventory. FAO forest land can include temporarily unstocked land and young
stands expected to regenerate. Our first cover map must not automatically label
bare land as present tree cover or infer deforestation from a temporary gap.
Minimum stand area is a contextual label/mapping rule, not the size of a single
10 m pixel. Report qualifying classified cover extent, not an exact sum of tree
crown areas or a survey-quality canopy-density inventory.

The Indian national forest-cover definition uses a different minimum area and
can include orchards. We intentionally exclude agricultural orchards under this
project's requirements and must not claim our area estimates reproduce FSI's
national classification. See the [FSI 2023 report](https://fsi.nic.in/uploads/isfr2023/isfr_book_eng-vol-1_2023.pdf).

## Reference classes

| Class | Evidence and treatment |
|---|---|
| `forest` | Dated independent evidence supports a qualifying stand and forest use/context. Include natural forest and confirmed forestry plantations; tag plantation origin separately when known. Seasonal leaf loss alone does not establish cover loss. |
| `non_forest` | Dated evidence supports crops, orchards/agricultural tree systems, settlements, roads, water, bare ground or grassland outside a qualifying forest stand. Individual boundary/road/water pixels are not forest merely because they lie in a PF/RF polygon. |
| `unknown` | Scrub versus tall-tree cover, young regeneration, mixed edges, uncertain plantation use, insufficient canopy/height evidence, stale references or unresolved interpretation. Exclude from binary training/evaluation until reviewed. |

Cloud, shadow, missing data and unusable observations are quality exclusions,
not evidence for the `non_forest` class. Keep their mask separate from reviewed
reference uncertainty.

Four Sentinel-2 bands and a green-looking preview cannot establish tree height,
exact canopy percentage or land-use history on their own. Those criteria require
reference evidence and human review. The first baseline evaluation will determine
whether the selected bands/seasons distinguish the defined classes reliably;
no accuracy is assumed from this definition.

## Required reference information

Reuse `config/label_review_template.geojson`; do not invent a second label schema.
Each reviewed patch needs location/geometry, observation and reference dates,
reference source and reuse conditions, reviewer, confidence and uncertainty,
study-area version and eventual evaluation group.

Suitable inputs include original dated geotagged field photos with site notes,
dated geolocated field/compartment survey records, and permitted dated higher-
resolution reference imagery sufficient to distinguish tree stands and land use.
A ground photo needs spatial context: GPS accuracy, viewing direction, the patch
it depicts and multiple views/site notes where one image is insufficient. A single
photo does not establish a whole compartment's canopy cover or tree heights.

Current 2026 observations support matching contemporary imagery; they do not
automatically label March 2024/2025. We can select satellite dates after reviewing
the available reference dates. Historical change validation needs evidence for
both periods. Weak maps or model predictions do not provide independent test truth.

For initial feasibility, seek several clearly supported forest/non-forest patches
and representative uncertain cases, distributed around the selected area. This
initial review establishes whether labeling is feasible; the required final
sample counts, independent sites and date separation are set during Phase 2.
Review available source permissions before adopting reference imagery; do not
scrape Google Earth imagery or assume a screenshot is freely redistributable
training data. The user's map screenshot is currently location-selection evidence.

Preserve the definition version in future dataset/model/report manifests.
