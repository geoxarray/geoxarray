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

LOG = logging.getLogger(__name__)
