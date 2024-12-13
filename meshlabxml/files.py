""" MeshLabXML functions that operate on mesh files """

import os
import sys
import math

import meshlabxml as mlx
from . import run
from . import util
from . import compute
from . import transform
from . import layers

#ml_version = '1.3.4BETA'
#ml_version = '2016.12'
ml_version = '2020.09'

def measure_aabb(fbasename=None, log=None, coord_system='CARTESIAN'):
    """ Measure the axis aligned bounding box (aabb) of a mesh
    in multiple coordinate systems.

    Args:
        fbasename (str): filename of input model
        log (str): filename of log file
        coord_system (enum in ['CARTESIAN', 'CYLINDRICAL']
            Coordinate system to use:
                'CARTESIAN': lists contain [x, y, z]
                'CYLINDRICAL': lists contain [r, theta, z]
    Returns:
        dict: dictionary with the following aabb properties
            min (3 element list): minimum values
            max (3 element list): maximum values
            center (3 element list): the center point
            size (3 element list): size of the aabb in each coordinate (max-min)
            diagonal (float): the diagonal of the aabb
    """
    # TODO: add center point, spherical coordinate system
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    if fext != 'xyz':
        fin = 'TEMP3D_aabb.xyz'
        run(log=log, file_in=fbasename, file_out=fin, script=None)
    else:
        fin = fbasename
    fread = open(fin, 'r')
    aabb = {'min': [999999.0, 999999.0, 999999.0], 'max': [-999999.0, -999999.0, -999999.0]}
    for line in fread:
        x_co, y_co, z_co = line.split()
        x_co = util.to_float(x_co)
        y_co = util.to_float(y_co)
        z_co = util.to_float(z_co)
        if coord_system == 'CARTESIAN':
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
        elif coord_system == 'CYLINDRICAL':
            radius = math.sqrt(x_co**2 + y_co**2)
            theta = math.degrees(math.atan2(y_co, x_co))
            if radius < aabb['min'][0]:
                aabb['min'][0] = radius
            if theta < aabb['min'][1]:
                aabb['min'][1] = theta
            if z_co < aabb['min'][2]:
                aabb['min'][2] = z_co
            if radius > aabb['max'][0]:
                aabb['max'][0] = radius
            if theta > aabb['max'][1]:
                aabb['max'][1] = theta
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
            print('{:10} = {}'.format(key, value))
        else:
            log_file = open(log, 'a')
            log_file.write('{:10} = {}\n'.format(key, value))
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


def measure_section(fbasename=None, log=None, axis='z', offset=0.0,
                    rotate_x_angle=None, ml_version=ml_version):
    """Measure a cross section of a mesh
    
    Perform a plane cut in one of the major axes (X, Y, Z). If you want to cut on
    a different plane you will need to rotate the model in place, perform the cut,
    and rotate it back.
    
    Args:
        fbasename (str): filename of input model
        log (str): filename of log file
        axis (str): axis perpendicular to the cutting plane, e.g. specify "z" to cut
            parallel to the XY plane.
        offset (float): amount to offset the cutting plane from the origin
        rotate_x_angle (float): degrees to rotate about the X axis. Useful for correcting "Up" direction: 90 to rotate Y to Z, and -90 to rotate Z to Y. 

    Returns:
        dict: dictionary with the following keys for the aabb of the section:
            min (list): list of the x, y & z minimum values
            max (list): list of the x, y & z maximum values
            center (list): the x, y & z coordinates of the center of the aabb
            size (list): list of the x, y & z sizes (max - min)
            diagonal (float): the diagonal of the aabb
    """
    ml_script1_file = 'TEMP3D_measure_section.mlx'
    file_out = 'TEMP3D_sect_aabb.xyz'

    ml_script1 = mlx.FilterScript(file_in=fbasename, file_out=file_out, ml_version=ml_version)
    if rotate_x_angle is not None:
        transform.rotate(ml_script1, axis='x', angle=rotate_x_angle)
    compute.section(ml_script1, axis=axis, offset=offset)
    layers.delete_lower(ml_script1)
    ml_script1.save_to_file(ml_script1_file)
    ml_script1.run_script(log=log, script_file=ml_script1_file)
    aabb = measure_aabb(file_out, log)
    return aabb


def polylinesort(fbasename=None, log=None):
    """Sort separate line segments in obj format into a continuous polyline or polylines.
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
            p1 = x_co
            p2 = y_co
            line_segments.append([int(p1), int(p2)])

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


def measure_geometry(fbasename=None, log=None, ml_version=ml_version):
    """Measures mesh geometry, including aabb"""
    ml_script1_file = 'TEMP3D_measure_geometry.mlx'
    if ml_version == '1.3.4BETA':
        file_out = 'TEMP3D_aabb.xyz'
    else:
        file_out = None

    ml_script1 = mlx.FilterScript(file_in=fbasename, file_out=file_out, ml_version=ml_version)
    compute.measure_geometry(ml_script1)
    ml_script1.save_to_file(ml_script1_file)
    ml_script1.run_script(log=log, script_file=ml_script1_file)
    geometry = ml_script1.geometry

    if ml_version == '1.3.4BETA':
        if log is not None:
            log_file = open(log, 'a')
            log_file.write(
                '***Axis Aligned Bounding Results for file "%s":\n' %
                fbasename)
            log_file.close()
        aabb = measure_aabb(file_out, log)
    else:
        aabb = geometry['aabb']
    return aabb, geometry


def measure_topology(fbasename=None, log=None, ml_version=ml_version):
    """Measures mesh topology

    Args:
        fbasename (str): input filename.
        log (str): filename to log output

    Returns:
        dict: dictionary with the following keys:
            vert_num (int): number of vertices
            edge_num (int): number of edges
            face_num (int): number of faces
            unref_vert_num (int): number or unreferenced vertices
            boundry_edge_num (int): number of boundary edges
            part_num (int): number of parts (components) in the mesh.
            manifold (bool): True if mesh is two-manifold, otherwise false.
            non_manifold_edge (int): number of non_manifold edges.
            non_manifold_vert (int): number of non-manifold verices
            genus (int or str): genus of the mesh, either a number or
                'undefined' if the mesh is non-manifold.
            holes (int or str): number of holes in the mesh, either a number
                or 'undefined' if the mesh is non-manifold.

    """
    ml_script1_file = 'TEMP3D_measure_topology.mlx'
    ml_script1 = mlx.FilterScript(file_in=fbasename, ml_version=ml_version)
    compute.measure_topology(ml_script1)
    ml_script1.save_to_file(ml_script1_file)
    ml_script1.run_script(log=log, script_file=ml_script1_file)
    topology = ml_script1.topology
    return topology


def measure_all(fbasename=None, log=None, ml_version=ml_version):
    """Measures mesh geometry, aabb and topology."""
    ml_script1_file = 'TEMP3D_measure_gAndT.mlx'
    if ml_version == '1.3.4BETA':
        file_out = 'TEMP3D_aabb.xyz'
    else:
        file_out = None

    ml_script1 = mlx.FilterScript(file_in=fbasename, file_out=file_out, ml_version=ml_version)
    compute.measure_geometry(ml_script1)
    compute.measure_topology(ml_script1)
    ml_script1.save_to_file(ml_script1_file)
    ml_script1.run_script(log=log, script_file=ml_script1_file)
    geometry = ml_script1.geometry
    topology = ml_script1.topology

    if ml_version == '1.3.4BETA':
        if log is not None:
            log_file = open(log, 'a')
            log_file.write(
                '***Axis Aligned Bounding Results for file "%s":\n' %
                fbasename)
            log_file.close()
        aabb = measure_aabb(file_out, log)
    else:
        aabb = geometry['aabb']
    return aabb, geometry, topology


def measure_dimension(fbasename=None, log=None, axis1=None, offset1=0.0,
                      axis2=None, offset2=0.0, ml_version=ml_version):
    """Measure a dimension of a mesh"""
    axis1 = axis1.lower()
    axis2 = axis2.lower()
    ml_script1_file = 'TEMP3D_measure_dimension.mlx'
    file_out = 'TEMP3D_measure_dimension.xyz'

    ml_script1 = mlx.FilterScript(file_in=fbasename, file_out=file_out, ml_version=ml_version)
    compute.section(ml_script1, axis1, offset1, surface=True)
    compute.section(ml_script1, axis2, offset2, surface=False)
    layers.delete_lower(ml_script1)
    ml_script1.save_to_file(ml_script1_file)
    ml_script1.run_script(log=log, script_file=ml_script1_file)

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
