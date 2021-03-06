"""Module for converting xarray datasets to and from matrix formats for Machine
learning purposes.
"""
import numpy as np
import pandas as pd
import xarray as xr
import pytest

from .datasets import tiltwave
from .data_matrix import (DataMatrix, Normalizer, dataset_to_mat, compute_weighted_scale,
                          stack_cat, unstack_cat)


def _assert_dataset_approx_eq(D, x):
    for k in D.data_vars:
        np.testing.assert_allclose(D[k], x[k].transpose(*D[k].dims))


def test_datamatrix():

    # setup data
    a = tiltwave()
    b = a.copy()
    D = xr.Dataset({'a': a, 'b': b})

    mat = DataMatrix(['x'])
    y = mat.dataset_to_mat(D)

    assert y.dims == ('samples', 'features')

    x = mat.mat_to_dataset(y, sample_dim='x')

    _assert_dataset_approx_eq(D, x)

    # test on just one sample
    x0 = mat.mat_to_dataset(y[0])
    d0 = D.isel(x=0)
    _assert_dataset_approx_eq(d0, x0)

    # test when variables have different dimensionality
    D = xr.Dataset({'a': a, 'b': b.isel(z=0)})
    mat = DataMatrix(sample_dims=['x'])
    y = mat.dataset_to_mat(D)
    assert y.dims == ('samples', 'features')
    x = mat.mat_to_dataset(y)
    _assert_dataset_approx_eq(D, x)


def test_stack_cat():

    # setup data
    a = tiltwave()
    b = a.copy()
    D = xr.Dataset({'a': a, 'b': b})

    feature_dims = ['z']
    y = stack_cat(D, 'features', feature_dims)\
        .transpose("x", "features")

    assert y.dims == ('x', 'features')

    x = unstack_cat(y, "features")
    _assert_dataset_approx_eq(D, x)

    # test on just one sample
    x0 = unstack_cat(y[0], "features")
    d0 = D.isel(x=0)
    _assert_dataset_approx_eq(d0, x0)

    # test when data is cast as numpy array
    y0 = y.data[0]
    coords = (y.coords['features'],)
    y0 = xr.DataArray(y0, coords)
    x0 = unstack_cat(y0, 'features')

    # test when variables have different dimensionality
    D = xr.Dataset({'a': a, 'b': b.isel(z=0)})
    y = stack_cat(D, 'features', feature_dims)\
            .transpose('x', 'features')
    x = unstack_cat(y, 'features')
    _assert_dataset_approx_eq(D, x)

    # another test
    ds = D.isel(z=0)
    ds_flat = stack_cat(ds, 'features', ['x'])
    ds_comp = unstack_cat(ds_flat, 'features')
    _assert_dataset_approx_eq(ds, ds_comp)

    # test for scalar variables
    a = xr.DataArray(np.r_[:6], dims=('x'), coords={'x': np.r_[:6]})
    ds = xr.Dataset({'a': a, 'b': 1.0})
    ds_flat = stack_cat(ds, 'features', ['x'])
    ds_comp = unstack_cat(ds_flat, 'features')
    _assert_dataset_approx_eq(ds, ds_comp)




def test_normalizer():
    # setup data
    a = tiltwave()
    b = a.copy()
    D = xr.Dataset({'a': a, 'b': b, 'c': a.isel(z=10)})

    w = np.exp(-a.z/10e3/2)
    w /= w.sum()
    norm = Normalizer(sample_dims=['x'], weight=w)
    d_norm = norm.transform(D)
    scales = compute_weighted_scale(weight=w, sample_dims=['x'], ds=d_norm)

    for k in scales:
        np.testing.assert_allclose(scales[k], 1.0)

    # test weight matrix
    # normalizer = norm.matrix


    # print((normalizer**2 * w).sum('z'), scales)
    # _assert_dataset_approx_eq((D-D.mean('x'))/(normalizer**2).sum('z').pipe(np.sqrt),
    #                           d_norm)

if __name__ == '__main__':
    test_datamatrix()
