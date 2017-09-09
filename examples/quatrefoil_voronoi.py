#!/usr/bin/python3
""" MLX logo and example script

Demonstrates how to use MLX as a design tool for a moderately complex project.

Units: mm

License:
    Copyright (C) 2017 by Tim Ayres, 3DLirious@gmail.com

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

import os
import time
import inspect
import math

import meshlabxml as mlx

THIS_SCRIPTPATH = os.path.dirname(
    os.path.realpath(inspect.getsourcefile(lambda: 0)))


def quatrefoil():
    """ Rainbow colored voronoi quatrefoil (3,4) torus knot """
    start_time = time.time()

    os.chdir(THIS_SCRIPTPATH)
    #ml_version = '1.3.4BETA'
    ml_version = '2016.12'

    # Add meshlabserver directory to OS PATH; omit this if it is already in
    # your PATH
    meshlabserver_path = 'C:\\Program Files\\VCG\\MeshLab'
    """
    if ml_version is '1.3.4BETA':
        meshlabserver_path = 'C:\\Program Files\\VCG\\MeshLab'
    elif ml_version is '2016.12':
        meshlabserver_path = 'C:\\Program Files\\VCG\\MeshLab_2016_12'
    """
    os.environ['PATH'] = meshlabserver_path + os.pathsep + os.environ['PATH']

    # Cross section parameters
    length = math.radians(360)
    tube_size = [10, 10, length]
    segments = [64, 64, 720*2]
    inner_radius = 2.0

    # Sinusoidal deformation parametera
    amplitude = 4.2
    freq = 4
    phase = 270
    center = 'r'
    start_pt = 0
    increment = 'z-{}'.format(start_pt)

    # Cyclic rainbow color parameters
    c_start_pt = 0
    c_freq = 5
    c_phase_shift = 0 #90 #300
    c_phase = (0 + c_phase_shift, 120 + c_phase_shift, 240 + c_phase_shift, 0)

    # Voronoi surface parameters
    holes = [2, 2, 44] # Number of holes in each axis; x are sides, y is outside
    web_thickness = 0.5
    solid_radius = 5.0 # If the mesh is smaller than this radius the holes will be closed
    faces_surface = 50000

    # Voronoi solid parameters
    voxel = 0.5
    thickness = 2.5
    faces_solid = 200000

    # Scaling parameters
    size = 75 # desired max size of the curve
    curve_max_size = 2*(1 + 1.5) # the 1.5 s/b inner_radius, but am keepng current scaling
    scale = (size-2*(thickness + amplitude) - tube_size[1])/curve_max_size

    # File names
    file_color = 'quatrefoil_color.ply'
    file_voronoi_surf = 'quatrefoil_voronoi_surf.ply'
    file_voronoi_solid = 'quatrefoil_voronoi_solid.ply'
    file_voronoi_color = 'quatrefoil_voronoi_final.ply'

    # Create FilterScript objects for each step in the process
    quatrefoil_color = mlx.FilterScript(
        file_in=None, file_out=file_color, ml_version=ml_version)
    quatrefoil_voronoi_surf = mlx.FilterScript(
        file_in=file_color, file_out=file_voronoi_surf, ml_version=ml_version)
    quatrefoil_voronoi_solid = mlx.FilterScript(
        file_in=file_voronoi_surf, file_out=file_voronoi_solid,
        ml_version=ml_version)
    quatrefoil_voronoi_color = mlx.FilterScript(
        file_in=[file_color, file_voronoi_solid], file_out=file_voronoi_color,
        ml_version=ml_version)


    print('\n Create colored quatrefoil curve ...')
    mlx.create.cube_open_hires(
        quatrefoil_color, size=tube_size, x_segments=segments[0],
        y_segments=segments[1], z_segments=segments[2], center=True)
    mlx.transform.translate(quatrefoil_color, [0, 0, length/2])

    # Sinusoidal deformation
    r_func = '({a})*sin(({f})*({i}) + ({p})) + ({c})'.format(
        f=freq, i=increment, p=math.radians(phase), a=amplitude, c=center)
    mlx.transform.function_cyl_co(
        quatrefoil_color, r_func=r_func, theta_func='theta', z_func='z')

    # Save max radius in quality field so that we can save it with the file
    #  for use in the next step
    max_radius = math.sqrt((tube_size[0]/2)**2+(tube_size[1]/2)**2) # at corners
    q_func = '({a})*sin(({f})*({i}) + ({p})) + ({c})'.format(
        f=freq, i=increment, p=math.radians(phase), a=amplitude, c=max_radius)
    mlx.mp_func.vq_function(quatrefoil_color, function=q_func)

    # Apply rainbow vertex colors
    mlx.vert_color.cyclic_rainbow(
        quatrefoil_color, direction='z', start_pt=c_start_pt, amplitude=255 / 2,
        center=255 / 2, freq=c_freq, phase=c_phase)

    # Deform mesh to quatrefoil curve. Merge vertices after, which
    # will weld the ends together so it becomes watertight
    quatrefoil_func = mlx.transform.deform2curve(
        quatrefoil_color,
        curve=mlx.mp_func.torus_knot('t', p=3, q=4, scale=scale,
                                     radius=inner_radius))
    mlx.clean.merge_vert(quatrefoil_color, threshold=0.0001)

    # Run script
    mlx.layers.delete_lower(quatrefoil_color)
    quatrefoil_color.run_script(output_mask='-m vc vq')

    print('\n Create Voronoi surface ...')
    # Move quality value into radius attribute
    mlx.mp_func.vert_attr(quatrefoil_voronoi_surf, name='radius', function='q')

    # Create seed vertices
    # For grid style holes, we will create a mesh similar to the original
    # but with fewer vertices.
    mlx.create.cube_open_hires(
        quatrefoil_voronoi_surf, size=tube_size, x_segments=holes[0]+1,
        y_segments=holes[1]+1, z_segments=holes[2]+1, center=True)
    mlx.select.all(quatrefoil_voronoi_surf, vert=False)
    mlx.delete.selected(quatrefoil_voronoi_surf, vert=False)
    mlx.select.cylindrical_vert(quatrefoil_voronoi_surf,
                                radius=max_radius-0.0001, inside=False)
    mlx.transform.translate(quatrefoil_voronoi_surf, [0, 0, 20])
    mlx.delete.selected(quatrefoil_voronoi_surf, face=False)

    mlx.transform.function_cyl_co(quatrefoil_voronoi_surf, r_func=r_func,
                                  theta_func='theta', z_func='z')
    mlx.transform.vert_function(
        quatrefoil_voronoi_surf, x_func=quatrefoil_func[0],
        y_func=quatrefoil_func[1], z_func=quatrefoil_func[2])

    mlx.layers.change(quatrefoil_voronoi_surf, 0)
    mlx.vert_color.voronoi(quatrefoil_voronoi_surf)

    if quatrefoil_voronoi_surf.ml_version == '1.3.4BETA':
        sel_func = '(q <= {}) or ((radius)<={})'.format(web_thickness, solid_radius)
    else:
        sel_func = '(q <= {}) || ((radius)<={})'.format(web_thickness, solid_radius)
    mlx.select.vert_function(quatrefoil_voronoi_surf, function=sel_func)
    #mlx.select.face_function(quatrefoil_voronoi_surf, function='(vsel0 && vsel1 && vsel2)')
    mlx.select.invert(quatrefoil_voronoi_surf, face=False)
    mlx.delete.selected(quatrefoil_voronoi_surf, face=False)

    mlx.smooth.laplacian(quatrefoil_voronoi_surf, iterations=3)
    mlx.remesh.simplify(quatrefoil_voronoi_surf, texture=False, faces=faces_surface)

    mlx.layers.delete_lower(quatrefoil_voronoi_surf)
    #quatrefoil_voronoi_surf.save_to_file('temp_script.mlx')
    quatrefoil_voronoi_surf.run_script(script_file=None, output_mask='-m vc vq')

    print('\n Solidify Voronoi surface ...')
    mlx.remesh.uniform_resampling(quatrefoil_voronoi_solid, voxel=voxel,
                                  offset=thickness/2, thicken=True)
    mlx.layers.delete_lower(quatrefoil_voronoi_solid)
    quatrefoil_voronoi_solid.run_script()

    print('\n Clean up & transfer color to final model ...')
    # Clean up from uniform mesh resamplng
    mlx.delete.small_parts(quatrefoil_voronoi_color)
    mlx.delete.unreferenced_vert(quatrefoil_voronoi_color)
    mlx.delete.faces_from_nonmanifold_edges(quatrefoil_voronoi_color)
    mlx.clean.split_vert_on_nonmanifold_face(quatrefoil_voronoi_color)
    mlx.clean.close_holes(quatrefoil_voronoi_color)

    # Simplify (to improve triangulation quality), refine, & smooth
    mlx.remesh.simplify(quatrefoil_voronoi_color, texture=False, faces=faces_solid)
    mlx.subdivide.ls3loop(quatrefoil_voronoi_color, iterations=1)
    mlx.smooth.laplacian(quatrefoil_voronoi_color, iterations=3)

    # Transfer colors from original curve
    mlx.transfer.vert_attr_2_meshes(
        quatrefoil_voronoi_color, source_mesh=0, target_mesh=1, color=True,
        max_distance=7)
    mlx.layers.delete_lower(quatrefoil_voronoi_color)
    quatrefoil_voronoi_color.run_script(script_file=None)
    print('    done! Took %.1f sec' % (time.time() - start_time))

    return None

if __name__ == '__main__':
    quatrefoil()
