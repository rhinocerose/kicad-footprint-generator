#!/usr/bin/env python

import csv
import sys
import os
from math import ceil, sqrt

sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))  # load parent path of KicadModTree

from KicadModTree import *  # NOQA
from KicadModTree.nodes.base.Pad import Pad  # NOQA

drill_extra = .2 # mm extra hole diameter
size_extra = 1.5 # mm copper
mounting_drill_extra = .2 # mm extra hole diameter
library = "Transformer_THT.pretty"

def setup_kicad_mod(name, url):
    kicad_mod = Footprint(name)
    kicad_mod.setDescription(url)
    kicad_mod.setTags("transformer tht")

    kicad_mod.append(Text(type="user", text="%R", at=[0, -1], layer="F.Fab"))
    kicad_mod.append(Text(type='value', text=name, at=[0, 1], layer="F.Fab"))

    return kicad_mod

def build_outline(kicad_mod, x, y):
    kicad_mod.append(Text(type='reference', text='REF**', at=[0, -y/2-1],
        layer="F.SilkS"))

    kicad_mod.append(RectLine(start=[-x/2, -y/2], end=[x/2, y/2],
        layer="F.Fab"))
    kicad_mod.append(RectLine(start=[-x/2, -y/2], end=[x/2, y/2],
        layer="F.SilkS", offset=.1))
    kicad_mod.append(RectLine(start=[-x/2, -y/2], end=[x/2, y/2],
        layer="F.CrtYd", offset=.25))

def add_pads(kicad_mod, size, drill, x_sep, pri_sep, sec_sep, pris_sep=None,
        secs_sep=None, shift=(0, 0)):
    if pris_sep:
        # dual input coils
        pads = [(-x_sep/2, y) for y in [-pri_sep - pris_sep/2, -pris_sep/2,
            pris_sep/2, pri_sep + pris_sep/2]]
    else:
        # single input coil
        pads = [(-x_sep/2, y) for y in [-pri_sep/2, pri_sep/2]]

    if secs_sep:
        # dual output coils
        pads += [(x_sep/2, -y) for y in [-sec_sep - secs_sep/2, -secs_sep/2,
            secs_sep/2, sec_sep + secs_sep/2]]
    else:
        # single output coil
        pads += [(x_sep/2, -y) for y in [-sec_sep/2, sec_sep/2]]

    pads = [(x + shift[0], y + shift[1]) for x, y in pads]

    for i, pos in enumerate(pads):
        shape = Pad.SHAPE_ROUNDRECT if i == 0 else Pad.SHAPE_CIRCLE
        kicad_mod.append(Pad(number=i+1, type=Pad.TYPE_THT, shape=shape,
            at=pos, size=size, drill=drill, layers=Pad.LAYERS_THT,
            radius_ratio=.25, maximum_radius=.5))

def add_mounting(kicad_mod, drill, x, y):
    for pos in ((-x/2, -y/2), (-x/2, y/2), (x/2, -y/2), (x/2, y/2)):
        kicad_mod.append(Pad(at=pos,
            type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, size=drill, drill=drill,
            layers=Pad.LAYERS_NPTH))

def build_flat_transformer(core, url, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P):
    # names are based on the listing in the catalogue on pages 281 and
    # following
    name = f"Transformer_Block_{core}"
    print(f"Building {name}")
    kicad_mod = setup_kicad_mod(name, url)
    build_outline(kicad_mod, A, B)
    if M:
        drill = M + drill_extra
    else:
        drill = ceil(sqrt(N**2 + O**2) * 10) / 10 + drill_extra
    size = drill + size_extra
    add_pads(kicad_mod, size=size, drill=drill, x_sep=F, pri_sep=I, pris_sep=J,
            sec_sep=L, secs_sep=K, shift=((A-F-2*G)/2, (B-2*I-J-2*H)/2))
    add_mounting(kicad_mod, drill=P+mounting_drill_extra, x=D, y=E)

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(f"{library}/{name}.kicad_mod")


def load_csvs():
    with open("./flats.csv", "r") as f:
        for row in csv.reader(f,delimiter=";"):
            args = [float(arg) for arg in row[2:]]
            build_flat_transformer(row[0], row[1], *args)

if __name__ == "__main__":
    try:
        os.mkdir(library)
    except FileExistsError:
        pass
    load_csvs()
