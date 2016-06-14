""" MeshLabXML remeshing functions """


def simplify(script='TEMP3D_default.mlx', texture=True, faces=25000,
             target_perc=0.0, quality_thr=0.3, preserve_boundary=False,
             boundary_weight=1.0, preserve_normal=False,
             optimal_placement=True, planar_quadric=False,
             selected=False, extra_tex_coord_weight=1.0,
             preserve_topology=True, quality_weight=False,
             autoclean=True, current_layer=None, last_layer=None):
    # TIP: measure topology fist to find number of faces and area
    script_file = open(script, 'a')

    if texture:
        script_file.write('  <filter name="Quadric Edge Collapse Decimation ' +
                          '(with texture)">\n')
    else:
        script_file.write(
            '  <filter name="Quadric Edge Collapse Decimation">\n')

    # Parameters common to both 'with' and 'without texture'
    script_file.write('    <Param name="TargetFaceNum" ' +
                      'value="%d" ' % faces +
                      'description="Target number of faces" ' +
                      'type="RichInt" ' +
                      'tooltip="The desired final number of faces"/>\n' +

                      '    <Param name="TargetPerc" ' +
                      'value="%s" ' % target_perc +
                      'description="Percentage reduction (0..1)" ' +
                      'type="RichFloat" ' +
                      'tooltip="If non zero, this parameter specifies the desired' +
                      ' final size of the mesh as a percentage of the initial' +
                      ' mesh size."/>\n' +

                      '    <Param name="QualityThr" ' +
                      'value="%s" ' % quality_thr +
                      'description="Quality threshold" ' +
                      'type="RichFloat" ' +
                      'tooltip="Quality threshold for penalizing bad shaped faces.' +
                      ' The value is in the range [0..1]' +
                      ' 0 accept any kind of face (no penalties),' +
                      ' 0.5 penalize faces with quality less than 0.5,' +
                      ' proportionally to their shape."/>\n' +

                      '    <Param name="PreserveBoundary" ' +
                      'value="%s" ' % str(preserve_boundary).lower() +
                      'description="Preserve Boundary of the mesh" ' +
                      'type="RichBool" ' +
                      'tooltip="The simplification process tries not to affect mesh' +
                      ' boundaries"/>\n' +

                      '    <Param name="BoundaryWeight" ' +
                      'value="%s" ' % boundary_weight +
                      'description="Boundary Preserving Weight" ' +
                      'type="RichFloat" ' +
                      'tooltip="The importance of the boundary during simplification.' +
                      ' Default (1.0) means that the boundary has the same importance' +
                      ' of the rest. Values greater than 1.0 raise boundary importance' +
                      ' and has the effect of removing less vertices on the border.' +
                      ' Admitted range of values (0,+inf)."/>\n' +

                      '    <Param name="OptimalPlacement" ' +
                      'value="%s" ' % str(optimal_placement).lower() +
                      'description="Optimal position of simplified vertices" ' +
                      'type="RichBool" ' +
                      'tooltip="Each collapsed vertex is placed in the position' +
                      ' minimizing the quadric error. It can fail (creating bad' +
                      ' spikes) in case of very flat areas. If disabled edges' +
                      ' are collapsed onto one of the two original vertices and' +
                      ' the final mesh is composed by a subset of the original' +
                      ' vertices."/>\n' +

                      '    <Param name="PreserveNormal" ' +
                      'value="%s" ' % str(preserve_normal).lower() +
                      'description="Preserve Normal" ' +
                      'type="RichBool" ' +
                      'tooltip="Try to avoid face flipping effects and try to' +
                      ' preserve the original orientation of the surface"/>\n' +

                      '    <Param name="PlanarQuadric" ' +
                      'value="%s" ' % str(planar_quadric).lower() +
                      'description="Planar Simplification" ' +
                      'type="RichBool" ' +
                      'tooltip="Add additional simplification constraints that' +
                      ' improves the quality of the simplification of the planar' +
                      ' portion of the mesh."/>\n' +

                      '    <Param name="Selected" ' +
                      'value="%s" ' % str(selected).lower() +
                      'description="Simplify only selected faces" ' +
                      'type="RichBool" ' +
                      'tooltip="The simplification is applied only to the selected' +
                      ' set of faces. Take care of the target number of faces!"/>\n')

    if texture:  # Parameters unique to 'with texture'
        script_file.write('    <Param name="Extratcoordw" ' +
                          'value="%s" ' % extra_tex_coord_weight +
                          'description="Texture Weight" ' +
                          'type="RichFloat" ' +
                          'tooltip="Additional weight for each extra Texture' +
                          ' Coordinates for every (selected) vertex"/>\n')

    else:  # Parameters unique to 'without texture'
        script_file.write('    <Param name="PreserveTopology" ' +
                          'value="%s" ' % str(preserve_topology).lower() +
                          'description="Preserve Topology" ' +
                          'type="RichBool" ' +
                          'tooltip="Avoid all the collapses that should cause a' +
                          ' topology change in the mesh (like closing holes,' +
                          ' squeezing handles, etc). If checked the genus of the' +
                          ' mesh should stay unchanged."/>\n' +

                          '    <Param name="QualityWeight" ' +
                          'value="%s" ' % str(quality_weight).lower() +
                          'description="Weighted Simplification" ' +
                          'type="RichBool" ' +
                          'tooltip="Use the Per-Vertex quality as a weighting factor' +
                          ' for the simplification. The weight is used as a error' +
                          ' amplification value, so a vertex with a high quality' +
                          ' value will not be simplified and a portion of the mesh' +
                          ' with low quality values will be aggressively' +
                          ' simplified."/>\n' +

                          '    <Param name="AutoClean" ' +
                          'value="%s" ' % str(autoclean).lower() +
                          'description="Post-simplification cleaning" ' +
                          'type="RichBool" ' +
                          'tooltip="After the simplification an additional set of' +
                          ' steps is performed to clean the mesh (unreferenced' +
                          ' vertices, bad faces, etc)/>\n')

    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def uniform_resampling(script='TEMP3D_default.mlx', voxel=1.0,
                       offset=0.0, merge_vert=True, discretize=False,
                       multisample=False, thicken=False,
                       current_layer=None, last_layer=None):

    # If you prefer to use a precision (as a percentage of AABB[diag])
    # instead of the voxel cell size include the following code in the parent
    # and pass voxel:
    #   precision=1 # 1% of AABB[diag]
    #   voxel=$(bc <<< "(${AABB[diag]} * 0.01 * $precision)")
    script_file = open(script, 'a')
    script_file.write('  <filter name="Uniform Mesh Resampling">\n' +

                      '    <Param name="CellSize" ' +
                      'value="%s" ' % voxel +
                      'description="Precision" ' +
                      'min="0" ' +
                      'max="100" ' +
                      'type="RichAbsPerc" ' +
                      'tooltip="Voxel (cell) size for resampling. Smaller cells give' +
                      ' better precision at a higher computational cost. Remember' +
                      ' that halving the cell size means that you build a volume 8' +
                      ' times larger."/>\n' +

                      '    <Param name="Offset" ' +
                      'value="%s" ' % offset +
                      'description="Offset" ' +
                      'min="-100" ' +
                      'max="100" ' +
                      'type="RichAbsPerc" ' +
                      'tooltip=" Offset amount of the created surface (i.e. distance' +
                      ' of the created surface from the original one). If offset is' +
                      ' zero, the created surface passes on the original mesh' +
                      ' itself. Values greater than zero mean an external surface' +
                      ' (offset), and lower than zero mean an internal surface' +
                      ' (inset). In practice this value is the threshold passed to' +
                      ' the Marching Cube algorithm to extract the isosurface from' +
                      ' the distance field representation."/>\n' +

                      '    <Param name="mergeCloseVert" ' +
                      'value="%s" ' % str(merge_vert).lower() +
                      'description="Clean Vertices" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the mesh generated by MC will be cleaned by' +
                      ' unifying vertices that are almost coincident"/>\n' +

                      '    <Param name="discretize" ' +
                      'value="%s" ' % str(discretize).lower() +
                      'description="Discretize" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the position of the intersected edge of the' +
                      ' marching cube grid is not computed by linear interpolation,' +
                      ' but it is placed in fixed middle position. As a consequence' +
                      ' the resampled object will look severely aliased by a' +
                      ' stairstep appearance. Useful only for simulating the output' +
                      ' of 3D printing devices."/>\n' +

                      '    <Param name="multisample" ' +
                      'value="%s" ' % str(multisample).lower() +
                      'description="Multisample" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the distance field is more accurately' +
                      ' compute by multisampling the volume (7 sample for each' +
                      ' voxel). Much slower but less artifacts."/>\n' +

                      '    <Param name="absDist" ' +
                      'value="%s" ' % str(thicken).lower() +
                      'description="Absolute Distance" ' +
                      'type="RichBool" ' +
                      'tooltip="If true, you have to choose a not zero Offset and a' +
                      ' double surface is built around the original surface, inside' +
                      ' and outside. Is useful to convert thin floating surfaces' +
                      ' into solid, thick meshes."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def hull(script='TEMP3D_default.mlx', reorient_normal=True,
         current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Convex Hull">\n' +

                      '    <Param name="reorient" ' +
                      'value="%s" ' % str(reorient_normal).lower() +
                      'description="Re-orient all faces coherentely" ' +
                      'type="RichBool" ' +
                      'tooltip="Re-orient all faces coherentely after hull' +
                      ' operation."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def reconstruct_surface_poisson(script='TEMP3D_default.mlx',
                                octree_depth=10, solver_divide=8,
                                samples_per_node=1.0, offset=1.0,
                                current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Surface Reconstruction: Poisson">\n' +

                      '    <Param name="OctDepth" ' +
                      'value="%d" ' % octree_depth +
                      'description="Octree Depth" ' +
                      'type="RichInt" ' +
                      'tooltip="Set the depth of the Octree used for extracting the' +
                      ' final surface. Suggested range 5..10. Higher numbers mean' +
                      ' higher precision in the reconstruction but also higher' +
                      ' processing times. Be patient."/>\n' +

                      '    <Param name="SolverDivide" ' +
                      'value="%d" ' % solver_divide +
                      'description="Solver Divide" ' +
                      'type="RichInt" ' +
                      'tooltip="This integer argument specifies the depth at which' +
                      ' a block Gauss-Seidel solver is used to solve the Laplacian' +
                      ' equation. Using this parameter helps reduce the memory' +
                      ' overhead at the cost of a small increase in reconstruction' +
                      ' time. In practice, the authors have found that for' +
                      ' reconstructions of depth 9 or higher a subdivide depth of 7' +
                      ' or 8 can reduce the memory usage. The default value is' +
                      ' 8."/>\n' +

                      '    <Param name="SamplesPerNode" ' +
                      'value="%s" ' % samples_per_node +
                      'description="Samples per Node" ' +
                      'type="RichFloat" ' +
                      'tooltip="This floating point value specifies the minimum' +
                      ' number of sample points that should fall within an octree' +
                      ' node as the octree&#xa;construction is adapted to sampling' +
                      ' density. For noise-free samples, small values in the range' +
                      ' [1.0 - 5.0] can be used. For more noisy samples, larger' +
                      ' values in the range [15.0 - 20.0] may be needed to provide' +
                      ' a smoother, noise-reduced, reconstruction. The default' +
                      ' value is 1.0."/>\n' +

                      '    <Param name="Offset" ' +
                      'value="%s" ' % offset +
                      'description="Surface offsetting" ' +
                      'type="RichFloat" ' +
                      'tooltip="This floating point value specifies a correction' +
                      ' value for the isosurface threshold that is chosen. Values' +
                      ' less than 1 mean internal offsetting, greater than 1 mean' +
                      ' external offsetting. Good values are in the range 0.5 .. 2.' +
                      ' The default value is 1.0 (no offsetting)."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer
