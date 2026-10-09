"""Estimate image-corner coverage on a saved study grid; not cloud/valid coverage."""
import argparse
import hashlib
import json
from pathlib import Path

import rasterio
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom


def check(metadata, boundary, grid, output):
    if output.exists():
        raise FileExistsError('Preserve previous assessments; choose a new output.')
    raw = metadata.read_bytes()
    values = dict(line.split('=', 1) for line in raw.decode().splitlines() if '=' in line)
    values = {key.strip(): value.strip() for key, value in values.items()}
    corners = [[float(values[f'Image{corner}Lon']), float(values[f'Image{corner}Lat'])]
               for corner in ['UL', 'UR', 'LR', 'LL']]
    assert all(-180 <= lon <= 180 and -90 <= lat <= 90 for lon, lat in corners)
    footprint = dict(type='Polygon', coordinates=[corners + [corners[0]]])
    document = json.loads(boundary.read_text())
    geometries = [feature['geometry'] for feature in document['features']]
    with rasterio.open(grid) as raster:
        if raster.width * raster.height > 1_000_000:
            raise ValueError('Only a small saved study grid is supported.')
        study = geometry_mask([transform_geom('EPSG:4326', raster.crs, g) for g in geometries],
                              raster.shape, raster.transform, invert=True)
        image = geometry_mask([transform_geom('EPSG:4326', raster.crs, footprint)],
                              raster.shape, raster.transform, invert=True)
        total, covered = int(study.sum()), int((study & image).sum())
        assert 0 < total and 0 <= covered <= total
        # The complement check catches coverage/count arithmetic mistakes.
        assert covered + int((study & ~image).sum()) == total
    result = dict(product=values['OTSProductID'], acquisition=values['DateOfPass'],
                  metadata_sha256=hashlib.sha256(raw).hexdigest(),
                  boundary_sha256=hashlib.sha256(boundary.read_bytes()).hexdigest(),
                  image_footprint_wgs84=footprint, study_grid_centres=total,
                  predicted_inside_image_centres=covered, predicted_fraction=covered / total,
                  uncompressed_band_bytes=int(values['NoScans']) * int(values['NoPixels']) *
                      int(values['NoOfBands']) * int(values['BytesPerPixel']),
                  compressed_download_bytes=None, cloud_percent=values['CloudPercent'],
                  limitation='Metadata corner estimate only; no pixels downloaded, no cloud, fill or registration validation.')
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['metadata', 'boundary', 'grid', 'output']:
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.metadata, args.boundary, args.grid, args.output), indent=2))
