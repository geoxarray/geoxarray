============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/geoxarray/geoxarray/issues.

If you are reporting a bug, please include:

* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Geoxarray could always use more documentation, whether
as part of the official Geoxarray docs, in docstrings,
or even on the web in blog posts, articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/geoxarray/geoxarray/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

.. _dev_install:

Get Started!
------------

Ready to contribute? Here's how to set up `geoxarray` for local development.

1. Fork the `geoxarray` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/geoxarray.git

3. Install your local copy into a local environment. If you are using a conda
   environment you can create a sub-environment::

    $ conda create -c conda-forge -n geoxarray python xarray pyproj
    $ conda activate geoxarray
    $ conda install -c conda-forge --only-deps geoxarray
    $ pip install -e .

   Alternatively, if you are using virtualenv and assuming you have
   virtualenvwrapper installed::

    $ mkvirtualenv geoxarray
    $ cd geoxarray/
    $ pip install -e .

4. Install pre-commit git hooks so various style checks and formatters are
   automatically run when you make a commit::

    $ pip install pre-commit
    $ pre-commit install

5. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

6. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ pytest geoxarray/tests

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

   If any of the pre-commit hooks have modified your files then your commit
   may have failed. You'll need to re-add the changed files and reattempt your
   commit.

8. `Submit a pull request <https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_
   through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring.
3. The pull request should work for Python 3.6 and above.

