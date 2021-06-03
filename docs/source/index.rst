Geoxarray
=========

Geoxarray is an open source Python library providing simple utilities and
wrappers around common geospatial data workflows. These tools are
primarily accessed through an "xarray accessor" available on
xarray Dataset and DataArray objects from the ``.geo`` property.
Geoxarray provides tools for standardizing dimension names, storage of
coordinate reference system information, and operations like resampling
and plotting.

.. warning::

    Geoxarray is currently in a pre-alpha state and may not do most of what
    you'd expect a library with the above description to do.

.. warning::

    Geoxarray has not had a release yet. Instructions referencing installing
    from PyPI or conda-forge are there as placeholders and will not run
    properly until there is a release.

Geoxarray directly uses, borrows from, or is based on the ideas of other open
source projects including:

* `rioxarray <https://corteva.github.io/rioxarray/stable/>`_
* `rasterio <https://rasterio.readthedocs.io/en/latest/>`_
* `satpy <https://satpy.readthedocs.io/en/stable/>`_
* `pyresample <https://pyresample.readthedocs.io/en/latest/>`_
* `xgcm <https://xgcm.readthedocs.io/en/latest/>`_
* `xesmf <https://xesmf.readthedocs.io/en/latest/>`_
* `The Pangeo Community <https://pangeo.io/>`_


GitHub: https://github.com/geoxarray/geoxarray

`Release Notes <https://github.com/geoxarray/geoxarray/blob/main/CHANGELOG.md>`_

.. toctree::
   :maxdepth: 1

   installation
   usage
   contributing
   faq
   API <api/modules>