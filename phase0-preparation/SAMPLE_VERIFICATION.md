# Phase 0 satellite-sample checkpoint

Checked: 6 October 2026. Phase 0 remains in progress.

## Actual state

- Existing project inspected at `G:\CODING PROJECTS\Forest Guard`.
- Cloud-readiness report records Python 3.13.15, NumPy 2.1.3, scikit-learn
  1.6.1, joblib 1.6.0, and Rasterio 1.5.1. These are observed cloud versions,
  not a tested Windows environment or a permanent Kaggle allocation.
- No successful satellite crop, reviewed labels, or trained model found.
- Browser access to the private notebook currently shows "We can't find that page".
  This does not prove deletion or the current verification state. User sign-in is pending.
- The last documented cloud failure was disabled Internet requiring phone verification.
- G: has 26,648,317,952 bytes free (about 24.8 GiB) at inspection. Available RAM
  could not be rechecked through CIM; no substantial local processing was performed.
- Original Lean Canvas and Synopsis files were not found in either inspected workspace.
- The earlier hosted Gemma demo is separate from the required product pipeline.
  Offline forest analysis must not call it or depend on its API key.

## Working deliverable

The revised `notebooks/01_satellite_sample.ipynb` retains the original scene,
cloud-only guard and 512-pixel crop limit. It adds a pixel-center study-box mask,
finite reflectance checks, saved-layer verification, complete source metadata,
dependency/processing records, diagnostics and SHA-256 checksums.

The original notebook is preserved as
`notebooks/01_satellite_sample.pre_verification.ipynb`.

Expected ZIP contents:

- reflectance.tif: B02/B03/B04/B08 in that order, float32, nodata -9999.
- scene_classes.tif: quality classes aligned by nearest neighbor from native 20 m.
- usable_mask.tif: all bands valid, finite, SCL 4/5/6, and inside the research box.
- study_mask.tif: pixel centers inside [76.785, 22.413, 76.805, 22.433].
- preview.png: display RGB, with invalid pixels transparent.
- source_stac_item.json, sample_report.json, checksums.json.

`usable_fraction` means usable pixels / study-box pixels, excluding the rounded
raster-window margins. It is not forest fraction or beat coverage. Masks are
discretized on a 10 m grid, and this box remains unapproved for beat reporting.

## Learning overview

Objective: establish whether one real, small observation can be read and inspected.
Inputs: one Sentinel-2 L2A scene, four 10 m bands, its 20 m quality layer and the
provisional research box. Processing: windowed reads, asset scale/offset once,
quality masking and saved-grid checks. Outputs: portable rasters, a preview,
coverage statistics and provenance. Verification: reopen outputs, recompute their
counts and mask rules, and verify every exported file's checksum.

SCL vegetation is not forest ground truth. A clear crop may still show agriculture,
orchards or scrub; forest feasibility needs independent reference review.

## User handoff and rerun

1. Sign in to the existing private [satellite-sample notebook](https://www.kaggle.com/code/adnankh4n/forestguard-satellite-sample).
2. Complete phone verification yourself if required. Do not send OTPs or credentials.
3. Import the revised local notebook into the existing private notebook. Preserve
   the previous failed version. Keep Accelerator None and enable Internet.
4. Save & Run All. The final cell must print `Verified export` before treating
   the result as a complete bundle.
5. Download `forestguard_sample.zip` before stopping the runtime. Preserve the
   saved notebook version and its logs. Stop the runtime after successful export.
6. Extract the ZIP into a new, dedicated folder under `data/research_sample/`.
   Do not overwrite previously verified data. Run:

   ```powershell
   python notebooks/verify_sample.py data/research_sample
   ```

This offline command uses only the Python standard library (Python 3.11+).
`--rasters` additionally checks the geospatial files using NumPy/Rasterio; the
cloud notebook already runs that check. Do not install a training stack locally
to repeat it. If needed, run the full check in the cloud with the saved bundle.

File checksums detect changes after export; they do not establish independent
ground truth or prove that an upstream calibration is scientifically correct.

## Verification completed and limitations

- Revised notebook syntax, empty output cells and local-runtime refusal passed.
- Synthetic file-contract check passed: valid contract accepted; changed size,
  changed checksum, incorrect coverage denominator, provenance mismatch and
  false model claims rejected. These fixtures are not satellite data.
- Missing output bundle is rejected with a clear error.
- Actual cloud execution, full raster checks, visual inspection, measured
  coverage, processing time and output footprint remain pending.
- No accuracy, forest area, beat boundary, labels or model feasibility is claimed.

## Phase 0 progress checklist

- [x] Inspect existing project and preserve prior readiness work.
- [x] Audit and strengthen the sample notebook/export contract.
- [x] Test local syntax, runtime guard and offline file-contract checks.
- [ ] Restore authenticated notebook access; verify Internet on and Accelerator None.
- [ ] Execute revised notebook, preserve outputs and inspect real pixels.
- [ ] Review calibration and usable coverage; decide whether another crop is needed.
- [ ] Obtain official beat polygon or confirm a provisional study polygon explicitly.
- [ ] Demonstrate credible forest/non-forest/unknown reference labels.
- [ ] Establish independent evaluation locations/dates and finalize attainable targets.

## After the sample succeeds

Record measured usable coverage, package versions, processing seconds and bundle
bytes from the outputs. Inspect the RGB and SCL together; identify crops, water,
settlement, woody cover and uncertain areas. Keep ambiguous areas unknown. A
10 m optical image alone may not distinguish natural forest from orchards.

Before creating pixel samples, choose separate geographic training, validation
and test blocks with an exclusion buffer justified by spatial correlation and
patch size. Reserve later dates for temporal evaluation. Store label geometry,
class, observation date, evidence/source, reviewer, review date, confidence,
uncertainty note and split. No reviewed labels or split polygons have been made yet.

Use the untouched reviewed test set for final precision, recall, F1, IoU and
area-error reporting. WorldCover can suggest weak labels after checking their
age; matching its predictions is not independent accuracy. Existing aspirational
F1/IoU goals remain aspirations until baseline and label review.

## Source and license register

Checked official project/provider sources on 6 October 2026; preserve license
notices for the actual package versions when distributing the application.

| Source/tool | Terms and project action | Reference |
|---|---|---|
| Sentinel-2 | Free/open Sentinel data; record year, source and modifications. Export attribution: Contains modified Copernicus Sentinel data 2025. | [Provider FAQ](https://documentation.dataspace.copernicus.eu/FAQ.html), [data license](https://cds.climate.copernicus.eu/licences/ec-sentinel) |
| EarthSearch | Public metadata/HTTPS assets; no availability guarantee. Export data and metadata so stored-data operation is independent. Apply asset scale/offset once; upstream consistency still needs review. | [Provider repository](https://github.com/Element84/earth-search), [provider overview](https://element84.com/geospatial/introducing-earth-search-v1-new-datasets-now-available/) |
| ESA WorldCover | Candidate only; not downloaded. CC BY 4.0; retain dataset citation and map attribution if adopted. 2020/2021 maps have different algorithms and cannot directly establish real change. | [Official data access](https://esa-worldcover.org/en/data-access) |
| NumPy | Modified BSD; retain applicable copyright/license notices in distribution. | [Official project](https://numpy.org/about/) |
| Rasterio | BSD; retain applicable copyright/license notices. Record GDAL version and bundled component notices when packaging. | [Official contributing guide](https://rasterio.readthedocs.io/en/stable/contributing.html) |
| scikit-learn | BSD 3-Clause; candidate Random Forest training, not yet run. | [Official repository](https://github.com/scikit-learn/scikit-learn) |
| joblib | BSD; model artifact export later, not currently an inference requirement. | [Official documentation](https://joblib.readthedocs.io/en/stable/index.html) |

Pillow is already used by the original cloud sample for previews; preserve its
version in the export and check its release license before redistributing a
local runtime. No packages or satellite rasters were installed/downloaded locally
for this checkpoint. No paid services were added.
