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


def cf_1gm_geos_y_x():
    return xr.Dataset(
        {
            "Rad": xr.DataArray(
                da.zeros((Y_DIM_SIZE, X_DIM_SIZE)),
                dims=("y", "x"),
                attrs={"grid_mapping": "goes_imager_projection"},
            )
        },
        coords={
            "y": xr.DataArray(
                da.linspace(0.1265, 0.04257, Y_DIM_SIZE),
                dims=("y",),
                attrs={"units": "rad"},
            ),
            "x": xr.DataArray(
                da.linspace(-0.07503, 0.06495, X_DIM_SIZE),
                dims=("x",),
                attrs={"units": "rad"},
            ),
            "t": np.array("2017-09-02T18:03:34", dtype=np.datetime64),
            "band_id": xr.DataArray(np.array([1], dtype=np.uint8), dims=("band",), attrs={"units": "1"}),
        },
    )


def cf_1gm_geos_b_a():
    return xr.Dataset(
        {
            "Rad": xr.DataArray(
                da.zeros((OTHER_DIM_SIZE, Y_DIM_SIZE, X_DIM_SIZE)),
                dims=("other", "b", "a"),
                attrs={"grid_mapping": "goes_imager_projection"},
            )
        },
        coords={
            "b": xr.DataArray(
                da.linspace(0.1265, 0.04257, Y_DIM_SIZE),
                dims=("b",),
                attrs={"units": "rad"},
            ),
            "a": xr.DataArray(
                da.linspace(-0.07503, 0.06495, X_DIM_SIZE),
                dims=("a",),
                attrs={"units": "rad"},
            ),
            "t": np.array("2017-09-02T18:03:34", dtype="datetime64[ns]"),
            "band_id": xr.DataArray(np.array([1], dtype=np.uint8), dims=("band",), attrs={"units": "1"}),
        },
    )
