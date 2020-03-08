# KicadModTree is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KicadModTree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2016-2018 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>

from __future__ import division
import math
import re

from KicadModTree.util.TolerancedSize import TolerancedSize

def ipc_body_edge_inside(
        ipc_data, ipc_round_base, manf_tol, body_size, lead_width,
        lead_len=None, lead_inside=None, heel_reduction=0):
    r""" Calculate IPC pad parameters (G,Z,X) for components with "leads" extending till the body edge.
    No lead packages and two terminal devices with terminals at the end.

    :params:
      * *ipc_data* (dict) --
        Dict holding the fillet size definitions. Expected keys are 'toe', 'heel' and 'side'.
      * *ipc_round_base* (dict) --
        Dict holding the round base for calculating each fillet. Expected keys are 'toe', 'heel' and 'side'.
      * *manf_tol* (dict) --
        Dict holding information about manufacturing tolerances.
        Value of key 'manufacturing_tolerance' is used to define the PCB manufacturing tolerances (default: 0.1mm)
        Value of key 'placement_tolerance' is used to define the part placement tolerances (default: 0.05mm)
      * *body_size* (TolerancedSize) --
        Toleranced dimension of the body size in the currently interesting direction.
      * *lead_width* (TolerancedSize) --
        Toleranced dimension of the lead width.
      * *lead_len* (TolerancedSize) --
        Toleranced length of the "lead" (contact area).
      * *lead_inside* (TolerancedSize) --
        Alternative for lead length. Toleranced distance between the inside edges of the "leads".
        (Directly giving IPC parameter "S").
      * *heel_reduction* (float) --
        Manual heel reduction. (default: 0)

    :return:
      * *pad parameters* (tuple of floats)
        Return parameters Gmin, Zmax and Xmax used to calculate pad size and position
    """
    pull_back = TolerancedSize(nominal=0)

    return ipc_body_edge_inside_pull_back(
                ipc_data, ipc_round_base, manf_tol, body_size, lead_width,
                lead_len=lead_len, lead_inside=lead_inside, pull_back=pull_back,
                heel_reduction=heel_reduction
                )

def ipc_body_edge_inside_pull_back(
        ipc_data, ipc_round_base, manf_tol, body_size, lead_width,
        lead_len=None, lead_inside=None, body_to_inside_lead_edge=None, pull_back=None, lead_outside=None, heel_reduction=0):
    r""" Calculate IPC pad parameters for components with "leads" pulled back from the body edge by given length.
    No lead packages and two terminal devices with terminals set in from what is called the body dimension.
    Set pullback to 0 for components without pullback.

    :params:
      * *ipc_data* (dict) --
        Dict holding the fillet size definitions. Expected keys are 'toe', 'heel' and 'side'.
      * *ipc_round_base* (dict) --
        Dict holding the round base for calculating each fillet. Expected keys are 'toe', 'heel' and 'side'.
      * *manf_tol* (dict) --
        Dict holding information about manufacturing tolerances.
        Value of key 'manufacturing_tolerance' is used to define the PCB manufacturing tolerances (default: 0.1mm)
        Value of key 'placement_tolerance' is used to define the part placement tolerances (default: 0.05mm)
      * *body_size* (TolerancedSize) --
        Toleranced dimension of the body size in the currently interesting direction.
      * *lead_width* (TolerancedSize) --
        Toleranced dimension of the lead width.
      * *lead_len* (TolerancedSize) --
        Toleranced length of the "lead" (contact area).
      * *lead_inside* (TolerancedSize) --
        Alternative for lead length. Toleranced distance between the inside edges of the "leads".
        (Directly giving IPC parameter "S").
      * *body_to_inside_lead_edge* (TolerancedSize) --
        Alternative for lead length in the case where the lead is pulled back from the body edge.
      * *pull_back* (TolerancedSize) --
        Toleranced distance between outside lead edge and body edge.
      * *lead_outside* (TolerancedSize) --
        Tolerance distance between the outside edges of the leads.
      * *heel_reduction* (float) --
        Manual heel reduction. (default: 0)

    :return:
      * *pad parameters* (tuple of floats)
        Return parameters Gmin, Zmax and Xmax used to calculate pad size and position

    :calculation:
        Zmax = Lmin + 2JT + √(CL^2 + F^2 + P^2)
        Gmin = Smax − 2JH − √(CS^2 + F^2 + P^2)
        Xmax = Wmin + 2JS + √(CW^2 + F^2 + P^2)

        Calculating terminal spacing from the terminal length
        Stol(RMS) = √(Ltol^2 + 2*^2)
        Smin = Lmin - 2*Tmax
        Smax(RMS) = Smin + Stol(RMS)
    """

    F = manf_tol.get('manufacturing_tolerance', 0.1)
    P = manf_tol.get('placement_tolerance', 0.05)

    if lead_outside is None:
        if pull_back is None:
            raise KeyError("Either lead outside or pull back distance must be given")
        lead_outside = body_size - pull_back*2

    if lead_inside is not None:
        S = lead_inside
    elif lead_len is not None:
        S = lead_outside - lead_len*2
    elif body_to_inside_lead_edge is not None:
        S = body_size - body_to_inside_lead_edge*2
    else:
        raise KeyError("either lead inside distance, lead to body edge or lead lenght must be given")

    Gmin = S.maximum_RMS - 2*ipc_data['heel'] + 2*heel_reduction - math.sqrt(S.ipc_tol_RMS**2 + F**2 + P**2)

    Zmax = lead_outside.minimum_RMS + 2*ipc_data['toe'] + math.sqrt(lead_outside.ipc_tol_RMS**2 + F**2 + P**2)
    Xmax = lead_width.minimum_RMS + 2*ipc_data['side'] + math.sqrt(lead_width.ipc_tol_RMS**2 + F**2 + P**2)

    Zmax = TolerancedSize.roundToBase(Zmax, ipc_round_base['toe'])
    Gmin = TolerancedSize.roundToBase(Gmin, ipc_round_base['heel'])
    Xmax = TolerancedSize.roundToBase(Xmax, ipc_round_base['side'])

    return Gmin, Zmax, Xmax

def ipc_gull_wing(
        ipc_data, ipc_round_base, manf_tol, lead_width, lead_outside,
        lead_len=None, lead_inside=None, heel_reduction=0):
    r""" Calculate IPC pad parameters for gullwing devices

    :params:
      * *ipc_data* (dict) --
        Dict holding the fillet size definitions. Expected keys are 'toe', 'heel' and 'side'.
      * *ipc_round_base* (dict) --
        Dict holding the round base for calculating each fillet. Expected keys are 'toe', 'heel' and 'side'.
      * *manf_tol* (dict) --
        Dict holding information about manufacturing tolerances.
        Value of key 'manufacturing_tolerance' is used to define the PCB manufacturing tolerances (default: 0.1mm)
        Value of key 'placement_tolerance' is used to define the part placement tolerances (default: 0.05mm)
      * *body_size* (TolerancedSize) --
        Toleranced dimension of the body size in the currently interesting direction.
      * *lead_width* (TolerancedSize) --
        Toleranced dimension of the lead width.
      * *lead_outside* (TolerancedSize) --
        Tolerance distance between the outside edges of the leads.
      * *lead_len* (TolerancedSize) --
        Toleranced length of the "lead" (contact area).
      * *lead_inside* (TolerancedSize) --
        Alternative for lead length. Toleranced distance between the inside edges of the "leads".
        (Directly giving IPC parameter "S").
      * *heel_reduction* (float) --
        Manual heel reduction. (default: 0)

    :return:
      * *pad parameters* (tuple of floats)
        Return parameters Gmin, Zmax and Xmax used to calculate pad size and position

    :calculation:
        Zmax = Lmin + 2JT + √(CL^2 + F^2 + P^2)
        Gmin = Smax − 2JH − √(CS^2 + F^2 + P^2)
        Xmax = Wmin + 2JS + √(CW^2 + F^2 + P^2)

        Calculating terminal spacing from the terminal length
        Stol(RMS) = √(Ltol^2 + 2*^2)
        Smin = Lmin - 2*Tmax
        Smax(RMS) = Smin + Stol(RMS)
    """

    F = manf_tol.get('manufacturing_tolerance', 0.1)
    P = manf_tol.get('placement_tolerance', 0.05)

    if lead_inside is not None:
        S = lead_inside
    elif lead_len is not None:
        S = lead_outside - lead_len*2
    else:
        raise KeyError("either lead inside distance or lead lenght must be given")

    Gmin = S.maximum_RMS - 2*ipc_data['heel'] + 2*heel_reduction - math.sqrt(S.ipc_tol_RMS**2 + F**2 + P**2)

    Zmax = lead_outside.minimum_RMS + 2*ipc_data['toe'] + math.sqrt(lead_outside.ipc_tol_RMS**2 + F**2 + P**2)
    Xmax = lead_width.minimum_RMS + 2*ipc_data['side'] + math.sqrt(lead_width.ipc_tol_RMS**2 + F**2 + P**2)

    Zmax = TolerancedSize.roundToBase(Zmax, ipc_round_base['toe'])
    Gmin = TolerancedSize.roundToBase(Gmin, ipc_round_base['heel'])
    Xmax = TolerancedSize.roundToBase(Xmax, ipc_round_base['side'])

    return Gmin, Zmax, Xmax

def ipc_pad_center_plus_size(
        ipc_data, ipc_round_base, manf_tol,
        center_position, lead_length, lead_width):
    r""" Calculate IPC pad parameters for leads given with their size and center point.
    Mostly used for pullback no lead packages especially LGA.

    :params:
      * *ipc_data* (dict) --
        Dict holding the fillet size definitions. Expected keys are 'toe', 'heel' and 'side'.
      * *ipc_round_base* (dict) --
        Dict holding the round base for calculating each fillet. Expected keys are 'toe', 'heel' and 'side'.
      * *manf_tol* (dict) --
        Dict holding information about manufacturing tolerances.
        Value of key 'manufacturing_tolerance' is used to define the PCB manufacturing tolerances (default: 0.1mm)
        Value of key 'placement_tolerance' is used to define the part placement tolerances (default: 0.05mm)
      * *center_position* (TolerancedSize) --
        Toleranced position of the lead center.
      * *lead_length* (TolerancedSize) --
        Toleranced length of the "lead" (contact area).
      * *lead_width* (TolerancedSize) --
        Toleranced dimension of the lead width.

    :return:
      * *pad parameters* (tuple of floats)
        Return parameters Gmin, Zmax and Xmax used to calculate pad size and position
    """
    F = manf_tol.get('manufacturing_tolerance', 0.1)
    P = manf_tol.get('placement_tolerance', 0.05)

    S = center_position*2 - lead_length
    lead_outside = center_position*2 + lead_length

    Gmin = S.maximum_RMS - 2*ipc_data['heel'] - math.sqrt(S.ipc_tol_RMS**2 + F**2 + P**2)
    Zmax = lead_outside.minimum_RMS + 2*ipc_data['toe'] + math.sqrt(lead_outside.ipc_tol_RMS**2 + F**2 + P**2)

    Xmax = lead_width.minimum_RMS + 2*ipc_data['side'] + math.sqrt(lead_width.ipc_tol_RMS**2 + F**2 + P**2)

    Zmax = TolerancedSize.roundToBase(Zmax, ipc_round_base['toe'])
    Gmin = TolerancedSize.roundToBase(Gmin, ipc_round_base['heel'])
    Xmax = TolerancedSize.roundToBase(Xmax, ipc_round_base['side'])

    return Gmin, Zmax, Xmax
