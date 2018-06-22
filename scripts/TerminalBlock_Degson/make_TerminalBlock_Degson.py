#!/usr/bin/env python

import sys
import os
import math

# ensure that the kicad-footprint-generator directory is available
sys.path.append(os.path.join(sys.path[0],"..","..")) # load kicad_mod path
sys.path.append(os.path.join(sys.path[0],"..","tools")) # load kicad_mod path

from KicadModTree import *  # NOQA
from footprint_scripts_terminal_blocks import *

def make_DG212V_THR_3_5():
    """DG212V-THR-3.5 - http://www.degson.com/en/pro_detail/id/150"""
    script_generated_note="https://github.com/pointhi/kicad-footprint-generator/tree/master/scripts/TerminalBlock_Degson";
    classname="TerminalBlock_Degson"
    pins=range(2,24+1)
    rm=3.5
    package_height=8.5
    leftbottom_offset=[2.10, 1.4]
    ddrill=1.2
    pad=[2.2,2.2]
    bevel_height=[1.5]
    opening=[2.7, 2.7]
    opening_xoffset=0
    opening_yoffset=1.5
    secondDrillDiameter=ddrill
    secondDrillOffset=[0,-5.5]
    secondDrillPad=pad
    secondHoleDiameter=[3,3]
    secondHoleOffset=[0,-5]
    thirdHoleDiameter=0
    thirdHoleOffset=[0,0]
    fourthHoleDiameter=0
    fourthHoleOffset=[0,0]
    fabref_offset=[0,3.6]
    nibbleSize=[]
    nibblePos=[]
    webpage="http://www.degson.com/en/downpdf/id/150.html"
    for p in pins:
        classname_description="Terminal Block Degson DG212V-THR-3.5-{:02d}P-1Y-00A(H)".format(p);
        footprint_name="DG212V-THR-3.5-{1:02d}P-1Y-00A_1x{1:02}_P{0:3.2f}mm_Vertical".format(rm, p)
        makeTerminalBlockVertical(footprint_name=footprint_name, 
                                  pins=p, rm=rm, 
                                  package_height=package_height, leftbottom_offset=leftbottom_offset, opening_xoffset=opening_xoffset, opening_yoffset=opening_yoffset, opening=opening,
                                  ddrill=ddrill, pad=pad, bevel_height=bevel_height, secondHoleDiameter=secondHoleDiameter, secondHoleOffset=secondHoleOffset, thirdHoleDiameter=thirdHoleDiameter, thirdHoleOffset=thirdHoleOffset, fourthHoleDiameter=fourthHoleDiameter, fourthHoleOffset=fourthHoleOffset, 
                                  secondDrillDiameter=secondDrillDiameter,secondDrillOffset=secondDrillOffset,secondDrillPad=secondDrillPad,
                                  nibbleSize=nibbleSize, nibblePos=nibblePos, fabref_offset=fabref_offset,
                                  tags_additional=[], lib_name='${KISYS3DMOD}/'+classname, classname=classname, classname_description=classname_description, 
                                  webpage=webpage, script_generated_note=script_generated_note)

if __name__ == '__main__':
    make_DG212V_THR_3_5()
 