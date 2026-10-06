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
| Matplotlib | PSF-based license; retain license/copyright notices when distributing. Used from the existing cloud runtime for review figures. | [Official license](https://matplotlib.org/stable/project/license.html) |

The notebook records the actual package versions used. Existing cloud packages
are used; no dependencies are automatically installed. A tested local version
set and complete redistributable notices will be established in Phase 1.

ESA WorldCover is a possible later weak-label source, not adopted or downloaded.
Its [official license](https://esa-worldcover.org/en/data-access) was checked:
CC BY 4.0; acknowledge the provider and cite the selected dataset. Preserve its
2020/2021 date and algorithm version. Temporal mismatch with 2025 imagery remains
unresolved; weak map labels cannot establish independent model accuracy.

Official Handia management map: obtained from the MP Forest Department's Harda
working-plan map catalogue (listed period 2022-23 to 2031-32). Preserved locally
as reference with checksum and retrieval metadata. No open redistribution license
was established; do not package the PDF or derived geometry for public release
until reuse conditions are checked. Management colors are not forest-cover labels.
The same catalogue supplies a 501,065-byte Handia KML containing a Joga/278/RF
polygon; it is likewise local reference only, pending boundary and reuse review.
See [map evidence](JOGA_MAP_EVIDENCE.md) for source links and unresolved geography.

The user-provided research box [76.785,22.413,76.805,22.433] and candidate scene
S2C_43QFE_20250329_0_L2A are starting research inputs, not inherited outputs,
an official beat boundary, an approved reporting polygon, or forest labels.
