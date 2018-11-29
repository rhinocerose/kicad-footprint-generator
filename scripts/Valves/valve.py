#!/usr/bin/env python3

import math
import os
import sys

# load parent path of KicadModTree
sys.path.append(os.path.join(sys.path[0], "..", ".."))

from KicadModTree import *

def drawOval(f, origo_x, origo_y, scx1, scy1, scr, fl_x2, fl_y2, fl_d2, bx, by, ex, ey, lcr, lgrad, fl_a, nlayer, wLayer):
    #
    # Make mid, left
    #
    x1 = origo_x + lcr * math.cos(math.radians(lgrad - fl_a))
    y1 = origo_y + lcr * math.sin(math.radians(lgrad - fl_a))
    da = 90.0 - lgrad
    f.append(Arc(center=(round(origo_x, 2), round(origo_y, 2)), start=(round(x1, 2), round(y1, 2)), angle = round(2.0 * da, 2) , layer=nlayer, width=wLayer))
    x2 = origo_x + lcr * math.cos(math.radians((lgrad - fl_a) + 2.0 * da))
    y2 = origo_y + lcr * math.sin(math.radians((lgrad - fl_a) + 2.0 * da))
    #
    # Mirror through origo to get left mid
    #
    x5 = origo_x - (x1 - origo_x)
    y5 = origo_y - (y1 - origo_y)
    f.append(Arc(center=(round(origo_x, 2), round(origo_y, 2)), start=(round(x5, 2), round(y5, 2)), angle =  round(2.0 * da, 2) , layer=nlayer, width=wLayer))
    x6 = origo_x - (x2 - origo_x)
    y6 = origo_y - (y2 - origo_y)
    
    
    #
    # Upper
    #
    llt = math.sqrt(((scx1 - 0.0) * (scx1 - 0.0)) + ((scy1 - 0.0) * (scy1 - 0.0)))
    fl_t = math.acos(scx1 / llt) + math.radians(fl_a)
    tx = origo_x + llt * math.cos(fl_t)
    ty = origo_y + (0.0 - llt * math.sin(fl_t))
    x7 = tx + scr * math.cos(math.radians((lgrad + 270) - fl_a))
    y7 = ty + scr * math.sin(math.radians((lgrad + 270) - fl_a))
    x8 = tx + scr * math.cos(math.radians((lgrad + 270) - fl_a + (2.0 * da)))
    y8 = ty + scr * math.sin(math.radians((lgrad + 270) - fl_a + (2.0 * da)))
    f.append(Arc(center=(round(tx, 2), round(ty, 2)), start=(round(x7, 2), round(y7, 2)), angle =  round(2.0 * da, 2) , layer=nlayer, width=wLayer))
    #
    # Lower
    #
    if fl_d2 > 0.01:
        llt = math.sqrt(((fl_x2 - 0.0) * (fl_x2 - 0.0)) + ((fl_y2 - 0.0) * (fl_y2 - 0.0)))
        fl_t = math.acos(fl_x2 / llt) + math.radians(fl_a)
        tx = origo_x + llt * math.cos(fl_t)
        ty = origo_y + (0.0 - llt * math.sin(fl_t))
        x3 = tx + scr * math.cos(math.radians((lgrad + 90) - fl_a))
        y3 = ty + scr * math.sin(math.radians((lgrad + 90) - fl_a))
        x4 = tx + scr * math.cos(math.radians((lgrad + 90) - fl_a + (2.0 * da)))
        y4 = ty + scr * math.sin(math.radians((lgrad + 90) - fl_a + (2.0 * da)))
        f.append(Arc(center=(round(tx, 2), round(ty, 2)), start=(round(x3, 2), round(y3, 2)), angle =  round(2.0 * da, 2) , layer=nlayer, width=wLayer))

    f.append(Line(start=(round(x2, 2), round(y2, 2)), end=(round(x3, 2), round(y3, 2)), layer=nlayer, width=wLayer))
    f.append(Line(start=(round(x4, 2), round(y4, 2)), end=(round(x5, 2), round(y5, 2)), layer=nlayer, width=wLayer))
    f.append(Line(start=(round(x8, 2), round(y8, 2)), end=(round(x1, 2), round(y1, 2)), layer=nlayer, width=wLayer))
    f.append(Line(start=(round(x6, 2), round(y6, 2)), end=(round(x7, 2), round(y7, 2)), layer=nlayer, width=wLayer))
    
    
    lsx = origo_x + x2
    lsy = origo_y + y2
    #
    #
    #
    llt = math.sqrt(((scx1 - 0.0) * (scx1 - 0.0)) + ((scy1 - 0.0) * (scy1 - 0.0)))
    tx = origo_x + llt * math.cos(math.radians(fl_a))
    ty = origo_y + (0.0 - llt * math.sin(math.radians(fl_a)))
    x3 = scr * math.cos(math.radians((lgrad + 90) - fl_a))
    y3 = scr * math.sin(math.radians((lgrad + 90) - fl_a))
    tsx = tx + x3
    tsy = ty + y3
 #   f.append(Arc(center=(round(tx, 2), round(ty, 2)), start=(round(tsx, 2), round(tsy, 2)), angle = 2.0 * da, layer=nlayer, width=wLayer))
    #
    llt = math.sqrt(((fl_x2 - 0.0) * (fl_x2 - 0.0)) + ((fl_y2 - 0.0) * (fl_y2 - 0.0)))
    tx = origo_x + llt * math.cos(math.radians(fl_a + 180.0))
    ty = origo_y + (0.0 - llt * math.sin(math.radians(fl_a + 180.0)))
    x3 = scr * math.cos(math.radians((lgrad + 90) - fl_a))
    y3 = scr * math.sin(math.radians((lgrad + 90) - fl_a))
    bsx = tx + x3
    bsy = ty + y3
#    f.append(Arc(center=(round(tx, 2), round(ty, 2)), start=(round(bsx, 2), round(bsy, 2)), angle = 2.0 * da, layer=nlayer, width=wLayer))
    x4 = tx + scr * math.cos(math.radians(((lgrad + 90) - fl_a) + 2.0 * da))
    y4 = ty + scr * math.sin(math.radians(((lgrad + 90) - fl_a) + 2.0 * da))
    
    #
    # Draw lines between arches
    #
#    f.append(Line(start=(round(rsx, 2), round(rsy, 2)), end=(round(bsx, 2), round(bsy, 2)), layer=nlayer, width=wLayer))
#    f.append(Line(start=(round(x4, 2), round(y4, 2)), end=(round(lsx, 2), round(lsy, 2)), layer=nlayer, width=wLayer))
    
#    f.append(Arc(center=(round(x1, 2), round(y1, 2)), start=(round(x1 + txd, 2), round(y1 + tyd, 2)), angle = 2.0 * (90 - lgrad), layer=nlayer, width=wLayer))
    
#    f.append(Arc(center=(round(x1, 2), round(y1, 2)), start=(round(x2, 2), round(y2, 2)), angle = 2.0 * (90 - lgrad), layer=nlayer, width=wLayer))
#    f.append(Arc(center=(round(x1, 2), round(y1, 2)), start=(round(y2, 2), round(y2, 2)), angle = 2.0 * (90 - lgrad), layer=nlayer, width=wLayer))

def bga(args):
    footprint_name = args["name"]
    description = args["pkg_description"]
    flange = args["pkg_flange"]
    datasheet = args["pkg_datasheet"]
    D = args["pkg_D"]
    valve_offset = args["pkg_valve_offset"]
    socket_offset = args["pkg_socket_offset"]
    npth_pin = args["pkg_npth_pin"]
    center_pin = args["pkg_center_pin"]
    pin_type = args["pkg_pin_type"]
    pin_number = args["pkg_pin_number"]
    pin_arc = args["pkg_pin_arc"]
    pin_diameter = args["pkg_pin_diameter"]
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
    #
    if len(flange) > 4:
        if len(flange) > 8:
            if flange[8] > -45.0 and flange[8] < 45.0:
                yRef = origo_y - (flange[7] / 2.0) - (s1[1] * 1.2)
                yValue = origo_y + (flange[7] / 2.0) + (s1[1] * 1.2)
            else:
                yRef = origo_y - (flange[6] / 2.0) - (s1[1] * 1.2)
                yValue = origo_y + (flange[6] / 2.0) + (s1[1] * 1.2)
        else:
            yRef = origo_y - (flange[6] / 2.0) - (s1[1] * 1.2)
            yValue = origo_y + (flange[6] / 2.0) + (s1[1] * 1.2)

    wFab = 0.10
    wCrtYd = 0.05
    wSilkS = 0.12
    
    description_tot = description + ', Made by script https://github.com/pointhi/kicad-footprint-generator/scripts/Valves, ' + datasheet
    
    #
    f = Footprint(footprint_name)
    f.setDescription(description_tot)
    f.setTags("{}".format(footprint_name))
    #
    s2ddh = 0.0
    if len(socket) > 2:
        s2ddh = valve_offset[2]
        s = socket
        f.append(Model(filename="${{KISYS3DMOD}}/Valve.3dshapes/{}.wrl".format(s), offset=(socket_offset[0], socket_offset[1], socket_offset[2])))
    #
    if len(tube) > 2:
        s = tube
        f.append(Model(filename="${{KISYS3DMOD}}/Valve.3dshapes/{}.wrl".format(s), offset=(valve_offset[0], valve_offset[1], s2ddh)))
    #
    if len(socket) == 0 and len(tube) == 0:
        f.append(Model(filename="${{KISYS3DMOD}}/Valve.3dshapes/{}.wrl".format(footprint_name), offset=(0,0,0)))

    #

    # Text
    #
    f.append(Text(type="reference", text="REF**",       at=[round(origo_x, 2), round(yRef, 2)],     layer="F.SilkS",    size=s1, thickness=t1))
    f.append(Text(type="value", text=footprint_name,    at=[round(origo_x, 2), round(yValue, 2)],   layer="F.Fab",      size=s1, thickness=t1))
    #
    f.append(Text(type="user", text="%R",               at=[round(origo_x, 2), round(origo_y, 2)],  layer="F.Fab",      size=s2, thickness=t2))

    if len(flange) < 1:
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

    if len(npth_pin) > 0:
        for n in npth_pin:
            #
            # Add npth hole
            #
            f.append(Pad(number="", 
                    type=Pad.TYPE_NPTH,
                    shape=Pad.SHAPE_CIRCLE,
                    at=[round(n[0], 2), round(n[1], 2)],
                    size=n[2],
                    layers=Pad.LAYERS_THT, 
                    drill=n[2],
                    radius_ratio=0.25))
            
        
                    

    if len(flange) > 4:
        #
        #   pkg_flange: [14.25, 0, 1.3, 0, 0, 0, 35.5, 26.5, 72]        # "npth hole 1 x-pos, y-pos, diameter", "npth hole 2 x-pos, y-pos, diameter", width, length of flange, rotation in degree of flange
        #
        fl_x1 = flange[0]
        fl_y1 = flange[1]
        fl_d1 = flange[2]
        fl_x2 = flange[3]
        fl_y2 = flange[4]
        fl_d2 = flange[5]
        fl_w = flange[6]
        fl_l = flange[7]
        fl_a = flange[8]
        
        #
        # Add right npth hole
        #
        if fl_d1 > 0.01:
            llt = math.sqrt(((fl_x1 - 0.0) * (fl_x1 - 0.0)) + ((fl_y1 - 0.0) * (fl_y1 - 0.0)))
            x3 = origo_x + llt * math.cos(math.radians(fl_a))
            y3 = origo_y + (0.0 - llt * math.sin(math.radians(fl_a)))
#            print("x3 " + str(x3))
#            print("y3 " + str(y3))
            #
            f.append(Pad(number="", 
                    type=Pad.TYPE_NPTH,
                    shape=Pad.SHAPE_CIRCLE,
                    at=[round(x3, 2), round(y3, 2)],
                    size=fl_d1,
                    layers=Pad.LAYERS_THT, 
                    drill=fl_d1,
                    radius_ratio=0.25))
                    
        if fl_d2 > 0.01:
            #
            # Add right npth hole
            #
            llt = math.sqrt(((fl_x2 - 0.0) * (fl_x2 - 0.0)) + ((fl_y2 - 0.0) * (fl_y2 - 0.0)))
            x3 = origo_x + llt * math.cos(math.radians(fl_a + 180.0))
            y3 = origo_y + (0.0 - llt * math.sin(math.radians(fl_a + 180.0)))
#            print("x3 " + str(x3))
#            print("y3 " + str(y3))
            #
            f.append(Pad(number="", 
                    type=Pad.TYPE_NPTH,
                    shape=Pad.SHAPE_CIRCLE,
                    at=[round(x3, 2), round(y3, 2)],
                    size=fl_d2,
                    layers=Pad.LAYERS_THT, 
                    drill=fl_d2,
                    radius_ratio=0.25))
        # 
        # Calculate it around origo so it can be easily rotated
        #
        #
        # Large circle
        #
        lcr = fl_l / 2.0    # radie
        lcx1 = 0.0
        lcy1 = 0.0
#        f.append(Circle(center=(round(lcx1, 2), round(lcy1, 2)), radius=round(lcr, 2), layer="F.CrtYd", width=wCrtYd))
        #
        # Small circle
        #
        scr = ((fl_w / 2.0) - fl_x1) # radie
        scx1 = fl_x1
        scy1 = fl_y1
#        f.append(Circle(center=(round(scx1, 2), round(scy1, 2)), radius=round(scr, 2), layer="F.CrtYd", width=wCrtYd))
        #
        # Calculate the line between the bigger circle and the small
        #
        lgrad = -1.0
        ex = -1.0
        ey = -1.0
        bx = -1.0
        by = -1.0
        circle_hit = False
        nums = 84
        grad_step_start = 20.0
        grad_step = (90.0 - grad_step_start) / nums
        grad = grad_step_start
        for i in range(1, nums):
            #
            # start point on the circle
            #
            x1 = lcr * math.cos(math.radians(grad))
            y1 = lcr * math.sin(math.radians(grad))
            # Calculate the straigt line equation for the tangent
            #
            slope_of_radius = (y1 - 0) / (x1 - 0)
            k = 0 - (1.0 / slope_of_radius)
            m = y1 - (k * x1)
            #
#            x4 = x3 + 10
#            y4 = k * x3 + m
#            f.append(Line(start=(round(x3, 2), round(y3, 2)), end=(round(x4, 2), round(y4, 2)), layer="F.SilkS", width=0.05))
            # k and m is the straight line equation of the tangent 
            #
            # Calculate the distance fform the point of the larger circle to the smaller origo
            #
            llt = math.sqrt(((scx1 - x1) * (scx1 - x1)) + ((scy1 - y1) * (scy1 - y1)))
            x2 = x1 + (llt * math.cos(math.radians(grad)))
            y2 = k * x2 + m
#            f.append(Line(start=(round(x1, 2), round(y1, 2)), end=(round(x2, 2), round(y2, 2)), layer="F.SilkS", width=0.05))
            #
            # Check which lines ends up in the smaller circle
            #
            llt = math.sqrt(((scx1 - x2) * (scx1 - x2)) + ((scy1 - y2) * (scy1 - y2)))
            if llt < scr:
#                f.append(Line(start=(round(x4, 2), round(y4, 2)), end=(round(x5, 2), round(y5, 2)), layer="F.SilkS", width=0.05))
#                f.append(Line(start=(round(x4, 2), round(y4, 2)), end=(round(x1, 2), round(y1, 2)), layer="F.SilkS", width=0.05))
                #
                # Save the latest one that hitted
                #
                lgrad = grad
                bx = x1
                by = y1
                ex = scx1 + (scr * math.cos(math.radians(grad)))
                ey = scy1 + (scr * math.sin(math.radians(grad)))
                circle_hit = True
                
            grad = grad + grad_step
        #
#            f.append(Line(start=(round(bx, 2), round(by, 2)), end=(round(ex, 2), round(ey, 2)), layer="F.SilkS", width=0.05))
        #
        drawOval(f, origo_x, origo_y, scx1, scy1, scr, fl_x2, fl_y2, fl_d2, bx, by, ex, ey, lcr, lgrad, fl_a, "F.Fab", wFab)
        drawOval(f, origo_x, origo_y, scx1, scy1, scr + 0.13, fl_x2, fl_y2, fl_d2 + 0.13, bx, by, ex, ey, lcr + 0.13, lgrad, fl_a, "F.SilkS", wSilkS)
        drawOval(f, origo_x, origo_y, scx1, scy1, scr + 0.25, fl_x2, fl_y2, fl_d2 + 0.25, bx, by, ex, ey, lcr + 0.25, lgrad, fl_a, "F.CrtYd", wCrtYd)
        #
        bx = (lcr + 0.13) * math.cos(math.radians(grad))
        by = (lcr + 0.13) * math.sin(math.radians(grad))
        ex = (scr + 0.13) * math.cos(math.radians(grad))
        ey = (scr + 0.13) * math.sin(math.radians(grad))
#        drawOval(f, origo_x, origo_y, scx1, scy1, scr, fl_x2, fl_y2, fl_d2, bx, by, ex, ey, lcr, lgrad, fl_a, "F.SilkS", wSilkS)
        #
        bx = (lcr + 0.25) * math.cos(math.radians(grad))
        by = (lcr + 0.25) * math.sin(math.radians(grad))
        ex = (scr + 0.25) * math.cos(math.radians(grad))
        ey = (scr + 0.25) * math.sin(math.radians(grad))
 #       drawOval(f, origo_x, origo_y, scx1, scy1, scr, fl_x2, fl_y2, fl_d2, bx, by, ex, ey, lcr, lgrad, fl_a, "F.CrtYd", wCrtYd)
        
                    
    file_handler = KicadFileHandler(f)
    file_handler.writeFile(footprint_name + ".kicad_mod")

if __name__ == '__main__':
    parser = ModArgparser(bga)
    # the root node of .yml files is parsed as name
    parser.add_parameter("name",                type=str,   required=True)
    parser.add_parameter("pkg_description",     type=str,   required=True)
    parser.add_parameter("pkg_datasheet",       type=str,   required=True)
    parser.add_parameter("pkg_flange",          type=list,  required=True)
    parser.add_parameter("pkg_D",               type=float, required=True)
    parser.add_parameter("pkg_valve_offset",    type=list,  required=True)
    parser.add_parameter("pkg_socket_offset",   type=list,  required=True)
    parser.add_parameter("pkg_npth_pin",        type=list,  required=True)
    parser.add_parameter("pkg_center_pin",      type=list,  required=True)
    parser.add_parameter("pkg_pin_type",        type=list,  required=True)
    parser.add_parameter("pkg_pin_number",      type=int,   required=True)
    parser.add_parameter("pkg_pin_arc",         type=float, required=False)
    parser.add_parameter("pkg_pin_diameter",    type=float, required=False)
    parser.add_parameter("pkg_socket",          type=str,   required=False)
    parser.add_parameter("pkg_tube",            type=str,   required=False)
    
    # now run our script which handles the whole part of parsing the files
    parser.run()
