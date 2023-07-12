Dimensions
==========

To do some of the things that Geoxarray needs to do, it needs to know what
certain dimensions mean. These dimensions are the temporal ``time``
dimension and these spatial dimensions:

* ``x``: The dimension along the x-axis. For data on a geographic coordinate
  reference system (CRS) this will be in the units of the projection space;
  typically meters or degrees. As an example, in a longitude/latitude CRS this
  would likely be the longitude dimension in degrees east.
* ``y``: The other 2D dimension to the ``x`` dimension in a geographic
  projection space. In a longitude/latitude CRS this would likely be the
  latitude dimension in degrees north.
* ``vertical``: The elevation, altitude, or vertical dimension. This is
  typically perpendicular to the surface of the Earth in some sense. This may
  be a distance in units like meters or a pressure like atmospheric pressure in
  hPa.

In well structured or common data schemes, Geoxarray can probably guess what
these dimensions are by their name or the shape of the array being looked at
(ex. a 2D array probably has (y, x) dimensions). Geoxarray will internally
rename these dimensions and this can be verified by accessing the dimensions
through the Geoxarray accessor.

.. code-block:: python

    my_data_arr.geo.dims

If the dimensions haven't been renamed then Geoxarray needs to be explicitly
told. Geoxarray makes it possible to :doc:`../howtos/set_dims` with the
:meth:`~geoxarray.accessor.GeoDataArrayAccessor.set_dims` accessor method.
