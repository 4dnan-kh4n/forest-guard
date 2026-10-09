# Compartment 279: second satellite-height reference route

Research on 9 October 2026. This is reference feasibility work, not a forest model.

## Documentary evidence checked first

The saved inventory contains 42 original office files. All 42 source SHA-256
hashes still match; the original records were not edited. Searching extracted
passages finds real compartment 279 mentions, plus incidental numeric matches
that must not be interpreted as compartment identifiers.

Three relevant workbooks were re-read using the bundled spreadsheet reader.
Their original values, cell addresses, fonts and hashes are preserved privately
in `data/phase0/closure_20261009/279_documentary_cells.json`.
These include a 2017–18 management/regeneration estimate and a root-shoot planting
record heading referring to 2 July 2017. The latter is potentially useful historical
plantation context; a dated heading is not proof of 2025 survival or exact patch
location. Different sheets contain different proposed planting extents.
No patch-linked canopy/height evidence or matching 2025 observation was established.
Compartment-level project areas cannot be painted onto satellite pixels as labels.
Legacy Hindi fonts and damaged characters limit text interpretation.
The private assessment is also recorded in `docs/JOGA_RECORDS_REVIEW.md`.

## ICESat-2 candidate selection

[NASA's data-product documentation](https://icesat-2.gsfc.nasa.gov/science/data-products)
identifies ATL08 as along-track terrain/vegetation height data. The
[Version 7 user guide](https://nsidc.org/sites/default/files/documents/user-guide/atl08-v007-userguide.pdf)
documents product changes including geolocation for 20 m height estimates.
We must inspect product-specific quality and fill values; GEDI field names and
quality rules cannot be copied onto this different product.

Bounded public CMR metadata requests selected the current numbered collection
`C3565574177-NSIDC_CPRD`, ATL08 V007. A 2025 study-box query returned three
granules, with `CMR-Hits=3`; no second page is needed for this particular query.

| Candidate | Source ID | Temporal relevance |
|---|---|---|
| 3 April 2025 | ATL08_20250403172543_02722701_007_01.h5 | Same acquisition day as saved April imagery, different time |
| 3 July 2025 | ATL08_20250703130512_02722801_007_01.h5 | No accepted matching monsoon image yet |
| 10 December 2025 | ATL08_20251210173740_13312907_007_01.h5 | One day after saved December imagery |

Catalogue footprints are not actual valid segment coverage. Nothing in this table
establishes a forest label, independent truth or measured canopy height in 279.
Metadata, exact queries, hashes and original responses are stored in
`data/reference/icesat2_feasibility_20261009/cmr/`.

The documented OpenAltimetry API URL returned HTTP 404 after a network retry.
The TESViS product-list API returned a 9,487-byte JSON response, but no ATL08
product entry. Its separate graphical subset route is documented by
[ORNL's official ATL08 tutorial](https://ornldaac.github.io/tesvis/notebooks/getting_started_icesat2_atl08.html).
No guessed API endpoints, bulk granules or tutorial dependency stack were adopted.

## Actual subset request

The existing signed-in Earthdata browser confirms ATL08 V007 supports spatial
customization. Order
[2688356423](https://search.earthdata.nasa.gov/downloads/2688356423) requests the
three candidates with **spatial trimming enabled** and **HDF output selected**.
The UI-rounded box is `[76.78831,22.39153,76.82119,22.41331]`; inspect returned
segments against the exact saved polygon afterward. The displayed 128 MB describes
original inputs, not a downloaded subset. No original granules were downloaded.

Initial visible status was `In Progress`, 0/1 orders complete. The request
screenshot and page text are saved under the ignored reference folder.
No login credentials were extracted, no new account was created, and no new
legal agreement or paid service was accepted. Existing Earthdata access is reused.

Next: inspect the underlying service outcome and any actual bounded subset files.
Enforce a 10 MiB per-file limit, retain source/hash/DOI provenance, and assess
coordinates, fill values, quality, beam strength and date matching before accepting
a height reference. Height alone still does not establish forest land use or stand
canopy fraction. Independent forest accuracy remains unmeasured; labels created=0.

## Completed service inspection

Earthdata subsequently displayed `Complete` / `Successful` for the order, but
exposed no download files. The underlying
[Harmony workflow](https://harmony.earthdata.nasa.gov/workflow-ui/f47d6dbf-322f-4e42-b0fe-a5bd9fb228a7)
reports **three `warning: nodata` work items**, one per requested granule.
The visible request confirms the intended spatial bounds and HDF format.
Work-item IDs are 397433414, 397433415 and 397433416; the metadata-query item
397433299 succeeded. The actual service outcome is zero returned subset files,
not three usable height observations. No satellite granule was downloaded.

Actual workflow text and screenshot are retained as `workflow_nodata.txt` and
`workflow_nodata.png` under the reference folder. Their hashes, the order URL,
exact requested bounds and the no-label outcome are saved in `outcome.json`.
The candidate metadata hashes and full bounded-page count were independently
checked. All 42 office-source hashes remain unchanged.

This particular 2025 ATL08 route does not supply our missing forest-height
reference. It does not prove that every year, every track or every reference
source is unusable. Continue reference research only with a specific evidence
hypothesis; repeated service-success badges cannot substitute for returned data.
No quality thresholds were weakened, and no forest labels or accuracy scores
were created to convert a negative feasibility result into a completed gate.
