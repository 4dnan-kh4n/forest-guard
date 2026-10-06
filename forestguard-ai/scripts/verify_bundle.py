"""Verify a small exported sample ZIP offline using only Python 3.11+."""
import argparse
import hashlib
import json
import math
import zipfile
from pathlib import Path


def verify(path):
    with zipfile.ZipFile(path) as archive:
        expected = {'source.json','reflectance.tif','scl.tif','study.tif','usable.tif',
                    'preview.png','report.json','checksums.json'}
        entries = archive.infolist()
        if (set(archive.namelist()) != expected or len(entries) != len(expected)
                or sum(i.file_size for i in entries) > 10*1024**2):
            raise ValueError('Unexpected files or oversized sample bundle.')
        manifest = json.loads(archive.read('checksums.json'))
        if set(manifest) != expected-{'checksums.json'}:
            raise ValueError('Unexpected checksum manifest.')
        for name, record in manifest.items():
            content = archive.read(name)
            if len(content) != record['bytes'] or hashlib.sha256(content).hexdigest() != record['sha256']:
                raise ValueError(f'File integrity failure: {name}')
        report, source = json.loads(archive.read('report.json')), json.loads(archive.read('source.json'))
        if (report['scene_id'] != source['id']
                or report['acquisition'] != source['properties']['datetime']
                or report['band_order'] != ['B02','B03','B04','B08']):
            raise ValueError('Source provenance/band order mismatch.')
        total, usable = report['study_pixels'], report['usable_pixels']
        if not 0 < usable <= total <= math.prod(report['shape']):
            raise ValueError('Invalid coverage counts.')
        if not math.isclose(report['usable_fraction'],usable/total,abs_tol=1e-12):
            raise ValueError('Coverage denominator mismatch.')
        if report['model_trained'] or report['reviewed_labels_exist']:
            raise ValueError('Research sample must not claim a model or reviewed labels.')
    return {'integrity':'PASS','verified_files':len(manifest),
            'scene_id':report['scene_id'],'usable_fraction':report['usable_fraction'],
            'limits':'File/provenance checks only; not radiometric validation, forest labels or accuracy.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip',type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.zip),indent=2))
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile) as error:
        parser.exit(1,f'Bundle verification failed: {error}\n')
