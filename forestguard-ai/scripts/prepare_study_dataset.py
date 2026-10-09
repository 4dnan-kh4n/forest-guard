"""Register verified compartment 279 imagery and current labels without training."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import rasterio
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile
from rasterio.warp import transform_geom

from audit_labels import audit
from inspect_research import inspect


def prepare(bundle, boundary, labels, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Dataset output already exists; choose a new folder.')
    labels = Path(labels).resolve(strict=True)
    if labels.stat().st_size > 2*1024**2:
        raise ValueError('Label input exceeds 2 MiB.')
    label_bytes = labels.read_bytes()
    document = json.loads(label_bytes)
    label_audit = audit(document)
    coverage = inspect(bundle,boundary)
    selected = json.loads(Path(boundary).read_bytes())
    version = selected['features'][0]['properties']['study_area_version']
    with rasterio.Env(PROJ_NETWORK='OFF'), zipfile.ZipFile(bundle) as archive:
        report = json.loads(archive.read('research_report.json'))
        observations = report['acquisitions']
        dates = {item['acquisition'][:10] for item in observations}
        common = None
        for item in observations:
            with MemoryFile(archive.read(item['season']+'/usable_mask.tif')) as memory, memory.open() as raster:
                values = raster.read(1).astype(bool)
                common = values if common is None else common & values
                shape, grid, crs = raster.shape, raster.transform, raster.crs
        support = []
        for feature in document['features']:
            props = feature['properties']
            if props['study_area_version'] != version or props['observation_date'] not in dates:
                raise ValueError('Label study version/date differs from the registered imagery.')
            projected = transform_geom('EPSG:4326',crs,feature['geometry'])
            points = [projected['coordinates']] if projected['type']=='Point' else projected['coordinates'][0]
            left,top = grid*(0,0)
            right,bottom = grid*(shape[1],shape[0])
            if not all(left <= x <= right and bottom <= y <= top for x,y in points):
                raise ValueError('Review footprint extends outside the crop grid.')
            footprint = geometry_mask([projected],
                                      shape,grid,invert=True)
            count = int(footprint.sum())
            usable = int((footprint & common).sum())
            if count == 0 or usable != count:
                raise ValueError('Review footprint lacks common usable pixel-centre coverage; revise it before sampling.')
            support.append({'label_id':props['label_id'],'footprint_pixels':count,
                            'common_usable_pixels':usable,'samples_extracted':0})
        manifest = json.loads(archive.read('checksums.json'))
    definition = Path(__file__).resolve().parents[1]/'docs/FOREST_COVER_DEFINITION.md'
    inputs = {'imagery_bundle':coverage['bundle_sha256'],'boundary':coverage['boundary_sha256'],
              'labels':hashlib.sha256(label_bytes).hexdigest(),
              'forest_definition_document':hashlib.sha256(definition.read_bytes()).hexdigest()}
    identifier = hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:16]
    registry = {'dataset_version':'compartment-279-'+identifier,'study_area_version':version,
                'input_sha256':inputs,'imagery_integrity':'PASS','coverage':coverage,
                'imagery_files':manifest,'observations':observations,
                'cloud_runtime':report['cloud_runtime'],'label_audit':label_audit,
                'label_pixel_support':support,'training_eligible':False,
                'evaluation_splits_frozen':False,'training_samples_extracted':0,
                'status':'IMAGERY_REGISTERED_LABELS_NOT_READY',
                'remaining':['Credible independently reviewed forest/non-forest reference evidence',
                             'Representative labels beyond the convenience review patches',
                             'Frozen spatial/date evaluation groups before sample extraction',
                             'Same-season dated observations and reviewed changes for change evaluation'],
                'limits':'Label audit checks declared metadata, not class truth. Historical weak maps are not test ground truth.'}
    output.mkdir(parents=True)
    (output/'dataset_registry.json').write_text(json.dumps(registry,indent=2)+'\n',encoding='utf-8')
    (output/'labels.geojson').write_bytes(label_bytes)
    (output/'forest_cover_definition.md').write_bytes(definition.read_bytes())
    return registry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['input','boundary','labels','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.input,args.boundary,args.labels,args.output)
        print(json.dumps({k:result[k] for k in ['dataset_version','status','label_audit','training_eligible']},indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,rasterio.errors.RasterioError) as error:
        parser.exit(1,f'Dataset preparation failed: {error}\n')
