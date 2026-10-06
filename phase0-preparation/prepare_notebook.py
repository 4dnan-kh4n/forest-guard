"""Prepare reviewed notebook revisions without modifying the existing G: project."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = Path(r'G:\CODING PROJECTS\Forest Guard')
notebook = json.loads((PROJECT / 'notebooks/01_satellite_sample.ipynb').read_text(encoding='utf-8'))
item = json.loads((PROJECT / 'docs/phase0/preview_stac_item.json').read_text(encoding='utf-8'))
cell = notebook['cells'][3]
code = ''.join(cell['source'])
prefix, code = code.split('import math, time, zipfile\n', 1)
code = 'ITEM = ' + repr(item) + '\nimport math, time, zipfile, hashlib\n' + code
code = code.replace('from rasterio.warp import transform_bounds, Resampling',
    'from rasterio.warp import transform_bounds, transform as project_points, Resampling')
code = code.replace("'EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_HTTP_TIMEOUT='60'",
    "'EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_HTTP_TIMEOUT='60', GDAL_CACHEMAX=64*1024*1024")
code = code.replace("assert src.crs == crs and src.transform == source_transform, 'Band grid mismatch'",
    "assert src.crs == crs and src.transform == source_transform and src.res == (10.0,10.0), 'Band grid mismatch'")
code = code.replace("valid = np.logical_and.reduce(masks) & np.isin(scl, [4,5,6])", """# Pixel centers define the research-box denominator; rounded window margins are excluded.
rows, cols = np.indices((height,width))
x = transform.c + (cols + .5) * transform.a
y = transform.f + (rows + .5) * transform.e
lon, lat = project_points(crs, 'EPSG:4326', x.ravel(), y.ravel())
lon, lat = np.array(lon).reshape(height,width), np.array(lat).reshape(height,width)
inside = (lon >= BBOX[0]) & (lon <= BBOX[2]) & (lat >= BBOX[1]) & (lat <= BBOX[3])
assert inside.any(), 'No research-box pixel centers'
valid = inside & np.logical_and.reduce(masks) & np.isfinite(reflectance).all(axis=0) & np.isin(scl, [4,5,6])""")
code = code.replace("('usable_mask.tif',valid.astype('uint8'))", "('usable_mask.tif',valid.astype('uint8')),('study_mask.tif',inside.astype('uint8'))")
code = code.replace('np.unique(scl,return_counts=True)', 'np.unique(scl[inside],return_counts=True)')
code = code.replace("    usable_fraction=float(valid.mean()),scene_class_counts=", "    transform=list(transform)[:6],study_pixels=int(inside.sum()),usable_pixels=int(valid.sum()),\n    usable_fraction=float(valid.sum()/inside.sum()),scene_class_counts_inside_study=")
code = code.replace("processing_seconds=round(time.monotonic()-started,2),source=META)", """processing_seconds=round(time.monotonic()-started,2),source=META,
    schema_version=2,generated_at_utc=datetime.now(timezone.utc).isoformat(),
    preprocessing={'reflectance_formula':'raw * asset scale + asset offset; once only',
        'scl_resampling':'nearest; native 20 m quality layer aligned to 10 m grid',
        'study_mask':'pixel centers inside the provisional EPSG:4326 research box',
        'display_only':'RGB / 0.3, clipped to 0..1; invalid pixels transparent'},
    calibration={k:META['assets'][k]['raster:bands'][0] for k in ['blue','green','red','nir']},
    calibration_status='asset metadata applied; upstream COG consistency not independently checked',
    attribution='Contains modified Copernicus Sentinel data 2025',
    license_url='https://cds.climate.copernicus.eu/licences/ec-sentinel',
    runtime={'provider':provider,'python':platform.python_version(),
        'packages':{p:metadata.version(p) for p in ['numpy','rasterio','Pillow']},
        'gdal':rasterio.__gdal_version__},
    reflectance_quantiles={name:np.quantile(reflectance[i,valid],[0,.01,.5,.99,1]).tolist()
        for i,name in enumerate(['B02','B03','B04','B08'])})""")
start = code.index("with zipfile.ZipFile(OUT.parent/")
end = code.index("print(json.dumps(", start)
code = code[:start] + """(OUT/'source_stac_item.json').write_text(json.dumps(ITEM,indent=2),encoding='utf-8')
SAMPLE_FILES = ['reflectance.tif','scene_classes.tif','usable_mask.tif','study_mask.tif',
    'preview.png','sample_report.json','source_stac_item.json']
checksums = {}
for name in SAMPLE_FILES:
    file = OUT/name
    with file.open('rb') as stream:
        digest = hashlib.file_digest(stream,'sha256').hexdigest()
    checksums[name] = {'sha256':digest,'bytes':file.stat().st_size}
(OUT/'checksums.json').write_text(json.dumps(checksums,indent=2),encoding='utf-8')
""" + code[end:]
cell['source'] = (prefix + code).splitlines(keepends=True)
verifier = (HERE/'verify_sample.py').read_text(encoding='utf-8').split("if __name__ == '__main__':")[0]
verification_code = verifier + "\nprint(json.dumps(verify(OUT, rasters=True),indent=2))\n" + """with zipfile.ZipFile(OUT.parent/'forestguard_sample.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for name in SAMPLE_FILES + ['checksums.json']:
        archive.write(OUT/name,arcname=name)
print('Verified export:', OUT.parent/'forestguard_sample.zip')
print('ZIP bytes:', (OUT.parent/'forestguard_sample.zip').stat().st_size)
"""
notebook['cells'] += [
    {'cell_type':'markdown','metadata':{},'source':[
        '## Verify and preserve the export\n',
        'This checks saved raster grids, study-box coverage, quality masks, provenance and checksums. ',
        'Download the ZIP after this cell succeeds. Coverage is not forest area or model accuracy.\n']},
    {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],
        'source':verification_code.splitlines(keepends=True)},
]
(HERE/'01_satellite_sample.ipynb').write_text(json.dumps(notebook,indent=1)+'\n',encoding='utf-8')
print('Prepared revised notebook:', HERE/'01_satellite_sample.ipynb')
