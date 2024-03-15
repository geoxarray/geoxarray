#!/usr/bin/env python
# Copyright geoxarray Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for the xarray DataArray-specific accessor."""
import numpy as np
import pytest
from pyproj import CRS

from ._data_array_cases import (
    band_as_read_by_rioxarray,
    cf_y_x,
    cf_y_x_with_bad_crs,
    cf_y_x_with_crs_coord,
    cf_y_x_with_crs_wkt_coord,
    geotiff_b_a,
    geotiff_bands_y_x,
    geotiff_x_y,
    geotiff_y_x,
    geotiff_y_x_bands,
    misc_t_z_y_x,
    misc_time_z_y_x,
    misc_y_x_z,
    misc_z_y_x,
    no_crs_no_dims_2d,
    pyr_geos_area_2d,
    raw_coords_lats1d_lons1d,
    tifffile_nonyx_with_geometa,
    tifffile_with_geometa,
)
from ._shared import (
    ALT_DIM_SIZE,
    MISSING_PYRESAMPLE,
    X_DIM_SIZE,
    Y_DIM_SIZE,
    check_written_crs,
)


@pytest.mark.parametrize(
    ("get_data_array", "exp_dims"),
    [
        (geotiff_b_a, ("y", "x")),
        (geotiff_x_y, ("x", "y")),
        (geotiff_y_x, ("y", "x")),
        (geotiff_bands_y_x, ("bands", "y", "x")),
        (geotiff_y_x_bands, ("y", "x", "bands")),
        (misc_t_z_y_x, ("time", "vertical", "y", "x")),
        (misc_time_z_y_x, ("time", "vertical", "y", "x")),
        (misc_y_x_z, ("y", "x", "vertical")),
        (misc_z_y_x, ("vertical", "y", "x")),
        (cf_y_x, ("y", "x")),
        (raw_coords_lats1d_lons1d, ("y", "x")),
    ],
)
def test_default_dim_decisions(get_data_array, exp_dims):
    data_arr = get_data_array()
    assert data_arr.geo.dims == exp_dims
    assert data_arr.geo.sizes["y"] == Y_DIM_SIZE
    assert data_arr.geo.sizes["x"] == X_DIM_SIZE
    if "vertical" in exp_dims:
        assert data_arr.geo.sizes["vertical"] == ALT_DIM_SIZE


def test_crs_no_crs():
    data_arr = no_crs_no_dims_2d()
    assert data_arr.geo._crs is None  # assert we haven't checked CRS info yet
    assert data_arr.geo.crs is None
    assert data_arr.geo._crs is False  # assert "cached" CRS findings
    assert data_arr.geo.crs is None


def test_crs_missing_grid_mapping():
    data_arr = cf_y_x()
    assert data_arr.geo._crs is None  # assert we haven't checked CRS info yet
    with pytest.warns(UserWarning, match=r"'grid_mapping' attribute found, but"):
        assert data_arr.geo.crs is None
    assert data_arr.geo._crs is False  # assert "cached" CRS findings
    assert data_arr.geo.crs is None


@pytest.mark.parametrize("data_func", [cf_y_x_with_crs_coord, cf_y_x_with_crs_wkt_coord])
def test_crs_from_cf_coordinate(data_func):
    data_arr = data_func()
    assert isinstance(data_arr.geo.crs, CRS)
    assert isinstance(data_arr.geo.crs, CRS)  # get cached CRS


def test_bad_crs_from_cf_coordinate():
    data_arr = cf_y_x_with_bad_crs()
    assert data_arr.geo.crs is None


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("gmap_var_name", [None, "my_gm"])
def test_no_crs_write_crs(inplace, gmap_var_name):
    data_arr = no_crs_no_dims_2d()
    new_crs = CRS.from_epsg(4326)

    assert data_arr.geo.crs is None
    new_data_arr = data_arr.geo.write_crs(new_crs, grid_mapping_name=gmap_var_name, inplace=inplace)

    assert new_data_arr is data_arr if inplace else new_data_arr is not data_arr
    check_written_crs(new_data_arr, new_crs, gmap_var_name)


@pytest.mark.skipif(MISSING_PYRESAMPLE, reason="Missing 'pyresample' dependency")
def test_pyresample_area_2d_crs():
    data_arr = pyr_geos_area_2d()
    assert data_arr.geo.crs == data_arr.attrs["area"].crs


@pytest.mark.skipif(MISSING_PYRESAMPLE, reason="Test dependency missing: pyresample")
def test_pyresample_write_crs():
    data_arr = pyr_geos_area_2d()
    assert "grid_mapping" not in data_arr.encoding
    assert "grid_mapping" not in data_arr.attrs
    assert "spatial_ref" not in data_arr.coords
    new_data_arr = data_arr.geo.write_crs()
    assert "grid_mapping" in new_data_arr.encoding
    assert "grid_mapping" not in new_data_arr.attrs
    assert "spatial_ref" in new_data_arr.coords


def test_write_crs_no_crs_found():
    data_arr = no_crs_no_dims_2d()
    assert "grid_mapping" not in data_arr.encoding
    assert "grid_mapping" not in data_arr.attrs
    assert data_arr.geo.crs is None
    with pytest.raises(RuntimeError):
        data_arr.geo.write_crs()


def test_write_coords_unknown():
    data_arr = no_crs_no_dims_2d()
    with pytest.raises(ValueError):
        data_arr.geo.write_spatial_coords()


X_EXP_COORDS = np.array(
    [
        -5434393.880734,
        -5433391.87209,
        -5432389.863446,
        -5431387.854802,
        -5430385.846158,
        -5429383.837514,
        -5428381.82887,
        -5427379.820226,
        -5426377.811582,
        -5425375.802938,
        -5424373.794294,
        -5423371.78565,
        -5422369.777006,
        -5421367.768362,
        -5420365.759718,
        -5419363.751074,
        -5418361.74243,
        -5417359.733786,
        -5416357.725142,
        -5415355.716498,
    ]
)
Y_EXP_COORDS = np.array(
    [
        5434393.880734,
        5433391.87209,
        5432389.863446,
        5431387.854802,
        5430385.846158,
        5429383.837514,
        5428381.82887,
        5427379.820226,
        5426377.811582,
        5425375.802938,
    ]
)


@pytest.mark.parametrize(
    ("data_func", "y_dim", "x_dim"),
    [
        (tifffile_with_geometa, "y", "x"),
        (tifffile_nonyx_with_geometa, "a", "b"),
    ],
)
def test_write_coords_tifffile(data_func, y_dim, x_dim):
    data_arr = data_func()
    assert "y" not in data_arr.coords
    assert "x" not in data_arr.coords

    new_data_arr = data_arr.geo.write_spatial_coords()
    assert y_dim in new_data_arr.coords
    assert x_dim in new_data_arr.coords
    assert "y" not in data_arr.coords
    assert "x" not in data_arr.coords
    assert y_dim not in data_arr.coords
    assert x_dim not in data_arr.coords
    np.testing.assert_allclose(
        new_data_arr.coords[x_dim],
        X_EXP_COORDS,
    )
    np.testing.assert_allclose(
        new_data_arr.coords[y_dim],
        Y_EXP_COORDS,
    )


def test_write_coords_pyr_area():
    data_arr = pyr_geos_area_2d()
    y_dim, x_dim = data_arr.dims
    assert "x" not in data_arr.coords
    assert "y" not in data_arr.coords
    assert x_dim not in data_arr.coords
    assert y_dim not in data_arr.coords

    new_data_arr = data_arr.geo.write_spatial_coords()
    assert "x" not in new_data_arr.coords
    assert "y" not in new_data_arr.coords
    assert x_dim in new_data_arr.coords
    assert y_dim in new_data_arr.coords
    assert x_dim not in data_arr.coords
    assert y_dim not in data_arr.coords
    np.testing.assert_allclose(
        new_data_arr.coords[x_dim],
        X_EXP_COORDS,
    )
    np.testing.assert_allclose(
        new_data_arr.coords[y_dim],
        Y_EXP_COORDS,
    )


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("has_spatial_ref", [False, True])
def test_using_gcps(inplace, has_spatial_ref):
    """Test using the GCPs."""
    data_arr = band_as_read_by_rioxarray()
    if not has_spatial_ref:
        data_arr = data_arr.drop_vars("spatial_ref")
    assert data_arr.geo.gcps is None

    geojson_gcps = """{'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'id': '1', 'info': '', 'row': 0.0, 'col': 0.0},
        'geometry': {'type': 'Point', 'coordinates': [33.03476120131667, 61.80752448531045, 126.43436405993998]}},
        {'type': 'Feature', 'properties': {'id': '2', 'info': '', 'row': 0.0, 'col': 530.0},
        'geometry': {'type': 'Point', 'coordinates': [32.64657656496346, 61.857612278077426, 126.43393892142922]}},
        {'type': 'Feature', 'properties': {'id': '3', 'info': '', 'row': 0.0, 'col': 1060.0},
        'geometry': {'type': 'Point', 'coordinates': [32.25713800902792, 61.90660152412569, 126.43354075308889]}},
        {'type': 'Feature', 'properties': {'id': '4', 'info': '', 'row': 0.0, 'col': 1590.0},
        'geometry': {'type': 'Point', 'coordinates': [31.86646667091431, 61.95448651271948, 126.43316515907645]}},
        {'type': 'Feature', 'properties': {'id': '5', 'info': '', 'row': 0.0, 'col': 2120.0},
        'geometry': {'type': 'Point', 'coordinates': [31.4745844704049, 62.001261591746335, 126.4328089589253]}},
        {'type': 'Feature', 'properties': {'id': '6', 'info': '', 'row': 0.0, 'col': 2650.0},
        'geometry': {'type': 'Point', 'coordinates': [31.081513897392732, 62.046921198482664, 126.4324697861448]}},
        {'type': 'Feature', 'properties': {'id': '7', 'info': '', 'row': 0.0, 'col': 3180.0},
        'geometry': {'type': 'Point', 'coordinates': [30.68727795468313, 62.09145986899579, 126.43214585445821]}}]}"""

    new_data_arr = data_arr.geo.write_gcps(geojson_gcps, inplace=inplace)
    if inplace:
        assert data_arr is new_data_arr
        assert new_data_arr.geo.gcps == geojson_gcps
    else:
        assert data_arr is not new_data_arr
        assert data_arr.geo.gcps is None
