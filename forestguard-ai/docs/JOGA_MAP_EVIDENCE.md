# Joga geographic evidence: official Handia management map

Inspected on 6 October 2026. Phase 0 remains in progress.

## Source and preserved deliverable

The Madhya Pradesh Forest Department's working-plan catalogue, filtered to
Narmadapuram circle, lists Harda with plan period **2022-23 to 2031-32**.
Its map page lists Handia (हांडिया) as the second map.

- [Working-plan catalogue](https://mpforest.gov.in/publicdomain/Workingplanlibrary/DataUpdation_2.aspx)
- [Harda map list](https://mpforest.gov.in/publicdomain/Workingplanlibrary/ViewMap.aspx?circularid=20277&DivId=10702)
- [Handia map PDF](https://mpforest.gov.in/publicdomain/Workingplanlibrary/WPLuploaddata//27118.pdf)

The downloaded PDF is preserved unchanged under
`data/reference/handia_working_plan_2022_2032/handia_27118.pdf`, with source URL,
retrieval time, HTTP headers and checksum in `source.json`. It contains one page,
12,748,142 bytes. SHA-256:
`c7aadcbda2920e0029c0762f48b24f0eba5bd7c961d85c8423d704cbc7859938`.
Metadata identifies an ArcMap export created in March 2023. Export/upload dates
do not establish the survey date, current field conditions or boundary accuracy.

The local folder also contains a bounded overview rendering, a readable Joga
detail, extracted text and exact PDF georeferencing metadata. Existing bundled
Poppler/pypdf tools were used; no new dependencies or training stack installed.
Observed available RAM was 990,248,960 bytes and C: free space 43,868,565,504
bytes before processing. No full-resolution map raster was saved.

## Verified observations

The title is **Management Map of Handia Range**, Harda Division, Madhya Pradesh
Forest Department. The stated scale is **1:50,000**. Visual review of the page,
legend and detailed excerpt confirms:

- Compartment label **278** alongside **Joga Reserved Forest**, **FV - JOGA**,
  Joga Kalan, Joga Khurd and the Narmada river.
- Neighboring P-320, P-326 and other compartment labels. This corroborates the
  historical records' geographic context without turning them into a beat map.
- The legend distinguishes compartment, coupe, range and division boundaries,
  boundary pillars, forest village, water and working circles.
- Green represents the **SCI working circle**, not measured tree canopy. Neither
  green map fill nor legal/management status is forest-cover ground truth.
- No Joga beat boundary is explicitly identified in the legend. Compartment 278
  must not be assumed to be the entire present Joga beat.

## Georeferencing issue to resolve

The PDF has two geographic viewports: the main map and a separate map-index inset.
Their `/GPTS`, `/LPTS`, viewport boxes and full projection WKT are preserved in
`georeferencing_inspection.json`. Use the main viewport for the main map.

The projection name says `WGS_1984_UTM_Zone_42N`, but its actual parameters include
central meridian **78.416**, latitude of origin **24**, and false northing
**500,000 m**. These differ from standard UTM zone 42N. Do not assign EPSG:32642
or EPSG:32643 based on the name, or transfer the satellite raster CRS to this map.
The coordinate/control metadata needs careful interpretation and alignment checks.
The PDF georeferencing has not been validated. A subsequently discovered official
KML now supplies geographic polygon coordinates directly, so PDF tracing is not
needed for the candidate extraction below. No polygon has been approved yet.

## Official KML compartment candidate

The same working-plan entry has a
[geographic download list](https://mpforest.gov.in/publicdomain/Workingplanlibrary/GoogleMap.aspx?circularid=20277&DivId=10702)
with [Handia KML](https://mpforest.gov.in/publicdomain/Workingplanlibrary/WPLuploaddata//27111.kml).
The original 501,065-byte file and its source checksum are preserved locally.
Its 94 placemarks contain one feature with `Range=HANDIA`, `N_BEAT=JOGA`,
`COMPT_NO=278`, `LGL_Status=RF`, `block_12=JOGA`, `COMPT=278`.
This is official-source evidence associating compartment 278 with Joga beat
within the published plan dataset; it does not certify absence of later changes.

`scripts/extract_handia_boundary.py` creates `joga_278.candidate.geojson` and
`boundary_extraction_report.json` alongside the local KML. Reproduce with:

```powershell
python scripts/extract_handia_boundary.py data/reference/handia_working_plan_2022_2032/handia_27111.kml
```

The source export has an undeclared `xsi` prefix. The converter adds the missing
XML namespace only in memory and records this workaround; original bytes and
coordinates remain unchanged. KML longitude/latitude order is preserved, altitude
is omitted for the 2D boundary, and ring direction follows GeoJSON convention.
See [KML coordinate reference](https://developers.google.com/kml/documentation/kmlreference#coordinates).

Extraction found one polygon with 57 vertices including closure. Finite geographic
coordinates, closed rings and nonzero signed ring area pass structural checks.
The later bounded offline simple-ring check passed (57 vertices, 1,484 nonadjacent
edge comparisons, no intersections/touches or degenerate/backtracking edges).
Positional accuracy and satellite registration have **not** been checked.
The GeoJSON explicitly sets `pilot_approved=false`, `current_boundary_verified=false`
and `forest_ground_truth=false`.

The user explicitly chose to keep this polygon for pipeline checks only. It is
not an accepted study area. The structural pass does not change that decision.

The KML's `AREA_HA` attribute is **589.361535 ha**, whereas the historical project
record reports **580.770 ha**. Preserve both values and reconcile the discrepancy;
neither is a remotely measured forest-cover total. No area has been calculated
from this candidate geometry.

## Next concrete verification

1. Check KML polygon topology, village exclusions and registration against the
   official PDF and independent identifiable imagery features. Use actual PDF
   projection parameters only if interpreting the PDF's geographic coordinates.
2. Reconcile the source-area discrepancy and assess positional error before
   accepting the candidate geometry.
3. Establish whether current Joga beat still contains only 278 or additional compartments.
   If unresolved, consider a separately confirmed compartment-based research area,
   explicitly distinct from beat-wide reporting.
4. Check access/reuse conditions before distributing the map or derived geometry.
   No open redistribution license was established; the PDF is local reference only.
5. Obtain dated independent forest/non-forest/unknown reference evidence before
   creating labels. This management map cannot label satellite pixels by itself.

The user chose to keep the neighboring Salyakhedi crop for pipeline checks only.
That decision remains unchanged. No forest model, reviewed labels, forest area,
change estimate or completed Phase 0 is claimed. No office has been contacted.
