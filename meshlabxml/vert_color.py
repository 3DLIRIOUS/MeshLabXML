""" MeshLabXML vertex color functions """

import math

from . import util


def function(script='TEMP3D_default.mlx', red=255, green=255,
             blue=255, alpha=255, color=None, current_layer=None,
             last_layer=None):
    """
    Color function using muparser lib to generate new RGBA color for every
    vertex. Red, Green, Blue and Alpha channels may be defined specifying
    a function in their respective fields.
    It's possible to use the following per-vertex variables in the
    expression:
      x,y,z (position),
      nx,ny,nz (normal),
      r,g,b,a (color),
      q (quality),
      rad (radius),
      vi (vertex index),
      vtu,vtv,ti (texture coords and texture index),
      vsel (is the vertex selected? 1 yes, 0 no)
      and all custom vertex attributes already defined by user.
    Function should produce values in the range 0-255
    """

    if color is not None:
        red, green, blue = util.color_values(color)

    script_file = open(script, 'a')
    script_file.write('  <filter name="Per Vertex Color Function">\n' +

                 '    <Param name="x" ' +
                 'value="%s" ' % str(red).replace('<', '&lt;') +
                 'description="func r = " ' +
                 'type="RichString" ' +
                 'tooltip="Function to generate Red component. Expected Range' +
                 ' 0-255"/>\n' +

                 '    <Param name="y" ' +
                 'value="%s" ' % str(green).replace('<', '&lt;') +
                 'description="func g = " ' +
                 'type="RichString" ' +
                 'tooltip="Function to generate Green component. Expected Range' +
                 ' 0-255"/>\n' +

                 '    <Param name="z" ' +
                 'value="%s" ' % str(blue).replace('<', '&lt;') +
                 'description="func b = " ' +
                 'type="RichString" ' +
                 'tooltip="Function to generate Blue component. Expected Range' +
                 ' 0-255"/>\n' +

                 '    <Param name="a" ' +
                 'value="%s" ' % str(alpha).replace('<', '&lt;') +
                 'description="func alpha = " ' +
                 'type="RichString" ' +
                 'tooltip="Function to generate Alpha component. Expected Range' +
                 ' 0-255"/>\n' +

                 '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def voronoi(script='TEMP3D_default.mlx', target_layer=0,
            source_layer=1, backward=True,
            current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Voronoi Vertex Coloring">\n' +

                 '    <Param name="ColoredMesh" ' +
                 'value="%d" ' % target_layer +
                 'description="To be Colored Mesh" ' +
                 'type="RichMesh" ' +
                 'tooltip="The mesh whose surface is colored. For each vertex' +
                 ' of this mesh we decide the color according the below' +
                 ' parameters."/>\n' +

                 '    <Param name="VertexMesh" ' +
                 'value="%d" ' % source_layer +
                 'description="Vertex Mesh" ' +
                 'type="RichMesh" ' +
                 'tooltip="The mesh whose vertexes are used as seed points for' +
                 ' the color computation. These seeds point are projected onto' +
                 ' the above mesh."/>\n' +

                 '    <Param name="backward" ' +
                 'value="%s" ' % str(backward).lower() +
                 'description="BackDistance" ' +
                 'type="RichBool" ' +
                 'tooltip="If true the mesh is colored according the distance' +
                 ' from the frontier of the voronoi diagram induced by the' +
                 ' VertexMesh seeds."/>\n' +

                 '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def cyclic_rainbow(script='TEMP3D_default.mlx', direction='sphere',
                   start_pt=[0, 0, 0], amplitude=255 / 2, center=255 / 2,
                   freq=0.8,
                   phase=[0, 120, 240, 0],
                   alpha=False, current_layer=None, last_layer=None):
    """Color your mesh vertices in a repeating rainbow pattern
    direction = sphere, x, y, z, function
    start_pt = start point of color function. For a sphere this is the center of the sphere.
    amplitude = amplitude, between 0-255
    center = center, between 0-255
    freq = frequency
    phase = phase
    """
    start_pt = util.check_list(start_pt, 3)
    amplitude = util.check_list(amplitude, 4)
    center = util.check_list(center, 4)
    freq = util.check_list(freq, 4)
    phase = util.check_list(phase, 4)

    if direction.lower() == 'sphere':
        increment = 'sqrt((x-%s)^2+(y-%s)^2+(z-%s)^2)' % (
            start_pt[0], start_pt[1], start_pt[2])
    elif direction.lower() == 'x':
        increment = 'x - %s' % start_pt[0]
    elif direction.lower() == 'y':
        increment = 'y - %s' % start_pt[1]
    elif direction.lower() == 'z':
        increment = 'z - %s' % start_pt[2]
    else:
        increment = direction

    red_func = 'sin(%s*%s + %s)*%s + %s' % (freq[0], increment, math.radians(phase[0]),
                                            amplitude[0], center[0])
    green_func = 'sin(%s*%s + %s)*%s + %s' % (freq[1], increment, math.radians(phase[1]),
                                              amplitude[1], center[1])
    blue_func = 'sin(%s*%s + %s)*%s + %s' % (freq[2], increment, math.radians(phase[2]),
                                             amplitude[2], center[2])
    if alpha:
        alpha_func = 'sin(%s*%s + %s)*%s + %s' % (freq[3],
                                                  increment, math.radians(phase[3]), amplitude[3], center[3])
    else:
        alpha_func = 255

    function(script, red=red_func, green=green_func, blue=blue_func,
             alpha=alpha_func)
    return current_layer, last_layer
