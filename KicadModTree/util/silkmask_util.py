# KicadModTree is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KicadModTree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2022 by Armin Schoisswohl, @armin.sch

import sys

from KicadModTree.nodes import *
from . import geometric_util as geo
from typing import Iterable

from math import tan


def calculateOffsetPolygonNodes(nodes: Iterable[Vector2D], offset: float, split_angle: float = 90):
    """
    Calculates the polygon with a specified offset from the given polygon.

    Args:
        nodes: the list of Vector2D nodes of the polygon to offset.
        offset: the offset in mm.

    Returns:
        the list of offset nodes.

    Notes:
        - the nodes must be sorted clockwise (in the left-handed KiCad
          coordinate system), otherwise the offset will have to be inverted
        - there is currently no detection of eventually resulting self
          intersections
        - the polygon is assumed to be closed by connecting start and end point
    """

    tol = 1e-7
    if (abs(offset) < tol):
        return nodes[:]

    def clean_duplicates(nodes):
        N = len(nodes)
        return [nodes[n] for n in range(N) if not (nodes[n] - nodes[(n + 1) % N]).is_nullvec(tol)]

    # check if the polygon in closed -- means that we have to close it again afterwards
    closed = (nodes[0] - nodes[-1]).is_nullvec(tol)

    # remove duplicates, these don't make life easier
    nodes = clean_duplicates(nodes)

    offset_polygon = []
    num_nodes = len(nodes)
    for n in range(num_nodes):
        node = Vector2D(nodes[n])

        # calculate directions (incoming and outgoing that node)
        dir_vec1 = (node - Vector2D(nodes[(n - 1) % num_nodes])).normalize(tol)
        dir_vec2 = (Vector2D(nodes[(n + 1) % num_nodes]) - node).normalize(tol)
        # special handling of start and end point if not closed
        if (not closed):
            if (n == 0):
                dir_vec1 = dir_vec2
            elif (n == num_nodes - 1):
                dir_vec2 = dir_vec1

        # calculate outwards-pointing normals
        # Note: we are assuming the polygon is given clockwise in the KiCad
        # coordinate system, which is left-handed (x to the right, y downwards)
        norm_vec1 = copy(dir_vec1).rotate(-90, use_degrees=True)
        norm_vec2 = copy(dir_vec2).rotate(-90, use_degrees=True)
        # calculate angular bisector
        bisec = (norm_vec1 + norm_vec2).normalize(tol)

        # calculate the angle between the incoming and outgoing line
        angle = geo.normalizeAngle(dir_vec2.arg() - dir_vec1.arg())

        if (angle > split_angle):
            # split sharp convex corners into two surrounding the initial corner
            forward = tan(radians(angle/4))
            offset_polygon.append(node + offset * (norm_vec1 + forward * dir_vec1))
            offset_polygon.append(node + offset * (norm_vec2 - forward * dir_vec2))
        else:
            # move point on the angular intersection the correct amount (which is the offset
            # divided by the cosine of the angle between the edges
            if (bisec.is_nullvec(tol) or (norm_vec1.is_nullvec(tol) and norm_vec2.is_nullvec(tol))):
                cos_phi = 1
            else:
                cos_phi = bisec.inner(norm_vec1 if not norm_vec1.is_nullvec(tol) else norm_vec2)
            offset_polygon.append(node + (offset / cos_phi) * bisec)

    # TODO: check if we get self-intersections and eliminate them
    # there may be duplicates; remove them before returning
    offset_polygon = clean_duplicates(offset_polygon)

    if (closed):    # close the polygon again in case it was closed before
        offset_polygon.append(offset_polygon[0])

    return offset_polygon
