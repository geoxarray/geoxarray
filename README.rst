===============================
Geoxarray
===============================

.. image:: https://github.com/geoxarray/geoxarray/workflows/CI/badge.svg?branch=main
        :target: https://github.com/geoxarray/geoxarray/actions?query=workflow%3A%22CI%22

.. image:: https://img.shields.io/pypi/v/geoxarray.svg
        :target: https://pypi.python.org/pypi/geoxarray

.. image:: https://badges.gitter.im/geoxarray/geoxarray.svg
    :target: https://gitter.im/geoxarray/geoxarray?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

.. image:: https://coveralls.io/repos/github/geoxarray/geoxarray/badge.svg?branch=main
    :target: https://coveralls.io/github/geoxarray/geoxarray?branch=main

.. image:: https://results.pre-commit.ci/badge/github/geoxarray/geoxarray/main.svg
   :target: https://results.pre-commit.ci/latest/github/geoxarray/geoxarray/main
   :alt: pre-commit.ci status


* Free software: Apache 2
* Documentation: https://geoxarray.github.io/.

Geolocation utilities for xarray objects. Geoxarray is meant to bring
together all of the features and conversions needed by various python
packages working with geolocation xarray objects. This means being
able to convert between various coordinate system implementations
(rasterio, cartopy, pyresample, NetCDF CF grid mapping, etc). It also
means providing basic access to properties of the geolocation information
like bounding boxes.

Installation
------------

The ``geoxarray`` library is available on PyPI and can be installed with
pip:

.. code-block:: bash

   pip install geoxarray

For the most recent development versions of geoxarray, it can be installed
directly from the root of the source directory:

.. code-block:: bash

   pip install -e .

Or to install into an existing conda-based environment::

.. code-block:: bash

   conda install -c conda-forge geoxarray

Dependencies
------------

Besides the xarray dependency, the ``geoxarray`` package uses CRS objects
from the `pyproj <https://pyproj4.github.io/pyproj/stable/>`_ library.
Additionally, geoxarray has a lot of optional dependencies when it comes
to converting to other libraries' CRS or geolocation objects. These
libraries include, but may not be limited to:

- rasterio
- cartopy
- pyresample

Relationship with rioxarray
---------------------------

At the time of writing, rioxarray is an independent project whose features
related to CRS and dimension handling are very similar if not exactly the
same as geoxarray. Rioxarray existed first and paved the way to show how CRS
information can be handled in an xarray-friendly way. Much of geoxarray is
inspired by rioxarray, if not copied directly. Portions of code copied from
rioxarray are noted in docstrings for that code and are under the Apache
License of rioxarray which has been copied as ``LICENSE_rioxarray`` in the
geoxarray package and repository.

Development Status
------------------

Geoxarray is actively being developed as a side project. Additions and
modifications are done as developers have time. If you would like to
contribute, suggest features, or discuss anything else please file a
bug on github.

Features
--------

See the documentation website for how-tos, concepts, and API documentation.

Parse various formats of storing Coordinate Reference System information:

.. code-block:: python

   import geoxarray

   pyproj_crs = my_data_arr.geo.crs

Write CRS information in a CF-compatible way or add CRS information
to an object that didn't have any:

.. code-block:: python

    import geoxarray

    new_dataset = my_dataset.geo.write_crs("EPSG:4326", inplace=False)
