Write CRS information
=====================

Geoxarray can rewrite CRS information into a CF compatible manner. It can use
either the CRS information discovered from ``.geo.crs`` (see the :doc:`access_crs`
how to for more information on supported formats) or provided by a user.

If we start with an xarray DataArray with no CRS information in it (at least
that geoxarray is unfamiliar with) that looks like this:

.. testsetup::

   import xarray as xr
   import numpy as np
   data_arr = xr.DataArray(np.zeros((20, 10)),
                           dims=("y", "x"))

.. testcode::

   print(data_arr)

.. testoutput::

   <xarray.DataArray (y: 20, x: 10)>
   ...
   Dimensions without coordinates: y, x

We can explicitly add the CRS information use the
:meth:`~geoxarray.accessor._SharedGeoAccessor.write_crs` method.

.. testcode::

   new_data_arr = data_arr.geo.write_crs("EPSG:4326", inplace=False)
   print(new_data_arr)

.. testoutput::

   <xarray.DataArray (y: 20, x: 10)>
   ...
   Coordinates:
       spatial_ref  int64 0
   Dimensions without coordinates: y, x

The new ``DataArray`` now has a ``spatial_ref`` coordinate variable that
contains NetCDF/CF compatible grid mapping information. There is also a
``grid_mapping`` attribute (stored in ``.encoding``) that will be written
to a NetCDF file if we were to wrap the DataArray in a :class:`xarray.Dataset`
object and called :meth:`xarray.Dataset.to_netcdf`.

.. testcode::

   print(new_data_arr.encoding["grid_mapping"])
   print(new_data_arr.coords["spatial_ref"])

.. testoutput::

   spatial_ref
   <xarray.DataArray 'spatial_ref' ()>
   array(0)
   Coordinates:
       spatial_ref  int64 0
   Attributes:
       crs_wkt:                      GEOGCRS["WGS 84",ENSEMBLE["World Geodetic S...
       semi_major_axis:              6378137.0
       semi_minor_axis:              6356752.314245179
       inverse_flattening:           298.257223563
       reference_ellipsoid_name:     WGS 84
       longitude_of_prime_meridian:  0.0
       prime_meridian_name:          Greenwich
       geographic_crs_name:          WGS 84
       horizontal_datum_name:        World Geodetic System 1984 ensemble
       grid_mapping_name:            latitude_longitude
       spatial_ref:                  GEOGCRS["WGS 84",ENSEMBLE["World Geodetic S...

The ``spatial_ref`` attributes (``.attrs``) also include a ``crs_wkt``
attribute with a Well-Known Text (WKT) version of the CRS for better
CF-compatibility. The ``spatial_ref`` attribute is the same WKT and exists
for GDAL compatibility.

This same behavior and workflow can be achieved if starting from a
:class:`xarray.Dataset` class.
