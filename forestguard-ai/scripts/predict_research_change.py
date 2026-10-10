"""Compare real December observations with a trusted weak-reference tree-cover proxy."""
import argparse
import base64
import csv
import hashlib
import html
import io
import json
import tempfile
import zipfile
from pathlib import Path

import joblib
import numpy as np
import rasterio
import sklearn
from rasterio.io import MemoryFile
from sklearn.ensemble import RandomForestClassifier

from assess_observation_pair import assess
from prepare_proxy_errors import ROOT, MODEL, MODEL_SHA, DATA, DATA_SHA, BEFORE, AFTER
from verify_weak_export import verify


def transitions(before, after, valid):
    result = np.full(valid.shape, 255, dtype='uint8')
    if not np.isin(before[valid], [0, 1]).all() or not np.isin(after[valid], [0, 1]).all():
        raise ValueError('Invalid observable proxy classes')
    # 0 stable other, 1 stable tree, 2 suspected tree loss, 3 suspected tree gain.
    for code, first, last in [(0, 0, 0), (1, 1, 1), (2, 1, 0), (3, 0, 1)]:
        result[valid & (before == first) & (after == last)] = code
    return result


def predict(output):
    output = Path(output)
    if output.exists():
        raise ValueError('Preserve existing research change output')
    verify(MODEL, MODEL_SHA, DATA, DATA_SHA)
    with zipfile.ZipFile(MODEL) as archive:
        manifest = json.loads(archive.read('model_manifest.json'))
        for name, version in [('numpy', np.__version__), ('sklearn', sklearn.__version__), ('joblib', joblib.__version__)]:
            if manifest['runtime'][name] != version:
                raise ValueError('Inference version mismatch: ' + name)
        for path, key in [(BEFORE, 'before_bundle'), (AFTER, 'bundle')]:
            if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['source_hashes'][key]:
                raise ValueError('Unexpected observation source')
        model = joblib.load(io.BytesIO(archive.read(manifest['selected_model_file'])))
    if type(model) is not RandomForestClassifier or model.n_features_in_ != 15 or not np.array_equal(model.classes_, [0, 1]):
        raise ValueError('Unsupported estimator')
    model.n_jobs = 1
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research_change_', dir=output.parent) as temporary:
        folder = Path(temporary)
        assessment = assess(BEFORE, AFTER, folder / 'observations')
        if assessment['status'] != 'PASS_DATA_CHECKS':
            raise ValueError('Insufficient common coverage')
        with rasterio.open(folder / 'observations/common_usable.tif') as raster:
            common = raster.read(1) == 1
            profile = raster.profile.copy()
        classes = []
        previews = []
        for path, name in [(BEFORE, 'before'), (AFTER, 'after')]:
            with zipfile.ZipFile(path) as archive:
                previews.append(base64.b64encode(archive.read('post_monsoon/preview.png')).decode('ascii'))
                with MemoryFile(archive.read('post_monsoon/features.tif')) as memory, memory.open() as raster:
                    if max(raster.shape) > 512 or list(raster.descriptions) != manifest['feature_order']:
                        raise ValueError('Unsupported feature crop/order')
                    values = raster.read(masked=True).filled(np.nan)
            if not np.isfinite(values[:, common]).all():
                raise ValueError('Nonfinite common features')
            predicted = np.full(common.shape, 255, dtype='uint8')
            for start in range(0, common.shape[0], 16):
                mask = common[start:start + 16]
                if mask.any():
                    predicted[start:start + 16][mask] = model.predict(values[:, start:start + 16][:, mask].T.astype('float32'))
            classes.append(predicted)
        changed = transitions(*classes, common)
        mapping = {'0': 'stable other-cover proxy', '1': 'stable tree-cover proxy',
                   '2': 'suspected tree-cover proxy loss', '3': 'suspected tree-cover proxy gain'}
        counts = {key: int((changed == int(key)).sum()) for key in mapping}
        assert sum(counts.values()) == int(common.sum())
        pixel_ha = abs(profile['transform'].a * profile['transform'].e) / 10000
        if profile['crs'].to_epsg() != 32643 or pixel_ha != .04:
            raise ValueError('Unexpected area grid')
        before_count, after_count = [int((array == 1).sum()) for array in classes]
        assert after_count - before_count == counts['3'] - counts['2']
        report = dict(assessment, format='forestguard-research-proxy-change-v1',
                      model_version=manifest['model_version'], model_sha256=MODEL_SHA,
                      dataset_sha256=DATA_SHA, model_kind='exploratory_weak_map_proxy',
                      class_mapping=mapping, transition_pixels=counts,
                      transition_area_ha={key: round(count * pixel_ha, 2) for key, count in counts.items()},
                      common_observable_area_ha=round(int(common.sum()) * pixel_ha, 2),
                      before_tree_proxy_ha=round(before_count * pixel_ha, 2),
                      after_tree_proxy_ha=round(after_count * pixel_ha, 2),
                      operational_use_approved=False, independent_forest_accuracy_measured=False,
                      synthetic=False, local_training_performed=False,
                      limits='Real images and model predictions, not confirmed forest changes. Before-date northern pixels were used in training; after-date southern pixels were used in model selection. This is not an independent accuracy test. Crop/shrub confusion, seasonal conditions and alignment uncertainty can produce apparent changes.')
        for name, array in [('before_classes.tif', classes[0]), ('after_classes.tif', classes[1]), ('change_classes.tif', changed)]:
            settings = dict(profile, count=1, dtype='uint8', nodata=255, compress='deflate')
            with rasterio.open(folder / name, 'w', **settings) as raster:
                raster.write(array, 1)
                raster.update_tags(model_kind=report['model_kind'], operational_use_approved='false', synthetic='false', model_version=report['model_version'])
        colors = {0: '#a18a62', 1: '#287d4d', 2: '#ef634b', 3: '#54cfb4'}
        shape = common.shape
        cells = ''.join(f'<rect x="{col}" y="{row}" width="1" height="1" fill="{colors[int(changed[row,col])]}"/>' for row, col in zip(*np.where(common)))
        panels = []
        for index, name in enumerate(['before', 'after', 'changes']):
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {shape[1]} {shape[0]}" role="img" aria-label="{name} research evidence"><image width="{shape[1]}" height="{shape[0]}" href="data:image/png;base64,{previews[0 if name=="before" else 1]}"/>' + (f'<g opacity="0.75">{cells}</g>' if name == 'changes' else '') + '</svg>'
            (folder / (name + '.svg')).write_text(svg, encoding='utf-8')
            panels.append(f'<section><h2>{assessment["observations"][index]["date"] if index<2 else "Estimated tree-cover transitions"}</h2>{svg}</section>')
        with (folder / 'changes.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(['transition', 'pixels', 'estimated_proxy_area_ha', 'before_date', 'after_date', 'independently_validated'])
            for key, label in mapping.items():
                writer.writerow([label, counts[key], report['transition_area_ha'][key], *[record['date'] for record in assessment['observations']], False])
        (folder / 'change_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compartment 279 estimated tree-cover change</title><style>body{font:16px system-ui;background:#f3f7f3;color:#173b2d;max-width:1000px;margin:auto;padding:24px}svg{width:100%;image-rendering:pixelated}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Compartment 279: estimated tree-cover change</h1><p>Research result from real satellite images. Red: suspected proxy loss; turquoise: suspected proxy gain; green: stable tree proxy; brown: stable other proxy. Only common clear pixels contribute to areas.</p><p>' + html.escape(report['limits']) + '</p>' + ''.join(panels) + '<h2>Source attribution</h2><p>' + html.escape(assessment['observations'][0]['attribution']) + '</p><pre>' + html.escape(json.dumps(report, indent=2)) + '</pre></html>'
        (folder / 'report.html').write_text(page, encoding='utf-8')
        hashes = {path.relative_to(folder).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in folder.rglob('*') if path.is_file()}
        (folder / 'checksums.json').write_text(json.dumps(hashes, indent=2) + '\n')
        folder.rename(output)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    print(json.dumps(predict(parser.parse_args().output), indent=2))
