#!/usr/bin/env python3

import sys
import os
import argparse
import math
import yaml

sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))  # load parent path of KicadModTree
sys.path.append(os.path.join(sys.path[0], "..", "..", "tools"))  # load parent path of tools

from ipc_pad_size_calculators import *
from footprint_scripts_sip import makeSIPVertical
from footprint_global_properties import crt_offset


# TODO BOTH FUNCTIONS SHOULD ALREADY BE IMPLEMENTED SOMEWHERE!!!
# Values are taken from
# https://www.pcb-3d.com/tutorials/how-to-calculate-pth-hole-and-pad-diameter-sizes-according-to-ipc-7251-ipc-2222-and-ipc-2221-standards/
def ipc_calc_min_drill_size(pin_diameter, ipc_density):
    if ipc_density == "A":
        return pin_diameter.maximum + 0.25
    elif ipc_density == "B":
        return pin_diameter.maximum + 0.20
    elif ipc_density == "C":
        return pin_diameter.maximum + 0.15
    else:
        sys.exit("ERROR: Invalid IPC density level: " + ipc_density)

def ipc_calc_pad_diameter(min_drill_diameter, ipc_density):
    if ipc_density == "A":
        return min_drill_diameter + 0.1 + 0.6
    elif ipc_density == "B":
        return min_drill_diameter + 0.1 + 0.5
    elif ipc_density == "C":
        return min_drill_diameter + 0.1 + 0.4
    else:
        sys.exit("ERROR: Invalid IPC density level: " + ipc_density)


def create_footprint(name, configuration, **kwargs):

    # ensure all provided dimensions are fully toleranced
    package = {
        'length': TolerancedSize.fromYaml(kwargs['package'], base_name='length'),
        'width':  TolerancedSize.fromYaml(kwargs['package'], base_name='width'),
        'height': TolerancedSize.fromYaml(kwargs['package'], base_name='height'),
    }

    top_offset  = kwargs['top_offset']   # offset from pin 1 to the upper package edge
    left_offset = kwargs['left_offset']  # offset from pin 1 to the left package edge

    # parse pin
    pin = kwargs['pin']
    if 'length' in pin and 'width' in pin and not 'diameter' in pin or not 'length' in pin and not 'width' in pin and 'diameter':
        if 'diameter' in pin:
            pin_diameter = TolerancedSize.fromYaml(pin, base_name='diameter')
        else:
            pin_length   = TolerancedSize.fromYaml(pin, base_name='length')
            pin_width    = TolerancedSize.fromYaml(pin, base_name='width')
            # calculate diameter of rectangular pin
            min_dia = math.sqrt(pin_length.minimum**2 + pin_width.minimum**2)
            nom_dia = math.sqrt(pin_length.nominal**2 + pin_width.nominal**2)
            max_dia = math.sqrt(pin_length.maximum**2 + pin_width.maximum**2)
            pin_diameter = TolerancedSize(minimum=min_dia, nominal=nom_dia, maximum=max_dia)
    else:
        sys.exit("ERROR: Do only specify ('length' and 'width') or 'diameter' for pins but not all 3!")

    if 'ddrill' in kwargs:
        ddrill = kwargs['ddrill']
    else:
        ddrill = ipc_calc_min_drill_size(pin_diameter, configuration['ipc_density'])

    if 'pad' in kwargs:
        pad = kwargs['pad']
        if 'length' in pad and 'width' in pad:
            pad = {
                'length': TolerancedSize.fromYaml(pad, base_name='length').nominal,
                'width':  TolerancedSize.fromYaml(pad, base_name='width').nominal
            }
        else:
            sys.exit("ERROR: You need to specify either both 'pad_length' and 'pad_width' or none of them to use IPC standard sizes!")
    else: # use IPC drill size
        pad = {
            'length': ipc_calc_pad_diameter(ddrill, configuration['ipc_density']),
            'width':  ipc_calc_pad_diameter(ddrill, configuration['ipc_density'])
        }

    pitch = kwargs['pitch'] # pin pitch
    pins  = kwargs['pins']  # amount of pins in package (including missing ones)
    missing_pins = kwargs['missing_pins'] if 'missing_pins' in kwargs else [] # list of pin numbers that are missing

    library     = kwargs['library']
    description = kwargs['description']
    datasheet   = kwargs['datasheet'] # link to datasheet
    revision    = kwargs['revision']  # revision of the datasheet

    tags = kwargs['tags']
    if tags:
        tags = "SIP-{0}".format(pins) + " " + tags
    else:
        tags = "SIP-{0}".format(pins)

    if datasheet:
        if not "#page=" in datasheet:
            print("WARNING: You should state the PDF page where the footprint is specified.")
            print("E.g. https://www.page.com/datasheet.pdf#page=3")
        if not datasheet.startswith("https"):
            print("WARNING: Datasheet links should use the HTTPS protocol.")
        description += ", " + datasheet
    if revision:
        description += " Rev. " + revision

    description += " (Generated with " + os.path.basename(__file__) + ")"

    # TODO Remove those print lines
    print(description)
    print(tags)

    # TODO: Move this check into makeSIPVertical and modify parameters to take a TolerancedSize
    if (package['length'].maximum - package['length'].nominal > 2 * crt_offset) or (package['width'].maximum - package['width'].nominal > 2 * crt_offset):
        print("ERROR: Your footprint has too high tolerances. This can't be handeld by makeSIPVertical!")

    makeSIPVertical(pins=pins, rm=pitch, ddrill=ddrill,
                    pad=[pad['length'], pad['width']],
                    package_size=[package['length'].nominal, package['width'].nominal, package['height'].nominal],
                    left_offset=left_offset, top_offset=top_offset,
                    footprint_name=name,
                    description=description,
                    tags=tags,
                    lib_name=library,
                    missing_pins=missing_pins)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse *.kicad_mod.yml file(s) and create matching footprints')
    parser.add_argument('files', metavar='file', type=str, nargs='+', help='yml-files to parse')
    parser.add_argument('--ipc_density', type=str, nargs='?', help='the IPC density', default='nominal')

    args = parser.parse_args()

    # TODO Here I overwrite the configuration with B as the configuration passes "nominal"
    # and I don't know what this means...
    configuration = {
        # 'ipc_density': args.ipc_density
        'ipc_density': "B"
    }

    for filepath in args.files:
        with open(filepath, 'r') as stream:
            try:
                yaml_parsed = yaml.safe_load(stream)
                for footprint in yaml_parsed:
                    print("generate {name}.kicad_mod".format(name=footprint))
                    create_footprint(footprint, configuration, **yaml_parsed.get(footprint))

            except yaml.YAMLError as exc:
                print(exc)