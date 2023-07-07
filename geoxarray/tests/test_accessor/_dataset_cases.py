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
import numpy as np
import xarray as xr
from dask import array as da

from ._shared import OTHER_DIM_SIZE, X_DIM_SIZE, Y_DIM_SIZE


def cf_1gm_geos_y_x(y_coord="y", x_coord="x", other=None):
    rad_size = (Y_DIM_SIZE, X_DIM_SIZE)
    rad_dims = (y_coord, x_coord)
    if other:
        rad_size = (OTHER_DIM_SIZE,) + rad_size
        rad_dims = ("other",) + rad_dims
    return xr.Dataset(
        {
            "Rad": xr.DataArray(
                da.zeros(rad_size),
                dims=rad_dims,
                attrs={"grid_mapping": "goes_imager_projection"},
            )
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
        },
    )


def cf_1gm_geos_other_b_a():
    return cf_1gm_geos_y_x("b", "a", other="other")


def cf_0gm_no_coords():
    return xr.Dataset(
        {
            "Rad": xr.DataArray(
                da.zeros((Y_DIM_SIZE, X_DIM_SIZE)),
                dims=("y", "x"),
            ),
        }
    )


# TODO: Add case of multiple variables (3?) and 1 shared grid mapping
# TODO: Add case of multiple variable (3?) with different grid mappings
