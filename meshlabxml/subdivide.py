""" MeshLabXML subdivide functions """

from . import util

def loop(script, iterations=1, loop_weight=0, edge_threshold=0,
         selected=False):
    """ Apply Loop's Subdivision Surface algorithm.

    It is an approximant subdivision method and it works for every triangle
    and has rules for extraordinary vertices.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): Number of times the model is subdivided.
        loop_weight (int): Change the weights used. Allow to optimize some
            behaviours in spite of others. Valid values are:
            0 - Loop (default)
            1 - Enhance regularity
            2 - Enhance continuity
        edge_threshold (float): All the edges longer than this threshold will
            be refined. Setting this value to zero will force a uniform
            refinement.
        selected (bool): If selected the filter is performed only on the
            selected faces.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Subdivision Surfaces: Loop">\n',
        '    <Param name="LoopWeight" ',
        'value="{:d}" '.format(loop_weight),
        'description="Weighting scheme" ',
        'enum_val0="Loop" ',
        'enum_val1="Enhance regularity" ',
        'enum_val2="Enhance continuity" ',
        'enum_cardinality="3" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="Iterations" ',
        'value="{:d}" '.format(iterations),
        'description="Iterations" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Threshold" ',
        'value="{}" '.format(edge_threshold),
        'description="Edge Threshold" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Affect only selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def ls3loop(script, iterations=1, loop_weight=0, edge_threshold=0,
            selected=False):
    """ Apply LS3 Subdivision Surface algorithm using Loop's weights.

    This refinement method take normals into account.
    See: Boye', S. Guennebaud, G. & Schlick, C.
    "Least squares subdivision surfaces"
    Computer Graphics Forum, 2010.

    Alternatives weighting schemes are based on the paper:
    Barthe, L. & Kobbelt, L.
    "Subdivision scheme tuning around extraordinary vertices"
    Computer Aided Geometric Design, 2004, 21, 561-583.

    The current implementation of these schemes don't handle vertices of
    valence > 12

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): Number of times the model is subdivided.
        loop_weight (int): Change the weights used. Allow to optimize some
            behaviours in spite of others. Valid values are:
            0 - Loop (default)
            1 - Enhance regularity
            2 - Enhance continuity
        edge_threshold (float): All the edges longer than this threshold will
            be refined. Setting this value to zero will force a uniform
            refinement.
        selected (bool): If selected the filter is performed only on the
            selected faces.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Subdivision Surfaces: LS3 Loop">\n',
        '    <Param name="LoopWeight" ',
        'value="{:d}" '.format(loop_weight),
        'description="Weighting scheme" ',
        'enum_val0="Loop" ',
        'enum_val1="Enhance regularity" ',
        'enum_val2="Enhance continuity" ',
        'enum_cardinality="3" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="Iterations" ',
        'value="{:d}" '.format(iterations),
        'description="Iterations" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Threshold" ',
        'value="{}" '.format(edge_threshold),
        'description="Edge Threshold" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Affect only selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def midpoint(script, iterations=1, edge_threshold=0, selected=False):
    """ Apply a plain subdivision scheme where every edge is split on its
        midpoint.

    Useful to uniformly refine a mesh substituting each triangle with four
    smaller triangles.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): Number of times the model is subdivided.
        edge_threshold (float): All the edges longer than this threshold will
            be refined. Setting this value to zero will force a uniform
            refinement.
        selected (bool): If selected the filter is performed only on the
            selected faces.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Subdivision Surfaces: Midpoint">\n',
        '    <Param name="Iterations" ',
        'value="{:d}" '.format(iterations),
        'description="Iterations" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Threshold" ',
        'value="{}" '.format(edge_threshold),
        'description="Edge Threshold" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Affect only selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def butterfly(script, iterations=1, edge_threshold=0, selected=False):
    """ Apply Butterfly Subdivision Surface algorithm.

    It is an interpolated method, defined on arbitrary triangular meshes.
    The scheme is known to be C1 but not C2 on regular meshes.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): Number of times the model is subdivided.
        edge_threshold (float): All the edges longer than this threshold will
            be refined. Setting this value to zero will force a uniform
            refinement.
        selected (bool): If selected the filter is performed only on the
            selected faces.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Subdivision Surfaces: Butterfly Subdivision">\n',
        '    <Param name="Iterations" ',
        'value="{:d}" '.format(iterations),
        'description="Iterations" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Threshold" ',
        'value="{}" '.format(edge_threshold),
        'description="Edge Threshold" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Affect only selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def catmull_clark(script):
    """ Apply the Catmull-Clark Subdivision Surfaces.

    Note that position of the new vertices is simply linearly interpolated.
    If the mesh is triangle based (no faux edges) it generates a quad mesh,
    otherwise it honors the faux-edge bits.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Subdivision Surfaces: Catmull-Clark"/>\n'
    util.write_filter(script, filter_xml)
    return None
