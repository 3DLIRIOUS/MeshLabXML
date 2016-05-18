#!/usr/bin/python3
"""example MeshLabXML script to create a heroic shield

MeshLab is typically used to process existing meshes; this script was created to demonstrate some of MeshLab's mesh creation features as well. It demonstrates combining python functionality (math and flow control) and MeshLab to create a parametric 3D model that's truly heroic!

Note that the final model is composed of separate surfaces. It is not manifold and is e.g. not suitable for 3D printing; it's just a silly example.

License:
    Written in 2016 by Tim Ayres 3DLirious@gmail.com

    To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.

    You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
"""

#Builtin modules
import os, sys, inspect
from math import *

#Add parent directory to python path for importing local modules; omit this if module is already in path. This assumes that this script is in the "examples" directory and meshlabxml.py is in the parent.
scriptpath = os.path.dirname(os.path.realpath(inspect.getsourcefile(lambda:0)))
sys.path.append(os.path.join(scriptpath,os.pardir))

#Local modules
import meshlabxml as mlx

# Add meshlabserver directory to OS PATH; omit this if it is already in your PATH
meshlabserver_path = 'C:\\Program Files\\VCG\\MeshLab'
os.environ['PATH'] += os.pathsep + meshlabserver_path

# fn = number of segments to use for circles
fn = 50
# starPoints = number of points (or sides) of the star
starPoints = 5
# r = radius of circle circumscribing the star
r = 2
# ring = thickness of the colored rings
ring = 1
# sphereR = radius of sphere the shield will be deformed to
sphereR = 2*(r + 3*ring)

# Star calculations:
# Visually approximate a star by using multiple diamonds (i.e. scaled  squares) which overlap in the center. For the star calculations, consider a central polygon with triangles attached to the edges, all circumscribed by a circle.
# p = distance from center of circle to polygon edge midpoint
p = r/(1 + tan(radians(180/starPoints))/tan(radians(90/starPoints)))
# w = 1/2 width of polygon edge/outer triangle bottom
w = p*tan(radians(180/starPoints))
# h = height of outer triangle
h = w/tan(radians(90/starPoints))


# This function always comes first and starts the mlx script
mlx.begin()

# Create the colored front of the shield using several concentric annuluses; combine them together and subdivide so we have more vertices to give a smoother deformation later.
mlx.annulus(r=r, segmentsC=fn, color='blue')
mlx.annulus(r1=r+ring, r2=r, segmentsC=fn, color='red')
mlx.annulus(r1=r+2*ring, r2=r+ring, segmentsC=fn, color='white')
mlx.annulus(r1=r+3*ring, r2=r+2*ring, segmentsC=fn, color='red')
mlx.join_L()
mlx.subdivide_midpoint(iterations=2)

# Create the inside surface of the shield & translate down slightly so it doesn't overlap the front.
mlx.annulus(r1=r+3*ring, segmentsC=fn, color='silver')
mlx.rotate(axis='y', angle=180)
mlx.translate(amount=[0,0,-0.005])
mlx.subdivide_midpoint(iterations=4)

# Create a diamond for the center star. First create a plane, specifying extra vertices to support the final deformation. The length from the center of the plane to the corners should be 1 for ease of scaling, so we use a side length of sqrt(2) (thanks Pythagoras!). Rotate the plane by 45 degrees and scale it to stretch it out per the calculations above, then translate it into place (including moving it up in z slightly so that it doesn't overlap the shield front).
mlx.plane(size=sqrt(2), segmentsX=10, segmentsY=10, center=True, color='white')
mlx.rotate(axis='z', angle=45)
mlx.scale(amount=[w,h,1])
mlx.translate(amount=[0,p,0.001])

# Duplicate the diamond and rotate the duplicates around, generating the star.
for a in range(1,starPoints):
    mlx.duplicate_L()
    mlx.rotate(axis='z', angle=360/starPoints)

# Combine everything together and deform using a spherical function.
mlx.join_L()
mlx.deform_func(z='sqrt(%s-x^2-y^2)-%s+z' % (sphereR**2, sphereR))

# This function always comes last and ends the mlx script
mlx.end()

# Run the script using meshlabserver and generate the model
mlx.run(o="Cap's_shield.ply")

wait = input('\nPress ENTER to delete MLTEMP* files, or type "n" to keep them: ')
if wait == '':
    mlx.delete_all('MLTEMP*')
