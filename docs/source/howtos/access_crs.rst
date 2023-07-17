Access CRS information
======================

Geoxarray can understand a couple different standard ways of storing
Coordinate Reference System (CRS) information in an Xarray object.
To learn more about what a CRS is see the :doc:`../topics/projections`
documentation.

Below you'll find examples of the common CRS storage cases that geoxarray
supports. In all cases, the basic access geoxarray usage is the same. Please
follow the specific storage format section closest to your use case for
details on what geoxarray expects. The basic usage, assuming you have an
xarray DataArray or Dataset object, is to do:

.. code-block::

   import geoxarray

   the_crs = my_data_arr.geo.crs

To access geoxarray's ``.geo`` accessor (the property) we must first import
geoxarray to register it. Then accessing
:meth:`.geo.crs <geoxarray.accessor._SharedGeoAccessor.crs>` gives us a pyproj
:class:`~pyproj.crs.CRS` object or ``None`` if geoxarray is unable to determine
the CRS.

.. contents:: Supported CRS Formats
   :depth: 1
   :backlinks: none
   :local:

CF Grid Mapping
---------------

If loading a NetCDF file that has a CF-compatible "grid mapping" variable,
you can load the file in a geoxarray-friendly way by doing:

.. code-block:: python

    import xarray as xr
    ds = xr.open_dataset("/path/to/file.nc", decode_coords="all")

The ``decode_coords="all"`` is required for the grid mapping coordinates to
be loaded in a way that geoxarray can understand and access.

Single Grid Mapping
^^^^^^^^^^^^^^^^^^^

.. testsetup::

   import xarray as xr
   import numpy as np
   data_arr = xr.DataArray(np.zeros((20, 10)),
                           dims=("y", "x"),
                           coords={
                               "y": np.arange(20.0),
                               "x": np.arange(10.0),
   })
   gmap_var = xr.DataArray(0.0, attrs={
     'long_name': 'GOES-R ABI fixed grid projection',
     'grid_mapping_name': 'geostationary',
     'perspective_point_height': 35786023.0,
     'semi_major_axis': 6378137.0,
     'semi_minor_axis': 6356752.31414,
     'inverse_flattening': 298.2572221,
     'latitude_of_projection_origin': 0.0,
     'longitude_of_projection_origin': -75.0,
     'sweep_angle_axis': 'x'})
   data_arr.encoding["grid_mapping"] = "goes_imager_projection"
   data_arr.coords["goes_imager_projection"] = gmap_var
   ds = xr.Dataset({"Rad": data_arr})

Let's say the file we loaded above looks something like this:

.. testcode::

   print(ds)

.. testoutput::

   <xarray.Dataset>
   Dimensions:                 (y: 20, x: 10)
   Coordinates:
     * y                       (y) float64 0.0 1.0 2.0 3.0 ... 16.0 17.0 18.0 19.0
     * x                       (x) float64 0.0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0
       goes_imager_projection  float64 0.0
   Data variables:
       Rad                     (y, x) float64 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0

This Dataset has ``x`` and ``y`` dimensions and coordinate variables and a
single ``Rad`` data variable. There is one grid mapping variable with the
following metadata:

.. testcode::

   print(ds.coords["goes_imager_projection"].attrs)

.. testoutput::

   {'long_name': 'GOES-R ABI fixed grid projection', 'grid_mapping_name': 'geostationary', 'perspective_point_height': 35786023.0, 'semi_major_axis': 6378137.0, 'semi_minor_axis': 6356752.31414, 'inverse_flattening': 298.2572221, 'latitude_of_projection_origin': 0.0, 'longitude_of_projection_origin': -75.0, 'sweep_angle_axis': 'x'}

To get the CRS information for this ``Rad`` variable we can do:

.. testcode::

   import geoxarray

   print(repr(ds["Rad"].geo.crs))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   <Projected CRS: {"$schema": "https://proj.org/schemas/v0.2/projjso ...>
   Name: undefined
   Axis Info [cartesian]:
   - E[east]: Easting (metre)
   - N[north]: Northing (metre)
   Area of Use:
   - undefined
   Coordinate Operation:
   - name: unknown
   - method: Geostationary Satellite (Sweep X)
   Datum: undefined
   - Ellipsoid: undefined
   - Prime Meridian: Greenwich

Due to some differences between CF's standard grid mapping definitions and the
amount of details made available via pyproj/PROJ and the amount of missing
information in this example (but real-world) CRS, many of the fields in this
CRS are listed as "undefined" or "unknown". This CRS is still perfectly
valid and usable by geoxarray and pyproj.

**Details**

In the CF NetCDF case, geoxarray looks for a ``grid_mapping`` name in
``.encoding`` or ``.attrs`` and then looks for that variable in ``.coords``.
The CRS is then constructed from the metadata in that grid mapping variable's
``.attrs``. If the grid mapping variable's metadata (``.attrs``) includes a
Well-Known Text (WKT) version of the CRS (a ``crs_wkt`` or ``spatial_ref``
attribute) then the CRS will be derived from that.

Satpy and Pyresample
--------------------

The :doc:`Satpy <satpy:index>` library uses
:doc:`Pyresample <pyresample:index>` geometry objects to define the geographic
region of a dataset. The most common objects are
:class:`pyresample.geometry.AreaDefinition` and
:class:`pyresample.geometry.SwathDefinition` objects and are typically found in
a DataArray in ``.attrs["area"]``.

.. testsetup::

   import xarray as xr
   from pyresample import AreaDefinition
   area = AreaDefinition("", "", "", "EPSG:3070", 10, 20,
                         (282455.22, 223080.17, 828240.35, 766436.45))
   satpy_data_arr = xr.DataArray(np.zeros((20, 10)),
                           dims=("y", "x"), attrs={"area": area})

.. testcode::

   print(satpy_data_arr)

.. testoutput::
   :options: +SKIP

   <xarray.DataArray (y: 20, x: 10)>
   ...
   Dimensions without coordinates: y, x
   Attributes:
       area:     Area ID: \nDescription: \nProjection: {'datum': 'NAD83', 'k': '...

These objects have a ``.crs`` property and
is directly returned by geoxarray if the other formats of CRS information
(see above) are not found.

.. testcode::

   print(repr(satpy_data_arr.geo.crs))

.. testoutput::
   :options: +NORMALIZE_WHITESPACE

   <Projected CRS: EPSG:3070>
   Name: NAD83 / Wisconsin Transverse Mercator
   Axis Info [cartesian]:
   - X[east]: Easting (metre)
   - Y[north]: Northing (metre)
   Area of Use:
   - name: United States (USA) - Wisconsin.
   - bounds: (-92.89, 42.48, -86.25, 47.31)
   Coordinate Operation:
   - name: Wisconsin Transverse Mercator 83
   - method: Transverse Mercator
   Datum: North American Datum 1983
   - Ellipsoid: GRS 1980
   - Prime Meridian: Greenwich