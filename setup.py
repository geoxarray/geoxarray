"""Setuptools configuration file."""

from os import path

from setuptools import find_packages, setup

try:
    # HACK: https://github.com/pypa/setuptools_scm/issues/190#issuecomment-351181286
    # Stop setuptools_scm from including all repository files
    import setuptools_scm.integration

    setuptools_scm.integration.find_files = lambda _: []
except ImportError:
    pass

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open(path.join(here, "requirements.txt")) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines() if not line.startswith("#")]

extras_require = {
    "pyresample": ["pyresample"],
    "docs": ["sphinx_rtd_theme", "numpydoc", "sphinx_copybutton", "sphinxcontrib-apidoc", "pyresample"],
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
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
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
