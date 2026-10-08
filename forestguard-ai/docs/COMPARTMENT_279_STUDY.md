# Selected study: compartment 279 — 7 October 2026

Update, 8 October 2026: the user confirms the supplied KML boundary is correct.
Use its selected coordinates without further approval. Original field photography
is prohibited; the active next step is the [satellite research protocol](SATELLITE_RESEARCH_PROTOCOL.md).
This user confirmation is distinct from an independently measured registration error.

The user selected the area marked 279 in their Google Earth `comp_PF` screenshot.
This confirms the study target; it does not supply the polygon's coordinate file,
survey date, positional accuracy or canopy classification. Use the name
**Compartment 279 study area**.

## Existing source and verification

The unchanged saved Handia working-plan KML contains one HANDIA/279 feature:
`LGL_Status=PF`, `N_BEAT=RAMPURA`, `N_CRICLE=JOGA`, `block_12=KAKARDA`,
`COMPT=P-279`. These are source attributes, not confirmation of current membership.
Compartment 279 must not be described as the entire Joga beat.

Original KML SHA-256:
`44eb2168008f5e9654d64cce4bfba9b9a3081d509ceb663b340f779c66c34250`.
The source URL and retrieval metadata are retained in the reference folder;
reuse conditions remain unestablished. No new download was needed.

Extraction preserved the source vertices and passed the bounded ring checker:
95 vertices including closure, 4,277 nonadjacent edge comparisons, no detected
crossings/touches/degenerate edges. Spatial registration and current boundary
accuracy have not been established. Outputs are local-only under
`data/reference/handia_working_plan_2022_2032/compartment_279/`.

Source AREA_HA attribute: **519.622059 ha**. The supplied Google Earth display
shows approximately **5.25 km² (525 ha)** and 11.63 km perimeter. These are
different evidence values; the screenshot's rounded area cannot identify the
exact geometry or resolve the difference. Neither value is measured forest cover.

Reproduce into a new output folder:

```powershell
python scripts/extract_handia_boundary.py data/reference/handia_working_plan_2022_2032/handia_27111.kml --compartment 279 --output data/reference/compartment_279_new
python scripts/check_boundary.py data/reference/compartment_279_new/compartment_279.candidate.geojson
python scripts/check_compartment_extraction.py
```

The extractor rejects existing outputs and preserves source bytes. Its original
278 selection remains available; the new check verifies both selections and
rejects invalid/missing compartments without creating labels or area approval.

## Next inputs

The user supplied `comp_PF.kml` on 8 October 2026. Exact coordinates are now
available and the extracted 279 polygon is selected as our provisional research
geometry. No further compartment-selection permission is needed. Current official
boundary status and independent spatial registration remain unverified.

Research permitted dated higher-resolution reference imagery and available
documentary records. Do not obtain prohibited field photos. Record what the
evidence supports: forest trees, scrub, forestry plantation, crops, orchard,
water, settlement or uncertainty. We obtain the free satellite input crops;
the user need not assemble a five-year monthly satellite collection.

Existing March 2024/2025 crops belong to the old 278 pipeline geometry. They
remain technical evidence and must not be relabeled as new 279 imagery or used
to report its area. Acquire/verify a new bounded 279 dataset after exact geometry
and useful reference dates are established. See `FOREST_COVER_DEFINITION.md`.

## User KML import — 8 October 2026

The 1,166,082-byte original is preserved unchanged under
`data/reference/user_comp_pf_2026_10_08/`, SHA-256
`60b45c21637d7d19bb70953715c87e662f58fd5f6d63eaedb60234eb4d197f2a`.
It has 201 placemarks and one matching HANDIA/279/PF polygon. The 82-vertex ring
passes 3,159 nonadjacent edge comparisons. The source includes older administrative
and block-version text; neither its export date nor those attributes certify a
current survey. The incoming file has no beat/circle attribute; RAMPURA/JOGA remain
attributes of the separately preserved working-plan candidate only.

| Metric | User KML | Saved working-plan candidate |
|---|---:|---:|
| Source AREA_HA attribute | 523.391065 ha | 519.622059 ha |
| Projected vector area, EPSG:32643 | 523.643276 ha | 519.872385 ha |
| Projected perimeter | 11,628.213 m | 11,341.043 m |
| Ring vertices including closure | 82 | 95 |

These are geometric/source values, not forest-cover measurements. The sources
are not identical geometries despite nearly identical bounding extents. The
projected area difference is about 3.770891 ha. Different versions/measurement
methods need interpretation; geometry must not be edited to force an area match.
The Google Earth screenshot shows about 525 ha and 11.63 km; its rounded display
does not establish an independent survey or resolve the source differences.
The local comparison report is `geometry_comparison.json` in the incoming folder.

`data/study/compartment_279_v1/boundary.geojson` retains the user's selected
coordinates with a minimal research metadata set. Original source properties and
bytes remain in the private reference copy; unnecessary personal metadata is
excluded from the study artifact. `config/study_area.json` records the selection,
source hash/version and remaining registration/administrative checks. The converter
now assigns the official URL only to the matching preserved official source hash;
it does not misattribute a user export to that download.

The officer request is in `FIELD_OFFICER_DATA_REQUEST.md`; current field observations
can support a new matched-date 279 imagery run without relabeling old 278 crops.
