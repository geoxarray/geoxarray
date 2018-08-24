#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""Coordinate Reference System (CRS) classes and tools.

The internal CRS representation of geoxarray attempts to follow the
CF conventions for parameter naming. More information on the CF conventions
can be found on their `website <http://cfconventions.org/>`_ and the possible
combinations of parameters for specific projections can be found on
`this page <http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/apf.html>`_.
The other common CRS representation used as an intermediate form in certain
cases is the PROJ.4 string or dictionary.

Currently `geoxarray` follows CF Conventions Version 1.7. Any differences
between geoxarray's parameter naming and the CF conventions should be noted
below. Any differences not in the table below are considered bugs and should
be filed on github.

geoxarray -vs- CF Conventions
-----------------------------

None currently

"""

import logging
from ._proj4 import proj4_to_geoxarray, geoxarray_to_proj4, proj4_dict_to_str

try:
    from rasterio.crs import CRS as RIOCRS
except ImportError:
    CRS = None

try:
    from ._cartopy import from_proj as cartopy_from_proj
except ImportError:
    cartopy_from_proj = None

LOG = logging.getLogger(__name__)

# XXX: Best way to include descriptions of parameters
# parameter -> description (?)
CRS_PARAMETERS = {

}


class CRS(dict):
    """Basic Coordinate Reference System (CRS) description container.

    Typical usage of this object is as a container and as a converter
    between the different ways to describe a CRS.

    Examples
    --------

    TODO

    """

    def __init__(self, *args, **kwargs):
        """Create a CRS object from CF standard parameters.

        For possible parameters see the :mod:`geoxarray.crs`.

        """
        self._proj = None
        self._proj4_str = None
        self._proj4_dict = None
        self._cartopy_crs = None
        self._rasterio_crs = None
        super(CRS).__init__(*args, **kwargs)

    @property
    def proj4_dict(self):
        if self._proj4_dict is None:
            self._proj4_dict = geoxarray_to_proj4(**self)
        return self._proj4_dict

    @property
    def proj4_str(self):
        if self._proj4_str is None:
            pd = self.proj4_dict
            self._proj4_str = proj4_dict_to_str(pd, sort=True)
        return self._proj4_str

    @property
    def cartopy_crs(self):
        if self._cartopy_crs is None:
            if cartopy_from_proj is None:
                raise ImportError("'cartopy' must be installed")
            self._cartopy_crs = cartopy_from_proj(self.proj4_dict)
        return self._cartopy_crs

    @property
    def rasterio_crs(self):
        if self._rasterio_crs is None:
            if RIOCRS is None:
                raise ImportError("'rasterio' must be installed")
            self._rasterio_crs = RIOCRS(**self)
        return self._rasterio_crs
