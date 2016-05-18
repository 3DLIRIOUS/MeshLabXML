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

s1 = 'MLTEMP_tube1.mlx'
o1 = 'MLTEMP_tube1.ply'
s2 = 'MLTEMP_tube2.mlx'
o2 = 'MLTEMP_tube2.ply'
i3 = [o1, o2]
s3 = 'MLTEMP_join.mlx'
o3 = 'ranbow_tubes.ply'

mlx.begin(s1)
mlx.tube_hires(s1, h=165, r1=1, r2=0.7, segmentsC=32, segmentsR=1, segmentsH=165, center=True)
mlx.rotate(s1, 'y', -90)
mlx.deform2cylinder(s1, r=3, pitch=8)
mlx.end(s1)
mlx.run(s=s1, o=o1)

mlx.begin(s2)
mlx.tube_hires(s2, h=300, r1=1.5, r2=1, segmentsC=32, segmentsR=1, segmentsH=300, center=True)
mlx.rotate(s2, 'y', -90)
mlx.deform2cylinder(s2, r=6, pitch=-8)
mlx.end(s2)
mlx.run(s=s2, o=o2)

mlx.begin(s3, i=i3)
mlx.join_L(s3)
mlx.color_V_cyclic_rainbow(s3, f=0.8)
mlx.rotate(s3, 'y', -90)
mlx.deform2cylinder(s3, r=20, pitch=0)
mlx.end(s3)
mlx.run(s=s3, o=o3, i=i3)

wait = input('\nPress ENTER to delete MLTEMP* files, or type "n" to keep them: ')
if wait == '':
    mlx.delete_all('MLTEMP*')
