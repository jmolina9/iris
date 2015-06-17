# (C) British Crown Copyright 2014 - 2015, Met Office
#
# This file is part of Iris.
#
# Iris is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Iris is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Iris.  If not, see <http://www.gnu.org/licenses/>.
"""
Common tools to support the loading and convertion of GRIB1 and GRIB2
messages into cube metadata.

"""

from __future__ import (absolute_import, division, print_function)

from collections import namedtuple


ScanningMode = namedtuple('ScanningMode', ['i_negative',
                                           'j_positive',
                                           'j_consecutive',
                                           'i_alternative'])

ProjectionCentre = namedtuple('ProjectionCentre',
                              ['south_pole_on_projection_plane',
                               'bipolar_and_symmetric'])
                                           
# Reference Common Code Table C-1.
_CENTRES = {
    'ecmf': 'European Centre for Medium Range Weather Forecasts'
}



def projection_centre(projectionCentreFlag):
    """
    Translate the projection centre flag bitmask.

    Reference GRIB2 Flag Table 3.5.

    Args:

    * projectionCentreFlag
        Message section 3, coded key value.

    Returns:
        A :class:`collections.namedtuple` representation.

    """
    south_pole_on_projection_plane = bool(projectionCentreFlag & 0x80)
    bipolar_and_symmetric = bool(projectionCentreFlag & 0x40)
    return ProjectionCentre(south_pole_on_projection_plane,
                            bipolar_and_symmetric)
                            

def scanning_mode(scanningMode):
    """
    Translate the scanning mode bitmask.

    Reference GRIB2 Flag Table 3.4.

    Args:

    * scanningMode:
        Message section 3, coded key value.

    Returns:
        A :class:`collections.namedtuple` representation.

    """
    i_negative = bool(scanningMode & 0x80)
    j_positive = bool(scanningMode & 0x40)
    j_consecutive = bool(scanningMode & 0x20)
    i_alternative = bool(scanningMode & 0x10)

    if i_alternative:
        msg = 'Grid definition section 3 contains unsupported ' \
            'alternative row scanning mode'
        raise TranslationError(msg)

    return ScanningMode(i_negative, j_positive,
                        j_consecutive, i_alternative)


