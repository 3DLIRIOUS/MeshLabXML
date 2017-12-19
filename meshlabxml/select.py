"""MeshLabXML selection functions"""

from . import util


def all(script, face=True, vert=True):
    """ Select all the faces of the current mesh

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        faces (bool): If True the filter will select all the faces.
        verts (bool): If True the filter will select all the vertices.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Select All">\n',
        '    <Param name="allFaces" ',
        'value="{}" '.format(str(face).lower()),
        'description="DSelect all Faces" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="allVerts" ',
        'value="{}" '.format(str(vert).lower()),
        'description="Select all Vertices" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def none(script, face=True, vert=True):
    """ Clear the current set of selected faces

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        faces (bool): If True the filter will deselect all the faces.
        verts (bool): If True the filter will deselect all the vertices.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Select None">\n',
        '    <Param name="allFaces" ',
        'value="{}" '.format(str(face).lower()),
        'description="De-select all Faces" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="allVerts" ',
        'value="{}" '.format(str(vert).lower()),
        'description="De-select all Vertices" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def invert(script, face=True, vert=True):
    """  Invert the current set of selected faces

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        faces (bool): If True the filter will invert the selected faces.
        verts (bool): If True the filter will invert the selected vertices.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Invert Selection">\n',
        '    <Param name="InvFaces" ',
        'value="{}" '.format(str(face).lower()),
        'description="Invert Faces" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="InvVerts" ',
        'value="{}" '.format(str(vert).lower()),
        'description="Invert Vertices" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def border(script):
    """ Select vertices and faces on the boundary

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Select Border"/>\n'
    util.write_filter(script, filter_xml)
    return None


def grow(script, iterations=1):
    """ Grow (dilate, expand) the current set of selected faces

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): the number of times to grow the selection.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Dilate Selection"/>\n'
    for _ in range(iterations):
        util.write_filter(script, filter_xml)
    return None


def shrink(script, iterations=1):
    """ Shrink (erode, reduce) the current set of selected faces

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): the number of times to shrink the selection.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Erode Selection"/>\n'
    for _ in range(iterations):
        util.write_filter(script, filter_xml)
    return None


def self_intersecting_face(script):
    """ Select only self intersecting faces

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Select Self Intersecting Faces"/>\n'
    util.write_filter(script, filter_xml)
    return None


def nonmanifold_vert(script):
    """ Select the non manifold vertices that do not belong to non manifold
        edges.

    For example two cones connected by their apex. Vertices incident on
    non manifold edges are ignored.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Select non Manifold Vertices"/>\n'
    util.write_filter(script, filter_xml)
    return None


def nonmanifold_edge(script):
    """ Select the faces and the vertices incident on non manifold edges (e.g.
        edges where more than two faces are incident).

    Note that this function selects the components that are related to
    non manifold edges. The case of non manifold vertices is specifically
    managed by nonmanifold_vert.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Select non Manifold Edges "/>\n'
    util.write_filter(script, filter_xml)
    return None


def small_parts(script, ratio=0.2, non_closed_only=False):
    """ Select the small disconnected parts (components) of a mesh.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        ratio (float): This ratio (between 0 and 1) defines the meaning of
            'small' as the threshold ratio between the number of faces of the
            largest component and the other ones. A larger value will select
            more components.
        non_closed_only (bool): Select only non-closed components.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Small component selection">\n',
        '    <Param name="NbFaceRatio" ',
        'value="{}" '.format(ratio),
        'description="Small component ratio" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="NonClosedOnly" ',
        'value="{}" '.format(str(non_closed_only).lower()),
        'description="Select only non closed components" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def vert_quality(script, min_quality=0.0, max_quality=0.05, inclusive=True):
    """ Select all the faces and vertexes within the specified vertex quality
        range.

    Args:
        script: the FilterScript object or script filename to write
            the filter] to.
        min_quality (float): Minimum acceptable quality value.
        max_quality (float): Maximum acceptable quality value.
        inclusive (bool): If True only the faces with ALL the vertices within
            the specified range are selected. Otherwise any face with at least
            one vertex within the range is selected.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Select by Vertex Quality">\n',
        '    <Param name="minQ" ',
        'value="{}" '.format(min_quality),
        'description="Min Quality" ',
        'min="0" ',
        'max="{}" '.format(2 * max_quality),
        'type="RichDynamicFloat" ',
        '/>\n',
        '    <Param name="maxQ" ',
        'value="{}" '.format(max_quality),
        'description="Max Quality" ',
        'min="0" ',
        'max="{}" '.format(2 * max_quality),
        'type="RichDynamicFloat" ',
        '/>\n',
        '    <Param name="Inclusive" ',
        'value="{}" '.format(str(inclusive).lower()),
        'description="Inclusive Sel." ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def face_function(script, function='(fi == 0)'):
    """Boolean function using muparser lib to perform face selection over
        current mesh.

    See help(mlx.muparser_ref) for muparser reference documentation.

    It's possible to use parenthesis, per-vertex variables and boolean operator:
        (, ), and, or, <, >, =
    It's possible to use per-face variables like attributes associated to the three
    vertices of every face.

    Variables (per face):
        x0, y0, z0 for first vertex; x1,y1,z1 for second vertex; x2,y2,z2 for third vertex
        nx0, ny0, nz0, nx1, ny1, nz1, etc. for vertex normals
        r0, g0, b0, a0, etc. for vertex color
        q0, q1, q2 for quality
        wtu0, wtv0, wtu1, wtv1, wtu2, wtv2 (per wedge texture coordinates)
        ti for face texture index (>= ML2016.12)
        vsel0, vsel1, vsel2 for vertex selection (1 yes, 0 no) (>= ML2016.12)
        fr, fg, fb, fa for face color (>= ML2016.12)
        fq for face quality (>= ML2016.12)
        fnx, fny, fnz for face normal (>= ML2016.12)
        fsel face selection (1 yes, 0 no) (>= ML2016.12)

    Args:
        script: the FilterScript object or script filename to write
            the filter] to.
        function (str): a boolean function that will be evaluated in order
            to select a subset of faces.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Conditional Face Selection">\n',
        '    <Param name="condSelect" ',
        'value="{}" '.format(str(function).replace('&', '&amp;').replace('<', '&lt;')),
        'description="boolean function" ',
        'type="RichString" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def vert_function(script, function='(q < 0)', strict_face_select=True):
    """Boolean function using muparser lib to perform vertex selection over current mesh.

    See help(mlx.muparser_ref) for muparser reference documentation.

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
        vtu, vtv (texture coordinates)
        ti (texture index)
        vsel (is the vertex selected? 1 yes, 0 no)
        and all custom vertex attributes already defined by user.

    Args:
        script: the FilterScript object or script filename to write
            the filter] to.
        function (str): a boolean function that will be evaluated in order
            to select a subset of vertices. Example: (y > 0) and (ny > 0)
        strict_face_select (bool): if True a face is selected if ALL its
            vertices are selected. If False a face is selected if at least
            one of its vertices is selected. ML v1.3.4BETA only; this is
            ignored in 2016.12. In 2016.12 only vertices are selected.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    if script.ml_version == '1.3.4BETA':
        strict_select = ''.join([
            '    <Param name="strictSelect" ',
            'value="{}" '.format(str(strict_face_select).lower()),
            'description="Strict face selection" ',
            'type="RichBool" ',
            '/>\n',
            ])
    else:
        strict_select = ''

    filter_xml = ''.join([
        '  <filter name="Conditional Vertex Selection">\n',
        '    <Param name="condSelect" ',
        'value="{}" '.format(str(function).replace('&', '&amp;').replace('<', '&lt;')),
        'description="boolean function" ',
        'type="RichString" ',
        '/>\n',
        strict_select,
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def cylindrical_vert(script, radius=1.0, inside=True):
    """Select all vertices within a cylindrical radius

    Args:
        radius (float): radius of the sphere
        center_pt (3 coordinate tuple or list): center point of the sphere

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    if inside:
        function = 'sqrt(x^2+y^2)<={}'.format(radius)
    else:
        function = 'sqrt(x^2+y^2)>={}'.format(radius)
    vert_function(script, function=function)
    return None


def spherical_vert(script, radius=1.0, center_pt=(0.0, 0.0, 0.0)):
    """Select all vertices within a spherical radius

    Args:
        radius (float): radius of the sphere
        center_pt (3 coordinate tuple or list): center point of the sphere

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    function = 'sqrt((x-{})^2+(y-{})^2+(z-{})^2)<={}'.format(
        center_pt[0], center_pt[1], center_pt[2], radius)
    vert_function(script, function=function)
    return None
