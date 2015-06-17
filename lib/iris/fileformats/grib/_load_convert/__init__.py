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
Module to support the loading and convertion of a GRIB message into
cube metadata.

"""

from __future__ import (absolute_import, division, print_function)

from collections import OrderedDict

from iris.exceptions import TranslationError
from iris.fileformats.grib._load_convert._edition1 import grib1_convert
from iris.fileformats.grib._load_convert._edition2 import grib2_convert
from iris.fileformats.rules import ConversionMetadata


def convert(field):
    """
    Translate the GRIB message into the appropriate cube metadata.

    Args:

    * field:
        GRIB message to be translated. It can be a GRIB edition 1 or 2
        message.

    Returns:
        A :class:`iris.fileformats.rules.ConversionMetadata` object.

    """
    editionNumber = field.sections[0]['editionNumber']

    # Initialise the cube metadata.
    metadata = OrderedDict()
    metadata['factories'] = []
    metadata['references'] = []
    metadata['standard_name'] = None
    metadata['long_name'] = None
    metadata['units'] = None
    metadata['attributes'] = {}
    metadata['cell_methods'] = []
    metadata['dim_coords_and_dims'] = []
    metadata['aux_coords_and_dims'] = []

    # Convert GRIB2 message to cube metadata.
    if editionNumber == 1:
        grib1_convert(field, metadata)
    elif editionNumber == 2:
        grib2_convert(field, metadata)
    else:
        msg = 'GRIB edition {} is not supported'.format(editionNumber)
        raise TranslationError(msg)

    return ConversionMetadata._make(metadata.values())