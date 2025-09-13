""" MeshLabXML layer functions """

#from . import mlx.FilterScript
#from meshlabxml import mlx.FilterScript
import meshlabxml as mlx
from . import util

def join(script, merge_visible=True, merge_vert=False, delete_layer=True,
         keep_unreferenced_vert=False):
    """ Flatten all or only the visible layers into a single new mesh.

    Transformations are preserved. Existing layers can be optionally
    deleted.

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        merge_visible (bool): merge only visible layers
        merge_vert (bool): merge the vertices that are duplicated among
            different layers. Very useful when the layers are spliced portions
            of a single big mesh.
        delete_layer (bool): delete all the merged layers. If all layers are
            visible only a single layer will remain after the invocation of
            this filter.
        keep_unreferenced_vert (bool): Do not discard unreferenced vertices
            from source layers. Necessary for point-only layers.

    Layer stack:
        Creates a new layer "Merged Mesh"
        Changes current layer to the new layer
        Optionally deletes all other layers

    MeshLab versions:
        2016.12
        1.3.4BETA

    Bugs:
        UV textures: not currently preserved, however will be in a future
            release. https://github.com/cnr-isti-vclab/meshlab/issues/128
        merge_visible: it is not currently possible to change the layer
            visibility from meshlabserver, however this will be possible
            in the future https://github.com/cnr-isti-vclab/meshlab/issues/123
    """
    filter_xml = ''.join([
        '  <filter name="Flatten Visible Layers">\n',
        '    <Param ',
        'value="{}" '.format(str(merge_visible).lower()),
        'name="MergeVisible" ',
        'description="Merge Only Visible Layers" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param ',
        'value="{}" '.format(str(merge_vert).lower()),
        'name="MergeVertices" ',
        'description="Merge duplicate vertices" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param ',
        'value="{}" '.format(str(delete_layer).lower()),
        'name="DeleteLayer" ',
        'description="Delete Layers" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param ',
        'value="{}" '.format(str(keep_unreferenced_vert).lower()),
        'name="AlsoUnreferenced" ',
        'description="Keep unreferenced vertices" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, mlx.FilterScript):
        script.add_layer('Merged Mesh')
        if delete_layer:
            # As it is not yet possible to change the layer visibility, all
            # layers will be deleted. This will be updated once layer
            # visibility is tracked.
            for i in range(script.last_layer()):
                script.del_layer(0)
    return None


def delete(script, layer_num=None):
    """ Delete layer

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        layer_num (int): the number of the layer to delete. Default is the
            current layer. Not supported on the file base API.

    Layer stack:
        Deletes a layer
        will change current layer if deleted layer is lower in the stack

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Delete Current Mesh"/>\n'
    if isinstance(script, mlx.FilterScript):
        if (layer_num is None) or (layer_num == script.current_layer()):
            util.write_filter(script, filter_xml)
            script.del_layer(script.current_layer())
        else:
            cur_layer = script.current_layer()
            change(script, layer_num)
            util.write_filter(script, filter_xml)
            if layer_num < script.current_layer():
                change(script, cur_layer - 1)
            else:
                change(script, cur_layer)
            script.del_layer(layer_num)
    else:
        util.write_filter(script, filter_xml)
    return None


def rename(script, label='blank', layer_num=None):
    """ Rename layer label

    Can be useful for outputting mlp files, as the output file names use
    the labels.

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        label (str): new label for the mesh layer
        layer_num (int): layer number to rename. Default is the
            current layer. Not supported on the file base API.

    Layer stack:
        Renames a layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = ''.join([
        '  <filter name="Rename Current Mesh">\n',
        '    <Param ',
        'value="{}" '.format(label),
        'name="newName" ',
        'description="New Label" ',
        'type="RichString" ',
        '/>\n',
        '  </filter>\n'])
    if isinstance(script, mlx.FilterScript):
        if (layer_num is None) or (layer_num == script.current_layer()):
            util.write_filter(script, filter_xml)
            script.layer_stack[script.current_layer()] = label
        else:
            cur_layer = script.current_layer()
            change(script, layer_num)
            util.write_filter(script, filter_xml)
            change(script, cur_layer)
            script.layer_stack[layer_num] = label
    else:
        util.write_filter(script, filter_xml)
    return None


def change(script, layer_num=None):
    """ Change the current layer by specifying the new layer number.

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        layer_num (int): the number of the layer to change to. Default is the
            last layer if script is a mlx.FilterScript object; if script is a
            filename the default is the first layer.

    Layer stack:
        Modifies current layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    if layer_num is None:
        if isinstance(script, mlx.FilterScript):
            layer_num = script.last_layer()
        else:
            layer_num = 0
    if script.ml_version == '1.3.4BETA' or script.ml_version == '2016.12':
        filter_xml = ''.join([
            '  <filter name="Change the current layer">\n',
            '    <Param ',
            'value="{:f}" '.format(layer_num),
            'name="mesh" ',
            'description="Mesh" ',
            'type="RichMesh" ',
            '/>\n',
            '  </filter>\n'])
    else:
        filter_xml = ''.join([
            '  <filter name="Change the current layer">\n',
            '    <Param ',
            'value="{:f}" '.format(layer_num),
            'name="layer" ',
            'description="Layer Name" ',
            'type="RichMesh" ',
            '/>\n',
            '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, mlx.FilterScript):
        script.set_current_layer(layer_num)
        #script.layer_stack[len(self.layer_stack) - 1] = layer_num
    return None


def duplicate(script, layer_num=None):
    """ Duplicate a layer.

    New layer label is '*_copy'.

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        layer_num (int): layer number to duplicate. Default is the
            current layer. Not supported on the file base API.

    Layer stack:
        Creates a new layer
        Changes current layer to the new layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <filter name="Duplicate Current layer"/>\n'
    if isinstance(script, mlx.FilterScript):
        if (layer_num is None) or (layer_num == script.current_layer()):
            util.write_filter(script, filter_xml)
            script.add_layer('{}_copy'.format(script.layer_stack[script.current_layer()]), True)
        else:
            change(script, layer_num)
            util.write_filter(script, filter_xml)
            script.add_layer('{}_copy'.format(script.layer_stack[layer_num]), True)
    else:
        util.write_filter(script, filter_xml)
    return None


def split_parts(script, part_num=None, layer_num=None):
    """ Split current layer into many layers, one for each part (connected
        component)

    Mesh is split so that the largest part is the lowest named layer "CC 0"
    and the smallest part is the highest numbered "CC" layer.

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        part_num (int): the number of parts in the model. This is needed in
            order to properly create and manage the layer stack. Can be found
            with mlx.compute.measure_topology.
        layer_num (int): the number of the layer to split. Default is the
            current layer. Not supported on the file base API.

    Layer stack:
        Creates a new layer for each part named "CC 0", "CC 1", etc.
        Changes current layer to the last new layer

    MeshLab versions:
        2016.12
        1.3.4BETA

    Bugs:
        UV textures: not currently preserved, however will be in a future
            release. https://github.com/cnr-isti-vclab/meshlab/issues/127
    """
    filter_xml = '  <filter name="Split in Connected Components"/>\n'
    if isinstance(script, mlx.FilterScript):
        if (layer_num is not None) and (layer_num != script.current_layer()):
            change(script, layer_num)
        util.write_filter(script, filter_xml)
        if part_num is not None:
            for i in range(part_num):
                script.add_layer('CC {}'.format(i), True)
        else:
            script.add_layer('CC 0', True)
            print('Warning: the number of parts was not provided and cannot',
                  'be determined automatically. The layer stack is likely',
                  'incorrect!')
    else:
        util.write_filter(script, filter_xml)
    return None

def delete_lower(script, layer_num=None):
    """ Delete all layers below the specified one.

    Useful for MeshLab ver 2016.12, which will only output layer 0.
    """
    if layer_num is None:
        layer_num = script.current_layer()
    if layer_num != 0:
        change(script, 0)
    for i in range(layer_num):
        delete(script, 0)
    return None
