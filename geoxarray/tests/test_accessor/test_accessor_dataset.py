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
"""Tests for the xarray Dataset-specific accessor."""
import pytest
from pyproj import CRS

from ._data_array_cases import cf_grid_mapping_geos_no_wkt
from ._dataset_cases import (
    cf_0gm_no_coords,
    cf_1gm_geos_other_b_a,
    cf_1gm_geos_y_x,
    cf_3gm_geos_y_x,
)
from ._shared import check_written_crs


def test_set_dims_modifies_data_arrs():
    ds = cf_1gm_geos_other_b_a()

    # the dims are unchanged if we only use the DataArray
    assert ds["Rad"].geo.dims != ("other", "y", "x")

    new_ds = ds.geo.set_dims(x="a", y="b")
    # original dataset is unchanged
    assert "a" in ds.geo.dims
    assert "y" not in ds.geo.dims
    # new dataset has new dimension mapping
    assert "a" not in new_ds.geo.dims
    assert "y" in new_ds.geo.dims
    # the dims should still not be modified on the DataArray
    assert ds["Rad"].geo.dims != ("other", "y", "x")

    new_ds2 = new_ds.geo.write_dims()
    # the basic xarray object itself has the new dimensions
    assert "a" not in new_ds2.dims
    assert "y" in new_ds2.dims
    # original dataset is unchanged
    assert ds["Rad"].geo.dims == ("other", "b", "a")
    # the underlying DataArrays all have renamed dimensions
    assert new_ds2["Rad"].geo.dims == ("other", "y", "x")


def test_crs_no_crs():
    ds = cf_0gm_no_coords()
    assert ds.geo.crs is None


def test_grid_mapping_single_crs_coord():
    ds = cf_1gm_geos_y_x()
    assert ds.geo.grid_mapping == "goes_imager_projection"


def test_crs_single_crs_coord():
    ds = cf_1gm_geos_other_b_a()
    assert ds.geo.crs == CRS.from_cf(cf_grid_mapping_geos_no_wkt().attrs)


def test_crs_three_crs_coord():
    ds = cf_3gm_geos_y_x()
    with pytest.raises(RuntimeError):
        ds.geo.crs


@pytest.mark.parametrize("inplace", [False, True])
@pytest.mark.parametrize("gmap_var_name", [None, "my_gm"])
def test_crs_write_crs(inplace, gmap_var_name):
    ds = cf_0gm_no_coords()
    new_crs = CRS.from_epsg(4326)

    assert ds.geo.crs is None
    new_ds = ds.geo.write_crs(new_crs, grid_mapping_name=gmap_var_name, inplace=inplace)
    assert new_ds is ds if inplace else new_ds is not ds
    check_written_crs(new_ds, new_crs, gmap_var_name)
