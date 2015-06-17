# (C) British Crown Copyright 2015, Met Office
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
Module to support the loading and convertion of a GRIB1 message into
cube metadata.

"""

ResolutionFlags = namedtuple('ResolutionFlags',
                             ['i_increments_given',
                              'j_increments_given',
                              'uv_resolved'])


def resolution_flags(resolutionAndComponentFlags):
    """
    Translate the resolution and component bitmask.

    Reference GRIB2 Flag Table 3.3.

    Args:

    * resolutionAndComponentFlags:
        Message section 3, coded key value.

    Returns:
        A :class:`collections.namedtuple` representation.

    """
    inc_given = bool(resolutionAndComponentFlags & 0x20)
    j_inc_given = bool(resolutionAndComponentFlags & 0x10)
    uv_resolved = bool(resolutionAndComponentFlags & 0x08)


def grid_type_regular_ll(section, metadata)
def grid_definition_template_0(section, metadata):
    # Earth assumed spherical with radius of 6 371 229.0m
    cs = icoord_systems.GeogCS(6371229)

    # Check for reduced grid.
    if section['PLPresent']:
        msg = ('Grid definition section 2 contains unsupported '
               'quasi-regular grid')
        raise TranslationError(msg)

    scan = scanning_mode(section['scanningMode'])

    # Calculate longitude points.
    x_inc = section['iDirectionIncrement'] * _GRID_ACCURACY_IN_DEGREES_GRIB1
    x_offset = section['longitudeOfFirstGridPoint'] * _GRID_ACCURACY_IN_DEGREES_GRIB1
    x_direction = -1 if scan.i_negative else 1
    Ni = section['Ni']
    x_points = np.arange(Ni, dtype=np.float64) * x_inc * x_direction + x_offset

    # Determine whether the x-points (in degrees) are circular.
    circular = _is_circular(x_points, 360.0)

    # Calculate latitude points.
    y_inc = section['jDirectionIncrement'] * _GRID_ACCURACY_IN_DEGREES_GRIB1
    y_offset = section['latitudeOfFirstGridPoint'] * _GRID_ACCURACY_IN_DEGREES_GRIB1
    y_direction = 1 if scan.j_positive else -1
    Nj = section['Nj']
    y_points = np.arange(Nj, dtype=np.float64) * y_inc * y_direction + y_offset

    # Create the lat/lon coordinates.
    y_coord = DimCoord(y_points, standard_name='latitude', units='degrees',
                       coord_system=cs)
    x_coord = DimCoord(x_points, standard_name='longitude', units='degrees',
                       coord_system=cs, circular=circular)

    # Determine the lat/lon dimensions.
    y_dim, x_dim = 0, 1
    if scan.j_consecutive:
        y_dim, x_dim = 1, 0

    # Add the lat/lon coordinates to the metadata dim coords.
    metadata['dim_coords_and_dims'].append((y_coord, y_dim))
    metadata['dim_coords_and_dims'].append((x_coord, x_dim))


def grib1_convert(field, metadata):
    
    # Section 1 - Product Definition Section (PDS)
    centre = _CENTRES.get(field.sections[1]['centre'])
    if centre is not None:
        metadata['attributes']['centre'] = centre

    # Section 2 - Grid Definition Section (GDS)
    grid_definition_section_grib1(field.sections[2], metadata)