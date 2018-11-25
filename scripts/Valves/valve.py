#!/usr/bin/env python3

import math
import os
import sys

# load parent path of KicadModTree
sys.path.append(os.path.join(sys.path[0], "..", ".."))

from KicadModTree import *

def bga(args):
    footprint_name = args["name"]
    description = args["pkg_description"]
    datasheet = args["pkg_datasheet"]
    D = args["pkg_D"]
    pkg_valve_offset = args["pkg_valve_offset"]
    pkg_socket_offset = args["pkg_socket_offset"]
    npth_pin = args["pkg_npth_pin"]
    center_pin = args["pkg_center_pin"]
    pin_type = args["pkg_pin_type"]
    pin_number = args["pkg_pin_number"]
    pin_arc = args["pkg_pin_arc"]
    pin_diameter = args["pkg_pin_diameter"]
    npth_pin = args["pkg_npth_pin"]
    socket = args["pkg_socket"]
    tube = args["pkg_tube"]

    socket
    
    alpha_delta = 0 - ((pin_arc * math.pi) / 180.0)
    h = pin_diameter / 2.0
    origo_dx = (h * math.sin(alpha_delta))
    origo_dy = (h * math.cos(alpha_delta))
    
    origo_x = 0 - origo_dx
    origo_y = origo_dy
    
    s1 = [1.0, 1.0]
    s2 = [1.0, 1.0]
    
    t1 = 0.15 * s1[0]
    t2 = 0.15 * s2[0]

    yRef = origo_y - (D / 2.0) - (s1[1] * 1.2)
    yValue = origo_y + (D / 2.0) + (s1[1] * 1.2)

    wFab = 0.10
    wCrtYd = 0.05
    wSilkS = 0.12
    
    description_tot = description + ', Made by script https://github.com/pointhi/kicad-footprint-generator/scripts/Valves, ' + datasheet
    
    #
    f = Footprint(footprint_name)
    f.setDescription(description_tot)
    f.setTags("{}".format(footprint_name))
    #
    s = socket
    f.append(Model(filename="${{KISYS3DMOD}}/Valve.3dshapes/{}.wrl".format(s), offset=(pkg_socket_offset[0], pkg_socket_offset[1], pkg_socket_offset[2])))
    #
    s = tube
    f.append(Model(filename="${{KISYS3DMOD}}/Valve.3dshapes/{}.wrl".format(s), offset=(pkg_valve_offset[0], pkg_valve_offset[1], pkg_valve_offset[2])))
    # Text
    f.append(Text(type="reference", text="REF**",       at=[round(origo_x, 2), round(yRef, 2)],     layer="F.SilkS",    size=s1, thickness=t1))
    f.append(Text(type="value", text=footprint_name,    at=[round(origo_x, 2), round(yValue, 2)],   layer="F.Fab",      size=s1, thickness=t1))
    f.append(Text(type="user", text="%R",               at=[round(origo_x, 2), round(origo_y, 2)],  layer="F.Fab",      size=s2, thickness=t2))

    # Fab
    f.append(Circle(center=(round(origo_x, 2), round(origo_y, 2)), radius=round((D / 2.0), 2), layer="F.Fab", width=wFab))

    # Courtyard
    f.append(Circle(center=(round(origo_x, 2), round(origo_y, 2)), radius=round((D / 2.0) + 0.12, 2), layer="F.CrtYd", width=wCrtYd))

    # Silk
    f.append(Circle(center=(round(origo_x, 2), round(origo_y, 2)), radius=round((D / 2.0) + 0.25, 2), layer="F.SilkS", width=wSilkS))

    pad_size = round(pin_type[1] * 1.7, 1)
    pad_drill = round(pin_type[1] * 1.1, 1)
    alpha = alpha_delta
    pad_shape = Pad.SHAPE_RECT
    if pin_type[0] == 'tap':
        pad_size = [round(pin_type[1] * 1.7, 1), round(pin_type[2] * 1.7, 1)]
        pad_drill = [round(pin_type[1] * 1.1, 1), round(pin_type[2] * 1.1, 1)]
        pad_shape = Pad.SHAPE_OVAL
    #
    pad_type = Pad.TYPE_THT
    pad_layers = Pad.LAYERS_THT
    for i in range(0, pin_number):
        x1 = (h * math.sin(alpha)) + origo_x
        y1 = (h * math.cos(alpha)) - origo_y

        rotation = 0.0
        if pin_type[0] == 'tap':
            rotation = 360.0 - (alpha * (360.0 / (2.0 * math.pi)))
        #
        f.append(Pad(number="{}".format(i+1), 
                    type=pad_type,
                    shape=pad_shape,
                    at=[round(x1, 2), round((0 - y1), 2)],
                    size=pad_size,
                    layers=pad_layers, 
                    rotation=rotation,
                    drill=pad_drill,
                    radius_ratio=0.25))
        #
        pad_shape = Pad.SHAPE_ROUNDRECT
        if pin_type[0] == 'tap':
            pad_shape = Pad.SHAPE_OVAL
        alpha = alpha + alpha_delta

    if len(center_pin) > 0:
        if center_pin[0] == "metal":
            f.append(Pad(number="{}".format(pin_number + 1), 
                    type=pad_type,
                    shape=pad_shape,
                    at=[round(origo_x, 2), round(origo_y, 2)],
                    size=pad_size,
                    layers=pad_layers, 
                    drill=pad_drill,
                    radius_ratio=0.25))
                         
    file_handler = KicadFileHandler(f)
    file_handler.writeFile(footprint_name + ".kicad_mod")

if __name__ == '__main__':
    parser = ModArgparser(bga)
    # the root node of .yml files is parsed as name
    parser.add_parameter("name",                type=str,   required=True)
    parser.add_parameter("pkg_description",     type=str,   required=True)
    parser.add_parameter("pkg_datasheet",       type=str,   required=True)
    parser.add_parameter("pkg_D",               type=float, required=True)
    parser.add_parameter("pkg_valve_offset",    type=list, required=True)
    parser.add_parameter("pkg_socket_offset",   type=list, required=True)
    parser.add_parameter("pkg_npth_pin",        type=list,  required=True)
    parser.add_parameter("pkg_center_pin",      type=list,  required=True)
    parser.add_parameter("pkg_pin_type",        type=list,  required=True)
    parser.add_parameter("pkg_pin_number",      type=int,   required=True)
    parser.add_parameter("pkg_pin_arc",         type=float, required=True)
    parser.add_parameter("pkg_pin_diameter",    type=float, required=True)
    parser.add_parameter("pkg_socket",          type=str,   required=True)
    parser.add_parameter("pkg_tube",            type=str,   required=True)
    
    # now run our script which handles the whole part of parsing the files
    parser.run()
