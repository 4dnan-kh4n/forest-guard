# Historical canopy-height supporting evidence — 9 October 2026

Objective: test whether a permitted, small historical predicted-height crop helps
prioritize the unresolved reference cases. It is not independent 2025 truth.

The [authors' product page](https://langnico.github.io/globalcanopyheight/)
identifies the ETH Global Canopy Height 2020 v1 map as model estimates from
Sentinel-2 and GEDI, with predictive uncertainty. Data license: CC BY 4.0.
Attribute Lang, Jetz, Schindler and Wegner (2023),
[paper](https://doi.org/10.1038/s41559-023-02206-6) and
[dataset](https://doi.org/10.3929/ethz-b-000609802). No external model weights,
training framework, account or payment are needed to inspect the saved crops.

The 2,608,985-byte official tile index has SHA-256
`c05f064c67c2afdcdf9765e2d95e1d48834070a91aa5e1c7a214cf2be95f5b64`.
Exactly one tile, N21E075 (75–78 E, 21–24 N), contains the selected study envelope.
Height and uncertainty files are 214,570,187 and 255,729,879 bytes. HTTP requests
for the first 1,024 bytes return 206 and correct Content-Range; only cropped
native windows are read in cloud, rather than downloading the complete tiles.
Header hashes, source URLs, sizes and access checks are preserved under
`data/reference/eth_canopy_height_2020/`.

Private CPU notebook:
[historical height check](https://www.kaggle.com/code/adnankh4n/forestguard-279-historical-canopy-height-check).
Version 1, scriptVersionId 356717456, succeeds in the reported 31.7 seconds.
Accelerator None and Internet On were verified. No draft session was started.

Native crop: 262 x 396, EPSG:4326, 1/12000-degree spacing. This is the product's
angular grid, not an exact uniform 10 m square grid or an area-measurement grid.
Source uint8, NoData 255, scale 1 and offset 0; zero is a valid estimate, not
automatically missing. TIFF units are unset; metre interpretation follows the
product description. Saved crops retain only finite study pixels. Both layers
have 57,499 valid centres of 66,135 inside the study polygon (86.94% rounded).
This describes historical estimate availability, not current observable coverage.

| Case | Historical median height estimate | Median predictive standard deviation | Interpretation |
|---|---:|---:|---|
| 1 | 4.5 m | 7 m | Weak/uncertain supporting hint |
| 2 | 2 m | 6 m | Weak/uncertain supporting hint |
| 3 | 12 m | 8 m | Higher priority wooded-cover candidate; unresolved current truth |
| 4 | 0 m | 1 m | Consistent with low historical cover; no new class assigned |
| 5 | 0 m | 1 m | Only 8 valid centres; not representative of the whole patch |
| 6/7 | Missing | Missing | No historical estimate; never filled by predictions |

Standard deviation is the published predictive uncertainty, not a calibrated
local confidence interval. The map shares Sentinel/GEDI information with other
research inputs; testing against it would measure agreement with weak predictions.
It supplies no canopy-density/forest-use guarantee, current height survey or new
reviewed forest labels. Earlier November interpretations remain unchanged.

Reproduce: import the private `07_canopy_height_reference.private.ipynb` from the
ignored reference folder into Kaggle CPU, enable Internet and Save & Run All.
Public source: `notebooks/07_canopy_height_reference.ipynb`, geometry/cases unset.
Download `eth_2020_height_reference.zip`; preserve in a new version folder. Run
`scripts/verify_height_reference.py` with the bundle, selected boundary GeoJSON and
original review-case GeoJSON to independently recompute masks and case statistics.
Cloud code refuses local acquisition, bounds each window to 512 pixels per side,
checks range support/source headers and verifies saved raster round trips.

Offline export milestone: the 39,819-byte ZIP is preserved at
`data/reference/eth_canopy_height_2020/crop_v1/eth_2020_height_reference.zip`, SHA-256
`9f9a1e95af1f29b1269a29d6cc447a7168a89cb837c913da76322e9e00c7dfc3`.
Both raster hashes and decompression CRC reads pass. The checker recomputes study
masks, coverage counts, all seven patch medians/minima/maxima and valid-centre
counts. An in-memory report with an altered median is rejected. Original case
labels, interpretations and evaluation splits remain unchanged.
