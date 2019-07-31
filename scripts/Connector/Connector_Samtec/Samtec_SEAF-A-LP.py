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
    print('Building footprint for parameter set: {}'.format(fpId))
    
    pkgA = fpParams["body_size_A"]
    pkgB = fpParams["body_size_B"]
    pkgC = fpParams["body_size_C"]
    pkgD = fpParams["body_size_D"]
    pkgE = fpParams["body_size_E"]
    pkgF = fpParams["body_size_F"]
    pkgG = fpParams["body_size_G"]
    pkgH = fpParams["body_size_H"]
    pkgJ = fpParams["body_size_J"]
    pkgLREF = fpParams["body_size_left_ref"]
    pkgRREF = fpParams["body_size_right_ref"]
    pkgMREF = fpParams["body_size_middle_ref"]
    
    pthDist = fpParams["pth_distance"]

    layoutX = fpParams["layout_x"]
    layoutY = fpParams["layout_y"]
    
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
    if "pitch" in fpParams:
        if "pitch_x" and "pitch_y" in fpParams:
            raise KeyError('{}: Either pitch or both pitch_x and pitch_y must be given.'.format(fpId))
        else:
            pitchString = str(fpParams["pitch"])
            pitchX = fpParams["pitch"]
            pitchY = fpParams["pitch"]
    else:
        if "pitch_x" and "pitch_y" in fpParams:
            pitchString = str(fpParams["pitch_x"]) + "x" + str(fpParams["pitch_y"])
            pitchX = fpParams["pitch_x"]
            pitchY = fpParams["pitch_y"]
        else:
            raise KeyError('{}: Either pitch or both pitch_x and pitch_y must be given.'.format(fpId))

    f = Footprint(fpId)
    f.setAttribute("smd")
    if "mask_margin" in fpParams: f.setMaskMargin(fpParams["mask_margin"])
    if "paste_margin" in fpParams: f.setPasteMargin(fpParams["paste_margin"])
    if "paste_ratio" in fpParams: f.setPasteMarginRatio(fpParams["paste_ratio"])

    s1 = [1.0, 1.0]
    s2 = [min(1.0, round((pkgLREF + pkgA + pkgRREF) / 4.3, 2))] * 2

    t1 = 0.15 * s1[0]
    t2 = 0.15 * s2[0]

    padShape = Pad.SHAPE_CIRCLE
    if "pad_shape" in fpParams:
        if fpParams["pad_shape"] == "rect":
            padShape = Pad.SHAPE_RECT
        if fpParams["pad_shape"] == "roundrect":
            padShape = Pad.SHAPE_ROUNDRECT

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
    P1XFab = xCenter - ((pkgA / 2.0) + pkgRREF)
    P2XFab = xCenter + ((pkgA / 2.0) + pkgLREF)
    P3XFab = P2XFab
    P4XFab = xCenter + (pkgH / 2.0)
    P5XFab = P4XFab
    P6XFab = P3XFab
    P7XFab = P6XFab
    P8XFab = P1XFab
    P9XFab = P8XFab
    P10XFab = xCenter - (pkgH / 2.0)
    P11XFab = P10XFab
    P12XFab = P1XFab

    P1YFab = yCenter - (pkgC / 2.0)
    P2YFab = P1YFab
    P3YFab = yCenter - (pkgMREF / 2.0)
    P4YFab = P3YFab
    P5YFab = yCenter + (pkgMREF / 2.0)
    P6YFab = P5YFab
    P7YFab = yCenter + (pkgC / 2.0)
    P8YFab = P7YFab
    P9YFab = P6YFab
    P10YFab = P9YFab
    P11YFab = P3YFab
    P12YFab = P11YFab

    # Generating Points for the "crtYd"-layer (courty yard)
    P1XcrtYd = crtYdRound(xCenter - ((pkgH / 2.0) + crtYdOffset))
    P2XcrtYd = crtYdRound(xCenter + ((pkgH / 2.0) + crtYdOffset))
    P3XcrtYd = P2XcrtYd
    P4XcrtYd = P1XcrtYd

    P1YcrtYd = crtYdRound(yCenter - ((pkgC / 2.0) + crtYdOffset))
    P2YcrtYd = P1YcrtYd
    P3YcrtYd = crtYdRound(yCenter + ((pkgC / 2.0) + crtYdOffset))
    P4YcrtYd = P3YcrtYd

    # Generating Points for the "Silk"-layer (silkscreed)
    P1XSilk = P1XFab - silkOffset
    P2XSilk = P2XFab + silkOffset
    P3XSilk = P2XSilk
    P4XSilk = P4XFab + silkOffset
    P5XSilk = P4XSilk
    P6XSilk = P3XSilk
    P7XSilk = P2XSilk
    P8XSilk = P1XSilk
    P9XSilk = P8XSilk
    P10XSilk = P10XFab - silkOffset
    P11XSilk = P10XSilk
    P12XSilk = P1XSilk
    
    P1YSilk = P1YFab - silkOffset
    P2YSilk = P1YSilk
    P3YSilk = P3YFab - silkOffset
    P4YSilk = P3YSilk
    P5YSilk = P5YFab + silkOffset
    P6YSilk = P5YSilk
    P7YSilk = P7YFab + silkOffset
    P8YSilk = P7YSilk
    P9YSilk = P6YSilk
    P10YSilk = P9YSilk
    P11YSilk = P4YSilk
    P12YSilk = P11YSilk

    # Define the position of pads to be placed
    xPadLeft = xCenter - pitchX * ((layoutX - 1) / 2.0)
    #xPadRight = xCenter + pitchX * ((layoutX - 1) / 2.0)
    yPadTop = yCenter - pitchY * ((layoutY - 1) / 2.0)
    #yPadBottom = yCenter + pitchY * ((layoutY - 1) / 2.0)

    # Define the position of the REF** in silkscreen
    xRefSilk = xCenter
    yRefSilk = P1YFab - 2.0

    # Define the position of the REF** in fabrication
    xRefFab = xCenter
    yRefFab = yCenter

    # Define the position of the VALUE in fabrication
    xValueFab = xCenter
    yValueFab = P8YFab + 2.0

    

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
                                    [P9XFab, P9YFab],
                                    [P10XFab, P10YFab],
                                    [P11XFab, P11YFab],
                                    [P12XFab, P12YFab],
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
                                    [P9XSilk, P9YSilk],
                                    [P10XSilk, P10YSilk],
                                    [P11XSilk, P11YSilk],
                                    [P12XSilk, P12YSilk],
                                    [P1XSilk, P1YSilk]],
                          layer="F.SilkS", width=wSilkS))

    # Pads
    balls = layoutX * layoutY
    if rowSkips == []:
        for _ in range(layoutY):
            rowSkips.append([])
    for rowNum, row in zip(range(layoutY), rowNames):
        rowSet = set(range(1, layoutX + 1))
        for item in rowSkips[rowNum]:
            try:
                # If item is a range, remove that range
                rowSet -= set(range(*item))
                balls -= item[1] - item[0]
            except TypeError:
                # If item is an int, remove that int
                rowSet -= {item}
                balls -= 1
        for col in rowSet:
            f.append(Pad(number="{}{}".format(row, col), type=Pad.TYPE_SMT,
                         shape=padShape,
                         at=[xPadLeft + (col-1) * pitchX, yPadTop + rowNum * pitchY],
                         size=[fpParams["pad_diameter"], fpParams["pad_diameter"]],
                         layers=Pad.LAYERS_SMT, 
                         radius_ratio=config['round_rect_radius_ratio']))

    # Placement Holes NPTH
    P1XPlacementHole = xCenter - (pkgB / 2.0)
    P1YPlacementHole = yCenter - pkgE

    f.append(Pad(at=[P1XPlacementHole, P1YPlacementHole], number="",
                    type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, size=fpParams["npth_drill"],
                    drill=fpParams["npth_drill"], layers=Pad.LAYERS_NPTH))

    P2XPlacementHole = xCenter + (pkgB / 2.0)
    P2YPlacementHole = yCenter

    f.append(Pad(at=[P2XPlacementHole, P2YPlacementHole], number="",
                    type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, size=fpParams["npth_drill"],
                    drill=fpParams["npth_drill"], layers=Pad.LAYERS_NPTH))

    # Guide Holes PTH
    P1XGuideHole = xCenter - (pkgJ / 2.0) - (pthDist / 2.0)
    P1YGuideHole = yCenter - (pthDist / 2.0)

    f.append(Pad(at=[P1XGuideHole, P1YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P2XGuideHole = xCenter - (pkgJ / 2.0) + (pthDist / 2.0)
    P2YGuideHole = yCenter - (pthDist / 2.0)

    f.append(Pad(at=[P2XGuideHole, P2YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P3XGuideHole = xCenter - (pkgJ / 2.0) - (pthDist / 2.0)
    P3YGuideHole = yCenter + (pthDist / 2.0)

    f.append(Pad(at=[P3XGuideHole, P3YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P4XGuideHole = xCenter - (pkgJ / 2.0) + (pthDist / 2.0)
    P4YGuideHole = yCenter + (pthDist / 2.0)

    f.append(Pad(at=[P4XGuideHole, P4YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P5XGuideHole = xCenter + (pkgJ / 2.0) - (pthDist / 2.0)
    P5YGuideHole = yCenter - (pthDist / 2.0)

    f.append(Pad(at=[P5XGuideHole, P5YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P6XGuideHole = xCenter + (pkgJ / 2.0) + (pthDist / 2.0)
    P6YGuideHole = yCenter - (pthDist / 2.0)

    f.append(Pad(at=[P6XGuideHole, P6YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P7XGuideHole = xCenter + (pkgJ / 2.0) - (pthDist / 2.0)
    P7YGuideHole = yCenter + (pthDist / 2.0)

    f.append(Pad(at=[P7XGuideHole, P7YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))

    P8XGuideHole = xCenter + (pkgJ / 2.0) + (pthDist / 2.0)
    P8YGuideHole = yCenter + (pthDist / 2.0)

    f.append(Pad(at=[P8XGuideHole, P8YGuideHole], number="",
                    type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, size=fpParams["pth_size"],
                    drill=fpParams["pth_drill"], layers=Pad.LAYERS_THT))



    ########################### Pin 1 - Marker #################################
    markerOffset = 0.4
    markerLength = fpParams['pad_diameter']
    
    P1XMarker = xPadLeft
    P1YMarker = P1YSilk - markerOffset
    P2XMarker = P1XMarker - (markerLength / 2)
    P2YMarker = P1YMarker - (markerLength / sqrt(2))
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
    packageType = fpParams['description']

    f.append(Model(filename="{}Connector_Samtec_{}.3dshapes/{}.wrl".format(
                  config['3d_model_prefix'], familiyType, fpParams['description'])))

    f.setDescription("{0}, {1}x{2}mm, {3} Ball, {4}x{5} Layout, {6}mm Pitch, {7}".format(fpParams["description"], pkgC, pkgA, balls, layoutX, layoutY, pitchString, fpParams["size_source"]))
    f.setTags("{} {} {}{}".format(packageType, balls, pitchString, additionalTag))

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
