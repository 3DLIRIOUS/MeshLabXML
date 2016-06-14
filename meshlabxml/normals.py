""" MeshLabXML functions for mesh normals """


def reorient(script='TEMP3D_default.mlx',
             current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Re-Orient all faces coherentely"/>\n')
    script_file.close()
    return current_layer, last_layer


def flip(script='TEMP3D_default.mlx', force_flip=False,
         selected=False, current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Invert Faces Orientation">\n' +

                      '    <Param name="forceFlip" ' +
                      'value="%s" ' % str(force_flip).lower() +
                      'description="Force Flip" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected, the normals will always be flipped;' +
                      ' otherwise, the filter tries to set them outside."/>\n' +

                      '    <Param name="onlySelected" ' +
                      'value="%s" ' % str(selected).lower() +
                      'description="Flip only selected faces" ' +
                      'type="RichBool" ' +
                      'tooltip="If selected, only selected faces will be' +
                      ' affected."/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer

# Will reorient normals & then make sure they are oriented outside


def fix(script='TEMP3D_default.mlx', current_layer=None, last_layer=None):
    reorient(script)
    flip(script)
    return current_layer, last_layer
