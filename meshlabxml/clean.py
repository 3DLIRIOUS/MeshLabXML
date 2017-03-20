"""MeshLabXML cleaning and repairing functions

Also see select and delete modules for more cleaning functions
"""


def merge_vert_o(FilterScriptObject, threshold=0.0):
    # This filter only works on the current layer
    FilterScriptObject.filters.append(''.join([
        '  <filter name="Merge Close Vertices">\n',
        '    <Param name="Threshold" ',
        'value="%s" ' % threshold,
        'description="Merging distance" ',
        'min="0" ',
        'max="1" ',
        'type="RichAbsPerc" ',
        'tooltip="All the vertices that closer than this threshold',
        ' are merged together. Use very small values, default value',
        ' is 1/10000 of bounding box diagonal."/>\n',
        '  </filter>\n']))
    return None


def merge_vert(script='TEMP3D_default.mlx', threshold=0.0,
               current_layer=None, last_layer=None):
    # This filter only works on the current layer
    script_file = open(script, 'a')
    script_file.write('  <filter name="Merge Close Vertices">\n' +

                      '    <Param name="Threshold" ' +
                      'value="%s" ' % threshold +
                      'description="Merging distance" ' +
                      'min="0" ' +
                      'max="1" ' +
                      'type="RichAbsPerc" ' +
                      'tooltip="All the vertices that closer than this threshold' +
                      ' are merged together. Use very small values, default value' +
                      ' is 1/10000 of bounding box diagonal."/>\n' +
                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def close_holes(script='TEMP3D_default.mlx', hole_max_edge=30,
                selected=False, sel_new_face=True,
                self_intersection=True,
                current_layer=None, last_layer=None):
    # TIP: run subdivide on the slected faces next if the hole is large
    # TODO: automatically subdivide based on how many edges are in hole.
    # Need to experiment to find good numbers.
    # Run filter with progressivley larger hole sizes, subdiving by increasing
    # amounts as hole gets bigger
    script_file = open(script, 'a')
    script_file.write('  <filter name="Close Holes">\n' +

                      '    <Param name="maxholesize" ' +
                      'value="%d" ' % hole_max_edge +
                      'description="Max size to be closed" ' +
                      'type="RichInt" ' +
                      'tooltip="The size is expressed as number of edges composing' +
                      ' the hole boundary."/>\n' +

                      '    <Param name="Selected" ' +
                      'value="%s" ' % str(selected).lower() +
                      'description="Close holes with selected faces" ' +
                      'type="RichBool" ' +
                      'tooltip="Only the holes with at least one of the boundary' +
                      ' faces selected are closed."/>\n' +

                      '    <Param name="NewFaceSelected" ' +
                      'value="%s" ' % str(sel_new_face).lower() +
                      'description="Select the newly created faces" ' +
                      'type="RichBool" ' +
                      'tooltip="After closing a hole the faces that have been' +
                      ' created are left selected. Any previous selection is lost.' +
                      ' Useful for example for smoothing or subdividing the newly' +
                      ' created holes."/>\n' +

                      '    <Param name="SelfIntersection" ' +
                      'value="%s" ' % str(self_intersection).lower() +
                      'description="Prevent creation of selfIntersecting faces" ' +
                      'type="RichBool" ' +
                      'tooltip="When closing an holes it tries to prevent the' +
                      ' creation of faces that intersect faces adjacent to the' +
                      ' boundary of the hole. It is an heuristic, non intersecting' +
                      ' hole filling can be NP-complete."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def split_vert_on_nonmanifold_face(script='TEMP3D_default.mlx',
                                   vert_displacement_ratio=0.0,
                                   current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Split Vertexes Incident on' +
                      ' Non Manifold Faces">\n' +

                      '    <Param name="VertDispRatio" ' +
                      'value="%d" ' % vert_displacement_ratio +
                      'description="Vertex Displacement Ratio" ' +
                      'type="RichFloat" ' +
                      'tooltip="When a vertex is split it is moved along the average' +
                      ' vector going from its position to the baricyenter of the' +
                      ' FF connected faces sharing it."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def fix_folded_face(script='TEMP3D_default.mlx',
                    current_layer=None, last_layer=None):
    # TODO: need to test
    script_file = open(script, 'a')
    script_file.write(
        '  <filter name="Remove Isolated Folded Faces by Edge Flip"/>\n')
    script_file.close()
    return current_layer, last_layer


def snap_mismatched_borders(script='TEMP3D_default.mlx',
                            edge_dist_ratio=0.01,
                            unify_vert=True,
                            current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Snap Mismatched Borders">\n' +

                      '    <Param name="EdgeDistRatio" ' +
                      'value="%s" ' % edge_dist_ratio +
                      'description="Edge Distance Ratio" ' +
                      'type="RichFloat" ' +
                      'tooltip="Collapse edge when the edge / distance ratio is' +
                      ' greater than this value. E.g. for default value 1000 two' +
                      ' straight border edges are collapsed if the central vertex' +
                      ' dist from the straight line composed by the two edges less' +
                      ' than a 1/1000 of the sum of the edges length. Larger values' +
                      ' enforce that only vertexes very close to the line are' +
                      ' removed."/>\n' +

                      '    <Param name="UnifyVertices" ' +
                      'value="%s" ' % str(unify_vert).lower() +
                      'description="UnifyVertices" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the snap vertices are weld together."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer
