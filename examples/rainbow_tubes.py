#!/usr/bin/python3
"""example MeshLabXML script to demonstrate functions

Sample script to demonstrate how MeshLab's powerful functions can be
used. Both mlx.transform.wrap2cylinder and mlx.vert_color.cyclic_rainbow
are based on MeshLab functions powered by muparser.

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

import meshlabxml as mlx

# Add meshlabserver directory to OS PATH; omit this if it is already in
# your PATH
MESHLABSERVER_PATH = 'C:\\Program Files\\VCG\\MeshLab'
os.environ['PATH'] += os.pathsep + MESHLABSERVER_PATH


def main():
    """Run main script"""

    script1 = 'TEMP3D_tube1.mlx'
    mesh1 = 'TEMP3D_tube1.ply'
    script2 = 'TEMP3D_tube2.mlx'
    mesh2 = 'TEMP3D_tube2.ply'
    input3 = [mesh1, mesh2]
    script3 = 'TEMP3D_join.mlx'
    final_output = 'ranbow_tubes.ply'

    mlx.begin(script1)
    mlx.create.tube_hires(
        script1,
        height=165,
        radius1=1,
        radius2=0.7,
        cir_segments=32,
        rad_segments=1,
        height_segments=165,
        center=True)
    mlx.transform.rotate(script1, 'y', -90)
    mlx.transform.wrap2cylinder(script1, radius=3, pitch=8)
    mlx.end(script1)
    mlx.run(script=script1, file_out=mesh1)

    mlx.begin(script2)
    mlx.create.tube_hires(
        script2,
        height=300,
        radius1=1.5,
        radius2=1,
        cir_segments=32,
        rad_segments=1,
        height_segments=300,
        center=True)
    mlx.transform.rotate(script2, 'y', -90)
    mlx.transform.wrap2cylinder(script2, radius=6, pitch=-8)
    mlx.end(script2)
    mlx.run(script=script2, file_out=mesh2)

    mlx.begin(script3, file_in=input3)
    mlx.layers.join(script3)
    mlx.vert_color.cyclic_rainbow(script3, freq=0.8)
    mlx.transform.rotate(script3, 'y', -90)
    mlx.transform.wrap2cylinder(script3, radius=20, pitch=0)
    mlx.end(script3)
    mlx.run(script=script3, file_out=final_output, file_in=input3)

    wait = input(
        '\nPress ENTER to delete TEMP3D* files, or type "n" to keep them: ')
    if wait == '':
        mlx.util.delete_all('TEMP3D*')

if __name__ == '__main__':
    main()
