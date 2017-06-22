"""MeshLabXML cleaning and repairing functions

See select and delete modules for additional cleaning functions
"""

from . import util


def merge_vert(script, threshold=0.0):
    """ Merge together all the vertices that are nearer than the specified
    threshold. Like a unify duplicate vertices but with some tolerance.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        threshold (float): Merging distance. All the vertices that are closer
            than this threshold are merged together. Use very small values,
            default is zero.

    Layer stack:
        No impacts; this filter only works on the current layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Merge Close Vertices">\n',
        '    <Param name="Threshold" ',
        'value="{}" '.format(threshold),
        'description="Merging distance" ',
        'min="0" ',
        'max="1" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '  </filter>\n'])
    util._write_filter(script, filter_xml)
    return None


def close_holes(script, hole_max_edge=30, selected=False,
                sel_new_face=True, self_intersection=True):
    """ Close holes smaller than a given threshold

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        hole_max_edge (int): The size is expressed as number of edges composing
            the hole boundary.
        selected (bool): Only the holes with at least one of the boundary faces
            selected are closed.
        sel_new_face (bool): After closing a hole the faces that have been
            created are left selected. Any previous selection is lost. Useful
            for example for smoothing or subdividing the newly created holes.
        self_intersection (bool): When closing an holes it tries to prevent the
            creation of faces that intersect faces adjacent to the boundary of
            the hole. It is an heuristic, non intersecting hole filling can be
            NP-complete.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Close Holes">\n',
        '    <Param name="maxholesize" ',
        'value="{:d}" '.format(hole_max_edge),
        'description="Max size to be closed" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Close holes with selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="NewFaceSelected" ',
        'value="{}" '.format(str(sel_new_face).lower()),
        'description="Select the newly created faces" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SelfIntersection" ',
        'value="{}" '.format(str(self_intersection).lower()),
        'description="Prevent creation of selfIntersecting faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util._write_filter(script, filter_xml)
    return None


def split_vert_on_nonmanifold_face(script, vert_displacement_ratio=0.0):
    """ Split non-manifold vertices until it becomes two-manifold.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        vert_displacement_ratio (float): When a vertex is split it is moved
            along the average vector going from its position to the centroid
            of the FF connected faces sharing it.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Split Vertexes Incident on Non Manifold Faces">\n',
        '    <Param name="VertDispRatio" ',
        'value="{}" '.format(vert_displacement_ratio),
        'description="Vertex Displacement Ratio" ',
        'type="RichFloat" ',
        '/>\n',
        '  </filter>\n'])
    util._write_filter(script, filter_xml)
    return None


def fix_folded_face(script):
    """ Delete all the single folded faces.

    A face is considered folded if its normal is opposite to all the adjacent
    faces. It is removed by flipping it against the face f adjacent along the
    edge e such that the vertex opposite to e fall inside f.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Remove Isolated Folded Faces by Edge Flip"/>\n'
    util._write_filter(script, filter_xml)
    return None


def snap_mismatched_borders(script, edge_dist_ratio=0.01, unify_vert=True):
    """ Try to snap together adjacent borders that are slightly mismatched.

    This situation can happen on badly triangulated adjacent patches defined by
    high order surfaces. For each border vertex the filter snaps it onto the
    closest boundary edge only if it is closest of edge_legth*threshold. When
    vertex is snapped the corresponding face it split and a new vertex is
    created.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        edge_dist_ratio (float): Collapse edge when the edge / distance ratio
            is greater than this value. E.g. for default value 1000 two
            straight border edges are collapsed if the central vertex dist from
            the straight line composed by the two edges less than a 1/1000 of
            the sum of the edges length. Larger values enforce that only
            vertexes very close to the line are removed.
        unify_vert (bool): If true the snap vertices are welded together.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Snap Mismatched Borders">\n',
        '    <Param name="EdgeDistRatio" ',
        'value="{}" '.format(edge_dist_ratio),
        'description="Edge Distance Ratio" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="UnifyVertices" ',
        'value="{}" '.format(str(unify_vert).lower()),
        'description="UnifyVertices" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util._write_filter(script, filter_xml)
    return None
