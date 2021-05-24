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

   https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch05s06.html
2. Geotiff DataArrays: A :class:`~xarray.DataArray` object returned by either
   the ``rioxarray`` library or by :func:`xarray.open_rasterio``.
3. Raw lon/lat coordinate arrays: A :class:`~xarray.DataArray` or :class:`~xarray.Dataset`
   object that contains 1D or 2D longitude and latitude arrays defining the
   coordinates of the data.

These accessors attempt to provide standard interfaces to the following information
from these different data cases:

1. Standard dimensions: X (columns), Y (rows), Vertical, and Time.
2. Coordinate Reference System (CRS)

Lastly, these accessor provide basic wrappers around other tools that are
typically used with geospatial data (resampling, plotting, etc) or converting
to other formats (CF compatible NetCDF file).

"""

from __future__ import annotations

import warnings
from typing import Optional

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
        """Set handle for xarray object."""
        self._obj = xarray_obj
        self._crs = None
        self._x_dim = None
        self._y_dim = None
        self._vertical_dim = None
        self._time_dim = None
        self._dim_map = False

    def _get_obj(self, inplace):
        """Get the object to modify.

        Parameters
        ----------
        inplace: bool
            If True, returns self.

        Returns
        -------
        :obj:`xarray.Dataset` | :obj:`xarray.DataArray`

        """
        if inplace:
            return self._obj
        obj_copy = self._obj.copy(deep=True)
        # preserve attribute information
        obj_copy.geo._crs = self._crs
        obj_copy.geo._x_dim = self._x_dim
        obj_copy.geo._y_dim = self._y_dim
        obj_copy.geo._vertical_dim = self._vertical_dim
        obj_copy.geo._time_dim = self._time_dim
        return obj_copy

    @property
    def dim_map(self):
        """Map current data dimension to geoxarray preferred dim name."""
        if self._dim_map is False:
            # we haven't determined dimensions yet
            self.set_dims(inplace=True)

        if self._dim_map is None:
            self._dim_map = {}
            if self._x_dim is not None:
                self._dim_map[self._x_dim] = "x"
            if self._y_dim is not None:
                self._dim_map[self._y_dim] = "y"
            if self._vertical_dim is not None:
                self._dim_map[self._vertical_dim] = "vertical"
            if self._time_dim is not None:
                self._dim_map[self._time_dim] = "time"

        return self._dim_map

    @property
    def dims(self):
        """Get preferred dimension names in order."""
        return tuple(self.dim_map.get(dname, dname) for dname in self._obj.dims)

    @property
    def sizes(self):
        """Get size map with preferred dimension names."""
        # return the same type of object as xarray
        sizes_dict = {}
        for dname, size in self._obj.sizes.items():
            sizes_dict[self.dim_map.get(dname, dname)] = size
        return self._obj.sizes.__class__(sizes_dict)

    def write_dims(self, inplace: bool = False):
        """Rename object's dimensions to match geoxarray's preferred dimension names."""
        obj_copy = self._get_obj(inplace)
        return obj_copy.rename(self.dim_map)


@xr.register_dataset_accessor("geo")
class GeoDatasetAccessor(_SharedGeoAccessor):
    """Provide Dataset geolocation helper functions from a `.geo` accessor."""

    def set_dims(
        self,
        x: Optional[str] = None,
        y: Optional[str] = None,
        vertical: Optional[str] = None,
        time: Optional[str] = None,
        inplace: bool = False,
    ):
        """Tell geoxarray the names of the provided dimensions in this Dataset.

        Parameters
        ----------
        x
        y
        vertical
        time
        inplace

        """
        all_dims = {
            "x": x,
            "y": y,
            "vertical": vertical,
            "time": time,
        }

        obj_copy = self._get_obj(inplace)
        # tell the dim_map property to produce the "as-is" dim map
        obj_copy.geo._dim_map = None
        dim_map = obj_copy.geo.dim_map
        for data_arr in self._obj.data_vars.values():
            dims = {k: v for k, v in all_dims.items() if v in data_arr.dims}
            if not dims:
                continue
            var_dim_map = data_arr.geo.set_dims(**dims, inplace=True).geo.dim_map
            self._update_gx_dim_dict(dim_map, var_dim_map)

        # update our attributes
        for dim_name, gx_dim_name in dim_map.items():
            if gx_dim_name is None:
                continue
            setattr(obj_copy.geo, f"_{gx_dim_name}_dim", dim_name)
        # tell the dim_map to get regenerated
        obj_copy.geo._dim_map = None
        return obj_copy

    def _update_gx_dim_dict(self, old, new):
        for k, v in new.items():
            if v in ("x", "y", "time", "vertical"):
                old[k] = v
        return old

    def set_crs(self, crs=None, variables=None):
        """Set CRS for this Dataset's variables.

        Parameters
        ----------
        crs : pyproj.crs.CRS
            Set CRS for specified variables to this CRS object. If not
            provided then the variables metadata is used to determine the
            best CRS (CF 'grid_mapping' variable, 'crs' attribute, etc).
        variables : iterable
            Names of variables that will have CRS information applied or
            determined. If not provided then all variables will be used or
            checked.

        Returns
        -------
        dict
            Map of variable names to DataArray objects with CRS objects
            applied.

        """
        if variables is None:
            variables = self._obj.variables.keys()

        applied_vars = {}
        gmap_names = {}
        for var_name in variables:
            var = self._obj[var_name]
            if crs is not None:
                var.geo.crs = crs
                applied_vars[var_name] = var
                continue

            # distribute grid_mapping variables to data variables if present
            gmap_name = var.attrs.get("grid_mapping")
            if gmap_name in self._obj.variables:
                gmap_var = self._obj[gmap_name]
                if gmap_name not in gmap_names:
                    gmap_crs = CRS.from_cf(gmap_var.attrs)
                    gmap_names[gmap_name] = gmap_crs
                var.geo.crs = gmap_names[gmap_name]
                applied_vars[var_name] = var
                continue

            # let the variable determine its own CRS
            applied_vars[var_name] = var
        return applied_vars

    def _set_crs_objects(self, crs=None, variables=None):
        """Get CRS object for each variable."""
        var_dict = self.set_crs(crs=crs, variables=variables)
        return {var_name: var.geo.crs for var_name, var in var_dict.items()}

    @property
    def crs(self):
        """Shared CRS object between all geolocated variables."""
        if self._crs is False:
            return None
        elif self._crs is not None:
            return self._crs
        applied_crs = set(self._set_crs_objects().values())
        num_crs = len(applied_crs)
        if num_crs == 1:
            self._crs = tuple(applied_crs)[0]
            return self._crs
        elif num_crs >= 1:
            raise RuntimeError("Dataset has more than one CRS")
        else:
            raise RuntimeError("No CRS information found in Dataset")


@xr.register_dataarray_accessor("geo")
class GeoDataArrayAccessor(_SharedGeoAccessor):
    """Provide DataArray geolocation helper functions from a `.geo` accessor."""

    def __init__(self, data_arr_obj):
        """Initialize a 'best guess' dimension mapping to preferred dimension names."""
        self._is_gridded = None
        super(GeoDataArrayAccessor, self).__init__(data_arr_obj)

    def _get_obj(self, inplace):
        """Get the object to modify.

        Parameters
        ----------
        inplace: bool
            If True, returns self.

        Returns
        -------
        :obj:`xarray.Dataset` | :obj:`xarray.DataArray`

        """
        obj_copy = super()._get_obj(inplace)
        # preserve attribute information
        obj_copy.geo._is_gridded = self._is_gridded
        return obj_copy

    def set_dims(self, x=None, y=None, vertical=None, time=None, inplace=True):
        """Set preferred dimension names inside the GeoXarray accessor.

        GeoXarray will use this information for future operations.
        If any of the dimensions are not provided they will be found
        by best guess.

        This information does not rename or modify the data of the Xarray
        object itself.

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
        obj = self._get_obj(inplace)
        dims = obj.dims
        if x is None and self._x_dim is None:
            if "x" in dims:
                obj.geo._x_dim = "x"
        elif x is not None:
            assert x in dims
            obj.geo._x_dim = x

        if y is None and self._y_dim is None:
            if "y" in dims:
                obj.geo._y_dim = "y"
        elif y is not None:
            assert y in dims
            obj.geo._y_dim = y

        if len(dims) == 2 and self._x_dim is None and self._y_dim is None:
            obj.geo._y_dim = dims[0]
            obj.geo._x_dim = dims[1]

        if vertical is None and self._vertical_dim is None:
            for z_dim in ("z", "vertical", "pressure_level"):
                if z_dim in dims:
                    obj.geo._vertical_dim = z_dim
                    break
        elif vertical is not None:
            assert vertical in dims
            obj.geo._vertical_dim = vertical

        if time is None and self._time_dim is None:
            for t_dim in ("time", "t"):
                if t_dim in dims:
                    obj.geo._time_dim = t_dim
                    break
        elif time is not None:
            assert time in dims
            obj.geo._time_dim = time

        obj.geo._dim_map = None
        return obj

    @property
    def crs(self):
        if self._crs is False:
            return None
        elif self._crs is not None:
            return self._crs

        grid_mapping = self._obj.attrs.get("grid_mapping")
        if grid_mapping:
            warnings.warn(
                "'grid_mapping' attribute found, but no grid_mapping variable"
                " was provided. Use 'data_arr.geo.set_cf_grid_mapping' to "
                "provide one. Will search other metadata for CRS information."
            )

        # TODO: Check for lon/lat 2D coordinate arrays
        coords_crs = self._obj.coords.get("crs")
        attrs_crs = self._obj.attrs.get("crs")
        area = self._obj.attrs.get("area")
        if coords_crs is not None:
            crs = CRS.from_user_input(coords_crs)
        elif attrs_crs is not None:
            crs = CRS.from_user_input(attrs_crs)
        elif has_pyresample and isinstance(area, AreaDefinition):
            crs = area.crs
        elif has_pyresample and isinstance(area, SwathDefinition):
            # TODO: Convert and gather information from definitions
            self._is_gridded = False
            crs = False
        else:
            crs = False

        self._crs = crs
        return self._crs if self._crs is not False else None

    @crs.setter
    def crs(self, value):
        """Force the CRS for this object.

        Set to `None` for the CRS to be recalculated.

        """
        self._crs = value

    def set_cf_grid_mapping(self, grid_mapping_var, errcheck=False):
        """Set CRS information based on CF standard 'grid_mapping' variable.

        See :meth:`pyproj.crs.CRS.from_cf` for details. Argument can be
        DataArray or Variable object for the grid mapping variable or a
        dictionary of CF standard grid mapping attributes.

        """
        # XXX: Should this just be part of the CRS setter? kwargs can't be passed then
        if not isinstance(grid_mapping_var, dict):
            grid_mapping_var = grid_mapping_var.attrs
        self._crs = CRS.from_cf(grid_mapping_var, errcheck=errcheck)

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
