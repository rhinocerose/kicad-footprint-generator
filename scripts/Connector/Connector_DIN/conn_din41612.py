#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.join(sys.path[0], "..", "..", ".."))  # load parent path of KicadModTree
from KicadModTree import *
from math import ceil

lib_name = 'Connector_DIN'

large_holes = {
        'pin_hole_diameter': 1.6,
        'pin_plating_diameter': 2.3,
        }


# dimensions based of ERNI, ept and Harting
dimensions = {
        'pin_hole_diameter': 1,
        'pin_plating_diameter': 1.7,
        'mounting_hole_diameter': 2.8,
        'pin_row_offset': 2.54,
        'pin_column_offset': 2.54,
        'silk_reference_offset': 1.0,
        'name_pattern': '{row}{pin}',
        'Horizontal': {
            'a1_mounting': 2.54,
            'a1_edge': 5.3,
            'mounting_housing_front': 10.2, # max set by ERNI
            'mounting_housing_back': -2.54, # max set by ept
            'full': {
                'housing_width': 94,
                'connector_width': 87.5,
                'mounting_width': 88.9,
                'row_pins': 32,
                },
            'half': {
                'housing_width': 53.9,
                'connector_width': 47,
                'mounting_width': 48.26,
                'row_pins': 16,
                },
            'third': {
                'housing_width': 38.1,
                'connector_width': 31.7,
                'mounting_width': 33.02,
                'row_pins': 10,
                },
            },
        'Vertical':  {
            'a1_mounting': 2.54 - 0.3,
            'housing_depth': 8.6,
            'connector_depth': 6.2,
            'nodge_width': 1,
            'mounting_hole_diameter': 2.8,
            'pin_hole_diameter': 1,
            'nodge_height': 3,
            'nodge_width': 1,
            'gender': 'female',
            'full': {
                'housing_width': 95,
                'connector_width': 85,
                'connector_outer_width': 88,
                'mounting_width': 90,
                'row_pins': 32,
                },
            'half': {
                'housing_width': 55,
                'connector_width': 44.4,
                'connector_outer_width': 47.4,
                'mounting_width': 50,
                'row_pins': 16,
                },
            'third': {
                'housing_width': 39.76,
                'connector_width': 29.2,
                'connector_outer_width': 32.1,
                'mounting_width': 34.76,
                'row_pins': 10,
                },
            },
        'series': {
            'B': dict(
                series_rows='ab',
                housing_height=8.1,
                connector_height=6,
                ),
            'C': dict(
                series_rows='abc',
                housing_height=10.6,
                connector_height=8.5,
                ),
#            'CD': { 'series_rows': 'abcd' },
            'D': dict(
                series_rows='abc',
                housing_height=10.6,
                connector_height=8.5,
                **large_holes
                ),
            'E': dict(
                series_rows='abcde',
                housing_height=15.7,
                connector_height=13.6,
                **large_holes
                ),
#            'E160': { 'series_rows': 'abcde', },
            'F': dict(
                series_rows='zbd',
                housing_height=14.8,
                connector_height=12.4,
                **large_holes),
#            'F_flat': { 'series_rows': 'zbd', },
# TODO H11 vertical and horizontal use different rows (e, vs. ac)
#            'H11': { 'series_rows': 'e',
#                'name_pattern': '{pin}', **large_holes,
#                'mounting_housing_front': 14.3,
#                'a1_mounting': 12.7,
#                'a1_edge': 12.7 + 2.3,
#                },
            'Q': dict(
                series_rows='ab',
                mounting_housing_back=10.2 - 12.6,
                housing_height=8.6,
                connector_height=6.2,
                nodge_height=2.5,
                gender='male',
                ),
            'R': dict(
                series_rows='abc',
                housing_height=11.1,
                connector_height=8.7,
                nodge_height=2.5,
                gender='male',
                ),
        },

}

mounting_args = dict(
            type=Pad.TYPE_NPTH,
            shape=Pad.SHAPE_CIRCLE,
            size=dimensions['mounting_hole_diameter'],
            drill=dimensions['mounting_hole_diameter'],
            layers=Pad.LAYERS_NPTH,
        )

silk_reference_args = dict(
        type='reference',
        text='REF**',
        layer='F.SilkS',
        thickness=0.15,
        size=(1,1),
        )

fab_reference_args = dict(
        type='user',
        text='%R',
        layer='F.Fab',
        thickness=0.15,
        size=(1,1),
        )

name_text_args = dict(
        type='value',
        layer='F.Fab',
        thickness=0.15,
        size=(1,1),
        )


def mirror_x(point, ref):
    shifted = point - ref
    return Point(ref.x - shifted.x, point.y)

def mirror_y(point, ref):
    shifted = point - ref
    return Point(point.x,  ref.y - shifted.y)

def round_courtyard(point):
    grid = .01
    return Point(ceil(point.x / grid) * grid,
            ceil(point.y / grid) * grid)

def build_pins(mod, config, pins, rows, row_direction, column_direction):
    pin_args = dict(
                type=Pad.TYPE_THT,
                size=config['pin_plating_diameter'],
                drill=config['pin_hole_diameter'],
                layers=Pad.LAYERS_THT,
                radius_ratio=0.25,
                maximum_radius=0.25,
            )

    pins_per_row = pins / len(rows)
    for row in rows.lower():
        if row_direction == Point(0,1): # horizontal
            offset = config['series_rows'].lower().index(row) * dimensions['pin_row_offset']
        else: # vertical always uses all rows, z is index -1
            rows = "zabcde"
            offset = (rows.index(row) - 1) * dimensions['pin_row_offset']
        pin_one = Point(row_direction.x * offset, row_direction.y * offset)
        if pins_per_row == config['row_pins']:
            positions = range(1, config['row_pins'] + 1)
        elif pins_per_row == config['row_pins'] // 2:
            positions = range(2, config['row_pins'] + 1, 2)
        elif pins_per_row == config['row_pins'] // 4:
            positions = range(2, config['row_pins'] + 1, 4)
        elif pins_per_row == 11:
            positions = range(2, config['row_pins'] + 1, 3)
        else:
            raise Exception(f"weird pins per row: {pins_per_row} (row_pins: "
                            f"{config['row_pins']}, {pins}x{rows}")

        for pin in positions:
            number = config['name_pattern'].format(**locals())
            if number == 'a1':
                shape = Pad.SHAPE_ROUNDRECT
            else:
                shape = Pad.SHAPE_CIRCLE
            pos = Point( pin_one.x + column_direction.x * (pin - 1) *
                    dimensions['pin_column_offset'], pin_one.y +
                    column_direction.y * (pin - 1) *
                    dimensions['pin_column_offset'])
            mod.append(Pad(at=pos, number=number, shape=shape, **pin_args))


def build_din41612_connector_horizontal(mod, series, direction, pins, rows,
    config):

    center = Point(config['pin_column_offset'] * (config['row_pins'] / 2 - 0.5), 0)
    mounting = Point(center.x - config['mounting_width'] / 2,
            -config['a1_mounting'])
    # place mounting holes
    mod.append(Pad(at=mounting, **mounting_args))
    mod.append(Pad(at=mirror_x(mounting, center), **mounting_args))

    build_pins(mod, config, pins, rows, 
            row_direction=Point(0,1), column_direction=Point(1,0))

    # silk screen reference
    mod.append(Text(at=mounting + (0, -config['mounting_housing_back'] +
        config['silk_reference_offset']), rotation=0, **silk_reference_args))
    mod.append(Text(at=Point(center.x, mounting.y), **fab_reference_args))
    mod.append(Text(text=config['footprint_name'],
        at=Point(center.x, config['last_row_pos'] + config['pin_row_offset']),
        **name_text_args))

    config['a1_housing_front'] = config['a1_mounting'] + config['mounting_housing_front']
    config['a1_housing_back'] = config['a1_mounting'] + config['mounting_housing_back']

    hole_part_depth = 6
    hole_part_width = 5
    hole_part_inset = 1
    # draw outline
    mod.append(PolygoneLine(polygone=[
            Point(center.x - config['connector_width']/2,
                -config['a1_housing_front']),
            Point(center.x - config['connector_width']/2,
                -config['a1_housing_front'] + hole_part_depth),
            Point(center.x - config['housing_width']/2,
                -config['a1_housing_front'] + hole_part_depth),
            Point(center.x - config['housing_width']/2,
                -config['a1_housing_back']),
            Point(center.x - config['housing_width']/2 + hole_part_width,
                -config['a1_housing_back']),
            Point(center.x - config['housing_width']/2 + hole_part_width,
                -config['a1_housing_back'] - hole_part_inset),
            Point(center.x + config['housing_width']/2 - hole_part_width,
                -config['a1_housing_back'] - hole_part_inset),
            Point(center.x + config['housing_width']/2 - hole_part_width,
                -config['a1_housing_back']),
            Point(center.x + config['housing_width']/2,
                -config['a1_housing_back']),
            Point(center.x + config['housing_width']/2,
                -config['a1_housing_front'] + hole_part_depth),
            Point(center.x + config['connector_width']/2,
                -config['a1_housing_front'] + hole_part_depth),
            Point(center.x + config['connector_width']/2,
                -config['a1_housing_front']),
            Point(center.x - config['connector_width']/2,
                -config['a1_housing_front']),
        ], layer='F.Fab', width=.1))

    # add silk screen
    sd = .2
    silk_points = [
            Point(center.x - config['housing_width']/2 - sd,
                -config['a1_edge']),
            Point(center.x - config['housing_width']/2 - sd,
                -config['a1_housing_back'] + sd),
            Point(center.x - config['housing_width']/2 + hole_part_width + sd,
                -config['a1_housing_back'] + sd),
            Point(center.x - config['housing_width']/2 + hole_part_width + sd,
                -config['a1_housing_back'] - hole_part_inset + sd),
            ]
    mod.append(PolygoneLine(polygone=silk_points, layer='F.SilkS', width=.12))
    mod.append(PolygoneLine(polygone=list(map(lambda x: mirror_x(x, center),
        silk_points)), layer='F.SilkS', width=.12))
    # add arrow pointing at a1
    arrow_points = [
            Point(-1.27, 0),
            Point(-1.95, -0.3),
            Point(-1.95, 0.3),
            Point(-1.27, 0)
            ]
    mod.append(PolygoneLine(polygone=arrow_points, layer='F.SilkS', width=.12))

    # add courtyard
    cy = .5
    mod.append(PolygoneLine(polygone=list(map(round_courtyard, [
            Point(center.x - config['housing_width']/2 - cy,
                -config['a1_housing_front'] - cy),
            Point(center.x - config['housing_width']/2 - cy,
                -config['a1_housing_back'] + cy),
            Point(center.x - (config['row_pins']-1)/2 *
                config['pin_row_offset'] - config['pin_plating_diameter']/2 - cy,
                -config['a1_housing_back'] + cy),
            Point(center.x - (config['row_pins']-1)/2 *
                config['pin_row_offset'] - config['pin_plating_diameter']/2 - cy, config['last_row_pos'] +
                config['pin_plating_diameter'] / 2 + cy),
            Point(center.x + (config['row_pins']-1)/2 *
                config['pin_row_offset'] + config['pin_plating_diameter']/2 + cy, config['last_row_pos'] +
                config['pin_plating_diameter'] / 2 + cy),
            Point(center.x + (config['row_pins']-1)/2 *
                config['pin_row_offset'] + config['pin_plating_diameter']/2 + cy, 
                -config['a1_housing_back'] + cy),
            Point(center.x + config['housing_width']/2 + cy,
                -config['a1_housing_back'] + cy),
            Point(center.x + config['housing_width']/2 + cy,
                -config['a1_housing_front'] - cy),
            Point(center.x - config['housing_width']/2 - cy,
                -config['a1_housing_front'] - cy)
        ])), layer='F.CrtYd', width=.05))
    # mark board edge
    mod.append(PolygoneLine(polygone=[
            Point(center.x - config['housing_width']/2, -config['a1_edge']),
            Point(center.x + config['housing_width']/2, -config['a1_edge']),
        ], layer='Dwgs.User', width=.08))
    mod.append(Text(text='Board edge',
        at=Point(center.x, -config['a1_edge'] - 2), layer='Cmts.User',
        size=(.7,.7), thickness=.1, type='user'))
    arrow_args = dict(
            width=.1,
            layer='Cmts.User',
            )
    mod.append(PolygoneLine(polygone=[
        Point(center.x - .2, -config['a1_edge'] - .6),
        Point(center.x, -config['a1_edge'] - .1),
        Point(center.x + .2, -config['a1_edge'] - .6),
        ], **arrow_args))
    mod.append(PolygoneLine(polygone=[
        Point(center.x, -config['a1_edge'] - .1),
        Point(center.x, -config['a1_edge'] - 1.4),
        ], **arrow_args))

def build_din41612_connector_vertical(mod, series, direction, pins, rows,
        config):
    all_rows = 'zabcde'
    min_row_index = all_rows.find(config['series_rows'][0])
    max_row_index = all_rows.find(config['series_rows'][-1])
    total_rows = max_row_index - min_row_index
    rows_width = (total_rows) * config['pin_column_offset']
    center_x = rows_width / 2
    if 'z' in config['series_rows']:
        center_x -= config['pin_column_offset']
    center = Point(center_x, config['pin_column_offset'] * (config['row_pins'] / 2 -
        0.5))
    build_pins(mod, config, pins, rows,
            row_direction=Point(1,0), column_direction=Point(0,1))
    mounting = Point(config['a1_mounting'],
               center.y - config['mounting_width'] / 2)
    mod.append(Pad(at=mounting, **mounting_args))
    mod.append(Pad(at=mirror_y(mounting, center), **mounting_args))

    # references
    mod.append(Text(at=center - (0, config['housing_width'] / 2 +
        config['silk_reference_offset'], 0), rotation=0,
        **silk_reference_args))
    mod.append(Text(at=center, **fab_reference_args))
    mod.append(Text(text=config['footprint_name'],
        at=center + (0, config['housing_width'] / 2 + 
            config['silk_reference_offset']), **name_text_args))

    # connector outline
    conn_left = center.x - config['connector_height'] / 2
    conn_right = center.x + config['connector_height'] / 2
    conn_top = center.y - config['connector_width'] / 2
    conn_bottom = center.y + config['connector_width'] / 2
    conn_outline = [
            Point(conn_left, conn_top),
            Point(conn_right - config['nodge_height'], conn_top),
            Point(conn_right - config['nodge_height'],
                  conn_top + config['nodge_width']),
            Point(conn_right,
                  conn_top + config['nodge_width']),
            Point(conn_right,
                  conn_bottom - config['nodge_width']),
            Point(conn_right - config['nodge_height'],
                  conn_bottom - config['nodge_width']),
            Point(conn_right - config['nodge_height'], conn_bottom),
            Point(conn_left, conn_bottom),
            Point(conn_left, conn_top),
            ]
    mod.append(PolygoneLine(polygone=conn_outline, layer='F.Fab', width=.1))
    if config['gender'] == 'male':
        for mul in (1, -1):
            height = center.y + mul * config['connector_outer_width'] / 2
            inner_height = center.y + mul * config['connector_width'] / 2
            mod.append(PolygoneLine(polygone=(
                    Point(center.x - config['housing_height'] / 2, height),
                    Point(mounting.x - 3, height),
                    Point(mounting.x - 3, inner_height),
                    Point(mounting.x + 3, inner_height),
                    Point(mounting.x + 3, height),
                    Point(center.x + config['housing_height'] / 2, height),
                ),
                layer='F.Fab', width=.1))

    # housing
    def housing(expand):
        return [
            Point(center.x - config['housing_height'] / 2 - expand,
                  center.y - config['housing_width'] / 2 - expand),
            Point(center.x + config['housing_height'] / 2 + expand,
                  center.y - config['housing_width'] / 2 - expand),
            Point(center.x + config['housing_height'] / 2 + expand,
                  center.y + config['housing_width'] / 2 + expand),
            Point(center.x - config['housing_height'] / 2 - expand,
                  center.y + config['housing_width'] / 2 + expand),
            Point(center.x - config['housing_height'] / 2 - expand,
                  center.y - config['housing_width'] / 2 - expand)
            ]
    mod.append(PolygoneLine(polygone=housing(0), layer='F.Fab', width=.1))
    mod.append(PolygoneLine(polygone=housing(.2), layer='F.SilkS', width=.12))
    mod.append(PolygoneLine(polygone=list(map(round_courtyard, housing(.5))),
        layer='F.CrtYd', width=.05))

    # add arrow pointing at a1
    arrow_tip = center.x - config['housing_height'] / 2 - 0.3
    arrow_points = [
            Point(arrow_tip, 0),
            Point(arrow_tip - 0.68, -0.3),
            Point(arrow_tip - 0.68, 0.3),
            Point(arrow_tip, 0)
            ]
    mod.append(PolygoneLine(polygone=arrow_points, layer='F.SilkS', width=.12))

    # highlight connector shape on silk
    highlight_depth = 2
    highlight_expand = .1
    he = highlight_expand
    conn_highlight = [
            Point(conn_left - he, conn_top + highlight_depth),
            Point(conn_left - he, conn_top - he),
            Point(conn_right - config['nodge_height'] + he, conn_top - he),
            Point(conn_right - config['nodge_height'] + he,
                  conn_top + config['nodge_width'] - he),
            Point(conn_right + he,
                  conn_top + config['nodge_width'] - he),
            Point(conn_right + he,
                  conn_top + highlight_depth),
            ]
    mod.append(PolygoneLine(polygone=conn_highlight, layer='F.SilkS',
        width=.12))
    mod.append(PolygoneLine(
        polygone=list(map(lambda x: mirror_y(x, center), conn_highlight)),
        layer='F.SilkS', width=.12))



def build_din41612_connector(series, direction, pins, rows, extra_args={}):
    width = 'full'
    try:
        if series.split('/')[1] == '2':
            width = 'half'
            safe_series = series.split('/')[0] + '2'
        elif series.split('/')[1] == '3':
            width = 'third'
            safe_series = series.split('/')[0] + '3'
    except:
        safe_series = series

    config = dimensions.copy()
    config.update(config[direction])
    config.update(config[direction][width])
    config.update(config['series'][series.split('/')[0]])
    config.update(extra_args)

    used_rows = config['series_rows'].find(rows[-1])
    config['last_row_pos'] = used_rows * config['pin_row_offset']

    # generate base settings
    pins_per_row = pins // len(rows)
    extra_fp_name = ''
    if config.get('extra_desc') == 'rows':
        extra_fp_name += f"_Rows{rows.upper()}"
    footprint_name = (
        f"DIN41612_{safe_series}_{len(rows)}x{pins_per_row}"
        f"{extra_fp_name}_{direction}" )
    config['footprint_name'] = footprint_name
    mod = Footprint(footprint_name)
    mod.setDescription(f"DIN41612 connector, type {series}, {direction}, "
            f"{len(config['series_rows'])} rows"
            f"{config['row_pins']} pins wide, "
            )
    mod.setTags(f'DIN 41612 IEC 60603 {series}')
    model3d_path_prefix = '${KISYS3DMOD}/'
    mod.append(Model(filename=f'{model3d_path_prefix}{lib_name}.3dshapes/{footprint_name}.wrl'))

    if direction == 'Horizontal':
        build_din41612_connector_horizontal(mod, series, direction, pins, rows, config)
    else:
        build_din41612_connector_vertical(mod, series, direction, pins, rows, config)

    file_handler = KicadFileHandler(mod)
    file_handler.writeFile(f'{lib_name}.pretty/{footprint_name}.kicad_mod')
    return mod

connectors = {
        'B': [ (64, 'ab'), (32, 'a'), (32, 'ab') ],
        'B/2': [ (32, 'ab'), (16, 'ab') ],
        'B/3': [ (20, 'ab'), (10, 'ab') ],
        'C': [ (96, 'abc'), (64, 'ac'), (32, 'ac'), (32, 'a'), (48, 'abc') ],
        'C/2': [ (32, 'ac'), (48, 'abc') ],
        'C/3': [ (20, 'ac'), (30, 'abc') ],
#        'CD': [ (128, 'abcd') ], 
        'D': [ (32, 'ac'), (16, 'ac') ],
        'E': [ (32, 'ae'), (32, 'ac', dict(extra_desc='rows')), (48, 'ace') ],
#        'E160': [ (160, 'abcde') ],
#        'F_flat': [ (32, 'zb') (32, 'zd'), (48, 'zbd') ],
        'F': [ (32, 'zd'), (32, 'zb', dict(extra_desc='rows')), (48, 'zbd') ],
#        'H11': [ (11, 'e') ],
        'Q': [ (64, 'ab') ],
        'Q/2': [ (32, 'ab') ],
        'Q/3': [ (20, 'ab') ],
        'R': [ (64, 'ac'), (96, 'abc'), (48, 'abc'), (32, 'ac'), (32, 'a') ],
        'R/2': [ (48, 'abc'), (32, 'ac') ],
        'R/3': [ (30, 'abc'), (20, 'ac') ],
}

# TODO: Q R RD TE M H15 H7/F24
# TODO: Vertical
# make fab shape depend on mounting position not on front of connector
# TODO: check housing dimensions for all variants

for direction in ('Horizontal', 'Vertical'):
    for series, variants in connectors.items():
        for v in variants:
            pins = v[0]
            rows = v[1]
            if len(v) > 2:
                args = v[2]
            else:
                args = {}
            build_din41612_connector(series=series, direction=direction,
                    pins=pins, rows=rows, extra_args=args)
