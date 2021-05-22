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
"""Conversion tools between PROJ.4 and other formats.

This modules main purpose is to hold the logic required to convert
PROJ.4-based information to something more useful by geoxarray.
This module also includes PROJ.4 string to PROJ.4 dictionary conversion
functions.

"""

from pyproj import CRS
import logging

LOG = logging.getLogger(__name__)

# http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/apf.html
PROJ_TO_GX = {
    "a": "semi_major_axis",
    "b": "semi_minor_axis",
}


def proj4_str_to_dict(proj4_str):
    """Convert PROJ.4 compatible string definition to dict.

    Note: Key only parameters will be assigned a value of `True`.
    """
    return CRS(proj4_str).to_dict()


def proj4_dict_to_str(proj4_dict, sort=False):
    """Convert a dictionary of PROJ.4 parameters to a valid PROJ.4 string."""
    return CRS(proj4_dict).to_proj4()


def proj4_radius_parameters(proj4_dict):
    """Calculate 'a' and 'b' radius parameters.

    Arguments:
        proj4_dict (str or dict): PROJ.4 parameters

    Returns:
        a (float), b (float): equatorial and polar radius
    """
    crs = CRS(proj4_dict)
    return crs.semi_major_metre, crs.semi_minor_metre
