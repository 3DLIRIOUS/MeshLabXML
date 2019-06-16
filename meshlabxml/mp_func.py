""" MeshLabXML muparser functions """

import math
import re

from . import FilterScript
from . import util


def muparser_ref():
    """Reference documentation for muparser.

    muparser is used by many internal MeshLab filters, specifically those
    where you can control parameters via a mathematical expression. Examples:
        transform.function
        select.vert_function
        vert_color.function

    The valid variables that can be used in an expression are given in the
    documentation for the individual functions. Generally, it's possible to use
    the following per-vertex variables in the expression:

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

    Below is a list of the predefined operators and functions within muparser.

    muparser homepage: http://beltoforion.de/article.php?a=muparser
    ml_version='1.3.4Beta' muparser version: 1.3.2
    ml_version='2016.12' muparser version: 2.2.5

    Built-in functions:
        Name    Argc.   Explanation
        ----------------------------
        sin     1       sine function
        cos     1       cosine function
        tan     1       tangens function
        asin    1       arcus sine function
        acos    1       arcus cosine function
        atan    1       arcus tangens function
        atan2   2       atan2(y, x)
        sinh    1       hyperbolic sine function
        cosh    1       hyperbolic cosine
        tanh    1       hyperbolic tangens function
        asinh   1       hyperbolic arcus sine function
        acosh   1       hyperbolic arcus tangens function
        atanh   1       hyperbolic arcur tangens function
        log2    1       logarithm to the base 2
        log10   1       logarithm to the base 10
        log     1       logarithm to the base 10
        ln      1       logarithm to base e (2.71828...)
        exp     1       e raised to the power of x
        sqrt    1       square root of a value
        sign    1       sign function -1 if x<0; 1 if x>0
        rint    1       round to nearest integer
        abs     1       absolute value
        min     var.    min of all arguments
        max     var.    max of all arguments
        sum     var.    sum of all arguments
        avg     var.    mean value of all arguments

    Built-in binary operators
        Operator    Description                Priority
        -----------------------------------------------
        =           assignment                 -1
        &&          logical and*                1
        ||          logical or*                 2
        <=          less or equal               4
        >=          greater or equal            4
        !=          not equal                   4
        ==          equal                       4
        >           greater than                4
        <           less than                   4
        +           addition                    5
        -           subtraction                 5
        *           multiplication              6
        /           division                    6
        ^           raise x to the power of y   7

    Built-in ternary operator
        ?:         (Test ? Then_value : Otherwise_value)*

    *: Some operators in older muparser (ml_version='1.3.4Beta') are different:
        and        logical and                 1
        or         logical or                  2
        if         ternary operator: if(Test, Then_value, Otherwise_value)
        atan2      not included; use mp_atan2 below
    """
    pass


def mp_atan2(y, x):
    """muparser atan2 function

    Implements an atan2(y,x) function for older muparser versions (<2.1.0);
    atan2 was added as a built-in function in muparser 2.1.0

    Args:
        y (str): y argument of the atan2(y,x) function
        x (str): x argument of the atan2(y,x) function

    Returns:
        A muparser string that calculates atan2(y,x)
    """
    return 'if((x)>0, atan((y)/(x)), if(((x)<0) and ((y)>=0), atan((y)/(x))+pi, if(((x)<0) and ((y)<0), atan((y)/(x))-pi, if(((x)==0) and ((y)>0), pi/2, if(((x)==0) and ((y)<0), -pi/2, 0)))))'.replace(
        'pi', str(math.pi)).replace('y', y).replace('x', x)


def modulo(a,b):
    """ Modulo operator
    Example: modulo(angle,2*pi) to limit an angle to within 2pi radians
    """
    return '(a < 0) ? b - (a - (b * rint(a/b))) : a - (b * rint(a/b))'.replace('a', a).replace('b', b)


def v_cross(u, v):
    """muparser cross product function

    Compute the cross product of two 3x1 vectors

    Args:
        u (list or tuple of 3 strings): first vector
        v (list or tuple of 3 strings): second vector
    Returns:
        A list containing a muparser string of the cross product
    """
    """
    i = u[1]*v[2] - u[2]*v[1]
    j = u[2]*v[0] - u[0]*v[2]
    k = u[0]*v[1] - u[1]*v[0]
    """

    i = '(({u1})*({v2}) - ({u2})*({v1}))'.format(u1=u[1], u2=u[2], v1=v[1], v2=v[2])
    j = '(({u2})*({v0}) - ({u0})*({v2}))'.format(u0=u[0], u2=u[2], v0=v[0], v2=v[2])
    k = '(({u0})*({v1}) - ({u1})*({v0}))'.format(u0=u[0], u1=u[1], v0=v[0], v1=v[1])
    return [i, j, k]


def v_dot(v1, v2):
    for i, x in enumerate(v1):
        if i == 0:
            dot = '({})*({})'.format(v1[i], v2[i])
        else:
            dot += '+({})*({})'.format(v1[i], v2[i])
    dot = '(' + dot + ')'
    return dot


def v_add(v1, v2):
    vector = []
    for i, x in enumerate(v1):
        vector.append('(({})+({}))'.format(v1[i], v2[i]))
    return vector


def v_subtract(v1, v2):
    vector = []
    for i, x in enumerate(v1):
        vector.append('(({})-({}))'.format(v1[i], v2[i]))
    return vector


def v_multiply(scalar, v1):
    """ Multiply vector by scalar"""
    vector = []
    for i, x in enumerate(v1):
        vector.append('(({})*({}))'.format(scalar, v1[i]))
    return vector


def v_length(v1):
    for i, x in enumerate(v1):
        if i == 0:
            length = '({})^2'.format(v1[i])
        else:
            length += '+({})^2'.format(v1[i])
    length = 'sqrt(' + length + ')'
    return length


def v_normalize(v1):
    vector = []
    length = v_length(v1)
    for i, x in enumerate(v1):
        vector.append('({})/({})'.format(v1[i], length))
    return vector


def torus_knot(t, p=3, q=4, scale=1.0, radius=2.0):
    """ A tight (small inner crossings) (p,q) torus knot parametric curve

    Source (for trefoil): https://en.wikipedia.org/wiki/Trefoil_knot

    """
    return ['{scale}*(sin({t}) + ({radius})*sin({p}*({t})))'.format(t=t, p=p, scale=scale, radius=radius),
            '{scale}*(cos({t}) - ({radius})*cos({p}*({t})))'.format(t=t, p=p, scale=scale, radius=radius),
            '{scale}*(-sin({q}*({t})))'.format(t=t, q=q, scale=scale)]

def torus_knot_bbox(scale=1.0, radius=2.0):
    """ Bounding box of the sprecified torus knot

    """
    return [2*scale*(1 + radius), 2*scale*(1 + radius), 2*scale]

def vert_attr(script, name='radius', function='x^2 + y^2'):
    """ Add a new Per-Vertex scalar attribute to current mesh and fill it with
        the defined function.

    The specified name can be used in other filter functions.

    It's possible to use parenthesis, per-vertex variables and boolean operator:
        (, ), and, or, <, >, =
    It's possible to use the following per-vertex variables in the expression:

    Variables:
        x, y, z (coordinates)
        nx, ny, nz (normal)
        r, g, b, a (color)
        q (quality)
        rad
        vi (vertex index)
        ?vtu, vtv (texture coordinates)
        ?ti (texture index)
        ?vsel (is the vertex selected? 1 yes, 0 no)
        and all custom vertex attributes already defined by user.

    Args:
        script: the FilterScript object or script filename to write
            the filter] to.
        name (str): the name of new attribute. You can access attribute in
            other filters through this name.
        function (str): function to calculate custom attribute value for each
            vertex

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Define New Per Vertex Attribute">\n',
        '    <Param name="name" ',
        'value="{}" '.format(name),
        'description="Name" ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="expr" ',
        'value="{}" '.format(str(function).replace('&', '&amp;').replace('<', '&lt;')),
        'description="Function" ',
        'type="RichString" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def face_attr(script, name='radiosity', function='fi'):
    """ Add a new Per-Face attribute to current mesh and fill it with
        the defined function..

    The specified name can be used in other filter functions.

    It's possible to use parenthesis, per-face variables and boolean operator:
        (, ), and, or, <, >, =

    It's possible to use per-face variables like attributes associated to the
    three vertices of every face.

    It's possible to use the following per-face variables in the expression:

    Variables:
        x0,y0,z0 (first vertex); x1,y1,z1 (second vertex); x2,y2,z2 (third vertex)
        nx0,ny0,nz0; nx1,ny1,nz1; nx2,ny2,nz2 (normals)
        r0,g0,b0 (color)
        q0,q1,q2 (quality)
        wtu0, wtv0; wtu1, wtv1; wtu2, wtv2 (per wedge tex coord)
        fi (face index)
        ?fsel (is the vertex selected? 1 yes, 0 no)
        fi (face index)
        and all custom face attributes already defined by user.

    Args:
        script: the FilterScript object or script filename to write
            the filter] to.
        name (str): the name of new attribute. You can access attribute in
            other filters through this name.
        function (str): function to calculate custom attribute value for each
            face

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Define New Per Face Attribute">\n',
        '    <Param name="name" ',
        'value="{}" '.format(name),
        'description="Name" ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="expr" ',
        'value="{}" '.format(str(function).replace('&', '&amp;').replace('<', '&lt;')),
        'description="Function" ',
        'type="RichString" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None

def vq_function(script, function='vi', normalize=False, color=False):
    """:Quality function using muparser to generate new Quality for every vertex<br>It's possibile to use the following per-vertex variables in the expression:<br>x, y, z, nx, ny, nz (normal), r, g, b (color), q (quality), rad, vi, <br>and all custom <i>vertex attributes</i> already defined by user.


    function function to generate new Quality for every vertex
    normalize if checked normalize all quality values in range [0..1]
    color if checked map quality generated values into per-vertex color

    """
    filter_xml = ''.join([
        '  <filter name="Per Vertex Quality Function">\n',
        '    <Param name="q" ',
        'value="{}" '.format(str(function).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func q = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="normalize" ',
        'value="{}" '.format(str(normalize).lower()),
        'description="normalize" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="map" ',
        'value="{}" '.format(str(color).lower()),
        'description="map into color" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None

def fq_function(script, function='x0+y0+z0', normalize=False, color=False):
    """ :Quality function using muparser to generate new Quality for every face<br>Insert three function each one for quality of the three vertex of a face<br>It's possibile to use per-face variables like attributes associated to the three vertex of every face.<br><b>x0,y0,z0</b> for <b>first vertex</b>; x1,y1,z1 for second vertex; x2,y2,z2 for third vertex.<br>and also <b>nx0,ny0,nz0</b> nx1,ny1,nz1 etc. for <b>normals</b> and <b>r0,g0,b0</b> for <b>color</b>,<b>q0,q1,q2</b> for <b>quality</b>.<br>

    function function to generate new Quality for each face
    normalize if checked normalize all quality values in range [0..1]
    color if checked map quality generated values into per-vertex color


    """
    filter_xml = ''.join([
        '  <filter name="Per Face Quality Function">\n',
        '    <Param name="q" ',
        'value="{}" '.format(str(function).replace('&', '&amp;').replace('<', '&lt;')),
        'description="func q0 = " ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="normalize" ',
        'value="{}" '.format(str(normalize).lower()),
        'description="normalize" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="map" ',
        'value="{}" '.format(str(color).lower()),
        'description="map into color" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None
