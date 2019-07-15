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
        # self._center = None
        self._crs = None
        self._is_gridded = True
        self._cf_grid_mapping_parameters = None

    @property
    def cf_grid_mapping_parameters(self):
        return self._cf_grid_mapping_parameters

    @cf_grid_mapping_parameters.setter
    def cf_grid_mapping_parameters(self, value):
        self._cf_grid_mapping_parameters = value
        # reset the CRS object so it gets recalculated
        self._crs = None

    def find_cf_grid_mapping(self):
        """Search for CF standard grid mapping information."""
        return self._cf_grid_mapping_parameters

    @property
    def crs(self):
        if self._crs is not None:
            return self._crs

        coords_crs = self._obj.coords.get('crs')
        attrs_crs = self._obj.attrs.get('crs')
        area = self._obj.attrs.get('area')
        cf_mapping_params = self.find_cf_grid_mapping()
        self._is_gridded = True
        if cf_mapping_params:
            # TODO: Convert CF params to CRS object
            self._cf_grid_mapping_parameters = cf_mapping_params
        elif coords_crs is not None:
            crs = coords_crs
            # TODO: Convert to geoxarray CRS object
        elif attrs_crs is not None:
            crs = attrs_crs
            # TODO: Convert to geoxarray CRS object
        elif has_pyresample and isinstance(area, AreaDefinition):
            # TODO: Convert and gather information from definitions
            pass
        elif has_pyresample and isinstance(area, SwathDefinition):
            # TODO: Convert and gather information from definitions
            self._is_gridded = False
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

    def set_xy_variables(self, x_var_name, y_var_name):
        """Specify the variables defining the X and Y coordinates for the gridded data.

        This method assumes 'grid_mapping' is either already set in `.attrs`
        or will be set with `set_grid_mapping`.

        """
        raise NotImplementedError()


@xr.register_dataarray_accessor('geo')
class GeoDataArrayAccessor(_SharedGeoAccessor):
    pass
