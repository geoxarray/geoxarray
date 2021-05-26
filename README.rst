===============================
GeoXarray
===============================

.. image:: https://github.com/geoxarray/geoxarray/workflows/CI/badge.svg?branch=main
        :target: https://github.com/geoxarray/geoxarray/actions?query=workflow%3A%22CI%22

.. image:: https://img.shields.io/pypi/v/geoxarray.svg
        :target: https://pypi.python.org/pypi/geoxarray

.. image:: https://coveralls.io/repos/github/geoxarray/geoxarray/badge.svg?branch=main
    :target: https://coveralls.io/github/geoxarray/geoxarray?branch=main


* Free software: Apache 2
* Documentation: https://geoxarray.github.io/.

Geolocation utilities for xarray objects. GeoXarray is meant to bring
together all of the features and conversions needed by various python
packages working with geolocation xarray objects. This means being
able to convert between various coordinate system implementations
(rasterio, cartopy, pyresample, NetCDF CF grid mapping, etc). It also
means providing basic access to properties of the geolocation information
like bounding boxes.

Installation
------------

The ``geoxarray`` library will be available on PyPI and can be installed with
pip::

    pip install geoxarray

For the most recent development versions of geoxarray, it can be installed
directly from the root of the source directory::

    pip install -e .

In the future geoxarray will also be available on conda-forge.

Dependencies
------------

Besides the xarray dependency, the ``geoxarray`` uses CRS objects
from the `pyproj <https://pyproj4.github.io/pyproj/stable/>`_ library
Additionally, geoxarray has a lot of optional dependencies when it comes
to converting to other libraries' CRS or geolocation objects. These
libraries include, but may not be limited to:

- rasterio
- cartopy
- pyresample

Development Status
------------------

GeoXarray is actively being developed as a side project. Additions and
modifications are done as developers have time. If you would like to
contribute, suggest features, or discuss anything else please file a
bug on github.

Features
--------

* TODO
