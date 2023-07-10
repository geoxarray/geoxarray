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
"""Shared information and utilities for the data cases."""
from __future__ import annotations

import xarray as xr
from pyproj import CRS

from geoxarray.accessor import DEFAULT_GRID_MAPPING_VARIABLE_NAME

try:
    from pyresample import AreaDefinition
except ImportError:
    AreaDefinition = None


X_DIM_SIZE = 20
Y_DIM_SIZE = 10
ALT_DIM_SIZE = 5
OTHER_DIM_SIZE = 3
TIME_DIM_SIZE = 100


def check_written_crs(xr_obj: xr.DataArray | xr.Dataset, exp_crs: CRS, gmap_var_name: str | None) -> None:
    """Check that CRS and grid mapping information was written properly to the xarray object."""
    exp_cf_params = exp_crs.to_cf()

    assert xr_obj.geo.crs == exp_crs
    gmap_var = xr_obj.coords[gmap_var_name or DEFAULT_GRID_MAPPING_VARIABLE_NAME]
    assert set(exp_cf_params.items()).issubset(set(gmap_var.attrs.items()))
    assert gmap_var.attrs["crs_wkt"] == exp_crs.to_wkt()
    assert gmap_var.attrs["spatial_ref"] == exp_crs.to_wkt()
    assert xr_obj.encoding["grid_mapping"] == gmap_var_name or DEFAULT_GRID_MAPPING_VARIABLE_NAME
    assert "grid_mapping" not in xr_obj.attrs
