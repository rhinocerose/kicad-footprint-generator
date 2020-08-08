#!/usr/bin/python

# This file is part of kicad-footprint-generator.
# 
# kicad-footprint-generator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# kicad-footprint-generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details. You should have received a copy of the GNU General Public
# License along with kicad-footprint-generator. If not, see
# <http://www.gnu.org/licenses/>.
# 
# Copyright (C) 2019 by Caleb Reister <calebreister@gmail.com>
#

"""
YAML footprint specification
---
Footprint_Name:
  library: 'library name' # [optional] KiCad library to use, overrides default
  meta: # Footprint metadata
    pn: 'part number' # [optional] overrides automatic part number detection
    description: 'Brief description of the footprint'
    tags: 'KiCad tags go here'
    datasheet: 'URL(s) to footprint datasheet'
  add-tags: 'more tags' # [optional] extends the tag list
  layout: # General footprint layout/drawing data
    type: '(Terminal|Socket)' # sets Pin 1 position and drawing mode
    width: !!float mm # [cosmetic] overall width of the connector
    height: !!float mm # [cosmetic] overall height of the connector
    y: !!float mm # [cosmetic] y-offset used to draw connector outline
    edge: !!float mm # y-offset of PCB edge
  banks:
    n: !!uint # number of banks in the connector
    diff: !!uint # number of differential banks
    space: !!float mm # distance between adjacent banks
    width: !!float mm # width of bank outline drawn on F.Fab
    height: !!float mm # height of bank outline drawn on F.Fab
  pads:
    signal: # signal pin parameters
      n: !!uint # Number of pin slots on a bank
      rows: !!uint # Number of pin rows
      pitch: !!float mm
      width: !!float mm # Pad width
      height: !!float mm # Pad height
      y: [!!float mm, ...] # y-offset for each pin row
    plane: # plane parameters
      n: !!uint # Number of holes for plane connection
      pitch: !!float mm
      y: !!float mm # y-offset of plane holes
      drill: !!float mm # drill diameter
      pad: !!float mm # pad diameter
  holes: # [optional] hole pair specifications, mirrored about y axis
    - # Hole spec. 1
      name: "" # [optional] name/number for plated holes
      n: !!uint # number of holes to drill
      drill: !!float mm # drill diameter (a list produces an oval)
      pad: !!float mm # [optional] PTH pad diameter (a list produces an oval)
      space: !!float mm # distance between holes mirrored about the y-axis
      y: !!float mm # vertical offset
    - # Hole spec. 2...
...
"""

import sys
import os
import argparse
from copy import deepcopy
from math import *
import yaml

# Load parent path of KicadModTree
sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))
sys.path.append(os.path.join(sys.path[0], "..", "..", "tools"))

from KicadModTree import *
from footprint_text_fields import addTextFields
from helpers import *

def generate_one_footprint(param, config, default_lib):
    fp = Footprint(param['name'])
    
    # Terminal or Socket mode
    mode = param['layout']['type'].capitalize()
    
    # Bank parameters
    banks  = param['banks']['n']
    bank_x = param['banks']['space']
    bank_w = param['banks']['width']
    bank_h = param['banks']['height']

    ############################################################################
    # Copper layer(s)
    
    # Signal pad parameters
    pad_pitch = param['pads']['signal']['pitch']
    pad_rows = param['pads']['signal']['rows']
    pad_w = param['pads']['signal']['width']
    pad_h = param['pads']['signal']['height']
    pad_y = param['pads']['signal']['y']
    pad_n = param['pads']['signal']['n']

    # Plane parameters
    plane_pitch = param['pads']['plane']['pitch']
    plane_d = param['pads']['plane']['drill']
    plane_p = param['pads']['plane']['pad']
    plane_y = param['pads']['plane']['y']
    plane_n = param['pads']['plane']['n']

    # Terminal or Socket mode
    mode = param['layout']['type'].capitalize()
    if mode == "Terminal":
        x_inv = 1
    elif mode == "Socket":
        x_inv = -1
    else:
        raise ValueError("Connector type must be either 'Terminal' or 'Socket'")
    
    # Pin 1 position
    pin1 = Vector2D(0,0)
    pin1.x = -(pad_n/4)*pad_pitch + pad_pitch/2 - ((banks-1) / 2)*bank_x
    pin1.y = pad_y[0]
    
    # Bank 1 center point
    bank1_mid = pin1.x - pad_pitch/2 + (pad_n / 4)*pad_pitch

    # Place signal pads
    n = 1 # Pin counter
    pin = [] # Pin position list, organized by bank
    for b in range(banks):
        pin.append([])
        for slot in range(pad_n):
            # Compute next pad location
            for r in range(pad_rows):
                pos = {'x': pin1.x + (slot // pad_rows)*pad_pitch + b*bank_x,
                       'y': pad_y[slot % 2],
                       'n': n+1, 'slot': slot}

            # Skip slots for differential banks
            if b < param['banks']['diff']:
                if ((slot+1) % 6 == 0 or # Skip every 3rd odd slot
                    (slot+2) % 6 == 0 or # Skip every 3rd even slot
                    # Only add end-of-bank pins if they are completing a pair
                    (slot+2 >= pad_n and
                     pin[b][-2]['slot'] != slot-2)):
                    continue

            # Create pad
            pin[b].append(pos) # Add position to list
            # Create pad (both single-ended and differential)
            pad = Pad(number = str(n),
                      at = pos,
                      size = (pad_w, pad_h),
                      type = Pad.TYPE_SMT,
                      layers = Pad.LAYERS_SMT,
                      shape = Pad.SHAPE_RECT)
            fp.append(pad)
            n += 1
        
        mid = bank1_mid + b*bank_x # Bank midpoint
        for h in range(plane_n):
            hole = Pad(number = "P" + str(b+1),
                       at     = ((h - (plane_n-1)/2)*plane_pitch + mid, plane_y),
                       drill  = plane_d,
                       size   = plane_p,
                       type   = Pad.TYPE_THT,
                       layers = Pad.LAYERS_THT,
                       shape  = Pad.SHAPE_CIRCLE)
            fp.append(hole)
    
    ############################################################################
    # Holes
    if 'holes' in param:
        for hole in param['holes']:
            drill = hole['drill']
            shape = Pad.SHAPE_CIRCLE if type(drill) is float else Pad.SHAPE_OVAL
            holes = [Pad(number = "MP" if 'pad' in hole else "",
                         at     = ((h/(hole['n']-1) - 1/2)*hole['space'], hole['y']),
                         drill  = drill,
                         size   = hole['pad'] if 'pad' in hole else drill,
                         type   = Pad.TYPE_THT if 'pad' in hole else Pad.TYPE_NPTH,
                         layers = Pad.LAYERS_THT if 'pad' in hole else Pad.LAYERS_NPTH,
                         shape  = shape) for h in range(hole['n'])]
            fp.extend(holes)

    ############################################################################
    # Fabrication layer: F.Fab
    fab_line = config['fab_line_width']
    fab_mark = config['fab_pin1_marker_length']
    fab_w = param['layout']['width'] if 'width' not in param else param['width']
    fab_h = param['layout']['height']
    fab_y = param['layout']['y']
    fab_edge = fab_w/2

    if param['layout']['type'] == "Terminal":
        # Draw left and right outlines
        # Angle measured from 3D model of QTH-060-01-L-D-RA
        fab_end = [[banks*bank_x/2, pin1.y],
                   [banks*bank_x/2 + (fab_y-fab_h-pin1.y)/tan(-1.112), fab_y-fab_h],
                   [fab_w/2, fab_y-fab_h],
                   [fab_w/2, fab_y],
                   [banks*bank_x/2, fab_y]]
        fp.append(PolygoneLine(nodes = fab_end,
                               layer = "F.Fab",
                               width = fab_line))
        fp.append(PolygoneLine(nodes = fab_end,
                               layer = "F.Fab",
                               width = fab_line,
                               x_mirror = 0))
        fp.append(Line(start = (-banks*bank_x/2, pin1.y),
                       end   = ( banks*bank_x/2, pin1.y),
                       layer = "F.Fab",
                       width = fab_line))
        # Terminal outline
        fp.append(RectLine(start  = (-banks*bank_x/2, fab_y),
                           end    = ( banks*bank_x/2, fab_y + bank_h),
                           layer  = "F.Fab",
                           width  = fab_line))

    ############################################################################
    # Silkscreen: F.SilkS
    silk_offset = config['silk_fab_offset']
    silk_pad = {'x': config['silk_pad_clearance'] + pad_w/2,
                'y': config['silk_pad_clearance'] + pad_h/2}
    silk_line = config['silk_line_width']
    silk_pad = {'x': config['silk_pad_clearance'] + pad_w/2,
                'y': config['silk_pad_clearance'] + pad_h/2}

    # Draw silkscreen end outlines
    silk_end = fab_end.copy()
    silk_end.pop()
    silk_end_offset = [(-silk_offset, -silk_offset),
                       (-silk_offset, -silk_offset),
                       ( silk_offset, -silk_offset),
                       ( silk_offset,  0)]
    for a in range(len(silk_end)):
        for b in range(2):
            silk_end[a][b] += silk_end_offset[a][b]
    
    fp.append(PolygoneLine(nodes = silk_end,
                           layer = "F.SilkS",
                           width = silk_line))
    fp.append(PolygoneLine(nodes = silk_end,
                           layer = "F.SilkS",
                           width = silk_line,
                           x_mirror = 0))

    # Extend end outlines to pins
    fp.append(Line(start = (-banks*bank_x/2+silk_offset, pin1.y-silk_offset),
                   end   = (pin[0][0]['x']-silk_pad['x'], pin1.y-silk_offset),
                   layer = "F.SilkS",
                   width = silk_line))
    fp.append(Line(start = (banks*bank_x/2-silk_offset, pin1.y-silk_offset),
                   end   = (pin[-1][-1]['x']+silk_pad['x'], pin1.y-silk_offset),
                   layer = "F.SilkS",
                   width = silk_line))

    # Pin 1 indicator
    fp.append(markerArrow(x = pin[0][0]['x'],
                          y = pin[0][0]['y'] - silk_pad['y'],
                          width = fab_mark / 2,
                          line_width = silk_line,
                          angle = 180,
                          layer = "F.SilkS"))

    # Draw outlines between banks
    for b in range(banks-1):
        fp.append(Line(start = (pin[b][-1]['x']  + x_inv*silk_pad['x'], pin1.y-silk_offset),
                       end   = (pin[b+1][0]['x'] - x_inv*silk_pad['x'], pin1.y-silk_offset),
                       layer = "F.SilkS",
                       width = silk_line))
    
    ############################################################################
    # PCB Edge: Dwgs.User
    fp.append(Line(start = (-fab_edge, fab_y + param['layout']['edge']),
                   end   = ( fab_edge, fab_y + param['layout']['edge']),
                   layer = "Dwgs.User",
                   width = fab_line))
    
    fp.append(Text(type = "user", text = "PCB Edge",
                   at = (0, fab_y + param['layout']['edge'] + 1.0),
                   layer = "Dwgs.User"))

    ############################################################################
    # Courtyard: F.CrtYd
    court_line = config['courtyard_line_width']
    court_grid = config['courtyard_grid']
    court_offset = config['courtyard_offset']['connector']
    
    court = {'x': roundToBase(fab_w/2 + court_offset, court_grid),
             'y': [roundToBase(fab_y -  fab_h - court_offset, court_grid),
                   roundToBase(fab_y + bank_h + court_offset, court_grid)]}
    
    fp.append(RectLine(start  = (-court['x'], court['y'][0]),
                       end    = ( court['x'], court['y'][1]),
                       layer  = "F.CrtYd",
                       width  = court_line))
    
    ############################################################################
    # Set Metadata
    
    # Draw reference and value
    text_y = fab_y + 1.0
    fp.append(Text(type = 'reference', text = 'REF**',
                   at = (0, -text_y),
                   layer = "F.SilkS"))
    fp.append(Text(type = 'user', text = '%R',
                   at = (0, -text_y),
                   layer = "F.Fab"))
    fp.append(Text(type = 'value', text=param['name'],
                   at = (0, text_y + bank_h + court_offset),
                   layer="F.Fab"))
    
    # Set surface-mount attribute
    fp.setAttribute('smd')
    
    # Part number
    partnum = param['meta'].get('pn', param['name'].split('_')[1])

    # Pins or pairs/bank
    if param['banks']['diff'] == banks:
        # Differential mode: round up to nearest even number of pairs
        pins_or_pairs = (pad_n // 3) + (pad_n // 3) % 2
    else:
        pins_or_pairs = pad_n

    # Description
    desc = param['meta']['description']
    desc = desc.format(pn = partnum,
                       type = mode,
                       ds = param['meta']['datasheet'],
                       pitch = pad_pitch,
                       banks = banks,
                       pins = pins_or_pairs)
    fp.setDescription(desc)

    # Tags
    tags = param['meta']['tags']
    if 'add-tags' in param:
        tags += ' ' + param['add-tags']
    fp.setTags(tags)

    # 3D model path
    library = param.get('library', default_lib)
    model_path = os.path.join("${KISYS3DMOD}",
                              library+".3dshapes",
                              param['name'] + ".wrl")
    fp.append(Model(filename = model_path))

    ############################################################################
    # Write kicad_mod file
    
    os.makedirs(library+'.pretty', exist_ok=True)
    filename = os.path.join(library+'.pretty', param['name']+'.kicad_mod')
    KicadFileHandler(fp).writeFile(filename)

################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--global-config', type=str, nargs='?',
                        default='../../tools/global_config_files/config_KLCv3.0.yaml',
                        help='Global KLC configuration YAML file')
    parser.add_argument('--series-config', type=str, nargs='?',
                        default='../conn_config_KLCv3.yaml',
                        help='Series KLC configuration YAML file')
    parser.add_argument('--library', type=str, nargs='?',
                        default='Connector_Samtec_QSeries',
                        help='Default KiCad library name (without extension)')
    parser.add_argument('files', metavar='file', type=str, nargs='*',
                        help='YAML file(s) containing footprint parameters')
    args = parser.parse_args()

    with open(args.global_config, 'r') as config_stream:
        try:
            config = yaml.safe_load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    with open(args.series_config, 'r') as config_stream:
        try:
            config.update(yaml.safe_load(config_stream))
        except yaml.YAMLError as exc:
            print(exc)

    if len(args.files) == 0:
        parser.print_help()
        sys.exit(1)

    print("Default Library:", args.library)
    
    for path in args.files:
        print("Reading", path)
        with open(path, 'r') as stream:
            try:
                footprints = yaml.safe_load(stream)
                
                if footprints is None:
                    print(path, "empty, skipping...")
                    continue

                for fp_name in footprints:
                    fp_params = footprints.get(fp_name)                    
                    if 'name' in fp_params:
                        print("WARNING: setting 'name' to", fp_name)
                        
                    fp_params['name'] = fp_name

                    print("  - ",
                          fp_params.get('library', args.library), ".pretty/",
                          fp_name, ".kicad_mod", sep="")
                    
                    generate_one_footprint(fp_params, config, args.library)
            except yaml.YAMLError as exc:
                print(exc)
