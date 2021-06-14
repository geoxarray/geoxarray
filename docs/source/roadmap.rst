Roadmap
=======

Where do we see geoxarray development going? Geoxarray is at a very early
stage in its development, but we still have some basic goals for its
near-term future.

Dimension and CRS handling
---------------------------

One of the original and most basic goals of geoxarray is to simplify the
handling of dimensions and Coordinate Reference System (CRS) information
for different datasets. While this work has been started, it is far from
over and far from easy. If your data follows any kind of standard scheme
for representing geospatial data, we want geoxarray to make it easy to
work with.

There are a few things that are fully fleshed out as far as how geoxarray
prefers this information to be stored in xarray objects, but it is being
worked on. For example, recent work in xarray with indexing data like the
work in
`pydata/xarray#5102 <https://github.com/pydata/xarray/pull/5102>`_ and
`pydata/xarray#5322 <https://github.com/pydata/xarray/pull/5322>`_ could
lead to improved storage of CRS information. You can see some additional
discussion on topics like this in
`pydata/xarray#3620 <https://github.com/pydata/xarray/issues/3620>`_.

Resampling Wrappers
-------------------

One of the common tasks when working with multiple geolocated datasets is the
need to put them on the same coordinate reference system (CRS) and the same
grid of pixels. This is where resampling comes in. Resampling typically
depends on knowing which dimensions are which and CRS information (see above).
There are many different ways of doing resampling and many different algorithms
available to python users (GDAL/rasterio/rioxarray, pyresample, etc).
Geoxarray's hope is that accessing these various algorithms won't require a ton
of pre-configuration or tons of knowledge to just get what you want. We want you
to focus on your science, not what needs to be done to get your data to work
together.

And beyond...
-------------

* To and From NetCDF files easily
* Anything else? Let us know at https://github.com/geoxarray/geoxarray/issues