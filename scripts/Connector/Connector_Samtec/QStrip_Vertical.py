#!/usr/bin/python

"""
YAML footprint specification

---
Footprint_Name:
  description: 'Brief description of the footprint'
  datasheet: 'URL to footprint datasheet'
  tags: 'KiCad tags go here'
  add-tags: 'more tags' # [optional], used to extend the tag list
  layout:
    type: '(Terminal|Socket)'
    width: !!float mm # width
    height: !!float mm # height
  width: !!float mm # [optional] overrides layout::width
  banks:
    n: !!int # number of banks in the connector
    pins: !!int even # number of pins in a bank
    diff: !!int <= n # number of differential banks
    space: !!float mm # distance between adjacent banks
    width: !!float mm # Width of outline on F.Fab
    height: !!float mm # Height of outline on F.Fab
  pins:
    signal: # Signal pin parameters
      pitch: !!float mm
      width: !!float mm # Pad width
      height: !!float mm # Pad height
      y: !!float mm # vertical offset
    ground: # Ground pin parameters
      width:
        - !!float mm # outer pins 
        - !!float mm # inner pins
      height: !!float mm # Ground pad heights
      space: # Distance between ground pads within each bank
        - !!float mm # outer pins
        - !!float mm # inner pins
  holes: # [optional] hole pair specifications
    - # Hole spec. 1
      name: "" # [optional] name/number for plated holes
      drill: !!float mm # drill diameter
      ring: !!float mm # [optional] annular ring
      space: !!float mm # distance between holes mirrored about the x-axis
      y: !!float mm # vertical offset
    - # Hole spec. 2
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

from KicadModTree import *

def markerArrow(x, y, width, line_width, layer, angle=0, close=True):
    node = Node()
    points = [(-width/2, width/2),
              (0, 0),
              (width/2, width/2)]

    if close:
        points.append((-width/2, width/2))

    node.append(PolygoneLine(nodes = points,
                             layer = "F.Fab",
                             width = line_width))
    node.insert(Rotation(angle))
    node.insert(Translation(x,y))
    return node

def generate_one_footprint(param, config, library):
    fp = Footprint(param['name'])

    # Terminal or Socket mode
    mode = param['layout']['type'].capitalize()

    # Bank parameters
    banks  = param['banks']['n']
    bank_x = param['banks']['space']
    bank_w = param['banks']['width']
    bank_h = param['banks']['height']
    pins_per_bank = param['banks']['pins']

    ############################################################################
    # Copper layer(s)
    
    # Signal pad parameters
    pitch = param['pins']['signal']['pitch']
    pad_w = param['pins']['signal']['width']
    pad_h = param['pins']['signal']['height']
    pad_y = param['pins']['signal']['y']

    # Pin 1 position
    pin1 = Vector2D(0,0)
    pin1.x = -(pins_per_bank / 4)*pitch + pitch/2 - ((banks-1) / 2)*bank_x
    if mode == "Terminal":
        pin1.y = -pad_y
    elif mode == "Socket":
        pin1.y = pad_y
    else:
        raise ValueError("Connector type must be either 'Terminal' or 'Socket'")
    
    # Bank 1 center point
    bank1_mid = pin1.x - pitch/2 + (pins_per_bank / 4)*pitch

    # Place signal pads
    n = 1 # Pin counter
    pin = [] # Pin position list, organized by bank
    for b in range(0, banks):
        pin.append([])
        for p in range(0, pins_per_bank):
            # Compute next pad location
            pos = Vector2D(pin1.x + (p // 2)*pitch + b*bank_x,
                           pin1.y - (p  % 2)*(2*pin1.y))
            if b < param['banks']['diff'] and ((p+1) % 6  == 0 or (p+2) % 6 == 0):
                # Place gaps between differential pairs
                continue
            else:
                pin[b].append(pos) # Add position to list
                # Create pad (both single-ended and differential)
                pad = Pad(number = str(n),
                          at = pos,
                          size = (pad_w, pad_h),
                          type = Pad.TYPE_SMT,
                          layers = Pad.LAYERS_SMT,
                          shape = Pad.SHAPE_RECT)
                fp.append(pad)
                n = n + 1
    
    # Ground pad parameters
    gnd_height    = param['pins']['ground']['height']
    gnd_width_out = param['pins']['ground']['width'][0]
    gnd_width_in  = param['pins']['ground']['width'][1]
    gnd_space_out = param['pins']['ground']['space'][0] / 2
    gnd_space_in  = param['pins']['ground']['space'][1] / 2
    gnd_space = [-gnd_space_out, -gnd_space_in, gnd_space_in, gnd_space_out]
    gnd_size  = [(gnd_width_out, gnd_height),
                 (gnd_width_in,  gnd_height),
                 (gnd_width_in,  gnd_height),
                 (gnd_width_out, gnd_height)]
    # Place ground plane pads
    for b in range(banks):
        mid = bank1_mid + b*bank_x # Bank midpoint
        for i in range(len(gnd_space)):
            pad = Pad(number = str(n),
                      at = (mid+gnd_space[i], 0),
                      size = gnd_size[i],
                      type = Pad.TYPE_SMT,
                      layers = Pad.LAYERS_SMT,
                      shape = Pad.SHAPE_RECT)
            fp.append(pad)
            n = n + 1

    ############################################################################
    # Holes
    if 'holes' in param:
        for p in param['holes']:
            h = [Pad(number = config['mounting_pad_number'] if 'ring' in p else "",
                     at = (m*p['space']/2, p['y']),
                     drill = p['drill'],
                     size = p['drill']+p['ring'] if 'ring' in p else p['drill'],
                     type = Pad.TYPE_THT if 'ring' in p else Pad.TYPE_NPTH,
                     layers = Pad.LAYERS_THT if 'ring' in p else Pad.LAYERS_NPTH,
                     shape = Pad.SHAPE_CIRCLE) for m in (-1,1)]
            fp.append(h[0])
            fp.append(h[1])

    ############################################################################
    # Fabrication layer: F.Fab
    fab_line = config['fab_line_width']
    fab_mark = pitch #config['fab_pin1_marker_length']
    fab_width = param['layout']['width'] if 'width' not in param else param['width']
    fab_height = param['layout']['height']
    fab_y = fab_height / 2
    lEdge = -fab_width / 2
    rEdge = lEdge + fab_width
    chamfer = fab_height / 4 # 1/4 connector height, cosmetic only

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
                              y = (fab_mark-fab_height) / 2,
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
                              y = (fab_height-fab_mark) / 2,
                              width = fab_mark,
                              layer = "F.Fab",
                              close = False,
                              line_width = fab_line))

    # Draw bank outlines
    for b in range(banks):
        mid = bank1_mid + b*bank_x
        fp.append(RectLine(start = (mid-bank_w/2, -bank_h/2),
                           end   = (mid+bank_w/2,  bank_h/2),
                           layer = "F.Fab",
                           width = fab_line))
                           
    
    ############################################################################
    # Silkscreen: F.SilkS
    #silk_offset = param['layout']['silk-offset']
    silk_offset_fab = config['silk_fab_offset']
    silk_pad = config['silk_pad_clearance'] + pad_w/2
    silk_line = config['silk_line_width']
    silk_y = fab_y + silk_offset_fab
    silk_lEdge = lEdge - silk_offset_fab
    silk_rEdge = rEdge + silk_offset_fab
    silk_chamfer = chamfer + silk_offset_fab/2
    silk_pin1 = pin1.x - silk_pad
    silk_lEnd = []
    silk_rEnd = []
    
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
        r = pad_w/4
        fp.append(Circle(center = (pin1.x, pin1.y + pad_h/2 + r + silk_pad),
                         radius = r,
                         layer  = "F.SilkS",
                         width  = 2*r))

    # Generate right end outline
    silk_rEnd = deepcopy(silk_lEnd)
    # Mirror about x axis
    for i in range(len(silk_rEnd)):
        silk_rEnd[i]['x'] = -silk_rEnd[i]['x']
    # Define right outline inner offset from the last pin
    # (if the last bank is differential, it does not perfectly mirror the first)
    silk_rEnd[0]['x'] = silk_rEnd[-1]['x'] = pin[-1][-1].x + silk_pad

    # Draw left and right end outlines
    fp.append(PolygoneLine(nodes = silk_lEnd,
                           layer = "F.SilkS",
                           width = silk_line))
    fp.append(PolygoneLine(nodes = silk_rEnd,
                           layer = "F.SilkS",
                           width = silk_line))

    # Draw outlines between banks
    for b in range(banks-1):
        fp.extend([Line(start = (pin[b][-1].x  + silk_pad, m*silk_y),
                        end   = (pin[b+1][0].x - silk_pad, m*silk_y),
                        layer = "F.SilkS",
                        width = silk_line) for m in (-1,1)])
    
    ############################################################################
    # Metadata
    
    # Part number
    if 'pn' in param:
        partnum = param['pn']
    else:
        partnum = param['name'].split('_')[1]
        
    # Pins or pairs/bank
    if param['banks']['diff'] == banks:
        # Differential mode: round up to nearest even number of pairs
        pins_or_pairs = (pins_per_bank // 3) + (pins_per_bank // 3) % 2
    else:
        pins_or_pairs = pins_per_bank

    # Description
    desc = param['description']
    desc = desc.format(pn = partnum,
                       type = mode,
                       ds = param['datasheet'],
                       pitch = pitch,
                       banks = banks,
                       pins = pins_or_pairs)
    fp.setDescription(desc)

    # Tags
    tags = param['tags']
    if 'add-tags' in param:
        tags += ' ' + param['add-tags']
    fp.setTags(tags)

    ############################################################################
    # Write kicad_mod file
    
    os.makedirs(library, exist_ok=True)
    filename = os.path.join(library, param['name'] + '.kicad_mod')
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
                        default='Connector_Samtec_QStrip.pretty',
                        help='KiCad library path')
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

    print("Library:", args.library)
    
    for path in args.files:
        print("Reading", path)
        with open(path, 'r') as stream:
            try:
                footprints = yaml.safe_load(stream)
                
                if footprints is None:
                    print(path, "empty, skipping...")
                    continue

                if '_local' in footprints:
                    del footprints['_local']
                
                for fp_name in footprints:
                    print("  - Generate {}.kicad_mod".format(fp_name))
                    fp_params = footprints.get(fp_name)
                    
                    if 'name' in fp_params:
                        print("WARNING: setting 'name' to", fp_name)
                    
                    fp_params['name'] = fp_name
                    generate_one_footprint(fp_params, config, args.library)
            except yaml.YAMLError as exc:
                print(exc)
