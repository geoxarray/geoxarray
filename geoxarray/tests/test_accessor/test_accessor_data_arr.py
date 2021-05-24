#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from ._data_array_cases import (
    cf_y_x,
    geotiff_b_a,
    geotiff_bands_y_x,
    geotiff_x_y,
    geotiff_y_x,
    geotiff_y_x_bands,
    misc_t_z_y_x,
    misc_time_z_y_x,
    misc_y_x_z,
    misc_z_y_x,
    raw_coords_lats1d_lons1d,
)
from ._shared import ALT_DIM_SIZE, X_DIM_SIZE, Y_DIM_SIZE


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
