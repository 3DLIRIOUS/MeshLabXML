""" MeshLabXML transformation and deformation functions """

import sys
import math
import re

from . import FilterScript
from . import util
from . import mp_func

def translate2(script, value=(0.0, 0.0, 0.0), center=False, freeze=True,
               all_layers=False):
    """


    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        value (vector, tuple or list): Absolute translation value along the X axis,
        center Translate center of bbox to the origin.
        freeze (bool): The transformation is explicitly applied and the  vertex coords are actually changed.
        all_layers (bool): The transformation is explicitly applied to all the mesh and raster layers in the project.


    """
    # Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    filter_xml = ''.join([
        '  <filter name="Transform: Move, Translate, Center">\n',
        '    <Param name="axisX" ',
        'value="%s" ' % value[0],
        'description="X Axis" ',
        'min="-500" ',
        'max="500" ',
        'type="RichDynamicFloat" ',
        '/>\n',
        '    <Param name="axisY" ',
        'value="%s" ' % value[1],
        'description="Y Axis" ',
        'min="-500" ',
        'max="500" ',
        'type="RichDynamicFloat" ',
        '/>\n',
        '    <Param name="axisZ" ',
        'value="%s" ' % value[2],
        'description="Z Axis" ',
        'min="-500" ',
        'max="500" ',
        'type="RichDynamicFloat" ',
        '/>\n',
        '    <Param name="centerFlag" ',
        'value="%s" ' % str(center).lower(),
        'description="Translate center of bbox to the origin." ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="Freeze" ',
        'value="%s" ' % str(freeze).lower(),
        'description="Freeze Matrix." ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="ToAll" ',
        'value="%s" ' % str(all_layers).lower(),
        'description="Apply to all layers." ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def translate(script, value=(0.0, 0.0, 0.0)):
    """An alternative translate implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    # Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    vert_function(script,
             x_func='x+(%s)' % value[0],
             y_func='y+(%s)' % value[1],
             z_func='z+(%s)' % value[2])
    return None


def rotate2(script, axis='z', angle=0.0, custom_axis=None, center_pt='origin',
            custom_center_pt=None, freeze=True, all_layers=False):
    """

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        axis (str): Choose a method.
        angle (float): "Angle of rotation (in degrees). If snapping is',
        ' enabled this value is rounded according to the snap',
        ' value.
        custom_axis (vector): This rotation axis is used only if the',
        ' _custom axis_ option is chosen.
        center_pt (str): Choose a method.
        custom_center_pt (bool): This rotation center is used only if the',
        ' _custom point_ option is chosen.
        freeze (bool): The transformation is explicitly applied and the',
        ' vertex coords are actually changed.
        all_layers (bool): The transformation is explicitly applied to all the',
        ' mesh and raster layers in the project.
    """
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
    filter_xml = ''.join([
        '  <filter name="Transform: Rotate">\n',
        '    <Param name="rotAxis" ',
        'value="%d" ' % axis_num,
        'description="Rotation on:" ',
        'enum_val0="X axis" ',
        'enum_val1="Y axis" ',
        'enum_val2="Z axis" ',
        'enum_val3="custom axis" ',
        'enum_cardinality="4" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="rotCenter" ',
        'value="%d" ' % center_pt_num,
        'description="Center of rotation:" ',
        'enum_val0="origin" ',
        'enum_val1="barycenter" ',
        'enum_val2="custom point" ',
        'enum_cardinality="3" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="angle" ',
        'value="%s" ' % angle,
        'description="Rotation Angle" ',
        'min="-360" ',
        'max="360" ',
        'type="RichDynamicFloat" ',
        '/>\n',
        '    <Param name="snapFlag" ',
        'value="false" ',
        'description="Snap angle" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="customAxis" ',
        'x="%s" ' % custom_axis[0],
        'y="%s" ' % custom_axis[1],
        'z="%s" ' % custom_axis[2],
        'description="Custom axis" ',
        'type="RichPoint3f" ',
        '/>\n',
        '    <Param name="customCenter" ',
        'x="%s" ' % custom_center_pt[0],
        'y="%s" ' % custom_center_pt[1],
        'z="%s" ' % custom_center_pt[2],
        'description="Custom center" ',
        'type="RichPoint3f" ',
        '/>\n',
        '    <Param name="snapAngle" ',
        'value="30" ',
        'description="Snapping Value" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="Freeze" ',
        'value="%s" ' % str(freeze).lower(),
        'description="Freeze Matrix." ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="ToAll" ',
        'value="%s" ' % str(all_layers).lower(),
        'description="Apply to all layers." ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def rotate(script, axis='z', angle=0.0):
    """An alternative rotate implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    angle = math.radians(angle)
    if axis.lower() == 'x':
        vert_function(script,
                 x_func='x',
                 y_func='y*cos({angle})-z*sin({angle})'.format(angle=angle),
                 z_func='y*sin({angle})+z*cos({angle})'.format(angle=angle))
    elif axis.lower() == 'y':
        vert_function(script,
                 x_func='z*sin({angle})+x*cos({angle})'.format(angle=angle),
                 y_func='y',
                 z_func='z*cos({angle})-x*sin({angle})'.format(angle=angle))
    elif axis.lower() == 'z':
        vert_function(script,
                 x_func='x*cos({angle})-y*sin({angle})'.format(angle=angle),
                 y_func='x*sin({angle})+y*cos({angle})'.format(angle=angle),
                 z_func='z')
    else:
        print('Axis name is not valid; exiting ...')
        sys.exit(1)
    return None


def scale2(script, value=1.0, uniform=True, center_pt='origin',
           custom_center_pt=None, unit=False, freeze=True, all_layers=False):
    """

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        value (float): Scaling along the X axis.
        uniform (bool): If selected an uniform scaling (the same for all the',
        ' three axis) is applied (the X axis value is used).
        center_pt (str): Choose a method.
        custom_center_pt (point): This scaling center is used only if the',
        ' _custom point_ option is chosen.
        unit (bool): If selected, the object is scaled to a box whose',
        ' sides are at most 1 unit length.
        freeze (bool): The transformation is explicitly applied and the',
        ' vertex coords are actually changed.
        all_layers (bool): The transformation is explicitly applied to all the',
        ' mesh and raster layers in the project.
    """
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
    filter_xml = ''.join([
        '  <filter name="Transform: Scale">\n',
        '    <Param name="axisX" ',
        'value="%s" ' % value[0],
        'description="X Axis" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="axisY" ',
        'value="%s" ' % value[1],
        'description="Y Axis" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="axisZ" ',
        'value="%s" ' % value[2],
        'description="Z Axis" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="uniformFlag" ',
        'value="%s" ' % str(uniform).lower(),
        'description="Uniform Scaling" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="scaleCenter" ',
        'value="%d" ' % center_pt_num,
        'description="Center of scaling:" ',
        'enum_val0="origin" ',
        'enum_val1="barycenter" ',
        'enum_val2="custom point" ',
        'enum_cardinality="3" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="customCenter" ',
        'x="%s" ' % custom_center_pt[0],
        'y="%s" ' % custom_center_pt[1],
        'z="%s" ' % custom_center_pt[2],
        'description="Custom center" ',
        'type="RichPoint3f" ',
        '/>\n',
        '    <Param name="unitFlag" ',
        'value="%s" ' % str(unit).lower(),
        'description="Scale to Unit bbox" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="Freeze" ',
        'value="%s" ' % str(freeze).lower(),
        'description="Freeze Matrix." ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="ToAll" ',
        'value="%s" ' % str(all_layers).lower(),
        'description="Apply to all layers." ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def scale(script, value=1.0):
    """An alternative scale implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    """# Convert value to list if it isn't already
    if not isinstance(value, list):
        value = list(value)
    # If a single value was supplied use it for all 3 axes
    if len(value) == 1:
        value = [value[0], value[0], value[0]]"""
    value = util.make_list(value, 3)
    vert_function(script,
             x_func='x*(%s)' % value[0],
             y_func='y*(%s)' % value[1],
             z_func='z*(%s)' % value[2])
    return None


def freeze_matrix(script, all_layers=False):
    """ Freeze the current transformation matrix into the coordinates of the
        vertices of the mesh (and set this matrix to the identity).

    In other words it applies in a definitive way the current matrix to the
    vertex coordinates.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        all_layers (bool): If selected the filter will be applied to all
            visible mesh layers.

    """
    filter_xml = ''.join([
        '  <filter name="Freeze Current Matrix">\n',
        '    <Param name="allLayers" ',
        'value="%s" ' % str(all_layers).lower(),
        'description="Apply to all visible Layers" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def function(script, x_func='x', y_func='y', z_func='z'):
    """Geometric function using muparser lib to generate new Coordinates

    You can change x, y, z for every vertex according to the function specified.

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
        x_func (str): function to generate new coordinates for x
        y_func (str): function to generate new coordinates for y
        z_func (str): function to generate new coordinates for z

    Layer stack:
        No impacts

    MeshLab versions:
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Geometric Function">\n',
        '    <Param name="x" ',
        'value="{}" '.format(str(x_func).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func x = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="y" ',
        'value="{}" '.format(str(y_func).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func y = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="z" ',
        'value="{}" '.format(str(z_func).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func z = " ',
        'type="RichString" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def vert_function(script, x_func='x', y_func='y', z_func='z', selected=False):
    """Geometric function using muparser lib to generate new Coordinates

    You can change x, y, z for every vertex according to the function specified.

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
        x_func (str): function to generate new coordinates for x
        y_func (str): function to generate new coordinates for y
        z_func (str): function to generate new coordinates for z
        selected (bool): if True, only affects selected vertices (ML ver 2016.12 & up)

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    if script.ml_version == '1.3.4BETA':
        filter_xml = ''.join([
            '  <filter name="Geometric Function">\n',
            '    <Param name="x" ',
            'value="{}" '.format(str(x_func).replace('&', '&amp;').replace('<', '&lt;')),
            'description="func x = " ',
            'type="RichString" ',
            '/>\n',
            '    <Param name="y" ',
            'value="{}" '.format(str(y_func).replace('&', '&amp;').replace('<', '&lt;')),
            'description="func y = " ',
            'type="RichString" ',
            '/>\n',
            '    <Param name="z" ',
            'value="{}" '.format(str(z_func).replace('&', '&amp;').replace('<', '&lt;')),
            'description="func z = " ',
            'type="RichString" ',
            '/>\n',
            '  </filter>\n'])
    else:
        filter_xml = ''.join([
            '  <filter name="Per Vertex Geometric Function">\n',
            '    <Param name="x" ',
            'value="{}" '.format(str(x_func).replace('&', '&amp;').replace('<', '&lt;')),
            'description="func x = " ',
            'type="RichString" ',
            '/>\n',
            '    <Param name="y" ',
            'value="{}" '.format(str(y_func).replace('&', '&amp;').replace('<', '&lt;')),
            'description="func y = " ',
            'type="RichString" ',
            '/>\n',
            '    <Param name="z" ',
            'value="{}" '.format(str(z_func).replace('&', '&amp;').replace('<', '&lt;')),
            'description="func z = " ',
            'type="RichString" ',
            '/>\n',
            '    <Param name="onselected" ',
            'value="%s" ' % str(selected).lower(),
            'description="only on selection" ',
            'type="RichBool" ',
            '/>\n',
            '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def function_cyl_co(script, r_func='r', theta_func='theta', z_func='z'):
    """Geometric function using cylindrical coordinates.

    Define functions in Z up cylindrical coordinates, with radius 'r',
    angle 'theta', and height 'z'

    See "function" docs for additional usage info and accepted parameters.

    Args:
        r_func (str): function to generate new coordinates for radius
        theta_func (str): function to generate new coordinates for angle.
            0 degrees is on the +X axis.
        z_func (str): function to generate new coordinates for height

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """

    r = 'sqrt(x^2+y^2)'
    # In newer MeshLab atan2 is builtin to muparser
    if isinstance(script, FilterScript) and script.ml_version >= '2016.12':
        theta = 'atan2(y, x)'
    else:
        theta = mp_func.mp_atan2('y', 'x')

    # Use re matching to match whole word; this prevents matching
    # 'sqrt' and 'rint' when replacing 'r'
    r_func = re.sub(r"\br\b", r, r_func).replace('theta', theta)
    theta_func = re.sub(r"\br\b", r, theta_func).replace('theta', theta)
    z_func = re.sub(r"\br\b", r, z_func).replace('theta', theta)

    x_func = '(r)*cos(theta)'.replace('r', r_func).replace('theta', theta_func)
    y_func = '(r)*sin(theta)'.replace('r', r_func).replace('theta', theta_func)

    vert_function(script, x_func, y_func, z_func)
    return None


def radial_flare2(script, flare_radius=None, start_radius=None, end_radius=None,
                  end_height=None):
    """
    flare_radius must be >= end_height (height)
    end_radius max = flare_radius + r
    
    end_radius (num): radius of mesh at end of flare
    
    +15 r= 8.8205
    -15 r= 1.1795
    
    z=10, 5 +/-15 - +/-15*0.74535599249992989880305788957709
    """
    # TODO: set radius limit, make it so flare continues to expand linearly after radius limit
    # if(r<=radius_limit, flare, factor*z+constant
    # TODO: add option to specify radius at height instead of radius
    if (end_radius is not None) and (end_height is not None):
        # this is only correct if r is constant
        # start_radius here is really r at end_height
        #flare_radius = '-((start_radius-end_radius)^2 + end_height^2)/(2*(start_radius-end_radius))'
        if (end_radius - start_radius) < end_height:
            flare_radius = -((start_radius-end_radius)**2 + end_height**2)/(2*(start_radius-end_radius))
            #print('flare_radius = %s' % flare_radius)
        else:
            print('Error, end_radius is too large for end_height; angle is > 90d')

    r_func = 'if(z>0, (r) + (flare_radius) - (flare_radius)*sqrt(1-z^2/(flare_radius)^2), (r))'.replace('flare_radius', str(flare_radius))
    #r_func = 'if(z>0, (r) + (flare_radius) - (flare_radius)*sqrt(1-z^2/(flare_radius)^2), (r))'.replace('flare_radius', str(flare_radius)).replace('start_radius', str(start_radius)).replace('end_radius', str(end_radius)).replace('end_height', str(end_height))
    function_cyl_co(script, r_func)
    return None

def radial_flare(script, flare_radius=None, start_radius=None, end_radius=None,
                 end_height=None):
    """
    flare_radius must be >= z2 (height)
    r2 max = flare_radius + r
    
    r2 (num): radius of mesh at end of flare
    
    +15 r= 8.8205
    -15 r= 1.1795
    
    z=10, 5 +/-15 - +/-15*0.74535599249992989880305788957709
    """
    # TODO: set radius limit, make it so flare continues to expand linearly after radius limit
    # if(r<=radius_limit, flare, factor*z+constant
    # TODO: add option to specify radius at height instead of radius
    effective_radius = '(flare_radius) + (start_radius) - (r)'
    
    r_func = 'if(z>0, (flare_radius) + (start_radius) - (effective_radius)*cos(z/(flare_radius)), (r))'
    z_func = 'if(z>0, (effective_radius)*sin(z/(flare_radius)), z)'
    
    r_func = r_func.replace('effective_radius', str(effective_radius)).replace('start_radius', str(start_radius)).replace('flare_radius', str(flare_radius))
    z_func = z_func.replace('effective_radius', str(effective_radius)).replace('start_radius', str(start_radius)).replace('flare_radius', str(flare_radius))
    
    function_cyl_co(script=script, r_func=r_func, z_func=z_func)
    return None

def curl_rim(script, curl_radius=None, start_radius=None, end_radius=None,
             end_height=None):
    """
    flare_radius must be >= z2 (height)
    r2 max = flare_radius + r
    
    r2 (num): radius of mesh at end of flare
    
    +15 r= 8.8205
    -15 r= 1.1795
    
    z=10, 5 +/-15 - +/-15*0.74535599249992989880305788957709
    """
    # TODO: set radius limit, make it so flare continues to expand linearly after radius limit
    # if(r<=radius_limit, flare, factor*z+constant
    # TODO: add option to specify radius at height instead of radius
    effective_radius = '(curl_radius) - z'
    
    r_func = 'if((r)>(start_radius), (start_radius) + (effective_radius)*sin(((r)-(start_radius))/(curl_radius)), (r))'
    z_func = 'if((r)>(start_radius), (curl_radius) - (effective_radius)*cos(((r)-(start_radius))/(curl_radius)), z)'
    
    r_func = r_func.replace('effective_radius', str(effective_radius)).replace('start_radius', str(start_radius)).replace('curl_radius', str(curl_radius))
    z_func = z_func.replace('effective_radius', str(effective_radius)).replace('start_radius', str(start_radius)).replace('curl_radius', str(curl_radius))
    
    function_cyl_co(script=script, r_func=r_func, z_func=z_func)
    return None

def wrap2cylinder(script, radius=1, pitch=0, taper=0, pitch_func=None,
                  taper_func=None):
    """Deform mesh around cylinder of radius and axis z

    y = 0 will be on the surface of radius "radius"
    pitch != 0 will create a helix, with distance "pitch" traveled in z for each rotation
    taper = change in r over z. E.g. a value of 0.5 will shrink r by 0.5 for every z length of 1

    """
    """vert_function(s=s, x='(%s+y-taper)*sin(x/(%s+y))' % (radius, radius),
                     y='(%s+y)*cos(x/(%s+y))' % (radius, radius),
                     z='z-%s*x/(2*%s*(%s+y))' % (pitch, pi, radius))"""
    if pitch_func is None:
        pitch_func = '-(pitch)*x/(2*pi*(radius))'
    pitch_func = pitch_func.replace(
        'pitch', str(pitch)).replace(
            'pi', str(math.pi)).replace(
                'radius', str(radius))
    if taper_func is None:
        taper_func = '-(taper)*(pitch_func)'
    taper_func = taper_func.replace(
        'taper', str(taper)).replace(
            'pitch_func', str(pitch_func)).replace(
                'pi', str(math.pi))

    x_func = '(y+(radius)+(taper_func))*sin(x/(radius))'.replace(
        'radius', str(radius)).replace('taper_func', str(taper_func))
    y_func = '(y+(radius)+(taper_func))*cos(x/(radius))'.replace(
        'radius', str(radius)).replace('taper_func', str(taper_func))
    z_func = 'z+(pitch_func)'.replace('pitch_func', str(pitch_func))

    vert_function(script, x_func, y_func, z_func)
    return None


def wrap2sphere(script, radius=1):
    """
    """
    #r = 'sqrt(x^2+y^2)'

    r_func = '(z+(radius))*sin((r)/(radius))'.replace('radius', str(radius))
    z_func = '(z+(radius))*cos((r)/(radius))'.replace('radius', str(radius))

    #z_func='if(r<radius, sqrt(radius-r^2)-radius+z'.replace('radius', str(radius))
    #z_func='sqrt(radius-x^2-y^2)-radius+z'.replace('radius', str(radius))
    # z_func='sqrt(%s-x^2-y^2)-%s+z' % (sphere_radius**2, sphere_radius))
    function_cyl_co(script=script, r_func=r_func, z_func=z_func)
    return None


def emboss_sphere(script, radius=1, radius_limit=None, angle=None):
    """

    angle overrides radius_limit
    """
    if angle is not None:
        radius_limit = radius * math.sin(math.radians(angle / 2))
    if (radius_limit is None) or (radius_limit > radius):
        radius_limit = radius
    r = 'sqrt(x^2+y^2)'

    #r_func = '(z+radius)*sin(r/radius)'.replace('radius', str(radius))
    #z_func = '(z+radius)*cos(r/radius)'.replace('radius', str(radius))

    z_func = 'if((r)<=(radius_limit), sqrt((radius)^2-(r)^2)+z-sqrt((radius)^2-(radius_limit)^2), z)'
    #z_func='if((r<=radius), if((r<=radius_limit), sqrt(radius^2-r^2)+z-sqrt(radius^2-radius_limit^2), z), z)'
    #z_func='if((r<=radius) and (r<=radius_limit), sqrt(radius^2-r^2)+z-sqrt(radius^2-radius_limit^2), z)'
    z_func = re.sub(r"\br\b", r, z_func).replace(
        'radius_limit', str(radius_limit)).replace('radius', str(radius))

    #z_func='sqrt(radius-x^2-y^2)-radius+z'.replace('radius', str(radius))
    # z_func='sqrt(%s-x^2-y^2)-%s+z' % (sphere_radius**2, sphere_radius))
    vert_function(script=script, z_func=z_func)
    return None


def bend(script, radius=1, pitch=0, taper=0, angle=0, straght_start=True,
         straght_end=False, radius_limit=None, outside_limit_end=True):
    """Bends mesh around cylinder of radius radius and axis z to a certain angle

    straight_ends: Only apply twist (pitch) over the area that is bent

    outside_limit_end (bool): should values outside of the bend radius_limit be considered part
        of the end (True) or the start (False)?
    """
    if radius_limit is None:
        radius_limit = 2 * radius
    # TODO: add limit so bend only applies over y<2*radius; add option to set
    # larger limit
    angle = math.radians(angle)
    segment = radius * angle
    """vert_function(s=s, x='if(x<%s and x>-%s, (%s+y)*sin(x/%s), (%s+y)*sin(%s/%s)+(x-%s)*cos(%s/%s))'
                        % (segment, segment,  radius, radius,  radius, segment, radius, segment, segment, radius),
                     y='if(x<%s*%s/2 and x>-%s*%s/2, (%s+y)*cos(x/%s), (%s+y)*cos(%s)-(x-%s*%s)*sin(%s))'
                        % (radius, angle, radius, angle, radius, radius, radius, angle/2, radius, angle/2, angle/2),"""
    pitch_func = '-(pitch)*x/(2*pi*(radius))'.replace(
        'pitch', str(pitch)).replace(
            'pi', str(math.pi)).replace(
                'radius', str(radius))
    taper_func = '(taper)*(pitch_func)'.replace(
        'taper', str(taper)).replace(
            'pitch_func', str(pitch_func)).replace(
                'pi', str(math.pi))
    # y<radius_limit

    if outside_limit_end:
        x_func = 'if(x<(segment) and y<(radius_limit), if(x>0, (y+(radius)+(taper_func))*sin(x/(radius)), x), (y+(radius)+(taper_func))*sin(angle)+(x-(segment))*cos(angle))'
    else:
        x_func = 'if(x<(segment), if(x>0 and y<(radius_limit), (y+(radius)+(taper_func))*sin(x/(radius)), x), if(y<(radius_limit), (y+(radius)+(taper_func))*sin(angle)+(x-(segment))*cos(angle), x))'

    x_func = x_func.replace(
        # x_func = 'if(x<segment, if(x>0, (y+radius)*sin(x/radius), x),
        # (y+radius)*sin(angle)-segment)'.replace(
        'segment', str(segment)).replace(
            'radius_limit', str(radius_limit)).replace(
                'radius', str(radius)).replace(
                    'taper_func', str(taper_func)).replace(
                        'angle', str(angle))

    if outside_limit_end:
        y_func = 'if(x<(segment) and y<(radius_limit), if(x>0, (y+(radius)+(taper_func))*cos(x/(radius))-(radius), y), (y+(radius)+(taper_func))*cos(angle)-(x-(segment))*sin(angle)-(radius))'
    else:
        y_func = 'if(x<(segment), if(x>0 and y<(radius_limit), (y+(radius)+(taper_func))*cos(x/(radius))-(radius), y), if(y<(radius_limit), (y+(radius)+(taper_func))*cos(angle)-(x-(segment))*sin(angle)-(radius), y))'

    y_func = y_func.replace(
        'segment', str(segment)).replace(
            'radius_limit', str(radius_limit)).replace(
                'radius', str(radius)).replace(
                    'taper_func', str(taper_func)).replace(
                        'angle', str(angle))

    if straght_start:
        start = 'z'
    else:
        start = 'z+(pitch_func)'
    if straght_end:
        end = 'z-(pitch)*(angle)/(2*pi)'
    else:
        end = 'z+(pitch_func)'

    if outside_limit_end:
        z_func = 'if(x<(segment) and y<(radius_limit), if(x>0, z+(pitch_func), (start)), (end))'
    else:
        z_func = 'if(x<(segment), if(x>0 and y<(radius_limit), z+(pitch_func), (start)), if(y<(radius_limit), (end), z))'
    z_func = z_func.replace(
        'start', str(start)).replace(
            'end', str(end)).replace(
                'segment', str(segment)).replace(
                    'radius_limit', str(radius_limit)).replace(
                        'radius', str(radius)).replace(
                            'angle', str(angle)).replace(
                                'pitch_func', str(pitch_func)).replace(
                                    'pitch', str(pitch)).replace(
                                        'pi', str(math.pi))

    """
    if straight_ends:
        z_func = 'if(x<segment, if(x>0, z+(pitch_func), z), z-pitch*angle/(2*pi))'.replace(
            'segment', str(segment)).replace(
            'radius', str(radius)).replace(
            'angle', str(angle)).replace(
            'pitch_func', str(pitch_func)).replace(
            'pitch', str(pitch)).replace(
            'pi', str(math.pi))
    else:
        #z_func = 'if(x<segment, z+(pitch_func), z-(taper)*(pitch)*(x)/(2*pi*(radius)))'.replace(
        #z_func = 'if(x<segment, z+(pitch_func), z+(pitch_func))'.replace(
        #bestz_func = 'if(x<segment, z+(pitch_func), z+(pitch_func)+(-(taper)*(pitch)*(x-segment)/(2*pi*(radius))))'.replace(
        #z_func = 'if(x<segment, z+(pitch_func), z+(pitch_func)+(-(taper)*(pitch)*x/(2*pi*(radius))))'.replace(
        #z_func = 'if(x<segment, z+(pitch_func), z+(pitch_func)+((taper)*pitch*angle/(2*pi)))'.replace(
        z_func = 'z+(pitch_func)'.replace(
            'radius', str(radius)).replace(
            'segment', str(segment)).replace(
            'angle', str(angle)).replace(
            'taper', str(taper)).replace(
            'pitch_func', str(pitch_func)).replace(
            'pitch', str(pitch)).replace(
            'pi', str(math.pi))
    """
    """
    x_func = 'if(x<%s, if(x>-%s, (%s+y)*sin(x/%s), (%s+y)*sin(-%s)+(x+%s)*cos(-%s)), (%s+y)*sin(%s)+(x-%s)*cos(%s))' % (
        segment, segment, radius, radius, radius, angle, segment, angle, radius, angle, segment, angle)
    y_func = 'if(x<%s, if(x>-%s, (%s+y)*cos(x/%s), (%s+y)*cos(-%s)-(x+%s)*sin(-%s)), (%s+y)*cos(%s)-(x-%s)*sin(%s))' % (
        segment, segment, radius, radius, radius, angle, segment, angle, radius, angle, segment, angle)
    if straight_ends:
        z_func = 'if(x<%s, if(x>-%s, z-%s*x/(2*%s*%s), z+%s*%s/(2*%s)), z-%s*%s/(2*%s))' % (
            segment, segment, pitch, math.pi, radius, pitch, angle, math.pi, pitch, angle, math.pi)
    else:
        z_func = 'z-%s*x/(2*%s*%s)' % (pitch, math.pi, radius)
    """
    vert_function(script, x_func=x_func, y_func=y_func, z_func=z_func)
    return None


def deform2curve(script, curve=mp_func.torus_knot('t'), step=0.001):
    """ Deform a mesh along a parametric curve function

    Provide a parametric curve function with z as the parameter. This will
    deform the xy cross section of the mesh along the curve as z increases.

    Source: http://blackpawn.com/texts/pqtorus/

    Methodology:
    T  = P' - P
    N1 = P' + P
    B  = T x N1
    N  = B x T

    newPoint = point.x*N + point.y*B

    """
    curve_step = []
    for idx, val in enumerate(curve):
        curve[idx] = val.replace('t', 'z')
        curve_step.append(val.replace('t', 'z+{}'.format(step)))

    tangent = mp_func.v_subtract(curve_step, curve)
    normal1 = mp_func.v_add(curve_step, curve)
    bee = mp_func.v_cross(tangent, normal1)
    normal = mp_func.v_cross(bee, tangent)
    bee = mp_func.v_normalize(bee)
    normal = mp_func.v_normalize(normal)

    new_point = mp_func.v_add(mp_func.v_multiply('x', normal), mp_func.v_multiply('y', bee))
    function = mp_func.v_add(curve, new_point)

    vert_function(script, x_func=function[0], y_func=function[1], z_func=function[2])
    return function


# TODO: add function to round mesh to desired tolerance
# use muparser rint (round to nearest integer)
