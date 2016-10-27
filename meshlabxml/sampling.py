""" MeshLabXML sampling functions """


def hausdorff_distance(script='TEMP3D_default.mlx',
                       sampled_layer=1, target_layer=0,
                       save_sample=False, sample_vert=True, sample_edge=True,
                       sample_faux_edge=False, sample_face=True, sample_num=1000,
                       maxdist=10, maxdist_max=100,
                       current_layer=None, last_layer=None):
    """
    sampledLayer=1 # The mesh whose surface is sampled.
    For each sample we search the closest point on the Target Mesh.
    targetLayer=0 # The mesh that is sampled for the comparison.
    saveSample="false" # Save the position and distance of all the used
    samples on both the two surfaces, creating two new layers with two
    point clouds representing the used samples.
    sample_V="true" # For the search of maxima it is useful to sample
    vertices and edges of the mesh with a greater care. It is quite
    probable that the farthest points falls along edges or on mesh
    vertexes, and with uniform montecarlo sampling approaches the
    probability of taking a sample over a vertex or an edge is
    theoretically null. On the other hand this kind of sampling
    could make the overall sampling distribution slightly biased
    and slightly affects the cumulative results.
    sample_E="true" # See the above comment.
    sample_fauxE="false" # See the above comment.
    sample_F="true" # See the above comment.
    sample_num=1000 # The desired number of samples. It can be smaller or
    larger than the mesh size, and according to the chosen sampling strategy
    it will try to adapt. ML default: number of vertices in sampled mesh
    maxdist=10 # Sample points for which we do not find anything within
    this distance are rejected and not considered neither for averaging
    nor for max. ML default: 5% AABB[diag] of sampled mesh,
    max 100% AABB[diag] of sampled mesh
    """

    """
    Defaults:
      sample_num=num_V
      maxdist=0.05 * AABB['diag'] #5% of AABB[diag]
      maxdistmax=AABB['diag']
    """
    # TODO: parse output (min, max, mean, etc.)

    script_file = open(script, 'a')
    script_file.write('  <filter name="Hausdorff Distance">\n' +

                      '    <Param name="SampledMesh" ' +
                      'value="%d" ' % sampled_layer +
                      'description="Sampled Mesh" ' +
                      'type="RichMesh" ' +
                      'tooltip="The mesh whose surface is sampled. For each sample' +
                      ' we search the closest point on the Target Mesh."/>\n' +

                      '    <Param name="TargetMesh" ' +
                      'value="%d" ' % target_layer +
                      'description="Target Mesh" ' +
                      'type="RichMesh" ' +
                      'tooltip="The mesh that is sampled for the comparison."/>\n' +

                      '    <Param name="SaveSample" ' +
                      'value="%s" ' % str(save_sample).lower() +
                      'description="Save Samples" ' +
                      'type="RichBool" ' +
                      'tooltip="Save the position and distance of all the used' +
                      ' samples on both the two surfaces, creating two new layers' +
                      ' with two point clouds representing the used samples."/>\n' +

                      '    <Param name="SampleVert" ' +
                      'value="%s" ' % str(sample_vert).lower() +
                      'description="Sample Vertexes" ' +
                      'type="RichBool" ' +
                      'tooltip="For the search of maxima it is useful to sample' +
                      ' vertices and edges of the mesh with a greater care. It is' +
                      ' quite probably the the farthest points falls along edges' +
                      ' or on mesh vertexes, and with uniform montecarlo sampling' +
                      ' approachesthe probability of taking a sample over a vertex' +
                      ' or an edge is theoretically null. On the other hand this' +
                      ' kind of sampling could make the overall sampling' +
                      ' distribution slightly biased and slightly affects the' +
                      ' cumulative results."/>\n' +

                      '    <Param name="SampleEdge" ' +
                      'value="%s" ' % str(sample_edge).lower() +
                      'description="Sample Edges" ' +
                      'type="RichBool" ' +
                      'tooltip="See the above comment"/>\n' +

                      '    <Param name="SampleFauxEdge" ' +
                      'value="%s" ' % str(sample_faux_edge).lower() +
                      'description="Sample FauxEdge" ' +
                      'type="RichBool" ' +
                      'tooltip="See the above comment"/>\n' +

                      '    <Param name="SampleFace" ' +
                      'value="%s" ' % str(sample_face).lower() +
                      'description="Sample Faces" ' +
                      'type="RichBool" ' +
                      'tooltip="See the above comment"/>\n' +

                      '    <Param name="SampleNum" ' +
                      'value="%d" ' % sample_num +
                      'description="Number of samples" ' +
                      'type="RichInt" ' +
                      'tooltip="The desired number of samples. It can be smaller or' +
                      ' larger than the mesh size, and according to the choosed' +
                      ' sampling strategy it will try to adapt."/>\n' +

                      '    <Param name="MaxDist" ' +
                      'value="%s" ' % maxdist +
                      'description="Max Distance" ' +
                      'min="0" ' +
                      'max="%s" ' % maxdist_max +
                      'type="RichAbsPerc" ' +
                      'tooltip="Sample points for which we do not find anything' +
                      ' whithin this distance are rejected and not considered' +
                      ' neither for averaging nor for max."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def poisson_disk(script='TEMP3D_default.mlx', sample_num=1000, radius=0.0,
                 montecarlo_rate=20, save_montecarlo=False,
                 approx_geodesic_dist=False, subsample=False, refine=False,
                 refine_layer=0, best_sample=True, best_sample_pool=10,
                 exact_num=False, radius_variance=1,
                 current_layer=None, last_layer=None):
    # NOTE: Poisson-disk sampling does not switch to the new sampling layer
    # after creation! Haven't tested other sampling filters yet
    script_file = open(script, 'a')
    script_file.write('  <filter name="Poisson-disk Sampling">\n' +

                      '    <Param name="SampleNum" ' +
                      'value="%d" ' % sample_num +
                      'description="Number of samples" ' +
                      'type="RichInt" ' +
                      'tooltip="The desired number of samples. The ray of the disk' +
                      ' is calculated according to the sampling density."/>\n' +

                      '    <Param name="Radius" ' +
                      'value="%s" ' % radius +
                      'description="Explicit Radius" ' +
                      'min="0" ' +
                      'max="100" ' +
                      'type="RichAbsPerc" ' +
                      'tooltip="If not zero this parameter override the previous' +
                      ' parameter to allow exact radius specification"/>\n' +

                      '    <Param name="MontecarloRate" ' +
                      'value="%d" ' % montecarlo_rate +
                      'description="MonterCarlo OverSampling" ' +
                      'type="RichInt" ' +
                      'tooltip="The over-sampling rate that is used to generate' +
                      ' the intial Montecarlo samples (e.g. if this parameter is' +
                      ' _K_ means that _K_ x _poisson sample_ points will be' +
                      ' used). The generated Poisson-disk samples are a subset of' +
                      ' these initial Montecarlo samples. Larger this number slows' +
                      ' the process but make it a bit more accurate."/>\n' +

                      '    <Param name="SaveMontecarlo" ' +
                      'value="%s" ' % str(save_montecarlo).lower() +
                      'description="Save Montecarlo" ' +
                      'type="RichBool" ' +
                      'tooltip="If true, it will generate an additional Layer with' +
                      ' the montecarlo sampling that was pruned to build the' +
                      ' poisson distribution."/>\n' +

                      '    <Param name="ApproximateGeodesicDistance" ' +
                      'value="%s" ' % str(approx_geodesic_dist).lower() +
                      'description="Approximate Geodesic Distance" ' +
                      'type="RichBool" ' +
                      'tooltip="If true Poisson Disc distances are computed using' +
                      ' an approximate geodesic distance, e.g. an euclidean' +
                      ' distance weighted by a function of the difference between' +
                      ' the normals of the two points."/>\n' +

                      '    <Param name="Subsample" ' +
                      'value="%s" ' % str(subsample).lower() +
                      'description="Base Mesh Subsampling" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the original vertices of the base mesh are' +
                      ' used as base set of points. In this case the SampleNum' +
                      ' should be obviously much smaller than the original vertex' +
                      ' number. Note that this option is very useful in the case' +
                      ' you want to subsample a dense point cloud."/>\n' +

                      '    <Param name="RefineFlag" ' +
                      'value="%s" ' % str(refine).lower() +
                      'description="Refine Existing Samples" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the vertices of the below mesh are used as' +
                      ' starting vertices, and they will utterly refined by adding' +
                      ' more and more points until possible."/>\n' +

                      '    <Param name="RefineMesh" ' +
                      'value="%d" ' % refine_layer +
                      'description="Samples to be refined" ' +
                      'type="RichMesh" ' +
                      'tooltip="Used only if the above option is checked."/>\n' +

                      '    <Param name="BestSampleFlag" ' +
                      'value="%s" ' % str(best_sample).lower() +
                      'description="Best Sample Heuristic" ' +
                      'type="RichBool" ' +
                      'tooltip="If true it will use a simple heuristic for choosing' +
                      ' the samples. At a small cost (it can slow a bit the' +
                      ' process) it usually improve the maximality of the generated' +
                      ' sampling."/>\n' +

                      '    <Param name="BestSamplePool" ' +
                      'value="%d" ' % best_sample_pool +
                      'description="Best Sample Pool Size" ' +
                      'type="RichInt" ' +
                      'tooltip="Used only if the Best Sample Flag is true. It' +
                      ' controls the number of atTEMP3Dts that it makes to get the' +
                      ' best sample. It is reasonable that it is smaller than the' +
                      ' Montecarlo oversampling factor."/>\n' +

                      '    <Param name="ExactNumFlag" ' +
                      'value="%s" ' % str(exact_num).lower() +
                      'description="Exact number of samples" ' +
                      'type="RichBool" ' +
                      'tooltip="If requested it will try to do a dicotomic search' +
                      ' for the best poisson disk radius that will generate the' +
                      ' requested number of samples with a tolerance of the 0.5%.' +
                      ' Obviously it takes much longer."/>\n' +

                      '    <Param name="RadiusVariance" ' +
                      'value="%s" ' % radius_variance +
                      'description="Radius Variance" ' +
                      'type="RichFloat" ' +
                      'tooltip="The radius of the disk is allowed to vary between' +
                      ' r and r*var. If this parameter is 1 the sampling is the' +
                      ' same of the Poisson Disk Sampling"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer
