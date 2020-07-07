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
    datasheet: 'URL(s) to footprint datasheet'
    tags: 'KiCad tags go here'
  add-tags: 'more tags' # [optional] extends the tag list
  layout: # General footprint layout/drawing data
    type: '(Terminal|Socket)' # sets Pin 1 position and drawing mode
    width: !!float mm # [cosmetic] overall width of the connector
    height: !!float mm # [cosmetic] overall height of the connector
  width: !!float mm # [optional, cosmetic] overrides layout::width
  banks:
    n: !!uint # number of banks in the connector
    diff: !!uint # number of differential banks
    slots: !!uint even # number of pin positions in a bank
    space: !!float mm # distance between adjacent banks
    width: !!float mm # width of bank outline drawn on F.Fab
    height: !!float mm # height of bank outline drawn on F.Fab
  pads:
    signal: # signal pin parameters
      pitch: !!float mm
      width: !!float mm # Pad width
      height: !!float mm # Pad height
      y: !!float mm # vertical offset
    planes: # plane parameters
      width:
        - !!float mm # outer pins 
        - !!float mm # inner pins
      height: !!float mm # Ground pad heights
      space: # Distance between ground pads within each bank
        - !!float mm # outer pins
        - !!float mm # inner pins
  holes: # [optional] hole pair specifications, mirrored about y axis
    - # Hole spec. 1
      name: "" # [optional] name/number for plated holes
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
import math
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
    bank_slots = param['banks']['slots']

    ############################################################################
    # Copper layer(s)
    
    # Signal pad parameters
    pitch = param['pads']['signal']['pitch']
    pad_w = param['pads']['signal']['width']
    pad_h = param['pads']['signal']['height']
    pad_y = param['pads']['signal']['y']

    # Pin 1 position
    pin1 = Vector2D(0,0)
    pin1.x = -(bank_slots / 4)*pitch + pitch/2 - ((banks-1) / 2)*bank_x
    if mode == "Terminal":
        pin1.y = -pad_y
    elif mode == "Socket":
        pin1.y = pad_y
    else:
        raise ValueError("Connector type must be either 'Terminal' or 'Socket'")
    
    # Bank 1 center point
    bank1_mid = pin1.x - pitch/2 + (bank_slots / 4)*pitch

    # Place signal pads
    n = 1 # Pin counter
    pin = [] # Pin position list, organized by bank
    for b in range(0, banks):
        pin.append([])
        for slot in range(bank_slots):
            # Compute next pad location
            pos = {'x': pin1.x + (slot // 2)*pitch + b*bank_x,
                   'y': pin1.y - (slot  % 2)*(2*pin1.y),
                   'n': n+1, 'slot': slot}

            # Skip slots for differential banks
            if b < param['banks']['diff']:
                if ((slot+1) % 6 == 0 or # Skip every 3rd odd slot
                    (slot+2) % 6 == 0 or # Skip every 3rd even slot
                    # Only add end-of-bank pins if they are completing a pair
                    (slot+2 >= bank_slots and
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
    
    # Ground pad parameters
    gnd_h = param['pads']['planes']['height']
    # Combine spacing and width data into a zipped list: [(space,width), ...]
    gnd_sw = [sw for sw in zip(param['pads']['planes']['space'],
                               param['pads']['planes']['width'])]
    gnd_sw.sort() # Sort from lowest (inner) to highest (outer) spacing
    
    # Place ground plane pads
    for b in range(banks):
        mid = bank1_mid + b*bank_x # Bank midpoint
        # Iterate through space/width list to generate ground pads...
        for (space, width) in [(-s,w) for s,w in reversed(gnd_sw)] + gnd_sw:
            pad = Pad(number = "P" + str(b+1),
                      at = (mid + space/2, 0),
                      size = (width, gnd_h),
                      type = Pad.TYPE_SMT,
                      layers = Pad.LAYERS_SMT,
                      shape = Pad.SHAPE_RECT)
            fp.append(pad)
            n += 1

    ############################################################################
    # Holes
    if 'holes' in param:
        for p in param['holes']:
            drill = p['drill']
            shape = Pad.SHAPE_CIRCLE if type(drill) is float else Pad.SHAPE_OVAL
            h = [Pad(number = "MP" if 'pad' in p else "",
                     at     = (m*p['space']/2, p['y']),
                     drill  = drill,
                     size   = p['pad'] if 'pad' in p else drill,
                     type   = Pad.TYPE_THT if 'pad' in p else Pad.TYPE_NPTH,
                     layers = Pad.LAYERS_THT if 'pad' in p else Pad.LAYERS_NPTH,
                     shape  = shape) for m in (-1,1)]
            fp.extend(h)

    ############################################################################
    # Fabrication layer: F.Fab
    fab_line = config['fab_line_width']
    fab_mark = config['fab_pin1_marker_length']
    fab_w = param['layout']['width'] if 'width' not in param else param['width']
    fab_h = param['layout']['height']
    fab_y = fab_h / 2
    lEdge = -fab_w / 2
    rEdge = lEdge + fab_w
    chamfer = fab_h / 4 # 1/4 connector height, cosmetic only

    if mode == 'Terminal':
        # Left end outline
        lEnd = [(lEdge, -fab_y),
                (lEdge, fab_y-chamfer),
                (lEdge+chamfer, fab_y)]
        fp.append(PolygoneLine(nodes = lEnd,
                               layer = "F.Fab",
                               width = fab_line))
        # Right end outline (mirrors left end)
        fp.append(PolygoneLine(nodes = lEnd,
                               layer = "F.Fab",
                               width = fab_line,
                               x_mirror = 0))
        # Top and bottom lines
        fp.append(Line(start = (lEdge, -fab_y),
                       end   = (rEdge, -fab_y),
                       layer = "F.Fab",
                       width = fab_line))
        fp.append(Line(start = (lEdge+chamfer, fab_y),
                       end   = (rEdge-chamfer, fab_y),
                       layer = "F.Fab",
                       width = fab_line))
        # Pin 1 marker
        fp.append(markerArrow(x = pin1.x,
                              y = (fab_mark-fab_h) / 2,
                              width = fab_mark,
                              angle = 180,
                              layer = "F.Fab",
                              close = False,
                              line_width = fab_line))
    elif mode == 'Socket':
        # Outline rectangle
        fp.append(RectLine(start = (lEdge, -fab_y),
                           end   = (rEdge,  fab_y),
                           layer = "F.Fab",
                           width = fab_line))
        # Chamfer lines
        fp.append(Line(start = (lEdge, -fab_y+chamfer),
                       end   = (lEdge+chamfer, -fab_y),
                       layer = "F.Fab",
                       width = fab_line))
        fp.append(Line(start = (rEdge, -fab_y+chamfer),
                       end   = (rEdge-chamfer, -fab_y),
                       layer = "F.Fab",
                       width = fab_line))
        # Pin 1 marker
        fp.append(markerArrow(x = pin1.x,
                              y = (fab_h-fab_mark) / 2,
                              width = fab_mark,
                              layer = "F.Fab",
                              close = False,
                              line_width = fab_line))

    # Draw bank and ground plane outlines
    for b in range(banks):
        mid = bank1_mid + b*bank_x
        # Bank outline
        fp.append(RectLine(start = (mid-bank_w/2, -bank_h/2),
                           end   = (mid+bank_w/2,  bank_h/2),
                           layer = "F.Fab",
                           width = fab_line))
    
    ############################################################################
    # Silkscreen: F.SilkS
    #silk_offset = param['layout']['silk-offset']
    silk_offset = config['silk_fab_offset']
    silk_pad = {'x': config['silk_pad_clearance'] + pad_w/2,
                'y': config['silk_pad_clearance'] + pad_h/2}
    silk_line = config['silk_line_width']
    silk_y = fab_y + silk_offset
    silk_lEdge = lEdge - silk_offset
    silk_rEdge = rEdge + silk_offset
    silk_chamfer = chamfer + silk_offset/2
    silk_pin1 = pin1.x - silk_pad['x']
    
    if mode == 'Terminal':
        # Polygon left end outline points
        silk_lEnd = [{'x': silk_pin1,  'y': -silk_y},
                     {'x': silk_lEdge, 'y': -silk_y},
                     {'x': silk_lEdge, 'y': silk_y-silk_chamfer},
                     {'x': silk_lEdge+silk_chamfer, 'y': silk_y},
                     {'x': silk_pin1,  'y': silk_y}]
        # Pin 1 indicator
        fp.append(Line(start = (silk_pin1, pin1.y - pad_h/2),
                       end   = (silk_pin1, -silk_y),
                       layer = "F.SilkS",
                       width = silk_line))
    elif mode == 'Socket':
        # Left end outline points
        silk_lEnd = [{'x': silk_pin1,  'y':  silk_y},
                     {'x': silk_lEdge, 'y':  silk_y},
                     {'x': silk_lEdge, 'y': -silk_y},
                     {'x': silk_pin1,  'y': -silk_y}]
        # Pin 1 indicator
        fp.append(markerArrow(x = pin1.x,
                              y = pin1.y + silk_pad['y'],
                              width = fab_mark / 2,
                              line_width = silk_line,
                              layer = "F.SilkS"))

    # Generate right end outline
    silk_rEnd = deepcopy(silk_lEnd)
    # Mirror about x axis
    for i in range(len(silk_rEnd)):
        silk_rEnd[i]['x'] = -silk_rEnd[i]['x']
    # Define right outline inner offset from the last pin
    # (if the last bank is differential, it does not perfectly mirror the first)
    silk_rEnd[0]['x'] = silk_rEnd[-1]['x'] = pin[-1][-1]['x'] + silk_pad['x']

    # Draw left and right end outlines
    fp.append(PolygoneLine(nodes = silk_lEnd,
                           layer = "F.SilkS",
                           width = silk_line))
    fp.append(PolygoneLine(nodes = silk_rEnd,
                           layer = "F.SilkS",
                           width = silk_line))

    # Draw outlines between banks
    for b in range(banks-1):
        fp.extend([Line(start = (pin[b][-1]['x']  + silk_pad['x'], m*silk_y),
                        end   = (pin[b+1][0]['x'] - silk_pad['x'], m*silk_y),
                        layer = "F.SilkS",
                        width = silk_line) for m in (-1,1)])

    ############################################################################
    # Courtyard: F.CrtYd
    court_line = config['courtyard_line_width']
    court_grid = config['courtyard_grid']
    court_offset = config['courtyard_offset']['connector']

    court_x = roundToBase(fab_w/2 + court_offset, court_grid)
    court_y = roundToBase(max(fab_y, pad_y + pad_h/2) + court_offset, court_grid)

    fp.append(RectLine(start  = (-court_x, -court_y),
                       end    = ( court_x,  court_y),
                       layer  = "F.CrtYd",
                       width  = court_line))
    
    ############################################################################
    # Set Metadata
    
    # Draw reference and value
    text_y = court_y + 1.0
    fp.append(Text(type = 'reference', text = 'REF**',
                   at = (0, -text_y),
                   layer = "F.SilkS"))
    fp.append(Text(type = 'user', text = '%R',
                   at = (0, -text_y),
                   layer = "F.Fab"))
    fp.append(Text(type = 'value', text=param['name'],
                   at = (0, text_y),
                   layer="F.Fab"))
    
    # Set surface-mount attribute
    fp.setAttribute('smd')
    
    # Part number
    partnum = param['meta'].get('pn', param['name'].split('_')[1])

    # Pins or pairs/bank
    if param['banks']['diff'] == banks:
        # Differential mode: round up to nearest even number of pairs
        pins_or_pairs = (bank_slots // 3) + (bank_slots // 3) % 2
    else:
        pins_or_pairs = bank_slots

    # Description
    desc = param['meta']['description']
    desc = desc.format(pn = partnum,
                       type = mode,
                       ds = param['meta']['datasheet'],
                       pitch = pitch,
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
                        default='Connector_Samtec_QStrip_QPairs',
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
