""" MeshLabXML smoothing functions """


def laplacian(script='TEMP3D_default.mlx', iterations=1,
              boundary=True, cotangent_weight=True, selected=False,
              current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Laplacian Smooth">\n' +

                      '    <Param name="stepSmoothNum" ' +
                      'value="%d" ' % iterations +
                      'description="Smoothing steps" ' +
                      'type="RichInt" ' +
                      'tooltip="The number of times that the whole algorithm' +
                      ' (normal smoothing + vertex fitting) is iterated."/>\n' +

                      '    <Param name="Boundary" ' +
                      'value="%s" ' % str(boundary).lower() +
                      'description="1D Boundary Smoothing" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the boundary edges are smoothed only by' +
                      ' themselves (e.g. the polyline forming the boundary of the' +
                      ' mesh is independently smoothed). Can reduce the shrinking' +
                      ' on the border but can have strange effects on very small' +
                      ' boundaries."/>\n' +

                      '    <Param name="cotangentWeight" ' +
                      'value="%s" ' % str(cotangent_weight).lower() +
                      'description="Cotangent weighting" ' +
                      'type="RichBool" ' +
                      'tooltip="If true the cotangent weighting scheme is computed' +
                      ' for the averaging of the position. Otherwise (false) the' +
                      ' simpler umbrella scheme (1 if the edge is present) is' +
                      ' used."/>\n' +

                      '    <Param name="Selected" ' +
                      'value="%s" ' % str(selected).lower() +
                      'description="Affect only selected faces" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected the filter is performed only on the' +
                      ' selected faces"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer
