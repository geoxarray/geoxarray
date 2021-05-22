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
    geotiff_y_x,
    geotiff_x_y,
    geotiff_a_b,
    cf_y_x,
    raw_coords_lats1d_lons1d,
    X_DIM_SIZE,
    Y_DIM_SIZE,
    ALT_DIM_SIZE,
)


@pytest.mark.parametrize(
    ("get_data_array", "exp_dims"),
    [
        (geotiff_y_x, ("y", "x")),
        (geotiff_x_y, ("x", "y")),
        (geotiff_a_b, ("y", "x")),
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
