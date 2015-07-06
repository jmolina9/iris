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
"""Test function :func:`iris.util.gaussian_latitudes_and_bounds`."""

from __future__ import (absolute_import, division, print_function)

# import iris tests first so that some things can be initialised before
# importing anything else
import iris.tests as tests

import numpy as np

from iris.util import gaussian_latitudes_and_bounds


class Test_gaussian_latitudes_and_bounds(tests.IrisTest):

    def test(self):
        n = 5
        expected_latitudes = np.array([-76.88245793, -59.88994169,
                                       -42.79752184, -25.68323419,
                                       -8.5616985, 8.5616985,
                                       25.68323419, 42.79752184,
                                       59.88994169, 76.88245793])
        expected_bounds = np.array([[-90., -68.95978371],
                                    [-68.95978371, -51.61696175],
                                    [-51.61696175, -34.38777535],
                                    [-34.38777535, -17.18897483],
                                    [-17.18897483, 0.],
                                    [0., 17.18897483],
                                    [17.18897483, 34.38777535],
                                    [34.38777535, 51.61696175],
                                    [51.61696175, 68.95978371],
                                    [68.95978371, 90.]])
        latitudes, bounds = gaussian_latitudes_and_bounds(n)
        self.assertArrayAlmostEqual(latitudes, expected_latitudes)
        self.assertArrayAlmostEqual(bounds, bounds)


if __name__ == '__main__':
    tests.main()
