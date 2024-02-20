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
"""Helper functions for generating coordinate arrays for Xarray objects.

The functions in this module are public, but typically don't need to be
directly imported by users. It is recommended to use the various coordinate
methods of the geoxarray Xarray accessor (``.geo``).

"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import xarray as xr


def spatial_coords(data_arr: xr.DataArray) -> dict[str, npt.ArrayLike]:
    """Generate 1-dimensional spatial coordinate arrays for a DataArray.

    Currently supported cases are:

    * geotiff read with kerchunk via tifffile
    * pyresample ``AreaDefinition`` in ``.attrs["area"]``

    Parameters
    ----------
    data_arr
        DataArray object to extract geolocation information from and
        generate the corresponding coordinate arrays.

    Returns
    -------
        Dictionary mapping "x" and "y" dimension names to the corresponding
        1-dimensional array-like object. Currently only numpy arrays are
        returned.

    Raises
    ------
    ValueError
        If the necessary metadata can't be found in the DataArray

    """
    # TODO: Add dask functionality?
    # TODO: Add pyresample AreaDefinition support
    # TODO: Add 2D y/x nonuniform coordinates (pyresample's SwathDefinition, GCPs, etc)
    if "ModelPixelScale" in data_arr.attrs:
        # tifffile as loaded by kerchunk
        width = data_arr.geo.sizes["x"]
        height = data_arr.geo.sizes["y"]
        x_pixel_res, y_pixel_res = data_arr.attrs["ModelPixelScale"][:2]
        x_left, y_top = data_arr.attrs["ModelTiepoint"][3:5]
        x_coord = (x_left + x_pixel_res / 2.0) + np.arange(width) * x_pixel_res
        y_coord = (y_top - y_pixel_res / 2.0) - np.arange(height) * y_pixel_res
        # XXX: What to do with  'GTRasterTypeGeoKey': <RasterPixel.IsArea: 1>?
    elif "area" in data_arr.attrs:
        area_def = data_arr.attrs["area"]
        x_coord, y_coord = area_def.get_proj_vectors()
    else:
        raise ValueError("Unknown data structure. Can't compute spatial coordinates.")
    return {"y": y_coord, "x": x_coord}
