""" MeshLabXML functions to transfer attributes """

import math

from . import util


def tex2vc(script='TEMP3D_default.mlx'):
    """Transfer texture colors to vertex colors

    BUG: this does not work correctly if the file has multiple textures; it
    only uses one texture and remaps all of the UVs to that
    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transfer Color: Texture to Vertex"/>\n')
    script_file.close()
    return


def vc2tex(script='TEMP3D_default.mlx',
           tex_name='TEMP3D_texture.png',
           tex_width=1024, tex_height=1024,
           overwrite_tex=False, assign_tex=False,
           fill_tex=True):
    """Transfer vertex colors to texture colors"""
    script_file = open(script, 'a')
    script_file.write('  <filter name="Vertex Color to Texture">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="textName"',
        'value="%s"' % tex_name,
        'description="Texture file"',
        'type="RichString"',
        'tooltip="The texture file to be created"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textW"',
        'value="%d"' % tex_width,
        'description="Texture width (px)"',
        'type="RichInt"',
        'tooltip="The texture width"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textH"',
        'value="%d"' % tex_height,
        'description="Texture height (px)"',
        'type="RichInt"',
        'tooltip="The texture height"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="overwrite"',
        'value="%s"' % str(overwrite_tex).lower(),
        'description="Overwrite texture"',
        'type="RichBool"',
        'tooltip="If current mesh has a texture will be overwritten (with provided texture dimension)"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="assign"',
        'value="%s"' % str(assign_tex).lower(),
        'description="Assign Texture"',
        'type="RichBool"',
        'tooltip="Assign the newly created texture"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="pullpush"',
        'value="%s"' % str(fill_tex).lower(),
        'description="Fill texture"',
        'type="RichBool"',
        'tooltip="If enabled the unmapped texture space is colored using a pull push filling algorithm, if false is set to black"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def fc2vc(script='TEMP3D_default.mlx'):
    """Transfer face colors to vertex colors"""
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transfer Color: Face to Vertex"/>\n')
    script_file.close()
    return


def vc2fc(script='TEMP3D_default.mlx'):
    """Transfer vertex colors to face colors"""
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transfer Color: Vertex to Face"/>\n')
    script_file.close()
    return


def mesh2fc(script='TEMP3D_default.mlx', all_visible_layers=False):
    """Transfer mesh colors to face colors"""
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transfer Color: Mesh to Face">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="allVisibleMesh"',
        'value="%s"' % str(all_visible_layers).lower(),
        'description="Apply to all Meshes"',
        'type="RichBool"',
        'tooltip="If true the color mapping is applied to all the meshes"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def vert_attributes_2_meshes(script='TEMP3D_default.mlx',
                             source_mesh=0, target_mesh=1,
                             geometry=False, normal=False,
                             color=True, quality=False,
                             selection=False, quality_distance=False,
                             upper_bound=0.5,
                             current_layer=None, last_layer=None):
    """Vertex Attribute Tranfer (between 2 meshes)
    
    Transfer the chosen per-vertex attributes from one mesh to another. Useful to transfer attributes to different representations of the same object. For each vertex of the target mesh the closest point (not vertex!) on the source mesh is computed, and the requested interpolated attributes from that source point are copied into the target vertex.
    
    The algorithm assumes that the two meshes are reasonably similar and aligned.

    UpperBound: absolute value (not percentage)
    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Vertex Attribute Transfer">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="SourceMesh"',
        'value="%d"' % source_mesh,
        'description="Source Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh that contains the source data that we want to transfer"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="TargetMesh"',
        'value="%d"' % target_mesh,
        'description="Target Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh whose vertexes will receive the data from the source"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="GeomTransfer"',
        'value="%s"' % str(geometry).lower(),
        'description="Transfer Geometry"',
        'type="RichBool"',
        'tooltip="If enabled, the position of each vertex of the target mesh will be snapped onto the corresponding closest point on the source mesh"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="NormalTransfer"',
        'value="%s"' % str(normal).lower(),
        'description="Transfer Normal"',
        'type="RichBool"',
        'tooltip="If enabled, the normal of each vertex of the target mesh will get the (interpolated) normal of the corresponding closest point on the source mesh"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="ColorTransfer"',
        'value="%s"' % str(color).lower(),
        'description="Transfer Color"',
        'type="RichBool"',
        'tooltip="If enabled, the color of each vertex of the target mesh will become the color of the corresponding closest point on the source mesh"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="QualityTransfer"',
        'value="%s"' % str(quality).lower(),
        'description="Transfer quality"',
        'type="RichBool"',
        'tooltip="If enabled, the quality of each vertex of the target mesh will become the quality of the corresponding closest point on the source mesh"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="SelectionTransfer"',
        'value="%s"' % str(selection).lower(),
        'description="Transfer Selection"',
        'type="RichBool"',
        'tooltip="If enabled, each vertex of the target mesh will be selected if the corresponding closest point on the source mesh falls in a selected face"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="QualityDistance"',
        'value="%s"' % str(quality_distance).lower(),
        'description="Store dist. as quality"',
        'type="RichBool"',
        'tooltip="If enabled, we store the distance of the transferred value as in the vertex quality"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="UpperBound"',
        'value="%s"' % upper_bound,
        'description="Max Dist Search"',
        'min="0"',
        'max="100"',
        'type="RichAbsPerc"',
        'tooltip="Sample points for which we do not find anything within this distance are rejected and not considered for recovering attributes"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def color2tex_2_meshes(script='TEMP3D_default.mlx',
                       source_mesh=0, target_mesh=1,
                       attribute=0, upper_bound=0.5, tex_name='TEMP3D_texture.png',
                       tex_width=1024, tex_height=1024,
                       overwrite_tex=True, assign_tex=False,
                       fill_tex=True,
                       current_layer=None, last_layer=None):
    """Transfer Vertex Attributes to Texture (between 2 meshes)

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Transfer Vertex Attributes to Texture (between 2 meshes)">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="sourceMesh"',
        'value="%d"' % source_mesh,
        'description="Source Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh that contains the source data that we want to transfer"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="targetMesh"',
        'value="%d"' % target_mesh,
        'description="Target Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh whose texture will be filled according to source mesh data"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="AttributeEnum"',
        'value="%d"' % attribute,
        'description="Color Data Source"',
        'enum_val0="Vertex Color"',
        'enum_val1="Vertex Normal"',
        'enum_val2="Vertex Quality"',
        'enum_val3="Texture Color"',
        'enum_cardinality="4"',
        'type="RichEnum"',
        'tooltip="Choose what attribute has to be transferred onto the target texture. You can choose between Per vertex attributes (color,normal,quality) or to transfer color information from source mesh texture"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="upperBound"',
        'value="%s"' % upper_bound,
        'description="Max Dist Search"',
        'min="0"',
        'max="100"',
        'type="RichAbsPerc"',
        'tooltip="Sample points for which we do not find anything within this distance are rejected and not considered for recovering data"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textName"',
        'value="%s"' % tex_name,
        'description="Texture file"',
        'type="RichString"',
        'tooltip="The texture file to be created"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textW"',
        'value="%d"' % tex_width,
        'description="Texture width (px)"',
        'type="RichInt"',
        'tooltip="The texture width"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textH"',
        'value="%d"' % tex_height,
        'description="Texture height (px)"',
        'type="RichInt"',
        'tooltip="The texture height"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="overwrite"',
        'value="%s"' % str(overwrite_tex).lower(),
        'description="Overwrite Target Mesh Texture"',
        'type="RichBool"',
        'tooltip="If target mesh has a texture will be overwritten (with provided texture dimension)"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="assign"',
        'value="%s"' % str(assign_tex).lower(),
        'description="Assign Texture"',
        'type="RichBool"',
        'tooltip="Assign the newly created texture to target mesh"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="pullpush"',
        'value="%s"' % str(fill_tex).lower(),
        'description="Fill texture"',
        'type="RichBool"',
        'tooltip="If enabled the unmapped texture space is colored using a pull push filling algorithm, if false is set to black"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer


def tex2vc_2_meshes(script='TEMP3D_default.mlx',
                               source_mesh=0, target_mesh=1,
                               upper_bound=0.5,
                               current_layer=None, last_layer=None):
    """Transfer texture colors to vertex colors (between 2 meshes)

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Texture to Vertex Color (between 2 meshes)">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="sourceMesh"',
        'value="%d"' % source_mesh,
        'description="Source Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh with associated texture that we want to sample from"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="targetMesh"',
        'value="%d"' % target_mesh,
        'description="Target Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh whose vertex color will be filled according to source mesh texture"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="upperBound"',
        'value="%s"' % upper_bound,
        'description="Max Dist Search"',
        'min="0"',
        'max="100"',
        'type="RichAbsPerc"',
        'tooltip="Sample points for which we do not find anything within this distance are rejected and not considered for recovering color"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return current_layer, last_layer
