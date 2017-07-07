""" MeshLabXML remeshing functions """

#import meshlabxml as mlx
from . import FilterScript
from . import util

def simplify(script, texture=True, faces=25000, target_perc=0.0,
             quality_thr=0.3, preserve_boundary=False, boundary_weight=1.0,
             optimal_placement=True, preserve_normal=False,
             planar_quadric=False, selected=False, extra_tex_coord_weight=1.0,
             preserve_topology=True, quality_weight=False, autoclean=True):
    """ Simplify a mesh using a Quadric based Edge Collapse Strategy, better
        than clustering but slower. Optionally tries to preserve UV
        parametrization for textured meshes.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        texture (bool):
        faces (int): The desired final number of faces
        target_perc (float): If non zero, this parameter specifies the desired
            final size of the mesh as a percentage of the initial mesh size.
        quality_thr (float): Quality threshold for penalizing bad shaped faces.
            The value is in the range [0..1]0 accept any kind of face (no
            penalties), 0.5 penalize faces with quality less than 0.5,
            proportionally to their shape.
        preserve_boundary (bool): The simplification process tries not to
            affect mesh boundaries
        boundary_weight (float): The importance of the boundary during
            simplification. Default (1.0) means that the boundary has the same
            importance of the rest. Values greater than 1.0 raise boundary
            importance and has the effect of removing less vertices on the
            border. Admitted range of values (0,+inf).
        optimal_placement (bool): Each collapsed vertex is placed in the
            position minimizing the quadric error. It can fail (creating bad
            spikes) in case of very flat areas. If disabled edges are collapsed
            onto one of the two original vertices and the final mesh is
            composed by a subset of the original vertices.
        preserve_normal (bool): Try to avoid face flipping effects and try to
            preserve the original orientation of the surface.
        planar_quadric (bool): Add additional simplification constraints that
            improves the quality of the simplification of the planar portion of
            the mesh.
        selected (bool): The simplification is applied only to the selected set
            of faces. Take care of the target number of faces!
        extra_tex_coord_weight (float): Additional weight for each extra
            Texture Coordinates for every (selected) vertex. Ignored if texture
            is False.
        preserve_topology (bool): Avoid all the collapses that should cause a
            topology change in the mesh (like closing holes, squeezing handles,
            etc). If checked the genus of the mesh should stay unchanged.
        quality_weight (bool): Use the Per-Vertex quality as a weighting factor
            for the simplification. The weight is used as a error amplification
            value, so a vertex with a high quality value will not be simplified
            and a portion of the mesh with low quality values will be
            aggressively simplified.
        autoclean (bool): After the simplification an additional set of steps
            is performed to clean the mesh (unreferenced vertices, bad faces,
            etc).

    Layer stack:
        Unchanged; current mesh is simplified in place.

    MeshLab versions:
        2016.12 (different filter name)
        1.3.4BETA
    """
    if texture:
        if isinstance(script, FilterScript) and (script.ml_version == '2016.12'):
            filter_xml = '  <filter name="Simplification: Quadric Edge Collapse Decimation (with texture)">\n'
        else:
            filter_xml = '  <filter name="Quadric Edge Collapse Decimation (with texture)">\n'
    else:
        if isinstance(script, FilterScript) and (script.ml_version == '2016.12'):
            filter_xml = '  <filter name="Simplification: Quadric Edge Collapse Decimation">\n'
        else:
            filter_xml = '  <filter name="Quadric Edge Collapse Decimation">\n'
    # Parameters common to both 'with' and 'without texture'
    filter_xml = ''.join([
        filter_xml,
        '    <Param name="TargetFaceNum" ',
        'value="{:d}" '.format(faces),
        'description="Target number of faces" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="TargetPerc" ',
        'value="{}" '.format(target_perc),
        'description="Percentage reduction (0..1)" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="QualityThr" ',
        'value="{}" '.format(quality_thr),
        'description="Quality threshold" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="PreserveBoundary" ',
        'value="{}" '.format(str(preserve_boundary).lower()),
        'description="Preserve Boundary of the mesh" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="BoundaryWeight" ',
        'value="{}" '.format(boundary_weight),
        'description="Boundary Preserving Weight" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="OptimalPlacement" ',
        'value="{}" '.format(str(optimal_placement).lower()),
        'description="Optimal position of simplified vertices" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="PreserveNormal" ',
        'value="{}" '.format(str(preserve_normal).lower()),
        'description="Preserve Normal" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="PlanarQuadric" ',
        'value="{}" '.format(str(planar_quadric).lower()),
        'description="Planar Simplification" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="Selected" ',
        'value="{}" '.format(str(selected).lower()),
        'description="Simplify only selected faces" ',
        'type="RichBool" ',
        '/>\n'])
    if texture:  # Parameters unique to 'with texture'
        filter_xml = ''.join([
            filter_xml,
            '    <Param name="Extratcoordw" ',
            'value="{}" '.format(extra_tex_coord_weight),
            'description="Texture Weight" ',
            'type="RichFloat" ',
            '/>\n'])
    else:  # Parameters unique to 'without texture'
        filter_xml = ''.join([
            filter_xml,
            '    <Param name="PreserveTopology" ',
            'value="{}" '.format(str(preserve_topology).lower()),
            'description="Preserve Topology" ',
            'type="RichBool" ',
            '/>\n',
            '    <Param name="QualityWeight" ',
            'value="{}" '.format(str(quality_weight).lower()),
            'description="Weighted Simplification" ',
            'type="RichBool" ',
            '/>\n',
            '    <Param name="AutoClean" ',
            'value="{}" '.format(str(autoclean).lower()),
            'description="Post-simplification cleaning" ',
            'type="RichBool" ',
            '/>\n'])
    filter_xml = ''.join([filter_xml, '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def uniform_resampling(script, voxel=1.0, offset=0.0, merge_vert=True,
                       discretize=False, multisample=False, thicken=False):
    """ Create a new mesh that is a resampled version of the current one.

    The resampling is done by building a uniform volumetric representation
    where each voxel contains the signed distance from the original surface.
    The resampled surface is reconstructed using the marching cube algorithm
    over this volume.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        voxel (float): voxel (cell) size for resampling. Smaller cells give
            better precision at a higher computational cost. Remember that
            halving the cell size means that you build a volume 8 times larger.
        offset (float): offset amount of the created surface (i.e. distance of
            the created surface from the original one). If offset is zero, the
            created surface passes on the original mesh itself. Values greater
            than zero mean an external surface (offset), and lower than zero
            mean an internal surface (inset). In practice this value is the
            threshold passed to the Marching Cube algorithm to extract the
            isosurface from the distance field representation.
        merge_vert (bool): if True the mesh generated by MC will be cleaned by
            unifying vertices that are almost coincident.
        discretize (bool): if True the position of the intersected edge of the
            marching cube grid is not computed by linear interpolation, but it
            is placed in fixed middle position. As a consequence the resampled
            object will look severely aliased by a stairstep appearance. Useful
            only for simulating the output of 3D printing devices.
        multisample (bool): if True the distance field is more accurately
            compute by multisampling the volume (7 sample for each voxel). Much
            slower but less artifacts.
        thicken (bool): if True, you have to choose a non zero Offset and a
            double surface is built around the original surface, inside and
            outside. Is useful to convert thin floating surfaces into solid,
            thick meshes.

    Layer stack:
        Creates 1 new layer 'Offset mesh'
        Current layer is changed to new layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Uniform Mesh Resampling">\n',
        '    <Param name="CellSize" ',
        'value="{}" '.format(voxel),
        'description="Precision" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="Offset" ',
        'value="{}" '.format(offset),
        'description="Offset" ',
        'min="-100" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="mergeCloseVert" ',
        'value="{}" '.format(str(merge_vert).lower()),
        'description="Clean Vertices" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="discretize" ',
        'value="{}" '.format(str(discretize).lower()),
        'description="Discretize" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="multisample" ',
        'value="{}" '.format(str(multisample).lower()),
        'description="Multisample" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="absDist" ',
        'value="{}" '.format(str(thicken).lower()),
        'description="Absolute Distance" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Offset mesh')
    return None


def hull(script, reorient_normal=True):
    """ Calculate the convex hull with Qhull library
        http://www.qhull.org/html/qconvex.htm

    The convex hull of a set of points is the boundary of the minimal convex
    set containing the given non-empty finite set of points.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        reorient_normal (bool): Re-orient all faces coherentely after hull
            operation.

    Layer stack:
        Creates 1 new layer 'Convex Hull'
        Current layer is changed to new layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Convex Hull">\n',
        '    <Param name="reorient" ',
        'value="{}" '.format(str(reorient_normal).lower()),
        'description="Re-orient all faces coherentely" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Convex Hull')
    return None


def surface_poisson(script, octree_depth=10, solver_divide=8,
                    samples_per_node=1.0, offset=1.0):
    """ Use the points and normals to build a surface using the Poisson
        Surface reconstruction approach.

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        octree_depth (int): Set the depth of the Octree used for extracting the
            final surface. Suggested range 5..10. Higher numbers mean higher
            precision in the reconstruction but also higher processing times.
            Be patient.
        solver_divide (int): This integer argument specifies the depth at which
            a block Gauss-Seidel solver is used to solve the Laplacian
            equation. Using this parameter helps reduce the memory overhead at
            the cost of a small increase in reconstruction time. In practice,
            the authors have found that for reconstructions of depth 9 or
            higher a subdivide depth of 7 or 8 can reduce the memory usage. The
            default value is 8.
        samples_per_node (float): This floating point value specifies the
            minimum number of sample points that should fall within an octree
            node as the octree&#xa;construction is adapted to sampling density.
            For noise-free samples, small values in the range [1.0 - 5.0] can
            be used. For more noisy samples, larger values in the range
            [15.0 - 20.0] may be needed to provide a smoother, noise-reduced,
            reconstruction. The default value is 1.0.
        offset (float): This floating point value specifies a correction value
            for the isosurface threshold that is chosen. Values less than 1
            mean internal offsetting, greater than 1 mean external offsetting.
            Good values are in the range 0.5 .. 2. The default value is 1.0
            (no offsetting).

    Layer stack:
        Creates 1 new layer 'Poisson mesh'
        Current layer is changed to new layer

    MeshLab versions:
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Surface Reconstruction: Poisson">\n',
        '    <Param name="OctDepth" ',
        'value="{:d}" '.format(octree_depth),
        'description="Octree Depth" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="SolverDivide" ',
        'value="{:d}" '.format(solver_divide),
        'description="Solver Divide" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="SamplesPerNode" ',
        'value="{}" '.format(samples_per_node),
        'description="Samples per Node" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="Offset" ',
        'value="{}" '.format(offset),
        'description="Surface offsetting" ',
        'type="RichFloat" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Poisson mesh', change_layer=True)
    return None


def surface_poisson_screened(script, visible_layer=False, depth=8,
                             full_depth=5, cg_depth=0, scale=1.1,
                             samples_per_node=1.5, point_weight=4.0,
                             iterations=8, confidence=False, pre_clean=False):
    """ This surface reconstruction algorithm creates watertight
        surfaces from oriented point sets.

    The filter uses the original code of Michael Kazhdan and Matthew Bolitho
    implementing the algorithm in the following paper:

    Michael Kazhdan, Hugues Hoppe,
    "Screened Poisson surface reconstruction"
    ACM Trans. Graphics, 32(3), 2013

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        visible_layer (bool): If True all the visible layers will be used for
            providing the points
        depth (int): This integer is the maximum depth of the tree that will
            be used for surface reconstruction. Running at depth d corresponds
            to solving on a voxel grid whose resolution is no larger than
            2^d x 2^d x 2^d. Note that since the reconstructor adapts the
            octree to the sampling density, the specified reconstruction depth
            is only an upper bound. The default value for this parameter is 8.
        full_depth (int): This integer specifies the depth beyond depth the
            octree will be adapted. At coarser depths, the octree will be
            complete, containing all 2^d x 2^d x 2^d nodes. The default value
            for this parameter is 5.
        cg_depth (int): This integer is the depth up to which a
            conjugate-gradients solver will be used to solve the linear system.
            Beyond this depth Gauss-Seidel relaxation will be used. The default
            value for this parameter is 0.
        scale (float): This floating point value specifies the ratio between
            the diameter of the cube used for reconstruction and the diameter
            of the samples' bounding cube.  The default value is 1.1.
        samples_per_node (float): This floating point value specifies the
            minimum number of sample points that should fall within an octree
            node as the octree construction is adapted to sampling density. For
            noise-free samples, small values in the range [1.0 - 5.0] can be
            used. For more noisy samples, larger values in the range
            [15.0 - 20.0] may be needed to provide a smoother, noise-reduced,
            reconstruction. The default value is 1.5.
        point_weight (float): This floating point value specifies the
            importance that interpolation of the point samples is given in the
            formulation of the screened Poisson equation. The results of the
            original (unscreened) Poisson Reconstruction can be obtained by
            setting this value to 0. The default value for this parameter is 4.
        iterations (int): This integer value specifies the number of
            Gauss-Seidel relaxations to be performed at each level of the
            hierarchy. The default value for this parameter is 8.
        confidence (bool): If True this tells the reconstructor to use the
            quality as confidence information; this is done by scaling the unit
            normals with the quality values. When the flag is not enabled, all
            normals are normalized to have unit-length prior to reconstruction.
        pre_clean (bool): If True will force a cleaning pre-pass on the data
            removing all unreferenced vertices or vertices with null normals.

    Layer stack:
        Creates 1 new layer 'Poisson mesh'
        Current layer is not changed

    MeshLab versions:
        2016.12
    """
    filter_xml = ''.join([
        '  <xmlfilter name="Screened Poisson Surface Reconstruction">\n',
        '    <xmlparam name="cgDepth" value="{:d}"/>\n'.format(cg_depth),
        '    <xmlparam name="confidence" value="{}"/>\n'.format(str(confidence).lower()),
        '    <xmlparam name="depth" value="{:d}"/>\n'.format(depth),
        '    <xmlparam name="fullDepth" value="{:d}"/>\n'.format(full_depth),
        '    <xmlparam name="iters" value="{:d}"/>\n'.format(iterations),
        '    <xmlparam name="pointWeight" value="{}"/>\n'.format(point_weight),
        '    <xmlparam name="preClean" value="{}"/>\n'.format(str(pre_clean).lower()),
        '    <xmlparam name="samplesPerNode" value="{}"/>\n'.format(samples_per_node),
        '    <xmlparam name="scale" value="{}"/>\n'.format(scale),
        '    <xmlparam name="visibleLayer" value="{}"/>\n'.format(str(visible_layer).lower()),
        '  </xmlfilter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, FilterScript):
        script.add_layer('Poisson mesh', change_layer=False)
    return None
