# Dated image reference feasibility — 9 October 2026

Current execution update: the first upload did not leave a saved dataset. The
retry completed with the original archive retained as `.zip.bin`; the
[private source dataset](https://www.kaggle.com/datasets/adnankh4n/forestguard-279-liss4-april-reference)
shows one 626.39 MB file, is ready and is attached to the private crop notebook.
After the diagnostic runs, final Version 5 (356634805) completed successfully on
Accelerator None and its small crop bundle passed offline checks. Nonzero
reference candidates cover 58.0576% of study centres; clouds and credible forest
labels remain unverified. Scratch bands use /kaggle/temp rather than the export
folder. Historical observations below describe earlier attempts.

## Verified final result

### Patch interpretation and second-date footprint check

The offline comparison preserves seven numbered 120 m patches and approximately
360 m surrounding context on April 3 Sentinel, April 7 LISS-IV and December 9
Sentinel images. Case 1/2 reference patches are entirely suspected fill. Case 3
vegetation and case 4 field/mixed cover remain unknown: colour and pattern alone
do not establish height or all relevant land uses. Cases 5/6/7 lie within the
river in all three images and are recorded as high visual-confidence open-water,
non-forest interpretations. These are AI-assisted interpretations, not field or
forest-staff validation, and are not independent test truth. All splits remain
unassigned; the provenance audit does not authorize training.

Saved comparison: `data/labels/compartment_279_liss4_comparison_v4/comparison.html`.
Review records and seven screenshots remain in the preserved v2 folder, alongside
`satellite_interpretations.geojson` and `interpretation_audit.json`. The original
seven-case review pack remains unchanged. No forest-positive labels were assigned.

The official November 9 metadata for
`RAF09NOV2025046306009700056SSANSTUC00GTDD` has SHA-256
`7fae8bd30a3b469644978b989122a62e3044180bb48b22c0da9e5a67ec48b4a1`.
Rasterizing its actual Image corners, rather than the rectangular Product corners,
onto the existing study grid predicts 209,356 of 209,468 centres (99.9465%) inside
the image footprint. This estimates swath coverage only; cloud percentage is
unavailable and actual fill/cloud/registration still require the pixels. Three
full bands would occupy 1,796,899,980 uncompressed bytes; compressed download size
is unknown. No November full scene has been downloaded. Metadata and the footprint
assessment are preserved under `data/reference/bhoonidhi_20261009/november_candidate/`.
Use `scripts/check_liss4_footprint.py` to reproduce this bounded check.

Earlier acquisition follow-up: the portal presented Login and an empty free cart;
adding the November product opens sign-in rather than adding a download. A user
session refresh is pending. No new terms were accepted and no November download
was started. Latest resource check: 46,628,470,784 bytes free on C: and
1,051,381,760 bytes available RAM out of 8,367,099,904. Small archive inspection
is feasible, but full raster processing remains cloud-only. Actual preparation
is saved as `november_candidate/acquisition_preparation.json`; source archive
checksum and compressed size deliberately remain null until acquisition.

The user refreshed the session and the free November cart was confirmed, SID
`20261009_MFN010817`. The complete archive is now 551,494,580 bytes, SHA-256
`3f0f9e0772fa613d5f850e03832c0a61c450d1c253ad79d27a2cca58561a70cb`.
The original download and preserved project copy match. ZIP-directory inspection
and small metadata reads pass; each full band entry is 599,101,118 bytes.
Full-band CRCs are deferred to streamed cloud extraction. The source archive,
inventory and actual source specification are under
`data/reference/bhoonidhi_20261009/november_product/`. A `.zip.bin` copy preserves
compression during Kaggle upload. Source/shape/date validation and the prior April
crop still pass; no local full-scene raster preprocessing occurred.

Notebook `notebooks/06_liss4_november_reference.ipynb` contains no private polygon.
Its executable copy is
`data/study/compartment_279_v1/06_liss4_november_reference.private.ipynb`.
Run the private copy with exactly the November archive attached, Accelerator None,
3 GiB free cloud disk and no need for Internet once the input is attached. Download
`liss4_279_reference.zip` after success, preserve it in a new November output folder,
then run `scripts/verify_liss4_crop.py` against it. The identical output filename
is isolated by notebook/output folder; never overwrite April outputs.
Private Kaggle dataset creation was requested while its upload was in progress;
this is not yet evidence of a saved dataset or completed crop.

Subsequent verified portal state: upload completes and the
[November input dataset](https://www.kaggle.com/datasets/adnankh4n/forestguard-279-liss4-november-reference)
is saved as Private with exactly one 551.49 MB binary file. Kaggle's license field
remains Unknown; this does not replace the original Bhoonidhi license/ISRO-IRS
attribution. The prepared private notebook is imported into
[November crop notebook](https://www.kaggle.com/code/adnankh4n/forestguard-279-liss4-november-reference-crop),
the exact input is attached and Accelerator None is visible. Version 1 is submitted
with Save & Run All. Successful execution and crop-output verification are still
pending; the draft session was not started.

### Successful November crop milestone

Version 1, scriptVersionId 356648963, succeeds in the reported 44.8 seconds.
The 1,640,588-byte bundle is preserved under `november_crop_v1/`, SHA-256
`8d2e79c49e820d9af33187007b67db3cf31bea0e20eb00bf80c9fed3d2a215d7`.
Seven file hashes and CRC reads pass offline, as do boundary hash, band order,
5 m grid/CRS, uint16 values and mask/count checks. Source full-band CRCs were
checked during streamed cloud extraction. Its crop grid equals the April crop
grid (3 x 486 x 676); original producer CRS remains recorded.

Declared masks include all 209,468 study centres, but 106 have all-band-zero
values. Conservative nonzero coverage is 209,362/209,468, **99.9494%**, before
cloud screening. Actual observed nonzero counts differ slightly from the corner
estimate, which is why pixels were required. All seven review footprints have
100% nonzero candidate coverage. The preview was visually inspected for general
river/field/vegetation context; no new forest class or independent accuracy is
assigned. The fresh pending-review comparison is saved at
`data/labels/compartment_279_november_comparison_v2/comparison.html`.
Original April interpretations and pending candidate records remain unchanged.

All seven November cases have now been visually inspected with their 360 m
context and saved screenshots. Cases 1/2/3 show heterogeneous vegetation texture
and are recorded as wooded-cover candidates, with binary class unknown because
height/canopy threshold and forest/scrub/use ambiguity are unresolved. Case 4
crosses contrasting field-like/mixed surfaces and remains unknown. Cases 5/6/7
are open-water/non-forest interpretations supported by the three dated images.
No cloud-free whole-area coverage or shadow mask is certified by visual review.
These AI-assisted records remain non-independent, with all seven splits unassigned.
Schema/provenance audit passes; training readiness remains false.

November review records, audit and seven screenshots are preserved under
`data/labels/compartment_279_november_comparison_v2/`; the final offline HTML with
per-case uncertainty notes is `compartment_279_november_comparison_v3/comparison.html`.
This closes the bounded acquisition and patch-inspection task. The remaining
scientific requirement is evidence supporting qualifying forest stands, rather
than another successful raster export or agreement with WorldCover predictions.

Version 5, scriptVersionId **356634805**, completed successfully in the portal's
reported **43.5 seconds**. The small ZIP was downloaded and preserved at
`data/reference/bhoonidhi_20261009/crop_v5/liss4_279_reference.zip`:
875,456 bytes, SHA-256
`dd5878d9674faebe2ed89e7f981c98e855f71c8435b08c83df491376aab786a5`.
Seven file hashes, ZIP decompression CRCs, boundary version, saved CRS/grid,
band order and coverage counts pass offline verification. The unchanged boundary
export has the original selected GeoJSON hash. No full raster was loaded locally.

The three-band output is 486 rows by 676 columns, 5 m spacing, EPSG:32643.
The supplier's rounded WGS84 inverse flattening prevents automatic EPSG lookup;
explicit parameter checks accept only UTM 43 north/metres and the documented
rounding. Original WKT is preserved in source_grid.json. Canonical CRS export
changes projected study-corner coordinates by at most 0.0000326312147 m; the
guard requires below 1 mm and no raster pixels are resampled. Regression checks
reject other zones, southern hemispheres and larger ellipsoid differences.

**Coverage limit discovered offline:** the producer declares no NoData value.
Its masks therefore mark all 209,468 study centres valid, but 87,856 have zero
in all three bands, consistent with the image-edge blank region. These are
suspected fill/unknown, not forest/non-forest evidence. Only 121,612 centres
remain nonzero candidates: **58.0576%** of the study mask, before cloud screening.
This is not 100% usable coverage. The original bundle/report are unchanged;
offline_assessment.json and separate suspected-fill/nonzero-candidate masks
record the conservative research screen. It does not prove all nonzero pixels
are clear or that any patch is forest.

The false-colour crop distinguishes the river and vegetation/field patterns,
but cannot by itself establish tree height or reliably resolve every orchard,
plantation and scrub patch. No class labels or model scores were generated.
Use only screened, interpreted patches for reference feasibility; the missing
east-side coverage needs another permitted observation if whole-area reference
coverage is required. The forest-positive reference gate remains open.

Reproduce lightweight local checks:
```powershell
python scripts/check_liss4_crs.py
python scripts/check_notebook.py
python scripts/verify_liss4_crop.py data/reference/bhoonidhi_20261009/crop_v5/liss4_279_reference.zip
```
The original failed versions remain historical diagnostic runs. Do not use their
partial outputs as completed crops or download their temporary full-band export.

Objective: find permitted, finer-resolution evidence for interpreting compartment
279 patches. This follows the unsuccessful bounded GEDI and ATL08 height checks.
No additional satellite imagery or reviewed labels were acquired in this check.

## Source decisions

| Route | Verified access/use finding | Decision |
|---|---|---|
| ISRO Bhoonidhi | Official FAQ says standard data at 5 m and coarser is free to registered users; registration requires the EULA. Finer than 5 m is priced for non-government users. | Candidate next route; account handoff pending, actual local/date coverage and product terms must be checked. |
| Planet Tropical Forest Observatory | Current official page lists USD 180/month and describes discounted non-commercial access. | Excluded under the INR 0 budget; historical NICFI free-access descriptions do not establish current free availability. |
| Esri World Imagery | Public permissions PDF explicitly permits feature tracing/vector sharing in the described ArcGIS uses. It does not provide a blanket open imagery license or expressly establish this project's ML-label use outside those apps. | Do not download tiles or treat displayed imagery as unrestricted training/reference data. A compatible permitted workflow would need separate verification. |
| Bhuvan display imagery | General portal terms restrict copying and derivative use without authorization. | Do not equate viewable basemap imagery with licensed downloadable Bhoonidhi products. |

Sources checked:
- [Bhoonidhi FAQ](https://bhoonidhi.nrsc.gov.in/bhoonidhi/htmls/FAQ2.html)
- [Registration and EULA](https://bhoonidhi.nrsc.gov.in/bhoonidhi/registration.html)
- [NRSC ordering procedure](https://www.nrsc.gov.in/nrscnew/archive_order_procedure.php)
- [Planet current program and pricing](https://www.planet.com/tropical-forest-observatory/)
- [Esri permitted vector uses PDF](https://www.arcgis.com/sharing/rest/content/items/8e90a00a0a6845a49262e0b756f57a10/data)
- [Esri terms summary](https://goto.arcgis.com/termsofuse/viewsummary)
- [Bhuvan portal terms](https://bhuvan.nrsc.gov.in/home/index.php/newsletter.php)

The Esri PDF was actually downloaded and its text inspected: 122,663 bytes,
SHA-256 `20216a8703ff71a0e7bcd52491eb4ceb7fcf8a1bfd83e9dd8ce1d43df59e0b4a`.
Public item metadata, access manifests and this PDF are preserved under ignored
`data/reference/high_resolution_feasibility_20261009/`. No account credentials
are stored there. The large Resourcesat handbook was not downloaded.

## Next bounded search

After the user completes Bhoonidhi registration and terms themselves:
1. Search the exact saved compartment 279 envelope:
   `[76.78831296092488, 22.3915380704959, 76.82119381828602, 22.41331677386371]`.
2. Look for free standard Resourcesat LISS-IV products. Verify actual native
   resolution from product metadata; do not infer it from an enlarged preview.
3. First search 2025 around April 3 and December 9, matching our saved images.
   Retain actual capture dates and any time mismatch; expand only if necessary.
4. Inspect catalogue coverage, quality, processing level, reuse terms and download
   size before selecting a product. Prefer a small spatial subset if provided.
   Run any necessary full-product cropping in Kaggle, after checking size/resources.
5. Preserve source identifier, licence/attribution, checksum, band order, CRS,
   pixel spacing and processing settings with exported crops.

The requested account is the user's genuine non-government/student account.
Government-only free access is not assumed. No purchase, trial or paid product
is authorized by this workflow.

## What this could establish

## Actual catalogue follow-up

The user reports registration complete on 9 October. The portal confirms that
registration details were recorded and requires an emailed activation link for
sign-in. No password, activation link or email contents were collected.

The public catalogue was searched with an outward-rounded envelope accepted by
the portal (five decimal places): `[76.78831, 22.39153, 76.82120, 22.41332]`.
The boundary itself was not modified. Dates: 1 March through 31 December 2025;
Open_Data and 5–25 m category selected.

- Resourcesat-2 / 2A LISS4 MX23 on-order search: the portal reported
  "No more results available for the selected inputs."
- Resourcesat-2 / 2A LISS4 MX70 L2 direct-download search: 13 displayed entries.
  This is the displayed result count, not a claim of exhaustive archive coverage.
- Promising April candidate: `RAF07APR2025043238009700056SSANSTUC00GTDC`,
  Resourcesat-2A LIS4, scene `043237_97_56`, capture 7 April 2025. It is four days
  after the saved Sentinel observation and tagged `OpenData_DirectDownload`.
  Metadata shows quality `Unknown : (Q)`. The initial text snapshot reported no
  preview, but the later screenshot shows a loaded whole-scene quicklook. That
  quicklook does not establish crop cloud coverage or native raster detail.
  Its displayed corner
  envelope spans our search box; actual pixel coverage remains unverified.
- The latest displayed candidate is 9 November 2025, thirty days before our
  December image. No December result is displayed in this bounded search.

Visible catalogue and April metadata snapshots plus a screenshot are preserved
under ignored `data/reference/bhoonidhi_20261009/`. Product download size,
native raster resolution, cloud coverage and calibration remain unchecked.
No satellite product has been downloaded or assigned a forest label.

The official login page is left ready. Next: the user activates the email link
and signs in; inspect the April product's size/download options, preserve product
terms and metadata, then select an affordable bounded cloud-cropping workflow.

## Interpretation limit

## Download milestone

The actual current Bhoonidhi EULA was read in the browser and preserved as
`eula_snapshot.txt`. It permits lawful use/combination of free open data and
requires the caption attribution **ISRO-IRS**; original data must not be
commercialized in its original form. This is source-specific permission, not
a claim that all web basemap imagery has the same terms. Product exports include
the attribution and source EULA URL.

Sign-in was verified by the portal's LogOut/account controls. One free April
product was added to the cart and confirmed; SID `20261009_4GJ001339`.
The download button started the full-scene transfer without a displayed size or
subset chooser. The completed ZIP is 626,385,051 bytes; its nine entries total
1,765,402,521 expanded bytes. No additional scene was downloaded.

The original download and an identical saved project copy were SHA-256 checked:
`1bbc0619381dcc85515cf35f15a1e0769ccb770d18890012deae281943e19947`.
Project copy: `data/reference/bhoonidhi_20261009/april_product/`.
ZIP directory and the small metadata/accuracy-report entries were inspected;
their decompression CRC checks passed. Full raster decompression/CRC and crop
quality checks remain for the hosted run.

Actual product metadata: green/red/NIR bands 2/3/4, 10-bit values stored in two
bytes, 16,578 scans by 17,743 pixels; native input resolution 5.80 m, output
spacing 5.00 m, UTM zone 43/WGS84, georeferenced standard processing and cubic
convolution resampling. This is not Sentinel surface reflectance. CloudPercent
is unavailable and Quality is Q. The supplier's tie-point accuracy report is
retained; it is not our independent boundary/image registration measurement.

`cloud/liss4_reference_crop.py` and notebook `05_liss4_reference.ipynb` implement
a cloud-only source-hash check, streamed one-band extraction, bounded raster
window, source-grid checks, study mask, raw-DN GeoTIFF, false-colour PNG and report
export. The private notebook embeds the unchanged selected boundary under ignored
data; the public notebook has no private geometry. Syntax/source correspondence,
empty outputs and the early local-execution guard pass. Actual cloud execution
is still pending. No dependency installation is needed.

Private Kaggle input creation was initiated with title
`ForestGuard 279 LISS4 April Reference`; visibility explicitly showed Private.
The upload was still in progress at the last observation. Do not claim a ready
dataset or a successful cloud crop until its actual results are inspected.

The source notebook was imported, named and confirmed private at
[ForestGuard 279 LISS4 Reference Crop](https://www.kaggle.com/code/adnankh4n/forestguard-279-liss4-reference-crop/edit).
Accelerator is None and the draft session is off. The separate private input
upload's last reported transfer progress was 31%; it has not been attached and
no crop execution has started. Screenshots of both states are preserved.

Resume by inspecting upload completion before creating another dataset. Inspect
whether Kaggle retained the ZIP or expanded it; the current notebook expects the
preserved ZIP. If expanded, adjust source verification using the retained source
manifest before running, rather than silently bypassing its checksum. Then attach
the private dataset, run/save the CPU notebook, export the small result and verify
its actual grid, masks, band descriptions and image detail locally.

A separate sensor with finer spatial detail may improve interpretation of rows,
field boundaries, canopy texture and land use. This is a feasibility hypothesis,
not a measured result. Two-dimensional imagery cannot directly verify tree
height. Ambiguous forest/plantation/orchard/scrub cases remain unknown until
supporting evidence is available. Review provenance and uncertainty are required;
agreement with WorldCover alone is not independent accuracy.

Phase 0 remains open at the credible forest-reference gate. No forest labels,
model, accuracy or forest-loss estimate is claimed by this source check.
