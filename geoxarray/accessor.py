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
"""XArray extensions via accessor objects.

The functionality in this module can be accessed via the `.geo` accessor on
any xarray DataArray or Dataset object.

Geolocation cases that these accessors are supposed to be able to handle:

1. CF compliant Dataset: A :class:`~xarray.Dataset` object with one or
   more data variables and one CRS specification variable. By default
   a 'grid_mapping' attribute is used to specify the name of the variable.

   http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch05s06.html

"""

import xarray as xr
from pyproj import CRS

try:
    from pyresample.geometry import AreaDefinition, SwathDefinition
    has_pyresample = True
except ImportError:
    AreaDefinition = SwathDefinition = None
    has_pyresample = False


try:
    from rasterio.crs import CRS as RioCRS
    has_rasterio = True
except ImportError:
    RioCRS = None
    has_rasterio = False


class _SharedGeoAccessor(object):
    """Accessor functionality shared between Dataset and DataArray objects."""

    def __init__(self, xarray_obj):
        self._obj = xarray_obj
        self._x_dim = None
        self._y_dim = None
        self._vertical_dim = None
        self._time_dim = None
        # map current dimension to geoxarray preferred dim name
        self._dim_map = {}

        self._crs = None
        self._is_gridded = None
        self.set_dims()

    def set_dims(self, x=None, y=None, vertical=None, time=None):
        """Set preferred dimension names.

        GeoXarray will use this information for future operations.
        If any of the dimensions are not provided they will be found
        by best guess.

        Parameters
        ----------

        x : str or None
            Name of the X dimension. This dimension usually exists with
            a corresponding coordinate variable in meters for
            gridded/projected data.
        y : str or None
            Name of the Y dimension. Similar to the X dimension but on the Y
            axis.
        vertical : str or None
            Name of the vertical or Z dimension. This dimension usually exists
            with a corresponding coordinate variable in meters for altitude
            or pressure level (ex. hPa, millibar, etc).
        time : str or None
            Name of the time dimension. This dimension usually exists with a
            corresponding coordinate variable with time objects.

        """
        obj = self._obj
        dims = obj.dims
        if x is None:
            if 'x' in dims:
                self._x_dim = 'x'
        if y is None:
            if 'y' in dims:
                self._y_dim = 'y'
        if vertical is None:
            for z_dim in ('z', 'vertical', 'pressure_level'):
                if z_dim in dims:
                    self._vertical_dim = z_dim
                    break
        if time is None:
            for t_dim in ('time', 't'):
                if t_dim in dims:
                    self._time_dim = t_dim
                    break

        self._dim_map[self._x_dim] = 'x'
        self._dim_map[self._y_dim] = 'y'
        self._dim_map[self._vertical_dim] = 'vertical'
        self._dim_map[self._time_dim] = 'time'

    @property
    def dims(self):
        """Get preferred dimension names in order."""
        return tuple(self._dim_map.get(dname, dname) for dname in self._obj.dims)

    @property
    def sizes(self):
        """Get size map with preferred dimension names."""
        # return the same type of object as xarray
        sizes_dict = {}
        for dname, size in self._obj.sizes.items():
            sizes_dict[self._dim_map.get(dname, dname)] = size
        return self._obj.sizes.__class__(sizes_dict)

    @property
    def crs(self):
        if self._crs is not None:
            return self._crs

        coords_crs = self._obj.coords.get('crs')
        attrs_crs = self._obj.attrs.get('crs')
        area = self._obj.attrs.get('area')
        grid_mapping = self._obj.attrs.get('grid_mapping')
        # TODO: Check for lon/lat 2D coordinate arrays
        if grid_mapping:
            self._crs = CRS.from_cf(self._obj[grid_mapping].attrs)
        elif coords_crs is not None:
            crs = CRS.from_user_input(coords_crs)
        elif attrs_crs is not None:
            crs = CRS.from_user_input(attrs_crs)
        elif has_pyresample and isinstance(area, AreaDefinition):
            if hasattr(area, 'crs'):
                crs = area.crs
            else:
                crs = CRS.from_dict(area.proj_dict)
        elif has_pyresample and isinstance(area, SwathDefinition):
            # TODO: Convert and gather information from definitions
            self._is_gridded = False
        else:
            crs = False

        self._crs = crs
        return self._crs

    @crs.setter
    def crs(self, value):
        """Force the CRS for this object.

        Set to `None` for the CRS to be recalculated.

        """
        self._crs = value

    def get_lonlats(self, chunks=None):
        """Return longitude and latitude arrays.

        Parameters
        ----------
        chunks : None or int
            Specify chunk size for dask arrays.

        Returns
        -------
        Longitude and latitude dask arrays. If `chunks` is None then a
        numpy array is returned.

        """
        raise NotImplementedError()

    def plot(self):
        """Plot data on a map."""
        # TODO: Support multiple backends (cartopy, geoviews, etc)?
        raise NotImplementedError()

    def freeze(self):
        """Set a 'crs' coordinate to the current computed CRS.

        This modifies the current metadata and assumes that no new CRS
        information will be added or modified from now on.

        """
        # XXX: Is this useful or needed at all?
        raise NotImplementedError()


@xr.register_dataset_accessor('geo')
class GeoDatasetAccessor(_SharedGeoAccessor):
    def find_cf_grid_mapping(self):
        """Search for CF standard grid mapping information."""
        params = super(GeoDataArrayAccessor, self).find_cf_grid_mapping()
        if not params and 'grid_mapping' in self._obj.attrs:
            params = self._obj.variables[self._obj.attrs['grid_mapping']]
        return params

    def set_cf_grid_mapping_parameters(self, grid_mapping_var_name):
        """Specify the variable containing the CF-compliant CRS information"""
        raise NotImplementedError()

    def set_ungridded_coordinates(self, lon_var_name, lat_var_name):
        """Specify longitude and latitude variables defining geolocation.

        Setting geolocation this way can be useful when using lazy arrays
        (dask) and computing large lon/lat arrays could be wasteful when
        stored in `.coords`.

        """
        raise NotImplementedError()


@xr.register_dataarray_accessor('geo')
class GeoDataArrayAccessor(_SharedGeoAccessor):
    pass
