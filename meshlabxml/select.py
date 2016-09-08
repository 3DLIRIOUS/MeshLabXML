"""MeshLabXML selection functions"""


def deselect(script='TEMP3D_default.mlx', face=True,
             vert=True, current_layer=None, last_layer=None):
    """Clear the current set of selected faces

    Args:
        script (str): filename of the mlx script file to write to.
        faces (bool): If true the filter will deselect all the faces.
        verts (bool): If true the filter will deselect all the vertices.
        current_layer (int): number of the current layer
        last_layer (int): number of the last (highest numbered) layer

    Returns:
        current_layer, last_layer

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Select None">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="allFaces"',
        'value="%s"' % str(face).lower(),
        'description="De-select all Faces"',
        'type="RichBool"',
        'tooltip="If true the filter will de-select all the faces."',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="allVerts"',
        'value="%s"' % str(vert).lower(),
        'description="De-select all Vertices"',
        'type="RichBool"',
        'tooltip="If true the filter will de-select all the vertices."',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def invert(script='TEMP3D_default.mlx', face=True,
           vert=True, current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Invert Selection">\n' +

                      '    <Param name="InvFaces" ' +
                      'value="%s" ' % str(face).lower() +
                      'description="Invert Faces" ' +
                      'type="RichBool" ' +
                      'tooltip="If true  the filter will invert the selected' +
                      ' faces."/>\n' +

                      '    <Param name="InvVerts" ' +
                      'value="%s" ' % str(vert).lower() +
                      'description="Invert Vertices" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the filter will invert the selected' +
                      ' vertices."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def border(script='TEMP3D_default.mlx',
           current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Select Border"/>\n')
    script_file.close()
    return current_layer, last_layer


def grow(script='TEMP3D_default.mlx', iterations=1,
         current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    i = 0
    while i < iterations:
        script_file.write('  <filter name="Dilate Selection"/>\n')
        i += 1
    script_file.close()
    return current_layer, last_layer


def shrink(script='TEMP3D_default.mlx', iterations=1,
           current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    i = 0
    while i < iterations:
        script_file.write('  <filter name="Erode Selection"/>\n')
        i += 1
    script_file.close()
    return current_layer, last_layer


def self_intersecting_face(script='TEMP3D_default.mlx',
                           current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Select Self Intersecting Faces"/>\n')
    script_file.close()
    return current_layer, last_layer


def nonmanifold_vert(script='TEMP3D_default.mlx',
                     current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Select non Manifold Vertices"/>\n')
    script_file.close()
    return current_layer, last_layer


def nonmanifold_edge(script='TEMP3D_default.mlx',
                     current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Select non Manifold Edges"/>\n')
    script_file.close()
    return current_layer, last_layer


def small_parts(script='TEMP3D_default.mlx', ratio=0.2,
                non_closed_only=False, current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Small component selection">\n' +

                      '    <Param name="NbFaceRatio" ' +
                      'value="%s" ' % ratio +
                      'description="Small component ratio" ' +
                      'type="RichFloat" ' +
                      'tooltip="This ratio (between 0 and 1) defines the meaning of' +
                      ' _small_as the threshold ratio between the number of faces of' +
                      ' the largest component and the other ones. A larger value' +
                      ' will select more components."/>\n' +

                      '    <Param name="NonClosedOnly" ' +
                      'value="%s" ' % str(non_closed_only).lower() +
                      'description="Select only non closed components" ' +
                      'type="RichBool" ' +
                      'tooltip="Select only non-closed components."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def vert_quality(script='TEMP3D_default.mlx', min_quality=0.0, max_quality=0.05,
                 inclusive=True, current_layer=None, last_layer=None):
    # TODO: set min & max better
    script_file = open(script, 'a')
    script_file.write('  <filter name="Select by Vertex Quality">\n' +

                      '    <Param name="minQ" ' +
                      'value="%s" ' % min_quality +
                      'description="Min Quality" ' +
                      'min="0" ' +
                      'max="0.1" ' +
                      'type="RichDynamicFloat" ' +
                      'tooltip="Minimum acceptable quality value."/>\n' +

                      '    <Param name="maxQ" ' +
                      'value="%s" ' % max_quality +
                      'description="Max Quality" ' +
                      'min="0" ' +
                      'max="0.1" ' +
                      'type="RichDynamicFloat" ' +
                      'tooltip="Maximum acceptable quality value."/>\n' +

                      '    <Param name="Inclusive" ' +
                      'value="%s" ' % str(inclusive).lower() +
                      'description="Inclusive Sel." ' +
                      'type="RichBool" ' +
                      'tooltip="If true only the faces with _all_ the vertices' +
                      ' within the specified range are selected. Otherwise any face' +
                      ' with at least one vertex within the range is selected."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def face_function(script='TEMP3D_default.mlx',
                  function='(fi == 0)', current_layer=None, last_layer=None):
    """Boolean function using muparser lib to perform face selection over current mesh.

    See help(mlx.muparser_ref) for muparser reference documentation.

    It's possible to use parenthesis, per-vertex variables and boolean operator:
        (, ), and, or, <, >, =
    It's possible to use per-face variables like attributes associated to the three
    vertices of every face.

    Variables (per face):
        x0, y0, z0 for first vertex; x1,y1,z1 for second vertex; x2,y2,z2 for third vertex
        nx0, ny0, nz0, nx1, ny1, nz1, etc. for normals
        r0, g0, b0 for color
        q0, q1, q2 for quality
        wtu0, wtv0, wtu1, wtv1, wtu2, wtv2 (per wedge texture coordinates)

    Args:
        function (str): a boolean function that will be evaluated in order
            to select a subset of faces.

    Returns:
        current_layer, last_layer

    """

    script_file = open(script, 'a')
    script_file.write('  <filter name="Conditional Face Selection">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="condSelect"',
        'value="%s"' % str(function).replace('<', '&lt;'),
        'description="boolean function"',
        'type="RichString"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def vert_function(script='TEMP3D_default.mlx', function='(q < 0)',
                  strict_face_select=True, current_layer=None, last_layer=None):
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
        function (str): a boolean function that will be evaluated in order
            to select a subset of vertices. Example: (y > 0) and (ny > 0)
        strict_face_select (bool): if True a face is selected if ALL its
            vertices are selected. If False a face is selected if at least
            one of its vertices is selected.

    Returns:
        current_layer, last_layer

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Conditional Vertex Selection">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="condSelect"',
        'value="%s"' % str(function).replace('<', '&lt;'),
        'description="boolean function"',
        'type="RichString"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="strictSelect"',
        'value="%s"' % str(strict_face_select).lower(),
        'description="Strict face selection"',
        'type="RichBool"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def spherical(script='TEMP3D_default.mlx',
              radius=1.0, center_pt=(0.0, 0.0, 0.0),
              strict_face_select=True,
              current_layer=None, last_layer=None):
    """Select all verties within a spherical radius

    Args:
        radius (float): radius of the sphere
        center_pt (tuple or list): center point of the sphere

    Returns:
        current_layer, last_layer

    """
    if not isinstance(center_pt, list):
        center_pt = list(center_pt)

    function = 'sqrt((x-%s)^2+(y-%s)^2+(z-%s)^2)<=%s' % (
        center_pt[0], center_pt[1], center_pt[2], radius)
    vert_function(script, function=function,
                  strict_face_select=strict_face_select)
    return current_layer, last_layer
