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
# (C) 2016-2018 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>

from __future__ import division

import sys, os
from KicadModTree import *  # NOQA
from KicadModTree.util.pad_number_generators import get_generator

def add_dual_or_quad_pad_border(kicad_mod, configuration, pad_details, device_params):
    r""" Add pads for a quad (qfn, qfp) or dual (soic, dfn) package

    :params:
        * *kicad_mod* (KicadModTree) --
          The KicadModTree instance that the pads should be added to
        * *configuration* (dict) --
          Dict holding configuration information. Details see below.
        * *pad_details* (dict) --
          Dict holding the size and position parameters for the pads. Details see below.
        * *device_params* (dict) --
          Dict holding the device parameters. Used entries see below.

    :configuration dict:
        * *round_rect_radius_ratio* (float) --
          Roundrect radius ratio for the pads (default: 0)
        * *round_rect_max_radius* (float) --
          Optional parameter to set maximum roundrect radius
        * *kicad4_compatible* (boolean) --
          Use only version 4 features (default: False)

    :pad details dict:
        Dict holding the details for the 4 possible pad arrays (left, right, top, bottom)
        Each of these has the following entries:
        * *center* (Vector2D compatible) --
          Array center
        * *size* (Vector2D compatible) --
          Size of pads

    :device parameters:
        * *num_pins_x* (int) --
          Pad count in x direction (count of vertical pads)
        * *num_pins_y* (int) --
          Pad count in y direction (count of horizontal pads)
        * *pitch* (float) --
          Distance between two pads (pitch)
        * *exclude_pin_list* (list) --
          List of pins that are excluded (default: empty list)
        * *chamfer_edge_pins* (float) --
          Chamfering of pads nearest the corners (used to increase clearance)
          Only used for quad version
        * *edge_heel_reduction* (float) --
          Heel reduction for pads nearest the corners (used to increase clearance)
          Only used for quad version
    """
    pad_shape_details = {}
    pad_shape_details['shape'] = Pad.SHAPE_ROUNDRECT
    pad_shape_details['radius_ratio'] = configuration.get('round_rect_radius_ratio', 0)
    if 'round_rect_max_radius' in configuration:
        pad_shape_details['maximum_radius'] = configuration['round_rect_max_radius']

    if 'exclude_pin_list' in device_params:
        pad_shape_details['exclude_pin_list'] = device_params['exclude_pin_list']

    if device_params['num_pins_x'] == 0:
        radius = add_dual_pad_border_y(kicad_mod, pad_details, device_params, pad_shape_details)
    elif device_params['num_pins_y'] == 0:
        radius = add_dual_pad_border_x(kicad_mod, pad_details, device_params, pad_shape_details)
    else:
        radius = add_quad_pad_border(
            kicad_mod, pad_details, device_params, pad_shape_details,
            configuration.get('kicad4_compatible', False))

    return radius

def add_dual_pad_border_y(kicad_mod, pad_details, device_params, pad_shape_details):
    r""" Add pads for a dual row packages

    :params:
        * *kicad_mod* (KicadModTree) --
          The KicadModTree instance that the pads should be added to
        * *pad_details* (dict) --
          Dict holding the size and position parameters for the pads. Details see below.
        * *device_params* (dict) --
          Dict holding the device parameters. Used entries see below.
        * *pad_shape_details* (dict) --
          Dict holding common pad parameters. Details see below.

    :pad details dict:
        Dict holding the details for the 2 possible pad arrays (left, right)
        Each of these has the following entries:
        * *center* (Vector2D compatible) --
          Array center
        * *size* (Vector2D compatible) --
          Size of pads

    :device parameters:
        * *num_pins_y* (int) --
          Pad count in y direction (count of horizontal pads)
        * *pitch* (float) --
          Distance between two pads (pitch)
        * *exclude_pin_list* (list) --
          List of pins that are excluded (default: empty list)

    :pad shape details:
        * *shape* (Pad.SHAPE) --
          Determines the pad shape option to be used for the arrays
        * *radius_ratio* (float) --
          Roundrect radius ratio for the pads
        * *maximum_radius* (float) --
          Maximum roundrect radius
        * *exclude_pin_list* (list) --
          List of pads to be included
    """
    init = 1
    increment = get_generator(device_params)

    pa = PadArray(
            initial= init,
            type=Pad.TYPE_SMT,
            layers=Pad.LAYERS_SMT,
            pincount=device_params['num_pins_y'],
            x_spacing=0, y_spacing=device_params['pitch'],
            increment=increment,
            **pad_details['left'], **pad_shape_details,
            )
    kicad_mod.append(pa)
    init += device_params['num_pins_y']
    kicad_mod.append(PadArray(
        initial= init,
        type=Pad.TYPE_SMT,
        layers=Pad.LAYERS_SMT,
        pincount=device_params['num_pins_y'],
        x_spacing=0, y_spacing=-device_params['pitch'],
        increment=increment,
        **pad_details['right'], **pad_shape_details,
        )
    )

    pads = pa.getVirtualChilds()
    pad = pads[0]
    return pad.getRoundRadius()

def add_dual_pad_border_x(kicad_mod, pad_details, device_params, pad_shape_details):
    r""" Add pads for a dual row packages with mirrored pad numbering

    :params:
        * *kicad_mod* (KicadModTree) --
          The KicadModTree instance that the pads should be added to
        * *pad_details* (dict) --
          Dict holding the size and position parameters for the pads. Details see below.
        * *device_params* (dict) --
          Dict holding the device parameters. Used entries see below.
        * *pad_shape_details* (dict) --
          Dict holding common pad parameters. Details see below.

    :pad details dict:
        Dict holding the details for the 2 possible pad arrays (top, bottom)
        Each of these has the following entries:
        * *center* (Vector2D compatible) --
          Array center
        * *size* (Vector2D compatible) --
          Size of pads

    :device parameters:
        * *num_pins_x* (int) --
          Pad count in x direction (count of vertical pads)
        * *pitch* (float) --
          Distance between two pads (pitch)
        * *exclude_pin_list* (list) --
          List of pins that are excluded (default: empty list)

    :pad shape details:
        * *shape* (Pad.SHAPE) --
          Determines the pad shape option to be used for the arrays
        * *radius_ratio* (float) --
          Roundrect radius ratio for the pads
        * *maximum_radius* (float) --
          Maximum roundrect radius
        * *exclude_pin_list* (list) --
          List of pads to be included
    """
    init = 1
    increment = get_generator(device_params)

    pa = PadArray(
            initial= init,
            type=Pad.TYPE_SMT,
            layers=Pad.LAYERS_SMT,
            pincount=device_params['num_pins_x'],
            y_spacing=0, x_spacing=device_params['pitch'],
            increment=increment,
            **pad_details['top'], **pad_shape_details,
    )
    kicad_mod.append(pa)
    init += device_params['num_pins_x']
    kicad_mod.append(PadArray(
        initial= init,
        type=Pad.TYPE_SMT,
        layers=Pad.LAYERS_SMT,
        pincount=device_params['num_pins_x'],
        y_spacing=0, x_spacing=-device_params['pitch'],
        increment=increment,
        **pad_details['bottom'], **pad_shape_details,
        )
    )

    pads = pa.getVirtualChilds()
    pad = pads[0]
    return pad.getRoundRadius()

def add_quad_pad_border(kicad_mod, pad_details, device_params,
                        pad_shape_details, kicad4_compatible):
    r""" Add pads for a quad package

    :params:
        * *kicad_mod* (KicadModTree) --
          The KicadModTree instance that the pads should be added to
        * *pad_details* (dict) --
          Dict holding the size and position parameters for the pads. Details see below.
        * *device_params* (dict) --
          Dict holding the device parameters. Used entries see below.
        * *pad_shape_details* (dict) --
          Dict holding common pad parameters. Details see below.
        * *kicad4_compatible* (boolean) --
          Flag for enabling compatibility mode (uses only version 4 file format features)

    :pad details dict:
        Dict holding the details for the 4 possible pad arrays (left, right, top, bottom)
        Each of these has the following entries:
        * *center* (Vector2D compatible) --
          Array center
        * *size* (Vector2D compatible) --
          Size of pads

    :device parameters:
        * *num_pins_x* (int) --
          Pad count in x direction (count of vertical pads)
        * *num_pins_y* (int) --
          Pad count in y direction (count of horizontal pads)
        * *pitch* (float) --
          Distance between two pads (pitch)
        * *exclude_pin_list* (list) --
          List of pins that are excluded (default: empty list)
        * *chamfer_edge_pins* (float) --
          Chamfering of pads nearest the corners (used to increase clearance)
        * *edge_heel_reduction* (float) --
          Heel reduction for pads nearest the corners (used to increase clearance)

    :pad shape details:
        * *shape* (Pad.SHAPE) --
          Determines the pad shape option to be used for the arrays
        * *radius_ratio* (float) --
          Roundrect radius ratio for the pads
        * *maximum_radius* (float) --
          Maximum roundrect radius
        * *exclude_pin_list* (list) --
          List of pads to be included
    """
    chamfer_size = device_params.get('chamfer_edge_pins', 0)

    pad_size_red = device_params.get('edge_heel_reduction', 0)
    if kicad4_compatible:
        chamfer_size = 0
        pad_size_red += device_params.get('chamfer_edge_pins', 0)


    init = 1
    corner_first = CornerSelection({CornerSelection.TOP_RIGHT: True})
    corner_last = CornerSelection({CornerSelection.BOTTOM_RIGHT: True})
    pad_size_reduction = {'x+': pad_size_red} if pad_size_red > 0 else None
    increment = get_generator(device_params)

    pa = PadArray(
            initial= init,
            type=Pad.TYPE_SMT,
            layers=Pad.LAYERS_SMT,
            pincount=device_params['num_pins_y'],
            x_spacing=0, y_spacing=device_params['pitch'],
            chamfer_size=chamfer_size,
            chamfer_corner_selection_first=corner_first,
            chamfer_corner_selection_last=corner_last,
            end_pads_size_reduction = pad_size_reduction,
            increment=increment,
            **pad_details['left'], **pad_shape_details,
            )
    kicad_mod.append(pa)

    init += device_params['num_pins_y']
    corner_first = copy(corner_first).rotateCCW()
    corner_last = copy(corner_last).rotateCCW()
    pad_size_reduction = {'y-': pad_size_red} if pad_size_red > 0 else None

    kicad_mod.append(PadArray(
        initial= init,
        type=Pad.TYPE_SMT,
        layers=Pad.LAYERS_SMT,
        pincount=device_params['num_pins_x'],
        y_spacing=0, x_spacing=device_params['pitch'],
        chamfer_size=chamfer_size,
        chamfer_corner_selection_first=corner_first,
        chamfer_corner_selection_last=corner_last,
        end_pads_size_reduction = pad_size_reduction,
        increment=increment,
        **pad_details['bottom'], **pad_shape_details,
        )
    )

    init += device_params['num_pins_x']
    corner_first = copy(corner_first).rotateCCW()
    corner_last = copy(corner_last).rotateCCW()
    pad_size_reduction = {'x-': pad_size_red} if pad_size_red > 0 else None

    kicad_mod.append(PadArray(
        initial= init,
        type=Pad.TYPE_SMT,
        layers=Pad.LAYERS_SMT,
        pincount=device_params['num_pins_y'],
        x_spacing=0, y_spacing=-device_params['pitch'],
        chamfer_size=chamfer_size,
        chamfer_corner_selection_first=corner_first,
        chamfer_corner_selection_last=corner_last,
        end_pads_size_reduction = pad_size_reduction,
        increment=increment,
        **pad_details['right'], **pad_shape_details,
        )
    )

    init += device_params['num_pins_y']
    corner_first = copy(corner_first).rotateCCW()
    corner_last = copy(corner_last).rotateCCW()
    pad_size_reduction = {'y+': pad_size_red} if pad_size_red > 0 else None

    kicad_mod.append(PadArray(
        initial= init,
        type=Pad.TYPE_SMT,
        layers=Pad.LAYERS_SMT,
        pincount=device_params['num_pins_x'],
        y_spacing=0, x_spacing=-device_params['pitch'],
        chamfer_size=chamfer_size,
        chamfer_corner_selection_first=corner_first,
        chamfer_corner_selection_last=corner_last,
        end_pads_size_reduction = pad_size_reduction,
        increment=increment,
        **pad_details['top'], **pad_shape_details,
        )
    )

    pads = pa.getVirtualChilds()
    pad = pads[0]
    return pad.getRoundRadius()
