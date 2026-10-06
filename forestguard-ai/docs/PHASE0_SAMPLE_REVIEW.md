# Phase 0: first real-data check

Checked 6 October 2026. Phase 0 remains in progress.

## Objective, inputs and processing

Check whether a small real Sentinel-2 observation can be acquired, quality-masked
and exported on free cloud CPU. The input is S2C_43QFE_20250329_0_L2A, acquired
29 March 2025, and the user-supplied provisional research box. Its boundary is
not the official Joga beat or an approved reporting area.

The notebook reads bounded COG windows, applies asset calibration, aligns the
20 m quality layer to the native 10 m band grid, and excludes invalid/uncertain
pixels. Coverage uses pixel centers inside the research box.

## Measured result: Version 1

Saved private run: [Version 1](https://www.kaggle.com/code/adnankh4n/forestguard-ai-fresh-feasibility?scriptVersionId=355664060).

| Measurement | Result |
|---|---|
| Raster shape | 225 rows x 210 columns |
| Bands | B02, B03, B04, B08 |
| Grid | EPSG:32643, 10 m |
| Research-box pixels | 45,606 |
| Usable pixels | 44,746 |
| Usable coverage | 98.1143% |
| Processing time reported by script | 15.461 seconds |
| Complete Kaggle run reported by UI | 36.6 seconds |
| Sample ZIP | 562,677 bytes |

The notebook reopened saved GeoTIFFs and checked grid/pixel equality. All seven
SHA-256 hashes in the downloaded bundle matched locally. Outputs are preserved
under `data/phase0/version1/`, including the complete Kaggle output archive.
No local geospatial/ML packages were installed.

## Interpretation and limitations

The preview shows a broad water feature and mixed surrounding land. Forest
labels cannot be established from this RGB preview alone. SCL is not ground
truth: its counts include 13,539 water-class pixels, 29,025 non-vegetated-class
pixels and 2,182 vegetation-class pixels, among other/uncertain classes.
Those classes must not be converted into forest/non-forest ground truth.

Calibration remains under investigation. Applying the supplied scale 0.0001
and offset -0.1 yielded blue median -0.03565 and green median -0.00585. Negative
values alone do not prove an offset error, but the distribution and dark preview
warrant a cross-source check. We have not clipped negatives into plausible
training data or silently changed the provider calibration.

The provider repository documents offset handling and an unresolved report
of COG/metadata inconsistencies. The reported issue concerns other scenes and
does not prove an error for this scene. A bounded Collection 1 comparison is
being run and its real results must be recorded before deciding on a source.

References: [provider calibration guidance](https://github.com/Element84/earth-search#gainoffset-in-items-after-jan-25-2022),
[provider issue tracker](https://github.com/Element84/earth-search/issues/66).

## What we learned

A successful file export proves that the data pipeline runs. Training suitability
also needs correct calibration, the right study area, representative land cover
and reviewed labels. High usable coverage is not forest percentage or accuracy.

## Remaining gates

- [x] Avoid the legacy calibration ambiguity using Collection 1 and metadata/header checks.
- Establish the intended forest geography through an official boundary or a
  clearly confirmed provisional polygon; do not report beat totals from this box.
- Inspect suitable forest/non-forest/unknown reference examples.
- Freeze independent spatial/temporal splits before sample extraction.
- Finalize attainable acceptance criteria after baseline/label review.

Before starting every new phase, explain its objective, inputs, processing,
deliverable and verification to the user.

## Calibration decision and successful Version 3

Version 2 compared the legacy source against Collection 1. The candidate has
the identical acquisition timestamp and source product URI. Its blue-band
raw median is 1644 and its header agrees with the asset scale 0.0001/offset -0.1,
giving median reflectance approximately 0.0644. The legacy crop's median is
approximately 0.1 lower. This is evidence of a legacy source/calibration
inconsistency, not an independent absolute radiometric validation.

The active pipeline now reads `sentinel-2-c1-l2a` item
`S2C_T43QFE_20250329T053314_L2A`. It rejects disagreement between each band's
asset calibration and its raster header. No correction was applied to the
preserved Version 1 files.

[Version 3](https://www.kaggle.com/code/adnankh4n/forestguard-ai-fresh-feasibility?scriptVersionId=355668914)
completed successfully. Its saved-grid/pixel checks and ZIP checksum checks
passed. Shape, grid and quality coverage remained unchanged. Processing took
17.892 seconds; Kaggle reported a 37.9-second run. The sample ZIP is 585,579 bytes.
Median B02/B03/B04/B08 reflectance is approximately
0.06435/0.09415/0.11320/0.17880. Collection 1 avoids the demonstrated legacy
ambiguity; calibration correctness is not established merely by positive values.

The complete Version 3 output archive, rasters, preview, source metadata,
calibration query/results and checksum manifest are saved in
`data/phase0/version3/`. The locally downloaded source product URI matches
Version 1, confirming the same original acquisition/product was compared.
The standalone offline verifier passed all seven exported file hashes and
checked band order, provenance and coverage counts:

```powershell
python scripts/verify_bundle.py data/phase0/version3/forestguard_phase0.zip
```

The updated RGB preview was visually inspected locally. It still shows water,
mixed land and excluded pixels. This is a valid pipeline experiment but is
insufficient as the sole forest-training dataset. No reviewed forest labels or
model accuracy have been established. All saved cloud versions completed, and
the draft session remains off; no persistent cloud runtime is required to view
these local artifacts.

## Geographic search and user response

The user does not have official compartment details or a boundary source.
The [official Harda district Joga Fort page](https://harda.nic.in/en/tourist-place/joga-fort/)
describes Joga village along the Narmada, northwest of Harda. This supports
location context but does not establish a current forest-beat polygon or
independently confirm the crop coordinates. The MP Forest Department homepage
request timed out in this check. No official beat boundary was obtained.

Keep this crop as a reproducible pipeline check. A representative forest-rich
study area and reviewed labels remain necessary before model feasibility can
be approved. Search authoritative mapping sources without substituting village
geometry for a beat. Do not contact anyone on the user's behalf without explicit
authorization.
