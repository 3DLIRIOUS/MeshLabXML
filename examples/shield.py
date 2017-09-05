#!/usr/bin/python3
"""Example MeshLabXML script to create a heroic shield.

MeshLab is typically used to process existing meshes; this script was
created to demonstrate some of MeshLab's mesh creation features as well.
It demonstrates combining python functionality (math and flow control)
and MeshLab to create a parametric 3D model that's truly heroic!

Note that the final model is composed of separate surfaces. It is not
manifold and is e.g. not suitable for 3D printing; it's just a silly
example.

License:
    Written in 2016 by Tim Ayres 3DLirious@gmail.com

    To the extent possible under law, the author(s) have dedicated all
    copyright and related and neighboring rights to this software to the
    public domain worldwide. This software is distributed without any
    warranty.

    You should have received a copy of the CC0 Public Domain Dedication
    along with this software. If not, see
    <http://creativecommons.org/publicdomain/zero/1.0/>.

"""

import os
import math

import meshlabxml as mlx

# Add meshlabserver directory to OS PATH; omit this if it is already in
# your PATH
MESHLABSERVER_PATH = 'C:\\Program Files\\VCG\\MeshLab'
os.environ['PATH'] += os.pathsep + MESHLABSERVER_PATH


def main():
    """Run main script"""
    # segments = number of segments to use for circles
    segments = 50
    # star_points = number of points (or sides) of the star
    star_points = 5
    # star_radius = radius of circle circumscribing the star
    star_radius = 2
    # ring_thickness = thickness of the colored rings
    ring_thickness = 1
    # sphere_radius = radius of sphere the shield will be deformed to
    sphere_radius = 2 * (star_radius + 3 * ring_thickness)

    # Star calculations:
    # Visually approximate a star by using multiple diamonds (i.e. scaled
    # squares) which overlap in the center. For the star calculations,
    # consider a central polygon with triangles attached to the edges, all
    # circumscribed by a circle.
    # polygon_radius = distance from center of circle to polygon edge midpoint
    polygon_radius = star_radius / \
        (1 + math.tan(math.radians(180 / star_points)) /
         math.tan(math.radians(90 / star_points)))
    # width = 1/2 width of polygon edge/outer triangle bottom
    width = polygon_radius * math.tan(math.radians(180 / star_points))
    # height = height of outer triangle
    height = width / math.tan(math.radians(90 / star_points))

    shield = mlx.FilterScript(file_out="shield.ply")

    # Create the colored front of the shield using several concentric
    # annuluses; combine them together and subdivide so we have more vertices
    # to give a smoother deformation later.
    mlx.create.annulus(shield, radius=star_radius, cir_segments=segments, color='blue')
    mlx.create.annulus(shield,
        radius1=star_radius + ring_thickness,
        radius2=star_radius,
        cir_segments=segments,
        color='red')
    mlx.create.annulus(shield,
        radius1=star_radius + 2 * ring_thickness,
        radius2=star_radius + ring_thickness,
        cir_segments=segments,
        color='white')
    mlx.create.annulus(shield,
        radius1=star_radius + 3 * ring_thickness,
        radius2=star_radius + 2 * ring_thickness,
        cir_segments=segments,
        color='red')
    mlx.layers.join(shield)
    mlx.subdivide.midpoint(shield, iterations=2)

    # Create the inside surface of the shield & translate down slightly so it
    # doesn't overlap the front.
    mlx.create.annulus(shield,
        radius1=star_radius + 3 * ring_thickness,
        cir_segments=segments,
        color='silver')
    mlx.transform.rotate(shield, axis='y', angle=180)
    mlx.transform.translate(shield, value=[0, 0, -0.005])
    mlx.subdivide.midpoint(shield, iterations=4)

    # Create a diamond for the center star. First create a plane, specifying
    # extra vertices to support the final deformation. The length from the
    # center of the plane to the corners should be 1 for ease of scaling, so
    # we use a side length of sqrt(2) (thanks Pythagoras!). Rotate the plane
    # by 45 degrees and scale it to stretch it out per the calculations above,
    # then translate it into place (including moving it up in z slightly so
    # that it doesn't overlap the shield front).
    mlx.create.grid(shield,
        size=math.sqrt(2),
        x_segments=10,
        y_segments=10,
        center=True,
        color='white')
    mlx.transform.rotate(shield, axis='z', angle=45)
    mlx.transform.scale(shield, value=[width, height, 1])
    mlx.transform.translate(shield, value=[0, polygon_radius, 0.001])

    # Duplicate the diamond and rotate the duplicates around, generating the
    # star.
    for _ in range(1, star_points):
        mlx.layers.duplicate(shield)
        mlx.transform.rotate(shield, axis='z', angle=360 / star_points)

    # Combine everything together and deform using a spherical function.
    mlx.layers.join(shield)
    mlx.transform.vert_function(shield,
        z_func='sqrt(%s-x^2-y^2)-%s+z' %
        (sphere_radius**2, sphere_radius))

    # Run the script using meshlabserver and generate the model
    shield.run_script()
    return None

if __name__ == '__main__':
    main()
