import sys
from os import path

from setuptools import find_packages, setup

try:
    # HACK: https://github.com/pypa/setuptools_scm/issues/190#issuecomment-351181286
    # Stop setuptools_scm from including all repository files
    import setuptools_scm.integration

    setuptools_scm.integration.find_files = lambda _: []
except ImportError:
    pass

# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for people with outdated setuptools
# and/or pip.
if sys.version_info < (3, 6):
    error = """
geoxarray does not support Python {0}.{1}.
Python 3.6 and above is required. Check your Python version like so:

python3 --version

This may be due to an out-of-date pip. Make sure you have pip >= 9.0.1.
Upgrade pip like so:

pip install --upgrade pip
""".format(
        3, 6
    )
    sys.exit(error)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open(path.join(here, "requirements.txt")) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [
        line
        for line in requirements_file.read().splitlines()
        if not line.startswith("#")
    ]

extras_require = {
    "pyresample": ["pyresample"],
}
all_extras = []
for extra_deps in extras_require.values():
    all_extras.extend(extra_deps)
extras_require["all"] = list(set(all_extras))

setup(
    name="geoxarray",
    description="Geolocation utilities for xarray objects",
    long_description=readme,
    author="geoxarray Developers",
    author_email="",
    url="https://github.com/geoxarray/geoxarray",
    packages=find_packages(exclude=["docs", "tests"]),
    include_package_data=True,
    python_requires=">=3.6",
    package_data={
        "geoxarray": [
            # When adding files here, remember to update MANIFEST.in as well,
            # or else they will not be included in the distribution on PyPI!
            # 'path/to/data_file',
        ]
    },
    install_requires=requirements,
    extras_require=extras_require,
    tests_require=["pytest", "dask", "pyresample"],
    use_scm_version={"write_to": "geoxarray/version.py"},
    setup_requires=["setuptools_scm", "setuptools_scm_git_archive"],
    license="Apache",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
)
