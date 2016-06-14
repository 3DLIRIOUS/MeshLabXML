""" MeshLabXML subdivide functions """


def loop(script='TEMP3D_default.mlx', iterations=1,
                   loop_weight=0, edge_threshold=0, selected=False,
                   current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Subdivision Surfaces: Loop">\n' +

                      '    <Param name="LoopWeight" ' +
                      'value="%d" ' % loop_weight +
                      'description="Weighting scheme" ' +
                      'enum_val0="Loop" ' +
                      'enum_val1="Enhance regularity" ' +
                      'enum_val2="Enhance continuity" ' +
                      'enum_cardinality="3" ' +
                      'type="RichEnum" ' +
                      'tooltip="Change the weights used. Allow to optimize some' +
                      ' behaviours in spite of others."/>\n' +

                      '    <Param name="Iterations" ' +
                      'value="%d" ' % iterations +
                      'description="Iterations" ' +
                      'type="RichInt" ' +
                      'tooltip="Number of times the model is subdivided"/>\n' +

                      '    <Param name="Threshold" ' +
                      'value="%s" ' % edge_threshold +
                      'description="Edge Threshold" ' +
                      'min="0" ' +
                      'max="100" ' +
                      'type="RichAbsPerc" ' +
                      'tooltip="All the edges longer than this threshold will be' +
                      ' refined. Setting this value to zero will force an uniform' +
                      ' refinement."/>\n' +

                      '    <Param name="Selected" ' +
                      'value="%s" ' % str(selected).lower() +
                      'description="Affect only selected faces" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected the filter is performed only on the' +
                      ' selected faces"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def midpoint(script='TEMP3D_default.mlx', iterations=1,
                       edge_threshold=0, selected=False,
                       current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Subdivision Surfaces: Midpoint">\n' +

                      '    <Param name="Iterations" ' +
                      'value="%d" ' % iterations +
                      'description="Iterations" ' +
                      'type="RichInt" ' +
                      'tooltip="Number of times the model is subdivided"/>\n' +

                      '    <Param name="Threshold" ' +
                      'value="%s" ' % edge_threshold +
                      'description="Edge Threshold" ' +
                      'min="0" ' +
                      'max="100" ' +
                      'type="RichAbsPerc" ' +
                      'tooltip="All the edges longer than this threshold will be' +
                      ' refined. Setting this value to zero will force an uniform' +
                      ' refinement."/>\n' +

                      '    <Param name="Selected" ' +
                      'value="%s" ' % str(selected).lower() +
                      'description="Affect only selected faces" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected the filter is performed only on the' +
                      ' selected faces"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer

# def subdivide_butterfly:
# def subdivide_CC:
# def subdivide_LS3loop:
