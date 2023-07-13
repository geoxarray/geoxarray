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

Geoxarray Documentation
-----------------------

This documentation is separated into four primary groups: Topics, Tutorials,
How-Tos, and Reference material.

* **Topics** contain higher-level information about the concepts involved in
  geoxarray; why things work the way they do and how geoxarray approaches
  problems.
* :doc:`tutorials/index` will provide you a start to finish example of using
  geoxarray to accomplish something without assuming you know anything about
  geoxarray.
* :doc:`howtos/index` are used to walk through specific use cases, but also
  provide enough details so that the example can be used in other cases.
* **Reference material** provides the lowest level details of how specific
  pieces of geoxarray work. What classes and functions exist and every option
  they provide. References will also point you to other parts of the project
  like release and git information.

For more on how this documentation is structured, see
:ref:`this FAQ question <doc_organization>`.

.. toctree::
   :caption: Topics and Guides
   :maxdepth: 1
   :glob:

   installation
   topics/xarray_accessors
   topics/dimensions
   topics/projections
   faq

.. toctree::
   :caption: Code Examples
   :maxdepth: 2

   tutorials/index
   howtos/index

.. toctree::
   :caption: Reference
   :maxdepth: 1

   API <api/modules>
   contributing
   roadmap
   Release Notes <https://github.com/geoxarray/geoxarray/blob/main/CHANGELOG.md>
   GitHub Project <https://github.com/geoxarray/geoxarray>
   related
