""" MeshLabXML layer functions """


def join(script='TEMP3D_default.mlx', merge_visible=True,
         merge_vert=False, delete_layer=True,
         keep_unreferenced_vert=False,
         current_layer=None, last_layer=None):

    # NOTE: filter will discard textures, creates a new layer "Merged Mesh"
    if current_layer is not None:
        if delete_layer:
            current_layer = 0
            last_layer = 0
        else:
            current_layer += 1
            last_layer += 1
    script_file = open(script, 'a')
    script_file.write('  <filter name="Flatten Visible Layers">\n' +

                      '    <Param name="MergeVisible" ' +
                      'value="%s" ' % str(merge_visible).lower() +
                      'description="Merge Only Visible Layers" ' +
                      'type="RichBool" ' +
                      'tooltip="Merge only visible layers"/>\n' +

                      '    <Param name="MergeVertices" ' +
                      'value="%s" ' % str(merge_vert).lower() +
                      'description="Merge duplicate vertices" ' +
                      'type="RichBool" ' +
                      'tooltip="Merge the vertices that are duplicated among' +
                      ' different layers. Very useful when the layers are spliced' +
                      ' portions of a single big mesh."/>\n' +

                      '    <Param name="DeleteLayer" ' +
                      'value="%s" ' % str(delete_layer).lower() +
                      'description="Delete Layers" ' +
                      'type="RichBool" ' +
                      'tooltip="Delete all the merged layers. If all layers are' +
                      ' visible only a single layer will remain after the' +
                      ' invocation of this filter."/>\n' +

                      '    <Param name="AlsoUnreferenced" ' +
                      'value="%s" ' % str(keep_unreferenced_vert).lower() +
                      'description="Keep unreferenced vertices" ' +
                      'type="RichBool" ' +
                      'tooltip="Do not discard unreferenced vertices from source' +
                      ' layers. Necessary for point-only layers"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def delete_o(FilterScriptObject):
    """Delete current layer"""
    FilterScriptObject.filters.append('  <filter name="Delete Current Mesh"/>\n')
    del FilterScriptObject.layer_stack[FilterScriptObject.current_layer()]
    # Set current layer:
    FilterScriptObject.layer_stack[FilterScriptObject.last_layer() + 1] = FilterScriptObject.current_layer() - 1
    return None


def delete(script='TEMP3D_default.mlx',
           current_layer=None, last_layer=None):
    """Delete current layer"""
    if current_layer is not None:
        current_layer -= 1
        last_layer -= 1
    script_file = open(script, 'a')
    script_file.write('  <filter name="Delete Current Mesh"/>\n')
    script_file.close()
    return current_layer, last_layer


def rename(script='TEMP3D_default.mlx', label='blank',
           current_layer=None, last_layer=None):
    """Renames current layer label. Not currently very useful for non-interactive use.

    Can be useful for outputting mlp files, as the output file names use
    the labels.
    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Rename Current Mesh">\n' +

                      '    <Param name="newName" ' +
                      'value="%s" ' % label +
                      'description="New Label" ' +
                      'type="RichString" ' +
                      'tooltip="New Label for the mesh"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def change_o(FilterScriptObject, layer_num):
    """change the current layer by specifying the new layer number.
    BROKEN: this filter crashes meshlabserver but runs fine in the gui. A MeshLab bug is suspected.
    TODO: do some more troubleshooting before filing a bug report.
      Find the minimum case that will cause this to occur, i.e. open cube, duplicate, change_L
      test on different computers
      does initial delete filter have anything to do with it?

    """
    FilterScriptObject.filters.append(''.join([
        '  <filter name="Change the current layer">\n',
        '    <Param name="mesh" ',
        'value="%d" ' % layer_num,
        'description="Mesh" ',
        'type="RichMesh" ',
        'tooltip="The number of the layer to change to"/>\n',
        '  </filter>\n']))
    FilterScriptObject.layer_stack[FilterScriptObject.last_layer() + 1] = layer_num
    return None



def change(script='TEMP3D_default.mlx', layer_num=0,
           current_layer=None, last_layer=None):
    """change the current layer by specifying the new layer number.
    BROKEN: this filter crashes meshlabserver but runs fine in the gui. A MeshLab bug is suspected.
    TODO: do some more troubleshooting before filing a bug report.
      Find the minimum case that will cause this to occur, i.e. open cube, duplicate, change_L
      test on different computers
      does initial delete filter have anything to do with it?

    """
    if current_layer is not None:
        current_layer = layer_num
    script_file = open(script, 'a')
    script_file.write('  <filter name="Change the current layer">\n' +

                      '    <Param name="mesh" ' +
                      'value="%d" ' % layer_num +
                      'description="Mesh" ' +
                      'type="RichMesh" ' +
                      'tooltip="The number of the layer to change to"/>\n' +

                      '  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def duplicate(script='TEMP3D_default.mlx',
              current_layer=None, last_layer=None):
    """Duplicate the current layer. New layer label is '*_copy'."""
    if current_layer is not None:
        current_layer += 1
        last_layer += 1
    script_file = open(script, 'a')
    script_file.write('  <filter name="Duplicate Current layer"/>\n')
    script_file.close()
    return current_layer, last_layer


def split_parts(script='TEMP3D_default.mlx', part_num=None,
                current_layer=None, last_layer=None):
    """Splits mesh into separate parts (components). Creates layers named
    'CC 0', 'CC 1', etc.

    Warnings: does not preserve textures."""
    if current_layer is not None:
        if part_num is not None:
            current_layer += part_num
            last_layer += part_num
        else:
            print('Warning: the number of parts was not provided and cannot be determined automatically. Cannot set correct current layer and last layer values.')
    script_file = open(script, 'a')
    script_file.write('  <filter name="Split in Connected Components"/>\n')
    script_file.close()
    return current_layer, last_layer
