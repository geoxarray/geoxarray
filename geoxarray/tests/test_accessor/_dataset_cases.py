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
"""Test cases for Dataset-specific interfaces."""
from __future__ import annotations

import numpy as np
import xarray as xr
from dask import array as da

from ._data_array_cases import cf_grid_mapping_geos_no_wkt
from ._shared import OTHER_DIM_SIZE, X_DIM_SIZE, Y_DIM_SIZE


def cf_1gm_geos_y_x(y_coord: str = "y", x_coord: str = "x", other: str | None = None) -> xr.Dataset:
    rad_size: tuple[int, ...] = (Y_DIM_SIZE, X_DIM_SIZE)
    rad_dims: tuple[str, ...] = (y_coord, x_coord)
    if other:
        rad_size = (OTHER_DIM_SIZE,) + rad_size
        rad_dims = (other,) + rad_dims
    return xr.Dataset(
        {
            "Rad": xr.DataArray(
                da.zeros(rad_size),
                dims=rad_dims,
                attrs={"grid_mapping": "goes_imager_projection"},
            ),
            "different_spatial": xr.DataArray(
                da.zeros((Y_DIM_SIZE, X_DIM_SIZE)),
                dims=(f"not_{y_coord}", f"not_{x_coord}"),
            ),
            "scalar_var": xr.DataArray(0.0),
        },
        coords={
            y_coord: xr.DataArray(
                da.linspace(0.1265, 0.04257, Y_DIM_SIZE),
                dims=(y_coord,),
                attrs={"units": "rad"},
            ),
            x_coord: xr.DataArray(
                da.linspace(-0.07503, 0.06495, X_DIM_SIZE),
                dims=(x_coord,),
                attrs={"units": "rad"},
            ),
            "t": np.array("2017-09-02T18:03:34", dtype="datetime64[ns]"),
            "band_id": xr.DataArray(np.array([1], dtype=np.uint8), dims=("band",), attrs={"units": "1"}),
            "goes_imager_projection": cf_grid_mapping_geos_no_wkt(),
        },
    )


def cf_1gm_geos_other_b_a() -> xr.Dataset:
    return cf_1gm_geos_y_x("b", "a", other="other")


def cf_0gm_no_coords() -> xr.Dataset:
    return xr.Dataset(
        {
            "Rad": xr.DataArray(
                da.zeros((Y_DIM_SIZE, X_DIM_SIZE)),
                dims=("y", "x"),
            ),
            "different_spatial": xr.DataArray(
                da.zeros((Y_DIM_SIZE, X_DIM_SIZE)),
                dims=("not_y", "not_x"),
            ),
            "scalar_var": xr.DataArray(0.0),
        }
    )


def cf_3gm_geos_y_x() -> xr.Dataset:
    ds = cf_1gm_geos_y_x()
    ds["Rad2"] = ds["Rad"].copy()
    ds["Rad3"] = ds["Rad"].copy()

    gm2 = cf_grid_mapping_geos_no_wkt()
    gm2["longitude_of_projection_origin"] = -95.5
    ds.coords["goes_imager_projection2"] = gm2
    ds["Rad2"].attrs["grid_mapping"] = "goes_imager_projection2"

    gm3 = cf_grid_mapping_geos_no_wkt()
    gm3["longitude_of_projection_origin"] = -105.5
    ds.coords["goes_imager_projection3"] = gm3
    ds["Rad3"].attrs["grid_mapping"] = "goes_imager_projection3"

    return ds


def cf_3vars_1gm_geos_y_x() -> xr.Dataset:
    ds = cf_1gm_geos_y_x()
    ds["Rad2"] = ds["Rad"].copy()
    ds["Rad3"] = ds["Rad"].copy()
    return ds
