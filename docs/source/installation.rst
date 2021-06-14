Installation
============

Geoxarray is available from either PyPI or conda-forge.

With conda
----------

To install the conda-forge package into an existing conda environment that
is also already activated (with ``conda activate <env>``):

.. code-block:: bash

    conda install -c conda-forge geoxarray

Create a separate environment (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We recommend when you are first learning how to use Geoxarray that you create
a separate sub-environment specifically for geoxarray. To do this with conda
run:

.. code-block:: bash

    conda create -c conda-forge -n geoxarray_env python geoxarray
    conda activate geoxarray_env

With pip
--------

For ``pip`` based environments you can install Geoxarray by running:

.. code-block:: bash

    pip install geoxarray

Create a separate environment (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We recommend when you are first learning how to use Geoxarray that you create
a virtualenv specifically for geoxarray. This isn't strictly necessary, but
it may save you from accidentally breaking your Python environments for other
projects. Assuming you have ``virtualenvwrapper`` installed, you can create a
new environment and install geoxarray in it by doing:

.. code-block:: bash

    mkvirtualenv geoxarray
    pip install geoxarray

From source
-----------

Geoxarray can be installed from source into a pip-based or conda-based
installation. In a conda environment it can be nice to install geoxarray's
dependencies from conda without installing geoxarray.
To do this run:

.. code-block:: bash

    conda install -c conda-forge --only-deps geoxarray

To install Geoxarray from the source directory (the one with `setup.py` in it)
in either a pip-based or conda-based environment run:

.. code-block:: bash

    pip install -e .

Alternatively, if you don't wish to modify any of the Geoxarray code you can
install a "read-only" version directly from GitHub in either a conda or pip
environment:

.. code-block:: bash

    pip install git+https://github.com/geoxarray/geoxarray.git@main

See the :ref:`Contributor's Guide <dev_install>` for more information on
installing Geoxarray from source and contributing changes to the project.