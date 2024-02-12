Coordinates
===========

One of the core functionalities made available through Xarray is the ability
to add :term:`coordinate arrays <xarray:Coordinate>` to a DataArray or
Dataset. By defining coordinate arrays our DataArrays we essentially label
the dimensions like ticks on a plot axis. For more information on coordinate
functionality see the :term:`Xarray documentation <xarray:Coordinate>`.

The below sections go into the details of how geoxarray uses and defines
certain types of coordinate arrays.

Spatial Coordinates
-------------------

Geoxarray is able to create and use spatial coordinates for the
spatial :doc:`dimensions` of a ``DataArray``. This typically falls
into one of two different cases:

* 1-dimensional ``x`` and ``y`` coordinate arrays
* 2-dimensional coordinate arrays with the ``y`` dimension on the row/vertical
  axis and ``x`` on the column/horizontal dimension.

The 1-dimensional coordinates are reserved for uniformly-spaced "grids" of
data. Due to these arrays being uniformly spaced and 1-dimensional, it is
usually easy and efficient to index or slice along using these labels.

The 2-dimensional coordinate arrays case is typically for
non-uniformly-spaced data that requires a 2D longitude and 2D latitude array
to accurately define the location of every element of the data. This may also
arise if geolocation information was computed from a series of Ground Control
Points (GCPs).

At the time of writing it is not currently efficient to index based on
2-dimensional coordinate arrays. Due to their size it may also be helpful
to define 2D coordinate arrays as a dask array or other Xarray-compatible lazy
array.
