""" MeshLabXML transformation and deformation functions """

import sys
import math
import re

from . import util
from . import mp_atan2


def translate2(script='TEMP3D_default.mlx', value=(0.0, 0.0, 0.0),
               center=False, freeze=True, all_layers=False,
               current_layer=None, last_layer=None):
    # Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transform: Move, Translate, Center">\n' +

                      '    <Param name="axisX" ' +
                      'value="%s" ' % value[0] +
                      'description="X Axis" ' +
                      'min="-500" ' +
                      'max="500" ' +
                      'type="RichDynamicFloat" ' +
                      'tooltip="Absolute translation value along the X axis."/>\n' +

                      '    <Param name="axisY" ' +
                      'value="%s" ' % value[1] +
                      'description="Y Axis" ' +
                      'min="-500" ' +
                      'max="500" ' +
                      'type="RichDynamicFloat" ' +
                      'tooltip="Absolute translation value along the Y axis."/>\n' +

                      '    <Param name="axisZ" ' +
                      'value="%s" ' % value[2] +
                      'description="Z Axis" ' +
                      'min="-500" ' +
                      'max="500" ' +
                      'type="RichDynamicFloat" ' +
                      'tooltip="Absolute translation value along the Z axis."/>\n' +

                      '    <Param name="centerFlag" ' +
                      'value="%s" ' % str(center).lower() +
                      'description="Translate center of bbox to the origin." ' +
                      'type="RichBool" ' +
                      'tooltip="Translate center of bbox to the origin."/>\n' +

                      '    <Param name="Freeze" ' +
                      'value="%s" ' % str(freeze).lower() +
                      'description="Freeze Matrix." ' +
                      'type="RichBool" ' +
                      'tooltip="The transformation is explicitly applied and the' +
                      ' vertex coords are actually changed."/>\n' +

                      '    <Param name="ToAll" ' +
                      'value="%s" ' % str(all_layers).lower() +
                      'description="Apply to all layers." ' +
                      'type="RichBool" ' +
                      'tooltip="The transformation is explicitly applied to all the' +
                      ' mesh and raster layers in the project."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def translate(script='TEMP3D_default.mlx', value=(0.0, 0.0, 0.0),
              current_layer=None, last_layer=None):
    """An alternative translate implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    # Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    function(script,
             x_func='x+%s' % value[0],
             y_func='y+%s' % value[1],
             z_func='z+%s' % value[2])
    return current_layer, last_layer


def rotate2(script='TEMP3D_default.mlx', axis='z', angle=0.0,
            custom_axis=None, center_pt='origin',
            custom_center_pt=None, freeze=True, all_layers=False,
            current_layer=None, last_layer=None):
    # Convert axis name into number
    if axis.lower() == 'x':
        axis_num = 0
    elif axis.lower() == 'y':
        axis_num = 1
    elif axis.lower() == 'z':
        axis_num = 2
    else:  # custom axis
        axis_num = 3
        if custom_axis is None:
            print('WARNING: a custom axis was selected, however',
                  '"custom_axis" was not provided. Using default (Z).')
            custom_axis = [0.0, 0.0, 1.0]
    # Convert center point name into number
    if center_pt.lower() == 'origin':
        center_pt_num = 0
    elif center_pt.lower() == 'barycenter':
        center_pt_num = 1
    else:  # custom cente point
        center_pt_num = 2
        if custom_center_pt is None:
            print('WARNING: a custom center point was selected, however',
                  '"custom_center_pt" was not provided. Using default',
                  '(origin).')
            custom_center_pt = [0.0, 0.0, 0.0]
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transform: Rotate">\n' +

                      '    <Param name="rotAxis" ' +
                      'value="%d" ' % axis_num +
                      'description="Rotation on:" ' +
                      'enum_val0="X axis" ' +
                      'enum_val1="Y axis" ' +
                      'enum_val2="Z axis" ' +
                      'enum_val3="custom axis" ' +
                      'enum_cardinality="4" ' +
                      'type="RichEnum" ' +
                      'tooltip="Choose a method."/>\n' +

                      '    <Param name="rotCenter" ' +
                      'value="%d" ' % center_pt_num +
                      'description="Center of rotation:" ' +
                      'enum_val0="origin" ' +
                      'enum_val1="barycenter" ' +
                      'enum_val2="custom point" ' +
                      'enum_cardinality="3" ' +
                      'type="RichEnum" ' +
                      'tooltip="Choose a method."/>\n' +

                      '    <Param name="angle" ' +
                      'value="%s" ' % angle +
                      'description="Rotation Angle" ' +
                      'min="-360" ' +
                      'max="360" ' +
                      'type="RichDynamicFloat" ' +
                      'tooltip="Angle of rotation (in degrees). If snapping is' +
                      ' enabled this value is rounded according to the snap' +
                      ' value."/>\n' +

                      '    <Param name="snapFlag" ' +
                      'value="false" ' +
                      'description="Snap angle" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected, before starting the filter will remove' +
                      ' any unreferenced vertex (for which curvature values are not' +
                      ' defined)."/>\n' +

                      '    <Param name="customAxis" ' +
                      'x="%s" ' % custom_axis[0] +
                      'y="%s" ' % custom_axis[1] +
                      'z="%s" ' % custom_axis[2] +
                      'description="Custom axis" ' +
                      'type="RichPoint3f" ' +
                      'tooltip="This rotation axis is used only if the' +
                      ' _custom axis_ option is chosen."/>\n' +

                      '    <Param name="customCenter" ' +
                      'x="%s" ' % custom_center_pt[0] +
                      'y="%s" ' % custom_center_pt[1] +
                      'z="%s" ' % custom_center_pt[2] +
                      'description="Custom center" ' +
                      'type="RichPoint3f" ' +
                      'tooltip="This rotation center is used only if the' +
                      ' _custom point_ option is chosen."/>\n' +

                      '    <Param name="snapAngle" ' +
                      'value="30" ' +
                      'description="Snapping Value" ' +
                      'type="RichFloat" ' +
                      'tooltip="This value is used to snap the rotation angle."/>\n' +

                      '    <Param name="Freeze" ' +
                      'value="%s" ' % str(freeze).lower() +
                      'description="Freeze Matrix." ' +
                      'type="RichBool" ' +
                      'tooltip="The transformation is explicitly applied and the' +
                      ' vertex coords are actually changed."/>\n' +

                      '    <Param name="ToAll" ' +
                      'value="%s" ' % str(all_layers).lower() +
                      'description="Apply to all layers." ' +
                      'type="RichBool" ' +
                      'tooltip="The transformation is explicitly applied to all the' +
                      ' mesh and raster layers in the project."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def rotate(script='TEMP3D_default.mlx', axis='z', angle=0.0,
           current_layer=None, last_layer=None):
    """An alternative rotate implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    angle = math.radians(angle)
    if axis.lower() == 'x':
        function(script,
                 x_func='x',
                 y_func='y*cos(%s)-z*sin(%s)' % (angle, angle),
                 z_func='y*sin(%s)+z*cos(%s)' % (angle, angle))
    elif axis.lower() == 'y':
        function(script,
                 x_func='z*sin(%s)+x*cos(%s)' % (angle, angle),
                 y_func='y',
                 z_func='z*cos(%s)-x*sin(%s)' % (angle, angle))
    elif axis.lower() == 'z':
        function(script,
                 x_func='x*cos(%s)-y*sin(%s)' % (angle, angle),
                 y_func='x*sin(%s)+y*cos(%s)' % (angle, angle),
                 z_func='z')
    else:
        print('Axis name is not valid; exiting ...')
        sys.exit(1)
    return current_layer, last_layer


def scale2(script='TEMP3D_default.mlx', value=1.0,
           uniform=True, center_pt='origin',
           custom_center_pt=None, unit=False, freeze=True,
           all_layers=False, current_layer=None, last_layer=None):
    """# Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    # If a single value was supplied use it for all 3 axes
    if len(value) == 1:
        value = [value[0], value[0], value[0]]"""
    value = util.make_list(value, 3)
    # Convert center point name into number
    if center_pt.lower() == 'origin':
        center_pt_num = 0
    elif center_pt.lower() == 'barycenter':
        center_pt_num = 1
    else:  # custom axis
        center_pt_num = 2
        if custom_center_pt is None:
            print('WARNING: a custom center point was selected, however',
                  '"custom_center_pt" was not provided. Using default',
                  '(origin).')
            custom_center_pt = [0.0, 0.0, 0.0]
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transform: Scale">\n' +

                      '    <Param name="axisX" ' +
                      'value="%s" ' % value[0] +
                      'description="X Axis" ' +
                      'type="RichFloat" ' +
                      'tooltip="Scaling along the X axis."/>\n' +

                      '    <Param name="axisY" ' +
                      'value="%s" ' % value[1] +
                      'description="Y Axis" ' +
                      'type="RichFloat" ' +
                      'tooltip="Scaling along the Y axis."/>\n' +

                      '    <Param name="axisZ" ' +
                      'value="%s" ' % value[2] +
                      'description="Z Axis" ' +
                      'type="RichFloat" ' +
                      'tooltip="Scaling along the Z axis."/>\n' +

                      '    <Param name="uniformFlag" ' +
                      'value="%s" ' % str(uniform).lower() +
                      'description="Uniform Scaling" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected an uniform scaling (the same for all the' +
                      ' three axis) is applied (the X axis value is used)."/>\n' +

                      '    <Param name="scaleCenter" ' +
                      'value="%d" ' % center_pt_num +
                      'description="Center of scaling:" ' +
                      'enum_val0="origin" ' +
                      'enum_val1="barycenter" ' +
                      'enum_val2="custom point" ' +
                      'enum_cardinality="3" ' +
                      'type="RichEnum" ' +
                      'tooltip="Choose a method."/>\n' +

                      '    <Param name="customCenter" ' +
                      'x="%s" ' % custom_center_pt[0] +
                      'y="%s" ' % custom_center_pt[1] +
                      'z="%s" ' % custom_center_pt[2] +
                      'description="Custom center" ' +
                      'type="RichPoint3f" ' +
                      'tooltip="This scaling center is used only if the' +
                      ' _custom point_ option is chosen."/>\n' +

                      '    <Param name="unitFlag" ' +
                      'value="%s" ' % str(unit).lower() +
                      'description="Scale to Unit bbox" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected, the object is scaled to a box whose' +
                      ' sides are at most 1 unit length."/>\n' +

                      '    <Param name="Freeze" ' +
                      'value="%s" ' % str(freeze).lower() +
                      'description="Freeze Matrix." ' +
                      'type="RichBool" ' +
                      'tooltip="The transformation is explicitly applied and the' +
                      ' vertex coords are actually changed."/>\n' +

                      '    <Param name="ToAll" ' +
                      'value="%s" ' % str(all_layers).lower() +
                      'description="Apply to all layers." ' +
                      'type="RichBool" ' +
                      'tooltip="The transformation is explicitly applied to all the' +
                      ' mesh and raster layers in the project."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def scale(script='TEMP3D_default.mlx', value=1.0,
          current_layer=None, last_layer=None):
    """An alternative scale implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    """# Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    # If a single value was supplied use it for all 3 axes
    if len(value) == 1:
        value = [value[0], value[0], value[0]]"""
    value = util.make_list(value, 3)
    function(script,
             x_func='x*%s' % value[0],
             y_func='y*%s' % value[1],
             z_func='z*%s' % value[2])
    return current_layer, last_layer


def freeze_matrix(script='TEMP3D_default.mlx', all_layers=False,
                  current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Freeze Current Matrix">\n' +

                      '    <Param name="allLayers" ' +
                      'value="%s" ' % str(all_layers).lower() +
                      'description="Apply to all visible Layers" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected the filter will be applied to all' +
                      ' visible layers."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def function(script='TEMP3D_default.mlx', x_func='x', y_func='y', z_func='z',
             current_layer=None, last_layer=None):
    """Geometric function using muparser lib to generate new Coordinates

    See help(mlx.muparser_ref) for muparser reference documentation.

    You can change x, y, z for every vertex according to the function specified.
    It's possible to use the following per-vertex variables in the expression:

    Variables (per vertex):
        x, y, z (coordinates)
        nx, ny, nz (normal)
        r, g, b, a (color)
        q (quality)
        rad
        vi (vertex index)
        vtu, vtv (texture coordinates)
        ti (texture index)
        vsel (is the vertex selected? 1 yes, 0 no)
        and all custom vertex attributes already defined by user.

    Args:
        x_func (str): function to generate new coordinates for x
        y_func (str): function to generate new coordinates for y
        z_func (str): function to generate new coordinates for z

    Returns:
        current_layer, last_layer

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Geometric Function">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="x"',
        'value="%s"' % str(x_func).replace('<', '&lt;'),
        'description="func x = "',
        'type="RichString"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="y"',
        'value="%s"' % str(y_func).replace('<', '&lt;'),
        'description="func y = "',
        'type="RichString"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="z"',
        'value="%s"' % str(z_func).replace('<', '&lt;'),
        'description="func z = "',
        'type="RichString"',
        '/>\n']))
    script_file.write('  </filter>\n')
    """script_file.write('  <filter name="Geometric Function">\n' +

                      '    <Param name="x" ' +
                      'value="%s" ' % x_func.replace('<', '&lt;') +
                      'description="func x = " ' +
                      'type="RichString" ' +
                      'tooltip="insert function to generate new coord for x"/>\n' +

                      '    <Param name="y" ' +
                      'value="%s" ' % y_func.replace('<', '&lt;') +
                      'description="func y = " ' +
                      'type="RichString" ' +
                      'tooltip="insert function to generate new coord for y"/>\n' +

                      '    <Param name="z" ' +
                      'value="%s" ' % z_func.replace('<', '&lt;') +
                      'description="func z = " ' +
                      'type="RichString" ' +
                      'tooltip="insert function to generate new coord for z"/>\n' +

                      '  </filter>\n')
    script_file.close()"""
    return current_layer, last_layer


def function_cyl_co(script='TEMP3D_default.mlx', r_func='r', theta_func='theta', z_func='z',
                    current_layer=None, last_layer=None):
    """Geometric function using cylindrical coordinates.

    See "function" documentation for usage.

    """
    # atan2(y,x)
    # TODO: replace with built-in muparser function when MeshLab is updated
    #atan2 = 'if(x>0, atan(y/x), if((x<0) and (y>=0), atan(y/x)+%s, if((x<0) and (y<0), atan(y/x)-%s, if((x==0) and (y>0), %s/2, if((x==0) and (y<0), -%s/2, 0)))))' % (math.pi, math.pi, math.pi, math.pi)

    r = 'sqrt(x^2+y^2)'
    theta = mp_atan2('y', 'x')

    # Use re matching to match whole word; this prevents matching
    # 'sqrt' and 'rint' when replacing 'r'
    r_func = re.sub(r"\br\b", r, r_func).replace('theta', theta)
    theta_func = re.sub(r"\br\b", r, theta_func).replace('theta', theta)

    x_func = '(r)*cos(theta)'.replace('r', r_func).replace('theta', theta_func)
    y_func = '(r)*sin(theta)'.replace('r', r_func).replace('theta', theta_func)

    function(script, x_func, y_func, z_func)
    return current_layer, last_layer


def radial_flare(script='TEMP3D_default.mlx', radius=10,
                 current_layer=None, last_layer=None):
    r_func = 'if(z>0, r + radius - radius*sqrt(1-z^2/radius^2), r)'.replace('radius', str(radius))
    function_cyl_co(script, r_func)
    return current_layer, last_layer


def wrap2cylinder(script='TEMP3D_default.mlx', radius=1,
                  pitch=0, current_layer=None, last_layer=None):
    """Deform mesh around cylinder of radius and axis z

    y = 0 will be on the surface of radius "radius"
    pitch != 0 will create a helix, with distance "pitch" traveled in z for each rotation

    """
    """function(s=s, x='(%s+y)*sin(x/(%s+y))' % (radius, radius),
                     y='(%s+y)*cos(x/(%s+y))' % (radius, radius),
                     z='z-%s*x/(2*%s*(%s+y))' % (pitch, pi, radius))"""
    function(script,
             x_func='(%s+y)*sin(x/%s)' % (radius, radius),
             y_func='(%s+y)*cos(x/%s)' % (radius, radius),
             z_func='z-%s*x/(2*%s*%s)' % (pitch, math.pi, radius))
    return current_layer, last_layer


def bend(script='TEMP3D_default.mlx', radius=1, pitch=0, angle=0,
         straight_ends=False, current_layer=None, last_layer=None):
    """Bends mesh around cylinder of radius radius and axis z to a certain angle

    straight_ends: Only apply twist (pitch) over the area that is bent
    """
    angle = math.radians(angle / 2)
    segment = radius * angle
    """function(s=s, x='if(x<%s and x>-%s, (%s+y)*sin(x/%s), (%s+y)*sin(%s/%s)+(x-%s)*cos(%s/%s))'
                        % (segment, segment,  radius, radius,  radius, segment, radius, segment, segment, radius),
                     y='if(x<%s*%s/2 and x>-%s*%s/2, (%s+y)*cos(x/%s), (%s+y)*cos(%s)-(x-%s*%s)*sin(%s))'
                        % (radius, angle, radius, angle, radius, radius, radius, angle/2, radius, angle/2, angle/2),"""
    x_func = 'if(x<%s, if(x>-%s, (%s+y)*sin(x/%s), (%s+y)*sin(-%s)+(x+%s)*cos(-%s)), (%s+y)*sin(%s)+(x-%s)*cos(%s))' % (
        segment, segment, radius, radius, radius, angle, segment, angle, radius, angle, segment, angle)
    y_func = 'if(x<%s, if(x>-%s, (%s+y)*cos(x/%s), (%s+y)*cos(-%s)-(x+%s)*sin(-%s)), (%s+y)*cos(%s)-(x-%s)*sin(%s))' % (
        segment, segment, radius, radius, radius, angle, segment, angle, radius, angle, segment, angle)
    if straight_ends:
        z_func = 'if(x<%s, if(x>-%s, z-%s*x/(2*%s*%s), z+%s*%s/(2*%s)), z-%s*%s/(2*%s))' % (
            segment, segment, pitch, math.pi, radius, pitch, angle, math.pi, pitch, angle, math.pi)
    else:
        z_func = 'z-%s*x/(2*%s*%s)' % (pitch, math.pi, radius)
    function(script, x_func=x_func, y_func=y_func, z_func=z_func)
    return current_layer, last_layer

# TODO: add function to round mesh to desired tolerance
# use muparser rint (round to nearest integer)
