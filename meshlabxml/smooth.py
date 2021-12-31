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
        '    <Param value="{:d}" '.format(iterations),
        'type="RichInt" ',
        'name="stepSmoothNum" ',
        'description="Smoothing steps" ',
        '/>\n',
        '    <Param value="{}" '.format(str(boundary).lower()),
        'type="RichBool" ',
        'name="Boundary" ',
        'description="1D Boundary Smoothing" ',
        '/>\n',
        '    <Param value="{}" '.format(str(cotangent_weight).lower()),
        'type="RichBool" ',
        'name="cotangentWeight" ',
        'description="Cotangent weighting" ',
        '/>\n',
        '    <Param value="{}" '.format(str(selected).lower()),
        'type="RichBool" ',
        'name="Selected" ',
        'description="Affect only selected faces" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def hc_laplacian(script):
    """ HC Laplacian Smoothing, extended version of Laplacian Smoothing, based
        on the paper of Vollmer, Mencl, and Muller

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="HC Laplacian Smooth"/>\n'
    util.write_filter(script, filter_xml)
    return None


def taubin(script, iterations=10, t_lambda=0.5, t_mu=-0.53, selected=False):
    """ The lambda & mu Taubin smoothing, it make two steps of smoothing, forth
        and back, for each iteration.

    Based on:
    Gabriel Taubin
    "A signal processing approach to fair surface design"
    Siggraph 1995

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): The number of times that the taubin smoothing is
            iterated. Usually it requires a larger number of iteration than the
            classical laplacian.
        t_lambda (float): The lambda parameter of the Taubin Smoothing algorithm
        t_mu (float): The mu parameter of the Taubin Smoothing algorithm
        selected (bool): If selected the filter is performed only on the
            selected faces

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Taubin Smooth">\n',
        '    <Param value="{}" '.format(t_lambda),
        'name="lambda" ',
        'description="Lambda" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param value="{}" '.format(t_mu),
        'type="RichFloat" ',
        'name="mu" ',
        'description="mu" ',
        '/>\n',
        '    <Param value="{:d}" '.format(iterations),
        'type="RichInt" ',
        'name="stepSmoothNum" ',
        'description="Smoothing steps" ',
        '/>\n',
        '    <Param value="{}" '.format(str(selected).lower()),
        'type="RichBool" ',
        'name="Selected" ',
        'description="Affect only selected faces" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def twostep(script, iterations=3, angle_threshold=60, normal_steps=20, fit_steps=20,
            selected=False):
    """ Two Step Smoothing, a feature preserving/enhancing fairing filter.

    It is based on a Normal Smoothing step where similar normals are averaged
    together and a step where the vertexes are fitted on the new normals.

    Based on:
    A. Belyaev and Y. Ohtake,
    "A Comparison of Mesh Smoothing Methods"
    Proc. Israel-Korea Bi-National Conf. Geometric Modeling and Computer
    Graphics, pp. 83-87, 2003.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): The number of times that the whole algorithm (normal
            smoothing + vertex fitting) is iterated.
        angle_threshold (float): Specify a threshold angle (0..90) for features
            that you want to be preserved.  Features forming angles LARGER than
            the specified threshold will be preserved.
            0 -> no smoothing
            90 -> all faces will be smoothed
        normal_steps (int): Number of iterations of normal smoothing step. The
            larger the better and (the slower)
        fit_steps (int): Number of iterations of the vertex fitting procedure
        selected (bool): If selected the filter is performed only on the
            selected faces

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="TwoStep Smooth">\n',
        '    <Param value="{:d}" '.format(iterations),
        'type="RichInt" ',
        'name="stepSmoothNum" ',
        'description="Smoothing steps" ',
        '/>\n',
        '    <Param value="{}" '.format(angle_threshold),
        'type="RichFloat" ',
        'name="normalThr" ',
        'description="Feature Angle Threshold (deg)" ',
        '/>\n',
        '    <Param value="{:d}" '.format(normal_steps),
        'type="RichInt" ',
        'name="stepNormalNum" ',
        'description="Normal Smoothing steps" ',
        '/>\n',
        '    <Param value="{:d}" '.format(fit_steps),
        'type="RichInt" ',
        'name="stepFitNum" ',
        'description="Vertex Fitting steps" ',
        '/>\n',
        '    <Param value="{}" '.format(str(selected).lower()),
        'type="RichBool" ',
        'name="Selected" ',
        'description="Affect only selected faces" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def depth(script, iterations=3, viewpoint=(0, 0, 0), selected=False):
    """ A laplacian smooth that is constrained to move vertices only along the
        view direction.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        iterations (int): The number of times that the whole algorithm (normal
            smoothing + vertex fitting) is iterated.
        viewpoint (vector tuple or list): The position of the view point that
            is used to get the constraint direction.
        selected (bool): If selected the filter is performed only on the
            selected faces

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Depth Smooth">\n',
        '    <Param value="{:d}" '.format(iterations),
        'type="RichInt" ',
        'name="stepSmoothNum" ',
        'description="Smoothing steps" ',
        '/>\n',
        '    <name="viewPoint" ',
        'x="{}" '.format(viewpoint[0]),
        'y="{}" '.format(viewpoint[1]),
        'z="{}" '.format(viewpoint[2]),
        'description="Smoothing steps" ',
        'type="RichPoint3f" ',
        '/>\n',
        '    <Param value="{}" '.format(str(selected).lower()),
        'type="RichBool" ',
        'name="Selected" ',
        'description="Affect only selected faces" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None
