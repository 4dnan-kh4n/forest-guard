# Sources and license decisions

Checked against official provider/project references on 6 October 2026.
No paid service, trial, card-dependent service or hosted inference API is adopted.

| Component | Use and obligations | Primary source |
|---|---|---|
| Sentinel-2 L2A | Free/open data. Preserve source ID, date, processing details and year-specific attribution. Modified 2025 sample: Contains modified Copernicus Sentinel data 2025. | [Copernicus Sentinel license](https://cds.climate.copernicus.eu/licences/ec-sentinel) |
| EarthSearch | Public metadata and HTTPS COG assets; no paid AWS account required by this workflow. No service guarantee. Download/export outputs for durable offline use. Apply the selected asset's scale/offset once. | [Provider repository](https://github.com/Element84/earth-search) |
| NumPy | BSD license; retain applicable copyright/license notices when distributing a runtime. | [Official license](https://numpy.org/doc/stable/license.html) |
| Rasterio | BSD license; preserve notices and record GDAL version. Bundled native libraries need their own distribution notices. | [Official repository license](https://github.com/rasterio/rasterio/blob/main/LICENSE.txt) |
| Pillow | PIL-derived MIT-CMU license in current project documentation; preserve applicable notices and check the actual runtime release when distributing. Cloud preview only at present. | [Official license](https://pillow.readthedocs.io/en/stable/about.html#license) |

The notebook records the actual package versions used. Existing cloud packages
are used; no dependencies are automatically installed. A tested local version
set and complete redistributable notices will be established in Phase 1.

ESA WorldCover is a possible later weak-label source, not adopted or downloaded.
Check its attribution and 2020/2021 temporal mismatch before adoption. Weak map
labels cannot establish independent model accuracy.

The user-provided research box [76.785,22.413,76.805,22.433] and candidate scene
S2C_43QFE_20250329_0_L2A are starting research inputs, not inherited outputs,
an official beat boundary, an approved reporting polygon, or forest labels.
