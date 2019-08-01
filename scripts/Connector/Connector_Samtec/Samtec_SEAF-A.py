#!/usr/bin/env python3

import math
import os
import sys
import argparse
import yaml

# load parent path of KicadModTree
sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))

from KicadModTree import *  # NOQA
from KicadModTree.nodes.base.Pad import Pad  # NOQA
sys.path.append(os.path.join(sys.path[0], "..", "..", "tools"))  # load parent path of tools

from KicadModTree import *
import itertools
from string import ascii_uppercase

def generateFootprint(config, fpParams, fpId):
    # Common parameters for all types
    size_source = "http://suddendocs.samtec.com/prints/seaf-xx-xx.x-xx-xx-x-a-xx-k-tr-mkt.pdf"
    pitchX = 1.27
    pitchY = pitchX
    pitchString = str(pitchX) + "x" + str(pitchY)
    pad_diameter = 0.64
#  pad_x_center_offset: 0.0
#  pad_y_center_offset: 0.0
    mask_margin = 0.0
    paste_margin = 0.12
    paste_ratio = 0.0
    layout_x = 10
    layout_y = 4
    npth_drill = 1.27
    pth_drill = 0.99
    pth_distance = 2.97
    
    
    print('Building footprint for parameter set: {}'.format(fpId))
    
    if fpParams["family"] == "SEAF":
        # define the correct pin-order here according datasheet
        # tlbr = top left to bottom right
        # trbl = top right to bottom left
        # bltr = bottom left to top right
        # brtl = bottom right to top left
        pin_order = "brtl"
        # Parameters for SEAF-A and SEAF-A-LP used from datasheet
        tab_DIM_A = [[10, 15, 19, 20, 25, 30, 40, 50],
                 [11.43, 17.78, 22.86, 24.13, 30.48, 36.83, 49.53, 62.23]]
        tab_DIM_B = [[10, 15, 19, 20, 25, 30, 40, 50],
                 [16.28, 22.63, 27.71, 28.98, 35.33, 41.68, 54.38, 67.08]]
        tab_DIM_C = [[4, 5, 6, 8, 10, 14],
                 [5.66,  8.20,  8.20, 10.74, 13.28, 18.36]]
        tab_DIM_D = [[4, 5, 6, 8, 10, 14],
                 [3.81, 5.08, 6.35, 8.89, 11.43, 16.51]]
        tab_DIM_E = [[4, 5, 6, 8, 10, 14],
                 [2.01, 3.05, 3.05, 3.05, 3.05, 3.05]]
        tab_DIM_F = [[4, 5, 6, 8, 10, 14],
                 [3.20, 5.69, 5.69, 3.20, 5.69, 5.69]]
        tab_DIM_G = [[4, 5, 6, 8, 10, 14],
                 [1.35, 0.84, 0.84, 0.84, 0.84, 0.84]]
        tab_DIM_H = [[10, 15, 19, 20, 25, 30, 40, 50],
                 [32.05, 38.40, 43.48, 44.75, 51.10, 57.45, 70.15, 82.85]]
        tab_DIM_J = [[10, 15, 19, 20, 25, 30, 40, 50],
                 [26.24, 32.59, 37.67, 38.94, 45.29, 51.64, 64.34, 77.04]]
        len_REF_A = 3.96
        len_REF_B = 3.12
        len_REF_C = 5.61
        # Read the number of positions (a.k.a. number of pins of an row )
        layoutX = fpParams["no_pins_of_row"]
        # Read the number of rows
        layoutY = fpParams["no_of_rows"]

        pkg_REF_A = len_REF_A
        pkg_REF_B = len_REF_B
        pkg_REF_C = len_REF_C
        
        
        if fpParams["design"] == "A":
            pkg_DIM_A = getTableEntry(tab_DIM_A, layoutX)
            if pkg_DIM_A == -1:
                print('Error, no_pins_of_row = {} does not exist in tab_DIM_A-list'.format(fpParams["no_pins_of_row"]))
                sys.exit()
            pkg_DIM_B = getTableEntry(tab_DIM_B, layoutX)
            if pkg_DIM_B == -1:
                print('Error, no_pins_of_row = {} does not exist in tab_DIM_B-list'.format(fpParams["no_pins_of_row"]))
                sys.exit()
            pkg_DIM_C = getTableEntry(tab_DIM_C, layoutY)
            if pkg_DIM_C == -1:
                print('Error, no_of_rows = {} does not exist in tab_DIM_C-list'.format(fpParams["no_of_rows"]))
                sys.exit()
            pkg_DIM_D = getTableEntry(tab_DIM_D, layoutY)
            if pkg_DIM_D == -1:
                print('Error, no_of_rows = {} does not exist in tab_DIM_D-list'.format(fpParams["no_of_rows"]))
                sys.exit()
            pkg_DIM_E = getTableEntry(tab_DIM_E, layoutY)
            if pkg_DIM_E == -1:
                print('Error, no_of_rows = {} does not exist in tab_DIM_E-list'.format(fpParams["no_of_rows"]))
                sys.exit()
            pkg_DIM_F = getTableEntry(tab_DIM_F, layoutY)
            if pkg_DIM_F == -1:
                print('Error, no_of_rows = {} does not exist in tab_DIM_F-list'.format(fpParams["no_of_rows"]))
                sys.exit()
            pkg_DIM_G = getTableEntry(tab_DIM_G, layoutY)
            if pkg_DIM_G == -1:
                print('Error, no_of_rows = {} does not exist in tab_DIM_G-list'.format(fpParams["no_of_rows"]))
                sys.exit()
            pkg_DIM_H = getTableEntry(tab_DIM_H, layoutX)
            if pkg_DIM_H == -1:
                print('Error, no_pins_of_row = {} does not exist in tab_DIM_H-list'.format(fpParams["no_pins_of_row"]))
                sys.exit()
            pkg_DIM_J = getTableEntry(tab_DIM_J, layoutX)
            if pkg_DIM_J == -1:
                print('Error, no_pins_of_row = {} does not exist in tab_DIM_J-list'.format(fpParams["no_pins_of_row"]))
                sys.exit()    

    #layoutX = fpParams["layout_x"]
    #layoutY = fpParams["layout_y"]
    
    if "additional_tags" in fpParams:
        additionalTag = " " + fpParams["additional_tags"]
    else:
        additionalTag = ""
    
    if "row_names" in fpParams:
        rowNames = fpParams["row_names"]
    else:
        rowNames = config['row_names']
    
    if "row_skips" in fpParams:
        rowSkips = fpParams["row_skips"]
    else:
        rowSkips = []

    # must be given pitch (equal in X and Y) or a unique pitch in both X and Y
    #if "pitch" in fpParams:
    #    if "pitch_x" and "pitch_y" in fpParams:
    #        raise KeyError('{}: Either pitch or both pitch_x and pitch_y must be given.'.format(fpId))
    #    else:
    #        pitchString = str(fpParams["pitch"])
    #        pitchX = fpParams["pitch"]
    #        pitchY = fpParams["pitch"]
    #else:
    #    if "pitch_x" and "pitch_y" in fpParams:
    #        pitchString = str(fpParams["pitch_x"]) + "x" + str(fpParams["pitch_y"])
    #        pitchX = fpParams["pitch_x"]
    #        pitchY = fpParams["pitch_y"]
    #    else:
    #        raise KeyError('{}: Either pitch or both pitch_x and pitch_y must be given.'.format(fpId))

    f = Footprint(fpId)
    f.setAttribute("smd")
    if "mask_margin" in fpParams: f.setMaskMargin(fpParams["mask_margin"])
    if "paste_margin" in fpParams: f.setPasteMargin(fpParams["paste_margin"])
    if "paste_ratio" in fpParams: f.setPasteMarginRatio(fpParams["paste_ratio"])

    s1 = [1.0, 1.0]
    s2 = [min(1.0, round((pkg_REF_A + pkg_DIM_A + pkg_REF_B) / 4.3, 2))] * 2

    t1 = 0.15 * s1[0]
    t2 = 0.15 * s2[0]

    padShape = Pad.SHAPE_CIRCLE
    if "pad_shape" in fpParams:
        if fpParams["pad_shape"] == "rect":
            padShape = Pad.SHAPE_RECT
        if fpParams["pad_shape"] == "roundrect":
            padShape = Pad.SHAPE_ROUNDRECT

    #chamfer = min(config['fab_bevel_size_absolute'], min(pkgX, pkgY) * config['fab_bevel_size_relative'])
    
    silkOffset = config['silk_fab_offset']
    crtYdOffset = config['courtyard_offset']['connector']
    
    def crtYdRound(x):
        # Round away from zero for proper courtyard calculation
        neg = x < 0
        if neg:
            x = -x
        x = math.ceil(x * 100) / 100.0
        if neg:
            x = -x
        return x

    xCenter = 0.0
    yCenter = 0.0

    # Caution: We draw the footprint 180° rotated than in datasheet, simplifing the PAD placement algorithm

    # Generating Points for the "Fab"-layer (fabrication)
    P1XFab = xCenter - ((pkg_DIM_A / 2.0) + pkg_REF_A)
    P1YFab = yCenter - (pkg_DIM_C / 2.0)
    
    P2XFab = xCenter + ((pkg_DIM_A / 2.0) + pkg_REF_B)
    P2YFab = P1YFab
    
    P3XFab = P2XFab
    P3YFab = yCenter - (pkg_DIM_F / 2.0)
    
    P4XFab = xCenter + ((pkg_DIM_A / 2.0) + pkg_REF_B + pkg_DIM_G)
    P4YFab = P3YFab
    
    P5XFab = P4XFab
    P5YFab = yCenter + (pkg_DIM_F / 2.0)
    
    
    P6XFab = P3XFab
    P6YFab = P5YFab
    
    P7XFab = P6XFab
    P7YFab = yCenter + (pkg_DIM_C / 2.0)
    
    P8XFab = P1XFab
    P8YFab = P7YFab
    

    # Generating Points for the "crtYd"-layer (courty yard)
    P1XcrtYd = crtYdRound(xCenter - ((pkg_DIM_A / 2.0) + pkg_REF_A + crtYdOffset))
    P1YcrtYd = crtYdRound(yCenter - ((pkg_DIM_C / 2.0) + crtYdOffset))
        
    P2XcrtYd = crtYdRound(xCenter + ((pkg_DIM_A / 2.0) + pkg_REF_B + pkg_DIM_G + crtYdOffset))
    P2YcrtYd = P1YcrtYd
    
    P3XcrtYd = P2XcrtYd
    P3YcrtYd = crtYdRound(yCenter + ((pkg_DIM_C / 2.0) + crtYdOffset))
    
    P4XcrtYd = P1XcrtYd
    P4YcrtYd = P3YcrtYd

    # Generating Points for the "Silk"-layer (silkscreed)
    P1XSilk = P1XFab - silkOffset
    P1YSilk = P1YFab - silkOffset
    
    P2XSilk = P2XFab + silkOffset
    P2YSilk = P1YSilk
    
    P3XSilk = P2XSilk
    P3YSilk = P3YFab - silkOffset
    
    P4XSilk = P4XFab + silkOffset
    P4YSilk = P3YSilk
    
    P5XSilk = P4XSilk
    P5YSilk = P5YFab + silkOffset
    
    
    P6XSilk = P3XSilk
    P6YSilk = P6YFab + silkOffset
    
    P7XSilk = P6XSilk
    P7YSilk = P7YFab + silkOffset
    
    P8XSilk = P1XSilk
    P8YSilk = P7YSilk

    # Define the position of pads to be placed
    xPadLeft = xCenter - pitchX * ((layoutX - 1) / 2.0)
    xPadRight = xCenter + pitchX * ((layoutX - 1) / 2.0)
    yPadTop = yCenter - pitchY * ((layoutY - 1) / 2.0)
    yPadBottom = yCenter + pitchY * ((layoutY - 1) / 2.0)

    # Define the position of the REF** in silkscreen
    xRefSilk = xCenter
    yRefSilk = P1YFab - 2.0

    # Define the position of the REF** in fabrication
    xRefFab = xCenter
    yRefFab = yCenter

    # Define the position of the VALUE in fabrication
    xValueFab = xCenter
    yValueFab = P4YFab + 2.0

    

    wFab = configuration['fab_line_width']
    wCrtYd = configuration['courtyard_line_width']
    wSilkS = configuration['silk_line_width']

    # Text
    f.append(Text(type="reference", text="REF**", at=[xRefSilk, yRefSilk], layer="F.SilkS", size=s1, thickness=t1))

    f.append(Text(type="value", text=fpId, at=[xValueFab, yValueFab], layer="F.Fab", size=s1, thickness=t1))

    f.append(Text(type="user", text="%R", at=[xRefFab, yRefFab], layer="F.Fab", size=s2, thickness=t2))

    # Fab
    f.append(PolygoneLine(polygone=[[P1XFab, P1YFab],
                                    [P2XFab, P2YFab],
                                    [P3XFab, P3YFab],
                                    [P4XFab, P4YFab],
                                    [P5XFab, P5YFab],
                                    [P6XFab, P6YFab],
                                    [P7XFab, P7YFab],
                                    [P8XFab, P8YFab],
                                    [P1XFab, P1YFab]],
                          layer="F.Fab", width=wFab))

    # Courtyard
    f.append(RectLine(start=[P1XcrtYd, P1YcrtYd],
                      end=[P3XcrtYd, P3YcrtYd],
                      layer="F.CrtYd", width=wCrtYd))

    # Silk
    f.append(PolygoneLine(polygone=[[P1XSilk, P1YSilk],
                                    [P2XSilk, P2YSilk],
                                    [P3XSilk, P3YSilk],
                                    [P4XSilk, P4YSilk],
                                    [P5XSilk, P5YSilk],
                                    [P6XSilk, P6YSilk],
                                    [P7XSilk, P7YSilk],
                                    [P8XSilk, P8YSilk],
                                    [P1XSilk, P1YSilk]],
                          layer="F.SilkS", width=wSilkS))

    
    
    # Pads generated according pin_order
    # tlbr = top left to bottom right
    # trbl = top right to bottom left
    # bltr = bottom left to top right
    # brtl = bottom right to top left
    pad_array_size = layoutX * layoutY
    if rowSkips == []:
        for _ in range(layoutY):
            rowSkips.append([])
    for rowNum, row in zip(range(layoutY), rowNames):
        rowSet = set(range(1, layoutX + 1))
        for item in rowSkips[rowNum]:
            try:
                # If item is a range, remove that range
                rowSet -= set(range(*item))
                pad_array_size -= item[1] - item[0]
            except TypeError:
                # If item is an int, remove that int
                rowSet -= {item}
                pad_array_size -= 1
        for col in rowSet:
            if pin_order == "tlbr":            
                f.append(Pad(number="{}{}".format(row, col), type=Pad.TYPE_SMT,
                         shape=padShape,
                         at=[xPadLeft + (col-1) * pitchX, yPadTop + rowNum * pitchY],
                         size=[pad_diameter, pad_diameter],
                         layers=Pad.LAYERS_SMT, 
                         radius_ratio=config['round_rect_radius_ratio']))
            elif pin_order == "trbl":
                f.append(Pad(number="{}{}".format(row, col), type=Pad.TYPE_SMT,
                         shape=padShape,
                         at=[xPadRight - (col-1) * pitchX, yPadTop + rowNum * pitchY],
                         size=[pad_diameter, pad_diameter],
                         layers=Pad.LAYERS_SMT, 
                         radius_ratio=config['round_rect_radius_ratio']))
            elif pin_order == "bltr":
                f.append(Pad(number="{}{}".format(row, col), type=Pad.TYPE_SMT,
                         shape=padShape,
                         at=[xPadLeft + (col-1) * pitchX, yPadBottom - rowNum * pitchY],
                         size=[pad_diameter, pad_diameter],
                         layers=Pad.LAYERS_SMT, 
                         radius_ratio=config['round_rect_radius_ratio']))
            elif pin_order == "brtl":
                f.append(Pad(number="{}{}".format(row, col), type=Pad.TYPE_SMT,
                         shape=padShape,
                         at=[xPadRight - (col-1) * pitchX, yPadBottom - rowNum * pitchY],
                         size=[pad_diameter, pad_diameter],
                         layers=Pad.LAYERS_SMT, 
                         radius_ratio=config['round_rect_radius_ratio']))
            else:
                print('Error, pin_order = {} does not exist.'.format(pin_order))
                sys.exit()
                



    # Placement Holes NPTH
    P1XPlacementHole = xCenter - (pkg_DIM_B / 2.0)
    P1YPlacementHole = yCenter

    f.append(Pad(at=[P1XPlacementHole, P1YPlacementHole], number="",
                    type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, size=npth_drill,
                    drill=npth_drill, layers=Pad.LAYERS_NPTH))

    P2XPlacementHole = xCenter + (pkg_DIM_B / 2.0)
    P2YPlacementHole = yCenter + pkg_DIM_E

    f.append(Pad(at=[P2XPlacementHole, P2YPlacementHole], number="",
                    type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, size=npth_drill,
                    drill=npth_drill, layers=Pad.LAYERS_NPTH))

    ########################### Pin 1 - Marker #################################
    markerOffset = 0.4
    markerLength = pad_diameter
    
    P1XMarker = xPadRight
    P1YMarker = P7YSilk + markerOffset
    
    P2XMarker = P1XMarker - (markerLength / 2)
    P2YMarker = P1YMarker + (markerLength / sqrt(2))
    
    P3XMarker = P2XMarker + markerLength
    P3YMarker = P2YMarker
    
    # Silk
    f.append(PolygoneLine(polygone=[[P1XMarker, P1YMarker],
                                    [P2XMarker, P2YMarker],
                                    [P3XMarker, P3YMarker],
                                    [P1XMarker, P1YMarker]],
                          layer="F.SilkS", width=wSilkS))

    # Prepare name variables for footprint folder, footprint name, etc.
    familiyType = fpParams['family']
    packageType = fpId

    f.append(Model(filename="{}Connector_Samtec_{}.3dshapes/{}.wrl".format(
                  config['3d_model_prefix'], familiyType, fpId)))

    f.setDescription("{0}, {1}x{2}mm, {3} Ball, {4}x{5} Layout, {6}mm Pitch, {7}".format(fpId, (pkg_REF_A + pkg_DIM_C + pkg_REF_B + pkg_DIM_G) , pkg_DIM_C, pad_array_size, layoutX, layoutY, pitchString, size_source))
    f.setTags("{} {} {}{}".format(packageType, pad_array_size, pitchString, additionalTag))

    outputDir = 'Connector_Samtec_{lib_name:s}.pretty/'.format(lib_name=familiyType)
    if not os.path.isdir(outputDir): #returns false if path does not yet exist!! (Does not check path validity)
        os.makedirs(outputDir)
    filename = '{outdir:s}{fpId:s}.kicad_mod'.format(outdir=outputDir, fpId=fpId)
    
    file_handler = KicadFileHandler(f)
    file_handler.writeFile(filename)

def rowNameGenerator(seq):
    for n in itertools.count(1):
        for s in itertools.product(seq, repeat = n):
            yield ''.join(s)

def getTableEntry(table, layout):
    pkg_val = -1
    for i in range(len(table[0])):
        #print('{}'.format(table[0][i]))
        if table[0][i] == layout:
            pkg_val = table[1][i]
            break; # quit the for-loop when a correct match is made to reduce script duration time
    return pkg_val
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='use confing .yaml files to create footprints.')
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='list of files holding information about what devices should be created.')
    parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='../../tools/global_config_files/config_KLCv3.0.yaml')
    # parser.add_argument('--series_config', type=str, nargs='?', help='the config file defining series parameters.', default='../package_config_KLCv3.yaml')

    args = parser.parse_args()
    
    with open(args.global_config, 'r') as config_stream:
        try:
            configuration = yaml.safe_load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    # with open(args.series_config, 'r') as config_stream:
        # try:
            # configuration.update(yaml.safe_load(config_stream))
        # except yaml.YAMLError as exc:
            # print(exc)
    
    # generate dict of A, B .. Y, Z, AA, AB .. CY less easily-confused letters
    rowNamesList = [x for x in ascii_uppercase if x not in ["I", "O", "Q", "S", "X", "Z"]]
    configuration.update({'row_names': list(itertools.islice(rowNameGenerator(rowNamesList), 80))})

    for filepath in args.files:
        with open(filepath, 'r') as command_stream:
            try:
                cmd_file = yaml.safe_load(command_stream)
            except yaml.YAMLError as exc:
                print(exc)
        for pkg in cmd_file:
            generateFootprint(configuration, cmd_file[pkg], pkg)
