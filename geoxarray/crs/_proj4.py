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

from pyproj import Proj, Geod
import logging

LOG = logging.getLogger(__name__)

# http://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/apf.html
PROJ_TO_GX = {
    'a': 'semi_major_axis',
    'b': 'semi_minor_axis',
}


def proj4_to_geoxarray(**kwargs):
    """Convert a PROJ.4 dict to a dict of geoxarray CRS parameters."""
    raise NotImplementedError()


def geoxarray_to_proj4(**kwargs):
    """Convert a dict of geoxarray CRS parameters to a PROJ.4 dict."""
    raise NotImplementedError()


def proj4_str_to_dict(proj4_str):
    """Convert PROJ.4 compatible string definition to dict

    Note: Key only parameters will be assigned a value of `True`.
    """
    pairs = (x.split('=', 1) for x in proj4_str.replace('+', '').split(" "))
    return dict((x[0], (x[1] if len(x) == 2 else True)) for x in pairs)


def proj4_dict_to_str(proj4_dict, sort=False):
    """Convert a dictionary of PROJ.4 parameters to a valid PROJ.4 string"""
    items = proj4_dict.items()
    if sort:
        items = sorted(items)
    params = []
    for key, val in items:
        key = str(key) if key.startswith('+') else '+' + str(key)
        if key in ['+no_defs', '+no_off', '+no_rot']:
            param = key
        else:
            param = '{}={}'.format(key, val)
        params.append(param)
    return ' '.join(params)


def proj4_radius_parameters(proj4_dict):
    """Calculate 'a' and 'b' radius parameters.

    Arguments:
        proj4_dict (str or dict): PROJ.4 parameters

    Returns:
        a (float), b (float): equatorial and polar radius
    """
    if isinstance(proj4_dict, str):
        new_info = proj4_str_to_dict(proj4_dict)
    else:
        new_info = proj4_dict.copy()

    # load information from PROJ.4 about the ellipsis if possible
    if 'ellps' in new_info:
        geod = Geod(**new_info)
        new_info['a'] = geod.a
        new_info['b'] = geod.b
    elif 'a' not in new_info or 'b' not in new_info:

        if 'rf' in new_info and 'f' not in new_info:
            new_info['f'] = 1. / float(new_info['rf'])

        if 'a' in new_info and 'f' in new_info:
            new_info['b'] = float(new_info['a']) * (1 - float(new_info['f']))
        elif 'b' in new_info and 'f' in new_info:
            new_info['a'] = float(new_info['b']) / (1 - float(new_info['f']))
        else:
            geod = Geod(**{'ellps': 'WGS84'})
            new_info['a'] = geod.a
            new_info['b'] = geod.b

    return float(new_info['a']), float(new_info['b'])
