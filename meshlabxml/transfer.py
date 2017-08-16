""" MeshLabXML functions to transfer attributes """

from . import util


def tex2vc(script):
    """Transfer texture colors to vertex colors

    BUG: this does not work correctly if the file has multiple textures; it
    only uses one texture and remaps all of the UVs to that
    """
    filter_xml = '  <filter name="Transfer Color: Texture to Vertex"/>\n'
    util.write_filter(script, filter_xml)
    return None


def vc2tex(script, tex_name='TEMP3D_texture.png', tex_width=1024,
           tex_height=1024, overwrite_tex=False, assign_tex=False,
           fill_tex=True):
    """Transfer vertex colors to texture colors

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        tex_name (str): The texture file to be created
        tex_width (int): The texture width
        tex_height (int): The texture height
        overwrite_tex (bool): If current mesh has a texture will be overwritten (with provided texture dimension)
        assign_tex (bool): Assign the newly created texture
        fill_tex (bool): If enabled the unmapped texture space is colored using a pull push filling algorithm, if false is set to black
    """
    filter_xml = ''.join([
        '  <filter name="Vertex Color to Texture">\n',
        '    <Param name="textName" ',
        'value="%s" ' % tex_name,
        'description="Texture file" ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="textW" ',
        'value="%d" ' % tex_width,
        'description="Texture width (px)" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="textH" ',
        'value="%d" ' % tex_height,
        'description="Texture height (px)" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="overwrite" ',
        'value="%s" ' % str(overwrite_tex).lower(),
        'description="Overwrite texture" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="assign" ',
        'value="%s" ' % str(assign_tex).lower(),
        'description="Assign Texture" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="pullpush" ',
        'value="%s" ' % str(fill_tex).lower(),
        'description="Fill texture" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def fc2vc(script):
    """Transfer face colors to vertex colors

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
    """
    filter_xml = '  <filter name="Transfer Color: Face to Vertex"/>\n'
    util.write_filter(script, filter_xml)
    return None


def vc2fc(script):
    """Transfer vertex colors to face colors

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
    """
    filter_xml = '  <filter name="Transfer Color: Vertex to Face"/>\n'
    util.write_filter(script, filter_xml)
    return None


def mesh2fc(script, all_visible_layers=False):
    """Transfer mesh colors to face colors

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        all_visible_layers (bool): If true the color mapping is applied to all the meshes
    """
    filter_xml = ''.join([
        '  <filter name="Transfer Color: Mesh to Face">\n',
        '    <Param name="allVisibleMesh" ',
        'value="%s" ' % str(all_visible_layers).lower(),
        'description="Apply to all Meshes" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def vert_attributes_2_meshes(script, source_mesh=0, target_mesh=1,
                             geometry=False, normal=False, color=True,
                             quality=False, selection=False,
                             quality_distance=False, max_distance=0.5):
    """Vertex Attribute Tranfer (between 2 meshes)

    Transfer the chosen per-vertex attributes from one mesh to another. Useful to transfer attributes to different representations of the same object. For each vertex of the target mesh the closest point (not vertex!) on the source mesh is computed, and the requested interpolated attributes from that source point are copied into the target vertex.

    The algorithm assumes that the two meshes are reasonably similar and aligned.

    UpperBound: absolute value (not percentage)

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        source_mesh (int): The mesh that contains the source data that we want to transfer
        target_mesh (int): The mesh whose vertexes will receive the data from the source
        geometry (bool): If enabled, the position of each vertex of the target mesh will be snapped onto the corresponding closest point on the source mesh
        normal (bool): If enabled, the normal of each vertex of the target mesh will get the (interpolated) normal of the corresponding closest point on the source mesh
        color (bool): If enabled, the color of each vertex of the target mesh will become the color of the corresponding closest point on the source mesh
        quality (bool): If enabled, the quality of each vertex of the target mesh will become the quality of the corresponding closest point on the source mesh
        selection (bool): If enabled, each vertex of the target mesh will be selected if the corresponding closest point on the source mesh falls in a selected face
        quality_distance (bool): If enabled, we store the distance of the transferred value as in the vertex quality
        max_distance (float): Sample points for which we do not find anything within this distance are rejected and not considered for recovering attributes

    """
    filter_xml = ''.join([
        '  <filter name="Vertex Attribute Transfer">\n',
        '    <Param name="SourceMesh" ',
        'value="{:d}" '.format(source_mesh),
        'description="Source Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="TargetMesh" ',
        'value="{:d}" '.format(target_mesh),
        'description="Target Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="GeomTransfer" ',
        'value="{}" '.format(str(geometry).lower()),
        'description="Transfer Geometry" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="NormalTransfer" ',
        'value="{}" '.format(str(normal).lower()),
        'description="Transfer Normal" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="ColorTransfer" ',
        'value="{}" '.format(str(color).lower()),
        'description="Transfer Color" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="QualityTransfer" ',
        'value="{}" '.format(str(quality).lower()),
        'description="Transfer quality" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="SelectionTransfer" ',
        'value="{}" '.format(str(selection).lower()),
        'description="Transfer Selection" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="QualityDistance" ',
        'value="{}" '.format(str(quality_distance).lower()),
        'description="Store dist. as quality" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="UpperBound" ',
        'value="{}" '.format(max_distance),
        'description="Max Dist Search" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def color2tex_2_meshes(script, source_mesh=0, target_mesh=1, attribute=0,
                       max_distance=0.5, tex_name='TEMP3D_texture.png',
                       tex_width=1024, tex_height=1024,
                       overwrite_tex=True, assign_tex=False,
                       fill_tex=True):
    """Transfer Vertex Attributes to Texture (between 2 meshes)

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        source_mesh (int): The mesh that contains the source data that we want to transfer
        target_mesh (int): The mesh whose texture will be filled according to source mesh data
        attribute (int): Choose what attribute has to be transferred onto the target texture. You can choose between Per vertex attributes (color,normal,quality) or to transfer color information from source mesh texture
        max_distance (float): Sample points for which we do not find anything within this distance are rejected and not considered for recovering data
        tex_name (str): The texture file to be created
        tex_width (int): The texture width
        tex_height (int): The texture height
        overwrite_tex (bool): If target mesh has a texture will be overwritten (with provided texture dimension)
        assign_tex (bool): Assign the newly created texture to target mesh
        fill_tex (bool): If enabled the unmapped texture space is colored using a pull push filling algorithm, if false is set to black
    """
    filter_xml = ''.join([
        '  <filter name="Transfer Vertex Attributes to Texture (between 2 meshes)">\n',
        '    <Param name="sourceMesh" ',
        'value="%d" ' % source_mesh,
        'description="Source Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="targetMesh" ',
        'value="%d" ' % target_mesh,
        'description="Target Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="AttributeEnum" ',
        'value="%d" ' % attribute,
        'description="Color Data Source" ',
        'enum_val0="Vertex Color" ',
        'enum_val1="Vertex Normal" ',
        'enum_val2="Vertex Quality" ',
        'enum_val3="Texture Color" ',
        'enum_cardinality="4" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="upperBound" ',
        'value="%s" ' % max_distance,
        'description="Max Dist Search" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '    <Param name="textName" ',
        'value="%s" ' % tex_name,
        'description="Texture file" ',
        'type="RichString" ',
        '/>\n',
        '    <Param name="textW" ',
        'value="%d" ' % tex_width,
        'description="Texture width (px)" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="textH" ',
        'value="%d" ' % tex_height,
        'description="Texture height (px)" ',
        'type="RichInt" ',
        '/>\n',
        '    <Param name="overwrite" ',
        'value="%s" ' % str(overwrite_tex).lower(),
        'description="Overwrite Target Mesh Texture" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="assign" ',
        'value="%s" ' % str(assign_tex).lower(),
        'description="Assign Texture" ',
        'type="RichBool" ',
        '/>\n',
        '    <Param name="pullpush" ',
        'value="%s" ' % str(fill_tex).lower(),
        'description="Fill texture" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None


def tex2vc_2_meshes(script, source_mesh=0, target_mesh=1, max_distance=0.5):
    """Transfer texture colors to vertex colors (between 2 meshes)

    Args:
        script: the FilterScript object or script filename to write
            the filter to.
        source_mesh (int): The mesh with associated texture that we want to sample from
        target_mesh (int): The mesh whose vertex color will be filled according to source mesh texture
        max_distance (float): Sample points for which we do not find anything within this distance are rejected and not considered for recovering color
    """
    filter_xml = ''.join([
        '  <filter name="Texture to Vertex Color (between 2 meshes)">\n',
        '    <Param name="sourceMesh" ',
        'value="%d" ' % source_mesh,
        'description="Source Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="targetMesh" ',
        'value="%d" ' % target_mesh,
        'description="Target Mesh" ',
        'type="RichMesh" ',
        '/>\n',
        '    <Param name="upperBound" ',
        'value="%s" ' % max_distance,
        'description="Max Dist Search" ',
        'min="0" ',
        'max="100" ',
        'type="RichAbsPerc" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    return None
