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
from typing import Any, Literal

import xarray as xr
from pyproj import CRS
from pyproj.exceptions import CRSError

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


DEFAULT_GRID_MAPPING_VARIABLE_NAME = "spatial_ref"


class _SharedGeoAccessor:
    """Accessor functionality shared between Dataset and DataArray objects."""

    def __init__(self, xarray_obj):
        """Set handle for xarray object."""
        self._obj = xarray_obj
        self._crs: CRS | Literal[False] | None = None
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
        x: str | None = None,
        y: str | None = None,
        vertical: str | None = None,
        time: str | None = None,
        inplace: bool = False,
    ):
        """Tell geoxarray the names of the provided dimensions in this Dataset.

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

    def _set_crs(self, crs=None, variables=None):
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
        var_dict = self._set_crs(crs=crs, variables=variables)
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
            self._crs = applied_crs.pop()
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
        super().__init__(data_arr_obj)

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
        """Set preferred dimension names inside the Geoxarray accessor.

        Geoxarray will use this information for future operations.
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

        See Also
        --------
        GeoDataArrayAccessor.dims : Show the current dimensions as Geoxarray knows them
        GeoDataArrayAccessor.write_dims : Rename dimensions to match Geoxarray preferred dimension names

        """
        obj = self._get_obj(inplace)
        self._set_x_dim(obj, x)
        self._set_y_dim(obj, y)
        self._set_2d_dims(obj)
        self._set_vertical_dims(obj, vertical)
        self._set_temporal_dims(obj, time)
        obj.geo._dim_map = None
        return obj

    def _set_x_dim(self, obj, x):
        dims = obj.dims
        if x is None and self._x_dim is None:
            if "x" in dims:
                obj.geo._x_dim = "x"
        elif x is not None:
            assert x in dims
            obj.geo._x_dim = x

    def _set_y_dim(self, obj, y):
        dims = obj.dims
        if y is None and self._y_dim is None:
            if "y" in dims:
                obj.geo._y_dim = "y"
        elif y is not None:
            assert y in dims
            obj.geo._y_dim = y

    def _set_2d_dims(self, obj):
        dims = obj.dims
        if len(dims) == 2 and self._x_dim is None and self._y_dim is None:
            obj.geo._y_dim = dims[0]
            obj.geo._x_dim = dims[1]

    def _set_vertical_dims(self, obj, vertical):
        dims = obj.dims
        if vertical is None and self._vertical_dim is None:
            for z_dim in ("z", "vertical", "pressure_level"):
                if z_dim in dims:
                    obj.geo._vertical_dim = z_dim
                    break
        elif vertical is not None:
            assert vertical in dims
            obj.geo._vertical_dim = vertical

    def _set_temporal_dims(self, obj, time):
        dims = obj.dims
        if time is None and self._time_dim is None:
            for t_dim in ("time", "t"):
                if t_dim in dims:
                    obj.geo._time_dim = t_dim
                    break
        elif time is not None:
            assert time in dims
            obj.geo._time_dim = time

    @property
    def crs(self):
        if self._crs is False:
            # we've tried to find the CRS, there isn't one
            return None
        elif self._crs is not None:
            # we've already determined what the CRS is, return it
            return self._crs

        crs_methods = (
            self._get_crs_from_grid_mapping,
            self._get_crs_from_pyresample,
        )
        for crs_method in crs_methods:
            crs = crs_method()
            if crs is not None:
                self._crs = crs
                break
        else:
            self._crs = False
            return None
        return self._crs

    def _get_crs_from_grid_mapping(self):
        gm_var = self._get_gm_var()
        if gm_var is None:
            return None
        for crs_attr in ("spatial_ref", "crs_wkt"):
            try:
                crs_info = gm_var.attrs[crs_attr]
            except KeyError:
                continue
            crs = CRS.from_wkt(crs_info)
            return crs
        else:
            return self._get_crs_from_cf()

    def _get_gm_var(self):
        gm_var_name = self.grid_mapping
        if gm_var_name not in self._obj.coords:
            warnings.warn(
                "'grid_mapping' attribute found, but the variable it refers to "
                f"{gm_var_name} is not a coordinate variable. "
                "Use 'data_arr.geo.set_cf_grid_mapping' to "
                "provide one. Will search other metadata for CRS information.",
                stacklevel=2,
            )
            return None
        return self._obj.coords[gm_var_name]

    def _get_crs_from_cf(self):
        try:
            return CRS.from_cf(self._obj.coords[self.grid_mapping].attrs)
        except (KeyError, CRSError):
            return None

    def _get_crs_from_pyresample(self):
        if has_pyresample is None:
            return None
        area = self._obj.attrs.get("area")
        if area is None:
            return None
        if isinstance(area, AreaDefinition):
            return area.crs
        if isinstance(area, SwathDefinition):
            # TODO: Set whether or not things are gridded?
            return area.crs
        return None

    def set_crs(self, value: Any):
        """Force the CRS for this object.

        Set to `None` for the CRS to be recalculated.

        """
        crs = CRS.from_user_input(value)
        # TODO: Add inplace
        self._crs = crs

    @property
    def grid_mapping(self) -> str:
        """Name of a grid mapping variable associated with this DataArray.

        If not found, defaults to "spatial_ref".

        """
        gm_var_name = self._obj.encoding.get("grid_mapping") or self._obj.attrs.get("grid_mapping")
        if gm_var_name is not None:
            return gm_var_name
        # TODO: Support other grid mapping variable names
        return DEFAULT_GRID_MAPPING_VARIABLE_NAME

    def set_cf_grid_mapping(self, grid_mapping_var, errcheck=False):
        """Set CRS information based on CF standard 'grid_mapping' variable.

        See :meth:`pyproj.crs.CRS.from_cf` for details. Argument can be
        DataArray or Variable object for the grid mapping variable or a
        dictionary of CF standard grid mapping attributes.

        """
        # XXX: Should this just be part of the CRS setter? kwargs can't be passed then
        if not isinstance(grid_mapping_var, dict):
            grid_mapping_var = grid_mapping_var.attrs
        # XXX: Should we set something in the coords or attrs when this is applied?
        # TODO: Replace with `write_grid_mapping`?
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
