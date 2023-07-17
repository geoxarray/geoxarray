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

import pytest
from pyproj import CRS

from ._data_array_cases import (
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
)
from ._shared import (
    ALT_DIM_SIZE,
    X_DIM_SIZE,
    Y_DIM_SIZE,
    AreaDefinition,
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


@pytest.mark.skipif(AreaDefinition is None, reason="Missing 'pyresample' dependency")
def test_pyresample_area_2d_crs():
    data_arr = pyr_geos_area_2d()
    assert data_arr.geo.crs == data_arr.attrs["area"].crs


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
