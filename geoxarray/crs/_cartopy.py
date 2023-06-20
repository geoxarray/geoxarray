#!/usr/bin/env python
# Copyright geoxarray Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for converting from PROJ.4 to Cartopy CRS.

This functionality is currently waiting to be merged to the Cartopy package.
Until the interface for this is finalized this implementation is used in
geoxarray. This code was originally written as part of the Cartopy
functionality and then copied to the `pyresample` package. It was all
originally written and copied by David Hoese (djhoese).

"""

from logging import getLogger

import numpy as np

try:
    from xarray import DataArray
except ImportError:
    DataArray = np.ndarray

import cartopy.crs as ccrs
import shapely.geometry as sgeom
from pyproj import CRS

try:
    from cartopy.crs import from_proj
except ImportError:
    from_proj = None

logger = getLogger(__name__)

_GLOBE_PARAMS = {
    "datum": "datum",
    "ellps": "ellipse",
    "a": "semimajor_axis",
    "b": "semiminor_axis",
    "f": "flattening",
    "rf": "inverse_flattening",
    "towgs84": "towgs84",
    "nadgrids": "nadgrids",
}


def _globe_from_proj4(proj4_terms):
    """Create a `Globe` object from PROJ.4 parameters."""
    globe_terms = filter(lambda term: term[0] in _GLOBE_PARAMS, proj4_terms.items())
    globe = ccrs.Globe(**{_GLOBE_PARAMS[name]: value for name, value in globe_terms})
    return globe


# copy of class in cartopy (before it was released)
class _PROJ4Projection(ccrs.Projection):
    def __init__(self, proj4_terms, globe=None, bounds=None):
        terms = CRS.from_user_input(proj4_terms).to_dict()
        globe = _globe_from_proj4(terms) if globe is None else globe

        other_terms = []
        for term in terms.items():
            if term[0] not in _GLOBE_PARAMS:
                other_terms.append(term)
        super().__init__(other_terms, globe)

        self.bounds = bounds

    def __repr__(self):
        return f"_PROJ4Projection({self.proj4_init})"

    @property
    def boundary(self):
        x0, x1, y0, y1 = self.bounds
        return sgeom.LineString([(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)])

    @property
    def x_limits(self):
        x0, x1, y0, y1 = self.bounds
        return (x0, x1)

    @property
    def y_limits(self):
        x0, x1, y0, y1 = self.bounds
        return (y0, y1)

    @property
    def threshold(self):
        x0, x1, y0, y1 = self.bounds
        return min(x1 - x0, y1 - y0) / 100.0


def _lesser_from_proj(proj4_terms, globe=None, bounds=None):
    """Not-as-good version of cartopy's 'from_proj' function.

    The user doesn't have a newer version of Cartopy so there is
    no `from_proj` function to use which does a fancier job of
    creating CRS objects from PROJ.4 strings than this does.

    """
    return _PROJ4Projection(proj4_terms, globe=globe, bounds=bounds)


if from_proj is None:
    from_proj = _lesser_from_proj
