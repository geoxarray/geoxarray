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
"""Tests for the xarray Dataset-specific accessor."""

from ._dataset_cases import cf_1gm_geos_b_a


def test_set_dims_modifies_data_arrs():
    ds = cf_1gm_geos_b_a()

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
