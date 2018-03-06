""" MeshLabXML vertex color functions """

import math

from . import util
from .color_names import color_name

def function(script, red=255, green=255, blue=255, alpha=255, color=None):
    """Color function using muparser lib to generate new RGBA color for every
        vertex

    Red, Green, Blue and Alpha channels may be defined by specifying a function
    for each.

    See help(mlx.muparser_ref) for muparser reference documentation.

    It's possible to use the following per-vertex variables in the expression:

    Variables (per vertex):
        x, y, z (coordinates)
        nx, ny, nz (normal)
        r, g, b, a (color)
        q (quality)
        rad (radius)
        vi (vertex index)
        vtu, vtv (texture coordinates)
        ti (texture index)
        vsel (is the vertex selected? 1 yes, 0 no)
        and all custom vertex attributes already defined by user.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        red (str [0, 255]): function to generate red component
        green (str [0, 255]): function to generate green component
        blue (str [0, 255]): function to generate blue component
        alpha (str [0, 255]): function to generate alpha component
        color (str): name of one of the 140 HTML Color Names defined
            in CSS & SVG.
            Ref: https://en.wikipedia.org/wiki/Web_colors#X11_color_names
            If not None this will override the per component variables.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    # TODO: add options for HSV
    # https://www.cs.rit.edu/~ncs/color/t_convert.html
    if color is not None:
        red, green, blue, _ = color_name[color.lower()]
    filter_xml = ''.join([
        '  <filter name="Per Vertex Color Function">\n',
        '    <Param name="x" ',
        'value="{}" '.format(str(red).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func r = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="y" ',
        'value="{}" '.format(str(green).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func g = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="z" ',
        'value="{}" '.format(str(blue).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func b = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="a" ',
        'value="{}" '.format(str(alpha).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func alpha = " ',
        'type="RichString" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def voronoi(script, target_layer=0, source_layer=1, backward=True):
    """ Given a Mesh 'M' and a Pointset 'P', the filter projects each vertex of
        P over M and color M according to the geodesic distance from these
        projected points. Projection and coloring are done on a per vertex
        basis.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        target_layer (int): The mesh layer whose surface is colored. For each
            vertex of this mesh we decide the color according to the following
            arguments.
        source_layer (int): The mesh layer whose vertexes are used as seed
            points for the color computation. These seeds point are projected
            onto the target_layer mesh.
        backward (bool): If True the mesh is colored according to the distance
            from the frontier of the voronoi diagram induced by the
            source_layer seeds.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Voronoi Vertex Coloring">\n',
        '    <Param name="ColoredMesh" ',
        'value="{:d}" '.format(target_layer),
        'description="To be Colored Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="VertexMesh" ',
        'value="{:d}" '.format(source_layer),
        'description="Vertex Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="backward" ',
        'value="{}" '.format(str(backward).lower()),
        'description="BackDistance" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def cyclic_rainbow(script, direction='sphere', start_pt=(0, 0, 0),
                   amplitude=255 / 2, center=255 / 2, freq=0.8,
                   phase=(0, 120, 240, 0), alpha=False):
    """ Color mesh vertices in a repeating sinusiodal rainbow pattern

    Sine wave follows the following equation for each color channel (RGBA):
    channel = sin(freq*increment + phase)*amplitude + center

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        direction (str) = the direction that the sine wave will travel; this
            and the start_pt determine the 'increment' of the sine function.
            Valid values are:
            'sphere' - radiate sine wave outward from start_pt (default)
            'x' - sine wave travels along the X axis
            'y' - sine wave travels along the Y axis
            'z' - sine wave travels along the Z axis
            or define the increment directly using a muparser function, e.g.
                '2x + y'. In this case start_pt will not be used; include it in
                the function directly.
    start_pt (3 coordinate tuple or list): start point of the sine wave. For a
        sphere this is the center of the sphere.
    amplitude (float [0, 255], single value or 4 term tuple or list): amplitude
        of the sine wave, with range between 0-255. If a single value is
        specified it will be used for all channels, otherwise specify each
        channel individually.
    center (float [0, 255], single value or 4 term tuple or list): center
        of the sine wave, with range between 0-255. If a single value is
        specified it will be used for all channels, otherwise specify each
        channel individually.
    freq (float, single value or 4 term tuple or list): frequency of the sine
        wave. If a single value is specified it will be used for all channels,
        otherwise specifiy each channel individually.
    phase (float [0, 360], single value or 4 term tuple or list): phase
        of the sine wave in degrees, with range between 0-360. If a single
        value is specified it will be used for all channels, otherwise specify
        each channel individually.
    alpha (bool): if False the alpha channel will be set to 255 (full opacity).

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    start_pt = util.make_list(start_pt, 3)
    amplitude = util.make_list(amplitude, 4)
    center = util.make_list(center, 4)
    freq = util.make_list(freq, 4)
    phase = util.make_list(phase, 4)

    if direction.lower() == 'sphere':
        increment = 'sqrt((x-{})^2+(y-{})^2+(z-{})^2)'.format(
            start_pt[0], start_pt[1], start_pt[2])
    elif direction.lower() == 'x':
        increment = 'x - {}'.format(start_pt[0])
    elif direction.lower() == 'y':
        increment = 'y - {}'.format(start_pt[1])
    elif direction.lower() == 'z':
        increment = 'z - {}'.format(start_pt[2])
    else:
        increment = direction

    red_func = '{a}*sin({f}*{i} + {p}) + {c}'.format(
        f=freq[0], i=increment, p=math.radians(phase[0]),
        a=amplitude[0], c=center[0])
    green_func = '{a}*sin({f}*{i} + {p}) + {c}'.format(
        f=freq[1], i=increment, p=math.radians(phase[1]),
        a=amplitude[1], c=center[1])
    blue_func = '{a}*sin({f}*{i} + {p}) + {c}'.format(
        f=freq[2], i=increment, p=math.radians(phase[2]),
        a=amplitude[2], c=center[2])
    if alpha:
        alpha_func = '{a}*sin({f}*{i} + {p}) + {c}'.format(
            f=freq[3], i=increment, p=math.radians(phase[3]),
            a=amplitude[3], c=center[3])
    else:
        alpha_func = 255

    function(script, red=red_func, green=green_func, blue=blue_func,
             alpha=alpha_func)
    return None
