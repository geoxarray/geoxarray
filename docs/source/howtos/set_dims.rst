Specify spatial and temporal dimensions
=======================================

Assuming you have an Xarray object that has some atypical or unusual names
for its dimensions, we can tell geoxarray what these dimensions represent.
For more information on what dimensions geoxarray understands see the
:doc:`../topics/dimensions` documentation.

.. testsetup::

    import xarray as xr
    import numpy as np
    data_arr = xr.DataArray(np.zeros((5, 20, 10)),
                            dims=('dim_0', 'dim_1', 'dim_2'),
                            coords={
                                'dim_1': np.arange(20.0),
                                'dim_2': np.arange(10.0)})

.. testcode::

    print(data_arr)

We can see from this output that there are three dimensions in this DataArray:
``(dim_0, dim_1, dim_2)``.

.. testoutput::

    <xarray.DataArray (dim_0: 5, dim_1: 20, dim_2: 10)>
    ...
    Coordinates:
      * dim_1    (dim_1) float64 0.0 1.0 2.0 3.0 4.0 ... 15.0 16.0 17.0 18.0 19.0
      * dim_2    (dim_2) float64 0.0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0
    Dimensions without coordinates: dim_0

These don't fit geoxarray's usual preferred names for
:doc:`../topics/dimensions`, but we can see if geoxarray can guess their
purpose by using
:attr:`.geo.dims <geoxarray.accessor.GeoDataArrayAccessor.dims>`:

.. testcode::

    import geoxarray

    print(data_arr.geo.dims)

And note that the names of the dimensions haven't changed:

.. testoutput::

    ('dim_0', 'dim_1', 'dim_2')

We can tell geoxarray what these mean by using
:meth:`.geo.set_dims() <geoxarray.accessor.GeoDataArrayAccessor.set_dims>`:

.. testcode::

    data_arr.geo.set_dims(y="dim_1", x="dim_2")
    print(data_arr.geo.dims)

And notice that geoxarray now knows that the second and third dimension
correspond to the ``y`` and ``x`` spatial dimensions.

.. testoutput::

    ('dim_0', 'y', 'x')

From now on geoxarray should be able to make decisions based on these known
dimensions. Note that geoxarray hasn't changed anything about the DataArray
itself. We can rename the dimensions with geoxarray's preferred names by
doing:

.. testcode::

    new_data_arr = data_arr.geo.write_dims()
    print(new_data_arr)

.. testoutput::

    <xarray.DataArray (dim_0: 5, y: 20, x: 10)>
    ...
    Coordinates:
      * y        (y) float64 0.0 1.0 2.0 3.0 4.0 ... 15.0 16.0 17.0 18.0 19.0
      * x        (x) float64 0.0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0
    Dimensions without coordinates: dim_0
