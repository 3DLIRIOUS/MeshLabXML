""" MeshLabXML sampling functions """

from . import FilterScript
from . import util

def hausdorff_distance(script, sampled_layer=1, target_layer=0,
                       save_sample=False, sample_vert=True, sample_edge=True,
                       sample_faux_edge=False, sample_face=True,
                       sample_num=1000, maxdist=10):
    """ Compute the Hausdorff Distance between two meshes, sampling one of the
        two and finding for each sample the closest point over the other mesh.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        sampled_layer (int): The mesh layer whose surface is sampled. For each
            sample we search the closest point on the target mesh layer.
        target_layer (int): The mesh that is sampled for the comparison.
        save_sample (bool): Save the position and distance of all the used
            samples on both the two surfaces, creating two new layers with two
            point clouds representing the used samples.
        sample_vert (bool): For the search of maxima it is useful to sample
            vertices and edges of the mesh with a greater care. It is quite
            probable that the farthest points falls along edges or on mesh
            vertexes, and with uniform montecarlo sampling approaches the
            probability of taking a sample over a vertex or an edge is
            theoretically null. On the other hand this kind of sampling could
            make the overall sampling distribution slightly biased and slightly
            affects the cumulative results.
        sample_edge (bool): see sample_vert
        sample_faux_edge (bool): see sample_vert
        sample_face (bool): see sample_vert
        sample_num (int): The desired number of samples. It can be smaller or
            larger than the mesh size, and according to the chosen sampling
            strategy it will try to adapt.
        maxdist (int): Sample points for which we do not find anything within
            this distance are rejected and not considered neither for averaging
            nor for max.

    Layer stack:
        If save_sample is True, two new layers are created: 'Hausdorff Closest
            Points' and 'Hausdorff Sample Point'; and the current layer is
            changed to the last newly created layer.
        If save_sample is False, no impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    # MeshLab defaults:
    #  sample_num = number of vertices
    #  maxdist = 0.05 * AABB['diag'] #5% of AABB[diag]
    #  maxdist_max = AABB['diag']
    maxdist_max = 2*maxdist
    # TODO: parse output (min, max, mean, etc.)
    filter_xml = ''.join([
        '  <filter name="Hausdorff Distance">\n',
        '    <Param name="SampledMesh" ',
        'value="{:d}" '.format(sampled_layer),
        'description="Sampled Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="TargetMesh" ',
        'value="{:d}" '.format(target_layer),
        'description="Target Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="SaveSample" ',
        'value="{}" '.format(str(save_sample).lower()),
        'description="Save Samples" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SampleVert" ',
        'value="{}" '.format(str(sample_vert).lower()),
        'description="Sample Vertexes" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SampleEdge" ',
        'value="{}" '.format(str(sample_edge).lower()),
        'description="Sample Edges" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SampleFauxEdge" ',
        'value="{}" '.format(str(sample_faux_edge).lower()),
        'description="Sample FauxEdge" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SampleFace" ',
        'value="{}" '.format(str(sample_face).lower()),
        'value="%s" ' % str(sample_face).lower() +
        'description="Sample Faces" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SampleNum" ',
        'value="{:d}" '.format(sample_num),
        'description="Number of samples" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="MaxDist" ',
        'value="{}" '.format(maxdist),
        'value="%s" ' % maxdist +
        'description="Max Distance" ',
        'min="0" ',
        'max="{}" '.format(maxdist_max),
        'type="RichAbsPerc" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript) and save_sample:
        script.add_layer('Hausdorff Closest Points')
        script.add_layer('Hausdorff Sample Point')
    return None


def poisson_disk(script, sample_num=1000, radius=0.0,
                 montecarlo_rate=20, save_montecarlo=False,
                 approx_geodesic_dist=False, subsample=False, refine=False,
                 refine_layer=0, best_sample=True, best_sample_pool=10,
                 exact_num=False, radius_variance=1.0):
    """ Create a new layer populated with a point sampling of the current mesh.

    Samples are generated according to a Poisson-disk distribution, using the
    algorithm described in:

    'Efficient and Flexible Sampling with Blue Noise Properties of Triangular Meshes'
    Massimiliano Corsini, Paolo Cignoni, Roberto Scopigno
    IEEE TVCG 2012

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        sample_num (int): The desired number of samples. The radius of the disk
            is calculated according to the sampling density.
        radius (float): If not zero this parameter overrides the previous
            parameter to allow exact radius specification.
        montecarlo_rate (int): The over-sampling rate that is used to generate
            the intial Monte Carlo samples (e.g. if this parameter is 'K' means
            that 'K * sample_num' points will be used). The generated
            Poisson-disk samples are a subset of these initial Monte Carlo
            samples. Larger numbers slow the process but make it a bit more
            accurate.
        save_montecarlo (bool): If True, it will generate an additional Layer
            with the Monte Carlo sampling that was pruned to build the Poisson
            distribution.
        approx_geodesic_dist (bool): If True Poisson-disk distances are
            computed using an approximate geodesic distance, e.g. an Euclidean
            distance weighted by a function of the difference between the
            normals of the two points.
        subsample (bool): If True the original vertices of the base mesh are
            used as base set of points. In this case the sample_num should be
            obviously much smaller than the original vertex number. Note that
            this option is very useful in the case you want to subsample a
            dense point cloud.
        refine (bool): If True the vertices of the refine_layer mesh layer are
            used as starting vertices, and they will be utterly refined by
            adding more and more points until possible.
        refine_layer (int): Used only if refine is True.
        best_sample (bool): If True it will use a simple heuristic for choosing
            the samples. At a small cost (it can slow the process a bit) it
            usually improves the maximality of the generated sampling.
        best_sample_pool (bool): Used only if best_sample is True. It controls
            the number of attempts that it makes to get the best sample. It is
            reasonable that it is smaller than the Monte Carlo oversampling
            factor.
        exact_num (bool): If True it will try to do a dicotomic search for the
            best Poisson-disk radius that will generate the requested number of
            samples with a tolerance of the 0.5%. Obviously it takes much
            longer.
        radius_variance (float): The radius of the disk is allowed to vary
            between r and r*var. If this parameter is 1 the sampling is the
            same as the Poisson-disk Sampling.

    Layer stack:
        Creates new layer 'Poisson-disk Samples'. Current layer is NOT changed
            to the new layer (see Bugs).
        If save_montecarlo is True, creates a new layer 'Montecarlo Samples'.
            Current layer is NOT changed to the new layer (see Bugs).

    MeshLab versions:
        2016.12
        1.3.4BETA

    Bugs:
        Current layer is NOT changed to the new layer, which is inconsistent
            with the majority of filters that create new layers.
    """
    filter_xml = ''.join([
        '  <filter name="Poisson-disk Sampling">\n',
        '    <Param name="SampleNum" ',
        'value="{:d}" '.format(sample_num),
        'description="Number of samples" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="Radius" ',
        'value="{}" '.format(radius),
        'description="Explicit Radius" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="MontecarloRate" ',
        'value="{:d}" '.format(montecarlo_rate),
        'description="MonterCarlo OverSampling" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="SaveMontecarlo" ',
        'value="{}" '.format(str(save_montecarlo).lower()),
        'description="Save Montecarlo" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="ApproximateGeodesicDistance" ',
        'value="{}" '.format(str(approx_geodesic_dist).lower()),
        'description="Approximate Geodesic Distance" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="Subsample" ',
        'value="{}" '.format(str(subsample).lower()),
        'description="Base Mesh Subsampling" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="RefineFlag" ',
        'value="{}" '.format(str(refine).lower()),
        'description="Refine Existing Samples" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="RefineMesh" ',
        'value="{:d}" '.format(refine_layer),
        'description="Samples to be refined" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="BestSampleFlag" ',
        'value="{}" '.format(str(best_sample).lower()),
        'description="Best Sample Heuristic" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="BestSamplePool" ',
        'value="{:d}" '.format(best_sample_pool),
        'description="Best Sample Pool Size" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="ExactNumFlag" ',
        'value="{}" '.format(str(exact_num).lower()),
        'description="Exact number of samples" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="RadiusVariance" ',
        'value="{}" '.format(radius_variance),
        'description="Radius Variance" ',
        'type="RichFloat" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Poisson-disk Samples')
        if save_montecarlo:
            script.add_layer('Montecarlo Samples')
    return None


def mesh_element(script, sample_num=1000, element='VERT'):
    """ Create a new layer populated with a point sampling of the current mesh,
        at most one sample for each element of the mesh is created.

    Samples are taking in a uniform way, one for each element
    (vertex/edge/face); all the elements have the same probabilty of being
    choosen.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        sample_num (int): The desired number of elements that must be chosen.
            Being a subsampling of the original elements if this number should
            not be larger than the number of elements of the original mesh.
        element (enum in ['VERT', 'EDGE', 'FACE']): Choose what mesh element
            will be used for the subsampling. At most one point sample will
            be added for each one of the chosen elements

    Layer stack:
        Creates new layer 'Sampled Mesh'. Current layer is changed to the new
            layer.

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    if element.lower() == 'vert':
        element_num = 0
    elif element.lower() == 'edge':
        element_num = 1
    elif element.lower() == 'face':
        element_num = 2
    filter_xml = ''.join([
        '  <filter name="Mesh Element Subsampling">\n',
        '    <Param name="Sampling" ',
        'value="{:d}" '.format(element_num),
        'description="Element to sample:" ',
        'enum_val0="Vertex" ',
        'enum_val1="Edge" ',
        'enum_val2="Face" ',
        'enum_cardinality="3" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="SampleNum" ',
        'value="{:d}" '.format(sample_num),
        'description="Number of samples" ',
        'type="RichInt" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Sampled Mesh')
    return None


def clustered_vert(script, cell_size=1.0, strategy='AVERAGE', selected=False):
    """ "Create a new layer populated with a subsampling of the vertexes of the
        current mesh

    The subsampling is driven by a simple one-per-gridded cell strategy.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        cell_size (float): The size of the cell of the clustering grid. Smaller the cell finer the resulting mesh. For obtaining a very coarse mesh use larger values.
        strategy (enum 'AVERAGE' or 'CENTER'): &lt;b>Average&lt;/b>: for each cell we take the average of the sample falling into. The resulting point is a new point.&lt;br>&lt;b>Closest to center&lt;/b>: for each cell we take the sample that is closest to the center of the cell. Choosen vertices are a subset of the original ones.
        selected (bool): If true only for the filter is applied only on the selected subset of the mesh.

    Layer stack:
        Creates new layer 'Cluster Samples'. Current layer is changed to the new
            layer.

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    if strategy.lower() == 'average':
        strategy_num = 0
    elif strategy.lower() == 'center':
        strategy_num = 1

    filter_xml = ''.join([
        '  <filter name="Clustered Vertex Subsampling">\n',
        '    <Param name="Threshold" ',
        'value="{}" '.format(cell_size),
        'description="Cell Size" ',
        'min="0" ',
        'max="1000" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="Sampling" ',
        'value="{:d}" '.format(strategy_num),
        'description="Representative Strategy:" ',
        'enum_val0="Average" ',
        'enum_val1="Closest to center" ',
        'enum_cardinality="2" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Selected" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Cluster Samples')
    return None
