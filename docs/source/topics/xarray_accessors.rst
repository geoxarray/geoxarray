Xarray Accessors
================

Geoxarray's primary interface is through an xarray accessor with the name
``.geo``. The
`xarray accessor design <https://docs.xarray.dev/en/stable/internals/extending-xarray.html>`_
is the suggested way to extend xarray functionality. This accessor gives you
access to geoxarray's functionality on any xarray object
(``DataArray`` or ``Dataset``) by calling methods or properties of it. For
example, ``my_data_array.geo.crs`` to get the Coordinate Reference System
information for ``my_data_array``. Due to this, geoxarray differs from a more
traditional software library where you would call functions or create objects
directly from the library.
