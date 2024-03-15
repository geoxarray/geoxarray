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
"""Test cases for DataArray-specific interfaces."""
from __future__ import annotations

import xarray as xr
from dask import array as da
from pyproj import CRS

from ._shared import (
    ALT_DIM_SIZE,
    OTHER_DIM_SIZE,
    TIME_DIM_SIZE,
    X_DIM_SIZE,
    Y_DIM_SIZE,
    AreaDefinition,
)


def geotiff_y_x():
    return xr.DataArray(
        da.empty((Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("y", "x"),
    )


def geotiff_x_y():
    # transposed data
    return xr.DataArray(
        da.empty((X_DIM_SIZE, Y_DIM_SIZE)),
        dims=("x", "y"),
    )


def geotiff_b_a():
    return xr.DataArray(
        da.empty((Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("a", "b"),
    )


def geotiff_bands_y_x():
    return xr.DataArray(
        da.empty((OTHER_DIM_SIZE, Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("bands", "y", "x"),
    )


def geotiff_y_x_bands():
    return xr.DataArray(
        da.empty((Y_DIM_SIZE, X_DIM_SIZE, OTHER_DIM_SIZE)),
        dims=("y", "x", "bands"),
    )


def misc_z_y_x():
    return xr.DataArray(
        da.empty((ALT_DIM_SIZE, Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("z", "y", "x"),
    )


def misc_y_x_z():
    return xr.DataArray(
        da.empty((Y_DIM_SIZE, X_DIM_SIZE, ALT_DIM_SIZE)),
        dims=("y", "x", "z"),
    )


def misc_time_z_y_x():
    return xr.DataArray(
        da.empty((TIME_DIM_SIZE, ALT_DIM_SIZE, Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("time", "z", "y", "x"),
    )


def misc_t_z_y_x():
    return xr.DataArray(
        da.empty((TIME_DIM_SIZE, ALT_DIM_SIZE, Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("t", "z", "y", "x"),
    )


def raw_coords_lats1d_lons1d():
    return xr.DataArray(
        da.empty((Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("lats", "lons"),
        coords={
            "lons": da.linspace(25, 35, X_DIM_SIZE),
            "lats": da.linspace(25, 35, Y_DIM_SIZE),
        },
    )


def cf_y_x():
    return xr.DataArray(
        da.empty((Y_DIM_SIZE, X_DIM_SIZE)),
        dims=("y", "x"),
        attrs={
            "grid_mapping": "a_grid_map_var",
        },
    )


def cf_y_x_with_crs_coord():
    data_arr = cf_y_x()
    data_arr.coords["a_grid_map_var"] = cf_grid_mapping_geos_no_wkt()
    return data_arr


def cf_grid_mapping_geos_no_wkt():
    return xr.DataArray(
        -1,
        attrs={
            "long_name": "GOES-R ABI fixed grid projection",
            "grid_mapping_name": "geostationary",
            "perspective_point_height": 35786023.0,
            "semi_major_axis": 6378137.0,
            "semi_minor_axis": 6356752.31414,
            "inverse_flattening": 298.2572221,
            "latitude_of_projection_origin": 0.0,
            "longitude_of_projection_origin": -89.5,
            "sweep_angle_axis": "x",
        },
    )


def cf_y_x_with_crs_wkt_coord():
    data_arr = cf_y_x_with_crs_coord()
    crs = CRS.from_cf(data_arr.coords["a_grid_map_var"].attrs)
    data_arr.coords["a_grid_map_var"].attrs["crs_wkt"] = crs.to_wkt()
    return data_arr


def cf_y_x_with_bad_crs():
    data_arr = cf_y_x_with_crs_coord()
    del data_arr.coords["a_grid_map_var"].attrs["grid_mapping_name"]
    return data_arr


def no_crs_no_dims_2d():
    return xr.DataArray(da.empty((Y_DIM_SIZE, X_DIM_SIZE)))


def pyr_geos_area_2d() -> xr.DataArray:
    geos_crs = CRS.from_dict(
        {
            "proj": "geos",
            "sweep": "x",
            "lon_0": -75,
            "h": 35786023,
            "ellps": "GRS80",
            "no_defs": None,
        }
    )
    area = AreaDefinition(
        "",
        "",
        "",
        geos_crs,
        X_DIM_SIZE,
        Y_DIM_SIZE,
        (-5434894.885056, 5424874.798616, -5414854.712176, 5434894.885056),
    )
    data_arr = no_crs_no_dims_2d()
    data_arr.attrs["area"] = area
    return data_arr


def tifffile_with_geometa() -> xr.DataArray:
    """Create DataArray mimicking kerchunk's use of tifffile."""
    data_arr = geotiff_y_x()
    data_arr.attrs["ModelPixelScale"] = [1002.008644, 1002.008644, 0.0]
    data_arr.attrs["ModelTiepoint"] = [0.0, 0.0, 0.0, -5434894.885056, 5434894.885056, 0.0]
    return data_arr


def tifffile_nonyx_with_geometa() -> xr.DataArray:
    """Create DataArray mimicking kerchunk's use of tifffile."""
    data_arr = geotiff_b_a()
    data_arr.attrs["ModelPixelScale"] = [1002.008644, 1002.008644, 0.0]
    data_arr.attrs["ModelTiepoint"] = [0.0, 0.0, 0.0, -5434894.885056, 5434894.885056, 0.0]
    return data_arr


def cf_grid_mapping_with_wkt():
    """Create a grid mapping with a wkt."""
    return xr.DataArray(
        0,
        attrs={
            "crs_wkt": (
                'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,'
                'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,'
                'AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],'
                'AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]'
            ),
            "long_name": "Sentinel 1",
            "grid_mapping_name": "latitude_longitude",
            "horizontal_datum_name": "World Geodetic System 1984",
            "longitude_of_prime_meridian": 0.0,
            "inverse_flattening": 298.257223563,
            "prime_meridian_name": "Greenwich",
            "reference_ellipsoid_name": "WGS 84",
            "semi_major_axis": 6378137.0,
            "semi_minor_axis": 6356752.314245179,
        },
    )


def band_as_read_by_rioxarray() -> xr.Dataset:
    """Create a data array liking a band as read by rioxarray."""
    spatial_ref = cf_grid_mapping_with_wkt()
    data_array = xr.DataArray(
        da.zeros((1, Y_DIM_SIZE, X_DIM_SIZE)), dims=("band", "y", "x"), coords=dict(band=[1], spatial_ref=spatial_ref)
    )
    return data_array
