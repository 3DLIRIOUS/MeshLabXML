""" MeshLabXML smoothing functions """

from . import util

def laplacian(script, iterations=1, boundary=True, cotangent_weight=True,
              selected=False):
    """ Laplacian smooth of the mesh: for each vertex it calculates the average
        position with nearest vertex

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): The number of times that the whole algorithm (normal
            smoothing + vertex fitting) is iterated.
        boundary (bool): If true the boundary edges are smoothed only by
            themselves (e.g. the polyline forming the boundary of the mesh is
            independently smoothed). Can reduce the shrinking on the border but
            can have strange effects on very small boundaries.
        cotangent_weight (bool): If True the cotangent weighting scheme is
            computed for the averaging of the position. Otherwise (False) the
            simpler umbrella scheme (1 if the edge is present) is used.
        selected (bool): If selected the filter is performed only on the
            selected faces

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Laplacian Smooth">\n',
        '    <Param name="stepSmoothNum" ',
        'value="{:d}" '.format(iterations),
        'description="Smoothing steps" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Boundary" ',
        'value="{}" '.format(str(boundary).lower()),
        'description="1D Boundary Smoothing" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="cotangentWeight" ',
        'value="{}" '.format(str(cotangent_weight).lower()),
        'description="Cotangent weighting" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Affect only selected faces" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None

