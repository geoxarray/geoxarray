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
from typing import Any, Literal, TypeVar

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
XarrayObject = TypeVar("XarrayObject", xr.DataArray, xr.Dataset)


class _SharedGeoAccessor:
    """Accessor functionality shared between Dataset and DataArray objects."""

    def __init__(self, xarray_obj: XarrayObject) -> None:
        """Set handle for xarray object."""
        self._obj = xarray_obj
        self._crs: CRS | Literal[False] | None = None
        self._x_dim = None
        self._y_dim = None
        self._vertical_dim = None
        self._time_dim = None
        self._dim_map = False

    def _get_obj(self, inplace: bool) -> XarrayObject:
        """Get the object to modify.

        Parameters
        ----------
        inplace
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

    def set_dims(self, *args, **kwargs) -> None:
        """Tell geoxarray the names of the provided dimensions in this Xarray object."""
        raise NotImplementedError()

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

    def write_dims(self) -> XarrayObject:
        """Rename object's dimensions to match geoxarray's preferred dimension names.

        This is a simple wrapper around Xarray's :meth:`xarray.DataArray.rename`
        or :meth:`xarray.Dataset.rename` methods along with ``.geo.dim_map`` to
        rename the dimension names. These methods always produce copies of the
        original object. It is not possible to do this operation "inplace".

        """
        obj_copy = self._get_obj(inplace=False)
        return obj_copy.rename(self.dim_map)

    @property
    def crs(self) -> None | CRS:
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
        if gm_var_name is None:
            return None
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
            return CRS.from_cf(self._obj.coords[self.grid_mapping or DEFAULT_GRID_MAPPING_VARIABLE_NAME].attrs)
        except (KeyError, CRSError):
            return None

    def _get_crs_from_pyresample(self):
        area = self._obj.attrs.get("area")
        if area is None:
            return None
        if hasattr(area, "crs"):
            return area.crs
        return None

    def write_crs(
        self, new_crs_info: Any | None = None, grid_mapping_name: str | None = None, inplace: bool = False
    ) -> XarrayObject:
        """Write the CRS to the xarray object in a CF compliant manner.

        .. note::

            Much of this code is copied from the rioxarray project and is under the Apache 2.0 license.
            A copy of this license is available in the source file ``LICENSE_rioxarray``.

        Parameters
        ----------
        new_crs_info:
            Coordinate Reference System (CRS) information to write to the
            Xarray object. Can be a :class:`pyproj.CRS` object or anything
            understood by the :meth:`pyproj.CRS.from_user_input` method.
            If not provided, the ``.crs`` property will be used.
            If ``.crs`` returns ``None`` a ``RuntimeError`` is raised.
        grid_mapping_name:
            Name to use for the coordinate variable created and written by this
            method. The coordinate variable, also known as the grid mapping
            variable, will have this name when written to a NetCDF file.
            Defaults to "spatial_ref".
        inplace:
            Whether to modify the current Xarray object inplace or to create
            a copy first. Default (``False``) is to make a copy.

        """
        obj = self._get_obj(inplace)
        crs = self._optional_crs_from_input(new_crs_info, obj)
        grid_mapping_var_name = self.grid_mapping if grid_mapping_name is None else grid_mapping_name
        if grid_mapping_var_name is None:
            grid_mapping_var_name = DEFAULT_GRID_MAPPING_VARIABLE_NAME

        gm_attrs = crs.to_cf()
        crs_wkt = crs.to_wkt()
        gm_attrs["crs_wkt"] = crs_wkt  # CF compatibility
        gm_attrs["spatial_ref"] = crs_wkt  # GDAL support

        obj.coords[grid_mapping_var_name] = xr.Variable((), 0)
        obj.coords[grid_mapping_var_name].attrs.update(gm_attrs)
        _assign_grid_mapping(obj, grid_mapping_var_name)
        return obj

    def _optional_crs_from_input(self, new_crs_info: Any | None, obj: XarrayObject) -> CRS:
        if new_crs_info is None:
            crs = self.crs
            if crs is None:
                raise RuntimeError("No CRS information provided or found.")
        else:
            crs = CRS.from_user_input(new_crs_info)
            obj.geo._crs = crs
        return crs

    @property
    def grid_mapping(self) -> str | None:
        """Name of a grid mapping variable associated with this DataArray.

        .. note::

            Much of this code is copied from the rioxarray project and is under the Apache 2.0 license.
            A copy of this license is available in the source file ``LICENSE_rioxarray``.

        Returns
        -------
        Grid mapping variable name defined in the xarray object. If not found,
        None is returned.

        """
        gm_var_name = self._obj.encoding.get("grid_mapping") or self._obj.attrs.get("grid_mapping")
        if gm_var_name is not None:
            return gm_var_name
        if hasattr(self._obj, "data_vars"):
            var_grid_mappings = set(self._all_grid_mapping_names())
            if len(var_grid_mappings) > 1:
                raise RuntimeError("Multiple grid mapping variables exist.")
            if len(var_grid_mappings) == 1:
                return var_grid_mappings.pop()
        return None

    def _all_grid_mapping_names(self):
        for var_name in self._obj.data_vars:
            var_grid_mapping = _get_encoding_or_attr(self._obj[var_name], "grid_mapping")
            if var_grid_mapping is None:
                continue
            yield var_grid_mapping


def _get_encoding_or_attr(xr_obj: xr.Dataset | xr.DataArray, attr_name: str) -> Any:
    return xr_obj.encoding.get(attr_name, xr_obj.attrs.get(attr_name))


def _assign_grid_mapping(xr_obj: xr.DataArray | xr.Dataset, grid_mapping_var_name: str) -> None:
    xr_obj.attrs.pop("grid_mapping", None)
    xr_obj.encoding["grid_mapping"] = grid_mapping_var_name

    if hasattr(xr_obj, "data_vars"):
        for var_name in xr_obj.data_vars:
            data_arr = xr_obj[var_name]
            dims = data_arr.geo.dims
            if not dims or all(dim_name not in dims for dim_name in ("x", "y", "z")):
                # no spatial dimensions
                continue
            _assign_grid_mapping(data_arr, grid_mapping_var_name)


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
        x:
            Name of the X dimension. This dimension usually exists with
            a corresponding coordinate variable in meters for
            gridded/projected data.
        y:
            Name of the Y dimension. Similar to the X dimension but on the Y
            axis.
        vertical:
            Name of the vertical or Z dimension. This dimension usually exists
            with a corresponding coordinate variable in meters for altitude
            or pressure level (ex. hPa, millibar, etc).
        time:
            Name of the time dimension. This dimension usually exists with a
            corresponding coordinate variable with time objects.
        inplace:
            If True, changes are made to the current xarray object. Otherwise,
            a copy of the object is made first. Default is False.

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
        for data_arr in obj_copy.data_vars.values():
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


@xr.register_dataarray_accessor("geo")
class GeoDataArrayAccessor(_SharedGeoAccessor):
    """Provide DataArray geolocation helper functions from a `.geo` accessor."""

    def __init__(self, data_arr_obj: xr.DataArray) -> None:
        """Initialize a 'best guess' dimension mapping to preferred dimension names."""
        self._is_gridded: bool | None = None
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

    def set_dims(
        self,
        x: None | str = None,
        y: None | str = None,
        vertical: None | str = None,
        time: None | str = None,
        inplace: bool = True,
    ) -> xr.DataArray:
        """Set preferred dimension names inside the Geoxarray accessor.

        Geoxarray will use this information for future operations.
        If any of the dimensions are not provided they will be found
        by best guess.

        This information does not rename or modify the data of the Xarray
        object itself. To easily rename the dimensions in a Geoxarray-friendly
        manner, follow a call of this method with :meth:`write_dims`.

        Parameters
        ----------
        x:
            Name of the X dimension. This dimension usually exists with
            a corresponding coordinate variable in meters for
            gridded/projected data.
        y:
            Name of the Y dimension. Similar to the X dimension but on the Y
            axis.
        vertical:
            Name of the vertical or Z dimension. This dimension usually exists
            with a corresponding coordinate variable in meters for altitude
            or pressure level (ex. hPa, millibar, etc).
        time:
            Name of the time dimension. This dimension usually exists with a
            corresponding coordinate variable with time objects.
        inplace:
            If True, changes are made to the current xarray object. Otherwise,
            a copy of the object is made first. Default is False.

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
