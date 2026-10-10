"""Cloud-only annual crops and weak-reference predictions; no invented imagery."""
import base64
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import Path


def annual_run(study,base_run,feature_builder,model_bytes,expected_sha,output_runner):
    import numpy as np
    import rasterio
    import sklearn
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    if hashlib.sha256(model_bytes).hexdigest()!=expected_sha:raise ValueError('Untrusted model archive')
    with zipfile.ZipFile(io.BytesIO(model_bytes)) as archive:
        manifest=json.loads(archive.read('model_manifest.json'))
        model_available=all(manifest['runtime'][name]==version for name,version in [('numpy',np.__version__),('sklearn',sklearn.__version__),('joblib',joblib.__version__)])
        model=joblib.load(io.BytesIO(archive.read(manifest['selected_model_file']))) if model_available else None
    if model is not None:
        if type(model) is not RandomForestClassifier or model.n_features_in_!=15 or not np.array_equal(model.classes_,[0,1]):raise ValueError('Unsupported annual proxy estimator')
        model.n_jobs=1
    folder=output_runner(study,base_run,feature_builder)
    research=json.loads((folder/'research_report.json').read_bytes());rows=[]
    for record in research['acquisitions']:
        year=int(record['season']);name=str(year)
        with rasterio.open(folder/name/'features.tif') as raster:
            if max(raster.shape)>256 or list(raster.descriptions)!=manifest['feature_order']:raise ValueError('Invalid annual feature grid')
            values=raster.read(masked=True).filled(np.nan);profile=raster.profile.copy()
        with rasterio.open(folder/name/'usable_mask.tif') as raster:valid=raster.read(1)==1
        if not np.isfinite(values[:,valid]).all():raise ValueError('Invalid annual feature values')
        predicted=np.full(valid.shape,255,dtype='uint8')
        if model is not None:
            for start in range(0,valid.shape[0],16):
                mask=valid[start:start+16]
                if mask.any():predicted[start:start+16][mask]=model.predict(values[:,start:start+16][:,mask].T.astype('float32'))
            with rasterio.open(folder/name/'proxy_classes.tif','w',**dict(profile,count=1,dtype='uint8',nodata=255)) as raster:
                raster.write(predicted,1);raster.update_tags(model_kind='exploratory_weak_map_proxy',operational_use_approved='false',acquisition_date=record['acquisition'])
        count=int((predicted==1).sum()) if model is not None else None
        rows.append({'year':year,'date':record['acquisition'][:10],'scene_id':record['scene_id'],
                     'usable_pixels':int(valid.sum()),'study_pixels':record['inside_study_pixels'],
                     'coverage_fraction':record['usable_fraction_inside_study'],
                     'tree_cover_proxy_percent':100*count/int(valid.sum()) if count is not None else None,
                     'tree_cover_proxy_ha':count*.04 if count is not None else None,
                     'median_ndvi':float(np.median(values[record['feature_order'].index('NDVI')][valid])),
                     'model_version':manifest['model_version'] if model is not None else None,
                     'attribution':record['attribution'],'license_url':record['source_license_url'],
                     'canopy_density_percent':None,'synthetic':False})
    report={'format':'forestguard-annual-observations-v1','years_requested':[2022,2023,2024,2025,2026],
            'study_area_version':study['features'][0]['properties']['study_area_version'],
            'observations':sorted(rows,key=lambda row:row['year']),'model_sha256':expected_sha,
            'model_available':model_available,'independent_forest_accuracy_measured':False,
            'limits':'Percentages describe predicted tree-cover class extent within each year\'s clear observed area, not canopy density. Differences in annual percentages are not automatically forest loss; pairwise common coverage and seasonal review are required. Missing images remain missing. Model transfer to these years/seasons has not been independently evaluated.'}
    (folder/'annual_report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    selected=['annual_report.json','research_report.json','boundary.geojson']
    for row in rows:selected.extend(str(row['year'])+'/'+name for name in ['preview.png','features.tif','usable_mask.tif','study_mask.tif','report.json','source.json']+(['proxy_classes.tif'] if model is not None else []))
    hashes={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in selected}
    (folder/'annual_checksums.json').write_bytes((json.dumps(hashes,indent=2)+'\n').encode())
    output=folder/'forestguard_annual_2022_2026.zip'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in [*selected,'annual_checksums.json']:archive.write(folder/name,name)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:raise ValueError('Annual export CRC failure')
        for name,digest in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=digest:raise ValueError('Annual export checksum failure')
    # Kaggle's output tree hides deeply nested files by default.
    download=folder.parent.parent/output.name
    shutil.copyfile(output,download)
    print(json.dumps(report,indent=2));print('DOWNLOAD:',download)
    return download
