"""Numerical research features; these functions do not generate land-cover labels."""
import numpy as np


def research_features(values, band_order, usable):
    values = np.asarray(values, dtype='float32')
    usable = np.asarray(usable, dtype=bool)
    if values.ndim != 3 or values.shape[1:] != usable.shape or values.shape[0] != len(band_order):
        raise ValueError('Band stack and usable mask must share a grid.')
    if len(set(band_order)) != len(band_order):
        raise ValueError('Band names must be unique.')
    required = {'B02','B04','B05','B08','B8A','B11'}
    if not required <= set(band_order):
        raise ValueError('Required visible/NIR/red-edge/SWIR bands are missing.')
    band = dict(zip(band_order, values))
    valid = usable & np.isfinite(values).all(axis=0)

    def ratio(numerator, denominator):
        result = np.full(usable.shape, np.nan, dtype='float32')
        np.divide(numerator, denominator, out=result, where=valid & (denominator > 1e-6))
        return result

    ndvi = ratio(band['B08']-band['B04'], band['B08']+band['B04'])
    ndre = ratio(band['B8A']-band['B05'], band['B8A']+band['B05'])
    ndmi = ratio(band['B8A']-band['B11'], band['B8A']+band['B11'])
    evi = ratio(2.5*(band['B08']-band['B04']), band['B08']+6*band['B04']-7.5*band['B02']+1)
    index_valid = valid & np.isfinite(ndvi) & (np.abs(ndvi) <= 1)
    for index in [ndre, ndmi]:
        index_valid &= np.isfinite(index) & (np.abs(index) <= 1)
    padded = np.pad(np.where(index_valid, ndvi, 0), 1)
    padded_valid = np.pad(index_valid, 1, constant_values=False)
    count = np.zeros(usable.shape, dtype='uint8')
    total = np.zeros(usable.shape, dtype='float32')
    squares = total.copy()
    height, width = usable.shape
    for dy in range(3):
        for dx in range(3):
            local = padded[dy:dy+height, dx:dx+width]
            count += padded_valid[dy:dy+height, dx:dx+width]
            total += local
            squares += local*local
    texture = np.sqrt(np.maximum(0, squares/9-(total/9)**2))
    features = np.concatenate([values, np.stack([ndvi,evi,ndre,ndmi,texture])])
    feature_valid = index_valid & (count == 9) & np.isfinite(features).all(axis=0)
    features[:, ~feature_valid] = np.nan
    return features, feature_valid, list(band_order)+['NDVI','EVI','NDRE_B8A_B05','NDMI_B8A_B11','NDVI_STD_3X3']
