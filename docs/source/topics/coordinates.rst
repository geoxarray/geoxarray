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

Ground Control Points
---------------------

An alternative to the 1D or 2D spatial coordinates is the idea of storing a
specific subset of the geolocation coordinates and then interpolating or
extrapolating to get the coordinates for all other points. If possible, when
uniformly-spaced/gridded data is involved, 1D coordinates should be preferred
when using geoxarray as they allow for indexing on those coordinates.
Using GCPs has the
benefit of not storing two large 2D arrays for each element and with good
interpolation can get very accurate results with a much smaller storage
requirement. However, it also comes with a few important downsides:

1. The preferred interpolation method must be known to get the most accurate
   2D coordinate arrays back.
2. Standard ways of storing tiepoint arrays are not widely used (yet). The
   CF NetCDF convention 1.11 has
   `this information <https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#compression-by-coordinate-subsampling-tie-points-and-interpolation-subareas>`_
   about tiepoint and tiepoint interpolation. Geoxarray does not currently
   follow, use, or recognize this standard.
3. GCP to 2D array calculations take time and memory
