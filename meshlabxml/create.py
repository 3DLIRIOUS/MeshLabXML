#! python3
""" MeshLabXML creation functions """

import math

from . import FilterScript
from . import util
from . import transform
from . import vert_color
from . import clean
from . import layers

def cube(script, size=1.0, center=False, color=None):
    """Create a cube primitive

    Note that this is made of 6 quads, not triangles
    """

    """# Convert size to list if it isn't already
    if not isinstance(size, list):
        size = list(size)
    # If a single value was supplied use it for all 3 axes
    if len(size) == 1:
        size = [size[0], size[0], size[0]]"""
    size = util.make_list(size, 3)
    if script.ml_version == '1.3.4BETA':
        filter_name = 'Box'
    else:
        filter_name = 'Box/Cube'
    filter_xml = ''.join([
        '  <filter name="{}">\n'.format(filter_name),
        '    <Param name="size" ',
        'value="1.0" ',
        'description="Scale factor" ',
        'type="RichFloat" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Cube', change_layer=True)
    transform.scale(script, value=size)
    # Box is centered on origin at creation
    if not center:
        transform.translate(script, value=[size[0]/2, size[1]/2, size[2]/2])
    if color is not None:
        vert_color.function(script, color=color)
    return None


# Usage: height=(1) (radius=(1)|(radius1=(1) radius2=(1)))|(diameter=(2)|(diameter1=(2) diameter2=(2))) center=(false)
# Note: need to know m_up in order to orient cylinder correctly!
# OpenSCAD cylinder:
#    height This is the height of the cylinder. Default value is 1.
#    radius The radius of both top and bottom ends of the cylinder. Use this parameter if you want plain cylinder. Default value is 1.
#    radius1 This is the radius of the cone on bottom end. Default value is 1.
#    radius2 This is the radius of the cone on top end. Default value is 1.
#    diameter The diameter of both top and bottom ends of the cylinder. Use this parameter if you want plain cylinder. Default value is 1.
#    diameter1 This is the diameter of the cone on bottom end. Default value is 1.
#    diameter2 This is the diameter of the cone on top end. Default value is 1.
# center If true will center the height of the cone/cylinder around the
# origin. Default is false, placing the base of the cylinder or radius1 radius
# of cone at the origin.
def cylinder(script, up='z', height=1.0, radius=None, radius1=None,
             radius2=None, diameter=None, diameter1=None, diameter2=None,
             center=False, cir_segments=32, color=None):
    """Create a cylinder or cone primitive. Usage is based on OpenSCAD.
    # height = height of the cylinder
    # radius1 = radius of the cone on bottom end
    # radius2 = radius of the cone on top end
    # center = If true will center the height of the cone/cylinder around
    # the origin. Default is false, placing the base of the cylinder or radius1
    # radius of cone at the origin.
    #
    cir_segments Number of sides of the polygonal approximation of the cone

    color = specify a color name to apply vertex colors to the newly
    # created mesh
    """
    if radius is not None and diameter is None:
        if radius1 is None and diameter1 is None:
            radius1 = radius
        if radius2 is None and diameter2 is None:
            radius2 = radius
    if diameter is not None:
        if radius1 is None and diameter1 is None:
            radius1 = diameter / 2
        if radius2 is None and diameter2 is None:
            radius2 = diameter / 2
    if diameter1 is not None:
        radius1 = diameter1 / 2
    if diameter2 is not None:
        radius2 = diameter2 / 2
    if radius1 is None:
        radius1 = 1.0
    if radius2 is None:
        radius2 = radius1

    # Cylinder is created centered with Y up
    filter_xml = ''.join([
        '  <filter name="Cone">\n',
        '    <Param name="h" ',
        'value="%s" ' % height,
        'description="Height" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="r0" ',
        'value="%s" ' % radius1,
        'description="Radius 1" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="r1" ',
        'value="%s" ' % radius2,
        'description="Radius 2" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="subdiv" ',
        'value="%d" ' % cir_segments,
        'description="Side" ',
        'type="RichInt" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Cone', change_layer=True)
    if not center:
        transform.translate(script, [0, height / 2, 0])
    if up.lower() == 'z':
        transform.rotate(script, axis='x', angle=90)  # rotate to Z up
    if color is not None:
        vert_color.function(script, color=color)
    return None


def icosphere(script, radius=1.0, diameter=None, subdivisions=3, color=None):
    """create an icosphere mesh

    radius Radius of the sphere
    # subdivisions = Subdivision level; Number of the recursive subdivision of the
    # surface. Default is 3 (a sphere approximation composed by 1280 faces).
    # Admitted values are in the range 0 (an icosahedron) to 8 (a 1.3 MegaTris
    # approximation of a sphere). Formula for number of faces: F=20*4^subdiv
    # color = specify a color name to apply vertex colors to the newly
    # created mesh"""
    if diameter is not None:
        radius = diameter / 2
    filter_xml = ''.join([
        '  <filter name="Sphere">\n',
        '    <Param name="radius" ',
        'value="%s" ' % radius,
        'description="Radius" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="subdiv" ',
        'value="%d" ' % subdivisions,
        'description="Subdiv. Level" ',
        'type="RichInt" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Sphere', change_layer=True)
    if color is not None:
        vert_color.function(script, color=color)
    return None


def sphere_cap(script, angle=1.0, subdivisions=3, color=None):
    """# angle = Angle of the cone subtending the cap. It must be <180 less than 180
    # subdivisions = Subdivision level; Number of the recursive subdivision of the
    # surface. Default is 3 (a sphere approximation composed by 1280 faces).
    # Admitted values are in the range 0 (an icosahedron) to 8 (a 1.3 MegaTris
    # approximation of a sphere). Formula for number of faces: F=20*4^subdivisions
    # color = specify a color name to apply vertex colors to the newly
    # created mesh"""
    filter_xml = ''.join([
        '  <filter name="Sphere Cap">\n',
        '    <Param name="angle" ',
        'value="%s" ' % angle,
        'description="Angle" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="subdiv" ',
        'value="%d" ' % subdivisions,
        'description="Subdiv. Level" ',
        'type="RichInt" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Sphere Cap', change_layer=True)
    if color is not None:
        vert_color.function(script, color=color)
    return None


def torus(script, major_radius=3.0, minor_radius=1.0, inner_diameter=None,
          outer_diameter=None, major_segments=48, minor_segments=12,
          color=None):
    """Create a torus mesh

    Args:
        major_radius (float, (optional)): radius from the origin to the
            center of the cross sections
        minor_radius (float, (optional)): radius of the torus cross
            section
        inner_diameter (float, (optional)): inner diameter of torus. If
            both inner_diameter and outer_diameter are provided then
            these will override major_radius and minor_radius.,
        outer_diameter (float, (optional)): outer diameter of torus. If
            both inner_diameter and outer_diameter are provided then
            these will override major_radius and minor_radius.
        major_segments (int (optional)): number of segments for the main
            ring of the torus
        minor_segments (int (optional)): number of segments for the minor
            ring of the torus
        color (str (optional)): color name to apply vertex colors to the
            newly created mesh

    Returns:
        None

    """
    if inner_diameter is not None and outer_diameter is not None:
        major_radius = (inner_diameter + outer_diameter) / 4
        minor_radius = major_radius - inner_diameter / 2
        # Ref: inner_diameter = 2 * (major_radius - minor_radius)
        # Ref: outer_diameter = 2 * (major_radius + minor_radius)
    filter_xml = ''.join([
        '  <filter name="Torus">\n',
        '    <Param name="hRadius" ',
        'value="%s" ' % major_radius,
        'description="Horizontal Radius" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="vRadius" ',
        'value="%s" ' % minor_radius,
        'description="Vertical Radius" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="hSubdiv" ',
        'value="%d" ' % major_segments,
        'description="Horizontal Subdivision" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="vSubdiv" ',
        'value="%d" ' % minor_segments,
        'description="Vertical Subdivision" ',
        'type="RichInt" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Torus', change_layer=True)
    if color is not None:
        vert_color.function(script, color=color)
    return None


def grid(script, size=1.0, x_segments=1, y_segments=1, center=False,
         color=None):
    """2D square/plane/grid created on XY plane

    x_segments # Number of segments in the X direction.
    y_segments # Number of segments in the Y direction.
    center="false" # If true square will be centered on origin;
    otherwise it is place in the positive XY quadrant.


    """
    size = util.make_list(size, 2)
    filter_xml = ''.join([
        '  <filter name="Grid Generator">\n',
        '    <Param name="absScaleX" ',
        'value="{}" '.format(size[0]),
        'description="x scale" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="absScaleY" ',
        'value="{}" '.format(size[1]),
        'description="y scale" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="numVertX" ',
        'value="{:d}" '.format(x_segments + 1),
        'description="num vertices on x" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="numVertY" ',
        'value="{:d}" '.format(y_segments + 1),
        'description="num vertices on y" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="center" ',
        'value="false" ',
        'description="centered on origin" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Grid Generator', change_layer=True)

    """This is to work around a bug in MeshLab whereby the Grid Generator does not
    create zero values for z. Ref bug #458: https://sourceforge.net/p/meshlab/bugs/458/"""
    transform.vert_function(script, z_func='rint(z)')

    """Note that the "center" parameter in the mlx script does not actually
    center the square, not sure what it is doing. Instead this is set to false,
    which places the plane in the -X,+Y quadrant, and it is translated to the
    appropriate position after creation.
    """
    if center:
        transform.translate(script, value=[size[0]/2, -size[1]/2, 0])
    else:
        transform.translate(script, value=[size[0], 0, 0])
    if color is not None:
        vert_color.function(script, color=color)
    return None


def annulus(script, radius=None, radius1=None, radius2=None, diameter=None,
            diameter1=None, diameter2=None, cir_segments=32, color=None):
    """Create a 2D (surface) circle or annulus
    radius1=1 # Outer radius of the circle
    radius2=0 # Inner radius of the circle (if non-zero it creates an annulus)
    color="" # specify a color name to apply vertex colors to the newly created mesh

    OpenSCAD: parameters: diameter overrides radius, radius1 & radius2 override radius
    """
    if radius is not None and diameter is None:
        if radius1 is None and diameter1 is None:
            radius1 = radius
        if radius2 is None and diameter2 is None:
            radius2 = 0
    if diameter is not None:
        if radius1 is None and diameter1 is None:
            radius1 = diameter / 2
        if radius2 is None and diameter2 is None:
            radius2 = 0
    if diameter1 is not None:
        radius1 = diameter1 / 2
    if diameter2 is not None:
        radius2 = diameter2 / 2
    if radius1 is None:
        radius1 = 1
    if radius2 is None:
        radius2 = 0

    # Circle is created centered on the XY plane
    filter_xml = ''.join([
        '  <filter name="Annulus">\n',
        '    <Param name="externalRadius" ',
        'value="%s" ' % radius1,
        'description="External Radius" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="internalRadius" ',
        'value="%s" ' % radius2,
        'description="Internal Radius" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="sides" ',
        'value="%d" ' % cir_segments,
        'description="Sides" ',
        'type="RichInt" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Annulus', change_layer=True)
    if color is not None:
        vert_color.function(script, color=color)
    return None


def cylinder_open_hires(script, height=1.0, radius=1, diameter=None,
                        cir_segments=48, height_segments=1,
                        invert_normals=False, center=False, color=None):
    """ Creates a round open tube, e.g. a cylinder with no top or bottom.

    Useful if you want to wrap it around and join the open ends together, forming a torus.

    invert_normals (bool (optional)): if True normals point outward; in false normals point inward.
    """
    if diameter is not None:
        radius = diameter / 2

    if center:
        z_translate = -height / 2
    else:
        z_translate = 0.0

    grid(script,
         [2 * math.pi * radius, height],
         x_segments=cir_segments,
         y_segments=height_segments)
    transform.rotate(script, 'x', 90)
    transform.translate(script, [math.pi * radius / 2, 0, z_translate])
    if not invert_normals:
        transform.rotate(script, 'z', 180)
    transform.wrap2cylinder(script, radius)
    clean.merge_vert(script, threshold=0.00002)
    if color is not None:
        vert_color.function(script, color=color)
    return None


def cube_open_hires_old(script, size=1.0, x_segments=1, y_segments=1, z_segments=1,
                    center=False, color=None):
    """ Creates a square open tube, e.g. a box with no top or bottom.

    Useful if you want to wrap it around and join the open ends together, forming a torus.
    """
    """# Convert size to list if it isn't already
    if not isinstance(size, list):
        size = list(size)
    # If a single value was supplied use it for all 3 axes
    if len(size) == 1:
        size = [size[0], size[0], size[0]]"""
    size = util.make_list(size, 3)

    # X sides
    grid(script, [size[0], size[2]],
         x_segments=x_segments,
         y_segments=z_segments)
    transform.rotate(script, 'x', 90)
    #transform.translate(script, [0, 0, -size[2]])
    layers.duplicate(script)
    # Rotate to correct normals
    transform.rotate(script, 'z', 180)
    transform.translate(script, [size[0], size[1], 0])

    # Y sides
    grid(script, [size[2], size[1]],
         x_segments=z_segments,
         y_segments=y_segments)
    transform.rotate(script, 'y', -90)
    #transform.rotate(script, 'z', 90)
    #transform.translate(script, [0, 0, -size[2]])
    layers.duplicate(script)
    # Rotate to correct normals
    transform.rotate(script, 'z', 180)
    transform.translate(script, [size[0], size[1], 0])

    layers.join(script)
    clean.merge_vert(script, threshold=0.00002)
    # normals.fix(script)
    if center:
        transform.translate(script, [-size[0] / 2, -size[1] / 2, -size[2] / 2])
    if color is not None:
        vert_color.function(script, color=color)
    return None


def cube_open_hires(script, size=1.0, x_segments=1, y_segments=1, z_segments=1,
                    center=False, color=None):
    """ Creates a square open tube, e.g. a box with no top or bottom.

    Useful if you want to wrap it around and join the open ends together, forming a torus.
    """
    """# Convert size to list if it isn't already
    if not isinstance(size, list):
        size = list(size)
    # If a single value was supplied use it for all 3 axes
    if len(size) == 1:
        size = [size[0], size[0], size[0]]"""
    size = util.make_list(size, 3)

    # Make big grid and bend
    grid(script, [2*(x_segments + y_segments), z_segments],
         x_segments=2*(x_segments + y_segments),
         y_segments=z_segments)
    transform.rotate(script, 'x', 90)
    # Bend 3 times into a rectangular tube
    if script.ml_version == '1.3.4BETA': # muparser version: 1.3.2
        transform.vert_function(script,
            x_func='if(x>{x_size}, {x_size}, x)'.format(x_size=x_segments),
            y_func='if(x>{x_size}, (x-{x_size}), y)'.format(x_size=x_segments),
            z_func='z')
        transform.vert_function(script,
            x_func='if(y>{y_size}, ({y_size}-y+{x_size}), x)'.format(x_size=x_segments, y_size=y_segments),
            y_func='if(y>{y_size}, {y_size}, y)'.format(y_size=y_segments),
            z_func='z')
        transform.vert_function(script,
            x_func='if(x<0, 0, x)',
            y_func='if(x<0, ({y_size}+x), y)'.format(y_size=y_segments),
            z_func='z')
    else: # muparser version: 2.2.5
        transform.vert_function(script,
            x_func='(x>{x_size} ? {x_size} : x)'.format(x_size=x_segments),
            y_func='(x>{x_size} ? (x-{x_size}) : y)'.format(x_size=x_segments),
            z_func='z')
        transform.vert_function(script,
            x_func='(y>{y_size} ? ({y_size}-y+{x_size}) : x)'.format(x_size=x_segments, y_size=y_segments),
            y_func='(y>{y_size} ? {y_size} : y)'.format(y_size=y_segments),
            z_func='z')
        transform.vert_function(script,
            x_func='(x<0 ? 0 : x)',
            y_func='(x<0 ? ({y_size}+x) : y)'.format(y_size=y_segments),
            z_func='z')
    clean.merge_vert(script, threshold=0.00002)
    transform.scale(script, [size[0]/x_segments, size[1]/y_segments, size[2]/z_segments])
    if center:
        transform.translate(script, [-size[0] / 2, -size[1] / 2, -size[2] / 2])
    if color is not None:
        vert_color.function(script, color=color)
    return None


def plane_hires_edges(script, size=1.0, x_segments=1, y_segments=1,
                      center=False, color=None):
    """ Creates a plane with a specified number of vertices
    on it sides, but no vertices on the interior.

    Currently used to create a simpler bottom for cube_hires.

    """
    size = util.make_list(size, 2)

    grid(script, size=[x_segments + y_segments - 1, 1],
         x_segments=(x_segments + y_segments - 1), y_segments=1)
    # Deform left side
    transform.vert_function(
        script,
        x_func='if((y>0) and (x<%s),0,x)' % (y_segments),
        y_func='if((y>0) and (x<%s),(x+1)*%s,y)' % (
            y_segments, size[1] / y_segments))
    # Deform top
    transform.vert_function(
        script,
        x_func='if((y>0) and (x>=%s),(x-%s+1)*%s,x)' % (
            y_segments, y_segments, size[0] / x_segments),
        y_func='if((y>0) and (x>=%s),%s,y)' % (y_segments, size[1]))
    # Deform right side
    transform.vert_function(
        script,
        x_func='if((y<.00001) and (x>%s),%s,x)' % (
            x_segments, size[0]),
        y_func='if((y<.00001) and (x>%s),(x-%s)*%s,y)' % (
            x_segments, x_segments, size[1] / y_segments))
    # Deform bottom
    transform.vert_function(
        script,
        x_func='if((y<.00001) and (x<=%s) and (x>0),(x)*%s,x)' % (
            x_segments, size[0] / x_segments),
        y_func='if((y<.00001) and (x<=%s) and (x>0),0,y)' % (x_segments))
    if center:
        transform.translate(script, [-size[0] / 2, -size[1] / 2])
    if color is not None:
        vert_color.function(script, color=color)
    return None


def half_sphere_hires():
    pass


def cube_hires(script, size=1.0, x_segments=1, y_segments=1, z_segments=1,
               simple_bottom=True, center=False, color=None):
    """Create a box with user defined number of segments in each direction.

    Grid spacing is the same as its dimensions (spacing = 1) and its
    thickness is one. Intended to be used for e.g. deforming using functions
    or a height map (lithopanes) and can be resized after creation.

    Warnings: function uses layers.join

    top_option
        0 open
        1 full
        2 simple
    bottom_option
        0 open
        1 full
        2 simple
    """
    """# Convert size to list if it isn't already
    if not isinstance(size, list):
        size = list(size)
    # If a single value was supplied use it for all 3 axes
    if len(size) == 1:
        size = [size[0], size[0], size[0]]"""
    size = util.make_list(size, 3)

    # Top
    grid(script,
         size,
         x_segments,
         y_segments)
    transform.translate(script, [0, 0, size[2]])

    # Bottom
    if simple_bottom:
        plane_hires_edges(
            script, size, x_segments, y_segments)
    else:
        layers.duplicate(script)
        transform.translate(script, [0, 0, -size[2]])
    # Rotate to correct normals
    transform.rotate(script, 'x', 180)
    transform.translate(script, [0, size[1], 0])

    # Sides
    cube_open_hires(
        script=script, size=size, x_segments=x_segments,
        y_segments=y_segments, z_segments=z_segments)

    # Join everything together
    layers.join(script)
    # Need some tolerance on merge_vert due to rounding errors
    clean.merge_vert(script, threshold=0.00002)
    if center:
        transform.translate(script, [-size[0] / 2, -size[1] / 2, -size[2] / 2])
    if color is not None:
        vert_color.function(script, color=color)
    return None


def annulus_hires(script, radius=None, radius1=None, radius2=None,
                  diameter=None, diameter1=None, diameter2=None,
                  cir_segments=48, rad_segments=1, color=None):
    """Create a cylinder with user defined number of segments

    """
    if radius is not None and diameter is None:
        if radius1 is None and diameter1 is None:
            radius1 = radius
        if radius2 is None and diameter2 is None:
            radius2 = 0
    if diameter is not None:
        if radius1 is None and diameter1 is None:
            radius1 = diameter / 2
        if radius2 is None and diameter2 is None:
            radius2 = 0
    if diameter1 is not None:
        radius1 = diameter1 / 2
    if diameter2 is not None:
        radius2 = diameter2 / 2
    if radius1 is None:
        radius1 = 1
    if radius2 is None:
        radius2 = 0
    ring = (radius1 - radius2) / rad_segments

    for i in range(0, rad_segments):
        annulus(script,
                radius1=radius1 - i * ring,
                radius2=radius1 - (i + 1) * ring,
                cir_segments=cir_segments)
    layers.join(script, merge_vert=True)
    if color is not None:
        vert_color.function(script, color=color)
    return None


def tube_hires(script, height=1.0, radius=None, radius1=None, radius2=None,
               diameter=None, diameter1=None, diameter2=None, cir_segments=32,
               rad_segments=1, height_segments=1, center=False,
               simple_bottom=False, color=None):
    """Create a cylinder with user defined number of segments

    """

    # TODO: add option to round the top of the cylinder, i.e. deform spherically
    # TODO: add warnings if values are ignored, e.g. if you specify both radius
    # and diameter.
    if radius is not None and diameter is None:
        if radius1 is None and diameter1 is None:
            radius1 = radius
        if radius2 is None and diameter2 is None:
            radius2 = 0
    if diameter is not None:
        if radius1 is None and diameter1 is None:
            radius1 = diameter / 2
        if radius2 is None and diameter2 is None:
            radius2 = 0
    if diameter1 is not None:
        radius1 = diameter1 / 2
    if diameter2 is not None:
        radius2 = diameter2 / 2
    if radius1 is None:
        radius1 = 1
    if radius2 is None:
        radius2 = 0

    # Create top
    annulus_hires(script,
                  radius1=radius1,
                  radius2=radius2,
                  cir_segments=cir_segments,
                  rad_segments=rad_segments)
    transform.translate(script, [0, 0, height])

    # Create bottom
    if simple_bottom:
        annulus(script,
                radius1=radius1,
                radius2=radius2,
                cir_segments=cir_segments)
    else:
        layers.duplicate(script)
        transform.translate(script, [0, 0, -height])
    # Rotate to correct normals
    transform.rotate(script, 'x', 180)

    # Create outer tube
    cylinder_open_hires(script, height, radius1,
                        cir_segments=cir_segments,
                        height_segments=height_segments)

    # Create inner tube
    if radius2 != 0:
        cylinder_open_hires(script, height, radius2,
                            cir_segments=cir_segments,
                            height_segments=height_segments,
                            invert_normals=True)

    # Join everything together
    layers.join(script)
    # Need some tolerance on merge_vert due to rounding errors
    clean.merge_vert(script, threshold=0.00002)
    if center:
        transform.translate(script, [0, 0, -height / 2])
    if color is not None:
        vert_color.function(script, color=color)
    return None


def triangle():
    """Create a triangle by specifying 3 points

    Under the hood: create a plane, delete one point, then move other vertices.
    """
    pass


def dna(sequence='GATTACA'):
    """Create  doublehelix function, takes spacing between helixes and
    rungs, rung diameter

    """
    pass
