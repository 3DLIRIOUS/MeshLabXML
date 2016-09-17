""" MeshLabXML functions that operate on mesh files """

import os
import sys
import math

from . import run, begin, end
from . import util
from . import compute


def measure_aabb(fbasename=None, log=None):
    """Measure the Axis Aligned Bounding Box of a mesh"""
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    if fext != 'xyz':
        fin = 'TEMP3D_aabb.xyz'
        run(log=log, file_in=fbasename, file_out=fin, script=None)
    else:
        fin = fbasename
    fread = open(fin, 'r')
    first = True
    for line in fread:
        x_co, y_co, z_co = line.split()
        x_co = util.to_float(x_co)
        y_co = util.to_float(y_co)
        z_co = util.to_float(z_co)
        if first:
            aabb = {'min': [x_co, y_co, z_co], 'max': [x_co, y_co, z_co]}
            first = False
        if x_co < aabb['min'][0]:
            aabb['min'][0] = x_co
        if y_co < aabb['min'][1]:
            aabb['min'][1] = y_co
        if z_co < aabb['min'][2]:
            aabb['min'][2] = z_co
        if x_co > aabb['max'][0]:
            aabb['max'][0] = x_co
        if y_co > aabb['max'][1]:
            aabb['max'][1] = y_co
        if z_co > aabb['max'][2]:
            aabb['max'][2] = z_co
    fread.close()
    try:
        aabb['center'] = [(aabb['max'][0] + aabb['min'][0]) / 2,
                          (aabb['max'][1] + aabb['min'][1]) / 2,
                          (aabb['max'][2] + aabb['min'][2]) / 2]
        aabb['size'] = [aabb['max'][0] - aabb['min'][0], aabb['max'][1] - aabb['min'][1],
                        aabb['max'][2] - aabb['min'][2]]
        aabb['diagonal'] = math.sqrt(
            aabb['size'][0]**2 +
            aabb['size'][1]**2 +
            aabb['size'][2]**2)
    except UnboundLocalError:
        print('Error: aabb input file does not contain valid data. Exiting ...')
        sys.exit(1)
    for key, value in aabb.items():
        if log is None:
            print('%s = %s' % (key, value))
        else:
            log_file = open(log, 'a')
            log_file.write('%s = %s\n'  % (key, value))
            log_file.close()
    """
    if log is not None:
        log_file = open(log, 'a')
        #log_file.write('***Axis Aligned Bounding Results for file "%s":\n' % fbasename)
        log_file.write('min = %s\n' % aabb['min'])
        log_file.write('max = %s\n' % aabb['max'])
        log_file.write('center = %s\n' % aabb['center'])
        log_file.write('size = %s\n' % aabb['size'])
        log_file.write('diagonal = %s\n\n' % aabb['diagonal'])
        log_file.close()
    # print(aabb)
    """
    return aabb


def polylinesort(fbasename=None, log=None):
    """Sort separate line segments in obj format into a continous polyline or polylines.
    NOT FINISHED; DO NOT USE

    Also measures the length of each polyline

    Return polyline and polylineMeta (lengths)

    """
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    if fext != 'obj':
        print('Input file must be obj. Exiting ...')
        sys.exit(1)
    fread = open(fbasename, 'r')
    first = True
    polyline_vertices = []
    line_segments = []
    for line in fread:
        element, x_co, y_co, z_co = line.split()
        if element == 'v':
            polyline_vertices.append(
                [util.to_float(x_co), util.to_float(y_co), util.to_float(z_co)])
        elif element == 'l':
            # x and y are really p1 and p2
            line_segments.append([int(x_co), int(y_co)])

    fread.close()
    if log is not None:
        log_file = open(log, 'a')
        #log_file.write('***Axis Aligned Bounding Results for file "%s":\n' % fbasename)
        """log_file.write('min = %s\n' % aabb['min'])
        log_file.write('max = %s\n' % aabb['max'])
        log_file.write('center = %s\n' % aabb['center'])
        log_file.write('size = %s\n' % aabb['size'])
        log_file.write('diagonal = %s\n' % aabb['diagonal'])"""
        log_file.close()
    # print(aabb)
    return None


def measure_geometry(fbasename=None, log=None):
    """Measures mesh geometry. Also runs measure_aabb"""
    script = 'TEMP3D_measure_geometry.mlx'
    ml_log = 'TEMP3D_measure_geometry_log.txt'
    file_in = fbasename
    file_out = 'TEMP3D_aabb.xyz'

    begin(script, file_in)
    compute.measure_geometry(script)
    end(script)
    run(log=log, ml_log=ml_log, file_in=file_in, file_out=file_out, script=script)

    if log is not None:
        log_file = open(log, 'a')
        log_file.write(
            '***Axis Aligned Bounding Results for file "%s":\n' %
            fbasename)
        log_file.close()
    aabb = measure_aabb(file_out, log)

    if log is not None:
        log_file = open(log, 'a')
        log_file.write(
            '***Parsed Geometry Values for file "%s":\n' %
            fbasename)
        log_file.close()
    geometry = compute.parse_geometry(ml_log, log)
    return aabb, geometry


def measure_all(fbasename=None, log=None):
    """Measures mesh geometry, aabb and topology."""
    script = 'TEMP3D_measure_gAndT.mlx'
    ml_log = 'TEMP3D_measure_gAndT_log.txt'
    file_in = fbasename
    file_out = 'TEMP3D_aabb.xyz'
    begin(script, file_in)
    compute.measure_geometry(script)
    compute.measure_topology(script)
    end(script)
    run(log=log, ml_log=ml_log, file_in=file_in, file_out=file_out, script=script)

    if log is not None:
        log_file = open(log, 'a')
        log_file.write(
            '***Axis Aligned Bounding Results for file "%s":\n' %
            fbasename)
        log_file.close()
    aabb = measure_aabb(file_out, log)

    if log is not None:
        log_file = open(log, 'a')
        log_file.write(
            '***Parsed Geometry Values for file "%s":\n' %
            fbasename)
        log_file.close()
    geometry = compute.parse_geometry(ml_log, log)

    if log is not None:
        log_file = open(log, 'a')
        log_file.write(
            '***Parsed Topology Values for file "%s":\n' %
            fbasename)
        log_file.close()
    topology = compute.parse_topology(ml_log, log)
    return aabb, geometry, topology


def measure_dimension(fbasename=None, log=None, axis1=None, offset1=0.0,
                      axis2=None, offset2=0.0):
    """Measure a dimension of a mesh"""
    axis1 = axis1.lower()
    axis2 = axis2.lower()
    script = 'TEMP3D_measure_dimension.mlx'
    file_out = 'TEMP3D_measure_dimension.xyz'
    begin(script, fbasename)
    compute.section(script, axis1, offset1, surface=True)
    compute.section(script, axis2, offset2, surface=False)
    end(script)
    run(log=log, file_in=fbasename, file_out=file_out, script=script)

    for val in ('x', 'y', 'z'):
        if val not in (axis1, axis2):
            axis = val
    # ord: Get number that represents letter in ASCII
    # Here we find the offset from 'x' to determine the list reference
    # i.e. 0 for x, 1 for y, 2 for z
    axis_num = ord(axis) - ord('x')
    aabb = measure_aabb(file_out, log)
    dimension = {'min': aabb['min'][axis_num], 'max': aabb['max'][axis_num],
                 'length': aabb['size'][axis_num], 'axis': axis}
    if log is None:
        print('\nFor file "%s"' % fbasename)
        print('Dimension parallel to %s with %s=%s & %s=%s:' % (axis, axis1, offset1,
                                                                axis2, offset2))
        print('  Min = %s, Max = %s, Total length = %s' % (dimension['min'],
                                                           dimension['max'], dimension['length']))
    else:
        log_file = open(log, 'a')
        log_file.write('\nFor file "%s"\n' % fbasename)
        log_file.write('Dimension parallel to %s with %s=%s & %s=%s:\n' % (axis, axis1, offset1,
                                                                           axis2, offset2))
        log_file.write('min = %s\n' % dimension['min'])
        log_file.write('max = %s\n' % dimension['max'])
        log_file.write('Total length = %s\n' % dimension['length'])
        log_file.close()
    return dimension
