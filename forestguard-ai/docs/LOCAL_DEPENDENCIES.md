# Local dependency decisions

Checked 6 October 2026. Existing hardware and free PyPI packages are used;
no paid service, trial, cloud database or mandatory model endpoint is adopted.

The [Rasterio 1.4.3 release](https://pypi.org/project/rasterio/1.4.3/) supports
Python >=3.9 and NumPy >=1.24 and provides Windows binary wheels. The selected
[NumPy 2.1.3 release](https://pypi.org/project/numpy/2.1.3/) supports Python >=3.10.
Windows CPython 3.11 wheels were checked and installed without compiling native
libraries. Actual compatibility is demonstrated by the saved-crop inspection.

| Package | Installed version | License metadata from wheel |
|---|---|---|
| NumPy | 2.1.3 | BSD-3-Clause core; bundled native-library notices also apply |
| Rasterio | 1.4.3 | BSD; bundled GDAL/native-library notices also apply |
| affine | 3.0.1 | BSD-3-Clause |
| attrs | 26.1.0 | MIT |
| certifi | 2026.7.22 | MPL-2.0 |
| click | 8.5.0 | BSD-3-Clause |
| click-plugins | 1.1.1.2 | BSD |
| cligj | 0.7.2 | BSD |
| pyparsing | 3.3.3 | MIT |

The wheels retain their full bundled copyright/license files. Local wheel
metadata and a list of those files are recorded in the ignored wheel manifest.
Redistributing a runtime requires retaining applicable notices and observing
bundled-library terms, including the certificate bundle's MPL terms. No package
source or certificate data has been modified. Do not describe an entire binary
wheel solely by the Python package's core license.

This phase distributes project code and dependency pins, not a repackaged native
runtime. The Windows wheel archive remains a local offline-reinstall resource.
