""" MeshLabXML functions for mesh normals """

from . import util


def reorient(script):
    """ Re-orient in a consistent way all the faces of the mesh.

    The filter visits a mesh face to face, reorienting any unvisited face so
    that it is coherent to the already visited faces. If the surface is
    orientable it will end with a consistent orientation of all the faces. If
    the surface is not orientable (e.g. it is non manifold or non orientable
    like a moebius strip) the filter will not build a consistent orientation
    simply because it is not possible. The filter can end up in a consistent
    orientation that can be exactly the opposite of the expected one; in that
    case simply invert the whole mesh orientation.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Re-Orient all faces coherentely"/>\n'])
    util._write_filter(script, filter_xml)
    return None


def flip(script, force_flip=False, selected=False):
    """ Invert faces orientation, flipping the normals of the mesh.

    If requested, it tries to guess the right orientation; mainly it decides to
    flip all the faces if the minimum/maximum vertexes have not outward point
    normals for a few directions. Works well for single component watertight
    objects.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        force_flip (bool): If selected, the normals will always be flipped;
            otherwise, the filter tries to set them outside.
        selected (bool): If selected, only selected faces will be affected.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Invert Faces Orientation">\n',

        '    <Param name="forceFlip" ',
        'value="{}" '.format(str(force_flip).lower()),
        'description="Force Flip" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="onlySelected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Flip only selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util._write_filter(script, filter_xml)
    return None


def fix(script):
    """ Will reorient normals & ensure they are oriented outwards


    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    reorient(script)
    flip(script)
    return


def point_sets(script, neighbors=10, smooth_iteration=0, flip=False,
               viewpoint_pos=(0.0, 0.0, 0.0)):
    """ Compute the normals of the vertices of a mesh without exploiting the
        triangle connectivity, useful for dataset with no faces.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        neighbors (int): The number of neighbors used to estimate normals.
        smooth_iteration (int): The number of smoothing iteration done on the
            p used to estimate and propagate normals.
        flip (bool): Flip normals w.r.t. viewpoint. If the 'viewpoint' (i.e.
            scanner position) is known, it can be used to disambiguate normals
            orientation, so that all the normals will be oriented in the same
            direction.
        viewpoint_pos (single xyz point, tuple or list): Set the x, y, z
            coordinates of the viewpoint position.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Compute normals for point sets">\n',
        '    <Param name="K" ',
        'value="{:d}" '.format(neighbors),
        'description="Neighbour num" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="smoothIter" ',
        'value="{:d}" '.format(smooth_iteration),
        'description="Smooth Iteration" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="flipFlag" ',
        'value="{}" '.format(str(flip).lower()),
        'description="Flip normals w.r.t. viewpoint" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="viewPos" ',
        'x="{}" y="{}" z="{}" '.format(viewpoint_pos[0], viewpoint_pos[1],
                                       viewpoint_pos[2],),
        'description="Viewpoint Pos." ',
        'type="RichPoint3f" ',
        '/>\n',
        '  </filter>\n'])
    util._write_filter(script, filter_xml)
    return None
