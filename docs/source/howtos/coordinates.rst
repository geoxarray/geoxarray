Add spatial coordinates
=======================

Geoxarray can extract the information from a ``DataArray`` to generate
:doc:`spatial coordinates <../topics/coordinates>`. These spatial
coordinates will be stored in ``.coords`` of the ``DataArray`` and can
be used for labeled indexing. Spatial coordinates are only ever added
for :doc:`dimensions <../topics/dimensions>` that geoxarray understands.
See :doc:`set_dims` for ways to work with non-standard dimension names.

To get a copy of your ``DataArray`` with spatial coordinates assigned
call the ``.geo.write_spatial_coords()`` method:

.. testcode::

   import xarray as xr
   import numpy as np
   import geoxarray

   my_data_arr = xr.DataArray(
       np.zeros((20, 10)),
       dims=("y", "x"),
       attrs={
           "ModelPixelScale": [1002.008644, 1002.008644, 0.0],
           "ModelTiepoint": [0.0, 0.0, 0.0, -5434894.885056, 5434894.885056, 0.0],
       },
   )
   new_data_arr = my_data_arr.geo.write_spatial_coords()
   print(new_data_arr)

Which will make the DataArray look like:

.. testoutput::

   <xarray.DataArray (y: 20, x: 10)> Size: 2kB
   ...
   Coordinates:
     * y        (y) float64 160B 5.434e+06 5.433e+06 ... 5.416e+06 5.415e+06
     * x        (x) float64 80B -5.434e+06 -5.433e+06 ... -5.426e+06 -5.425e+06
   Attributes:
       ModelPixelScale:  [1002.008644, 1002.008644, 0.0]
       ModelTiepoint:    [0.0, 0.0, 0.0, -5434894.885056, 5434894.885056, 0.0]

See the :meth:`~geoxarray.accessor.GeoDataArrayAccessor.write_spatial_coords`
API documentation for more information on supported and expected metadata
structure for this operation.